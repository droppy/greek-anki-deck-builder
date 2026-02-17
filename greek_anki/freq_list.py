"""Frequency list management (SQLite)."""
import csv
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from .config import FUNCTION_WORDS
from .matcher import normalize_greek

_SCHEMA = """\
CREATE TABLE IF NOT EXISTS freq_words (
    rank        INTEGER PRIMARY KEY,
    greek       TEXT NOT NULL,
    frequency   INTEGER NOT NULL,
    processed   INTEGER DEFAULT 0,
    processed_at TEXT,
    notes       TEXT
);
CREATE INDEX IF NOT EXISTS idx_greek ON freq_words(greek);
CREATE INDEX IF NOT EXISTS idx_processed ON freq_words(processed);
"""

# processed states
PENDING = 0
IN_ANKI = 1
SKIPPED = 2


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class FreqDB:
    """Interface to the frequency list SQLite database."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def init_schema(self):
        conn = self._get_conn()
        conn.executescript(_SCHEMA)
        conn.commit()

    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------

    def import_csv(
        self,
        csv_path: str | Path,
        auto_skip_function_words: bool = True,
    ) -> dict:
        """Import frequency CSV into the database.

        Returns dict with import statistics.
        """
        csv_path = Path(csv_path)
        conn = self._get_conn()
        self.init_schema()

        stats = {
            "total_rows": 0,
            "imported": 0,
            "duplicates_skipped": 0,
            "empty_skipped": 0,
            "function_words_skipped": 0,
        }

        norm_function_words = {normalize_greek(w) for w in FUNCTION_WORDS}

        # Track seen normalized forms to catch micro-sign / latin-o dupes
        seen_normalized: dict[str, int] = {}

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header

            for row_num, row in enumerate(reader, start=1):
                stats["total_rows"] += 1

                if not row or not row[0].strip():
                    stats["empty_skipped"] += 1
                    continue

                lemma = row[0].strip()
                try:
                    frequency = int(row[1])
                except (IndexError, ValueError):
                    stats["empty_skipped"] += 1
                    continue

                normalized = normalize_greek(lemma)

                # Normalized-form dedup: keep higher-ranked (lower row_num)
                if normalized in seen_normalized:
                    stats["duplicates_skipped"] += 1
                    continue
                seen_normalized[normalized] = row_num

                is_function = normalized in norm_function_words

                try:
                    if is_function and auto_skip_function_words:
                        conn.execute(
                            "INSERT INTO freq_words "
                            "(rank, greek, frequency, processed, processed_at, notes) "
                            "VALUES (?, ?, ?, ?, ?, ?)",
                            (
                                row_num,
                                lemma,
                                frequency,
                                SKIPPED,
                                _now_iso(),
                                "auto-skip: function word",
                            ),
                        )
                        stats["function_words_skipped"] += 1
                    else:
                        conn.execute(
                            "INSERT INTO freq_words (rank, greek, frequency) "
                            "VALUES (?, ?, ?)",
                            (row_num, lemma, frequency),
                        )
                    stats["imported"] += 1
                except sqlite3.IntegrityError:
                    stats["duplicates_skipped"] += 1

        conn.commit()
        return stats

    # ------------------------------------------------------------------
    # Marking
    # ------------------------------------------------------------------

    def mark_processed(
        self,
        greek: str,
        status: int = IN_ANKI,
        notes: Optional[str] = None,
    ) -> bool:
        """Mark a word as processed. Returns True if a row was updated."""
        conn = self._get_conn()

        # Exact match first
        cursor = conn.execute(
            "UPDATE freq_words SET processed=?, processed_at=?, notes=? "
            "WHERE greek=?",
            (status, _now_iso(), notes, greek),
        )
        if cursor.rowcount > 0:
            conn.commit()
            return True

        # Fallback: normalized match
        normalized = normalize_greek(greek)
        rows = conn.execute(
            "SELECT rank, greek FROM freq_words WHERE processed=0"
        ).fetchall()
        for row in rows:
            if normalize_greek(row["greek"]) == normalized:
                conn.execute(
                    "UPDATE freq_words SET processed=?, processed_at=?, notes=? "
                    "WHERE rank=?",
                    (status, _now_iso(), notes, row["rank"]),
                )
                conn.commit()
                return True

        return False

    def mark_many_processed(
        self,
        greeks: List[str],
        status: int = IN_ANKI,
        notes: Optional[str] = None,
    ) -> int:
        """Batch mark words as processed. Returns count of updated rows."""
        conn = self._get_conn()
        all_rows = conn.execute(
            "SELECT rank, greek FROM freq_words WHERE processed=0"
        ).fetchall()

        norm_to_rank: dict[str, int] = {}
        for row in all_rows:
            norm = normalize_greek(row["greek"])
            norm_to_rank[norm] = row["rank"]

        updated = 0
        now = _now_iso()
        for word in greeks:
            norm = normalize_greek(word)
            if norm in norm_to_rank:
                conn.execute(
                    "UPDATE freq_words SET processed=?, processed_at=?, notes=? "
                    "WHERE rank=?",
                    (status, now, notes, norm_to_rank[norm]),
                )
                updated += 1

        conn.commit()
        return updated

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_pending(
        self,
        range_start: Optional[int] = None,
        range_end: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[sqlite3.Row]:
        """Get pending (unprocessed) words, optionally in a rank range."""
        conn = self._get_conn()
        query = "SELECT * FROM freq_words WHERE processed=0"
        params: list = []

        if range_start is not None:
            query += " AND rank >= ?"
            params.append(range_start)
        if range_end is not None:
            query += " AND rank <= ?"
            params.append(range_end)

        query += " ORDER BY rank"

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        return conn.execute(query, params).fetchall()

    def get_range(
        self,
        range_start: int,
        range_end: int,
    ) -> List[sqlite3.Row]:
        """Get all words in a rank range, regardless of processed state.

        Excludes only auto-skipped function words (articles, prepositions, etc.).
        Used by build-deck to assemble shareable decks.
        """
        conn = self._get_conn()
        return conn.execute(
            "SELECT * FROM freq_words "
            "WHERE rank >= ? AND rank <= ? "
            "AND NOT (processed = 2 AND notes LIKE 'auto-skip%') "
            "ORDER BY rank",
            (range_start, range_end),
        ).fetchall()

    def get_status_summary(self) -> dict:
        """Get summary statistics for the status dashboard."""
        conn = self._get_conn()

        total = conn.execute("SELECT COUNT(*) FROM freq_words").fetchone()[0]
        in_anki = conn.execute(
            "SELECT COUNT(*) FROM freq_words WHERE processed=1"
        ).fetchone()[0]
        skipped = conn.execute(
            "SELECT COUNT(*) FROM freq_words WHERE processed=2"
        ).fetchone()[0]
        pending = conn.execute(
            "SELECT COUNT(*) FROM freq_words WHERE processed=0"
        ).fetchone()[0]

        max_rank = (
            conn.execute("SELECT MAX(rank) FROM freq_words").fetchone()[0] or 0
        )

        ranges = []
        for start in range(1, max_rank + 1, 500):
            end = start + 499
            row = conn.execute(
                "SELECT "
                "  COUNT(*) as total, "
                "  SUM(CASE WHEN processed=1 THEN 1 ELSE 0 END) as in_anki, "
                "  SUM(CASE WHEN processed=0 THEN 1 ELSE 0 END) as pending, "
                "  SUM(CASE WHEN processed=2 THEN 1 ELSE 0 END) as skipped "
                "FROM freq_words WHERE rank BETWEEN ? AND ?",
                (start, end),
            ).fetchone()
            ranges.append(
                {
                    "start": start,
                    "end": end,
                    "total": row[0],
                    "in_anki": row[1],
                    "pending": row[2],
                    "skipped": row[3],
                }
            )

        return {
            "total": total,
            "in_anki": in_anki,
            "skipped": skipped,
            "pending": pending,
            "ranges": ranges,
        }

    def skip_words(
        self,
        words: List[str],
        reason: Optional[str] = None,
    ) -> int:
        """Mark words as skipped. Returns count of updated rows."""
        return self.mark_many_processed(
            words,
            status=SKIPPED,
            notes=f"manual skip: {reason}" if reason else "manual skip",
        )

    def get_word_by_greek(self, greek: str) -> Optional[sqlite3.Row]:
        """Look up a word by its Greek text (normalized matching)."""
        conn = self._get_conn()

        row = conn.execute(
            "SELECT * FROM freq_words WHERE greek=?", (greek,)
        ).fetchone()
        if row:
            return row

        normalized = normalize_greek(greek)
        all_rows = conn.execute("SELECT * FROM freq_words").fetchall()
        for r in all_rows:
            if normalize_greek(r["greek"]) == normalized:
                return r
        return None
