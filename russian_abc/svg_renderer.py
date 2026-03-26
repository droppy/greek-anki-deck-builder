"""Render SVG strings to PNG files using Playwright (headless Chromium)."""
from pathlib import Path
from typing import Dict, List, Optional


def render_svg_to_png(
    svg_content: str,
    output_path: str | Path,
    width: int = 400,
    height: int = 400,
) -> Path:
    """Render a single SVG string to a PNG file.

    Uses Playwright with headless Chromium for accurate rendering.
    """
    from playwright.sync_api import sync_playwright

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    html = (
        f'<html><body style="margin:0;padding:0;display:flex;'
        f'align-items:center;justify-content:center;'
        f'width:{width}px;height:{height}px;background:white">'
        f'{svg_content}</body></html>'
    )

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.set_content(html)
        page.screenshot(path=str(output_path))
        browser.close()

    return output_path


def render_svgs_batch(
    items: List[dict],
    output_dir: str | Path,
    width: int = 400,
    height: int = 400,
    progress_callback=None,
) -> Dict[str, Path]:
    """Render multiple SVGs to PNGs efficiently (single browser instance).

    Args:
        items: List of dicts with 'key' (filename stem) and 'svg' (SVG string).
        output_dir: Directory for output PNGs.
        width: Image width in pixels.
        height: Image height in pixels.
        progress_callback: Optional function for progress updates.

    Returns:
        Dict mapping key -> output Path.
    """
    from playwright.sync_api import sync_playwright

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})

        for i, item in enumerate(items):
            key = item["key"]
            svg = item["svg"]
            filepath = output_dir / f"{key}.png"

            html = (
                f'<html><body style="margin:0;padding:0;display:flex;'
                f'align-items:center;justify-content:center;'
                f'width:{width}px;height:{height}px;background:white">'
                f'{svg}</body></html>'
            )

            page.set_content(html)
            page.screenshot(path=str(filepath))
            results[key] = filepath

            if progress_callback and (i + 1) % 5 == 0:
                progress_callback(f"  Rendered {i + 1}/{len(items)} images...")

        browser.close()

    if progress_callback:
        progress_callback(f"  Rendered {len(items)}/{len(items)} images.")

    return results
