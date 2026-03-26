"""Configuration constants for Russian dictionary deck."""
from pathlib import Path

DEFAULT_CARD_CACHE = "russian_dict_cache.sq3"
DEFAULT_IMAGE_DIR = "russian_dict_images"
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
WORD_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "russian_dict" / "word_prompt.txt"

FIELDS = ["Word", "Translation", "Example", "Mnemonic", "Visual"]

# Card 1: Recognition — see Russian, recall English
CARD1_QFMT = """\
<div class="card-label">What does this mean?</div>
<div class="word">{{Word}}</div>"""

CARD1_AFMT = """\
<div class="word">{{Word}}</div>
<hr>
<div class="translation">{{Translation}}</div>
{{#Example}}
<div class="example">{{Example}}</div>
{{/Example}}
{{#Mnemonic}}
<div class="mnemonic">{{Mnemonic}}</div>
{{/Mnemonic}}
{{#Visual}}
<div class="visual">{{Visual}}</div>
{{/Visual}}"""

# Card 2: Recall — see English + picture, recall Russian
CARD2_QFMT = """\
<div class="card-label">How do you say this in Russian?</div>
<div class="translation">{{Translation}}</div>
{{#Visual}}
<div class="visual">{{Visual}}</div>
{{/Visual}}"""

CARD2_AFMT = """\
<div class="translation">{{Translation}}</div>
<hr>
<div class="word">{{Word}}</div>
{{#Example}}
<div class="example">{{Example}}</div>
{{/Example}}
{{#Mnemonic}}
<div class="mnemonic">{{Mnemonic}}</div>
{{/Mnemonic}}
{{#Visual}}
<div class="visual">{{Visual}}</div>
{{/Visual}}"""

CARD_CSS = """\
.card {
    font-family: 'Comic Sans MS', 'Chalkboard SE', 'Comic Neue', cursive, sans-serif;
    text-align: center;
    padding: 20px;
    min-height: 250px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
.word {
    font-size: 48px;
    font-weight: bold;
    color: #2c3e50;
    margin: 15px 0;
}
.translation {
    font-size: 28px;
    color: #27ae60;
    margin: 10px 0;
}
.example {
    font-size: 20px;
    color: #2980b9;
    margin: 10px 0;
    line-height: 1.5;
    padding: 8px;
    background: rgba(41, 128, 185, 0.08);
    border-radius: 8px;
}
.mnemonic {
    font-size: 18px;
    color: #8e44ad;
    margin: 10px 0;
    padding: 8px;
    background: rgba(142, 68, 173, 0.08);
    border-radius: 8px;
}
.visual {
    margin: 12px auto;
    max-width: 250px;
}
.visual img {
    max-width: 100%;
    border-radius: 10px;
}
hr {
    border: none;
    border-top: 2px dashed #bdc3c7;
    margin: 12px 0;
}
.card-label {
    font-size: 14px;
    color: #95a5a6;
    font-style: italic;
    margin-bottom: 5px;
}"""
