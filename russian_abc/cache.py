"""Card cache for Russian alphabet — persists mnemonics and image paths."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .config import DEFAULT_CARD_CACHE

_SCHEMA = """\
CREATE TABLE IF NOT EXISTS letter_cache (
    letter       TEXT NOT NULL,
    age          INTEGER NOT NULL,
    gender       TEXT NOT NULL DEFAULT 'neutral',
    mnemonic     TEXT NOT NULL,
    fun_fact     TEXT,
    example_word TEXT,
    example_translation TEXT,
    sound_tip    TEXT,
    svg_content  TEXT,
    image_prompt TEXT,
    image_path   TEXT,
    model        TEXT NOT NULL,
    created_at   TEXT NOT NULL,
    PRIMARY KEY (letter, age, gender)
);
"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AbcCache:
    """SQLite-backed cache for Russian alphabet card data."""

    def __init__(self, db_path: str | Path = DEFAULT_CARD_CACHE):
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.executescript(_SCHEMA)
            self._conn.commit()
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def store(
        self,
        letter: str,
        age: int,
        gender: str,
        mnemonic: str,
        model: str,
        fun_fact: Optional[str] = None,
        example_word: Optional[str] = None,
        example_translation: Optional[str] = None,
        sound_tip: Optional[str] = None,
        svg_content: Optional[str] = None,
        image_prompt: Optional[str] = None,
        image_path: Optional[str] = None,
    ) -> None:
        """Upsert letter mnemonic data into cache."""
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO letter_cache "
            "(letter, age, gender, mnemonic, fun_fact, example_word, example_translation, "
            "sound_tip, svg_content, image_prompt, image_path, model, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(letter, age, gender) DO UPDATE SET "
            "mnemonic=excluded.mnemonic, fun_fact=excluded.fun_fact, "
            "example_word=excluded.example_word, example_translation=excluded.example_translation, "
            "sound_tip=excluded.sound_tip, svg_content=excluded.svg_content, "
            "image_prompt=excluded.image_prompt, "
            "image_path=COALESCE(excluded.image_path, letter_cache.image_path), "
            "model=excluded.model",
            (letter, age, gender, mnemonic, fun_fact, example_word,
             example_translation, sound_tip, svg_content, image_prompt, image_path,
             model, _now_iso()),
        )
        conn.commit()

    def update_image(self, letter: str, age: int, gender: str, image_path: str) -> None:
        """Update just the image path for an existing cached letter."""
        conn = self._get_conn()
        conn.execute(
            "UPDATE letter_cache SET image_path=? WHERE letter=? AND age=? AND gender=?",
            (image_path, letter, age, gender),
        )
        conn.commit()

    def get(self, letter: str, age: int, gender: str) -> Optional[dict]:
        """Look up cached letter data."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM letter_cache WHERE letter=? AND age=? AND gender=?",
            (letter, age, gender),
        ).fetchone()
        if row is None:
            return None
        return dict(row)

    def get_all(self, age: int, gender: str) -> Dict[str, dict]:
        """Get all cached letters for given age/gender."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM letter_cache WHERE age=? AND gender=?",
            (age, gender),
        ).fetchall()
        return {row["letter"]: dict(row) for row in rows}

    def letters_without_images(self, age: int, gender: str) -> List[dict]:
        """Get cached letters that don't have images yet."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM letter_cache WHERE age=? AND gender=? AND (image_path IS NULL OR image_path='')",
            (age, gender),
        ).fetchall()
        return [dict(row) for row in rows]

    def stats(self, age: Optional[int] = None, gender: Optional[str] = None) -> dict:
        """Return cache statistics."""
        conn = self._get_conn()
        conditions = []
        params = []
        if age is not None:
            conditions.append("age=?")
            params.append(age)
        if gender is not None:
            conditions.append("gender=?")
            params.append(gender)

        where = f" WHERE {' AND '.join(conditions)}" if conditions else ""

        total = conn.execute(f"SELECT COUNT(*) FROM letter_cache{where}", params).fetchone()[0]
        with_svg = conn.execute(
            f"SELECT COUNT(*) FROM letter_cache{where}"
            + (" AND" if conditions else " WHERE")
            + " svg_content IS NOT NULL AND svg_content != ''",
            params,
        ).fetchone()[0]
        with_images = conn.execute(
            f"SELECT COUNT(*) FROM letter_cache{where}"
            + (" AND" if conditions else " WHERE")
            + " image_path IS NOT NULL AND image_path != ''",
            params,
        ).fetchone()[0]

        return {
            "total": total,
            "with_svg": with_svg,
            "with_images": with_images,
            "without_visuals": total - max(with_svg, with_images),
        }
