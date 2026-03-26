"""Click CLI for English C1+ Anki deck generator."""
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
from rich.prompt import Prompt
from rich.table import Table

from .card_cache import CardCache
from .config import DEFAULT_CARD_CACHE, DEFAULT_LANG, DEFAULT_MODEL, DEFAULT_WORD_DB
from .deck_builder import build_apkg
from .generator import (
    GeneratedCard,
    delete_api_key,
    generate_batch_cached,
    generate_card,
    generate_card_cached,
    get_api_key,
    store_api_key,
)
from .normalizer import normalize_english
from .word_db import IN_ANKI, SKIPPED, WordDB
from .wordlists import get_all_lists, get_stats

console = Console()


def _display_card(card: GeneratedCard):
    """Display a generated card in the terminal."""
    pronunciation = f"  {card.pronunciation}" if card.pronunciation else ""
    console.print(Panel(
        f"[bold]{card.word}[/bold]  [dim]({card.part_of_speech})[/dim]  "
        f"[italic]{card.register}[/italic]{pronunciation}\n\n"
        f"[green]{card.definition_native}[/green]\n"
        f"[dim]{card.definition_en}[/dim]\n"
        + (f"[dim italic]{card.morphology}[/dim italic]\n" if card.morphology else ""),
        title="Definition", width=75,
    ))

    if card.examples:
        ex_text = ""
        for ex in card.examples:
            reg = f" [{ex.get('register', '')}]" if ex.get('register') else ""
            ex_text += f"  [blue]{ex.get('en', '')}[/blue][dim]{reg}[/dim]\n"
        console.print(Panel(ex_text.rstrip(), title="Examples", width=75))

    if card.collocations:
        console.print(f"  [bold]Collocations:[/bold] {', '.join(card.collocations)}")

    if card.synonyms:
        for s in card.synonyms:
            console.print(
                f"  [bold]{s.get('word', '')}[/bold] — "
                f"[dim]{s.get('distinction', '')}[/dim]"
            )

    if card.usage_note:
        console.print(f"  [yellow]Note:[/yellow] {card.usage_note}")
    if card.native_trap:
        console.print(f"  [red]Warning:[/red] {card.native_trap}")
    if card.cultural_note:
        console.print(f"  [blue]Culture:[/blue] {card.cultural_note}")


def _interactive_review(card: GeneratedCard, word: str) -> str:
    """Show card and prompt for action. Returns 'accept', 'regenerate', or 'skip'."""
    _display_card(card)
    console.print()
    action = Prompt.ask(
        "[bold]Action[/bold]",
        choices=["a", "r", "s"],
        default="a",
    )
    return {"a": "accept", "r": "regenerate", "s": "skip"}[action]


# ── Commands ──────────────────────────────────────────────────────

@click.group()
def cli():
    """English C1+ vocabulary deck generator for Russian speakers."""
    pass


@cli.command("import-lists")
@click.option("--category", "-c",
              type=click.Choice(["awl", "phrasal", "idiom", "all"]),
              default="all",
              help="Which list(s) to import: awl, phrasal, idiom, or all")
@click.option("--db", type=click.Path(), default=DEFAULT_WORD_DB,
              help="Word database path")
def import_lists(category, db):
    """Import built-in word lists (AWL, phrasal verbs, idioms) into the database."""
    all_lists = get_all_lists()
    categories = list(all_lists.keys()) if category == "all" else [category]

    with WordDB(db) as wdb:
        for cat in categories:
            words = all_lists[cat]
            stats = wdb.import_list(words, cat)
            console.print(
                f"  [bold]{cat}[/bold]: {stats['imported']} imported, "
                f"{stats['skipped']} already existed"
            )

        total = wdb.stats()
        console.print(f"\n[green]Total words in DB: {total['total']}[/green]")


@cli.command("status")
@click.option("--category", "-c", default=None,
              help="Filter by category (awl, phrasal, idiom, user)")
@click.option("--db", type=click.Path(), default=DEFAULT_WORD_DB,
              help="Word database path")
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE,
              help="Card cache path")
