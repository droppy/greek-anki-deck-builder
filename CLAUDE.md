# Anki Deck Generator Suite

Multi-tool project for generating Anki flashcard decks using Claude API. Each tool is a separate Python package with its own CLI, sharing the same repo and dependencies.

## Project Structure

```
greek-anki/
├── greek_anki/                      # Greek vocabulary deck generator
│   ├── __init__.py                  # Version
│   ├── __main__.py                  # python -m greek_anki entrypoint
│   ├── cli.py                       # Click CLI — all commands
│   ├── anki_deck.py                 # APKG read (zstd+SQLite) and write (genanki)
│   ├── freq_list.py                 # Frequency list SQLite management (FreqDB)
│   ├── claude_generator.py          # Claude API card generation
│   ├── card_cache.py                # Card cache (SQLite) — persists generated cards
│   ├── matcher.py                   # Greek word normalization and fuzzy matching
│   └── config.py                    # Constants: deck/model IDs, function words, templates
├── math_anki/                       # Kids math operations deck generator
│   ├── __init__.py                  # Version
│   ├── __main__.py                  # python -m math_anki entrypoint
│   ├── cli.py                       # Click CLI — all commands
│   ├── config.py                    # Fields, CSS, templates, level definitions
│   ├── problems.py                  # Deterministic problem generator (8 levels)
│   ├── generator.py                 # Claude API: batch hints, fun facts, ordering
│   ├── cache.py                     # SQLite cache (problem_key + age composite key)
│   └── deck_builder.py             # Assemble problems + hints into APKG
├── russian_abc/                     # Russian alphabet deck for English-speaking kids
│   ├── __init__.py                  # Version
│   ├── __main__.py                  # python -m russian_abc entrypoint
│   ├── cli.py                       # Click CLI — all commands
│   ├── config.py                    # Fields, CSS, card templates
│   ├── letters.py                   # 33 Russian letters with phonetic data
│   ├── generator.py                 # Claude API (mnemonics) + DALL-E (images)
│   ├── cache.py                     # SQLite cache (letter + age + gender key)
│   └── deck_builder.py             # Assemble APKG with embedded images
├── russian_dict/                     # Russian vocabulary deck for English-speaking kids
│   ├── __init__.py                  # Version
│   ├── __main__.py                  # python -m russian_dict entrypoint
│   ├── cli.py                       # Click CLI — all commands
│   ├── config.py                    # Fields, CSS, card templates
│   ├── vocabulary.py                # 149 basic + 246 conversational words by theme
│   ├── generator.py                 # Claude API (translations, examples, mnemonics, SVG)
│   ├── cache.py                     # SQLite cache (word + age + gender key)
│   └── deck_builder.py             # Assemble APKG with SVG→PNG images
├── english_anki/                     # C1+ English vocabulary for Russian speakers
│   ├── __init__.py
│   ├── __main__.py                  # python -m english_anki entrypoint
│   ├── cli.py                       # Click CLI — all commands
│   ├── config.py                    # Fields (6), CSS, bidirectional card templates
│   ├── wordlists.py                 # Built-in: AWL (360), phrasal verbs (132), idioms (107)
│   ├── word_db.py                   # SQLite: unified word DB (built-in + user-added)
│   ├── card_cache.py                # SQLite cache keyed by normalized English word
│   ├── generator.py                 # Claude API: definitions, examples, collocations, synonyms
│   ├── deck_builder.py             # Assemble bidirectional APKG
│   └── normalizer.py                # English word normalization
├── prompts/
│   ├── card_prompt.txt              # Greek card prompt template
│   ├── math/
│   │   ├── hint_prompt.txt          # Math hint/mnemonic prompt (age-tunable)
│   │   └── order_prompt.txt         # Pedagogical ordering prompt
│   ├── russian_abc/
│   │   ├── mnemonic_prompt.txt      # Letter mnemonic prompt (age/gender-tunable)
│   │   └── image_prompt.txt         # DALL-E image generation prompt template
│   ├── russian_dict/
│   │   └── word_prompt.txt          # Word card prompt (age/gender-tunable)
│   └── english/
│       └── card_prompt.txt          # C1+ English prompt (register, collocations, synonyms)
├── pyproject.toml                   # PEP 621 packaging (all entry points)
└── design.md                        # Greek deck design spec
```

