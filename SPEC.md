# Spec: KerinciLang Multi-Dialect

Status: **approved 2026-11-02.** Date: 2026-11-02.
Source plan: `KerinciLang-Multi-Dialect-Plan.md` (external, project root).
Review: `docs/08-multi-dialect-plan-review.md`.
Capability map: `CAPABILITY-MAP.md` (approved).
First module spec: `SPEC-core-ids.md` (draft for approval).

Module specs are written in dependency order; no later module starts until the current one is approved.

---

## 1. Objective

KerinciLang is one programming language with several Kerinci dialects. A program written in any dialect means the same thing and runs on the same interpreter. Dialects are data files; the language's meaning is defined by neutral IDs, never by one dialect's words.

### Target users

1. **Koto Payang speakers** who want to write and read programs in their own dialect.
2. **Existing Siulak users** whose v0.5 programs must keep running.
3. **Speakers of other Kerinci dialects** (Semurup, Sungai Liuk, Rawang, ...) who join later. The architecture must not privilege any dialect.
4. **Maintainers, teachers, and linguists** who review vocabulary, add dialects, and write lessons.

### Success for the first release

- A Koto Payang speaker can write a program using Koto Payang words, run it with `krc`, and see Koto Payang true/false/null words, type names, file modes, and error messages.
- An existing v0.5 Siulak program runs unchanged after `krc migrasi` adds its header, with the same output.
- A missing Koto Payang word falls back to the neutral English base with one visible warning per ID per run, and the program still runs.
- A contributor can add a dialect with a JSON file and a notes file, without changing Python.
- Adding a dialect does not change any other dialect's behavior.

### Non-goals for this release

- Changing the grammar to follow Kerinci sentence structure (separate research track).
- Translating tutorial prose into Kerinci.
- Incung script keywords.
- Semurup, Sungai Liuk, Rawang, and other dialects (they follow later).
- A web playground or a dialect picker in the VS Code extension.
- The section 9 language fixes (newline termination, richer syntax errors, redeclaration errors). These change behavior and are deferred to 0.7 unless separately approved.

## 2. Assumptions I am making

Correct these now or the spec proceeds with them:

1. **Koto Payang is the first completed dialect.** Siulak is frozen at its v0.5 vocabulary as a `draft` legacy dialect so existing programs, tests, and the tutorial keep working. "Completed Siulak" is a later re-review.
2. **No default dialect.** A file must declare `# dialek: <code>`; `--dialek` is for the REPL and `-c`. The header always wins over the command line.
3. **The Koto Payang worksheet is a first draft.** It needs normalization and a second speaker pass before it becomes `dialects/koto-payang.json`.
4. **Multi-word concepts are joined with underscores** (`lebih_nik_dari`), matching Siulak's `lebih_daripado`. Natural two-token syntax such as else-if (`kalu laen`) remains two tokens, not one ID.
5. **Message placeholders stay neutral English** (`{name}`, `{message}`, `{length}`) and are not translated. The filled sheet must be corrected.
6. **Existing Suilak tests stay unchanged.** 271 language cases and 550 tutorial blocks pass with the frozen Siulak dialect. If Siulak is re-reviewed later, expected output changes are a separate, explicit change.
7. **Code stays MIT.** The CC BY-SA 4.0 decision applies only to `dialects/` and `core/ids.json`, with attribution in each dialect file. Confirm before release.
8. **No new runtime dependencies.** Python 3.9+ standard library only. Developer-only tools may use the standard library; anything else is an `Ask first`.
9. **The single-file build and the wheel must include dialect data.** Packaging is part of the refactor, not a release afterthought.
10. **The dialect code is `koto-payang`.** The filename is `dialects/koto-payang.json`; the header is `# dialek: koto-payang`.

## 3. Capability map

Canonical map: `CAPABILITY-MAP.md`.