def status(category, db, cache_db):
    """Show word database and cache statistics."""
    with WordDB(db) as wdb:
        stats = wdb.stats(category)

        table = Table(title="English C1+ Word Database")
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")

        table.add_row("Total words", str(stats["total"]))
        table.add_row("Pending", f"[yellow]{stats['pending']}[/yellow]")
        table.add_row("In Anki", f"[green]{stats['in_anki']}[/green]")
        table.add_row("Skipped", f"[dim]{stats['skipped']}[/dim]")

        if stats.get("categories"):
            table.add_section()
            for cat, cnt in stats["categories"].items():
                table.add_row(f"  {cat}", str(cnt))

        console.print(table)

    with CardCache(cache_db) as cache:
        cs = cache.stats()
        console.print(f"\nCard cache: [green]{cs['total']}[/green] cards generated")


@cli.command("pending")
@click.option("--category", "-c", default=None,
              help="Filter by category")
@click.option("-n", "--count", type=int, default=20,
              help="Number of words to show")
@click.option("--db", type=click.Path(), default=DEFAULT_WORD_DB,
              help="Word database path")
def pending(category, count, db):
    """List unprocessed words."""
    with WordDB(db) as wdb:
        words = wdb.get_pending(category=category, limit=count)

    if not words:
        console.print("[green]No pending words![/green]")
        return

    table = Table(title=f"Pending Words ({len(words)} shown)")
    table.add_column("#", style="dim", justify="right")
    table.add_column("Word", style="bold")
    table.add_column("Category", style="cyan")
    table.add_column("Hint", style="dim")

    for i, w in enumerate(words, 1):
        table.add_row(str(i), w["original"], w["category"], w.get("hint", "") or "")

    console.print(table)


@cli.command("preview")
@click.argument("word")
@click.option("--model", "-m", default=DEFAULT_MODEL,
              help="Claude model to use")
@click.option("--lang", default=DEFAULT_LANG,
              help="Native language for definitions (ru, th, etc.)")
def preview(word, model, lang):
    """Preview a card for a word (dry run, no caching).

    Uses a language-specific prompt template from prompts/english/card_prompt_{lang}.txt
    """
    console.print(f"[bold]Generating preview for:[/bold] {word} [dim](lang={lang})[/dim]")
    try:
        card = generate_card(word, model=model, lang=lang)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        return
    _display_card(card)


@cli.command("add")
@click.argument("words", nargs=-1, required=True)
@click.option("--model", "-m", default=DEFAULT_MODEL,
              help="Claude model to use")
@click.option("--lang", default=DEFAULT_LANG,
              help="Native language for definitions (ru, th, etc.)")
@click.option("--db", type=click.Path(), default=DEFAULT_WORD_DB,
              help="Word database path")
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE,
              help="Card cache path")
@click.option("--no-review", is_flag=True,
              help="Auto-accept all cards without review")
@click.option("-o", "--output", type=click.Path(), default=None,
              help="Output APKG path (auto-generated if omitted)")
def add(words, model, lang, db, cache_db, no_review, output):
    """Add hand-picked words: generate cards, review, write APKG.

    Examples:
      python -m english_anki add ubiquitous eloquent albeit
      python -m english_anki add "break down" --lang th --no-review
    """
    accepted = []

    with WordDB(db) as wdb, CardCache(cache_db) as cache:
        for word in words:
            console.print(f"\n[bold]--- {word} ---[/bold]")

            # Add to DB if not there
            wdb.add_user_word(word)

            # Generate with retry loop
            force = False
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    card = generate_card_cached(word, cache, model=model, force=force, lang=lang)
                except FileNotFoundError as e:
                    console.print(f"[red]{e}[/red]")
                    return

                if no_review:
                    action = "accept"
                else:
                    action = _interactive_review(card, word)

                if action == "accept":
                    accepted.append(card)
                    wdb.mark_processed(word, IN_ANKI)
                    console.print(f"  [green]Accepted: {word}[/green]")
                    break
                elif action == "regenerate":
                    force = True
                    console.print("  [yellow]Regenerating...[/yellow]")
                elif action == "skip":
                    wdb.mark_processed(word, SKIPPED, "skipped during add")
                    console.print(f"  [dim]Skipped: {word}[/dim]")
                    break

    if not accepted:
        console.print("\n[yellow]No cards accepted.[/yellow]")
        return

    # Build APKG
    cards_dict = {normalize_english(c.word): c for c in accepted}
    tags = ["auto-generated", "source::add"]
    result_path = build_apkg(cards_dict, output_path=output, tags=tags, lang=lang)
    console.print(
        f"\n[bold green]APKG created:[/bold green] {result_path}\n"
        f"  {len(accepted)} words ({len(accepted) * 2} cards: recognition + recall)"
    )


