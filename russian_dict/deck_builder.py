"""Assemble Russian vocabulary cards into an Anki APKG deck with images."""
import hashlib
import html
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import genanki

from .config import (
    CARD1_AFMT, CARD1_QFMT, CARD2_AFMT, CARD2_QFMT,
    CARD_CSS, DEFAULT_IMAGE_DIR, FIELDS,
)
from .vocabulary import RussianWord


_UNSAFE_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\s,]+')


def _safe_image_key(word_key: str) -> str:
    """Build a filesystem-safe image key from a word key.

    Word keys may contain slashes, spaces, commas, question marks
    (e.g. grammar cards 'большой / большая / большое / большие',
    phrases 'как дела?'). Sanitize them so they cannot escape the
    image directory. Long keys are hashed to keep paths under MAX_PATH.
    """
    safe = _UNSAFE_FILENAME_CHARS.sub("_", word_key.strip()).strip("_")
    if len(safe) > 80:
        safe = safe[:60] + "_" + hashlib.md5(word_key.encode("utf-8")).hexdigest()[:8]
    return f"word_{safe}"


def deck_id_from_name(name: str) -> int:
    return int(hashlib.sha256(name.encode()).hexdigest()[:12], 16)


def _model_id_from_name(name: str) -> int:
    return int(hashlib.sha256(f"model:{name}".encode()).hexdigest()[:12], 16)


def get_dict_model(deck_name: str = "Russian Words") -> genanki.Model:
    return genanki.Model(
        _model_id_from_name(deck_name),
        f"{deck_name} Model",
        fields=[{"name": n} for n in FIELDS],
        templates=[
            {
                "name": "Recognition (RU → EN)",
                "qfmt": CARD1_QFMT,
                "afmt": CARD1_AFMT,
            },
            {
                "name": "Recall (EN → RU)",
                "qfmt": CARD2_QFMT,
                "afmt": CARD2_AFMT,
            },
        ],
        css=CARD_CSS,
    )


def _render_svgs(words, cached_data, image_dir, progress_callback=None):
    """Render SVGs to PNGs. Returns {img_key: Path}."""
    from russian_abc.svg_renderer import render_svgs_batch

    items = []
    for w in words:
        c = cached_data.get(w.key)
        if not c or not c.get("svg_content"):
            continue
        if c.get("image_path") and Path(c["image_path"]).exists():
            continue
        items.append({"key": _safe_image_key(w.key), "svg": c["svg_content"]})

    if not items:
        return {}

    if progress_callback:
        progress_callback(f"Rendering {len(items)} SVG illustrations to PNG...")

    return render_svgs_batch(items, image_dir, progress_callback=progress_callback)


def build_note_data(word: RussianWord, cached: Optional[dict],
                    rendered_images: Optional[Dict[str, Path]] = None) -> tuple:
    esc = html.escape

    word_html = esc(word.russian)
    translation_html = ""
    example_html = ""
    mnemonic_html = ""
    visual_html = ""
    image_file = None

    if cached:
        translation_html = esc(cached.get("translation", word.english))
        ex_ru = cached.get("example_ru", "")
        ex_en = cached.get("example_en", "")
        if ex_ru:
            example_html = f"<b>{esc(ex_ru)}</b>"
            if ex_en:
                example_html += f"<br>{esc(ex_en)}"
        mnemonic = cached.get("mnemonic", "")
        if mnemonic:
            mnemonic_html = esc(mnemonic)

        # Image: DALL-E > rendered SVG
        if cached.get("image_path") and Path(cached["image_path"]).exists():
            p = Path(cached["image_path"])
            visual_html = f'<img src="{esc(p.name)}">'
            image_file = p

        img_key = _safe_image_key(word.key)
        if not visual_html and rendered_images and img_key in rendered_images:
            p = rendered_images[img_key]
            if p.exists():
                visual_html = f'<img src="{esc(p.name)}">'
                image_file = p
    else:
        translation_html = esc(word.english)

    return {
        "word": word_html,
        "translation": translation_html,
        "example": example_html,
        "mnemonic": mnemonic_html,
        "visual": visual_html,
    }, image_file


def build_apkg(
    words: List[RussianWord],
    cached_data: Dict[str, dict],
    deck_name: str = "Russian Words for Kids",
    output_path: Optional[str | Path] = None,
    tags: Optional[List[str]] = None,
    image_dir: str | Path = DEFAULT_IMAGE_DIR,
    progress_callback=None,
) -> Path:
    if output_path is None:
        ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = Path(f"russian_dict_{ts}.apkg")
    else:
        output_path = Path(output_path)

    rendered = _render_svgs(words, cached_data, image_dir, progress_callback)

    model = get_dict_model(deck_name)
    deck = genanki.Deck(deck_id_from_name(deck_name), deck_name)
    base_tags = tags or []
    media_files = []

    for word in words:
        cached = cached_data.get(word.key)
        note_data, image_file = build_note_data(word, cached, rendered)

        if image_file and image_file.exists():
            abs_path = str(image_file.resolve())
            if abs_path not in media_files:
                media_files.append(abs_path)

        card_tags = list(base_tags) + [f"theme::{word.theme}", f"level::{word.level}", f"pos::{word.pos}"]

        note = genanki.Note(
            model=model,
            fields=[note_data["word"], note_data["translation"], note_data["example"],
                    note_data["mnemonic"], note_data["visual"]],
            tags=card_tags,
            guid=genanki.guid_for(word.key, deck_name),
        )
        deck.add_note(note)

    pkg = genanki.Package(deck, media_files=media_files)
    pkg.write_to_file(str(output_path))
    return output_path
