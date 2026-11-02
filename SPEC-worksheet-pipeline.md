# Spec: worksheet-pipeline

Status: **draft for approval.** Parent: `SPEC.md`. Capability map:
`worksheet-pipeline`.
Depends on: `core-ids` (implemented, commit `2cb1c55`) and `dialect-model`
(implemented, commit `60f9335`). Date: 2026-11-02.

## 1. Objective

Give a dialect one canonical answer file that a speaker can fill, a machine can
validate, and a maintainer can export without hand-editing JSON.

After this module:

- `tools/lembar_kerja.py buat --kode koto-payang` writes one CSV row per
  catalogue ID, in tier order.
- A speaker answers the `answer` column, in CSV or in a generated DOCX.
- `periksa` normalizes answers and reports every problem by row and ID.
- `docx` and `baca` move a sheet between CSV and a reviewable Word table without
  losing answers or inventing approvals.
- `json` merges accepted answers into an existing dialect skeleton, and the
  result passes `load_dialect`.
- `core/ids.json` is read-only for this tool. No runtime output changes.

## 2. Scope

### In scope

- The canonical CSV schema and its location.
- `buat` (create) and `perbarui` (reconcile with a grown catalogue).
- Answer normalization for words and messages.
- `periksa` validation, readiness gate, and `--tulis`.
- A deterministic DOCX view and a reader for sheets this tool generated.
- A tier/completeness report.
- `json` export into an existing `dialects/<code>.json` skeleton.
- `tests/test_worksheet.py` and the tool's documentation.

### Out of scope

- The contents of `dialects/koto-payang.json` (that is `dialect-koto-payang`).
- `dialects/siulak.json` (that is `dialect-siulak-legacy`).
- Automatic ingestion of the existing `Translation Worksheet (Koto Payang).docx`.
  Review B4/B5 showed 287 rows for 137 IDs, no ID column, and 193 rows with no
  ID. Matching those rows automatically would invent answers. The Koto Payang
  module maps them by hand during the second speaker pass.
- Rows without a catalogue ID, and `core/future.json`. The 0.6 pipeline only
  writes IDs that already exist in `core/ids.json`.
- A web editor, a translation memory, and `krc terjemah`.
- Any change to `core/ids.json`, `dialects/loader.py`, or the runtime.

## 3. Canonical CSV

Location: `dialects/src/<code>.csv`. It sits under `dialects/`, so it is covered
by the CC BY-SA 4.0 scope in `SPEC.md` decision 7; it is working data and is not
in the wheel. Generated files are UTF-8 without a BOM, LF line endings, comma
separated, with a final newline.

Header, exactly and in this order:

```
id,tier,namespace,en,id_gloss,answer,notes,status
```

| Column | Written by | Rule |
|---|---|---|
| `id` | catalogue | Must exist in `core/ids.json`; unique |
| `tier` | catalogue | `1`, `2`, or `3`; must match the catalogue |
| `namespace` | catalogue | `kw`, `op`, `reserved`, `fn`, `type`, `mode`, or `msg` |
| `en` | catalogue | Neutral English text; must match the catalogue |
| `id_gloss` | catalogue | Indonesian template; must match the catalogue |
| `answer` | speaker | A word ID's identifier, or a message ID's template; may be empty |
| `notes` | speaker | Free text; may be empty; newlines allowed |
| `status` | speaker | `todo`, `draft`, `reviewed`, or `rejected` |

The catalogue columns are **read-only**. `id` identifies the row; `tier`,
`namespace`, `en`, and `id_gloss` must match `core/ids.json` exactly. `periksa`
reports a mismatch, and `perbarui` rewrites those four columns from the
catalogue. Never hand-edit them.

One row per catalogue ID (137 today), sorted by `tier` then `id`. A missing row,
an extra row, or a duplicate is an error. This is a catalogue inventory, not the
old Python-feature list: `elif`, `dict`, `class`, and the other rows without an
ID do not appear.

```csv
id,tier,namespace,en,id_gloss,answer,notes,status
kw.if,1,kw,if,Jika,kalu,Speaker A 2026-11-02,reviewed
kw.else,1,kw,else,Lainnya,nga_laen,normalized from "nga laen",draft
msg.value.div_zero,2,msg,Division by zero,Pembagian dengan nol,,,todo
```