@cli.command("generate")
@click.option("--category", "-c", default=None,
              help="Generate for a specific category (awl, phrasal, idiom, user)")
@click.option("-n", "--count", type=int, default=None,
              help="Max words to generate (default: all pending)")
@click.option("--model", "-m", default=DEFAULT_MODEL,
              help="Claude model to use")
@click.option("--lang", default=DEFAULT_LANG,
              help="Native language for definitions (ru, th, etc.)")
@click.option("--db", type=click.Path(), default=DEFAULT_WORD_DB,
              help="Word database path")
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE,
              help="Card cache path")
@click.option("-y", "--yes", is_flag=True,
              help="Skip confirmation prompt")
@click.option("--delay", type=float, default=1.0,
              help="Delay between API batches in seconds")
def generate_cmd(category, count, model, lang, db, cache_db, yes, delay):
    """Generate cards for pending words from the database.

    Uses the word DB to find unprocessed words, generates cards via Claude API,
    and caches results. Does NOT build an APKG — use build-deck for that.

    Examples:
      python -m english_anki generate --category awl -n 50 -y
      python -m english_anki generate -c phrasal --lang th -y
      python -m english_anki generate  # all pending words
    """
    with WordDB(db) as wdb:
        pending_words = wdb.get_pending(category=category, limit=count)

    if not pending_words:
        console.print("[green]No pending words to generate![/green]")
        return

    word_strs = [w["original"] for w in pending_words]
    console.print(
        f"[bold]Generating cards for {len(word_strs)} words[/bold]"
        + (f" (category: {category})" if category else "")
    )

    if not yes and not click.confirm("Proceed?"):
        return

    with CardCache(cache_db) as cache:
        def progress(msg):
            console.print(f"  {msg}")

        try:
            result = generate_batch_cached(
                word_strs, cache, model=model, delay=delay,
                progress_callback=progress, lang=lang,
            )
        except FileNotFoundError as e:
            console.print(f"[red]{e}[/red]")
            return

        console.print(f"\n[bold green]Done![/bold green] {len(result)} cards cached.")


@cli.command("skip")
@click.argument("words", nargs=-1, required=True)
@click.option("--reason", "-r", default=None,
              help="Reason for skipping")
@click.option("--db", type=click.Path(), default=DEFAULT_WORD_DB,
              help="Word database path")
def skip(words, reason, db):
    """Mark words as skipped in the database.

    Examples:
      python -m english_anki skip area data --reason "already know"
    """
    with WordDB(db) as wdb:
        for word in words:
            if wdb.mark_processed(word, SKIPPED, reason):
                console.print(f"  [dim]Skipped: {word}[/dim]")
            else:
                console.print(f"  [yellow]Not found: {word}[/yellow]")


@cli.command("build-deck")
@click.option("--category", "-c", default=None,
              help="Build from specific category only")
@click.option("--deck-name", default=None,
              help="Custom deck name")
@click.option("-o", "--output", type=click.Path(), default=None,
              help="Output APKG path")
@click.option("--lang", default=DEFAULT_LANG,
              help="Native language for definitions (ru, th, etc.)")
@click.option("--db", type=click.Path(), default=DEFAULT_WORD_DB,
              help="Word database path")
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE,
              help="Card cache path")
@click.option("--generate-missing", is_flag=True,
              help="Generate cards for uncached words before building")
