"""Click-based CLI entry point."""
import csv as csv_mod
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Force UTF-8 output on Windows to avoid cp1252 encoding errors
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

import genanki

from .anki_deck import AnkiNote, create_supplement_apkg, get_anki_model, read_apkg_notes
from .config import DEFAULT_APKG, DEFAULT_CARD_CACHE, DEFAULT_FREQ_DB, DEFAULT_MODEL, DECK_ID, DECK_NAME
from .freq_list import IN_ANKI, SKIPPED, FreqDB
from .matcher import freq_word_in_anki, normalize_greek

console = Console()


@click.group()
@click.version_option()
def cli():
    """Greek Anki Deck Builder - manage flashcards with Claude AI."""


# ======================================================================
# API key management (stored in Windows Credential Manager / macOS Keychain)
# ======================================================================


@cli.command("set-key")
def set_key():
    """Store Anthropic API key in the OS credential store."""
    from .claude_generator import get_api_key, store_api_key

    existing = get_api_key()
    if existing:
        console.print("[dim]An API key is already stored.[/dim]")
        if not click.confirm("Overwrite?"):
            return

    key = Prompt.ask("Anthropic API key", password=True)
    if not key.strip():
        console.print("[red]Empty key, aborting.[/red]")
        return

    store_api_key(key.strip())
    console.print("[green]API key saved to OS credential store.[/green]")


@cli.command("clear-key")
def clear_key():
    """Remove stored API key from the OS credential store."""
    from .claude_generator import delete_api_key

    delete_api_key()
    console.print("[green]API key removed.[/green]")


# ======================================================================
# Phase 1 commands: import-freq, sync, status, pending, skip
# ======================================================================


@cli.command("import-freq")
@click.argument("csv_path", type=click.Path(exists=True))
@click.option(
    "--output", "-o", default=DEFAULT_FREQ_DB, help="Output SQLite database path"
)
@click.option("--no-auto-skip", is_flag=True, help="Don't auto-skip function words")
def import_freq(csv_path: str, output: str, no_auto_skip: bool):
    """Import frequency list CSV into SQLite database."""
    with FreqDB(output) as db:
        stats = db.import_csv(csv_path, auto_skip_function_words=not no_auto_skip)

    console.print(f"\n[bold green]Import complete:[/bold green] {output}")
    console.print(f"  Total rows processed: {stats['total_rows']}")
    console.print(f"  Imported:             {stats['imported']}")
    console.print(f"  Empty rows skipped:   {stats['empty_skipped']}")
    console.print(f"  Duplicates skipped:   {stats['duplicates_skipped']}")
    if not no_auto_skip:
        console.print(
            f"  Function words auto-skipped: {stats['function_words_skipped']}"
        )


@cli.command()
@click.argument("freq_db", type=click.Path(exists=True))
@click.argument("apkg_path", type=click.Path(exists=True))
def sync(freq_db: str, apkg_path: str):
    """Mark frequency words already in APKG as processed."""
    console.print(f"Reading APKG: {apkg_path}...")
    notes = read_apkg_notes(apkg_path)
    console.print(f"  Found {len(notes)} notes")

    back_fields = [n.back for n in notes]

    console.print("Matching against frequency list...")
    with FreqDB(freq_db) as db:
        pending = db.get_pending()
        matched_words = []

        for row in pending:
            if freq_word_in_anki(row["greek"], back_fields):
                matched_words.append(row["greek"])

        if matched_words:
            count = db.mark_many_processed(
                matched_words, status=IN_ANKI, notes="sync: found in APKG"
            )
            console.print(
                f"\n[bold green]Sync complete:[/bold green] "
                f"{count} words marked as in_anki"
            )
        else:
            console.print("\n[yellow]No new matches found.[/yellow]")


@cli.command()
@click.argument("freq_db", type=click.Path(exists=True))
def status(freq_db: str):
    """Show frequency list status dashboard."""
    with FreqDB(freq_db) as db:
        summary = db.get_status_summary()

    console.print(f"\n[bold]Frequency List:[/bold] {summary['total']} words")
    console.print(f"  [green]\u2713 In Anki:[/green]  {summary['in_anki']:,}")
    console.print(f"  [yellow]\u25cb Pending:[/yellow]  {summary['pending']:,}")
    console.print(f"  [red]\u2717 Skipped:[/red]  {summary['skipped']:,}")

    console.print(f"\n[bold]Range breakdown:[/bold]")
    table = Table(show_header=True)
    table.add_column("Range", style="cyan")
    table.add_column("In Anki", justify="right")
    table.add_column("Pending", justify="right")
    table.add_column("Skipped", justify="right")
    table.add_column("Coverage", justify="right")

    for r in summary["ranges"]:
        if r["total"] == 0:
            continue
        coverage = (r["in_anki"] / r["total"] * 100) if r["total"] > 0 else 0
        style = "green" if coverage >= 80 else "yellow" if coverage >= 50 else "red"
        table.add_row(
            f"[{r['start']}-{r['end']}]",
            str(r["in_anki"]),
            str(r["pending"]),
            str(r["skipped"]),
            f"[{style}]{coverage:.1f}%[/{style}]",
        )

    console.print(table)