CSV quoting follows Python's `csv` module (`excel` dialect). A cell may contain
commas, quotes, or newlines; the writer quotes it. A field beginning with `=`,
`+`, `-`, or `@` gets a warning (`csv-formula`) because spreadsheet programs may
treat it as a formula; the tool never evaluates it.

## 4. Answer states

| Status | Answer | Meaning |
|---|---|---|
| `todo` | empty | Not answered yet |
| `draft` | non-empty | A proposal, not speaker-approved |
| `reviewed` | non-empty | A speaker approved the normalized answer |
| `rejected` | non-empty | Kept for the record; never exported or shown as a proposal |

`buat` writes `todo`. `perbarui` keeps an existing status. The DOCX reader
downgrades a row to `draft` when its answer changes; it never sets `reviewed`.
Only a human edits `reviewed` in the CSV. `periksa` rejects an empty `draft`,
`reviewed`, or `rejected`, and an answer in a `todo` row.

`notes` records the speaker, date, and the raw answer when normalization changed
it. Notes never affect export except for provenance.

## 5. Commands

One tool, subcommands. All paths have defaults so the common command is short:

```bash
python3 tools/lembar_kerja.py buat    --kode koto-payang
python3 tools/lembar_kerja.py perbarui --kode koto-payang
python3 tools/lembar_kerja.py periksa --kode koto-payang --tulis
python3 tools/lembar_kerja.py periksa --kode koto-payang --siap
python3 tools/lembar_kerja.py docx    --kode koto-payang
python3 tools/lembar_kerja.py baca    --kode koto-payang --tulis
python3 tools/lembar_kerja.py laporan --kode koto-payang
python3 tools/lembar_kerja.py json    --kode koto-payang
```

| Flag | Default | Role |
|---|---|---|
| `--kode CODE` | required | Dialect code, matching `^[a-z0-9-]+$` |
| `--csv PATH` | `dialects/src/<code>.csv` | Canonical answers |
| `--docx PATH` | `dialects/src/<code>.docx` | Review view |
| `--json PATH` | `dialects/<code>.json` | Existing dialect skeleton and export target |
| `--paksa` | off | `buat`/`docx` may replace an existing file |
| `--tulis` | off | `periksa`/`baca` may write the CSV |
| `--siap` | off | Apply the readiness gate |

Exit codes: `0` success, `1` a validation or file problem, `2` bad usage
(missing `--kode`, unknown subcommand, unknown flag). A command that would write
uses a temporary file in the same directory and `os.replace`, so a failure never
leaves a half-written sheet.

### `buat`

Creates `dialects/src/<code>.csv` from the catalogue: one `todo` row per ID,
empty `answer` and `notes`, catalogue columns copied, sorted. Refuses if the CSV
exists unless `--paksa` (which discards answers; `perbarui` is the safe way to
add a new ID). `--docx PATH` also writes the review view.

### `perbarui`

Reads an existing CSV, checks that every row's ID still exists, rewrites the
four value columns from `core/ids.json`, adds a `todo` row for each new
catalogue ID, preserves `answer`, `notes`, and `status`, and writes the file
sorted. An ID that left the catalogue is an error: the tool never silently drops
a speaker's work.

### `periksa`

Runs every rule in section 6 and prints one line per problem:

```
row 12: kw.if: answer-choice: choose one alternative, not "kalu/lamun"
row 40: msg.value.div_zero: message-placeholder: expected {code}, found {kode}
checked 137 rows: 120 answered, 90 reviewed, 2 errors, 1 warning
```

`--tulis` writes the normalized CSV only when there are no errors. Warnings do
not block a write. `--siap` applies the readiness gate from section 9.

### `docx`

Renders the CSV as a Word table. It requires a structurally readable CSV (exact
header, unique known IDs) but does not require clean answers, so a speaker can
review a work in progress. Refuses to overwrite an existing DOCX unless
`--paksa`.

### `baca`

Reads a DOCX generated by `docx`, compares it with the current CSV, and updates
only `answer` and `notes` (section 7). Without `--tulis` it prints what would
change. The ID set in the DOCX must match the CSV exactly. A DOCX without an ID
column (including the old Koto Payang sheet) is rejected with `docx-format` and a
message that the old sheet has to be mapped by hand.

