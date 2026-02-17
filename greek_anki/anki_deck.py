"""APKG read/write operations."""
import sqlite3
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import genanki
import zstandard as zstd

from .config import (
    CARD_AFMT,
    CARD_CSS,
    CARD_QFMT,
    DECK_ID,
    DECK_NAME,
    FIELDS,
    MODEL_ID,
    MODEL_NAME,
)


@dataclass
class AnkiNote:
    """A single note extracted from an APKG file."""

    note_id: int
    guid: str
    front: str
    back: str
    example: str
    comment: str
    collocations: str = ""
    etymology: str = ""
    tags: List[str] = field(default_factory=list)


def _decompress_anki21b(data: bytes) -> bytes:
    """Decompress zstandard-compressed anki21b data."""
    dctx = zstd.ZstdDecompressor()
    return dctx.decompress(data, max_output_size=50 * 1024 * 1024)


def read_apkg_notes(apkg_path: str | Path) -> List[AnkiNote]:
    """Read all notes from an APKG file.

    Handles both old (collection.anki2) and new (collection.anki21b) formats.
    The new format requires zstandard decompression before SQLite access.
    """
    apkg_path = Path(apkg_path)
    if not apkg_path.exists():
        raise FileNotFoundError(f"APKG file not found: {apkg_path}")

    with zipfile.ZipFile(apkg_path, "r") as zf:
        names = zf.namelist()
        if "collection.anki21b" in names:
            compressed = zf.read("collection.anki21b")
            db_bytes = _decompress_anki21b(compressed)
        elif "collection.anki2" in names:
            db_bytes = zf.read("collection.anki2")
        else:
            raise ValueError(
                f"No collection database found in {apkg_path}. "
                f"Files present: {names}"
            )

    # Write to temp file for sqlite3 access
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp.write(db_bytes)
        tmp_path = tmp.name

    notes = []
    try:
        conn = sqlite3.connect(tmp_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, guid, flds, tags FROM notes")
        for row in cursor.fetchall():
            note_id = row[0]
            guid = row[1]
            fields = row[2].split("\x1f")
            tags_str = row[3].strip() if row[3] else ""
            tags = tags_str.split() if tags_str else []

            while len(fields) < 6:
                fields.append("")

            notes.append(
                AnkiNote(
                    note_id=note_id,
                    guid=guid,
                    front=fields[0],
                    back=fields[1],
                    example=fields[2],
                    comment=fields[3],
                    collocations=fields[4],
                    etymology=fields[5],
                    tags=tags,
                )
            )
        conn.close()
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return notes


def get_anki_model() -> genanki.Model:
    """Create the genanki Model matching the existing deck's notetype."""
    return genanki.Model(
        MODEL_ID,
        MODEL_NAME,
        fields=[{"name": name} for name in FIELDS],
        templates=[
            {
                "name": "Card 1",
                "qfmt": CARD_QFMT,
                "afmt": CARD_AFMT,
            }
        ],
        css=CARD_CSS,
    )


def deck_id_from_name(name: str) -> int:
    """Generate a stable deck ID from a name."""
    import hashlib

    h = int(hashlib.sha256(name.encode()).hexdigest()[:12], 16)
    return h


def create_supplement_apkg(
    notes_data: List[dict],
    output_path: str | Path,
    tags: Optional[List[str]] = None,
    deck_name: Optional[str] = None,
    deck_id: Optional[int] = None,
) -> Path:
    """Generate a supplementary APKG file for import into Anki.

    Args:
        notes_data: List of dicts with keys: front, back, example, comment
        output_path: Where to write the .apkg file.
        tags: Optional list of tags to apply to all notes.
        deck_name: Custom deck name (defaults to DECK_NAME).
        deck_id: Custom deck ID (defaults to DECK_ID).

    Returns:
        Path to the generated .apkg file.
    """
    model = get_anki_model()
    deck = genanki.Deck(deck_id or DECK_ID, deck_name or DECK_NAME)

    for data in notes_data:
        note = genanki.Note(
            model=model,
            fields=[
                data.get("front", ""),
                data.get("back", ""),
                data.get("example", ""),
                data.get("comment", ""),
                data.get("collocations", ""),
                data.get("etymology", ""),
            ],
            tags=tags or [],
            guid=data.get("guid"),
        )
        deck.add_note(note)

    output_path = Path(output_path)
    genanki.Package(deck).write_to_file(str(output_path))
    return output_path