@cli.command()
@click.argument("freq_db", type=click.Path(exists=True))
@click.option(
    "--range", "rank_range", nargs=2, type=int, default=None, help="Rank range"
)
@click.option("--limit", "-n", type=int, default=None, help="Limit results")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["table", "csv"]),
    default="table",
)
def pending(freq_db: str, rank_range, limit: int, fmt: str):
    """List pending (unprocessed) words."""
    range_start = rank_range[0] if rank_range else None
    range_end = rank_range[1] if rank_range else None

    with FreqDB(freq_db) as db:
        rows = db.get_pending(range_start, range_end, limit)

    if fmt == "csv":
        click.echo("rank,greek,frequency")
        for r in rows:
            click.echo(f"{r['rank']},{r['greek']},{r['frequency']}")
    else:
        table = Table(show_header=True)
        table.add_column("Rank", justify="right")
        table.add_column("Greek")
        table.add_column("Frequency", justify="right")
        for r in rows:
            table.add_row(str(r["rank"]), r["greek"], str(r["frequency"]))
        console.print(table)
        console.print(f"\n[dim]{len(rows)} pending words[/dim]")


@cli.command()
@click.argument("freq_db", type=click.Path(exists=True))
@click.argument("words", nargs=-1, required=True)
@click.option("--reason", "-r", default=None, help="Reason for skipping")
def skip(freq_db: str, words: tuple, reason: str):
    """Mark words as skipped (won't be added to Anki)."""
    with FreqDB(freq_db) as db:
        count = db.skip_words(list(words), reason)
    console.print(f"[green]Skipped {count} word(s)[/green]")


# ======================================================================
# Phase 2 commands: add, preview
# ======================================================================


def _display_card_preview(card) -> None:
    """Display a generated card for interactive review."""
    console.print(
        Panel(
            f"[bold]{card.front_ru}[/bold]\n\n{card.front_en}",
            title="Front (translations)",
            border_style="blue",
        )
    )

    pos_line = f"\n[dim]{card.part_of_speech}[/dim]" if card.part_of_speech else ""
    console.print(
        Panel(
            f"[bold]{card.back}[/bold]{pos_line}",
            title="Back (Greek)",
            border_style="green",
        )
    )

    if card.examples:
        lines = []
        for i, ex in enumerate(card.examples, 1):
            lines.append(f"{i}. {ex['greek']}\n   {ex['russian']}")
        console.print(Panel("\n".join(lines), title="Examples", border_style="yellow"))

    comment_parts = []
    if card.conjugation:
        comment_parts.append(f"Conjugation: {card.conjugation}")
    if card.synonyms:
        comment_parts.append("Synonyms:")
        for syn in card.synonyms:
            comment_parts.append(f"  \u2022 {syn['word']}: {syn['distinction']}")

    if comment_parts:
        console.print(
            Panel("\n".join(comment_parts), title="Comment", border_style="magenta")
        )

    if card.collocations:
        console.print(
            Panel(
                "\n".join(f"\u2022 {c}" for c in card.collocations),
                title="Collocations",
                border_style="cyan",
            )
        )

    if card.etymology_note:
        console.print(
            Panel(card.etymology_note, title="Etymology", border_style="dim")
        )


def _interactive_review(card, word: str) -> str:
    """Show card and prompt for action. Returns action string."""
    _display_card_preview(card)
    console.print()
    action = Prompt.ask(
        "[bold]Action[/bold]  [a]ccept / [r]egenerate / [s]kip",
        choices=["a", "r", "s"],
        default="a",
    )
    return {"a": "accept", "r": "regenerate", "s": "skip"}[action]


@cli.command()
@click.argument("words", nargs=-1, required=True)
@click.option("--freq-db", type=click.Path(exists=True), default=None,
              help="Frequency list DB (for marking processed)")
@click.option("--apkg", type=click.Path(exists=True), default=None,
              help="Existing APKG to check for duplicates")
@click.option("--cache", "cache_path", type=click.Path(), default=DEFAULT_CARD_CACHE,
              help="Card cache database path")
