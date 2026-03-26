"""Configuration constants for Russian alphabet deck."""
from pathlib import Path

# Default file names
DEFAULT_CARD_CACHE = "russian_abc_cache.sq3"
DEFAULT_IMAGE_DIR = "russian_abc_images"

# Claude API
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
MNEMONIC_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "russian_abc" / "mnemonic_prompt.txt"
IMAGE_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "russian_abc" / "image_prompt.txt"

# DALL-E defaults
DALLE_MODEL = "dall-e-3"
DALLE_SIZE = "1024x1024"
DALLE_QUALITY = "standard"

# Anki field names
FIELDS = ["Letter", "Name", "Sound", "Mnemonic", "ExampleWord", "Visual"]

# Card template — front (question side): show the letter large
CARD_QFMT = """\
<div class="letter-display">{{Letter}}</div>
<div class="letter-type">{{Name}}</div>"""

# Card template — back (answer side): reveal everything
CARD_AFMT = """\
<div class="letter-display">{{Letter}}</div>
<div class="letter-name">{{Name}}</div>
<hr>
<div class="sound">{{Sound}}</div>
<hr>
<div class="mnemonic">{{Mnemonic}}</div>
{{#ExampleWord}}
<hr>
<div class="example">{{ExampleWord}}</div>
{{/ExampleWord}}
{{#Visual}}
<div class="visual">{{Visual}}</div>
{{/Visual}}"""

# Kid-friendly CSS for alphabet cards
CARD_CSS = """\
.card {
    font-family: 'Comic Sans MS', 'Chalkboard SE', 'Comic Neue', cursive, sans-serif;
    text-align: center;
    padding: 20px;
    min-height: 300px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.letter-display {
    font-size: 80px;
    font-weight: bold;
    color: #2c3e50;
    margin: 10px 0;
    line-height: 1.1;
}
.letter-name {
    font-size: 22px;
    color: #7f8c8d;
    margin: 5px 0;
}
.letter-type {
    font-size: 18px;
    color: #95a5a6;
    font-style: italic;
}
.sound {
    font-size: 26px;
    color: #2980b9;
    margin: 10px 0;
}
.mnemonic {
    font-size: 20px;
    color: #8e44ad;
    margin: 10px 0;
    line-height: 1.5;
    padding: 10px;
    background: rgba(142, 68, 173, 0.08);
    border-radius: 10px;
}
.example {
    font-size: 22px;
    color: #27ae60;
    margin: 10px 0;
}
.visual {
    margin: 15px auto;
    max-width: 300px;
}
.visual img {
    max-width: 100%;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
hr {
    border: none;
    border-top: 2px dashed #bdc3c7;
    margin: 12px 0;
}

/* Vowel cards get warm background */
.vowel .card { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); }
/* Consonant cards get cool background */
.consonant .card { background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%); }
/* Sign cards get neutral background */
.sign .card { background: linear-gradient(135deg, #e0e0e0 0%, #f5f5f5 100%); }"""

# Background colors by letter type (inline style fallback)
LETTER_TYPE_COLORS = {
    "vowel": "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
    "consonant": "linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)",
    "sign": "linear-gradient(135deg, #e0e0e0 0%, #f5f5f5 100%)",
}
