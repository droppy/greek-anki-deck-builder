"""Configuration constants for English C1+ deck."""
from pathlib import Path

DEFAULT_WORD_DB = "english_words.sq3"
DEFAULT_CARD_CACHE = "english_card_cache.sq3"
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_LANG = "ru"
PROMPTS_DIR = Path(__file__).parent.parent / "prompts" / "english"


def get_prompt_path(lang: str) -> Path:
    """Get prompt template path for a target language.

    Looks for prompts/english/card_prompt_{lang}.txt
    Raises FileNotFoundError if not found.
    """
    path = PROMPTS_DIR / f"card_prompt_{lang}.txt"
    if not path.exists():
        available = sorted(
            p.stem.replace("card_prompt_", "")
            for p in PROMPTS_DIR.glob("card_prompt_*.txt")
        )
        raise FileNotFoundError(
            f"No prompt template for language '{lang}'.\n"
            f"Expected file: {path}\n"
            f"Available languages: {', '.join(available) if available else 'none'}\n"
            f"Create {path.name} to add support for '{lang}'."
        )
    return path

# Anki field names
FIELDS = ["Word", "Definition", "Example", "Collocations", "Synonyms", "Register"]

# Card 1: Recognition — see English word, recall meaning/usage
CARD1_QFMT = """\
<div class="word">{{Word}}</div>"""

CARD1_AFMT = """\
<div class="word">{{Word}}</div>
{{#Collocations}}<div class="extras">{{Collocations}}</div>{{/Collocations}}
<hr>
<div class="definition">{{Definition}}</div>
{{#Example}}<div class="example">{{Example}}</div>{{/Example}}
{{#Synonyms}}<div class="synonyms"><b>Synonyms:</b> {{Synonyms}}</div>{{/Synonyms}}
{{#Register}}<div class="register">{{Register}}</div>{{/Register}}"""

# Card 2: Recall — see definition, recall English word
CARD2_QFMT = """\
<div class="definition">{{Definition}}</div>
{{#Example}}<div class="example hint-example">{{Example}}</div>{{/Example}}"""

CARD2_AFMT = """\
<div class="definition">{{Definition}}</div>
<hr>
<div class="word">{{Word}}</div>
{{#Collocations}}<div class="extras">{{Collocations}}</div>{{/Collocations}}
{{#Register}}<div class="register">{{Register}}</div>{{/Register}}
{{#Example}}<div class="example">{{Example}}</div>{{/Example}}
{{#Synonyms}}<div class="synonyms"><b>Synonyms:</b> {{Synonyms}}</div>{{/Synonyms}}"""

CARD_CSS = """\
.card {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 18px;
    text-align: left;
    padding: 24px 28px;
    background: #fafafa;
    color: #222;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.5;
}
.card-label {
    font-size: 13px;
    color: #999;
    font-style: italic;
    text-align: center;
    margin-bottom: 8px;
}
.word {
    font-size: 32px;
    font-weight: bold;
    text-align: center;
    color: #1a1a1a;
    margin: 12px 0;
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
}
.definition {
    font-size: 20px;
    color: #2c3e50;
    margin: 10px 0;
    text-align: center;
}
.example {
    font-family: 'Consolas', 'Menlo', 'Courier New', monospace;
    font-size: 15px;
    color: #34495e;
    margin: 10px 0;
    padding: 10px 14px;
    background: #f0f3f6;
    border-left: 3px solid #3498db;
    border-radius: 0 6px 6px 0;
    line-height: 1.6;
}
.hint-example {
    filter: blur(3px);
    transition: filter 0.3s;
}
.hint-example:hover, .hint-example:active {
    filter: none;
}
.collocations {
    font-size: 16px;
    color: #555;
    margin: 8px 0;
    padding: 8px 12px;
    background: rgba(39, 174, 96, 0.06);
    border-radius: 6px;
}
.synonyms {
    font-size: 16px;
    color: #555;
    margin: 8px 0;
    padding: 8px 12px;
    background: rgba(142, 68, 173, 0.06);
    border-radius: 6px;
}
.register {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    text-align: center;
    margin: 4px 0 8px;
    padding: 3px 10px;
    border-radius: 3px;
    display: inline-block;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-weight: 600;
}
.extras {
    text-align: center;
    margin: 4px 0;
}
hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 14px 0;
}

/* Night mode */
.nightMode .card { background: #1e1e1e; color: #ddd; }
.nightMode .word { color: #eee; }
.nightMode .definition { color: #ccc; }
.nightMode .example { background: #2a2a2a; color: #bbb; border-left-color: #5dade2; }
.nightMode .collocations { background: rgba(39,174,96,0.1); color: #aaa; }
.nightMode .synonyms { background: rgba(142,68,173,0.1); color: #aaa; }
.nightMode hr { border-top-color: #444; }"""
