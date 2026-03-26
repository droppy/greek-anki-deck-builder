"""Card cache for Russian dictionary — persists translations, examples, SVGs."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .config import DEFAULT_CARD_CACHE

_SCHEMA = """\
CREATE TABLE IF NOT EXISTS word_cache (
    word         TEXT NOT NULL,
    age          INTEGER NOT NULL,
    gender       TEXT NOT NULL DEFAULT 'neutral',
    translation  TEXT NOT NULL,
    example_ru   TEXT,
    example_en   TEXT,
    mnemonic     TEXT,
    svg_content  TEXT,
    image_path   TEXT,
    model        TEXT NOT NULL,
    created_at   TEXT NOT NULL,
    PRIMARY KEY (word, age, gender)
);
"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DictCache:
    """SQLite-backed cache for word card data."""

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

    def store(self, word: str, age: int, gender: str, translation: str,
              model: str, example_ru: str = None, example_en: str = None,
              mnemonic: str = None, svg_content: str = None,
              image_path: str = None) -> None:
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO word_cache "
            "(word, age, gender, translation, example_ru, example_en, mnemonic, "
            "svg_content, image_path, model, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(word, age, gender) DO UPDATE SET "
            "translation=excluded.translation, example_ru=excluded.example_ru, "
            "example_en=excluded.example_en, mnemonic=excluded.mnemonic, "
            "svg_content=excluded.svg_content, "
            "image_path=COALESCE(excluded.image_path, word_cache.image_path), "
            "model=excluded.model",
            (word.lower(), age, gender, translation, example_ru, example_en,
             mnemonic, svg_content, image_path, model, _now_iso()),
        )
        conn.commit()

    def get(self, word: str, age: int, gender: str) -> Optional[dict]:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM word_cache WHERE word=? AND age=? AND gender=?",
            (word.lower(), age, gender),
        ).fetchone()
        return dict(row) if row else None

    def get_batch(self, words: List[str], age: int, gender: str) -> Dict[str, dict]:
        conn = self._get_conn()
        keys = [w.lower() for w in words]
        result = {}
        for i in range(0, len(keys), 500):
            chunk = keys[i:i + 500]
            placeholders = ",".join("?" * len(chunk))
            rows = conn.execute(
                f"SELECT * FROM word_cache WHERE age=? AND gender=? AND word IN ({placeholders})",
                [age, gender] + chunk,
            ).fetchall()
            for row in rows:
                result[row["word"]] = dict(row)
        return result

    def stats(self, age: Optional[int] = None, gender: Optional[str] = None) -> dict:
        conn = self._get_conn()
        conditions, params = [], []
        if age is not None:
            conditions.append("age=?"); params.append(age)
        if gender is not None:
            conditions.append("gender=?"); params.append(gender)
        where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        total = conn.execute(f"SELECT COUNT(*) FROM word_cache{where}", params).fetchone()[0]
        with_svg = conn.execute(
            f"SELECT COUNT(*) FROM word_cache{where}"
            + (" AND" if conditions else " WHERE")
            + " svg_content IS NOT NULL AND svg_content != ''", params,
        ).fetchone()[0]
        return {"total": total, "with_svg": with_svg}
