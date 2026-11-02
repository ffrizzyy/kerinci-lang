# Spec: docs-release

Status: **proposed for approval.** Parent: `SPEC.md`. Capability map:
`docs-release`.
Depends on `core-ids`, `dialect-model`, `runtime-selection`,
`worksheet-pipeline`, `dialect-siulak-legacy`, `dialect-koto-payang`,
`cli-migration`, `translator`, and `tutorial-multidialect`, all implemented and
green. Date: 2026-11-02.

## 1. Objective

Make the 0.6 multi-dialect work teachable and shippable:

- A person who has never read the Python can add a dialect by following one
  guide, from an empty worksheet to a validated, runnable dialect.
- Every current document, tutorial index, editor file, package and command
  tells the truth about which dialects exist, which status each one has, and
  what a reader must type.
- The 0.6.0 release can be reproduced and verified from a clean checkout.

This module does not add language features, dialect words, or dialect status.
It closes the gap between the implemented system and the documents that are
supposed to explain it.

After this module:

- `docs/09-adding-a-dialect.md` is the executable contributor guide required
  by `SPEC.md` success criterion 10.
- `python3 tools/lembar_kerja.py rangka --kode CODE --nama NAME` creates a
  valid draft JSON skeleton and a notes stub, so the guide never asks a
  contributor to hand-write JSON.
- The VS Code grammar highlights every dialect's words, not only Siulak's.
- The wheel and `dist/krc.pyz` contain every dialect file, and the installed
  wheel runs both dialects from a directory with no checkout.
- `krc --version` and every install document say **0.6.0**.
- `CHANGELOG.md` has a 0.6.0 entry with a status and completeness table for
  each dialect that actually exists.
- The 0.6 release scope is stated honestly: Siulak is frozen at its v0.5
  vocabulary, Koto Payang is at `review`, and Semurup, Sungai Liuk, and Rawang
  are **not** in this release.

## 2. Release scope decision

The parent plan (Phase 7 and decision 8) describes 0.6 as shipping Siulak,
Semurup, and Sungai Liuk. The repository contains no `semurup.json` or
`sungai-liuk.json`, and no speaker-approved worksheet for either. Claiming
them would violate the project's own rule that speakers own their dialect.

Recommended decision:

| Dialect | File | Status in 0.6.0 | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|---|---|
| Siulak | `dialects/siulak.json` | `draft` (frozen v0.5) | 32/32 | 104/104 | 1/1 |
| Koto Payang | `dialects/koto-payang.json` | `review` | 32/32 | 57/104 | 0/1 |

- Siulak owns every ID but stays `draft` because 0.6 freezes the approved v0.5
  vocabulary instead of running a new approval pass. Its 271 language tests
  and 550 tutorial blocks are the compatibility oracle.
- Koto Payang owns 89 of 137 IDs. The other 48 fall back to the English base.
  A second speaker pass is still required before `approved`.
- Semurup, Sungai Liuk, and Rawang are explicitly listed as **not included**,
  with the reason and the path to add them (`docs/09`). They are not renamed,
  stubbed, guessed, or copied from Siulak.
- The version stays `0.6.0`. The engineering contract for multi-dialect is
  complete; dialect coverage is a separate, speaker-gated axis. A future
  release adds a dialect without changing the runtime.

If the human wants 0.6 to wait for Semurup and Sungai Liuk, this module stops
before the version bump and the release notes stay under "Unreleased". That is
the only alternative considered; shipping invented or empty dialects is not.

## 3. Contributor guide: `docs/09-adding-a-dialect.md`

This is the primary deliverable. It must be usable in order, by copy and
paste, on Windows, macOS, and Linux. It is written in English with the same
tone as `CONTRIBUTING.md`; no Python reading is required.

### 3.1 Required outline

1. **What a dialect is.** A JSON file, a CSV worksheet, and a notes file. The
   engine, grammar, tutorial generator, and tests are shared. No Python change
   per dialect. A dialect never changes another dialect.
2. **Before you start.** Choose the code (`^[a-z0-9-]+$`), display name, the
   speaker(s), the maintainer, the reviewer, the dictionary/source, and the
   licence (CC BY-SA 4.0 for dialect data). Write the spelling rules first.
   Never guess, machine-translate, or borrow a Siulak word to fill a gap.
3. **Scaffold.** The exact commands in section 3.2, with a made-up code
   `dialek-baru` that is clearly a placeholder. Explain the three files and
   which one is canonical.
