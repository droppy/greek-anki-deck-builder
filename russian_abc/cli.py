"""Click CLI for Russian alphabet Anki deck generator."""
import os
import sys

# Fix Windows console encoding for Unicode
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

from .cache import AbcCache
from .config import DEFAULT_CARD_CACHE, DEFAULT_IMAGE_DIR, DEFAULT_MODEL
from .deck_builder import build_apkg
from .generator import (
    delete_api_key,
    delete_openai_key,
    generate_images_batch,
    generate_mnemonics,
    get_api_key,
    get_openai_key,
    store_api_key,
    store_openai_key,
)
from .letters import get_all_letters

console = Console()


@click.group()
def cli():
    """Russian alphabet Anki deck generator for English-speaking kids."""
    pass


@cli.command("alphabet")
def show_alphabet():
    """Show all 33 Russian letters with pronunciation info."""
    letters = get_all_letters()
    table = Table(title="Russian Alphabet (33 letters)")
    table.add_column("#", style="dim", justify="right")
    table.add_column("Letter", style="bold cyan", justify="center")
    table.add_column("Name", style="bold")
    table.add_column("Sound", style="green")
    table.add_column("Type", style="dim")
    table.add_column("Example")

    for lt in letters:
        type_color = {"vowel": "red", "consonant": "blue", "sign": "dim"}.get(lt.letter_type, "")
        example = f"{lt.example_word} ({lt.example_translation})" if lt.example_word else ""
        table.add_row(
            str(lt.position),
            f"{lt.upper} {lt.lower}",
            lt.name,
            lt.english_approx or "(none)",
            f"[{type_color}]{lt.letter_type}[/{type_color}]",
            example,
        )

    console.print(table)


@cli.command("generate")
@click.option("--age", type=int, default=6, help="Target kid age (4-10)")
@click.option("--gender", type=click.Choice(["boy", "girl", "neutral"]), default="neutral", help="Gender for themed examples")
@click.option("--model", "-m", default=DEFAULT_MODEL, help="Claude model")
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE, help="Cache DB path")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation")
def generate_cmd(age, gender, model, cache_db, yes):
    """Generate mnemonics for all 33 letters via Claude API."""
    letters = get_all_letters()

    console.print(
        f"[bold]Generating mnemonics for {len(letters)} Russian letters[/bold]\n"
        f"  Age: {age}, Gender: {gender}, Model: {model}"
    )

    if not yes:
        if not click.confirm("Proceed?"):
            return

    with AbcCache(cache_db) as cache:
        def progress(msg):
            console.print(f"  {msg}")

        cached = generate_mnemonics(
            letters, age=age, gender=gender, cache=cache, model=model,
            progress_callback=progress,
        )

        console.print(
            f"\n[bold green]Done![/bold green] {len(cached)} letter mnemonics cached."
        )


@cli.command("generate-images")
@click.option("--age", type=int, default=6, help="Target kid age (4-10)")
@click.option("--gender", type=click.Choice(["boy", "girl", "neutral"]), default="neutral")
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE, help="Cache DB path")
@click.option("--image-dir", type=click.Path(), default=DEFAULT_IMAGE_DIR, help="Output directory for images")
@click.option("--delay", type=float, default=2.0, help="Delay between DALL-E calls (seconds)")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation")
def generate_images_cmd(age, gender, cache_db, image_dir, delay, yes):
    """Generate DALL-E images for letters that don't have them yet."""
    with AbcCache(cache_db) as cache:
        missing = cache.letters_without_images(age, gender)
        total_cached = cache.stats(age, gender)

        if total_cached["total"] == 0:
            console.print(
                "[red]No mnemonics cached yet. Run 'generate' first.[/red]"
            )
            return

        if not missing:
            console.print("[green]All cached letters already have images![/green]")
            return

        # Filter to only those with image prompts
        with_prompts = [m for m in missing if m.get("image_prompt")]
        console.print(
            f"[bold]Generating DALL-E images for {len(with_prompts)} letters[/bold]\n"
            f"  Age: {age}, Gender: {gender}\n"
            f"  Output: {image_dir}/\n"
            f"  Estimated cost: ~${len(with_prompts) * 0.04:.2f}"
        )

        if not yes:
            if not click.confirm("Proceed?"):
                return

        def progress(msg):
            console.print(f"  {msg}")

        try:
            count = generate_images_batch(
                cache, age, gender, image_dir, delay=delay, progress_callback=progress,
            )
        except RuntimeError as e:
            console.print(f"[red]{e}[/red]")
            return

        console.print(
            f"\n[bold green]Done![/bold green] {count} images generated in {image_dir}/"
        )


