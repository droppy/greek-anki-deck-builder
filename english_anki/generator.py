"""Claude API integration for C1+ English card generation."""
import html
import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import keyring
from anthropic import Anthropic

from .card_cache import CardCache
from .config import DEFAULT_LANG, DEFAULT_MODEL, get_prompt_path
from .normalizer import normalize_english

KEYRING_SERVICE = "greek-anki"
KEYRING_USERNAME = "anthropic-api-key"
BATCH_SIZE = 8  # C1 cards are detailed, keep batches smaller

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.DOTALL)


def get_api_key() -> Optional[str]:
    key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
    return key or os.environ.get("ANTHROPIC_API_KEY")


def store_api_key(key: str) -> None:
    keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, key)


def delete_api_key() -> None:
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
    except keyring.errors.PasswordDeleteError:
        pass


def _extract_json(text: str) -> object:
    m = _JSON_FENCE_RE.search(text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    for open_ch, close_ch in [("[", "]"), ("{", "}")]:
        start = text.find(open_ch)
        if start != -1:
            depth = 0
            for i in range(start, len(text)):
                if text[i] == open_ch:
                    depth += 1
                elif text[i] == close_ch:
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[start:i + 1])
                        except json.JSONDecodeError:
                            break
    raise ValueError(f"Could not extract JSON:\n{text[:500]}")


def _load_template(lang: str = DEFAULT_LANG) -> str:
    path = get_prompt_path(lang)
    return path.read_text(encoding="utf-8")


@dataclass
class GeneratedCard:
    """Structured card data returned by Claude."""

    word: str
    definition_native: str  # Russian, Thai, or any native language
    definition_en: str
    part_of_speech: str
    register: str
    examples: List[dict]
    collocations: List[str]
    synonyms: List[dict]
    usage_note: str
    pronunciation: str = ""
    morphology: str = ""
    native_trap: str = ""  # Common error for this L1 speaker
    cultural_note: str = ""

    # Rendered HTML fields
    definition_html: str = ""
    example_html: str = ""
    collocations_html: str = ""
    synonyms_html: str = ""
    register_html: str = ""

    _raw_data: dict = field(default_factory=dict, repr=False)
    _usage: dict = field(default_factory=dict, repr=False)

    def render_fields(self):
        """Convert structured data into HTML fields for Anki."""
        esc = html.escape

        # Definition: native translation + trap/cultural + English definition
        self.definition_html = f"<div>{esc(self.definition_native)}</div>"
        if self.native_trap:
            self.definition_html += (
                f"<div style='font-size:14px;color:#c0855a;margin-top:4px'>"
                f"\u26a0\ufe0f {esc(self.native_trap)}</div>"
            )
        if self.cultural_note:
            self.definition_html += (
                f"<div style='font-size:14px;color:#5b8db8;margin-top:4px'>"
                f"\U0001f4d6 {esc(self.cultural_note)}</div>"
            )
        self.definition_html += (
            f"<div style='color:#777;font-size:16px;margin-top:4px'>{esc(self.definition_en)}</div>"
        )

        # Collocations field repurposed for pronunciation + morphology (answer-side only)
        extras = []
        if self.pronunciation:
            extras.append(
                f"<div style='color:#999;font-size:15px;font-family:monospace'>"
                f"{esc(self.pronunciation)}</div>"
            )
        if self.morphology:
            extras.append(
                f"<div style='color:#888;font-size:13px;font-style:italic'>"
                f"{esc(self.morphology)}</div>"
            )
        self.collocations_html = "\n".join(extras)

        # Examples
        lines = []
        for ex in self.examples:
            reg = ex.get("register", "")
            reg_tag = f" <span style='color:#999;font-size:12px'>[{esc(reg)}]</span>" if reg else ""
            lines.append(f"<div>{esc(ex.get('en', ''))}{reg_tag}</div>")
        self.example_html = "\n".join(lines)

        # Synonyms with distinctions
        if self.synonyms:
            syn_lines = []
            for s in self.synonyms:
                syn_lines.append(
                    f"<b>{esc(s.get('word', ''))}</b> — "
                    f"<span style='color:#666'>{esc(s.get('distinction', ''))}</span>"
                )
            self.synonyms_html = "<br>".join(syn_lines)

        # Register — trap/cultural moved into Definition; this field is now empty
        self.register_html = ""

    def to_note_dict(self) -> dict:
        if not self.definition_html:
            self.render_fields()
        return {
            "word": self.word,
            "definition": self.definition_html,
            "example": self.example_html,
            "collocations": self.collocations_html,
            "synonyms": self.synonyms_html,
            "register": self.register_html,
        }


