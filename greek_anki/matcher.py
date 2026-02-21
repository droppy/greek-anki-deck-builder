"""Greek word matching and normalization."""
import re
import unicodedata
from typing import List

from Levenshtein import distance as levenshtein_distance

from .config import ARTICLES

# Latin-to-Greek confusable character map.
# The frequency CSV contains MICRO SIGN (U+00B5) instead of GREEK MU (U+03BC)
# in ~118 entries, and LATIN O (U+006F) instead of GREEK OMICRON (U+03BF) in ~11.
_CONFUSABLES = {
    "\u00b5": "\u03bc",  # MICRO SIGN -> GREEK SMALL MU
    "\u006f": "\u03bf",  # LATIN SMALL O -> GREEK SMALL OMICRON
    "\u004f": "\u039f",  # LATIN CAPITAL O -> GREEK CAPITAL OMICRON
}

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_ARTICLE_RE = None  # built lazily


def _get_article_re() -> re.Pattern:
    global _ARTICLE_RE
    if _ARTICLE_RE is None:
        alts = "|".join(sorted(ARTICLES, key=len, reverse=True))
        _ARTICLE_RE = re.compile(rf"^({alts})\s+", re.IGNORECASE)
    return _ARTICLE_RE


def normalize_greek(text: str) -> str:
    """Normalize Greek text for comparison.

    1. Replace Latin confusable characters with Greek equivalents
    2. Unicode NFC normalization
    3. Strip HTML tags
    4. Replace &nbsp; with space
    5. Strip leading articles
    6. Normalize whitespace
    7. Lowercase
    """
    for latin, greek in _CONFUSABLES.items():
        text = text.replace(latin, greek)

    text = unicodedata.normalize("NFC", text)
    text = _HTML_TAG_RE.sub("", text)
    text = text.replace("&nbsp;", " ").replace("\xa0", " ")

    text = text.strip()
    text = _get_article_re().sub("", text)

    text = " ".join(text.split())
    return text.lower().strip()


def extract_tokens(text: str) -> List[str]:
    """Extract individual word tokens from a potentially multi-word entry.

    Splits on comma, slash, and newline, normalizes each token.
    """
    # Split on newlines BEFORE normalization (normalize_greek collapses whitespace)
    lines = re.split(r"[\n\r]+", text)
    tokens = []
    for line in lines:
        norm = normalize_greek(line)
        parts = re.split(r"[,/]", norm)
        tokens.extend(t.strip() for t in parts if t.strip())
    return tokens


def find_note_by_word(word: str, notes) -> "AnkiNote | None":
    """Find a note in a list by fuzzy matching on Back field.

    Uses the same logic as freq_word_in_anki: article stripping,
    token extraction, exact match, then Levenshtein ≤ 1 for words > 3 chars.
    """
    norm = normalize_greek(word)
    for note in notes:
        tokens = extract_tokens(note.back)
        for token in tokens:
            if token == norm:
                return note
            if len(norm) > 3 and levenshtein_distance(token, norm) <= 1:
                return note
    return None


def freq_word_in_anki(freq_word: str, anki_back_fields: List[str]) -> bool:
    """Check if a frequency list word exists in any Anki Back field.

    Args:
        freq_word: A lemma from the frequency list.
        anki_back_fields: List of Back field values from existing Anki notes.

    Returns:
        True if the word is found in the deck.
    """
    freq_normalized = normalize_greek(freq_word)

    for back_field in anki_back_fields:
        tokens = extract_tokens(back_field)
        for token in tokens:
            if token == freq_normalized:
                return True
            if len(freq_normalized) > 3 and levenshtein_distance(token, freq_normalized) <= 1:
                return True

    return False
