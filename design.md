# Greek Anki Deck Builder — Analysis & Design

## 1. APKG Structure Analysis

### Deck Overview
- **Total notes:** 3,073
- **Note type:** All use a single custom "Basic" model (ID: `1722180007066`)
- **Fields:** `Front` | `Back` | `Example` | `Comment`
- **Card template:** Reverse-style — front shows `{{Back}}` (Greek), answer reveals all 4 fields

### Field Semantics

| Field | Content | Population |
|-------|---------|------------|
| **Front** | Russian translation + English translation (65.5% bilingual, 34% RU-only) | 100% |
| **Back** | Greek word/phrase, often with article (ο/η/το ~28%) | 100% |
| **Example** | Greek sentences with Russian translations, HTML formatted (`<li>`, `<strong>`, `<em>`) | 59.3% (1,822 notes) |
| **Comment** | Etymology, verb conjugation, synonyms with usage distinctions, collocations | 30.8% (945 notes) |

### Content Patterns Observed

**For nouns** (Back field has article):
- Front: `место, пространство, помещение\n\nspace, area, place, room`
- Back: `ο χώρος`
- Example: 3-5 sentences with **bolded target word** in *italics*, each followed by Russian translation
- Comment: Synonyms with usage distinctions (`τόπος` vs `χώρος` vs `περιοχή`), register notes

**For verbs:**
- Front: `содержать, включать, охватывать\n\ncontain, include, comprise`
- Back: `περιέχω`
- Example: Same pattern as nouns
- Comment: **Conjugation triplet first** (`περιέχω - περιείχα - θα περιέχω`), then synonyms/collocations
- Common collocations noted separately

**For phrases/expressions:**
- Front: `давно, много лет назад\n\nlong ago, a long time ago`
- Back: `πριν πολύ καιρό`
- Comment: Grammar notes (e.g., "неизменяемая фраза"), simpler alternatives (`παλιά`, `στο παρελθόν`)

### HTML Formatting Convention
```html
<!-- Example field -->
<li><strong>Ο <em>χώρος</em> του σπιτιού είναι πολύ φωτεινός.</strong> Пространство дома очень светлое.</li>

<!-- Comment field - verb conjugation -->
<div>περιέχω - περιείχα - θα περιέχω</div>
<div><br></div>
<div><li><strong>περιλαμβάνω</strong>: почти синонимично с <strong>περιέχω</strong>...</li></div>
```

---

## 2. Proposed Card Data Structure

Based on your best-filled cards, here's the standardized structure for Claude API generation:

### Front Field (RU + EN translations)
```
<div>{Russian translations, comma-separated}</div>
<div><br></div>
<div>{English translations, comma-separated}</div>
```

### Back Field (Greek headword)
```
{article if noun} {Greek word/phrase}
```
- Nouns: include article (ο/η/το) — indicates gender
- Verbs: first person singular present (dictionary form)
- Adjectives: masculine singular
- Phrases: as-is

### Example Field (3-5 contextual sentences)
```html
<li><strong>{Greek sentence with <em>target word</em> in italics}.</strong> {Russian translation}.</li>
<!-- Repeat 3-5 times, progressing from simple to complex usage -->
```
Sentence selection criteria:
- Cover different meanings/contexts of the word
- Progress from A2→B1 difficulty
- Include at least one idiomatic or figurative usage if applicable
- Target word always **bold + italic**

### Comment Field (grammar + synonyms + etymology)
```html
<!-- For verbs: conjugation triplet first -->
<div>{present} - {past (αόριστος)} - {future (θα + ...)}</div>
<div><br></div>
<!-- For all: synonyms with usage distinctions -->
<li><strong>{synonym}</strong>: {how it differs from the headword, in Russian}</li>
<!-- Optional: etymology, collocations, register notes -->
```

---

## 3. CLI Application Design

### Architecture

```
greek-anki/
├── greek_anki/
│   ├── __init__.py
│   ├── cli.py              # Click-based CLI entry point
│   ├── anki_deck.py        # APKG read/write operations
│   ├── freq_list.py        # Frequency list management (SQLite)
│   ├── claude_generator.py # Claude API card generation
│   ├── matcher.py          # Greek word matching/normalization
│   └── config.py           # API keys, paths, prompt templates
├── prompts/
│   └── card_prompt.txt     # System prompt template for Claude
├── requirements.txt
└── README.md
```

