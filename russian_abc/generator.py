"""Claude API for mnemonics + OpenAI DALL-E for image generation."""
import json
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

import keyring
from anthropic import Anthropic

from .cache import AbcCache
from .config import (
    DALLE_MODEL,
    DALLE_QUALITY,
    DALLE_SIZE,
    DEFAULT_MODEL,
    IMAGE_PROMPT_PATH,
    MNEMONIC_PROMPT_PATH,
)
from .letters import RussianLetter

KEYRING_SERVICE = "greek-anki"
KEYRING_USERNAME = "anthropic-api-key"

# Batch size for mnemonic generation
BATCH_SIZE = 11  # ~11 letters per batch = 3 batches for full alphabet

GENDER_DESCRIPTIONS = {
    "boy": "boy",
    "girl": "girl",
    "neutral": "child",
}


# ── API key management ──────────────────────────────────────────────

def get_api_key() -> Optional[str]:
    """Resolve Anthropic API key: keyring first, then env var."""
    key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
    if key:
        return key
    return os.environ.get("ANTHROPIC_API_KEY")


def store_api_key(key: str) -> None:
    keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, key)


def delete_api_key() -> None:
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
    except keyring.errors.PasswordDeleteError:
        pass


def get_openai_key() -> Optional[str]:
    """Resolve OpenAI API key: keyring first, then env var."""
    key = keyring.get_password("russian-abc", "openai-api-key")
    if key:
        return key
    return os.environ.get("OPENAI_API_KEY")


def store_openai_key(key: str) -> None:
    keyring.set_password("russian-abc", "openai-api-key", key)


def delete_openai_key() -> None:
    try:
        keyring.delete_password("russian-abc", "openai-api-key")
    except keyring.errors.PasswordDeleteError:
        pass


# ── JSON extraction ────────────────────────────────────────────────

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.DOTALL)


def _extract_json(text: str) -> object:
    """Extract JSON from Claude's response."""
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
                            return json.loads(text[start : i + 1])
                        except json.JSONDecodeError:
                            break

    raise ValueError(f"Could not extract JSON from response:\n{text[:500]}")


def _load_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path.resolve()}")
    return path.read_text(encoding="utf-8")


# ── Mnemonic generation (Claude API) ──────────────────────────────