## Shared Technical Details

- API key stored via `keyring` in Windows Credential Manager (service: `greek-anki`, username: `anthropic-api-key`) — shared by all tools
- All tools use the same `pyproject.toml` with separate entry points: `greek-anki`, `math-anki`, `russian-abc`, `russian-dict`, `english-anki`
- `genanki.Package(deck, media_files=[...])` supports embedding images/audio in APKG — media referenced in card HTML as `<img src="filename.png">`
- APKG media stored as indexed files (0, 1, 2...) with a JSON manifest mapping indices to filenames
- Claude API JSON extraction: Claude sometimes returns a single `{}` dict instead of a `[{}]` array, especially with small batches or opus models. All generators handle this with `if isinstance(results, dict): results = [results]` before validating. If adding a new generator, always include this fallback after `_extract_json()`.

## Greek Anki — Key Technical Details

- APKG files are ZIP archives; this deck uses `collection.anki21b` (zstd-compressed SQLite), not the plain `anki2` format
- `genanki` can only write new .apkg files — reading existing ones uses raw zstd decompression + sqlite3
- Fields in the SQLite `notes` table are delimited by `\x1f` (unit separator)
- The frequency CSV has Unicode issues: MICRO SIGN (U+00B5) and LATIN O (U+006F) mixed with Greek characters — `matcher.py` normalizes both
- 70+ normalized duplicates exist in the CSV; dedup happens during `import-freq`
- Deck ID: `1728801742169`, Model ID: `1722180007066`
- Fields (6 total): Front, Back, Example, Comment, Collocations, Etymology
- Comment contains conjugation + synonyms only; Collocations and Etymology are separate fields
- Card template: front shows `{{Back}}` (Greek), back reveals all fields

## Greek Anki Commands

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

---

## Math Anki — Kids Math Deck Generator

### Key Details

- Problems generated deterministically by `problems.py`; Claude API generates only hints, fun facts, and difficulty ratings
- 8 levels: L1 addition (100 cards), L2 subtraction (55), L3 mixed +/- (155), L4 multiplication (100), L5 division (81), L6 two-digit+ (90), L7 two-digit- (90), L8 mixed all (675)
- Cache keyed by `(problem_key, age)` composite — different ages get different hint styles
- Cards have 4 fields: Problem (colored by operation), Answer, Hint (emoji visual), FunFact
- Kid-friendly CSS: Comic Sans, gradient background, large fonts, operation-specific colors (+green, -red, ×blue, ÷orange)
- Hint prompt is age-tunable (5-10): silly/animals for young, puns/tricks for older
- Batch API calls: 20 problems per request for efficiency
- Card front has collapsible hint (`<details>` tag)

### Math Anki Commands

```bash
# Run via: python -m math_anki <command>
levels                                          # Show level descriptions + card counts
preview --level L [--count N] [--age AGE]       # Preview sample cards
generate --level L [--age AGE] [-y]             # Generate hints via Claude API
build-deck --level L... [--age AGE] [-o FILE]   # Assemble APKG from cached hints
cache-status [--level L] [--age AGE]            # Show cache coverage
set-key / clear-key                             # API key management
```

### Typical Math Workflow

```powershell
# Generate hints for levels 1-4, age 7
python -m math_anki generate -l 1 -l 2 -l 3 -l 4 --age 7 -y

# Build combined deck
python -m math_anki build-deck -l 1 -l 2 -l 3 -l 4 --age 7 --deck-name "Math for Alex" -o math_alex.apkg

# Or generate + build in one step
python -m math_anki build-deck -l 1 -l 2 --age 6 --generate-missing -y -o math.apkg
```

---

## Russian ABC — Alphabet Deck for English-Speaking Kids

### Key Details

