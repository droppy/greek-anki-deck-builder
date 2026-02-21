"""Claude API card generation."""
import html
import json
import os
from dataclasses import dataclass, field
from typing import List, Optional

import keyring
from anthropic import Anthropic

from .config import DEFAULT_MODEL, PROMPT_TEMPLATE_PATH

KEYRING_SERVICE = "greek-anki"
KEYRING_USERNAME = "anthropic-api-key"


def get_api_key() -> Optional[str]:
    """Resolve API key: keyring first, then env var."""
    key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
    if key:
        return key
    return os.environ.get("ANTHROPIC_API_KEY")


def store_api_key(key: str) -> None:
    """Store API key in the OS credential store."""
    keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, key)


def delete_api_key() -> None:
    """Remove API key from the OS credential store."""
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
    except keyring.errors.PasswordDeleteError:
        pass


@dataclass
class GeneratedCard:
    """Structured card data returned by Claude."""

    front_ru: str
    front_en: str
    back: str
    part_of_speech: str
    examples: List[dict]  # [{"greek": ..., "russian": ...}]
    conjugation: Optional[str]
    synonyms: List[dict]  # [{"word": ..., "distinction": ...}]
    etymology_note: Optional[str]
    collocations: List[str]

    # Rendered HTML fields for Anki
    front: str = ""
    example: str = ""
    comment: str = ""
    collocations_html: str = ""
    etymology_html: str = ""

    # Token usage tracking
    _usage: dict = field(default_factory=dict, repr=False)
    # Raw JSON data from Claude (for cache serialization)
    _raw_data: dict = field(default_factory=dict, repr=False)

    @staticmethod
    def _sanitize_example_greek(text: str) -> str:
        """Allow only <em>/<em> tags in Greek examples, escape everything else."""
        import re
        # Temporarily replace valid <em> and </em> with placeholders
        text = text.replace("<em>", "\x00EM\x00").replace("</em>", "\x00/EM\x00")
        # Escape any remaining HTML
        text = html.escape(text)
        # Restore <em> tags
        text = text.replace("\x00EM\x00", "<em>").replace("\x00/EM\x00", "</em>")
        return text

    def render_fields(self):
        """Convert structured data into HTML fields matching Anki format."""
        esc = lambda s: html.escape(s) if s else ""

        # Front field
        self.front = (
            f"<div>{esc(self.front_ru)}</div>"
            f"<div><br></div>"
            f"<div>{esc(self.front_en)}</div>"
        )

        # Example field
        example_lines = []
        for ex in self.examples:
            example_lines.append(
                f"<li><strong>{self._sanitize_example_greek(ex.get('greek', ''))}</strong> {esc(ex.get('russian', ''))}</li>"
            )
        self.example = "\n".join(example_lines)

        # Comment field
        comment_parts = []

        if self.conjugation:
            comment_parts.append(f"<div>{esc(self.conjugation)}</div>")
            comment_parts.append("<div><br></div>")

        if self.synonyms:
            syn_lines = []
            for syn in self.synonyms:
                syn_lines.append(
                    f"<li><strong>{esc(syn.get('word', ''))}</strong>: "
                    f"{esc(syn.get('distinction', ''))}</li>"
                )
            comment_parts.append("<div>" + "\n".join(syn_lines) + "</div>")

        self.comment = "\n".join(comment_parts)

        # Collocations field
        if self.collocations:
            colloc_lines = [f"<li><strong>{esc(c)}</strong></li>" for c in self.collocations]
            self.collocations_html = "".join(colloc_lines)

        # Etymology field
        if self.etymology_note:
            self.etymology_html = f"<em>{esc(self.etymology_note)}</em>"

    def to_note_dict(self) -> dict:
        """Convert to dict suitable for create_supplement_apkg."""
        if not self.front:
            self.render_fields()
        return {
            "front": self.front,
            "back": self.back,
            "example": self.example,
            "comment": self.comment,
            "collocations": self.collocations_html,
            "etymology": self.etymology_html,
        }


import re as _re

_JSON_FENCE_RE = _re.compile(r"```(?:json)?\s*\n(.*?)```", _re.DOTALL)


def _extract_json(text: str, word: str) -> dict:
    """Extract a JSON object from Claude's response, tolerating extra text."""
    # 1. Try fenced code block
    m = _JSON_FENCE_RE.search(text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # 2. Find the outermost { ... } in the response
    start = text.find("{")
    if start != -1:
        # Walk forward counting braces to find the matching close
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        break

    raise ValueError(
        f"Could not extract JSON from Claude's response for '{word}':\n"
        f"{text[:500]}"
    )


def _load_prompt_template() -> str:
    path = PROMPT_TEMPLATE_PATH
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path.resolve()}")
    return path.read_text(encoding="utf-8")


def generate_card(
    word: str,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
) -> GeneratedCard:
    """Generate a flashcard for a Greek word using Claude API.

    Args:
        word: Greek word to generate a card for.
        model: Claude model to use.
        api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var).

    Returns:
        GeneratedCard with structured data and rendered HTML fields.
    """
    resolved_key = api_key or get_api_key()
    if not resolved_key:
        raise RuntimeError(
            "No API key found. Set one with:\n"
            "  python -m greek_anki set-key\n"
            "Or set the ANTHROPIC_API_KEY environment variable."
        )
    client = Anthropic(api_key=resolved_key)

    template = _load_prompt_template()
    prompt = template.replace("{word}", word)

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text.strip()
    data = _extract_json(raw_text, word)

    card = GeneratedCard(
        front_ru=data.get("front_ru", ""),
        front_en=data.get("front_en", ""),
        back=data.get("back", word),
        part_of_speech=data.get("part_of_speech", "unknown"),
        examples=data.get("examples", []),
        conjugation=data.get("conjugation"),
        synonyms=data.get("synonyms", []),
        etymology_note=data.get("etymology_note"),
        collocations=data.get("collocations", []),
    )
    card.render_fields()
    card._raw_data = data
    card._usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }

    return card