### Data Flow

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Frequency   │───▶│   Matcher    │◀───│  APKG Deck  │
│  List (.sq3) │    │  (diff/filter)│    │  (existing) │
└─────────────┘    └──────┬───────┘    └─────────────┘
                          │ unprocessed words
                          ▼
                   ┌──────────────┐
                   │  Claude API  │
                   │  (generate)  │
                   └──────┬───────┘
                          │ structured card data
                          ▼
                   ┌──────────────┐    ┌─────────────┐
                   │  Review CSV  │───▶│  APKG Deck  │
                   │  (optional)  │    │  (updated)  │
                   └──────────────┘    └─────────────┘
```

### Frequency List: Source Data Analysis

**File:** `Greek_words_frequency_list.csv` — 21,192 words

| Column | Name | Usage |
|--------|------|-------|
| 1 | LEMMA | Greek word (dictionary form) ✅ **primary** |
| 2 | FREQUENCY | Raw occurrence count in corpus ✅ **used for ranking** |
| 3 | f/M | Frequency per million — **ignored** (derivable) |
| 4 | LOG F/M | Log frequency — **ignored** |
| 5 | (translation) | Rows 1-5000: English (decent), rows 5001+: Russian (Google Translate, unreliable) — **ignored**, Claude generates proper translations |
| 6 | (empty) | — |

**Notable:** 3 duplicate lemmas (μετανοώ, κλέβω, διακόσιοι). Rank is implicit from row position.

### Frequency List Storage (SQLite)

The app converts the CSV into a local SQLite DB on `import-freq`:

```sql
CREATE TABLE freq_words (
    rank        INTEGER PRIMARY KEY,  -- frequency rank (row position, 1 = most common)
    greek       TEXT NOT NULL,        -- lemma from CSV column 1
    frequency   INTEGER NOT NULL,     -- raw count from CSV column 2
    processed   INTEGER DEFAULT 0,    -- 0=pending, 1=in_anki, 2=skipped
    processed_at TEXT,                -- ISO timestamp when processed
    notes       TEXT                  -- optional: skip reason, manual notes
);
CREATE INDEX idx_greek ON freq_words(greek);
CREATE INDEX idx_processed ON freq_words(processed);
CREATE UNIQUE INDEX idx_greek_unique ON freq_words(greek);  -- dedup on import
```

**Import logic:**
1. Read CSV, skip header
2. For each row: rank = row_number, greek = col[0].strip(), frequency = int(col[1])
3. Skip empty lemmas (2 in file)
4. On duplicate lemma: keep the higher-ranked (lower rank number) entry
5. Ignore columns 3-6 entirely

### CLI Commands

```bash
# === SETUP ===
# Import frequency list from CSV (the Greek_words_frequency_list.csv)
# Uses col 1 (LEMMA) and col 2 (FREQUENCY), ignores the rest
greek-anki import-freq Greek_words_frequency_list.csv --output freq_list.sq3

# Sync: mark frequency words already in APKG as processed
greek-anki sync freq_list.sq3 AZ_greek_words.apkg

# === ADDING WORDS ===
# Add a specific word (checks it's not in APKG, generates via Claude, marks processed)
greek-anki add διπλός freq_list.sq3 AZ_greek_words.apkg

# Add N random unprocessed words from frequency rank range [2000, 2500]
greek-anki add-batch freq_list.sq3 AZ_greek_words.apkg \
    --range 2000 2500 --count 10

# Add N random unprocessed words (no range filter)
greek-anki add-batch freq_list.sq3 AZ_greek_words.apkg --count 5

# === REVIEW / MANAGE ===
# Show status of frequency list (coverage by range, processed/pending/skipped)
greek-anki status freq_list.sq3

# Preview what Claude would generate (dry run, no APKG write)
greek-anki preview διπλός

# Skip a word (mark processed without adding to Anki)
greek-anki skip freq_list.sq3 "ο" "η" "το" --reason "articles, too basic"

# List pending words in a range
greek-anki pending freq_list.sq3 --range 2000 2500

# === MAINTENANCE ===
# Re-generate Example/Comment for existing minimal cards in APKG
greek-anki enrich AZ_greek_words.apkg --limit 20