| Module id | Responsibility | Depends on |
|---|---|---|
| `core-ids` | Neutral ID catalogue; move lexer, parser, runtime, and messages onto neutral IDs; compatibility shims. | - |
| `dialect-model` | Dialect schema, loader, fallback, namespace-aware validation, completeness report. | `core-ids` |
| `runtime-selection` | Required header, `--dialek`, per-module dialect context, output words, messages, warnings, `--ketat`. | `dialect-model` |
| `cli-migration` | `krc migrasi` (including imports), precedence, REPL/`-c`, exit codes. | `runtime-selection` |
| `worksheet-pipeline` | Canonical CSV, DOCX view, generator, normalizer, placeholder validation, reports. | `core-ids` |
| `dialect-koto-payang` | Normalized Koto Payang data, orthography, provenance, review record. | `worksheet-pipeline`, `runtime-selection` |
| `dialect-siulak-legacy` | Frozen v0.5 vocabulary, provenance, legacy word mapping. | `core-ids` |
| `translator` | `krc terjemah`, lossless policy, user symbols, mixed imports. | `runtime-selection`, two dialects |
| `tutorial-multidialect` | `tutorial/src/`, prose x dialect layout, generated lessons, tests. | `runtime-selection`, one dialect |
| `docs-release` | Contributor guide, docs, VS Code, package data, release notes. | all |

Build order: `core-ids` -> `dialect-model` -> `runtime-selection` + `worksheet-pipeline` + `dialect-siulak-legacy` -> `dialect-koto-payang` -> `cli-migration` -> `translator` -> `tutorial-multidialect` -> `docs-release`.

First milestone (M1): `core-ids`, `dialect-model`, `runtime-selection`, `worksheet-pipeline`, `dialect-siulak-legacy`, `dialect-koto-payang`, `cli-migration`.

## 4. Tech stack

- Python **3.9+** (CI covers 3.9-3.13; local 3.14 must also work).
- Standard library only at runtime: `json`, `re`, `os`, `sys`, `importlib.resources`, `zipapp`, `unittest`-style test scripts.
- Dialect data: UTF-8 JSON, no executable content.
- Tests: the existing plain-Python test scripts, not pytest. New tests follow the same style.
- CI: GitHub Actions, `.github/workflows/tests.yml`.
- Packaging: `pyproject.toml` (setuptools) and `build.py` (zipapp). Dialect data must be included in both.

## 5. Commands

Current commands, kept working:

```bash
# Run the interpreter from a checkout
python kerincilang.py examples/contoh.krc
python kerincilang.py -c "nyetak 1"

# Run the existing suites
python tests/test_kerincilang.py
python tests/test_tutorial.py

# Build the single-file program and run an example
python build.py
python dist/krc.pyz examples/contoh.krc

# Install the command
pip install .
krc --version
```

New commands (introduced by the modules above; names are part of this spec):

```bash
# Dialect validation and completeness (CI gate)
python tools/cek_dialek.py --semua
python tools/cek_dialek.py --kode koto-payang --ketat
# exit 0 = valid; 1 = validation error; 2 = strict-mode fallback error

# Worksheet generation (canonical CSV + DOCX view)
python tools/buat_lembar_kerja.py --kode koto-payang --format csv,docx --out worksheets/

# Read and normalize a filled worksheet
python tools/baca_lembar_kerja.py worksheets/koto-payang.csv --kode koto-payang --periksa

# Required header for old programs (recurses into imports)
krc migrasi examples/contoh.krc
krc migrasi examples/ --semua

# Translate between dialects (M2)
krc terjemah program.krc --ke koto-payang --out program.koto-payang.krc

# Select a dialect for the REPL or a one-liner
krc --dialek koto-payang
krc --dialek koto-payang -c "nyetak 1"
```

Rules:

- `krc FILE` reads the dialect from the file header and never from `--dialek`.
- `krc --dialek CODE -c "..."` and `krc --dialek CODE` require the flag; without it, the error names the flag and `krc migrasi`.
- `--ketat` turns fallback warnings into errors (exit 2) for validation and runs.
- All warnings go to **stderr**. stdout must remain the program's output only.
- `krc migrasi` is idempotent and never rewrites a file that already has a header.