4. **Fill the worksheet.** Tier 1 first, then Tier 2, then Tier 3. One word per
   answer, no spaces, joined with `_` where the natural form is two words.
   Message placeholders (`{name}`, `{line}`, `{path}`) stay exactly as they
   are and are never translated. Record alternatives and sources in `notes`.
   Use `todo`, `draft`, `reviewed`, `rejected`; a `rejected` row keeps its
   reason. A `reviewed` row needs a speaker, not a guess.
5. **Check and convert.** `periksa --siap`, `laporan`, `json`. Explain that
   `json` reads only accepted (`draft` / `reviewed`) rows, preserves metadata,
   validates the merged file, and refuses to write on a blocking problem.
6. **Write the notes file.** The headings and content that `dialects/<code>.md`
   needs: provenance, orthography, mapping decisions, review record, gaps.
   Point to `dialects/koto-payang.md` as the worked example. State that the
   DOCX is an optional review view and is never ingested.
7. **Promote the status.** `draft` -> `review` -> `approved`, with the exact
   gates: `review` needs all Tier 1 rows `reviewed` and at least one source;
   `approved` additionally needs all Tier 2 rows `reviewed` and a named
   reviewer. `approved` is not a label a contributor gives themselves.
8. **Validate.** `cek_dialek --kode`, `cek_dialek --ketat`, and a real program
   with `# dialek: <code>`. Explain the fallback warning: one line per missing
   ID, stdout stays clean, and `--ketat` fails an `approved` dialect that still
   borrows a Tier 1 word.
9. **Tutorial.** `sinkron_tutorial.py --bangun <code>` for a local check;
   `--semua-dialek` for every `review` / `approved` dialect. Only commit a
   generated tree for a dialect that is at least `review`. Extend
   `tests/test_tutorial_dialects.py` with a case for the new dialect before
   committing its tree. Never edit generated output by hand.
10. **Editor and glossary.** `make_highlight.py` picks up the new words
    automatically. `buat_glosarium.py` remains the Siulak glossary; a generated
    tutorial gets a glossary stub until the dialect is approved.
11. **Tests and CI.** `python3 build.py`, then the release smoke in
    `RELEASING.md`. Add a focused `tests/test_<code>.py` only if the dialect
    pins exact words or messages; the shared suites already validate and run
    the file.
12. **Checklist and common errors.** A short checklist and a table of the
    loader/worksheet errors a contributor will actually see: unknown ID,
    duplicate word, keyword/built-in clash, a missing placeholder, an
    alternative answer containing `/`, an invalid identifier, a missing
    source for `review`/`approved`, an `approved` file with no reviewer.

### 3.2 The exact scaffold commands

The guide uses this sequence with the placeholder `dialek-baru`:

```bash
python3 tools/lembar_kerja.py buat --kode dialek-baru
python3 tools/lembar_kerja.py rangka --kode dialek-baru --nama "Dialek Baru"
python3 tools/lembar_kerja.py periksa --kode dialek-baru
python3 tools/lembar_kerja.py laporan --kode dialek-baru
python3 tools/lembar_kerja.py json --kode dialek-baru
python3 tools/cek_dialek.py --kode dialek-baru
python3 tools/cek_dialek.py --kode dialek-baru --ketat
python3 tools/sinkron_tutorial.py --bangun dialek-baru
python3 make_highlight.py
python3 build.py
```

`--kode dialek-baru` is a placeholder. The guide must say so in bold: "Do not
commit a dialect called `dialek-baru`." A test uses this exact code in a
temporary copy, so the steps are proven, not just described.

### 3.3 New worksheet command: `rangka`

`lembar_kerja.py` gains one command:

```bash
python3 tools/lembar_kerja.py rangka --kode CODE --nama NAME
    [--pemelihara TEXT] [--ortografi TEXT]
    [--json PATH] [--md PATH] [--paksa]
```

- `--kode` is required and must match `^[a-z0-9-]+$`.
- `--nama` is required and non-empty.
- `--pemelihara` defaults to `pending`; the guide tells the contributor to
  replace it.
- `--ortografi` defaults to a clearly pending sentence.
- It writes `dialects/CODE.json` and `dialects/CODE.md`. Both paths are
  overridable for tests. It refuses an existing file unless `--paksa`.