### `laporan`

Prints the completeness report from section 9 to stdout and exits 0; it never
writes. `periksa --siap` reuses the same readiness calculation.

### `json`

Merges the accepted answers into `dialects/<code>.json` (section 8). The file
must already exist and its `code` must match. The tool never writes metadata.

## 6. Normalization and validation

Normalization is deterministic and never guesses between alternatives.

### Words (`namespace != msg`)

1. Unicode NFC.
2. Strip leading and trailing whitespace.
3. Lowercase.
4. Collapse each run of internal whitespace to one `_`.
5. Remove one trailing `()` pair (`Nytak()` -> `nyetak`).
6. Leave every other character alone for validation.

The result must match `^[a-z][a-z0-9_]*$`, the loader's `WORD_RE`. A hyphen,
slash, comma, semicolon, pipe, period, or parenthesis that remains is an error,
not something the tool rewrites. A `/` or `,` in a word answer is specifically
`answer-choice`: the sheet offered alternatives and a person must choose. An
empty result is `answer-empty`.

### Messages (`namespace == msg`)

1. Unicode NFC.
2. Strip leading and trailing whitespace.
3. Otherwise preserve case, spaces, and punctuation.

The placeholder set must equal `core/ids.json`'s `placeholders` for that ID.
`{nama}` for `{name}` is `message-placeholder`, exactly as the dialect loader
would report it. Placeholders are never renamed by normalization.

### Full-set checks

`periksa` builds a synthetic draft dialect from the non-empty answers and calls
`validate_dialect` from `dialects/loader.py`, passing `filename=code`. That
reuses one source of truth for the clash matrix, word rules, placeholders, and
unknown IDs. Problems are mapped back to their CSV row by ID; a problem without a
row is `internal`. The synthetic data uses valid placeholder metadata, so
`periksa` never invents a reviewer or a review status.

The checker also reports:

| Code | Meaning |
|---|---|
| `csv-read` | The file cannot be decoded or parsed |
| `csv-header` | The header is missing, reordered, or has extra/missing columns |
| `csv-width` | A row has the wrong number of fields |
| `csv-formula` | A cell starts with `=`, `+`, `-`, or `@` (warning) |
| `csv-bom` | The file starts with a BOM |
| `unknown-id` | The ID is not in `core/ids.json` |
| `missing-id` | A catalogue ID has no row |
| `duplicate-id` | An ID appears twice |
| `catalogue-value` | A read-only column differs from the catalogue |
| `status` | An unknown status, or an answer/status combination from section 4 |
| `answer-empty` | A non-todo row has an empty answer |
| `answer-choice` | A word answer contains alternatives |
| `word-case`, `word-charset` | From the loader |
| `message-placeholder` | From the loader |
| `clash` | From the loader |
| `skeleton-missing` | `--siap` needs `dialects/<code>.json`, and it is absent |
| `write` | A file could not be read or replaced |

Every message is English and names the row, the ID, and the problem code. The
tool never prints a traceback for a bad file.

## 7. DOCX view

The DOCX is a derived view, never a second source of truth.

- Written with the standard library only (`zipfile`, `xml.etree.ElementTree`,
  no third-party package). No macros, no external links, no embedded objects.
- A4 landscape, 1.5 cm margins, one table with a header row that repeats on each
  page. Columns: `ID`, `Tier`, `English`, `Indonesian`, `Answer`, `Notes`.
- `ID`, `Tier`, `English`, and `Indonesian` cells are shaded light grey; a
  legend line above the table says grey columns come from the catalogue and must
  not be edited.
- The header row is bold. All text is XML-escaped. A newline in `notes` becomes
  `<w:br/>`.
- Deterministic output: fixed ZIP timestamps (1980-01-01) and a fixed entry
  order, so the same CSV produces byte-identical DOCX. Tests compare two writes.
- Caps: the CSV is at most 2 MiB, the DOCX at most 8 MiB uncompressed, at most 32
  ZIP entries. The reader opens only `word/document.xml`; it does not follow
  relationships or extract any other file.

The reader:

