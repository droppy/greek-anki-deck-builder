"""Configuration constants and defaults."""
from pathlib import Path

# Anki IDs (hardcoded from existing deck)
DECK_ID = 1728801742169
DECK_NAME = "AZ greek words"
MODEL_ID = 1722180007066
MODEL_NAME = "Basic"

# Field names in order
FIELDS = ["Front", "Back", "Example", "Comment", "Collocations", "Etymology"]

# Default file names
DEFAULT_FREQ_DB = "freq_list.sq3"
DEFAULT_APKG = "AZ_greek_words_new_fields.apkg"
DEFAULT_CARD_CACHE = "card_cache.sq3"

# Claude API
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
PROMPT_TEMPLATE_PATH = Path(__file__).parent.parent / "prompts" / "card_prompt.txt"

# Card template
CARD_CSS = """.card {
    font-family: arial;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
}"""

CARD_QFMT = "{{Back}}"
CARD_AFMT = (
    "{{FrontSide}}\n\n<hr id=answer>\n\n"
    "{{Front}}\n<hr/>\n{{Example}}\n<hr/>\n{{Comment}}"
    "\n<hr/>\n{{Collocations}}\n<hr/>\n{{Etymology}}"
)

# Function words to auto-skip on import (articles, prepositions,
# conjunctions, pronouns, particles, negation)
FUNCTION_WORDS = {
    # Articles
    "ο", "η", "το", "τo",  # τo with Latin o exists at rank 5 in CSV
    "οι", "τα", "ένας", "μία", "ένα",
    # Prepositions
    "από", "σε", "με", "για", "προς",
    "κατά", "μετά", "παρά", "αντί", "ως",
    # Conjunctions
    "και", "ή", "αλλά", "όμως", "ούτε",
    "ότι", "ώστε", "αν", "όταν", "ενώ",
    # Pronouns / particles
    "εγώ", "εσύ", "αυτός", "αυτή", "αυτό",
    "εμείς", "εσείς", "αυτοί", "αυτές", "αυτά",
    "μου", "σου", "του", "της", "μας", "σας", "τους",
    # Relative / interrogative
    "που", "ποιος",
    "τι", "πώς", "πόσος", "οποίος",
    # Particles / negation
    "να", "θα", "δεν", "δε", "μην",
    "πιο", "πολύ",
}

# Greek articles for stripping during matching
ARTICLES = {"ο", "η", "το", "οι", "τα", "τις", "τους", "την", "τον"}