- It validates the JSON with `loader.validate_dialect` before writing.
- The JSON is a valid `draft` skeleton: `code`, `name`, `core` from
  `CORE_VERSION`, `revision: 1`, `parent: null`, `license: "CC BY-SA 4.0"`,
  `maintainer`, `reviewer: null`, `sources: []`, `orthography`, `notes`,
  `words: {}`, `messages: {}`. Keys sorted, two-space indent, UTF-8, LF,
  trailing newline.
- The Markdown stub has the headings from section 3.1 step 6 and a one-line
  status banner. It is a writing prompt, not a generated report.
- Exit codes match the existing tool: 0 ok, 1 file/validation problem, 2 bad
  usage. Help lists `rangka`.

The command is generic. It adds no dialect and no dialect word.

## 4. Document truth audit

The audit fixes current statements that the multi-dialect implementation made
false. It does not rewrite history: `SPEC-*`, `docs/08`, and the changelog keep
their dated records.

| File | Change |
|---|---|
| `README.md` | Present 0.6.0 as multi-dialect. Keep the Siulak sample, add the `# dialek:` rule, `--dialek`, `krc migrasi`, `krc terjemah`, and a status table with only Siulak and Koto Payang. Replace the "vocabulary approved" paragraph with the frozen-Siulak / Koto Payang-review truth. Link `docs/09`. |
| `GETTING-STARTED.md` | Every 0.5.0 folder, banner, extension-folder, tag, and release name becomes 0.6.0. Add a short "Choose a dialect" step. Say `build.py` runs all offline checks, not "both test files". |
| `CONTRIBUTING.md` | Replace "the reference dialect is Siulak" with the no-standard rule. Replace the obsolete `KEYWORDS` / `WORD_OPERATORS` / `BUILTINS` recipe with the CSV/JSON workflow. Add "If you add a dialect" with a link to `docs/09`. Update the test commands. Update the Indonesian summary. |
| `docs/01-vision-and-goals.md` | Add a dated status banner: this is the original v1 vision; current status is `07`. Replace the "Reference dialect: Siulak" decision with the two-dialect / no-standard decision. |
| `docs/02-vocabulary-worksheet.md` | Mark the page as the frozen Siulak v0.5 provenance and checklist. Replace "Changing a word" (edit `KEYWORDS`) with: Siulak is frozen; a new dialect starts at `docs/09`. |
| `docs/03-syntax-design.md` | Label the keyword list as Siulak (frozen v0.5). Keep the existing choosing/migration/translation sections and add a link to `docs/09` for a new dialect. |
| `docs/04-implementation.md` | Add `docs-release` to the test/tool layout. Add a short "Adding a dialect" section that points to the guide instead of repeating the worksheet recipe. |
| `docs/05-tooling-and-docs.md` | Document the union grammar and the extension README. Add `09-adding-a-dialect.md` and `RELEASING.md` to the document table. |
| `docs/06-community-and-preservation.md` | Say the project is multi-dialect, Siulak is first and frozen for compatibility, and a new dialect needs its own speakers. Update the outreach message and the dialect-dispute risk row. |
| `docs/07-roadmap.md` | Add "Milestone 8: v0.6.0 multi-dialect" with what shipped, the Koto Payang second pass still open, and the Semurup/Sungai Liuk/Rawang deferral. |
| `docs/README.md` | Index `08-multi-dialect-plan-review.md` (currently missing) and `09-adding-a-dialect.md`; link `RELEASING.md`. |
| `tutorial/README.md`, `tutorial/id/README.md` | Keep the existing Koto Payang pointer. Do not touch lesson code or the 14 numbered lesson files; `tests/test_tutorial.py` still requires all 14 links. |
| `vscode-extension/README.md` | New: install path for 0.6.0, `.krc`, `# dialek:`, what the union grammar covers, and that a per-dialect picker is not in 0.6. |
| `RELEASING.md` | New: the repeatable release checklist (section 8). |

The test suite forbids these stale strings in current reader-facing files
(`README.md`, `GETTING-STARTED.md`, `CONTRIBUTING.md`, `docs/01`-`07`,
`vscode-extension/README.md`):

- `Reference dialect: Siulak`
- `the reference dialect is **Siulak**`
- `edit the value in the `KEYWORDS` table`
- `Edit the right-hand side of `KEYWORDS``
- `TYPE_NAMES["bool"]`
- `kerincilang-0.5.0`
- `uses Siulak Kerinci words`

