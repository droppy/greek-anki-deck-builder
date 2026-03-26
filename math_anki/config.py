"""Configuration constants and defaults for math deck."""
from pathlib import Path

# Default file names
DEFAULT_CARD_CACHE = "math_card_cache.sq3"

# Claude API
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
HINT_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "math" / "hint_prompt.txt"
ORDER_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "math" / "order_prompt.txt"

# Anki field names in order
FIELDS = ["Problem", "Answer", "Hint", "FunFact"]

# Operation colors (inline style in Problem field)
OP_COLORS = {
    "+": "#27ae60",  # green
    "-": "#e74c3c",  # red
    "*": "#2980b9",  # blue
    "/": "#e67e22",  # orange
}

# Display symbols for operations
OP_SYMBOLS = {
    "+": "+",
    "-": "\u2212",   # minus sign
    "*": "\u00d7",   # multiplication sign
    "/": "\u00f7",   # division sign
}

# Card template — front (question side)
CARD_QFMT = """\
<div class="problem">{{Problem}}</div>
<details class="hint-toggle">
  <summary>\U0001f4a1 Need a hint?</summary>
  <div class="hint">{{Hint}}</div>
</details>"""

# Card template — back (answer side)
CARD_AFMT = """\
<div class="problem">{{Problem}}</div>
<div class="answer">{{Answer}}</div>
<hr>
<div class="hint">{{Hint}}</div>
{{#FunFact}}
<div class="funfact">\U0001f389 {{FunFact}}</div>
{{/FunFact}}"""

# Kid-friendly CSS
CARD_CSS = """\
.card {
    font-family: 'Comic Sans MS', 'Chalkboard SE', 'Comic Neue', cursive, sans-serif;
    text-align: center;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 20px;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.problem {
    font-size: 42px;
    font-weight: bold;
    margin: 20px 0;
    color: #2c3e50;
}
.answer {
    font-size: 56px;
    font-weight: bold;
    color: #27ae60;
    margin: 15px 0;
}
.hint {
    font-size: 24px;
    margin: 15px 0;
    line-height: 1.6;
}
.hint-toggle summary {
    font-size: 18px;
    cursor: pointer;
    color: #7f8c8d;
    margin-top: 10px;
}
.hint-toggle[open] summary {
    margin-bottom: 5px;
}
.funfact {
    font-size: 18px;
    color: #8e44ad;
    margin-top: 15px;
    padding: 10px;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 10px;
}
hr {
    border: none;
    border-top: 2px dashed #bdc3c7;
    margin: 15px 0;
}"""

# Level definitions: (description, operations, a_range, b_range, constraints)
LEVELS = {
    1: {
        "name": "Addition basics",
        "description": "Single-digit addition (0-9 + 0-9)",
        "ops": ["+"],
        "a_range": (0, 9),
        "b_range": (0, 9),
    },
    2: {
        "name": "Subtraction basics",
        "description": "Single-digit subtraction (result \u2265 0)",
        "ops": ["-"],
        "a_range": (0, 9),
        "b_range": (0, 9),
    },
    3: {
        "name": "Mixed add & subtract",
        "description": "Single-digit addition and subtraction mixed",
        "ops": ["+", "-"],
        "a_range": (0, 9),
        "b_range": (0, 9),
    },
    4: {
        "name": "Multiplication tables",
        "description": "Single-digit multiplication (0-9 \u00d7 0-9)",
        "ops": ["*"],
        "a_range": (0, 9),
        "b_range": (0, 9),
    },
    5: {
        "name": "Exact division",
        "description": "Division with whole-number results (divisor 1-9)",
        "ops": ["/"],
        "a_range": (1, 9),  # quotient range
        "b_range": (1, 9),  # divisor range
    },
    6: {
        "name": "Two-digit addition",
        "description": "Two-digit + single-digit (10-19 + 1-9)",
        "ops": ["+"],
        "a_range": (10, 19),
        "b_range": (1, 9),
    },
    7: {
        "name": "Two-digit subtraction",
        "description": "Two-digit \u2212 single-digit (10-19 \u2212 1-9)",
        "ops": ["-"],
        "a_range": (10, 19),
        "b_range": (1, 9),
    },
    8: {
        "name": "Mixed all operations",
        "description": "All four operations with single and two-digit numbers",
        "ops": ["+", "-", "*", "/"],
        "a_range": (0, 19),
        "b_range": (1, 9),
    },
}