# Export all cards as CSV for review
greek-anki export AZ_greek_words.apkg --output cards.csv
```

### Word Matching Logic

Matching a frequency list word against existing Anki entries is non-trivial due to:
- Articles: `ο χώρος` in Anki vs `χώρος` in freq list
- Multiple forms: `κομπιούτερ, υπολογιστής` (two words in one card)
- HTML artifacts in Back field
- Phrases vs single words

**Matching algorithm:**
1. **Unicode normalization** (CRITICAL): The frequency CSV contains MICRO SIGN (U+00B5 `µ`) instead of GREEK SMALL LETTER MU (U+03BC `μ`) in many words (e.g., `χρησιµοποιώ`, `πρόβληµα`). Must normalize both sides before comparison.
2. Strip HTML tags from Back field
3. Remove articles (ο, η, το, οι, τα, τις, τους, την, τον)
4. Normalize whitespace, remove `&nbsp;`
5. Split on `,` and `/` for multi-word entries
6. Compare each normalized token against frequency word (case-insensitive)
7. Use Levenshtein distance ≤ 1 for accent variations

```python
def normalize_greek(text: str) -> str:
    """Normalize Greek text for matching."""
    text = text.replace('\u00b5', '\u03bc')  # MICRO SIGN → GREEK MU
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'<[^>]+>', '', text)       # strip HTML
    text = text.replace('&nbsp;', ' ')
    text = re.sub(r'^(ο|η|το|οι|τα|τις|τους|την|τον)\s+', '', text.strip())
    return text.lower().strip()
```

### Claude API Prompt Design

```
System: You are a Greek language expert creating Anki flashcard data.
Generate structured card content for the Greek word "{word}".

The learner speaks Russian (primary) and English.
Their Greek level is approximately B1.

Return a JSON object with these fields:
{
  "front_ru": "Russian translations (2-4 meanings)",
  "front_en": "English translations (2-4 meanings)",
  "back": "Greek headword with article if noun",
  "part_of_speech": "noun|verb|adjective|adverb|phrase|...",
  "examples": [
    {"greek": "...", "russian": "..."},  // 3-5 sentences
  ],
  "conjugation": "present - aorist - future" // verbs only, null otherwise
  "synonyms": [
    {"word": "...", "distinction": "...in Russian..."}
  ],
  "etymology_note": "..." // optional, if interesting
  "collocations": ["common phrase 1", "common phrase 2"]  // optional
}

Rules:
- In Greek sentences, wrap the target word with <em> tags
- Sentences should progress from simple (A2) to intermediate (B1)
- Include at least one idiomatic or figurative usage
- Synonym distinctions must explain WHEN to use each word
- For verbs: always include the conjugation triplet
- For nouns: always include the article
```

### APKG Write Strategy

**Approach: Generate a supplementary `.apkg` and import into Anki** (safest).

Why not modify the original `.apkg` directly:
- Anki uses internal schema tracking (mod counters, usn)
- Direct DB modification can corrupt sync state
- Import-merge is Anki's intended workflow

The tool will:
1. Read existing deck to extract model definition and deck ID
2. Use `genanki` to create new notes with the same model schema
3. Generate a new `.apkg` file (e.g., `AZ_update_2025-02-15.apkg`)
4. You import this in Anki → it merges into the existing deck

Alternatively, for power users: direct SQLite injection with proper ID generation (riskier but fully automated).

---

## 4. Quality of Life Features

### 4a. `enrich` — Backfill Existing Minimal Cards
You have 1,214 cards with no Example or Comment (40%). The `enrich` command feeds these through Claude to fill in missing fields, producing an update APKG.

### 4b. `status` Dashboard
```
Frequency List: 5000 words
  ✓ Processed (in Anki):  2,847
  ○ Pending:              2,043
  ✗ Skipped:                110

Range breakdown:
  [1-500]     498/500  (99.6%)
  [501-1000]  487/500  (97.4%)
  [1001-1500] 412/500  (82.4%)
  [1501-2000] 350/500  (70.0%)
  [2001-2500] 200/500  (40.0%)
  ...
```

### 4c. Interactive Review Before Commit
After Claude generates card data, show it in the terminal for approval:
```
── διπλός ──────────────────────────────
Front: двойной, удвоенный; двуличный
       double, dual; two-faced

Back:  διπλός, -ή, -ό

Example:
  1. Το δωμάτιο έχει διπλό κρεβάτι. — В номере двуспальная кровать.
  2. Πλήρωσε διπλή τιμή. — Он заплатил двойную цену.
  ...

Comment:
  Synonyms: διπλάσιος (specifically "twice as much")...

