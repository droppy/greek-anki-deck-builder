"""English word/phrase normalization for cache keys."""
import re


def normalize_english(text: str) -> str:
    """Normalize an English word or phrase for use as a cache/DB key.

    - Lowercase
    - Strip leading 'to ' (infinitive verbs)
    - Normalize whitespace
    - Strip trailing punctuation
    """
    text = text.lower().strip()
    text = re.sub(r"^to\s+", "", text)
    text = re.sub(r"\s+", " ", text)
    text = text.rstrip(".,;:!?")
    return text