@cli.command("build-deck")
@click.option("--age", type=int, default=6, help="Target kid age (4-10)")
@click.option("--gender", type=click.Choice(["boy", "girl", "neutral"]), default="neutral")
@click.option("--deck-name", default=None, help="Custom deck name")
@click.option("-o", "--output", type=click.Path(), default=None, help="Output APKG path")
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE, help="Cache DB path")
@click.option("--generate-missing", is_flag=True, help="Generate mnemonics for uncached letters")
@click.option("--with-images", is_flag=True, help="Also generate DALL-E images if missing")
@click.option("--image-dir", type=click.Path(), default=DEFAULT_IMAGE_DIR, help="Image directory")
@click.option("--model", "-m", default=DEFAULT_MODEL, help="Claude model")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation")
def build_deck_cmd(age, gender, deck_name, output, cache_db, generate_missing, with_images, image_dir, model, yes):
    """Build an APKG deck from cached mnemonics and images."""
    letters = get_all_letters()

    if deck_name is None:
        deck_name = f"Russian ABC (age {age})"

    console.print(
        f"[bold]Building deck:[/bold] {deck_name}\n"
        f"  Letters: {len(letters)}\n"
        f"  Age: {age}, Gender: {gender}"
    )

    with AbcCache(cache_db) as cache:
        cached = cache.get_all(age, gender)
        uncached_count = len(letters) - len(cached)

        if uncached_count > 0:
            if generate_missing:
                console.print(
                    f"  [yellow]{uncached_count} letters not cached — generating...[/yellow]"
                )
                if not yes:
                    if not click.confirm("Generate missing mnemonics?"):
                        return

                def progress(msg):
                    console.print(f"    {msg}")

                cached = generate_mnemonics(
                    letters, age=age, gender=gender, cache=cache, model=model,
                    progress_callback=progress,
                )
            else:
                console.print(
                    f"  [yellow]Warning: {uncached_count} letters have no cached mnemonics. "
                    f"Use --generate-missing to generate them.[/yellow]"
                )

        # Optionally generate images
        if with_images:
            missing_images = cache.letters_without_images(age, gender)
            if missing_images:
                console.print(
                    f"  [yellow]{len(missing_images)} letters need images — generating...[/yellow]"
                )

                def img_progress(msg):
                    console.print(f"    {msg}")

                generate_images_batch(
                    cache, age, gender, image_dir, progress_callback=img_progress,
                )
                # Refresh cached data after image generation
                cached = cache.get_all(age, gender)

        tags = [
            "auto-generated",
            f"age::{age}",
            f"gender::{gender}",
            "russian-alphabet",
        ]

        def build_progress(msg):
            console.print(f"  {msg}")

        result_path = build_apkg(
            letters, cached, deck_name=deck_name, output_path=output, tags=tags,
            image_dir=image_dir, progress_callback=build_progress,
        )

        stats = cache.stats(age, gender)
        console.print(
            f"\n[bold green]Deck created:[/bold green] {result_path}\n"
            f"  {len(letters)} cards, {len(cached)} with mnemonics, "
            f"{stats['with_svg']} with SVG illustrations"
        )


