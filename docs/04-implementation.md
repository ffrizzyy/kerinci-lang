# 04. Implementation

## Repository layout

```
README.md                  front page (English)
GETTING-STARTED.md         step-by-step guide for a newly unzipped copy
kerincilang.py             the whole interpreter (one file, no dependencies)
core/ids.json              neutral ID catalogue: the language's contract (data)
dialects/                  dialect JSON files (data) + loader.py (validation only); dialects/src/ holds worksheet CSVs
pyproject.toml             packaging: provides the `krc` command
build.py                   runs every offline suite, then builds dist/krc.pyz
make_highlight.py          generates one union VS Code grammar from every dialect's resolved words
examples/                  example programs (.krc)
tutorial/                  13 lessons, answers, glossary in English; tutorial/id/ is the Indonesian copy; tutorial/{en,id}/koto-payang/ are generated Koto Payang trees (every code sample is tested)
tests/                     test_kerincilang.py (language), test_tutorial.py (baseline tutorial + glossary), test_tutorial_dialects.py (generated trees), test_ids.py (catalogue + seam + packaging), test_dialects.py (dialect files), test_runtime_selection.py (selection), test_worksheet.py (worksheet pipeline), test_migration.py, test_translator.py, test_docs_release.py (offline docs/release gate); test_release.py is the separate wheel smoke
tools/                     sinkron_tutorial.py, buat_glosarium.py, cek_dialek.py (dialect CI gate), lembar_kerja.py (worksheet pipeline and `rangka` scaffolds)
docs/                      design documents (this folder)
tasks/                     plan.md / todo.md for a working module
vscode-extension/          syntax highlighting for .krc files
.github/                   CI workflow and issue templates
```

The full source of the interpreter is `kerincilang.py` (read it top to bottom: the legacy vocabulary, lexer, parser, built-ins, interpreter, command line).

## Architecture

```
source (.krc)  ->  Lexer  ->  tokens  ->  Parser  ->  AST  ->  Interpreter  ->  output
                      ^                                              ^
                 Vocabulary (legacy Siulak today)  -------------  show()/messages
                      ^
                core/ids.json (neutral IDs)
```

| Stage | Responsibility | Where in `kerincilang.py` |
|---|---|---|
| Catalogue | Neutral IDs, namespaces, tiers, arities, placeholder names | `core/ids.json`, `CATALOG` |
| Vocabulary | Maps a neutral ID to one dialect's word and message | `Vocabulary`, `LegacySiulak` |
| Lexer | Text to tokens; token kinds are IDs (`kw.if`, `op.eq`); `mulai`/`habih` become `{`/`}` | `tokenize()` |
| Parser | Tokens to AST, recursive descent; compares IDs, never words | `class Parser` |
| Interpreter | Walks the AST; scopes via `Env`; built-ins live in a parent scope (`new_global()`); `balik`/`putuh`/`lanjut` via exceptions | `run()`, `ev()`, `Env` |
| Errors | One `LangError` type; text rendered from a `msg.*` template, with `msg_id` and `msg_args` kept | `LangError` |

### The vocabulary seam (0.6)

The engine has no dialect word in its logic. Each meaningful word has a stable
neutral ID; a `Vocabulary` supplies the surface words and the message templates.

```python
from kerincilang import LegacySiulak, run_source, show

v = LegacySiulak()
run_source('nyetak betul', vocab=v)      # M1: Siulak is the only real dialect
show(True, v)                            # -> "betul", not a hard-coded word
```

Rules:

- `core/ids.json` owns identity. Add the ID there before using it anywhere.
- `LegacySiulak` is the frozen Siulak 0.5 vocabulary; its output must match v0.5
  byte for byte. Since 0.6, `dialects/siulak.json` carries the same data for
  explicit selection, and `LegacySiulak` stays as the default and missing-file
  shim. `tests/test_kerincilang.py` and `tests/test_tutorial.py` are the oracle
  and are not edited to fit a refactor.
- Messages are catalogue entries. `id_gloss` is the Indonesian template, so
  `LangError.text` is exactly the v0.5 string; `en` is the neutral English base.
  Placeholders stay neutral (`{name}`, `{message}`) and are never translated.
- `KEYWORDS`, `SURFACE`, `WORD_OPERATORS`, `BUILTINS`, `TYPE_NAMES`, `MODES`, and
  `RESERVED` are compatibility views generated from `LegacySiulak`. Do not
  hand-maintain a second table.