@click.option("--model", "-m", default=DEFAULT_MODEL,
              help="Claude model (if --generate-missing)")
@click.option("-y", "--yes", is_flag=True,
              help="Skip confirmation")
def build_deck_cmd(category, deck_name, output, lang, db, cache_db, generate_missing, model, yes):
    """Build an APKG deck from cached cards.

    Assembles all cached words (or a specific category) into an Anki deck.
    Each word produces two cards: Recognition (EN→RU) and Recall (RU→EN).

    Examples:
      python -m english_anki build-deck -o english_c1.apkg
      python -m english_anki build-deck -c awl --deck-name "Academic English" -o awl.apkg
      python -m english_anki build-deck -c phrasal --generate-missing -y -o phrasal.apkg
    """
    with WordDB(db) as wdb:
        if category:
            words = wdb.get_by_category(category)
        else:
            words = wdb.get_all()

    if not words:
        console.print("[red]No words in database. Run import-lists first.[/red]")
        return

    word_strs = [w["original"] for w in words]

    if deck_name is None:
        if category:
            deck_name = f"English C1+ — {category.upper()}"
        else:
            deck_name = "English C1+"

    console.print(
        f"[bold]Building deck:[/bold] {deck_name}\n"
        f"  Words: {len(word_strs)}"
        + (f" (category: {category})" if category else "")
    )

    with CardCache(cache_db) as cache:
        cached_data = cache.get_batch(word_strs)
        uncached = [w for w in word_strs if normalize_english(w) not in cached_data]

        if uncached:
            if generate_missing:
                console.print(f"  [yellow]{len(uncached)} words not cached — generating...[/yellow]")
                if not yes and not click.confirm("Generate missing cards?"):
                    return

                def progress(msg):
                    console.print(f"    {msg}")

                from .generator import generate_batch_cached, _dict_to_card
                try:
                    result = generate_batch_cached(
                        word_strs, cache, model=model, progress_callback=progress, lang=lang,
                    )
                except FileNotFoundError as e:
                    console.print(f"[red]{e}[/red]")
                    return
                cards_dict = result
            else:
                console.print(
                    f"  [yellow]Warning: {len(uncached)} words not cached. "
                    f"Use --generate-missing to generate.[/yellow]"
                )
                # Build with what we have
                from .generator import _dict_to_card
                cards_dict = {k: _dict_to_card(v) for k, v in cached_data.items()}
        else:
            from .generator import _dict_to_card
            cards_dict = {k: _dict_to_card(v) for k, v in cached_data.items()}

    tags = ["auto-generated"]
    if category:
        tags.append(f"category::{category}")

    result_path = build_apkg(cards_dict, deck_name=deck_name, output_path=output, tags=tags, lang=lang)
    console.print(
        f"\n[bold green]Deck created:[/bold green] {result_path}\n"
        f"  {len(cards_dict)} words ({len(cards_dict) * 2} cards: recognition + recall)"
    )


@cli.command("cache-status")
@click.option("--cache-db", type=click.Path(), default=DEFAULT_CARD_CACHE,
              help="Card cache path")
def cache_status(cache_db):
    """Show card cache statistics."""
    with CardCache(cache_db) as cache:
        stats = cache.stats()
        console.print(
            f"Card cache: [green]{stats['total']}[/green] words cached"
        )
        if stats.get("models"):
            for m, cnt in stats["models"].items():
                console.print(f"  {m}: {cnt}")


@cli.command("set-key")
def set_key():
    """Store Anthropic API key in OS credential store."""
    existing = get_api_key()
    if existing:
        console.print("[yellow]Key already stored.[/yellow]")
        if not click.confirm("Overwrite?"):
            return
    key = click.prompt("Anthropic API key", hide_input=True)
    if key.strip():
        store_api_key(key.strip())
        console.print("[green]Stored.[/green]")


@cli.command("clear-key")
def clear_key():
    """Remove stored Anthropic API key."""
    delete_api_key()
    console.print("[green]Removed.[/green]")


if __name__ == "__main__":
    cli()
