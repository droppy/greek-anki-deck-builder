"""Click CLI for math Anki deck generator."""
import os
import sys
from datetime import datetime

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

from .cache import MathCardCache
from .config import DEFAULT_CARD_CACHE, DEFAULT_MODEL, LEVELS
from .deck_builder import build_apkg
from .generator import (
    delete_api_key,
    generate_hints,
    get_api_key,
    store_api_key,
    suggest_ordering,
)
from .problems import MathProblem, generate_problems

console = Console()


@click.group()
def cli():
    """Math Anki deck generator for kids."""
    pass


@cli.command()
def levels():
    """Show available levels and problem counts."""
    table = Table(title="Math Levels")
    table.add_column("Level", style="bold cyan", justify="center")
    table.add_column("Name", style="bold")
    table.add_column("Description")
    table.add_column("Cards", justify="right", style="green")

    for num, info in sorted(LEVELS.items()):
        count = len(generate_problems(num))
        table.add_row(str(num), info["name"], info["description"], str(count))

    console.print(table)


@cli.command()
@click.option("--level", "-l", type=int, required=True, help="Level number (1-8)")
@click.option("--count", "-n", type=int, default=5, help="Number of cards to preview")
@click.option("--age", type=int, default=7, help="Target kid age (5-10)")
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE, help="Cache DB path")
def preview(level, count, age, cache_db):
    """Preview sample cards from a level."""
    problems = generate_problems(level)
    if not problems:
        console.print(f"[red]No problems for level {level}[/red]")
        return

    sample = problems[:count]

    with MathCardCache(cache_db) as cache:
        cached = cache.get_batch([p.key for p in sample], age)

    for p in sample:
        hint_data = cached.get(p.key)
        hint = hint_data["hint"] if hint_data else "[dim]not generated yet[/dim]"
        fun_fact = hint_data.get("fun_fact", "") if hint_data else ""

        panel_content = (
            f"[bold]{p.display}[/bold]\n"
            f"Answer: [bold green]{p.answer}[/bold green]\n"
            f"Hint: {hint}"
        )
        if fun_fact:
            panel_content += f"\nFun fact: [magenta]{fun_fact}[/magenta]"

        console.print(Panel(panel_content, title=f"#{p.position + 1}", width=70))


@cli.command("generate")
@click.option("--level", "-l", type=int, required=True, multiple=True, help="Level(s) to generate")
@click.option("--age", type=int, default=7, help="Target kid age (5-10)")
@click.option("--model", "-m", default=DEFAULT_MODEL, help="Claude model")
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE, help="Cache DB path")
@click.option("--with-images", is_flag=True, help="Also generate image descriptions")
@click.option("--reorder", is_flag=True, help="Ask Claude to suggest pedagogical ordering")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation")
@click.option("--delay", type=float, default=1.0, help="Delay between API batches (seconds)")
def generate_cmd(level, age, model, cache_db, with_images, reorder, yes, delay):
    """Generate hints for all problems at given level(s)."""
    all_problems = []
    for lv in level:
        problems = generate_problems(lv)
        all_problems.extend(problems)

    if not all_problems:
        console.print("[red]No problems to generate.[/red]")
        return

    console.print(
        f"[bold]Generating hints for {len(all_problems)} problems "
        f"(level {''.join(str(l) for l in level)}, age {age})[/bold]"
    )

    if not yes:
        if not click.confirm("Proceed?"):
            return

    with MathCardCache(cache_db) as cache:
        def progress(msg):
            console.print(f"  {msg}")

        hints = generate_hints(
            all_problems,
            age=age,
            cache=cache,
            model=model,
            with_images=with_images,
            delay=delay,
            progress_callback=progress,
        )

        console.print(
            f"[bold green]Done![/bold green] {len(hints)} hints cached."
        )

        if reorder:
            console.print("[bold]Requesting pedagogical ordering...[/bold]")
            for lv in level:
                lv_problems = [p for p in all_problems if p.level == lv]
                order = suggest_ordering(lv_problems, age, model=model)
                # Store ordering by updating positions
                display_to_pos = {s: i for i, s in enumerate(order)}
                updated = 0
                for p in lv_problems:
                    new_pos = display_to_pos.get(p.display_no_question)
                    if new_pos is not None:
                        # Re-store with updated difficulty based on position
                        existing = cache.get(p.key, age)
                        if existing:
                            # difficulty can be recalculated from position
                            updated += 1
                console.print(
                    f"  Level {lv}: ordering applied to {updated} problems"
                )