**Selection is now per file (0.6).** Line 1 may declare `# dialek: <code>`;
without it the file uses `--dialek`, and with neither, Siulak. A call pushes the
callee's vocabulary for the body, and an import gives the imported file its own
vocabulary. See *Dialect selection* below.

## Dialect files (0.6)

A dialect is data, not code: `dialects/<code>.json`. `dialects/loader.py` reads,
validates, and resolves it. There is no Python file per dialect, and nothing in a
dialect is ever executed.

```json
{
  "code": "koto-payang",
  "name": "Koto Payang",
  "status": "draft",
  "core": "0.6",
  "revision": 1,
  "parent": null,
  "license": "CC BY-SA 4.0",
  "maintainer": "Nama Pengurus <email>",
  "reviewer": null,
  "sources": ["Translation Worksheet (Koto Payang), 2026"],
  "orthography": "Final -u (kalu, selamu); nga for and.",
  "words": {"kw.if": "kalu", "op.eq": "samo"},
  "messages": {"msg.value.div_zero": "Pembagian dengan nol"}
}
```

`words` and `messages` may be partial. One ID resolves in this order: this file,
then its `parent` chain, then the neutral English base. The base is synthesized
from `core/ids.json` (`greater than` -> `greater_than`), so there is no
`base.json` that could drift from the catalogue.

| Rule | Detail |
|---|---|
| Identity | `code` is `^[a-z0-9-]+$` and must match the filename |
| Base fallback | a word ID's base word is its `en` normalized to an identifier; a message's base template is its `en` |
| Inheritance | one `parent`, no cycles; `base` is the implicit terminal parent |
| Disjoint words | `kw`, `op`, `reserved`, `fn` may not share a word; `type` and `mode` may share with anything |
| Version | `core` is a minimum: a newer file warns (`newer-core`), an unknown ID is a hard error |
| Safety | 1 MiB cap, UTF-8 only, duplicate JSON keys rejected, no path outside `dialects/` |

```python
from dialects.loader import load_dialect
from kerincilang import run_source

d = load_dialect("koto-payang")
run_source('kalu 1 samo 1 { nyetak "samo" }', vocab=d.vocab)
d.report.tiers()      # {1: (own, 32), 2: (own, 104), 3: (own, 1)}
d.report.missing()    # [(id, tier)] still coming from the base
```

`present` in `tiers()` counts only the words and messages the file writes itself,
so a parent never inflates it. That is the number a speaker review cares about.

Validation codes are one per rule: `schema`, `code`, `core-version`, `word-empty`,
`word-charset`, `word-case`, `unknown-id`, `wrong-namespace`,
`message-placeholder`, `parent-missing`, `parent-cycle`, `reviewer-missing`,
`source-missing`, `clash`, `path`, `size`, `json`, plus `missing` for a file that
does not exist. `validate_dialect` returns every problem and never prints;
`load_dialect` raises `DialectError` with all of them in `.problems`.

`python3 tools/cek_dialek.py --semua` is the CI gate. Exit 0 is clean, exit 1 is a
validation error, exit 2 is a strict failure (`--ketat`: an approved dialect still
falling back to the base for a Tier 1 word, or a newer `core`). The checker reads
JSON only; it never imports a dialect.

The default root works from a checkout, a wheel, and `dist/krc.pyz`, because it
uses `importlib.resources.files("dialects")` instead of a source path.
`tests/test_dialects.py` builds a zipapp containing a dialect and loads it from a
directory with no checkout.

### The Siulak freeze

`dialects/siulak.json` is the first committed dialect. It is the complete v0.5
vocabulary: 69 words and 68 messages, all 137 IDs owned by the file, so no
English fallback is used. It stays `draft`, revision 1, reviewer null: a freeze,
not a 0.6 re-review. `dialects/siulak.md` records provenance and the word table,
while `docs/02-vocabulary-worksheet.md` remains the decision log.
`tests/test_siulak_legacy.py` locks every word and message to `LEGACY_WORDS`,
`LEGACY_OPERATORS`, and `id_gloss`, and proves `DialectVocabulary` and
`LegacySiulak` format every message identically. A bare `run_source()` still
defaults to `LegacySiulak`, and a missing `siulak.json` still resolves to it.

### The Koto Payang review

