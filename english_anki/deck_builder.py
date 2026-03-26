"""Assemble English C1+ cards into an Anki APKG deck."""
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import genanki

from .config import (
    CARD1_AFMT, CARD1_QFMT, CARD2_AFMT, CARD2_QFMT,
    CARD_CSS, FIELDS,
)
from .generator import GeneratedCard
from .normalizer import normalize_english


def deck_id_from_name(name: str) -> int:
    return int(hashlib.sha256(name.encode()).hexdigest()[:12], 16)


def _model_id_from_name(name: str) -> int:
    return int(hashlib.sha256(f"model:{name}".encode()).hexdigest()[:12], 16)


LANG_NAMES = {
    "ru": "RU", "th": "TH", "en": "EN", "zh": "ZH", "ja": "JA",
    "ko": "KO", "vi": "VI", "es": "ES", "fr": "FR", "de": "DE",
}


def get_english_model(deck_name: str = "English C1+", lang: str = "ru") -> genanki.Model:
    lang_label = LANG_NAMES.get(lang, lang.upper())
    return genanki.Model(
        _model_id_from_name(deck_name),
        f"{deck_name} Model",
        fields=[{"name": n} for n in FIELDS],
        templates=[
            {
                "name": f"Recognition (EN → {lang_label})",
                "qfmt": CARD1_QFMT,
                "afmt": CARD1_AFMT,
            },
            {
                "name": f"Recall ({lang_label} → EN)",
                "qfmt": CARD2_QFMT,
                "afmt": CARD2_AFMT,
            },
        ],
        css=CARD_CSS,
    )


def build_apkg(
    cards: Dict[str, GeneratedCard],
    deck_name: str = "English C1+",
    output_path: Optional[str | Path] = None,
    tags: Optional[List[str]] = None,
    lang: str = "ru",
) -> Path:
    """Build an APKG file from generated cards.

    Args:
        cards: Dict mapping normalized word -> GeneratedCard.
        deck_name: Name for the Anki deck.
        output_path: Output file path.
        tags: Base tags to apply to all cards.

    Returns:
        Path to the generated .apkg file.
    """
    if output_path is None:
        ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = Path(f"english_c1_{ts}.apkg")
    else:
        output_path = Path(output_path)

    model = get_english_model(deck_name, lang=lang)
    deck = genanki.Deck(deck_id_from_name(deck_name), deck_name)
    base_tags = tags or []

    import random
    items = list(cards.items())
    random.shuffle(items)

    for norm_word, card in items:
        note_data = card.to_note_dict()

        card_tags = list(base_tags)
        if card.part_of_speech:
            card_tags.append(f"pos::{card.part_of_speech.replace(' ', '-')}")
        reg = card.register.lower().split("/")[0].strip().replace(" ", "")
        if reg:
            card_tags.append(f"register::{reg}")

        note = genanki.Note(
            model=model,
            fields=[
                note_data["word"],
                note_data["definition"],
                note_data["example"],
                note_data["collocations"],
                note_data["synonyms"],
                note_data["register"],
            ],
            tags=card_tags,
            guid=genanki.guid_for(norm_word, deck_name),
        )
        deck.add_note(note)

    genanki.Package(deck).write_to_file(str(output_path))
    return output_path