`CHANGELOG.md` and the `SPEC-*` files are exempt; they record history.
`docs/04-implementation.md` may still name `KEYWORDS` as a compatibility
export, but not as the place to change a word.

## 5. Editor support

`make_highlight.py` no longer imports `KEYWORDS`, `WORD_OPERATORS`, or
`BUILTINS`. It loads every dialect in `dialects/` through
`available_dialects()` and `load_dialect()`, and builds one deterministic
union grammar.

Rules:

- The union contains every highlighted surface a reader can legally type in any
  dialect: for each dialect, every `kw.*`, `op.*`, and `fn.*` word it resolves
  to, whether owned or taken from the base. Koto Payang therefore contributes
  `contains`, `list`, `map`, and `wait` as valid fallback function names.
  `error` is a reserved word and is not highlighted; `base` itself is not a
  dialect file and is not added wholesale.
- Groups stay the same as 0.5: comments, strings with escapes, numbers,
  `keyword.control`, `storage.type`, `keyword.operator.word`,
  `support.function`, `support.function.builtin` (requires a following `(`),
  and `constant.language`.
- Words are de-duplicated, sorted, and regex-escaped. The header line
  `# dialek: CODE` is a comment, so the existing comment rule covers it.
- `type.*` and `mode.*` words are not added to source highlighting; they are
  runtime output or string arguments, and adding them would color ordinary
  text. `fn.*` remains highlighted only before `(`.
- `buat_glosarium.py` stays Siulak-only. It is not part of the union grammar.
- The generator is deterministic: JSON with two-space indent, sorted keys,
  `ensure_ascii=False`, LF, one trailing newline. It writes relative to the
  repository root, so it works from any working directory.
- `vscode-extension/package.json` gets version `0.6.0` and a description that
  names every dialect, not only Siulak.
- No dialect picker or per-dialect grammar is added in 0.6. The parent plan
  lists a picker as a later idea. The union grammar is the honest 0.6 answer:
  every valid word gets color, and no dialect is presented as the standard.

## 6. Packaging

The wheel and the zipapp must both find their data from a directory with no
checkout.

- `pyproject.toml` version becomes `0.6.0`; description becomes a multi-dialect
  description; keywords add `dialect` and `koto-payang`.
- Keep `packages = ["core", "dialects"]`.
- Keep package data as `core/*.json`, `dialects/*.json`, and `dialects/*.md`.
- Do **not** ship `dialects/src/*.csv`. The CSV is the canonical worksheet and
  provenance for contributors; the runtime needs only JSON and the notes. A
  wheel that grew by 17 KB of worksheets would still work, but the CSV is not
  a runtime artifact and its location is documented as a checkout file.
- A fresh wheel must contain no `.pyc` or `__pycache__` entries. The release
  smoke builds from a clean copy, so a stale local `build/` directory cannot
  hide a packaging bug.
- The installed wheel must run a Siulak program and a Koto Payang program with
  `PYTHONPATH` pointing at the install target and a cwd outside the checkout.
- `dist/krc.pyz` already copies `core/` and `dialects/`; `build.py` keeps that
  behavior and the existing zipapp smoke stays green.

## 7. Version and release notes

### 7.1 Version locations

All must agree on `0.6.0`:

| Location | What changes |
|---|---|
| `kerincilang.py` | `__version__ = "0.6.0"` |
| `pyproject.toml` | `version = "0.6.0"` |
| `vscode-extension/package.json` | `"version": "0.6.0"` |
| `README.md` | `Version **0.6.0**` |
| `GETTING-STARTED.md` | `KerinciLang 0.6.0`, `kerincilang-0.6.0`, `kerincilang.kerincilang-0.6.0`, `v0.6.0` |
| `CHANGELOG.md` | top entry `## 0.6.0 (2026-11-02)` |
| `RELEASING.md` | tag `v0.6.0` |
| `docs/07-roadmap.md` | milestone heading `v0.6.0` |

`core/ids.json` stays `"core": "0.6"`. It is a compatibility tuple
(MAJOR.MINOR), not the package version. The guide and release notes explain
the difference.

### 7.2 `CHANGELOG.md` 0.6.0 entry

The entry must contain:

- A one-paragraph summary: one language, many dialects; the same program
  meaning; dialects are data; incomplete dialects fall back with a warning.