@cli.command("preview")
@click.option("--age", type=int, default=6, help="Target kid age (4-10)")
@click.option("--gender", type=click.Choice(["boy", "girl", "neutral"]), default="neutral")
@click.option("--count", "-n", type=int, default=5, help="Number of letters to preview")
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE, help="Cache DB path")
def preview(age, gender, count, cache_db):
    """Preview sample letter cards."""
    letters = get_all_letters()[:count]

    with AbcCache(cache_db) as cache:
        cached = cache.get_all(age, gender)

    for lt in letters:
        data = cached.get(lt.lower)
        mnemonic = data["mnemonic"] if data else "[dim]not generated yet[/dim]"
        sound_tip = data.get("sound_tip", "") if data else ""
        fun_fact = data.get("fun_fact", "") if data else ""
        example_word = data.get("example_word", "") if data else ""
        example_trans = data.get("example_translation", "") if data else ""
        has_svg = bool(data.get("svg_content")) if data else False
        has_image = bool(data.get("image_path")) if data else False

        type_color = {"vowel": "red", "consonant": "blue", "sign": "dim"}.get(lt.letter_type, "white")

        content = (
            f"[bold]{lt.upper} {lt.lower}[/bold]  [{type_color}]({lt.letter_type})[/{type_color}]\n"
            f"Name: \"{lt.name}\"  |  Sound: [cyan]{lt.english_approx or '(none)'}[/cyan]\n"
        )
        if sound_tip:
            content += f"Tip: {sound_tip}\n"
        content += f"Mnemonic: {mnemonic}\n"
        if fun_fact:
            content += f"Fun fact: [yellow]{fun_fact}[/yellow]\n"
        if example_word:
            content += f"Example: [green]{example_word}[/green]"
            if example_trans:
                content += f" = {example_trans}"
            content += "\n"
        visuals = []
        if has_svg:
            visuals.append("[bold green]SVG[/bold green]")
        if has_image:
            visuals.append("[bold green]DALL-E[/bold green]")
        content += f"Visual: {', '.join(visuals) if visuals else '[dim]none[/dim]'}"

        console.print(Panel(content, title=f"#{lt.position}", width=75))


@cli.command("cache-status")
@click.option("--age", type=int, default=None, help="Filter by age")
@click.option("--gender", type=click.Choice(["boy", "girl", "neutral"]), default=None)
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE, help="Cache DB path")
def cache_status(age, gender, cache_db):
    """Show cache coverage statistics."""
    with AbcCache(cache_db) as cache:
        stats = cache.stats(age=age, gender=gender)

        table = Table(title="Russian ABC Cache")
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")

        table.add_row("Total cached", str(stats["total"]))
        table.add_row("With SVG visuals", f"[green]{stats['with_svg']}[/green]")
        table.add_row("With DALL-E images", f"[green]{stats['with_images']}[/green]")
        table.add_row("Without any visual", f"[yellow]{stats['without_visuals']}[/yellow]")

        if age is not None:
            table.add_row("Filtered by age", str(age))
        if gender is not None:
            table.add_row("Filtered by gender", gender)

        console.print(table)
        console.print(f"\n33 letters total, {stats['total']}/33 cached ({100 * stats['total'] / 33:.0f}%)")


@cli.command("set-key")
def set_key():
    """Store Anthropic API key in OS credential store."""
    existing = get_api_key()
    if existing:
        console.print("[yellow]An Anthropic API key is already stored.[/yellow]")
        if not click.confirm("Overwrite?"):
            return

    key = click.prompt("Enter your Anthropic API key", hide_input=True)
    if not key.strip():
        console.print("[red]Empty key, nothing stored.[/red]")
        return

    store_api_key(key.strip())
    console.print("[green]Anthropic API key stored.[/green]")


@cli.command("clear-key")
def clear_key():
    """Remove stored Anthropic API key."""
    delete_api_key()
    console.print("[green]Anthropic API key removed.[/green]")


@cli.command("set-openai-key")
def set_openai_key():
    """Store OpenAI API key for DALL-E image generation."""
    existing = get_openai_key()
    if existing:
        console.print("[yellow]An OpenAI API key is already stored.[/yellow]")
        if not click.confirm("Overwrite?"):
            return

    key = click.prompt("Enter your OpenAI API key", hide_input=True)
    if not key.strip():
        console.print("[red]Empty key, nothing stored.[/red]")
        return

    store_openai_key(key.strip())
    console.print("[green]OpenAI API key stored.[/green]")


@cli.command("clear-openai-key")
def clear_openai_key():
    """Remove stored OpenAI API key."""
    delete_openai_key()
    console.print("[green]OpenAI API key removed.[/green]")


if __name__ == "__main__":
    cli()