- Finds every table whose header row has `ID` in its first cell; maps columns by
  header text, so reordering the read-only columns is harmless.
- Requires the six headers above; a different header is `docx-format`.
- Ignores the read-only cells except to locate the row; the CSV's catalogue
  columns stay authoritative.
- Errors on a missing ID, an unknown ID, or a duplicate ID. An empty `Answer`
  clears the answer; a changed answer becomes `draft`; a changed note is kept
  without changing an approval; an unchanged row keeps its status. It never
  writes `reviewed`.
- Rejects a DOCX that contains a second table with a different header, so a
  pasted-in old sheet cannot be partly ingested.

## 8. Export to a dialect file

`json` reads the CSV and an existing `dialects/<code>.json` skeleton:

1. The skeleton must load (`load_dialect`), its `code` must equal `--kode`, and
   its `status` decides the readiness gate.
2. Accepted answers are rows with status `draft` or `reviewed`. `todo` and
   `rejected` are omitted.
3. `words` gets every accepted non-`msg` answer; `messages` gets every accepted
   `msg` answer. Keys are sorted; empty maps are written as `{}`.
4. The skeleton's metadata (`name`, `status`, `core`, `revision`, `parent`,
   `license`, `maintainer`, `reviewer`, `sources`, `orthography`) is copied
   unchanged. `revision` is not bumped automatically; the maintainer does that.
5. The merged data is validated with `validate_dialect` (including its parent
   chain) before writing. Any problem means nothing is written.
6. Write UTF-8, 2-space indent, sorted keys, final newline, atomically.

The default target is the skeleton path, so a successful export replaces the
skeleton's `words`/`messages`. `--json PATH` points elsewhere for tests. The
tool never creates a dialect file from nothing and never edits metadata.

## 9. Reports and readiness

`laporan` prints:

```
koto-payang: 137 ids
tier 1: 32/32 answered, 30 reviewed
tier 2: 90/104 answered, 40 reviewed
tier 3: 0/1 answered, 0 reviewed
missing tier 1: none
errors: 0, warnings: 1
ready for review: no (tier 1 has 2 unreviewed)
ready for approved: no (tier 2 has 64 unreviewed)
```

- `answered` counts non-empty answers; `reviewed` counts `reviewed` rows only.
- Missing tier 1 is listed by ID; other tiers are counted.
- Readiness for `review`: every tier-1 row is `reviewed`.
- Readiness for `approved`: every tier-1 and tier-2 row is `reviewed`.
- A `draft` target has no readiness requirement; `--siap` passes once structure
  and answers are valid.
- The report is deterministic English on stdout; errors and warnings from
  `periksa` are listed first, then the counts.

`periksa --siap` exits 1 when the target's status is `review` or `approved` and
the matching readiness rule fails, and 0 for `draft` when there are no errors.

## 10. Tests (`tests/test_worksheet.py`)

Fixtures use `tempfile.TemporaryDirectory()` and pass `--csv`, `--docx`, and
`--json` paths; no dialect or worksheet is committed by this module.

1. `buat` writes the exact header, one row per catalogue ID (137), tier/id order,
   and all `todo`.
2. `buat` refuses an existing CSV and `--paksa` replaces it.
3. `perbarui` restores a row deleted from the CSV as `todo` while an existing
   answer survives, refreshes a stale catalogue column, and errors on an unknown
   row instead of dropping it.
4. `periksa` accepts a minimal sheet and reports no errors.
5. Every structure/answer code in section 6 has a failing fixture:
   `csv-header`, `csv-width`, `csv-bom`, `unknown-id`, `missing-id`,
   `duplicate-id`, `catalogue-value`, `status`, `answer-empty`, `answer-choice`;
   `csv-formula` is a warning with exit 0.
6. Word normalization: `"  Kalu   Laen "` -> `kalu_laen`; `"Nytak()"` ->
   `nyetak`; `"ka-lu"` stays and fails `word-charset`; `"impor/masukka"` fails
   `answer-choice`; `"1kalu"` fails `word-charset`; `"BETUL"` -> `betul`.
7. Message normalization preserves spaces and case; a renamed placeholder fails
   `message-placeholder`; a valid message with every declared placeholder passes.