- 33 Russian letters defined in `letters.py` with IPA, English approximations, example words, and phonetic notes
- Claude API generates age/gender-tuned mnemonics connecting Cyrillic letter shapes and sounds to English
- Claude generates inline SVG illustrations per letter by default (free, embedded directly in card HTML)
- Optional DALL-E upgrade: `generate-images` creates PNG illustrations (~$1.32 for all 33 letters)
- SVG visual is generated together with mnemonics in a single `generate` step (no extra API call)
- Cache keyed by `(letter, age, gender)` composite — different age/gender combos get different content
- Cards have 6 fields: Letter, Name, Sound, Mnemonic, ExampleWord, Visual
- Letter-type-specific card backgrounds: warm gradient for vowels, cool for consonants, neutral for signs
- "Tricky friends" concept for letters that look like English but sound different (В=V, Н=N, Р=R, С=S)
- OpenAI API key stored separately in keyring (service: `russian-abc`, username: `openai-api-key`)
- `openai` is an optional dependency: `pip install -e ".[images]"`

### Russian ABC Commands

```bash
# Run via: python -m russian_abc <command>
alphabet                                                    # Show all 33 letters
generate [--age AGE] [--gender boy|girl|neutral] [-y]       # Generate mnemonics via Claude
generate-images [--age AGE] [--gender G] [--image-dir DIR]  # Generate DALL-E images
build-deck [--age AGE] [--gender G] [-o FILE]               # Assemble APKG
preview [--age AGE] [--gender G] [--count N]                # Preview cards
cache-status [--age AGE] [--gender G]                       # Cache coverage
set-key / clear-key                                         # Anthropic API key
set-openai-key / clear-openai-key                           # OpenAI API key (for DALL-E)
```

### Typical Russian ABC Workflow

```powershell
# Generate mnemonics + SVG visuals for a 6-year-old boy (default, free)
python -m russian_abc generate --age 6 --gender boy -y

# Build deck (SVG visuals included automatically)
python -m russian_abc build-deck --age 6 --gender boy --deck-name "Russian ABC for Max" -o abc_max.apkg

# Or all-in-one
python -m russian_abc build-deck --age 6 --gender girl --generate-missing -y -o abc.apkg

# Optional: upgrade visuals to DALL-E images (~$1.32 for all 33 letters)
python -m russian_abc set-openai-key
python -m russian_abc generate-images --age 6 --gender boy -y
python -m russian_abc build-deck --age 6 --gender boy -o abc_dalle.apkg  # DALL-E images take priority over SVG
```

---

## Russian Dict — Vocabulary Deck for English-Speaking Kids

### Key Details

- 149 basic words + 246 conversational words = 395 total, organized by 20 themes
- Two deck levels: `basic` (starter ~150 words) and `conversational` (extends to ~395)
- Claude generates: kid-friendly translation with emoji, example sentence (RU+EN), sound mnemonic, SVG illustration
- Cards have 5 fields: Word, Translation, Example, Mnemonic, Visual
- SVG rendered to PNG via Playwright, same pipeline as russian_abc
- Cache keyed by `(word, age, gender)` — different ages/genders get different examples and mnemonics
- Themes: animals, food, family, colors, numbers, verbs, adjectives, body, home, nature, clothes, places, transport, time, emotions, school, phrases, pronouns, grammar, people

### Russian Dict Commands

```bash
# Run via: python -m russian_dict <command>
words [--level basic|conversational|all]           # Show vocabulary by theme
generate [--level L] [--age AGE] [--gender G] [-y] # Generate cards via Claude
build-deck [--level L] [--age AGE] [-o FILE]       # Build APKG with SVG→PNG
preview [--level L] [--theme T] [--count N]        # Preview cards
cache-status [--age AGE] [--gender G]              # Cache stats
set-key                                            # Anthropic API key
```

### Typical Workflow

```powershell
# Basic deck for a 6-year-old boy
python -m russian_dict build-deck --level basic --age 6 --gender boy --generate-missing -y -o russian_basic.apkg

# Full deck (basic + conversational)
python -m russian_dict build-deck --level all --age 8 --gender girl --generate-missing -y -o russian_full.apkg
```

---

## English Anki — C1+ Vocabulary for Russian Speakers

### Key Details