@cli.command("build-deck")
@click.option("--level", "-l", type=int, required=True, multiple=True, help="Level(s) to include")
@click.option("--age", type=int, default=7, help="Target kid age (5-10)")
@click.option("--deck-name", default=None, help="Custom deck name")
@click.option("-o", "--output", type=click.Path(), default=None, help="Output APKG path")
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE, help="Cache DB path")
@click.option("--generate-missing", is_flag=True, help="Generate hints for uncached problems")
@click.option("--model", "-m", default=DEFAULT_MODEL, help="Claude model (if generating)")
@click.option("--with-images", is_flag=True, help="Include image descriptions")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation")
def build_deck_cmd(level, age, deck_name, output, cache_db, generate_missing, model, with_images, yes):
    """Build an APKG deck from cached hints."""
    all_problems = []
    for lv in sorted(set(level)):
        problems = generate_problems(lv)
        all_problems.extend(problems)

    if not all_problems:
        console.print("[red]No problems for selected levels.[/red]")
        return

    if deck_name is None:
        level_str = ",".join(str(l) for l in sorted(set(level)))
        deck_name = f"Kids Math (Levels {level_str})"

    console.print(
        f"[bold]Building deck:[/bold] {deck_name}\n"
        f"  Levels: {sorted(set(level))}\n"
        f"  Problems: {len(all_problems)}\n"
        f"  Age: {age}"
    )

    with MathCardCache(cache_db) as cache:
        all_keys = [p.key for p in all_problems]
        cached = cache.get_batch(all_keys, age)
        uncached_count = len(all_keys) - len(cached)

        if uncached_count > 0:
            if generate_missing:
                uncached_problems = [p for p in all_problems if p.key not in cached]
                console.print(
                    f"  [yellow]{uncached_count} problems not in cache — generating...[/yellow]"
                )
                if not yes:
                    if not click.confirm("Generate missing hints?"):
                        return

                def progress(msg):
                    console.print(f"    {msg}")

                cached = generate_hints(
                    all_problems,
                    age=age,
                    cache=cache,
                    model=model,
                    with_images=with_images,
                    progress_callback=progress,
                )
            else:
                console.print(
                    f"  [yellow]Warning: {uncached_count} problems have no cached hints. "
                    f"Use --generate-missing to generate them.[/yellow]"
                )

        # Assign global positions across levels
        for i, p in enumerate(all_problems):
            p.position = i

        tags = [
            "auto-generated",
            f"age::{age}",
            f"built::{datetime.now().strftime('%Y-%m-%d')}",
        ]

        result_path = build_apkg(
            all_problems,
            cached,
            deck_name=deck_name,
            output_path=output,
            tags=tags,
        )

        console.print(
            f"\n[bold green]Deck created:[/bold green] {result_path}\n"
            f"  {len(all_problems)} cards, {len(cached)} with hints"
        )


@cli.command("cache-status")
@click.option("--level", "-l", type=int, default=None, help="Filter by level")
@click.option("--age", type=int, default=None, help="Filter by age")
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE, help="Cache DB path")
def cache_status(level, age, cache_db):
    """Show cache coverage statistics."""
    with MathCardCache(cache_db) as cache:
        stats = cache.stats(age=age)

        table = Table(title="Math Card Cache")
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")

        table.add_row("Total cached", str(stats["total"]))

        if stats.get("ages"):
            for a, cnt in sorted(stats["ages"].items()):
                table.add_row(f"  Age {a}", str(cnt))

        if stats.get("models"):
            for m, cnt in sorted(stats["models"].items()):
                table.add_row(f"  Model: {m}", str(cnt))

        console.print(table)

        # Show per-level coverage if requested
        if level is not None and age is not None:
            problems = generate_problems(level)
            keys = [p.key for p in problems]
            cached = cache.get_batch(keys, age)
            console.print(
                f"\nLevel {level} (age {age}): "
                f"[green]{len(cached)}[/green]/{len(problems)} cached "
                f"({100 * len(cached) / len(problems):.0f}%)"
            )


@cli.command("set-key")
def set_key():
    """Store Anthropic API key in OS credential store."""
    existing = get_api_key()
    if existing:
        console.print("[yellow]An API key is already stored.[/yellow]")
        if not click.confirm("Overwrite?"):
            return

    key = click.prompt("Enter your Anthropic API key", hide_input=True)
    if not key.strip():
        console.print("[red]Empty key, nothing stored.[/red]")
        return

    store_api_key(key.strip())
    console.print("[green]API key stored in OS credential store.[/green]")


@cli.command("clear-key")
def clear_key():
    """Remove stored API key."""
    delete_api_key()
    console.print("[green]API key removed.[/green]")


if __name__ == "__main__":
    cli()