def generate_mnemonics_batch(
    letters: List[RussianLetter],
    age: int,
    gender: str,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
) -> List[dict]:
    """Generate mnemonics for a batch of letters via Claude API."""
    resolved_key = api_key or get_api_key()
    if not resolved_key:
        raise RuntimeError(
            "No Anthropic API key found. Set one with:\n"
            "  python -m russian_abc set-key\n"
            "Or set the ANTHROPIC_API_KEY environment variable."
        )

    client = Anthropic(api_key=resolved_key)
    template = _load_template(MNEMONIC_PROMPT_PATH)

    letters_json = json.dumps(
        [
            {
                "letter": lt.upper,
                "lowercase": lt.lower,
                "name": lt.name,
                "ipa": lt.ipa,
                "english_sound": lt.english_approx,
                "type": lt.letter_type,
                "notes": lt.notes,
            }
            for lt in letters
        ],
        ensure_ascii=False,
    )

    gender_desc = GENDER_DESCRIPTIONS.get(gender, "child")
    prompt = (
        template.replace("{age}", str(age))
        .replace("{gender_desc}", gender_desc)
        .replace("{letters}", letters_json)
    )

    response = client.messages.create(
        model=model,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text.strip()
    results = _extract_json(raw_text)
    if isinstance(results, dict):
        results = [results]
    if not isinstance(results, list):
        raise ValueError(f"Expected JSON array, got {type(results).__name__}")

    return results


def generate_mnemonics(
    letters: List[RussianLetter],
    age: int,
    gender: str,
    cache: AbcCache,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    delay: float = 1.0,
    progress_callback=None,
) -> Dict[str, dict]:
    """Generate mnemonics for all letters, using cache."""
    cached = cache.get_all(age, gender)
    uncached = [lt for lt in letters if lt.lower not in cached]

    if progress_callback:
        progress_callback(f"[dim]{len(cached)} cached, {len(uncached)} to generate[/dim]")

    for i in range(0, len(uncached), BATCH_SIZE):
        batch = uncached[i : i + BATCH_SIZE]

        if progress_callback:
            batch_letters = "".join(lt.upper for lt in batch)
            progress_callback(
                f"Generating mnemonics for {batch_letters} "
                f"(batch {i // BATCH_SIZE + 1}/{(len(uncached) + BATCH_SIZE - 1) // BATCH_SIZE})..."
            )

        results = generate_mnemonics_batch(batch, age, gender, model=model, api_key=api_key)

        # Match results to letters
        upper_to_letter = {lt.upper: lt for lt in batch}
        for item in results:
            letter_char = item.get("letter", "")
            lt = upper_to_letter.get(letter_char)
            if lt is None:
                continue

            cache.store(
                letter=lt.lower,
                age=age,
                gender=gender,
                mnemonic=item.get("mnemonic", ""),
                model=model,
                fun_fact=item.get("fun_fact"),
                example_word=item.get("example_word"),
                example_translation=item.get("example_translation"),
                sound_tip=item.get("sound_tip"),
                svg_content=item.get("svg"),
                image_prompt=item.get("image_prompt"),
            )
            cached[lt.lower] = cache.get(lt.lower, age, gender)

        if i + BATCH_SIZE < len(uncached):
            time.sleep(delay)

    return cached


# ── Image generation (DALL-E) ─────────────────────────────────────

def generate_image(
    letter: RussianLetter,
    custom_prompt: str,
    age: int,
    output_dir: str | Path,
    openai_key: Optional[str] = None,
    dalle_model: str = DALLE_MODEL,
    size: str = DALLE_SIZE,
    quality: str = DALLE_QUALITY,
) -> Path:
    """Generate an image for a letter using DALL-E.

    Returns path to the saved image file.
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError(
            "OpenAI package not installed. Run:\n  pip install openai"
        )

    resolved_key = openai_key or get_openai_key()
    if not resolved_key:
        raise RuntimeError(
            "No OpenAI API key found. Set one with:\n"
            "  python -m russian_abc set-openai-key\n"
            "Or set the OPENAI_API_KEY environment variable."
        )

    # Build the image prompt
    template = _load_template(IMAGE_PROMPT_PATH)
    full_prompt = (
        template.replace("{letter}", letter.upper)
        .replace("{letter_upper}", letter.upper)
        .replace("{letter_lower}", letter.lower)
        .replace("{custom_prompt}", custom_prompt)
        .replace("{age}", str(age))
    )

    client = OpenAI(api_key=resolved_key)

    response = client.images.generate(
        model=dalle_model,
        prompt=full_prompt,
        size=size,
        quality=quality,
        n=1,
    )

    image_url = response.data[0].url

    # Download and save the image
    import urllib.request

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"letter_{letter.lower}_{age}.png"
    filepath = output_dir / filename

    urllib.request.urlretrieve(image_url, str(filepath))

    return filepath


def generate_images_batch(
    cache: AbcCache,
    age: int,
    gender: str,
    output_dir: str | Path,
    openai_key: Optional[str] = None,
    delay: float = 2.0,
    progress_callback=None,
) -> int:
    """Generate DALL-E images for all cached letters that don't have images yet.

    Returns count of images generated.
    """
    from .letters import get_letter

    # Check key upfront to fail fast
    resolved_key = openai_key or get_openai_key()
    if not resolved_key:
        raise RuntimeError(
            "No OpenAI API key found. Set one with:\n"
            "  python -m russian_abc set-openai-key\n"
            "Or set the OPENAI_API_KEY environment variable."
        )

    missing = cache.letters_without_images(age, gender)

    if not missing:
        if progress_callback:
            progress_callback("[green]All letters already have images![/green]")
        return 0

    if progress_callback:
        progress_callback(f"[dim]{len(missing)} letters need images[/dim]")

    generated = 0
    for i, item in enumerate(missing):
        letter_char = item["letter"]
        image_prompt = item.get("image_prompt") or ""

        if not image_prompt:
            if progress_callback:
                progress_callback(f"  [yellow]Skipping {letter_char} — no image prompt in cache[/yellow]")
            continue

        try:
            letter = get_letter(letter_char)
        except ValueError:
            continue

        if progress_callback:
            progress_callback(f"  Generating image for {letter.upper} ({i + 1}/{len(missing)})...")

        try:
            filepath = generate_image(
                letter, image_prompt, age, output_dir, openai_key=resolved_key
            )
            cache.update_image(letter.lower, age, gender, str(filepath))
            generated += 1
        except Exception as e:
            if progress_callback:
                progress_callback(f"  [red]Error generating {letter.upper}: {e}[/red]")

        if i + 1 < len(missing):
            time.sleep(delay)

    return generated