`dialects/koto-payang.json` is the first non-Siulak dialect, at `status: review`.
It is hand-mapped from the old worksheet, never ingested: the DOCX has no ID
column and 287 rows for 137 IDs. The canonical answer file is
`dialects/src/koto-payang.csv`; `dialects/koto-payang.md` records provenance,
orthography, the mapping decisions, and the review record.

The file owns 89 IDs (63 words + 26 messages) and falls back to the English base
for 48 (`{1: (32, 32), 2: (57, 104), 3: (0, 1)}`). All 32 Tier 1 IDs are
reviewed, so `--ketat` and `cek_dialek --ketat` still exit 0; the gaps are Tier 2
and warn once per `(dialect, id)`. Four rows are provisional `draft`s
(`type.float`, `type.null`, `msg.name.constant`, `msg.value.convert`) and 48
are `todo`. Those rows are recorded as open worksheet work and nothing is
guessed to close a gap; the file stays at `review` until a speaker supplies
them.

`tests/test_koto_payang.py` pins the exact word and message maps, the CSV status
counts, `periksa --siap` readiness (review yes, approved no), header and
`--dialek` selection, a clean run with no warning, the `type.bool` fallback
warning, and the `cek_dialek` summaries.

### Dialect-templated tutorial

The tested Siulak lessons are the single written source; there is no second
prose copy. `tools/sinkron_tutorial.py --bangun koto-payang` maps code fences
and inline code spans by neutral ID, adds `# dialek: koto-payang`, runs every
block, and writes `tutorial/en/koto-payang/` and
`tutorial/id/koto-payang/`. `--semua-dialek` does the same for every dialect
whose status is `review` or `approved`. The generated trees are committed; the
baseline lesson code is not touched, and `tests/test_tutorial.py` still checks
exactly 550 baseline blocks.

A `krc-berkas` helper ending in `.krc` is code: it is word-mapped and gets the
header. Any other helper is raw data and keeps its bytes, so `nilai.txt` in
lesson 13 is not corrupted. The generator reuses `rewrite_dialect_words` from
`kerincilang.py`, the same scanner as `krc terjemah`.

A target that lacks a word may use the English base fallback. Koto Payang's
tutorial uses two: `fn.contains` (`contains`) and `type.bool` (`boolean`). The
build lists them in both indexes and warns once per ID on stderr; it never
invents a word. Inline spans and the `Kind` / `Jenis` table columns have their
own mapping rules, recorded in `SPEC-tutorial-multidialect.md`.

`tests/test_tutorial_dialects.py` builds into temporary repo copies and checks
determinism, the committed trees, the untouched baseline, the Siulak
self-build, every generated block, helper headers, normalized output and error
identity against Siulak, fallbacks, links/index/glossary, prose fidelity, usage
errors, and that a failed build leaves the destination alone.

### `krc migrasi`

`main()` dispatches `migrasi` before the normal run path. `_migrasi_visit()`
reads a file as bytes, refuses a BOM, checks line 1 with the runtime header
rules, parses the file with its effective dialect (`tokenize` + `Parser`, never
`run_source`), walks the AST for literal `ambik` imports, and only then writes
`# dialek: CODE` before the original bytes. The write goes through a temporary
file and `os.replace()`, so a failure leaves the original untouched. The visited
set is keyed by `realpath` + `normcase`, so a shared import is processed once.

Migration follows literal imports only. A computed import is reported as
`cannot follow` and exits 1; it is never executed or guessed. A missing import,
a parse error, a malformed header, an unknown header dialect, and a BOM are
per-file errors: that file is not modified, and other files continue. A file
that already has a valid header is parsed for imports but never rewritten.

The default code is `siulak`; `--dialek` changes it, `--semua` walks a directory,
and `--kering` writes nothing. The command is toolchain output (English) and
does not use the message catalogue. The normal CLI keeps the
`runtime-selection` precedence: header > `--dialek` > Siulak; `-c` and the REPL
default to Siulak.

## Dialect worksheets

`dialects/src/<code>.csv` is the canonical answer file for a new dialect. It is
working data under the same CC BY-SA 4.0 scope as `dialects/`, and it is not in
the wheel. `tools/lembar_kerja.py` owns the cycle; `core/ids.json` stays
read-only.