- The dialect table from section 2 with status and tier counts.
- **New:** neutral IDs and the catalogue; dialect loader and validation;
  `# dialek:` header, `--dialek`, fallbacks, `--ketat`; `krc migrasi`;
  `krc terjemah`; the worksheet pipeline; the generated English/Indonesian
  Koto Payang tutorial; the union VS Code grammar; `docs/09`; `RELEASING.md`.
- **Compatibility:** existing v0.5 programs still run. A headerless file uses
  Siulak; `krc migrasi` adds the header and recurses into literal imports.
  No Siulak word or tutorial output changed.
- **Fallbacks:** a missing word uses the English base and warns once per ID on
  stderr; stdout stays clean; `--ketat` exits 2 for an `approved` dialect with
  a Tier 1 gap. Koto Payang's tutorial lists `contains` and `boolean`.
- **Not in this release:** Semurup, Sungai Liuk, and Rawang. No speaker-approved
  files exist; the guide is the path to add them. This sentence is required so
  a reader cannot mistake the parent plan's original phase list for a shipped
  promise.
- **Tests:** 271 language checks, 550 baseline tutorial blocks, the new
  dialect/migration/translator/worksheet/generated-tutorial suites, and the
  release smoke. Do not print a single grand total that will drift.

## 8. `RELEASING.md`

A short maintainer checklist, linked from `CONTRIBUTING.md`, `docs/README.md`,
and `docs/09`:

1. Clean tree on `main`; `git pull`.
2. Confirm the version locations in section 7.1 and the changelog heading
   agree.
3. Regenerate and check no diff:
   `python3 tools/buat_glosarium.py`,
   `python3 make_highlight.py`,
   `python3 tools/sinkron_tutorial.py --bangun koto-payang`.
4. Run `python3 build.py` (all offline suites), then
   `python3 tools/cek_dialek.py --semua`.
5. Run `python3 tests/test_release.py` (wheel build, contents, install, run).
6. Run the zipapp smoke from a temporary directory with both dialects.
7. Commit, tag `v0.6.0`, push, and publish a GitHub release that attaches
   `dist/krc.pyz`; paste the dialect status table into the notes.
8. Post-release: install the wheel in a clean environment, run
   `krc --version`, and run one Siulak and one Koto Payang program.

The checklist also records how to change the release scope: add the dialect
file and its speaker record first, then update the changelog table; never
attach a dialect name to a release before its file exists.

## 9. Tests

### 9.1 `tests/test_docs_release.py` (offline)

At least these checks, all in temporary copies where a file could be written:

1. **Guide walkthrough.** Run the section 3.2 commands in order in a temporary
   repo with the placeholder `dialek-baru`: scaffold CSV, JSON, and notes;
   fill the 32 Tier 1 rows with reviewed answers; set `status: review` and a
   source; `periksa --siap` and `laporan` pass; `json` merges 32 words and no
   messages; `cek_dialek` and `cek_dialek --ketat` exit 0; a program with
   `# dialek: dialek-baru` prints its output.
2. **Guide references.** Every `python3 tools/...py` command named in
   `docs/09` resolves to an existing file; every local path it names exists;
   it names `rangka`, `periksa`, `laporan`, `json`, `cek_dialek`,
   `sinkron_tutorial.py --bangun`, `make_highlight.py`, and `build.py`.
3. **Docs index and links.** `docs/README.md` lists 08 and 09; `CONTRIBUTING.md`
   links 09; `docs/09` links `RELEASING.md`, `dialects/koto-payang.md`, and
   `dialects/src/koto-payang.csv`.
4. **Stale-string audit.** The forbidden strings in section 4 are absent from
   the current reader-facing files; `CHANGELOG.md` and `SPEC-*.md` are exempt.
5. **Version consistency.** The eight locations in section 7.1 agree, and no
   current reader-facing file outside `CHANGELOG.md` / `SPEC-*.md` says
   `0.5.0`.
6. **Release notes.** `CHANGELOG.md` has a 0.6.0 heading, rows for `siulak` and
   `koto-payang` with their tier counts, and a "Not in this release" sentence
   naming Semurup, Sungai Liuk, and Rawang.
7. **Grammar freshness.** `make_highlight.render()` equals the committed
   `vscode-extension/syntaxes/krc.tmLanguage.json` byte for byte.
