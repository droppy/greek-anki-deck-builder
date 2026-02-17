"""Card cache — persists generated card data to avoid redundant API calls."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .claude_generator import GeneratedCard
from .config import DEFAULT_MODEL
from .matcher import normalize_greek

_SCHEMA = """\
CREATE TABLE IF NOT EXISTS card_cache (
    word_normalized TEXT PRIMARY KEY,
    word_original   TEXT NOT NULL,
    card_json       TEXT NOT NULL,
    model           TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);
"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _dict_to_card(data: dict) -> GeneratedCard:
    """Reconstruct a GeneratedCard from cached JSON data."""
    card = GeneratedCard(
        front_ru=data.get("front_ru", ""),
        front_en=data.get("front_en", ""),
        back=data.get("back", ""),
        part_of_speech=data.get("part_of_speech", "unknown"),
        examples=data.get("examples", []),
        conjugation=data.get("conjugation"),
        synonyms=data.get("synonyms", []),
        etymology_note=data.get("etymology_note"),
        collocations=data.get("collocations", []),
    )
    card._raw_data = data
    card.render_fields()
    return card


class CardCache:
    """SQLite-backed cache for generated card data."""

    def __init__(self, db_path: str | Path):
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

    def store(self, word: str, card_data: dict, model: str) -> None:
        """Upsert a card into the cache."""
        conn = self._get_conn()
        norm = normalize_greek(word)
        now = _now_iso()
        data_json = json.dumps(card_data, ensure_ascii=False)
        conn.execute(
            "INSERT INTO card_cache (word_normalized, word_original, card_json, model, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(word_normalized) DO UPDATE SET "
            "card_json=excluded.card_json, model=excluded.model, updated_at=excluded.updated_at",
            (norm, word, data_json, model, now, now),
        )
        conn.commit()

    def get(self, word: str) -> Optional[dict]:
        """Look up raw card data dict by word. Returns None if not cached."""
        conn = self._get_conn()
        norm = normalize_greek(word)
        row = conn.execute(
            "SELECT card_json FROM card_cache WHERE word_normalized=?", (norm,)
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["card_json"])

    def get_card(self, word: str) -> Optional[GeneratedCard]:
        """Look up and reconstruct a full GeneratedCard from cache."""
        data = self.get(word)
        if data is None:
            return None
        return _dict_to_card(data)

    def stats(self) -> dict:
        """Return cache statistics."""
        conn = self._get_conn()
        total = conn.execute("SELECT COUNT(*) FROM card_cache").fetchone()[0]
        model_rows = conn.execute(
            "SELECT model, COUNT(*) as cnt FROM card_cache GROUP BY model"
        ).fetchall()
        models = {row["model"]: row["cnt"] for row in model_rows}
        return {"total": total, "models": models}


def generate_card_cached(
    word: str,
    cache: CardCache,
    model: str = DEFAULT_MODEL,
    force: bool = False,
) -> GeneratedCard:
    """Generate a card, using cache if available.

    If force=True, always calls the API and updates the cache.
    """
    if not force:
        cached = cache.get_card(word)
        if cached is not None:
            return cached

    from .claude_generator import generate_card

    card = generate_card(word, model=model)
    cache.store(word, card._raw_data, model=model)
    return card