## 6. Project structure

Current (v0.5) and target:

```
kerincilang.py              interpreter (current single file)
core/
  ids.json                  NEW: neutral ID catalogue, the contract
  future.json               NEW: Tier 3 vocabulary with no ID yet
dialects/
  base.json                 NEW: neutral English base, parent null
  siulak.json               NEW: frozen v0.5 Siulak (draft)
  siulak.md                 NEW: provenance, decisions (from docs/02)
  koto-payang.json          NEW: normalized Koto Payang data
  koto-payang.md            NEW: orthography, speaker, sources, review
tools/
  buat_lembar_kerja.py      NEW: worksheet generator (CSV canonical, DOCX view)
  baca_lembar_kerja.py      NEW: reader + normalizer + validation
  cek_dialek.py             NEW: validation and completeness report
  sinkron_tutorial.py       existing; extended for dialect templating (M3)
  buat_glosarium.py         existing; becomes dialect-driven
tests/
  test_kerincilang.py       existing 271 cases (must stay green)
  test_tutorial.py          existing 550 blocks (must stay green)
  test_ids.py               NEW: catalogue integrity
  test_dialects.py          NEW: loader, fallback, validation
  test_runtime.py           NEW: header, selection, output words, warnings
  test_migration.py         NEW: migrasi, idempotence, imports
  test_worksheet.py         NEW: CSV round trip, placeholders
  test_translator.py        NEW: M2
  test_packaging.py         NEW: wheel/pyz contains and loads data
tutorial/
  src/                      NEW (M3): canonical lessons with neutral placeholders
  en/<dialect>/             NEW (M3): generated English lessons
  id/<dialect>/             NEW (M3): generated Indonesian lessons
  *.md, id/*.md             existing Siulak baseline; unchanged in M1
examples/                   existing; add headers during migration
worksheets/                 NEW: generated and filled worksheets (CSV + DOCX)
docs/
  08-multi-dialect-plan-review.md
  09-adding-a-dialect.md    NEW (docs-release)
```

Packaging rule: the runtime must locate `core/ids.json` and `dialects/` from a checkout, an installed wheel, and `dist/krc.pyz`. `build.py` and `pyproject.toml` must include the data. The exact package layout is decided in `SPEC-core-ids.md`.

## 7. Code style

The engine never contains a dialect word. Dialect words appear only in data, tests, examples, docs, and generated tutorial output.

```python
# BAD: the dialect leaks into the engine and the message is hard-coded
if tok.text == "ngan":
    ...
raise LangError("Pembagian dengan nol")

# GOOD: neutral token IDs and a message catalogue entry
if tok.kind == "AND":
    ...
raise LangError(message("msg.div_zero"))

# GOOD: resolve once per module, not once per token
words = dialect.resolve_words()          # {"kw.if": "kalu", ...}
surface = {word: token_id for token_id, word in words.items()}
```

```json
{
  "id": "kw.if",
  "namespace": "kw",
  "tier": 1,
  "en": "if",
  "id_gloss": "jika",
  "arity": null,
  "placeholders": []
}
```

Conventions:

- Python: `snake_case` functions and variables, `UPPER_CASE` constants, 4 spaces, ~100-column lines, no type hints required, no new dependencies.
- Neutral IDs: `namespace.snake_case`, English, immutable once released. Namespaces: `kw`, `op`, `fn`, `val` (if kept), `type`, `mode`, `msg`, `reserved`.
- Dialect files: lower-case kebab-case filename; UTF-8 JSON; 2-space indent; keys sorted; no comments.
- Words: one token per ID, lower-case, NFC-normalized, `[a-z][a-z0-9_]*` for Latin script. A non-Latin word needs an explicit orthography note and a Unicode-aware validator.
- Messages: placeholders are `{snake_case}` names declared in `core/ids.json`; the placeholder set must match exactly.
- Built-ins: registered by the dialect's word in the module scope; never rewritten in the lexer, so user code can shadow them.
- User-facing text: always through the message catalogue, including CLI and REPL text. No f-string user messages.
- Validation: reject unknown IDs, malformed JSON, duplicate resolved words in a lexer namespace, a built-in word equal to a lexer word, and a path outside `dialects/`.
- Output: `show()` takes the current module's dialect; true/false/null and type names come from that dialect.