8. **Grammar coverage.** For every dialect from `available_dialects()`, every
   `kw.*`, `op.*`, and `fn.*` word the dialect resolves to appears in the
   grammar text. `type.*`, `mode.*`, `reserved.*`, and messages are
   intentionally absent. The grammar is valid JSON, contains the
   comment/string/number rules, and does not contain a hardcoded Siulak-only
   keyword list.
9. **Extension metadata.** `vscode-extension/package.json` version is 0.6.0,
   the description names the dialects, and `vscode-extension/README.md`
   explains the union rule and the missing picker.
10. **Packaging configuration.** `pyproject.toml` declares `core` and
    `dialects`, the package-data globs match every `core/*.json`,
    `dialects/*.json`, and `dialects/*.md`, and the description is
    multi-dialect. This is the offline half; the wheel itself is tested by
    9.2.
11. **Release document.** `RELEASING.md` names the version, `build.py`,
    `cek_dialek --semua`, `test_release.py`, `pip wheel`, and the tag.
12. **No collateral change.** The baseline tutorial still reports 550 blocks,
    `tests/test_tutorial.py` is untouched, and `dialects/koto-payang.json`
    still says `review`.

### 9.2 `tests/test_release.py` (wheel smoke)

This suite needs `pip` and its isolated build (network on a clean CI runner).
It is run by CI on Python 3.12 and by `RELEASING.md`; `build.py` runs every
offline suite and prints one line saying the wheel smoke runs separately.

1. Copy the repository to a temporary directory, excluding `.git`, `build`,
   `dist`, `*.egg-info`, `__pycache__`, and `*.pyc`.
2. `python -m pip wheel . --no-deps -w <tmp>`; fail with the captured stderr
   if it cannot build.
3. Open the wheel: it contains `core/ids.json`, `dialects/siulak.json`,
   `dialects/siulak.md`, `dialects/koto-payang.json`, and
   `dialects/koto-payang.md`; it contains no `dialects/src/*.csv`, no
   `__pycache__`, and no `.pyc`.
4. `python -m pip install --no-deps --target <target> <wheel>` succeeds.
5. From a cwd outside the checkout, with `PYTHONPATH` set to the target, run a
   Siulak program and a Koto Payang program through the installed module. Both
   print the expected output, and `available_dialects()` returns both codes.

### 9.3 Existing suites

No existing expectation changes. The 271 language checks, 550 baseline
tutorial blocks, dialect, worksheet, migration, translator, and generated
tutorial suites stay green. `build.py` discovers `tests/test_*.py` in sorted
order, skips `test_release.py`, prints each suite name, and stops on the first
failure.

## 10. CI

The workflow keeps the Python 3.9-3.13 matrix and the Windows/macOS smoke, and
adds release gates on Ubuntu 3.12:

- Full offline suite: `python build.py` (includes the new docs-release suite).
- `python -m compileall -q .`.
- `python tools/cek_dialek.py --semua`.
- Freshness: run `buat_glosarium.py`, `make_highlight.py`, and
  `sinkron_tutorial.py --bangun koto-payang`, then `git diff --exit-code`.
- `python tests/test_release.py` (wheel build/install/run).
- `pip install .`, `krc --version`, and one Koto Payang program from `/tmp`.

Smoke jobs on the other Python versions and on Windows/macOS run the language,
tutorial, Koto Payang, and generated-tutorial suites. They do not need the
wheel smoke or the regeneration diff.

## 11. Boundaries

### Always

- Run `python3 build.py` and `python3 tools/cek_dialek.py --semua` before a
  commit; run `tests/test_release.py` before a release.
- Keep the guide executable: a command, path, or option it names must exist.
- Keep dialect status and tier counts copied from `cek_dialek` and `laporan`,
  not estimated.
- Keep the baseline lessons, their output, the 271 checks, and the 550 count
  untouched.
- Keep the engine free of dialect words and the package free of per-dialect
  Python.
- Regenerate the grammar, glossary, and tutorial trees instead of editing
  generated files.
- Keep Python 3.9 compatibility in tests and tools.
- Credit speakers and sources in the dialect notes.

### Ask first

- Adding Semurup, Sungai Liuk, Rawang, or any new dialect file or word.
- Promoting Koto Payang to `approved` (needs the second speaker pass).
- Changing the 0.6 release scope or version scheme.
- Adding a dependency to the test or release path.
- Changing the CLI, header, status ladder, or `--ketat` behavior.
- Changing the licence or the dialect data format.