@click.option("--model", default=DEFAULT_MODEL, help="Claude model to use")
@click.option("--no-review", is_flag=True, help="Skip interactive review")
def add(words: tuple, freq_db: str, apkg: str, cache_path: str, model: str, no_review: bool):
    """Add one or more words: generate via Claude, review, and create APKG.

    \b
    Examples:
      python -m greek_anki add αίτηση
      python -m greek_anki add αίτηση πρόταση κίνηση
      python -m greek_anki add αίτηση --apkg AZ_greek_words.apkg --freq-db freq_list.sq3
    """
    from .card_cache import CardCache, generate_card_cached
    import genanki

    # Load existing deck for duplicate checking (optional)
    back_fields = []
    if apkg:
        console.print(f"Reading deck: {apkg}...")
        notes = read_apkg_notes(apkg)
        back_fields = [n.back for n in notes]
        console.print(f"  {len(notes)} existing notes loaded for duplicate check")

    accepted_cards: list = []  # [(GeneratedCard, word, tags)]

    with CardCache(cache_path) as cache:
        for i, word in enumerate(words, 1):
            console.print(
                f"\n[bold]\u2500\u2500 [{i}/{len(words)}] {word} \u2500\u2500[/bold]"
            )

            # Duplicate check
            if back_fields and freq_word_in_anki(word, back_fields):
                console.print(f"[yellow]Already in deck, skipping.[/yellow]")
                if freq_db:
                    with FreqDB(freq_db) as db:
                        db.mark_processed(word, status=IN_ANKI, notes="already in deck")
                continue

            # Generate with retry loop
            card = None
            force = False
            for _attempt in range(3):
                console.print(f"Generating card for [bold]{word}[/bold]...")
                try:
                    card = generate_card_cached(word, cache, model=model, force=force)
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                    continue

                if no_review:
                    action = "accept"
                else:
                    action = _interactive_review(card, word)

                if action == "accept":
                    break
                elif action == "regenerate":
                    console.print("[dim]Regenerating...[/dim]")
                    force = True  # bypass cache on regenerate
                    continue
                elif action == "skip":
                    console.print("[yellow]Skipped.[/yellow]")
                    if freq_db:
                        with FreqDB(freq_db) as db:
                            db.mark_processed(word, status=SKIPPED, notes="skipped during add")
                    card = None
                    break
            else:
                console.print("[red]Max attempts reached, skipping.[/red]")
                card = None

            if card is None:
                continue

            # Build per-word tags
            tags = [
                "auto-generated",
                f"added::{datetime.now().strftime('%Y-%m')}",
                f"pos::{card.part_of_speech}",
            ]
            if freq_db:
                with FreqDB(freq_db) as db:
                    freq_row = db.get_word_by_greek(word)
                    if freq_row:
                        rank = freq_row["rank"]
                        rs = ((rank - 1) // 500) * 500 + 1
                        tags.append(f"freq::{rs}-{rs + 499}")

            accepted_cards.append((card, word, tags))

    # Write all accepted cards to one APKG
    if not accepted_cards:
        console.print("\n[yellow]No cards to write.[/yellow]")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_name = f"AZ_update_{timestamp}.apkg"

    model_obj = get_anki_model()
    deck = genanki.Deck(DECK_ID, DECK_NAME)
    for card, _word, tags in accepted_cards:
        nd = card.to_note_dict()
        note = genanki.Note(
            model=model_obj,
            fields=[
                nd["front"], nd["back"], nd["example"], nd["comment"],
                nd["collocations"], nd["etymology"],
            ],
            tags=tags,
        )
        deck.add_note(note)

    output_path = Path(output_name)
    genanki.Package(deck).write_to_file(str(output_path))

    # Mark all as processed in freq DB
    if freq_db:
        with FreqDB(freq_db) as db:
            for card, word, _ in accepted_cards:
                db.mark_processed(word, status=IN_ANKI, notes=f"added -> {output_name}")

    console.print(f"\n[bold green]Done! {len(accepted_cards)} card(s) created.[/bold green]")
    console.print(f"  Import [cyan]{output_path}[/cyan] into Anki")


@cli.command()
@click.argument("word")
@click.option("--model", default=DEFAULT_MODEL, help="Claude model to use")
def preview(word: str, model: str):
    """Preview Claude-generated card (dry run, no write)."""
    from .claude_generator import generate_card

    console.print(f"Generating preview for [bold]{word}[/bold]...")
    card = generate_card(word, model=model)
    _display_card_preview(card)

    console.print(
        f"\n[dim]Input tokens: {card._usage['input_tokens']}, "
        f"Output tokens: {card._usage['output_tokens']}[/dim]"
    )


# ======================================================================
# Phase 3 commands: add-batch, enrich, export
# ======================================================================


def _create_batch_apkg(cards_with_tags: list, output_path: str) -> Path:
    """Create an APKG with per-note tags."""
    import genanki

    model = get_anki_model()
    deck = genanki.Deck(DECK_ID, DECK_NAME)

    for card, _word, tags in cards_with_tags:
        nd = card.to_note_dict()
        note = genanki.Note(
            model=model,
            fields=[
                nd["front"], nd["back"], nd["example"], nd["comment"],
                nd["collocations"], nd["etymology"],
            ],
            tags=tags,
        )
        deck.add_note(note)

    output_path = Path(output_path)
    genanki.Package(deck).write_to_file(str(output_path))
    return output_path


@cli.command("add-batch")
@click.argument("freq_db", type=click.Path(exists=True))
@click.argument("apkg_path", type=click.Path(exists=True))
@click.option("--range", "rank_range", nargs=2, type=int, default=None, help="Rank range")
@click.option("--count", "-n", type=int, required=True, help="Number of words")
@click.option("--cache", "cache_path", type=click.Path(), default=DEFAULT_CARD_CACHE,
              help="Card cache database path")
@click.option("--model", default=DEFAULT_MODEL)
@click.option("--delay", type=float, default=0.5, help="Delay between API calls (s)")
@click.option("--no-review", is_flag=True, help="Skip interactive review")
@click.option("--yes", "-y", is_flag=True, help="Skip cost estimation prompt")
def add_batch(
    freq_db, apkg_path, rank_range, count, cache_path, model, delay, no_review, yes
):
    """Add N random pending words from frequency list via Claude API.

    Picks random pending words, checks for duplicates against the APKG,
    generates cards, and marks them as processed. For generating fresh
    shareable decks, use build-deck instead.

    \b
    Examples:
      python -m greek_anki add-batch freq_list.sq3 deck.apkg -n 10 --range 1 500
      python -m greek_anki add-batch freq_list.sq3 deck.apkg -n 50 --no-review -y
    """
    from .card_cache import CardCache, generate_card_cached

    range_start = rank_range[0] if rank_range else None
    range_end = rank_range[1] if rank_range else None

    with FreqDB(freq_db) as db:
        pending_rows = db.get_pending(range_start, range_end)

    if not pending_rows:
        console.print("[yellow]No pending words in the specified range.[/yellow]")
        return

    if len(pending_rows) > count:
        selected = random.sample(list(pending_rows), count)
    else:
        selected = list(pending_rows)

    if len(selected) < count:
        console.print(
            f"[yellow]Only {len(selected)} pending words available "
            f"(requested {count})[/yellow]"
        )

    # Count how many are already cached (no API cost)
    with CardCache(cache_path) as cache:
        cached_count = sum(1 for row in selected if cache.get(row["greek"]) is not None)
    api_count = len(selected) - cached_count

    # Cost estimation
    estimated_tokens = api_count * 800
    estimated_cost = estimated_tokens * 0.000015
    if not yes:
        console.print(f"\n[bold]Batch estimation:[/bold]")
        console.print(f"  Words to process: {len(selected)}")
        if cached_count > 0:
            console.print(f"  Already cached:   {cached_count} (no API cost)")
        console.print(f"  API calls needed: {api_count}")
        console.print(f"  Estimated cost:   ~${estimated_cost:.2f}")
        if not click.confirm("Proceed?"):
            return

    # Duplicate check against existing deck
    console.print(f"Reading existing deck: {apkg_path}...")
    notes = read_apkg_notes(apkg_path)
    back_fields = [n.back for n in notes]

    accepted_cards: list = []
    tags_base = [
        "auto-generated",
        f"added::{datetime.now().strftime('%Y-%m')}",
        "source::batch",
    ]

    with CardCache(cache_path) as cache:
        for i, row in enumerate(selected, 1):
            word = row["greek"]
            rank = row["rank"]

            console.print(
                f"\n[bold]\u2500\u2500 [{i}/{len(selected)}] {word} (rank {rank}) \u2500\u2500[/bold]"
            )

            if freq_word_in_anki(word, back_fields):
                console.print("[yellow]Already in deck, skipping[/yellow]")
                with FreqDB(freq_db) as db:
                    db.mark_processed(
                        word, status=IN_ANKI, notes="sync: found during batch"
                    )
                continue

            try:
                card = generate_card_cached(word, cache, model=model)
            except Exception as e:
                console.print(f"[red]Error generating card: {e}[/red]")
                continue

            if no_review:
                action = "accept"
            else:
                action = _interactive_review(card, word)

            if action == "accept":
                rs = ((rank - 1) // 500) * 500 + 1
                card_tags = tags_base + [
                    f"pos::{card.part_of_speech}",
                    f"freq::{rs}-{rs + 499}",
                ]
                accepted_cards.append((card, word, card_tags))
            elif action == "skip":
                with FreqDB(freq_db) as db:
                    db.mark_processed(
                        word, status=SKIPPED, notes="skipped during batch"
                    )
            elif action == "regenerate":
                try:
                    card = generate_card_cached(word, cache, model=model, force=True)
                    _display_card_preview(card)
                    if click.confirm("Accept this version?"):
                        rs = ((rank - 1) // 500) * 500 + 1
                        card_tags = tags_base + [
                            f"pos::{card.part_of_speech}",
                            f"freq::{rs}-{rs + 499}",
                        ]
                        accepted_cards.append((card, word, card_tags))
                except Exception as e:
                    console.print(f"[red]Regeneration failed: {e}[/red]")

            if i < len(selected):
                time.sleep(delay)

    if accepted_cards:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_name = f"AZ_batch_{timestamp}.apkg"
        output_path = _create_batch_apkg(accepted_cards, output_name)

        with FreqDB(freq_db) as db:
            for card, word, _ in accepted_cards:
                db.mark_processed(
                    word, status=IN_ANKI, notes=f"batch add -> {output_name}"
                )

        console.print(f"\n[bold green]Batch complete![/bold green]")
        console.print(f"  Cards created: {len(accepted_cards)}")
        console.print(f"  Import [cyan]{output_path}[/cyan] into Anki")
    else:
        console.print("\n[yellow]No cards were accepted.[/yellow]")


@cli.command()
@click.argument("apkg_path", type=click.Path(exists=True))
@click.option("--limit", "-n", type=int, default=10, help="Number of cards to enrich")
@click.option("--model", default=DEFAULT_MODEL)
@click.option("--delay", type=float, default=0.5)
@click.option("--no-review", is_flag=True)
@click.option(
    "--full", is_flag=True,
    help="Full enrichment: fill Example/Comment/Collocations/Etymology for minimal cards",
)
def enrich(apkg_path: str, limit: int, model: str, delay: float, no_review: bool, full: bool):
    """Backfill Collocations/Etymology (default) or all fields (--full) for existing cards."""
    from .card_cache import CardCache, generate_card_cached

    console.print(f"Reading APKG: {apkg_path}...")
    notes = read_apkg_notes(apkg_path)

    if full:
        # Original mode: find cards with no Example AND no Comment
        candidates = [
            n for n in notes if not n.example.strip() and not n.comment.strip()
        ]
        mode_label = "minimal cards (no Example or Comment)"
    else:
        # Default: find cards missing any enrichable field
        candidates = [
            n for n in notes
            if not n.example.strip() or not n.comment.strip()
            or not n.collocations.strip() or not n.etymology.strip()
        ]
        mode_label = "cards with empty fields"

    console.print(f"  Found {len(candidates)} {mode_label}")

    if not candidates:
        console.print("[green]All cards already have content![/green]")
        return

    to_enrich = candidates[:limit]
    console.print(f"  Will enrich {len(to_enrich)} cards\n")

    cache = CardCache("card_cache.sq3")
    enriched_cards = []
    for i, note in enumerate(to_enrich, 1):
        word_clean = re.sub(r"<[^>]+>", "", note.back).strip()

        console.print(f"[bold]\u2500\u2500 [{i}/{len(to_enrich)}] {word_clean} \u2500\u2500[/bold]")

        try:
            card = generate_card_cached(word_clean, cache, model=model)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            continue

        if not no_review:
            _display_card_preview(card)
            if not click.confirm("Accept enrichment?"):
                continue

        if full:
            # Replace all generated fields unconditionally
            enriched_cards.append(
                {
                    "guid": note.guid,
                    "front": note.front,
                    "back": note.back,
                    "example": card.example,
                    "comment": card.comment,
                    "collocations": card.collocations_html,
                    "etymology": card.etymology_html,
                }
            )
        else:
            # Fill empty fields from generated data, keep existing content
            enriched_cards.append(
                {
                    "guid": note.guid,
                    "front": note.front,
                    "back": note.back,
                    "example": note.example if note.example.strip() else card.example,
                    "comment": note.comment if note.comment.strip() else card.comment,
                    "collocations": note.collocations if note.collocations.strip() else card.collocations_html,
                    "etymology": note.etymology if note.etymology.strip() else card.etymology_html,
                }
            )

        if i < len(to_enrich):
            time.sleep(delay)

    if enriched_cards:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_name = f"AZ_enriched_{timestamp}.apkg"
        output_path = create_supplement_apkg(
            enriched_cards,
            output_name,
            tags=["enriched", f"added::{datetime.now().strftime('%Y-%m')}"],
        )
        console.print(f"\n[bold green]Enrichment complete![/bold green]")
        console.print(f"  Cards enriched: {len(enriched_cards)}")
        console.print(f"  Import [cyan]{output_path}[/cyan] into Anki")
    else:
        console.print("\n[yellow]No cards were enriched.[/yellow]")


@cli.command()
@click.argument("words", nargs=-1, required=True)
@click.option("--apkg", type=click.Path(exists=True), default=DEFAULT_APKG,
              help="APKG to find existing cards in")
@click.option("--model", default=DEFAULT_MODEL)
@click.option("--no-review", is_flag=True, help="Skip interactive review")
def refresh(words: tuple, apkg: str, model: str, no_review: bool):
    """Regenerate all fields for existing cards by Greek word.

    Finds cards in the APKG whose Back field matches the given word(s),
    regenerates all fields via Claude API, and writes a supplement APKG
    (same GUIDs so Anki overwrites on import).

    \b
    Examples:
      python -m greek_anki refresh αίτηση
      python -m greek_anki refresh αίτηση πρόταση
      python -m greek_anki refresh αίτηση --apkg my_deck.apkg --no-review
    """
    from .card_cache import CardCache, generate_card_cached

    console.print(f"Reading APKG: {apkg}...")
    notes = read_apkg_notes(apkg)
    console.print(f"  {len(notes)} notes loaded")

    # Build lookup: normalized Back -> note
    back_lookup: dict[str, AnkiNote] = {}
    for note in notes:
        norm = normalize_greek(re.sub(r"<[^>]+>", "", note.back))
        back_lookup[norm] = note

    cache = CardCache("card_cache.sq3")
    refreshed_cards = []

    for i, word in enumerate(words, 1):
        console.print(
            f"\n[bold]\u2500\u2500 [{i}/{len(words)}] {word} \u2500\u2500[/bold]"
        )

        norm_word = normalize_greek(word)
        note = back_lookup.get(norm_word)
        if note is None:
            console.print(f"[red]Not found in deck, skipping.[/red]")
            continue

        word_clean = re.sub(r"<[^>]+>", "", note.back).strip()
        console.print(
            f"Found: [cyan]{word_clean}[/cyan] (guid={note.guid})"
        )

        card = None
        for _attempt in range(3):
            console.print(f"Generating card for [bold]{word_clean}[/bold]...")
            try:
                card = generate_card_cached(word_clean, cache, model=model, force=True)
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                continue

            if no_review:
                action = "accept"
            else:
                action = _interactive_review(card, word_clean)

            if action == "accept":
                break
            elif action == "regenerate":
                console.print("[dim]Regenerating...[/dim]")
                continue
            elif action == "skip":
                console.print("[yellow]Skipped.[/yellow]")
                card = None
                break
        else:
            console.print("[red]Max attempts reached, skipping.[/red]")
            card = None

        if card is None:
            continue

        nd = card.to_note_dict()
        refreshed_cards.append(
            {
                "guid": note.guid,
                "front": nd["front"],
                "back": note.back,  # preserve original Back field
                "example": nd["example"],
                "comment": nd["comment"],
                "collocations": nd["collocations"],
                "etymology": nd["etymology"],
            }
        )

    if not refreshed_cards:
        console.print("\n[yellow]No cards to write.[/yellow]")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_name = f"AZ_refresh_{timestamp}.apkg"
    output_path = create_supplement_apkg(
        refreshed_cards,
        output_name,
        tags=["refreshed", f"added::{datetime.now().strftime('%Y-%m')}"],
    )
    console.print(f"\n[bold green]Refresh complete![/bold green]")
    console.print(f"  Cards refreshed: {len(refreshed_cards)}")
    console.print(f"  Import [cyan]{output_path}[/cyan] into Anki")


# ======================================================================
# Shareable deck commands: build-deck, cache-status
# ======================================================================


@cli.command("build-deck")
@click.argument("freq_db", type=click.Path(exists=True))
@click.option("--range", "rank_range", nargs=2, type=int, required=True,
              help="Rank range (e.g. --range 1 1000)")
@click.option("--cache", "cache_path", type=click.Path(),
              default=DEFAULT_CARD_CACHE, help="Card cache database path")
@click.option("--deck-name", default=None,
              help="Custom deck name (default: 'Greek Top N')")
@click.option("--output", "-o", default=None, help="Output APKG filename")
@click.option("--generate-missing", is_flag=True,
              help="Generate missing cards via API (otherwise skip them)")
@click.option("--model", default=DEFAULT_MODEL)
@click.option("--delay", type=float, default=0.5, help="Delay between API calls (s)")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompts")
def build_deck(
    freq_db, rank_range, cache_path, deck_name, output, generate_missing,
    model, delay, yes
):
    """Build a shareable APKG deck from cached cards for a frequency range.

    Assembles cards from the card cache without API calls (unless
    --generate-missing is used). Use add-batch first to populate the cache.

    \b
    Examples:
      python -m greek_anki build-deck freq_list.sq3 --range 1 1000
      python -m greek_anki build-deck freq_list.sq3 --range 1 3000 --deck-name "Greek Top 3000"
      python -m greek_anki build-deck freq_list.sq3 --range 1001 3000 --generate-missing -y
    """
    from .anki_deck import deck_id_from_name
    from .card_cache import CardCache, generate_card_cached

    range_start, range_end = rank_range

    # Default deck name
    if deck_name is None:
        if range_start == 1:
            deck_name = f"Greek Top {range_end}"
        else:
            deck_name = f"Greek {range_start}-{range_end}"

    # Default output filename
    if output is None:
        if range_start == 1:
            output = f"Greek_top_{range_end}.apkg"
        else:
            output = f"Greek_{range_start}_{range_end}.apkg"

    console.print(f"[bold]Building deck:[/bold] {deck_name}")
    console.print(f"  Range: {range_start}-{range_end}")

    # Get all words in range (ignoring personal processed state)
    with FreqDB(freq_db) as db:
        all_words = db.get_range(range_start, range_end)

    if not all_words:
        console.print("[yellow]No words found in the specified range.[/yellow]")
        return

    console.print(f"  Words in range: {len(all_words)}")

    # Check cache coverage
    cached = []
    missing = []
    with CardCache(cache_path) as cache:
        for row in all_words:
            card = cache.get_card(row["greek"])
            if card is not None:
                cached.append((row, card))
            else:
                missing.append(row)

    console.print(
        f"  Cache coverage: {len(cached)}/{len(all_words)} "
        f"({len(cached) / len(all_words) * 100:.0f}%)"
    )

    if missing:
        console.print(f"  Missing: {len(missing)} words")

    # Generate missing cards if requested
    if missing and generate_missing:
        estimated_tokens = len(missing) * 800
        estimated_cost = estimated_tokens * 0.000015
        if not yes:
            console.print(f"\n[bold]Generation estimate for missing cards:[/bold]")
            console.print(f"  API calls needed: {len(missing)}")
            console.print(f"  Estimated cost:   ~${estimated_cost:.2f}")
            if not click.confirm("Generate missing cards?"):
                generate_missing = False

        if generate_missing:
            with CardCache(cache_path) as cache:
                for i, row in enumerate(missing, 1):
                    word = row["greek"]
                    console.print(
                        f"  Generating [{i}/{len(missing)}] {word}...",
                        end="",
                    )
                    try:
                        card = generate_card_cached(word, cache, model=model, force=True)
                        cached.append((row, card))
                        console.print(" [green]ok[/green]")
                    except Exception as e:
                        console.print(f" [red]error: {e}[/red]")

                    if i < len(missing):
                        time.sleep(delay)

            missing_count = len(all_words) - len(cached)
            if missing_count > 0:
                console.print(
                    f"  [yellow]{missing_count} words still missing after generation[/yellow]"
                )

    if not cached:
        console.print("[yellow]No cached cards available to build deck.[/yellow]")
        return

    # Sort by rank
    cached.sort(key=lambda x: x[0]["rank"])

    # Assemble APKG
    did = deck_id_from_name(deck_name)
    notes_data = []
    for row, card in cached:
        nd = card.to_note_dict()
        rank = row["rank"]
        rs = ((rank - 1) // 500) * 500 + 1
        notes_data.append(
            {
                "front": nd["front"],
                "back": nd["back"],
                "example": nd["example"],
                "comment": nd["comment"],
                "collocations": nd["collocations"],
                "etymology": nd["etymology"],
            }
        )

    tags = [
        "auto-generated",
        "source::build-deck",
        f"freq::{range_start}-{range_end}",
    ]

    output_path = create_supplement_apkg(
        notes_data, output, tags=tags, deck_name=deck_name, deck_id=did
    )

    console.print(f"\n[bold green]Deck built![/bold green]")
    console.print(f"  Deck name:  {deck_name}")
    console.print(f"  Cards:      {len(notes_data)}")
    console.print(f"  Output:     [cyan]{output_path}[/cyan]")


@cli.command("cache-status")
@click.option("--cache", "cache_path", type=click.Path(exists=True),
              default=DEFAULT_CARD_CACHE, help="Card cache database path")
@click.option("--freq-db", type=click.Path(exists=True), default=None,
              help="Frequency list DB (for range coverage)")
@click.option("--range", "rank_range", nargs=2, type=int, default=None,
              help="Rank range to check coverage for")
def cache_status(cache_path, freq_db, rank_range):
    """Show card cache statistics and coverage.

    \b
    Examples:
      python -m greek_anki cache-status
      python -m greek_anki cache-status --freq-db freq_list.sq3
      python -m greek_anki cache-status --freq-db freq_list.sq3 --range 1 5000
    """
    from .card_cache import CardCache

    with CardCache(cache_path) as cache:
        st = cache.stats()

    console.print(f"\n[bold]Card Cache:[/bold] {cache_path}")
    console.print(f"  Total cached cards: {st['total']:,}")
    if st["models"]:
        for m, cnt in st["models"].items():
            console.print(f"  Model: {m} ({cnt:,})")

    if freq_db:
        range_start = rank_range[0] if rank_range else 1
        range_end = rank_range[1] if rank_range else None

        with FreqDB(freq_db) as db:
            if range_end is None:
                conn = db._get_conn()
                range_end = conn.execute(
                    "SELECT MAX(rank) FROM freq_words"
                ).fetchone()[0] or 0

            console.print(f"\n[bold]Frequency coverage ({range_start}-{range_end}):[/bold]")

            table = Table(show_header=True)
            table.add_column("Range", style="cyan")
            table.add_column("Words", justify="right")
            table.add_column("Cached", justify="right")
            table.add_column("Coverage", justify="right")

            with CardCache(cache_path) as cache:
                for start in range(range_start, range_end + 1, 500):
                    end = min(start + 499, range_end)
                    words_in_range = db.get_range(start, end)
                    if not words_in_range:
                        continue
                    cached_count = sum(
                        1 for row in words_in_range
                        if cache.get(row["greek"]) is not None
                    )
                    total = len(words_in_range)
                    pct = (cached_count / total * 100) if total > 0 else 0
                    style = "green" if pct >= 80 else "yellow" if pct >= 50 else "red"
                    table.add_row(
                        f"[{start}-{end}]",
                        str(total),
                        str(cached_count),
                        f"[{style}]{pct:.0f}%[/{style}]",
                    )

            console.print(table)


@cli.command()
@click.argument("apkg_path", type=click.Path(exists=True))
@click.option("--output", "-o", default="cards.csv")
def export(apkg_path: str, output: str):
    """Export all APKG cards as CSV."""
    notes = read_apkg_notes(apkg_path)

    with open(output, "w", encoding="utf-8", newline="") as f:
        writer = csv_mod.writer(f)
        writer.writerow(["note_id", "front", "back", "example", "comment", "collocations", "etymology", "tags"])
        for n in notes:
            writer.writerow(
                [n.note_id, n.front, n.back, n.example, n.comment,
                 n.collocations, n.etymology, " ".join(n.tags)]
            )

    console.print(f"[green]Exported {len(notes)} notes to {output}[/green]")


@cli.command()
@click.argument("apkg_path", type=click.Path(exists=True))
@click.argument("tags", nargs=-1, required=True)
@click.option("--output", "-o", default=None,
              help="Output APKG path (default: overwrite input)")
@click.option("--deck-name", default=None, help="Custom deck name")
def tag(apkg_path: str, tags: tuple, output: str, deck_name: str):
    """Add tag(s) to all cards in an APKG file.

    Useful for watermarking decks before sharing.

    \b
    Examples:
      python -m greek_anki tag Greek_top_300.apkg my-watermark
      python -m greek_anki tag deck.apkg shared by-az -o deck_tagged.apkg
    """
    from .anki_deck import deck_id_from_name

    console.print(f"Reading APKG: {apkg_path}...")
    notes = read_apkg_notes(apkg_path)
    console.print(f"  {len(notes)} notes loaded")

    output_path = output or apkg_path
    d_name = deck_name or DECK_NAME
    d_id = deck_id_from_name(d_name) if deck_name else DECK_ID

    model = get_anki_model()
    deck = genanki.Deck(d_id, d_name)

    for note in notes:
        merged_tags = list(set(note.tags) | set(tags))
        n = genanki.Note(
            model=model,
            fields=[
                note.front, note.back, note.example,
                note.comment, note.collocations, note.etymology,
            ],
            tags=merged_tags,
            guid=note.guid,
        )
        deck.add_note(n)

    genanki.Package(deck).write_to_file(str(output_path))

    console.print(f"\n[bold green]Tagged {len(notes)} cards![/bold green]")
    console.print(f"  Added tags: {', '.join(tags)}")
    console.print(f"  Output: [cyan]{output_path}[/cyan]")
