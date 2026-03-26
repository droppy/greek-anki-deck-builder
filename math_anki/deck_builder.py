"""Assemble math problems + cached hints into an Anki APKG deck."""
import hashlib
import html
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import genanki

from .cache import MathCardCache
from .config import CARD_AFMT, CARD_CSS, CARD_QFMT, FIELDS
from .problems import MathProblem


def deck_id_from_name(name: str) -> int:
    """Generate a stable deck ID from a name."""
    h = int(hashlib.sha256(name.encode()).hexdigest()[:12], 16)
    return h


def _model_id_from_name(name: str) -> int:
    """Generate a stable model ID from a name."""
    h = int(hashlib.sha256(f"model:{name}".encode()).hexdigest()[:12], 16)
    return h


def get_math_model(deck_name: str = "Kids Math") -> genanki.Model:
    """Create the genanki Model for math cards."""
    return genanki.Model(
        _model_id_from_name(deck_name),
        f"{deck_name} Model",
        fields=[{"name": name} for name in FIELDS],
        templates=[
            {
                "name": "Math Card",
                "qfmt": CARD_QFMT,
                "afmt": CARD_AFMT,
            }
        ],
        css=CARD_CSS,
    )


def build_note_data(
    problem: MathProblem,
    hint_data: Optional[dict],
) -> dict:
    """Build a note data dict from a problem and its cached hint."""
    esc = html.escape

    # Problem field with colored inline style
    problem_html = problem.problem_html

    # Answer
    answer_str = str(problem.answer)

    # Hint and FunFact from cache
    hint = ""
    fun_fact = ""
    if hint_data:
        hint = hint_data.get("hint") or ""
        fun_fact = hint_data.get("fun_fact") or ""

    return {
        "problem": problem_html,
        "answer": answer_str,
        "hint": hint,
        "funfact": fun_fact,
    }


def build_apkg(
    problems: List[MathProblem],
    hints: Dict[str, dict],
    deck_name: str = "Kids Math",
    output_path: Optional[str | Path] = None,
    tags: Optional[List[str]] = None,
) -> Path:
    """Build an APKG file from problems and cached hints.

    Args:
        problems: List of MathProblem objects (already ordered).
        hints: Dict mapping problem.key -> hint_data dict.
        deck_name: Name for the Anki deck.
        output_path: Output file path (auto-generated if None).
        tags: Optional tags to apply to all cards.

    Returns:
        Path to the generated .apkg file.
    """
    if output_path is None:
        ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = Path(f"math_deck_{ts}.apkg")
    else:
        output_path = Path(output_path)

    model = get_math_model(deck_name)
    did = deck_id_from_name(deck_name)
    deck = genanki.Deck(did, deck_name)

    base_tags = tags or []

    for problem in problems:
        hint_data = hints.get(problem.key)
        note_data = build_note_data(problem, hint_data)

        # Per-card tags
        card_tags = list(base_tags)
        card_tags.append(f"level::{problem.level}")
        card_tags.append(f"op::{problem.op}")
        if hint_data and hint_data.get("difficulty"):
            card_tags.append(f"difficulty::{hint_data['difficulty']}")

        note = genanki.Note(
            model=model,
            fields=[
                note_data["problem"],
                note_data["answer"],
                note_data["hint"],
                note_data["funfact"],
            ],
            tags=card_tags,
            # Stable GUID from problem key + deck name
            guid=genanki.guid_for(problem.key, deck_name),
        )
        deck.add_note(note)

    genanki.Package(deck).write_to_file(str(output_path))
    return output_path