def _dict_to_card(data: dict) -> GeneratedCard:
    # Pick native-language definition: try definition_ru, definition_th, etc.
    definition_native = ""
    for key in ("definition_ru", "definition_th", "definition_native"):
        if data.get(key):
            definition_native = data[key]
            break

    card = GeneratedCard(
        word=data.get("word", ""),
        definition_native=definition_native,
        definition_en=data.get("definition_en", ""),
        part_of_speech=data.get("part_of_speech", ""),
        register=data.get("register", ""),
        examples=data.get("examples", []),
        collocations=data.get("collocations", []),
        synonyms=data.get("synonyms", []),
        usage_note=data.get("usage_note", ""),
        pronunciation=data.get("pronunciation", ""),
        morphology=data.get("morphology", ""),
        native_trap=data.get("thai_trap", "") or data.get("native_trap", ""),
        cultural_note=data.get("cultural_note", ""),
    )
    card._raw_data = data
    card.render_fields()
    return card


def generate_cards_batch(
    words: List[str],
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    lang: str = DEFAULT_LANG,
) -> List[dict]:
    """Generate cards for a batch of words via Claude API."""
    resolved_key = api_key or get_api_key()
    if not resolved_key:
        raise RuntimeError(
            "No API key found. Set one with:\n"
            "  python -m english_anki set-key\n"
            "Or set ANTHROPIC_API_KEY env var."
        )
    client = Anthropic(api_key=resolved_key)
    template = _load_template(lang)

    words_json = json.dumps(
        [{"word": w} for w in words], ensure_ascii=False
    )
    prompt = template.replace("{words}", words_json).replace("{{", "{").replace("}}", "}")

    # Use streaming to avoid 10-minute timeout with large max_tokens
    raw = ""
    with client.messages.stream(
        model=model, max_tokens=16384,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            raw += text
    raw = raw.strip()
    results = _extract_json(raw)
    if isinstance(results, dict):
        # Claude sometimes returns a single object instead of an array
        results = [results]
    if not isinstance(results, list):
        raise ValueError(f"Expected JSON array, got {type(results).__name__}")
    return results


def generate_card(
    word: str,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    lang: str = DEFAULT_LANG,
) -> GeneratedCard:
    """Generate a single card (for preview/add commands)."""
    results = generate_cards_batch([word], model=model, api_key=api_key, lang=lang)
    if not results:
        raise ValueError(f"No result returned for '{word}'")
    card = _dict_to_card(results[0])
    return card


def generate_card_cached(
    word: str,
    cache: CardCache,
    model: str = DEFAULT_MODEL,
    force: bool = False,
    lang: str = DEFAULT_LANG,
) -> GeneratedCard:
    """Generate a card, using cache if available."""
    if not force:
        data = cache.get(word)
        if data is not None:
            return _dict_to_card(data)

    card = generate_card(word, model=model, lang=lang)
    cache.store(word, card._raw_data, model=model)
    return card


def generate_batch_cached(
    words: List[str],
    cache: CardCache,
    model: str = DEFAULT_MODEL,
    delay: float = 1.0,
    progress_callback=None,
    lang: str = DEFAULT_LANG,
) -> Dict[str, GeneratedCard]:
    """Generate cards for multiple words with caching and batching."""
    cached_data = cache.get_batch(words)
    result = {}

    # Return cached ones
    for w in words:
        norm = normalize_english(w)
        if norm in cached_data:
            result[norm] = _dict_to_card(cached_data[norm])

    uncached = [w for w in words if normalize_english(w) not in result]

    if progress_callback:
        progress_callback(f"[dim]{len(result)} cached, {len(uncached)} to generate[/dim]")

    total = len(uncached) + len(result)
    generated_count = len(result)

    for w in uncached:
        generated_count += 1
        try:
            card = generate_card(w, model=model, lang=lang)
        except Exception as e:
            if progress_callback:
                progress_callback(
                    f"  [red]{generated_count:4d}/{total}  {w}  — ERROR: {e}[/red]"
                )
            if delay > 0:
                time.sleep(delay)
            continue

        norm = normalize_english(w)
        cache.store(w, card._raw_data, model=model)
        result[norm] = card

        if progress_callback:
            pos = f" ({card.part_of_speech})" if card.part_of_speech else ""
            defn = card.definition_native[:50]
            progress_callback(
                f"  [green]{generated_count:4d}[/green]/{total}  "
                f"[bold]{card.word}[/bold]{pos}  {defn}"
            )

        if delay > 0:
            time.sleep(delay)

    return result