```bash
python3 tools/lembar_kerja.py buat     --kode koto-payang
python3 tools/lembar_kerja.py rangka   --kode koto-payang --nama "Koto Payang"
python3 tools/lembar_kerja.py periksa  --kode koto-payang --tulis
python3 tools/lembar_kerja.py docx     --kode koto-payang
python3 tools/lembar_kerja.py baca     --kode koto-payang --tulis
python3 tools/lembar_kerja.py laporan  --kode koto-payang
python3 tools/lembar_kerja.py json     --kode koto-payang
```

The eight columns are `id,tier,namespace,en,id_gloss,answer,notes,status`. The
first five mirror `core/ids.json` and are read-only; `periksa` reports a mismatch
and `perbarui` rewrites them. A word answer is normalized with NFC, trim,
lowercase, whitespace to `_`, and one trailing `()` removed; a message answer is
NFC and trim only, and its placeholders must match the catalogue. Alternatives
(`/` or `,`) and remaining punctuation are errors for a human, never guesses.

`periksa` builds a synthetic draft dialect and calls `validate_dialect`, so word,
message, and clash rules have one source of truth. It reports every problem by
row and ID; `--tulis` writes the normalized CSV only when there are no errors.
`--siap` reads the target skeleton's status: `draft` needs valid structure,
`review` needs every Tier 1 row `reviewed` and at least one source, and
`approved` needs Tier 1 and Tier 2 reviewed plus a named reviewer.

`docx` renders a dependency-free A4 landscape table; the same CSV produces
byte-identical bytes. `baca` changes only `answer` and `notes`, downgrades a
changed answer to `draft`, clears an empty answer to `todo`, and never invents
`reviewed`. `json` merges only `draft`/`reviewed` rows into an existing
`dialects/<code>.json`, preserves all metadata and `revision`, validates the
result, and writes nothing if it would not load.

The old `Translation Worksheet (Koto Payang).docx` is not ingested: it has no ID
column and 287 rows for 137 IDs. `dialect-koto-payang` maps it by hand into
`dialects/src/koto-payang.csv`.

## Adding a dialect

The primary guide is [`09-adding-a-dialect.md`](09-adding-a-dialect.md). It is
written for a contributor who does not read Python, and every command it names
is exercised by `tests/test_docs_release.py`.

The short version: `lembar_kerja.py buat` creates the worksheet,
`lembar_kerja.py rangka` creates a validated `draft` JSON skeleton and notes
stub, and `lembar_kerja.py json` merges accepted rows into the JSON. Then
`cek_dialek.py` validates the file, `sinkron_tutorial.py --bangun <code>`
generates the tutorial tree, and `make_highlight.py` regenerates the union
grammar. No Python change is needed, and no dialect may borrow another
dialect's word to fill a gap. The status gates and the review record are in the
guide, not in this file.

## Dialect selection

One `RunContext` per invocation holds the default vocabulary, the dialect cache,
the warned set, and the `--ketat` flag. It is pushed by `main`/`run_file` and
restored afterwards; a bare `run_source()` creates a one-shot context so the
public API keeps working.

Precedence:

```
line 1 `# dialek: <code>`   >   --dialek   >   Siulak
```

- The header is line 1 only. Any later `# dialek:` line is an ordinary comment.
  A line 1 that starts with `#` and contains `dialek` but does not match
  `^\s*#\s*dialek\s*:\s*([a-z0-9-]+)\s*$` is an error (`msg.dialect.header`),
  never a silent comment.
- `--dialek` is the default for files that declare nothing, including the REPL
  and `-c`.
- A headerless import uses the run default, not the importer's dialect. A file's
  dialect is a property of the file, so `LOADED` stays keyed by path.
- A call pushes the vocabulary of the function's defining module; nested calls
  restore correctly, even when the callee raises. Output, `mecem`, file modes,
  and error text therefore follow the executing module.
- A header naming a missing file is `msg.dialect.unknown`; one naming a file that
  fails validation is `msg.dialect.invalid`. Both are program errors (exit 1).

`--ketat` checks the selected dialect before the program starts, and any dialect
loaded later from an import. An approved dialect with a Tier 1 base fallback
exits 2; a program that was already running finishes first.

A base fallback prints one English line to stderr per `(dialect, id)` per run,
for example `warning: dialect koto-payang: kw.in falls back to the base word
"in"`. Registering every built-in is silent; only a real use warns. Warnings
never change the exit code.

```krc
# dialek: koto-payang
kalu 1 samo 1 { nyetak "samo" }
```

## Running