- Target audience: 40+ year old software engineers, native Russian speakers, aiming for C1+
- Built-in word lists: AWL (360), phrasal verbs (278), idioms (243), parenting (44), household (45), workplace (43), health (44), emotions (45), social (38), cultural (38), relationships (37), finance (40) = 1255 unique words
- User-added words via `add` command — stored alongside built-in lists in unified SQLite DB
- Bidirectional cards: Recognition (EN→RU) + Recall (RU→EN) = 2 cards per word
- Cards have 6 fields: Word, Definition (RU+EN), Example (3 sentences with register tags), Collocations, Synonyms (with nuanced distinctions in Russian), Register + usage notes
- Professional CSS: Georgia serif, monospace examples (familiar to engineers), dark mode support, register color-coded
- Recall card has blurred example hint (hover/tap to reveal) to avoid giving away the answer
- Claude prompt tuned for professional/technical context in examples
- Multi-language support via `--lang` flag: definitions/synonyms in native language (default: ru)
- Prompt templates at `prompts/english/card_prompt_{lang}.txt` — currently `ru` available
- To add a new language: create `card_prompt_{code}.txt` (e.g., `card_prompt_th.txt` for Thai)

### English Anki Commands

```bash
# Run via: python -m english_anki <command>

# Setup — import built-in word lists into database
import-lists [--category awl|phrasal|idiom|all]     # Load built-in lists (default: all)
  # --db DB          Word database path (default: english_words.sq3)

# Database info
status [--category C] [--db DB] [--cache-db DB]     # Dashboard: word counts by category + cache stats
pending [--category C] [-n N] [--db DB]              # List unprocessed words

# Hand-picked words — interactive add
add WORD... [--model M] [--lang LANG] [--no-review] [-o FILE]  # Generate, review, write APKG
  # --lang LANG      Native language for definitions (default: ru). Looks up card_prompt_{lang}.txt
  # --db DB          Word database path
  # --cache-db DB    Card cache path
  # Examples:
  #   python -m english_anki add ubiquitous eloquent albeit
  #   python -m english_anki add "break down" --lang th --no-review -o new_words.apkg

preview WORD [--model M] [--lang LANG]                # Dry run — show card, no caching

# Batch generation from lists
generate [--category C] [-n N] [--model M] [--lang LANG] [-y]  # Generate cards for pending words
  # --delay D        Delay between API batches (default: 1.0s)
  # --db DB          Word database path
  # --cache-db DB    Card cache path
  # Examples:
  #   python -m english_anki generate -c awl -n 50 -y
  #   python -m english_anki generate -c phrasal -y

skip WORD... [--reason R] [--db DB]                   # Mark words as skipped

# Deck building
build-deck [--category C] [--deck-name NAME] [--lang LANG] [-o FILE]  # Build APKG from cache
  # --generate-missing   Generate uncached words before building
  # --model M            Claude model (if generating)
  # -y                   Skip confirmation
  # --db DB              Word database path
  # --cache-db DB        Card cache path
  # Examples:
  #   python -m english_anki build-deck -o english_c1.apkg
  #   python -m english_anki build-deck -c awl --deck-name "Academic English" -o awl.apkg
  #   python -m english_anki build-deck -c phrasal --generate-missing -y -o phrasal.apkg

cache-status [--cache-db DB]                           # Show card cache stats

# API key management (shared with other tools)
set-key                                                # Store Anthropic API key
clear-key                                              # Remove stored key
```

### Typical English Anki Workflows

```powershell
# Initial setup — load all built-in lists
python -m english_anki import-lists

# Check what's available
python -m english_anki status

# Generate a batch of AWL cards
python -m english_anki generate -c awl -n 50 -y

# Build AWL deck
python -m english_anki build-deck -c awl -o awl.apkg

# Add a word you encountered in a podcast
python -m english_anki add "push the envelope" ubiquitous

# Build a deck from everything cached
python -m english_anki build-deck -o english_all.apkg

# Use a different model
python -m english_anki add albeit --model claude-opus-4-6 --no-review
```

---

## Greek Anki — Development Notes

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