[A]ccept  [E]dit  [R]egenerate  [S]kip  >
```

### 4d. Batch Cost Estimation
Before running `add-batch --count 50`, show estimated API cost:
```
Estimated: 50 words × ~800 tokens/word = ~40K tokens
Cost: ~$0.12 (Haiku) / ~$0.60 (Sonnet)
Proceed? [y/N]
```

### 4e. `duplicates` — Find Near-Duplicate Cards
Detect cards that are too similar (e.g., `καρέκλα` and `η καρέκλα`, or `γράφω` and `εγγράφω`):
```bash
greek-anki duplicates AZ_greek_words.apkg
```

### 4f. Smart Word Selection for `add-batch`
Instead of pure random from range, weight selection by:
- Prefer words that have **related words already in the deck** (builds connections)
- Prefer **different parts of speech** in a batch (mix nouns, verbs, adjectives)
- Avoid words too similar to recently added ones

### 4g. Tags for Organization
Auto-tag new cards with:
- Frequency range: `freq::2000-2500`
- Part of speech: `pos::verb`, `pos::noun`
- Generation date: `added::2025-02`
- Source: `auto-generated`

### 4h. `export-pending` — Generate Study Candidates
Export pending frequency words as a simple list for manual review before batch processing:
```bash
greek-anki pending freq_list.sq3 --range 2000 2500 --format csv > candidates.csv
```

### 4i. Auto-Skip Function Words on Import
The frequency list top ranks are dominated by articles, prepositions, conjunctions, and pronouns (ο, και, να, εγώ, με, η, που, ...) that don't need Anki cards. The `import-freq` command auto-marks ~40 common function words as `skipped` with reason "function word".

### 4j. Current Coverage Snapshot
After `sync`, the status would look approximately like:

| Range | In Anki | Pending | Coverage |
|-------|---------|---------|----------|
| 1-500 | ~344 | ~100* | 68.8% |
| 501-1000 | ~401 | ~96 | 80.2% |
| 1001-1500 | ~383 | ~117 | 76.6% |
| 1501-2000 | ~315 | ~185 | 63.0% |
| 2001-2500 | ~173 | ~327 | 34.6% |
| 2501-3000 | ~128 | ~372 | 25.6% |

*\*Many "pending" in top 500 are function words that should be auto-skipped*

**Note:** Matching accuracy will improve once Unicode normalization (MICRO SIGN issue) is applied — some current "gaps" like `πράγµα`/`πράγμα` are false negatives.

---

## 5. Implementation Notes

### Dependencies
```
genanki          # APKG generation
anthropic        # Claude API
click            # CLI framework
rich             # Terminal formatting & tables
pandas           # CSV/data handling
python-Levenshtein  # Fuzzy matching
```

### Model Selection
- **Claude Haiku 4.5** for bulk generation (cheapest, fast, good enough for structured data)
- **Claude Sonnet 4.5** for `enrich` or when quality matters more
- Configurable via `--model` flag

### Rate Limiting
- Anthropic API: respect rate limits with exponential backoff
- For batch operations: configurable delay between calls (default 0.5s)
- Option to use Anthropic Batch API for 50% cost savings on large runs

### Frequency List Import
The CSV file (`Greek_words_frequency_list.csv`) is imported once via `import-freq`:
- Parses 21,192 entries, deduplicates 3 repeated lemmas (μετανοώ, κλέβω, διακόσιοι)
- Stores rank (row position), greek (LEMMA), frequency (raw count)
- Ignores unreliable translations — Claude generates proper RU+EN
- After import, run `sync` to cross-reference existing APKG words

---

## Appendix A: APKG Implementation Details

### Deck & Model IDs

```
Deck ID:     1728801742169
Deck Name:   "AZ greek words"
Notetype ID: 1722180007066
Notetype:    "Basic" (custom, 4 fields)
```

### Card Template

**Front of card** (question — shows Greek word):
```
{{Back}}
```

**Back of card** (answer — shows everything):
```html
{{FrontSide}}

<hr id=answer>

{{Front}}
<hr/>
{{Example}}
<hr/>
{{Comment}}
```

**CSS:**
```css
.card {
    font-family: arial;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
}
```

### genanki Model Definition

```python
import genanki

MODEL_ID = 1722180007066
DECK_ID  = 1728801742169

model = genanki.Model(
    MODEL_ID,
    'Basic',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
        {'name': 'Example'},
        {'name': 'Comment'},
    ],
    templates=[{
        'name': 'Card 1',
        'qfmt': '{{Back}}',
        'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Front}}\n<hr/>\n{{Example}}\n<hr/>\n{{Comment}}',
    }],
    css='.card {\n    font-family: arial;\n    font-size: 20px;\n    text-align: center;\n    color: black;\n    background-color: white;\n}',
)