## 8. Testing strategy

### Test levels

| Level | Where | What it proves |
|---|---|---|
| Unit | `tests/test_ids.py`, `test_dialects.py` | Catalogue integrity; loader, fallback, every validation rule, clash matrix. |
| Integration | `tests/test_runtime.py`, `test_migration.py` | Header selection, `--dialek`, per-module scopes, output words, warnings to stderr, `--ketat`, migration and imports. |
| Corpus / equivalence | `tests/test_kerincilang.py`, new dialect corpus test | Every example and every tutorial block runs in each dialect; output is equal **after normalizing dialect words back to IDs**. |
| Translator | `tests/test_translator.py` | Round trip A -> B -> A on the corpus; refusal cases are explicit and tested. |
| Worksheet | `tests/test_worksheet.py` | CSV -> JSON -> CSV round trip; placeholder mismatch rejected; tier counts. |
| Packaging | `tests/test_packaging.py` | Wheel and `krc.pyz` contain `ids.json` and dialects and run from a clean temp directory. |
| Security | `tests/test_dialects.py` | Path traversal, malformed JSON, huge file, duplicate keys, unknown ID, invalid code. |
| Manual | Speaker review | Tier 1 and Tier 2 words, orthography, and messages accepted by the named reviewer. |

### Existing suites

- `python tests/test_kerincilang.py` must pass **271/271**.
- `python tests/test_tutorial.py` must pass **550 blocks** and the glossary check.
- Any deliberate change to an expected Siulak output is a separate, reviewed change, not a side effect.

### Equivalence rule

Raw stdout is not comparable across dialects because true/false/null, type names, and messages are dialect-specific. The harness must:

1. Run the program in dialect A and dialect B.
2. Map every emitted dialect word and message back to its neutral ID (or compare error message ID + arguments).
3. Compare the normalized streams.

This is the only way the plan's "identical output" claim can be true.

### Coverage

- Every validation rule has at least one positive and one negative test.
- Target 85% line coverage for the new core modules and 100% of the validation matrix. A coverage tool is an `Ask first` (no new dependency by default), so the CI gate is the test matrix until that is approved.

### CI

- Full matrix on Python 3.12: both suites, all dialects, packaging.
- Smoke on 3.9, 3.10, 3.11, 3.13: language tests + one dialect.
- Windows and macOS smoke on 3.12.
- `python -m compileall -q .` as the syntax gate; no linter is configured today.

## 9. Boundaries

### Always

- Run `python tests/test_kerincilang.py` and `python tests/test_tutorial.py` before every commit.
- Add or change an ID in `core/ids.json` before using it anywhere.
- Keep dialect files data-only; no Python per dialect.
- Validate dialect files on load and in CI.
- Write warnings to stderr; keep stdout stable.
- Preserve `{placeholders}` exactly.
- Record maintainer, reviewer, sources, and licence for every dialect.
- Keep Python 3.9 compatibility.
- Keep the engine free of dialect words.
- Make `krc migrasi` idempotent and recurse into imports.

### Ask first

- Adding a new dependency.
- Changing an ID or a released word.
- Changing a Siulak word (this changes output and tests).
- Changing the dialect JSON or `core/ids.json` schema.
- Changing the CLI syntax, header syntax, or precedence rules.
- Adding a new namespace or tier.
- Changing the licence or the scope of CC BY-SA 4.0.
- Dropping, skipping, or rewriting an existing test.
- Deleting a dialect file or a tutorial lesson.

### Never

