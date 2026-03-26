"""Claude API for Russian vocabulary card generation."""
import json
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

import keyring
from anthropic import Anthropic

from .cache import DictCache
from .config import DEFAULT_MODEL, WORD_PROMPT_PATH
from .vocabulary import RussianWord

KEYRING_SERVICE = "greek-anki"
KEYRING_USERNAME = "anthropic-api-key"
BATCH_SIZE = 12

GENDER_DESCRIPTIONS = {"boy": "boy", "girl": "girl", "neutral": "child"}

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.DOTALL)


def get_api_key() -> Optional[str]:
    key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
    return key or os.environ.get("ANTHROPIC_API_KEY")


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


def _load_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path.resolve()}")
    return path.read_text(encoding="utf-8")


def generate_words_batch(
    words: List[RussianWord],
    age: int,
    gender: str,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
) -> List[dict]:
    resolved_key = api_key or get_api_key()
    if not resolved_key:
        raise RuntimeError(
            "No API key found. Set one with:\n"
            "  python -m russian_dict set-key\n"
            "Or set ANTHROPIC_API_KEY env var."
        )
    client = Anthropic(api_key=resolved_key)
    template = _load_template(WORD_PROMPT_PATH)

    words_json = json.dumps(
        [{"word": w.russian, "english_hint": w.english, "pos": w.pos, "theme": w.theme}
         for w in words],
        ensure_ascii=False,
    )
    prompt = (
        template.replace("{age}", str(age))
        .replace("{gender_desc}", GENDER_DESCRIPTIONS.get(gender, "child"))
        .replace("{words}", words_json)
    )
    response = client.messages.create(
        model=model, max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )
    results = _extract_json(response.content[0].text.strip())
    if isinstance(results, dict):
        results = [results]
    if not isinstance(results, list):
        raise ValueError(f"Expected JSON array, got {type(results).__name__}")
    return results


def generate_words(
    words: List[RussianWord],
    age: int,
    gender: str,
    cache: DictCache,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    delay: float = 1.0,
    progress_callback=None,
) -> Dict[str, dict]:
    cached = cache.get_batch([w.russian for w in words], age, gender)
    uncached = [w for w in words if w.key not in cached]

    if progress_callback:
        progress_callback(f"[dim]{len(cached)} cached, {len(uncached)} to generate[/dim]")

    for i in range(0, len(uncached), BATCH_SIZE):
        batch = uncached[i:i + BATCH_SIZE]
        if progress_callback:
            progress_callback(
                f"Generating batch {i // BATCH_SIZE + 1}"
                f"/{(len(uncached) + BATCH_SIZE - 1) // BATCH_SIZE}..."
            )

        results = generate_words_batch(batch, age, gender, model=model, api_key=api_key)

        word_map = {w.russian.lower(): w for w in batch}
        for item in results:
            word_str = item.get("word", "").lower()
            w = word_map.get(word_str)
            if w is None:
                continue
            cache.store(
                word=w.russian, age=age, gender=gender,
                translation=item.get("translation", w.english),
                model=model,
                example_ru=item.get("example_ru"),
                example_en=item.get("example_en"),
                mnemonic=item.get("mnemonic"),
                svg_content=item.get("svg") or "",
            )
            cached[w.key] = cache.get(w.key, age, gender)

        if i + BATCH_SIZE < len(uncached):
            time.sleep(delay)

    return cached