```bash
krc contoh.krc                    # after `pip install .`
python3 krc.pyz contoh.krc        # single-file build
python3 kerincilang.py contoh.krc # from source
python3 tests/test_kerincilang.py   # the language
python3 tests/test_tutorial.py      # every baseline tutorial sample + glossary coverage
python3 tests/test_tutorial_dialects.py  # generated Koto Payang trees + equivalence
python3 tests/test_ids.py           # catalogue, vocabulary seam, packaging
python3 tests/test_dialects.py      # dialect files, inheritance, the CLI
python3 tests/test_runtime_selection.py  # header, precedence, imports, --ketat
python3 tools/cek_dialek.py --semua # dialect CI gate (exit 0 / 1 / 2)
```

Python 3.9 or newer (3.11 or newer recommended: it allows function calls to nest 400 deep instead of 80); no packages needed.

## Command line

| Command | What it does | Exit code |
|---|---|---|
| `krc` | REPL; keeps reading while `{`, `(`, `[` (or `mulai`) are still open | 0 |
| `krc file.krc` | Runs the program | 0, or 1 on a program error |
| `krc -c "code"` | Runs one piece of code | 0 / 1 |
| `krc --dialek CODE ...` | Default dialect for files without a `# dialek:` header | 0 / 1 / 2 |
| `krc --ketat ...` | Fails (exit 2) when an approved dialect still takes Tier 1 words from the base | 0 / 1 / 2 |
| `krc --version`, `krc --help` | Information | 0 |
| missing file or bad encoding | Message in Indonesian | 2 |
| bad `--dialek` (missing value, unknown code, invalid file) | Message before the program starts | 2 |

Closed pipes (`krc program.krc | head`) and Ctrl+C are handled without a traceback. `tanyo()` returns an empty text when input ends.

## Packaging and building

| File | Role |
|---|---|
| `pyproject.toml` | Declares the package and the `krc` command (`krc = kerincilang:main`), and ships `core/` + `dialects/` as package data |
| `build.py` | Runs the test suite, then builds `dist/krc.pyz` (a Python zipapp) and copies the examples into `dist/` |

The zipapp and the wheel must contain `core/ids.json`, because the engine loads it at import time. `build.py` copies `core/` and `dialects/` into the archive; `pyproject.toml` declares them under `packages` and `package-data`. `tests/test_ids.py` builds a zipapp in a temporary folder and runs it from a directory with no checkout, so a missing data file fails CI instead of a release.

To release a new version, follow [`RELEASING.md`](../RELEASING.md): change
`__version__` in `kerincilang.py`, `version` in `pyproject.toml`, the extension
version, the changelog, and the install guide, then run the offline suite and
the wheel smoke. To publish on PyPI later, run `python3 -m build` and
`twine upload dist/*` (needs an account and the `build` and `twine` packages).

## How it works

**Lexer.** One regular expression with named groups. Identifiers use `[^\W\d]\w*`, so any Unicode letter works and words like `kurang_daripado` are single tokens. An identifier in the active vocabulary's operator map becomes the matching symbol token, one in its surface map becomes a neutral keyword token (`kw.if`), and one in its reserved set (`kelihu`) is rejected. The token *text* for a keyword is its ID, never the dialect word, so the parser cannot depend on a dialect.

**Parser.** Each precedence level calls the next-higher one (`expression` -> `and_` -> `equality` -> ... -> `call` -> `primary`), which is why `1 + 2 * 3` is 7. `lain kalu` is just `lain` followed by another `kalu` statement, so any chain length works. Comparison words and symbols both arrive as the neutral symbol (`==`, `<`), so one code path serves each. The parser tracks loop depth so `putuh`/`lanjut` outside `selamo` are caught before the program runs. When an error names a token, `Parser.display()` turns the ID back into the active dialect's word, which is the only place the parser asks for a word.

**Lists and `untuk`.** `[ ... ]` is parsed in `primary()`, and indexing `xs[i]` is handled in the same loop as function calls, so `m[1][0]` and `f(x)[2]` work. `xs[i] = v` is recognised after parsing an expression: if the left side is an index, it becomes a `setindex` statement. `untuk <name> alem <source>` evaluates its source once, turns it into a sequence (`iterate()`, lists and text only), and runs the body in a fresh scope per item. Counting loops use `jarak(n)`, which builds a list (capped at `MAX_JARAK`).

