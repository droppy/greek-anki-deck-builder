"""Unified word database — tracks built-in lists and user-added words."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .config import DEFAULT_WORD_DB
from .normalizer import normalize_english

PENDING, IN_ANKI, SKIPPED = 0, 1, 2

_SCHEMA = """\
CREATE TABLE IF NOT EXISTS words (
    word       TEXT PRIMARY KEY,
    original   TEXT NOT NULL,
    category   TEXT NOT NULL,
    hint       TEXT,
    processed  INTEGER DEFAULT 0,
    added_at   TEXT NOT NULL,
    notes      TEXT
);
"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class WordDB:
    """SQLite database for English word tracking."""

    def __init__(self, db_path: str | Path = DEFAULT_WORD_DB):
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

    def import_list(self, words: list, category: str) -> dict:
        """Import a list of (word, hint) tuples. Returns stats."""
        conn = self._get_conn()
        imported, skipped = 0, 0
        now = _now_iso()
        for word, hint in words:
            norm = normalize_english(word)
            try:
                conn.execute(
                    "INSERT INTO words (word, original, category, hint, processed, added_at) "
                    "VALUES (?, ?, ?, ?, 0, ?)",
                    (norm, word, category, hint, now),
                )
                imported += 1
            except sqlite3.IntegrityError:
                skipped += 1
        conn.commit()
        return {"imported": imported, "skipped": skipped, "total": imported + skipped}

    def add_user_word(self, word: str, hint: str = None) -> bool:
        """Add a user-picked word. Returns True if new, False if already exists."""
        conn = self._get_conn()
        norm = normalize_english(word)
        try:
            conn.execute(
                "INSERT INTO words (word, original, category, hint, processed, added_at) "
                "VALUES (?, ?, 'user', ?, 0, ?)",
                (norm, word, hint, _now_iso()),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_pending(self, category: str = None, limit: int = None) -> List[dict]:
        """Get unprocessed words, optionally filtered by category."""
        conn = self._get_conn()
        sql = "SELECT * FROM words WHERE processed=0"
        params = []
        if category:
            sql += " AND category=?"
            params.append(category)
        sql += " ORDER BY added_at"
        if limit:
            sql += " LIMIT ?"
            params.append(limit)
        return [dict(row) for row in conn.execute(sql, params).fetchall()]

    def get_by_category(self, category: str) -> List[dict]:
        """Get all words in a category (regardless of processed state)."""
        conn = self._get_conn()
        return [dict(row) for row in conn.execute(
            "SELECT * FROM words WHERE category=? ORDER BY original", (category,)
        ).fetchall()]

    def get_all(self) -> List[dict]:
        """Get all words."""
        conn = self._get_conn()
        return [dict(row) for row in conn.execute(
            "SELECT * FROM words ORDER BY category, original"
        ).fetchall()]

    def mark_processed(self, word: str, status: int = IN_ANKI, notes: str = None) -> bool:
        """Mark a word as processed. Returns True if found."""
        conn = self._get_conn()
        norm = normalize_english(word)
        result = conn.execute(
            "UPDATE words SET processed=?, notes=? WHERE word=?",
            (status, notes, norm),
        )
        conn.commit()
        return result.rowcount > 0

    def exists(self, word: str) -> bool:
        """Check if a word exists in the DB."""
        conn = self._get_conn()
        norm = normalize_english(word)
        return conn.execute(
            "SELECT 1 FROM words WHERE word=?", (norm,)
        ).fetchone() is not None

    def stats(self, category: str = None) -> dict:
        """Return word counts by category and processed state."""
        conn = self._get_conn()
        where = f" WHERE category='{category}'" if category else ""
        total = conn.execute(f"SELECT COUNT(*) FROM words{where}").fetchone()[0]
        pending = conn.execute(
            f"SELECT COUNT(*) FROM words{where}"
            + (" AND" if category else " WHERE") + " processed=0"
        ).fetchone()[0]
        in_anki = conn.execute(
            f"SELECT COUNT(*) FROM words{where}"
            + (" AND" if category else " WHERE") + " processed=1"
        ).fetchone()[0]
        skipped = conn.execute(
            f"SELECT COUNT(*) FROM words{where}"
            + (" AND" if category else " WHERE") + " processed=2"
        ).fetchone()[0]

        cats = {}
        for row in conn.execute(
            "SELECT category, COUNT(*) as cnt FROM words GROUP BY category ORDER BY cnt DESC"
        ).fetchall():
            cats[row["category"]] = row["cnt"]

        return {
            "total": total, "pending": pending,
            "in_anki": in_anki, "skipped": skipped,
            "categories": cats,
        }