### Never

- Invent, machine-translate, or copy a word to fill a gap.
- Claim a dialect that has no file or no speaker review.
- Mark a row `reviewed` without a speaker.
- Edit generated tutorial output, the grammar, or a glossary by hand.
- Weaken a test, delete a check, or change an expected output to make a
  release pass.
- Ship a wheel or zipapp that cannot find `core/ids.json` and `dialects/`.
- Put dialect words in Python logic.
- Publish `dialek-baru` or any placeholder as a real dialect.

## 12. Success criteria

1. A new contributor can follow `docs/09` alone, in a clean copy, and produce
   a valid draft dialect, a converted JSON file, a passing `cek_dialek`, and a
   runnable program. The walkthrough test proves the exact commands.
2. `docs/09` exists, is indexed, is linked from `CONTRIBUTING.md`, and names no
   missing command or path.
3. `krc --version` prints `KerinciLang 0.6.0`; all eight version locations
   agree; no current reader-facing file outside the changelog and the specs
   says 0.5.0.
4. The wheel built from a clean copy contains both dialect JSON/MD files and
   `core/ids.json`, contains no CSV or bytecode, installs, and runs both
   dialects from outside the checkout.
5. The committed VS Code grammar is byte-identical to a fresh generation and
   covers every highlighted word every dialect resolves to; the extension
   README explains the union rule.
6. `build.py` runs every offline suite; CI runs the full suite, the freshness
   diffs, and the wheel smoke.
7. `CHANGELOG.md` 0.6.0 lists Siulak (draft, frozen) and Koto Payang (review)
   with real tier counts and says Semurup, Sungai Liuk, and Rawang are not
   included.
8. `RELEASING.md` gives the repeatable release steps and is linked from the
   guide and the docs index.
9. The stale-string audit passes; no current doc tells a reader to edit
   `KEYWORDS` or install `kerincilang-0.5.0`.
10. The baseline tutorial still has 550 blocks, the language suite still has
    271 checks, Koto Payang is still `review`, and every earlier suite passes
    unchanged.

## 13. Decisions

| # | Decision | Why |
|---|---|---|
| D1 | 0.6.0 ships Siulak (frozen draft) and Koto Payang (review); Semurup, Sungai Liuk, and Rawang are explicitly not included. | The parent phase list names dialects that have no speaker-approved file. Shipping only what exists follows the project's own rule. |
| D2 | Add `lembar_kerja.py rangka` for a JSON and notes skeleton. | Otherwise the guide cannot be followed without hand-writing JSON or copying Koto Payang words. |
| D3 | One union VS Code grammar; no per-dialect picker in 0.6. | The parent plan lists a picker as a later idea, and a content-based grammar cannot switch on `# dialek:`. Union colors every valid word without making one dialect standard. |
| D4 | Ship dialect JSON and notes in the wheel, not `dialects/src/*.csv`. | The runtime needs data, not worksheets; the CSV stays canonical in the checkout. |
| D5 | `tests/test_docs_release.py` is offline and runs in `build.py`; `tests/test_release.py` is a separate wheel smoke run by CI 3.12 and `RELEASING.md`. | Keeps the everyday build offline and keeps the network-dependent wheel check in the release gate. |
| D6 | Keep `core` at `0.6` and the package at `0.6.0`. | `core` is a MAJOR.MINOR compatibility tuple; the package has a patch release. |
| D7 | Add `RELEASING.md` rather than another numbered design doc. | It is a maintainer checklist, not design history; GitHub surfaces it next to `CONTRIBUTING.md`. |
| D8 | Do not change `--ketat`, the CLI text, any dialect word, or any expected output. | Those are product changes outside a docs/release module; the audit describes what the tools actually do. |

## 14. Next step

On approval:

1. Archive the tutorial plan/todo under `tasks/archive/`.
2. Write `tasks/plan.md` and `tasks/todo.md` for `docs-release`.
3. Add `rangka`, the guide, the truth-audit edits, the union grammar, the
   extension README, `RELEASING.md`, the two new test suites, and the version
   bump.
4. Run all offline suites, `cek_dialek --semua`, the generators, `compileall`,
   `build.py`, the wheel smoke, and the zipapp smoke.
5. Commit, tag the release only after the human confirms, and push.

## 15. Implementation log

Not started. This section is filled in only after the module is green and
committed.