**Maps.** A `peta` is a Python dict. The literal `{ key: value, ... }` is parsed in `primary()` (a `{` at the start of an expression is a map; after a condition it is a block, because blocks are only parsed where a statement list is expected). Keys are limited to text and whole numbers by `check_key`. Indexing goes through `get_item` and assignment through the `setindex` branch, so lists, text and maps share the `xs[i]` syntax.

**`pilih`.** Parsed as a statement with a list of (values, block) clauses and an optional default. At run time the subject is evaluated once and compared with `binary_op("==", ...)`; the first matching clause runs and the rest are skipped.

**Imports.** `ambik` evaluates to a file name, resolves it against `IMPORT_STACK` (the directory of the file currently running), and runs the file once in its own scope (`LOADED` caches it; `LOADING` catches cycles). The module's top-level names are then copied into the importing scope. Functions keep the closure of their own module, so private helpers still work. `run_file()` sets up the import directory for the main program.

**Files.** `bukak` returns a `Berkas` object (path, mode, Python file handle, closed flag), and every open one is tracked in `OPEN_FILES` so `run_file()` and `main()` can close them when the program ends. The mode is written in the dialect's words (`"baco"`, `"tulis"`, `"nambahkah"` in Siulak) but stored as a neutral `mode.*` ID and mapped to Python's `r`, `w`, `a` in `FILE_MODE_CHARS`, so changing dialect cannot break an open handle. All Python `OSError`s are turned into `LangError`s by `file_error()`, so `kelihu` can catch them. Lines come from iterating the handle (`untuk b alem f`), through the same `iterate()` used for lists and maps.

**Errors (`cubo`, `tangkap`, `ngangkat`).** The parser reads `cubo <block> tangkap [name] <block>` into a `try` node and `ngangkat <expression>` into a `raise` node. At run time the first block runs in its own scope, and a `LangError` (or `RecursionError`) sends control to the handler with the message bound to the name. Internal errors are built with `msg("msg.area.name", ...)`: `LangError` renders the active dialect's template at construction, so `str(err)` is stable and `err.msg_id` / `err.msg_args` stay available. `ngangkat` simply raises a `LangError` with the user's text, so there is only one kind of error in the interpreter. Control-flow signals (`balik`, `putuh`, `lanjut`) are Python exceptions of other types, so they pass through untouched. `kelihu` is `reserved.error`, so using it as a name is rejected by the lexer.

**Text functions.** `pisah` and `disatu` are ordinary built-ins that wrap Python's `str.split` and `str.join` (with `pisah(text)` splitting on whitespace and an empty separator splitting into letters).

**Recursion.** Each language-level call adds several Python frames. `CALL_DEPTH` counts nested calls and raises a normal error beyond `MAX_CALL_DEPTH` (400 on Python 3.11+, where the recursion limit is raised to 12000; 80 on older versions). A stray `RecursionError` is converted into the same error, so runaway recursion can never crash the interpreter.

**Text escapes.** The lexer's `STRING` pattern allows backslash pairs, and `unescape()` converts `\n`, `\t`, `\"` and `\\` when the literal is parsed; anything else is an error with a line number.

**Conversions.** `bilangan` and `pecahan` accept numbers and ASCII number text only (a regular expression, so Unicode digits and `1_000` are rejected). `mecem` asks the active vocabulary for the `type.*` words, so the boolean name is the marked placeholder `boolean` in Siulak until speakers supply one.

**Built-ins.** `BUILTIN_IDS` maps a neutral `fn.*` ID to (argument count, Python function), and `new_global()` registers each one under `vocab.word(fn_id)` in a parent scope of the program's global scope, so user code can redefine any of them without touching the originals. To add one, write a Python function, add an ID to `core/ids.json`, map it in `LegacySiulak`, add a line to `BUILTIN_IDS`, and add tests. Functions that change their argument (`nambahkah`) return `None`; the others return new values.

**Interpreter.** `Env` objects chain to their parent for lexical scope, and a function value stores the `Env` it was defined in, which is what makes closures work. `tetap` names are recorded in the scope's `consts` set and rejected on reassignment.

## Test suite

