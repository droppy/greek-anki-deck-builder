"""Assemble Russian alphabet cards into an Anki APKG deck with images."""
import hashlib
import html
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import genanki

from .config import CARD_AFMT, CARD_CSS, CARD_QFMT, DEFAULT_IMAGE_DIR, FIELDS, LETTER_TYPE_COLORS
from .letters import RussianLetter


def deck_id_from_name(name: str) -> int:
    """Generate a stable deck ID from a name."""
    h = int(hashlib.sha256(name.encode()).hexdigest()[:12], 16)
    return h


def _model_id_from_name(name: str) -> int:
    h = int(hashlib.sha256(f"model:{name}".encode()).hexdigest()[:12], 16)
    return h


def get_abc_model(deck_name: str = "Russian ABC") -> genanki.Model:
    """Create the genanki Model for alphabet cards."""
    return genanki.Model(
        _model_id_from_name(deck_name),
        f"{deck_name} Model",
        fields=[{"name": name} for name in FIELDS],
        templates=[
            {
                "name": "Letter Card",
                "qfmt": CARD_QFMT,
                "afmt": CARD_AFMT,
            }
        ],
        css=CARD_CSS,
    )


def render_svgs_to_images(
    letters: List[RussianLetter],
    cached_data: Dict[str, dict],
    image_dir: str | Path = DEFAULT_IMAGE_DIR,
    progress_callback=None,
) -> Dict[str, Path]:
    """Render SVGs from cache to PNG images using Playwright.

    Only renders letters that have SVG but no DALL-E image.
    Returns dict mapping letter.lower -> image Path.
    """
    from .svg_renderer import render_svgs_batch

    items = []
    for letter in letters:
        cached = cached_data.get(letter.lower)
        if not cached:
            continue
        # Skip if already has a DALL-E image
        if cached.get("image_path"):
            img = Path(cached["image_path"])
            if img.exists():
                continue
        svg = cached.get("svg_content")
        if not svg:
            continue
        items.append({"key": f"letter_{letter.lower}", "svg": svg})

    if not items:
        return {}

    if progress_callback:
        progress_callback(f"Rendering {len(items)} SVG illustrations to PNG...")

    return render_svgs_batch(items, image_dir, progress_callback=progress_callback)


def build_note_data(
    letter: RussianLetter,
    cached: Optional[dict],
    rendered_images: Optional[Dict[str, Path]] = None,
) -> tuple:
    """Build a note data dict from a letter and its cached mnemonic.

    Returns (note_dict, image_path_or_None).
    """
    esc = html.escape

    # Letter field: large uppercase + lowercase
    letter_html = f"{esc(letter.upper)} {esc(letter.lower)}"

    # Name field: letter name + type
    name_parts = [f'"{esc(letter.name)}"']
    if letter.letter_type == "vowel":
        name_parts.append("(vowel)")
    elif letter.letter_type == "consonant":
        name_parts.append("(consonant)")
    else:
        name_parts.append("(special sign)")
    name_html = " ".join(name_parts)

    # Sound field
    if letter.ipa:
        sound_tip = cached.get("sound_tip", "") if cached else ""
        sound_html = f"<b>{esc(letter.english_approx)}</b>"
        if sound_tip:
            sound_html += f"<br><span style='font-size:18px'>{esc(sound_tip)}</span>"
    else:
        sound_html = "<em>(no sound — this is a modifier sign)</em>"

    # Mnemonic
    mnemonic_html = ""
    if cached:
        mnemonic = cached.get("mnemonic", "")
        fun_fact = cached.get("fun_fact", "")
        if mnemonic:
            mnemonic_html = esc(mnemonic)
        if fun_fact:
            mnemonic_html += f"<br><br><span style='color:#e67e22'>{esc(fun_fact)}</span>"

    # Example word
    example_html = ""
    if cached:
        ex_word = cached.get("example_word", "")
        ex_trans = cached.get("example_translation", "")
        if ex_word:
            example_html = f"<b>{esc(ex_word)}</b>"
            if ex_trans:
                example_html += f" = {esc(ex_trans)}"
    elif letter.example_word:
        example_html = (
            f"<b>{esc(letter.example_word)}</b> = {esc(letter.example_translation)}"
        )

    # Visual: pick the best available image source
    visual_html = ""
    image_file = None
    img_key = f"letter_{letter.lower}"

    # Priority 1: DALL-E image from cache
    if cached and cached.get("image_path"):
        p = Path(cached["image_path"])
        if p.exists():
            visual_html = f'<img src="{esc(p.name)}">'
            image_file = p

    # Priority 2: rendered SVG PNG
    if not visual_html and rendered_images and img_key in rendered_images:
        p = rendered_images[img_key]
        if p.exists():
            visual_html = f'<img src="{esc(p.name)}">'
            image_file = p

    return {
        "letter": letter_html,
        "name": name_html,
        "sound": sound_html,
        "mnemonic": mnemonic_html,
        "example_word": example_html,
        "visual": visual_html,
    }, image_file


def build_apkg(
    letters: List[RussianLetter],
    cached_data: Dict[str, dict],
    deck_name: str = "Russian ABC for Kids",
    output_path: Optional[str | Path] = None,
    tags: Optional[List[str]] = None,
    image_dir: str | Path = DEFAULT_IMAGE_DIR,
    progress_callback=None,
) -> Path:
    """Build an APKG file from letters and cached data, embedding images.

    SVGs are automatically rendered to PNG and embedded.
    Returns path to the generated .apkg file.
    """
    if output_path is None:
        ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = Path(f"russian_abc_{ts}.apkg")
    else:
        output_path = Path(output_path)

    # Render SVGs to PNGs
    rendered_images = render_svgs_to_images(
        letters, cached_data, image_dir, progress_callback=progress_callback
    )

    model = get_abc_model(deck_name)
    did = deck_id_from_name(deck_name)
    deck = genanki.Deck(did, deck_name)

    base_tags = tags or []
    media_files = []

    for letter in letters:
        cached = cached_data.get(letter.lower)
        note_data, image_file = build_note_data(letter, cached, rendered_images)

        if image_file and image_file.exists():
            abs_path = str(image_file.resolve())
            if abs_path not in media_files:
                media_files.append(abs_path)

        # Per-card tags
        card_tags = list(base_tags)
        card_tags.append(f"type::{letter.letter_type}")
        card_tags.append(f"position::{letter.position}")

        note = genanki.Note(
            model=model,
            fields=[
                note_data["letter"],
                note_data["name"],
                note_data["sound"],
                note_data["mnemonic"],
                note_data["example_word"],
                note_data["visual"],
            ],
            tags=card_tags,
            guid=genanki.guid_for(letter.lower, deck_name),
        )
        deck.add_note(note)

    # Build package with media files
    pkg = genanki.Package(deck, media_files=media_files)
    pkg.write_to_file(str(output_path))

    return output_path
