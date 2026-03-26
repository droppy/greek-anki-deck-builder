"""Click CLI for Russian dictionary Anki deck generator."""
import os
import sys

if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .cache import DictCache
from .config import DEFAULT_CARD_CACHE, DEFAULT_IMAGE_DIR, DEFAULT_MODEL
from .deck_builder import build_apkg
from .generator import generate_words, get_api_key
from .vocabulary import get_themes, get_words

console = Console()


@click.group()
def cli():
    """Russian vocabulary Anki deck generator for English-speaking kids."""
    pass


@cli.command("words")
@click.option("--level", type=click.Choice(["basic", "conversational", "all"]), default="all")
def show_words(level):
    """Show vocabulary list with word counts by theme."""
    words = get_words(level)
    themes = {}
    for w in words:
        themes.setdefault(w.theme, []).append(w)

    table = Table(title=f"Russian Vocabulary — {level} ({len(words)} words)")
    table.add_column("Theme", style="bold cyan")
    table.add_column("Count", justify="right", style="green")
    table.add_column("Sample words")

    for theme, wlist in sorted(themes.items(), key=lambda x: -len(x[1])):
        samples = ", ".join(w.russian for w in wlist[:5])
        if len(wlist) > 5:
            samples += "..."
        table.add_row(theme, str(len(wlist)), samples)

    console.print(table)


@cli.command("generate")
@click.option("--level", type=click.Choice(["basic", "conversational", "all"]), default="basic")
@click.option("--age", type=int, default=6)
@click.option("--gender", type=click.Choice(["boy", "girl", "neutral"]), default="neutral")
@click.option("--model", "-m", default=DEFAULT_MODEL)
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE)
@click.option("-y", "--yes", is_flag=True)
def generate_cmd(level, age, gender, model, cache_db, yes):
    """Generate word cards via Claude API."""
    words = get_words(level)
    console.print(
        f"[bold]Generating cards for {len(words)} {level} words[/bold]\n"
        f"  Age: {age}, Gender: {gender}, Model: {model}"
    )
    if not yes and not click.confirm("Proceed?"):
        return

    with DictCache(cache_db) as cache:
        def progress(msg):
            console.print(f"  {msg}")
        cached = generate_words(words, age, gender, cache, model=model, progress_callback=progress)
        console.print(f"\n[bold green]Done![/bold green] {len(cached)} word cards cached.")


@cli.command("build-deck")
@click.option("--level", type=click.Choice(["basic", "conversational", "all"]), default="basic")
@click.option("--age", type=int, default=6)
@click.option("--gender", type=click.Choice(["boy", "girl", "neutral"]), default="neutral")
@click.option("--deck-name", default=None)
@click.option("-o", "--output", type=click.Path(), default=None)
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE)
@click.option("--image-dir", type=click.Path(), default=DEFAULT_IMAGE_DIR)
@click.option("--generate-missing", is_flag=True)
@click.option("--model", "-m", default=DEFAULT_MODEL)
@click.option("-y", "--yes", is_flag=True)
def build_deck_cmd(level, age, gender, deck_name, output, cache_db, image_dir,
                   generate_missing, model, yes):
    """Build an APKG deck from cached word cards."""
    words = get_words(level)
    if deck_name is None:
        deck_name = f"Russian {level.title()} (age {age})"

    console.print(
        f"[bold]Building deck:[/bold] {deck_name}\n"
        f"  Words: {len(words)} ({level}), Age: {age}, Gender: {gender}"
    )

    with DictCache(cache_db) as cache:
        cached = cache.get_batch([w.russian for w in words], age, gender)
        uncached_count = len(words) - len(cached)

        if uncached_count > 0:
            if generate_missing:
                console.print(f"  [yellow]{uncached_count} words not cached — generating...[/yellow]")
                if not yes and not click.confirm("Generate missing?"):
                    return
                def progress(msg):
                    console.print(f"    {msg}")
                cached = generate_words(words, age, gender, cache, model=model, progress_callback=progress)
            else:
                console.print(
                    f"  [yellow]Warning: {uncached_count} words not cached. "
                    f"Use --generate-missing to generate.[/yellow]"
                )

        tags = ["auto-generated", f"age::{age}", f"gender::{gender}", f"level::{level}"]

        def build_progress(msg):
            console.print(f"  {msg}")

        result_path = build_apkg(
            words, cached, deck_name=deck_name, output_path=output,
            tags=tags, image_dir=image_dir, progress_callback=build_progress,
        )
        stats = cache.stats(age, gender)
        console.print(
            f"\n[bold green]Deck created:[/bold green] {result_path}\n"
            f"  {len(words)} cards, {len(cached)} with content, {stats['with_svg']} with SVG"
        )


@cli.command("preview")
@click.option("--level", type=click.Choice(["basic", "conversational", "all"]), default="basic")
@click.option("--age", type=int, default=6)
@click.option("--gender", type=click.Choice(["boy", "girl", "neutral"]), default="neutral")
@click.option("--theme", default=None, help="Filter by theme")
@click.option("--count", "-n", type=int, default=5)
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE)
def preview(level, age, gender, theme, count, cache_db):
    """Preview sample word cards."""
    words = get_words(level)
    if theme:
        words = [w for w in words if w.theme == theme]
    words = words[:count]

    with DictCache(cache_db) as cache:
        cached = cache.get_batch([w.russian for w in words], age, gender)

    for w in words:
        data = cached.get(w.key)
        translation = data["translation"] if data else w.english
        example = ""
        if data and data.get("example_ru"):
            example = f"{data['example_ru']} — {data.get('example_en', '')}"
        mnemonic = data.get("mnemonic", "") if data else ""
        has_svg = bool(data.get("svg_content")) if data else False

        content = (
            f"[bold]{w.russian}[/bold]  [dim]({w.pos})[/dim]  [{w.theme}]\n"
            f"Translation: [green]{translation}[/green]\n"
        )
        if example:
            content += f"Example: [blue]{example}[/blue]\n"
        if mnemonic:
            content += f"Mnemonic: [magenta]{mnemonic}[/magenta]\n"
        content += f"Visual: {'[bold green]SVG[/bold green]' if has_svg else '[dim]none[/dim]'}"

        console.print(Panel(content, title=w.russian, width=75))


@cli.command("cache-status")
@click.option("--age", type=int, default=None)
@click.option("--gender", type=click.Choice(["boy", "girl", "neutral"]), default=None)
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE)
def cache_status(age, gender, cache_db):
    """Show cache statistics."""
    with DictCache(cache_db) as cache:
        stats = cache.stats(age, gender)
        from .vocabulary import ALL_WORDS, BASIC_WORDS
        console.print(
            f"Total cached: [green]{stats['total']}[/green] "
            f"(basic: {len(BASIC_WORDS)}, all: {len(ALL_WORDS)})\n"
            f"With SVG: [green]{stats['with_svg']}[/green]"
        )


@cli.command("set-key")
def set_key():
    """Store Anthropic API key."""
    import keyring
    existing = get_api_key()
    if existing:
        console.print("[yellow]Key already stored.[/yellow]")
        if not click.confirm("Overwrite?"):
            return
    key = click.prompt("Anthropic API key", hide_input=True)
    if key.strip():
        keyring.set_password("greek-anki", "anthropic-api-key", key.strip())
        console.print("[green]Stored.[/green]")


if __name__ == "__main__":
    cli()