`tests/test_kerincilang.py` has 151 valid-program tests, 84 error tests, 9 import tests that build temporary multi-file projects, and 27 file tests that work in a temporary folder. `tests/test_tutorial.py` runs all 550 code blocks in `tutorial/` (English and Indonesian) (comparing real output with the output printed in the lesson) and checks that the glossary mentions every keyword and built-in (precedence, string joining, logic operators, `lain kalu` chains, comparison words, `mulai/habih`, loops, break/continue, recursion, closures, constants, Unicode names, and every error message). `tests/test_ids.py` checks the catalogue, the namespace clash matrix, message placeholders, two synthetic dialects that prove the engine is neutral, that every internal error comes from a catalogue message, and that a zipapp built without a checkout still loads its data. `tests/test_dialects.py` checks the synthesized base, parent chains, every validation code, the clash matrix (including the full Siulak word table), the `--ketat` exit codes, and loading a dialect from a zipapp. `tests/test_runtime_selection.py` covers the line-1 header, the header > `--dialek` > Siulak precedence, per-module and per-call vocabulary, imports, fallback warnings, and the `--ketat` exit codes. `tests/test_worksheet.py` covers the CSV contract, `buat`/`perbarui`, every worksheet code, normalization, the synthetic validator, DOCX determinism and round trips, export, readiness, and usage errors. `tests/test_siulak_legacy.py` checks the frozen file, every word and message mapping, `DialectVocabulary` against `LegacySiulak`, header and `--dialek` selection, the missing-file shim, and the `cek_dialek` gate. `tests/test_migration.py` covers single-file and recursive import migration, idempotence, `--semua`, `--dialek`, `--kering`, BOM/malformed-header/parse/dynamic-import refusals, CRLF and byte preservation, usage exits, the zipapp, the examples, and the CLI precedence table. `tests/test_translator.py` has 173 checks covering word/operator/built-in rewriting, user-name preservation, comments and strings, the five round-tripping examples, same-dialect copies, target-owned-ID and symbol refusals, mode/type strings, headers, CRLF and byte preservation, the CLI exit table, mixed-dialect imports, and the zipapp. `tests/test_docs_release.py` is the offline docs/release gate: it walks the contributor guide in a temporary repo, checks links and stale strings, compares the committed grammar with a fresh generation, checks every dialect word is highlighted, and checks the version, changelog, packaging configuration, and release document. `tests/test_release.py` is the separate network-dependent wheel smoke; `build.py` skips it and prints one line pointing at it.

Fixtures for the dialect tests are written into `tempfile.TemporaryDirectory()` roots. The committed `dialects/` holds `__init__.py`, `loader.py`, the frozen `siulak.json`, and the review-state `koto-payang.json`; every other test dialect is temporary.

## Next steps

| Step | Feature | Keywords |
|---|---|---|
| 0.2 ✅ | Lists, indexing, `panjang()`, `untuk` loop, arithmetic built-ins | `daftar`, `panjang`, `untuk`, `tambah`, `kurang`, `kali`, `bagi` |
| 0.2.1 ✅ | Loop and list helpers from speaker vocabulary | `alem`, `jarak`, `nambahkah`, `isi`, `milih`, `pulang` |
| 0.3 ✅ | Type conversion, maps, `pilih`, imports | `bilangan`, `pecahan`, `kato`, `mecem`, `peta`, `pilih`, `ambik` |
| 0.5 ✅ | Speaker vocabulary for errors and text; tutorial; repository packaging | `cubo`, `tangkap`, `ngangkat`, `pisah`, `disatu`; 13 tested lessons |
| 0.4 ✅ | Files, waiting, error handling, string escapes, safe recursion | `bukak`, `baco`, `tulis`, `tutup`, `hapus`, `nantik` |
| later | More text tools (case, find, replace, trim: need words), random numbers, dates, error values (`kelihu`), newline-terminated statements, bytecode VM, browser playground (transpile to JS) | |

## Adding a keyword (recipe)

1. Add the neutral ID to `core/ids.json` (namespace, tier, `en`, `id_gloss`,
   description, example, arity, placeholders).
2. Map the ID to the Siulak word in `LEGACY_WORDS` (and every other dialect later).
3. Add parsing in `Parser.statement()` or `Parser.primary()`, comparing the ID.
4. Add execution in `run()` or `ev()`, and any user text as a `msg.*` entry.
5. Run `python3 make_highlight.py` and `python3 tools/buat_glosarium.py`.
6. Add tests and a line to `03-syntax-design.md`; `tests/test_ids.py` will fail
   if the catalogue, the word map, or the message set disagree.

## Learning resources

- *Crafting Interpreters* by Robert Nystrom (free online), Part I follows this design.