8. A clash (`kw.if` and `op.eq` sharing a word) is reported with both IDs named.
9. `periksa --tulis` writes normalized text only with no errors; it leaves the
   file untouched on an error.
10. `docx` writes a readable DOCX; writing twice is byte-identical; the ZIP has
    no extra entries.
11. `baca` round-trips unchanged answers, changes an answer to `draft`, clears an
    answer to `todo`, preserves a changed note without changing `reviewed`, and
    never invents `reviewed`.
12. `baca` rejects a DOCX with no ID column and one with a duplicate ID.
13. `json` merges `draft` and `reviewed` answers, omits `todo` and `rejected`,
    preserves metadata and `revision`, and the result passes `load_dialect`.
14. `json` writes nothing when validation fails.
15. `laporan` prints the tier counts, missing tier-1 IDs, and readiness.
16. `--siap`: a `draft` skeleton passes with unreviewed rows; a `review` skeleton
    fails with an unreviewed tier 1; an `approved` skeleton fails with an
    unreviewed tier 2.
17. Usage errors (no `--kode`, unknown subcommand, unknown flag) exit 2.
18. All existing suites stay green and unedited.

## 11. Boundaries

### Always

- Keep `core/ids.json` read-only for the worksheet.
- Write the CSV atomically and deterministically.
- Reuse `validate_dialect` for word, message, and clash rules.
- Require an ID for every row.
- Export only `draft`/`reviewed` answers.
- Keep DOCX generation dependency-free and macro-free.
- Name the row, the ID, and the problem code in every diagnostic.

### Ask first

- Adding a column or a status.
- Changing a normalization rule (especially whitespace, `()`, or case).
- Exporting `rejected` or `todo` answers.
- Reading the old Koto Payang DOCX automatically.
- Adding `core/future.json` or rows without IDs.
- Changing the readiness gate.

### Never

- Execute CSV or DOCX content.
- Modify `core/ids.json` or a dialect's metadata from the worksheet.
- Accept a changed placeholder.
- Let `baca` set `reviewed`.
- Silently drop an answer when the catalogue changes.
- Add a Python package dependency for DOCX.

## 12. Success criteria

1. `buat` produces 137 rows with the exact header and tier/id order.
2. A normalized CSV plus a skeleton becomes a loader-valid dialect file with no
   hand-editing.
3. `periksa` reports every section 6 code by row and ID and exits 0/1/2 as
   specified.
4. A DOCX round trip preserves answers and notes, is byte-identical on repeat
   generation, and never invents an approval.
5. `laporan` and `--siap` agree on tier totals and readiness.
6. Existing suites stay green and unchanged; `compileall`, `build.py`, and
   `dist/krc.pyz` still pass.

## 13. Decisions

D1. **CSV location.** `dialects/src/<code>.csv`, under the existing CC BY-SA
scope, not packaged in the wheel.

D2. **Eight columns.** `id,tier,namespace,en,id_gloss,answer,notes,status`;
catalogue columns are read-only mirrors.

D3. **Four statuses.** `todo`, `draft`, `reviewed`, `rejected`; only `draft` and
`reviewed` are exported.

D4. **Conservative normalization.** Words: NFC, trim, lowercase, whitespace to
`_`, one trailing `()` removed. Messages: NFC and trim only. Alternatives,
punctuation, and empty answers are errors for a human, never guesses.

D5. **One validator.** `periksa` builds a synthetic dialect and calls the
existing `validate_dialect`, so the worksheet cannot drift from the loader.

D6. **Dependency-free DOCX.** Standard-library writer and reader, fixed
columns, deterministic bytes, no macros or links; the reader accepts only sheets
this tool generated.

D7. **Export into a skeleton.** `json` fills `words`/`messages` of an existing
`dialects/<code>.json` and never touches metadata or `revision`.

D8. **Readiness is separate from validity.** `draft` needs only valid structure;
`review` needs every tier 1 reviewed; `approved` needs every tier 1 and tier 2
reviewed.

## 14. Next step

Approval of this spec, then `tasks/plan.md` and `tasks/todo.md`, then
implementation in the order: CSV + `buat`/`perbarui`, normalizer + `periksa`,
DOCX, `baca`, `json`, `laporan`, tests, docs.
