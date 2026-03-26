"""Card cache — persists generated hints to avoid redundant API calls."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .config import DEFAULT_CARD_CACHE
from .problems import normalize_problem_key

_SCHEMA = """\
CREATE TABLE IF NOT EXISTS card_cache (
    problem_key  TEXT NOT NULL,
    age          INTEGER NOT NULL,
    hint         TEXT NOT NULL,
    fun_fact     TEXT,
    difficulty   TEXT,
    image_desc   TEXT,
    model        TEXT NOT NULL,
    created_at   TEXT NOT NULL,
    PRIMARY KEY (problem_key, age)
);
"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MathCardCache:
    """SQLite-backed cache for math card hints, keyed by (problem_key, age)."""

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
        problem_key: str,
        age: int,
        hint: str,
        fun_fact: Optional[str],
        difficulty: Optional[str],
        model: str,
        image_desc: Optional[str] = None,
    ) -> None:
        """Upsert a hint into the cache."""
        conn = self._get_conn()
        key = normalize_problem_key(problem_key)
        conn.execute(
            "INSERT INTO card_cache (problem_key, age, hint, fun_fact, difficulty, image_desc, model, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(problem_key, age) DO UPDATE SET "
            "hint=excluded.hint, fun_fact=excluded.fun_fact, "
            "difficulty=excluded.difficulty, image_desc=excluded.image_desc, "
            "model=excluded.model",
            (key, age, hint, fun_fact, difficulty, image_desc, model, _now_iso()),
        )
        conn.commit()

    def get(self, problem_key: str, age: int) -> Optional[dict]:
        """Look up cached hint data. Returns dict with hint, fun_fact, difficulty, image_desc."""
        conn = self._get_conn()
        key = normalize_problem_key(problem_key)
        row = conn.execute(
            "SELECT hint, fun_fact, difficulty, image_desc FROM card_cache "
            "WHERE problem_key=? AND age=?",
            (key, age),
        ).fetchone()
        if row is None:
            return None
        return dict(row)

    def get_batch(self, problem_keys: List[str], age: int) -> Dict[str, dict]:
        """Look up multiple problem keys at once. Returns {key: data_dict}."""
        conn = self._get_conn()
        keys = [normalize_problem_key(k) for k in problem_keys]
        result = {}
        # SQLite has a variable limit; batch in chunks of 500
        for i in range(0, len(keys), 500):
            chunk = keys[i : i + 500]
            placeholders = ",".join("?" * len(chunk))
            rows = conn.execute(
                f"SELECT problem_key, hint, fun_fact, difficulty, image_desc "
                f"FROM card_cache WHERE age=? AND problem_key IN ({placeholders})",
                [age] + chunk,
            ).fetchall()
            for row in rows:
                result[row["problem_key"]] = {
                    "hint": row["hint"],
                    "fun_fact": row["fun_fact"],
                    "difficulty": row["difficulty"],
                    "image_desc": row["image_desc"],
                }
        return result

    def stats(self, age: Optional[int] = None) -> dict:
        """Return cache statistics."""
        conn = self._get_conn()
        if age is not None:
            total = conn.execute(
                "SELECT COUNT(*) FROM card_cache WHERE age=?", (age,)
            ).fetchone()[0]
            model_rows = conn.execute(
                "SELECT model, COUNT(*) as cnt FROM card_cache WHERE age=? GROUP BY model",
                (age,),
            ).fetchall()
        else:
            total = conn.execute("SELECT COUNT(*) FROM card_cache").fetchone()[0]
            model_rows = conn.execute(
                "SELECT model, COUNT(*) as cnt FROM card_cache GROUP BY model"
            ).fetchall()
        models = {row["model"]: row["cnt"] for row in model_rows}
        ages_rows = conn.execute(
            "SELECT age, COUNT(*) as cnt FROM card_cache GROUP BY age"
        ).fetchall()
        ages = {row["age"]: row["cnt"] for row in ages_rows}
        return {"total": total, "models": models, "ages": ages}
