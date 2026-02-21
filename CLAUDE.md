# Greek Anki CLI Tool

## Project Structure

```
greek-anki/
├── greek_anki/
│   ├── __init__.py          # Version
│   ├── __main__.py          # python -m greek_anki entrypoint
│   ├── cli.py               # Click CLI — all commands
│   ├── anki_deck.py         # APKG read (zstd+SQLite) and write (genanki)
│   ├── freq_list.py         # Frequency list SQLite management (FreqDB)
│   ├── claude_generator.py  # Claude API card generation
│   ├── card_cache.py        # Card cache (SQLite) — persists generated cards for reuse
│   ├── matcher.py           # Greek word normalization and fuzzy matching
│   └── config.py            # Constants: deck/model IDs, function words, templates
├── prompts/
│   └── card_prompt.txt      # Claude system prompt template ({word} placeholder)
├── pyproject.toml            # PEP 621 packaging
└── design.md                 # Full design spec
```

## Key Technical Details

- APKG files are ZIP archives; this deck uses `collection.anki21b` (zstd-compressed SQLite), not the plain `anki2` format
- `genanki` can only write new .apkg files — reading existing ones uses raw zstd decompression + sqlite3
- Fields in the SQLite `notes` table are delimited by `\x1f` (unit separator)
- The frequency CSV has Unicode issues: MICRO SIGN (U+00B5) and LATIN O (U+006F) mixed with Greek characters — `matcher.py` normalizes both
- 70+ normalized duplicates exist in the CSV; dedup happens during `import-freq`
- Deck ID: `1728801742169`, Model ID: `1722180007066`
- Fields (6 total): Front, Back, Example, Comment, Collocations, Etymology
- Comment contains conjugation + synonyms only; Collocations and Etymology are separate fields
- Card template: front shows `{{Back}}` (Greek), back reveals all fields

## Commands

```bash
# Run via: python -m greek_anki <command>
# Or if Scripts dir is on PATH: greek-anki <command>

# Phase 1 — no API key needed
import-freq CSV [--output DB]     # Import frequency CSV to SQLite
sync DB APKG                       # Mark freq words found in APKG as processed
status DB                          # Dashboard: coverage by range
pending DB [--range S E] [-n N]    # List unprocessed words
skip DB WORD... [--reason R]       # Mark words as skipped

# API key management
set-key                            # Store API key in OS credential store
clear-key                          # Remove stored API key

# Card generation — needs API key (keyring or ANTHROPIC_API_KEY env var)
preview WORD [--model M]           # Dry run card generation
add WORD... [--apkg APKG] [--freq-db DB] [--model M]  # Generate cards, review, write APKG
add-batch DB APKG -n COUNT [--range S E] [--delay D]  # Batch random pending words from frequency list
enrich APKG [-n N] [--model M]     # Backfill empty fields (default) or all fields (--full)
refresh WORD... [--apkg APKG]      # Regenerate all fields for existing cards (same GUID), updates cache
export APKG [-o FILE]              # Export all cards as CSV

# Shareable decks — generate once, assemble any combination
build-deck DB --range S E [--deck-name NAME] [-o FILE] [--generate-missing]  # Assemble APKG from cache
cache-status [--freq-db DB] [--range S E]  # Show cache coverage stats
```

## Environment

- Python 3.11+ (tested with 3.14)
- Install: `pip install -e .`
- API key: run `python -m greek_anki set-key` to store securely in Windows Credential Manager (preferred), or set `ANTHROPIC_API_KEY` env var as fallback
- Windows: set `PYTHONIOENCODING=utf-8` if unicode output breaks

## Typical Workflows

```powershell
# After a lesson — add new words (simplest form)
python -m greek_anki add αίτηση πρόταση κίνηση

# With duplicate check + frequency tracking
python -m greek_anki add αίτηση πρόταση κίνηση --apkg AZ_greek_words_new_fields.apkg --freq-db freq_list.sq3

# Skip interactive review (auto-accept all)
python -m greek_anki add αίτηση πρόταση --no-review

# Quick preview without writing anything
python -m greek_anki preview διπλός
```

Output is a timestamped `.apkg` file (e.g. `AZ_update_2026-02-15_182518.apkg`) — import it into Anki via File > Import.

### Building shareable decks for friends

Use `build-deck` (not `add-batch`) — it ignores word processing status and doesn't mutate the frequency DB.

```powershell
# Generate top-1000 deck in one command (API calls + cache + APKG)
python -m greek_anki build-deck freq_list.sq3 --range 1 1000 --generate-missing -y

# Build top-3000 (only 2000 new API calls, first 1000 already cached)
python -m greek_anki build-deck freq_list.sq3 --range 1 3000 --generate-missing -y

# Rebuild any range from cache (no API calls)
python -m greek_anki build-deck freq_list.sq3 --range 1 1000 --deck-name "Greek Top 1000"

# Check cache coverage
python -m greek_anki cache-status --freq-db freq_list.sq3 --range 1 5000
```

## Development Notes

- `freq_list.py` processed states: 0=pending, 1=in_anki, 2=skipped
- Matching uses Levenshtein distance ≤ 1 for accent variations
- Auto-skip: ~48 function words (articles, prepositions, conjunctions, pronouns, particles) are marked as skipped during import
- Supplementary APKG strategy: tool generates new `.apkg` files, user imports them into Anki (safe merge)
- Tags applied to new cards: `auto-generated`, `added::YYYY-MM`, `pos::TYPE`, `freq::START-END`
- `add` command: `--apkg` and `--freq-db` are optional; without them it skips duplicate check / frequency tracking
- `add-batch` command: classic personal workflow — picks random pending words, checks duplicates against APKG, marks processed; for fresh shareable decks use `build-deck --generate-missing` instead
- Card cache (`card_cache.sq3`): SQLite DB storing generated card JSON by normalized Greek word; avoids redundant API calls across `add`, `add-batch`, `build-deck`, and `enrich`
- `build-deck` reads all words in rank range regardless of processed state (excludes only auto-skipped function words); uses deterministic deck ID from deck name
- `enrich` command: finds cards with any empty field (Example/Comment/Collocations/Etymology), fills only empty fields from cache or API; uses `--no-review` for bulk runs; `--full` overwrites all generated fields; preserves GUID so Anki updates in place
- `refresh` command: finds existing card by Back field, regenerates all other fields via API (force, bypasses cache), updates cache with new data, preserves GUID so Anki overwrites on import
- API key stored via `keyring` in Windows Credential Manager (service: `greek-anki`, username: `anthropic-api-key`)