- Commit secrets, credentials, or personal speaker data without consent.
- Load a dialect from an arbitrary path (`--dialek ../../x`).
- Put a dialect word in the lexer, parser, or interpreter logic.
- Translate or rename `{placeholders}`.
- Edit generated tutorial output by hand.
- Break old `.krc` programs without a migration path.
- Remove or weaken a failing test to get green.
- Relicence the code as CC BY-SA (or the data as MIT) without an explicit decision.
- Ship a build that cannot find its dialect data.

## 10. Success criteria

The initiative is done for M1 when all of the following are true:

1. `python tests/test_kerincilang.py` passes 271/271 and `python tests/test_tutorial.py` passes 550 blocks with the frozen Siulak dialect.
2. A Koto Payang program with a `# dialek: koto-payang` header runs and prints Koto Payang true/false/null words, type names, and file-mode errors.
3. A missing Koto Payang word falls back to `base` and prints exactly one warning per ID per run to stderr; `--ketat` exits 2 instead.
4. `krc migrasi` adds the header to a v0.5 file and its imports, is idempotent, and the migrated file produces the same output.
5. Every invalid dialect case in the review is rejected with a specific, tested message: unknown ID, duplicate lexer word, built-in/keyword clash, missing parent entry, invalid identifier, malformed JSON, path traversal.
6. A mixed-dialect import (`ambik`) runs: the main file and the imported file keep their own dialects, words, and built-in scopes.
7. `python build.py` produces `dist/krc.pyz` that runs both dialects from a clean temporary directory; `pip install .` does the same.
8. `python tools/cek_dialek.py --kode koto-payang` reports tier completeness and exits non-zero for an `approved` dialect with fallbacks.
9. A filled, normalized Koto Payang CSV becomes a valid `dialects/koto-payang.json` with placeholders unchanged.
10. Adding a test dialect requires only a JSON file and a notes file; a contributor can follow `docs/09-adding-a-dialect.md` without reading Python.
11. No dialect word appears in `kerincilang.py` (or the package engine) outside a compatibility shim or a test fixture.

M2 adds: round-trip translation is byte-identical for the corpus, or the tool refuses with a clear error when losslessness is impossible; the translator never rewrites user-declared names.

M3 adds: every generated tutorial block runs in its dialect and normalizes to the same output as the Siulak baseline.

## 11. Open questions

These need a decision before the module specs are written. Recommended defaults are in brackets.

1. **First-release scope.** Koto Payang only, with Siulak frozen as a `draft` legacy dialect? [Yes]
2. **Worksheet status.** Is the Koto Payang sheet a first draft requiring normalization and a second speaker pass? [Yes]
3. **Multi-word concepts.** Underscore-joined identifiers (`lebih_nik_dari`), multi-word lexing, or symbols only? [Underscore-joined, matching Siulak]
4. **Siulak tests.** Freeze v0.5 and keep 271 + 550 unchanged, or re-review Siulak now and accept expected-output changes? [Freeze]
5. **Message placeholders.** Keep neutral English placeholders and re-ask the speaker, or allow translated placeholders? [Keep neutral; re-ask]
6. **Licence scope.** Code MIT, `dialects/` + `core/ids.json` CC BY-SA 4.0? [Yes, confirm with the maintainer]
7. **Section 9 fixes.** Defer all three to 0.7? [Defer]
8. **Tutorial layout.** `tutorial/src/` + `tutorial/en/<dialect>/` + `tutorial/id/<dialect>/`, generated and tested? [Yes, in M3]
9. **Warnings.** stderr only, once per ID per run, `--ketat` exit 2? [Yes]
10. **Dialect code.** `koto-payang` and header `# dialek: koto-payang`? [Yes]
11. **Translator losslessness.** Refuse translation when a user name collides with a target keyword, rather than renaming? [Refuse in 0.6]
12. **Capability map and M1.** Approve the module ids, dependency direction, build order, and M1 above? [Yes]

## 12. Next step after approval

1. Write `SPEC-core-ids.md`.
2. Implement `core-ids` with the 271 + 550 suites green.
3. Proceed in the build order; write each module spec only when its turn arrives.