deck = genanki.Deck(DECK_ID, 'AZ greek words')
```

### Reference Cards (HTML format targets for Claude generation)

#### Noun: ο χώρος

**Front:**
```html
<div>место, пространство, помещение, территория</div>
<div><br></div>
<div>space, area, place, room</div>
```

**Back:**
```html
<div>ο χώρος</div>
```

**Example:**
```html
<li><strong>Ο <em>χώρος</em> του σπιτιού είναι πολύ φωτεινός.</strong> Пространство дома очень светлое.</li>
<li><strong>Βρήκαμε έναν <em>χώρο</em> για να παρκάρουμε το αυτοκίνητο.</strong> Мы нашли место, чтобы припарковать машину.</li>
<li><strong>Ο <em>χώρος</em> της εκδήλωσης ήταν γεμάτος κόσμο.</strong> Помещение для мероприятия было полно людей.</li>
<li><strong>Χρειαζόμαστε περισσότερο <em>χώρο</em> για τα βιβλία μας.</strong> Нам нужно больше места для наших книг.</li>
```

**Comment:**
```html
<div><ul>
<li><strong>τόπος</strong> (ο): в отличие от <strong>χώρος</strong>, больше акцентирует конкретное расположение или географическую точку, а не пространство в целом.</li>
<li><strong>περιοχή</strong> (η): Более специфично и чаще относится к географическим или административным зонам.</li>
<li><strong>διάστημα</strong> (το): Означает "пространство" или "промежуток" в более абстрактном или научном контексте.</li>
</ul></div>
```

#### Verb: μεταμορφώνω

**Front:**
```html
<div>преображаю, трансформирую, изменяю</div>
<div><br></div>
<div>transform, metamorphose, change</div>
```

**Back:**
```
μεταμορφώνω
```

**Example:**
```html
<li><strong>Η Μαρία <em>μεταμορφώνει</em> το δωμάτιο με νέα διακόσμηση.</strong> — Мария преображает комнату новой декорацией.</li>
<li><strong>Η εμπειρία αυτή <em>μεταμόρφωσε</em> την άποψή του για τη ζωή.</strong> — Этот опыт изменил его взгляд на жизнь.</li>
<li><strong>Αν <em>μεταμορφώσεις</em> τον κήπο, θα γίνει υπέροχος.</strong> — Если ты преобразишь сад, он станет великолепным.</li>
<li><strong>Τα παιδιά <em>θα μεταμορφώσουν</em> το σπίτι σε πάρτι απόψε.</strong> — Дети сегодня вечером превратят дом в вечеринку.</li>
```

**Comment:**
```html
<div>μεταμορφώνω - μεταμόρφωσα - θα μεταμορφώσω</div>
<div><br></div>
<div>
<li><strong>Μεταμορφώνω εντελώς</strong> — «полностью преобразить», подчеркивает радикальное изменение.</li>
<li><strong>Μεταμορφώνομαι σε...</strong> — «превращаюсь в...», часто используется в шутливом или метафорическом смысле.</li>
</div>
```

### Frequency CSV Format

```
LEMMA,FREQUENCY,f/M,LOG F/M,,
ο,212923,157108.02,6.20,the,
και,51262,37824.34,5.58,and,
...
```

- 21,192 data rows + 1 header
- Column 0 (LEMMA) and Column 1 (FREQUENCY) are the only useful ones
- Column 4: English for rows 1-5000, Russian (Google Translate) for 5001+
- **Unicode issue:** Some lemmas use MICRO SIGN (U+00B5 `µ`) instead of GREEK MU (U+03BC `μ`)
- 3 duplicate lemmas: μετανοώ, κλέβω, διακόσιοι
- 2 empty rows

### Existing Deck Statistics

```
Total notes:              3,073
Using model 1722180007066: 3,073 (100%)
With Example field:        1,822 (59.3%)
With Comment field:          945 (30.8%)
With both Example+Comment:   908 (29.5%)
Minimal (no Example/Comment): 1,214 (39.5%) — candidates for enrichment
```

### Configuration: Use Claude Sonnet 4.5 for All Generation

Model: `claude-sonnet-4-5-20250514`  
Strategy: Generate separate `.apkg` files for import (not direct injection)
