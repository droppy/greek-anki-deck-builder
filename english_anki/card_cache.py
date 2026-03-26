"""Card cache — persists generated C1+ card data."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .config import DEFAULT_CARD_CACHE
from .normalizer import normalize_english

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


class CardCache:
    """SQLite-backed cache for generated card data."""

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

    def store(self, word: str, card_data: dict, model: str) -> None:
        """Upsert a card into the cache."""
        conn = self._get_conn()
        norm = normalize_english(word)
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
        """Look up raw card data dict by word."""
        conn = self._get_conn()
        norm = normalize_english(word)
        row = conn.execute(
            "SELECT card_json FROM card_cache WHERE word_normalized=?", (norm,)
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["card_json"])

    def get_batch(self, words: List[str]) -> Dict[str, dict]:
        """Look up multiple words. Returns {normalized_key: data_dict}."""
        conn = self._get_conn()
        keys = [normalize_english(w) for w in words]
        result = {}
        for i in range(0, len(keys), 500):
            chunk = keys[i:i + 500]
            placeholders = ",".join("?" * len(chunk))
            rows = conn.execute(
                f"SELECT word_normalized, card_json FROM card_cache "
                f"WHERE word_normalized IN ({placeholders})", chunk,
            ).fetchall()
            for row in rows:
                result[row["word_normalized"]] = json.loads(row["card_json"])
        return result

    def stats(self) -> dict:
        conn = self._get_conn()
        total = conn.execute("SELECT COUNT(*) FROM card_cache").fetchone()[0]
        model_rows = conn.execute(
            "SELECT model, COUNT(*) as cnt FROM card_cache GROUP BY model"
        ).fetchall()
        return {"total": total, "models": {r["model"]: r["cnt"] for r in model_rows}}
