# Multi-Dialect Plan Review

Date: 2026-11-02
Reviewed:

- `KerinciLang-Multi-Dialect-Plan.md` (project root, outside this repo)
- `kerinci-lang` v0.5.0, commit `7ea40ba`
- `Translation Worksheet (Koto Payang).docx` (filled)
- `Translation Worksheet.docx` (blank template)

Verdict: **the architecture is right, but the plan is not ready for phase 1 as written.** There are ten blocking contradictions between the plan, the current code, and the filled Koto Payang worksheet, plus a number of design gaps that will surface during implementation.

The most important single finding: **the Koto Payang worksheet is a first linguistic draft, not an ingestible data file.** It fails the plan's own rules (spaces, uppercase, slash alternatives, changed placeholders, no ID column), so the roadmap gate "a filled worksheet becomes a valid dialect file" is not true today.

---

## 1. What the plan gets right

- Neutral IDs, dialects as data, and a neutral English base are the correct shape.
- Per-file `# dialek:` headers and per-module scopes are the right way to mix dialects across imports.
- Tiering vocabulary by essentiality makes progress visible to speakers.
- Keeping built-ins as ordinary names (so user code can shadow them) preserves the current language's best design decision.
- The migration path for 0.5 programs and the round-trip translator gate are the right instincts.
- The stated test counts are accurate: **271** language cases and **550** tutorial code fences.

## 2. Blocking findings

### B1. Validation rule 3 rejects today's Siulak vocabulary

The plan says a dialect is rejected if "two IDs resolve to the same word after fallback". Today's Siulak vocabulary deliberately shares words across namespaces:

| Word | Namespaces |
|---|---|
| `betul` | `kw.true`, `val.true` |
| `salah` | `kw.false`, `val.false` |
| `kosong` | `kw.null`, `val.null`, `type.null` |
| `guno` | `kw.func`, `type.func` |
| `bilangan` | `fn.int`, `type.int` |
| `pecahan` | `fn.float`, `type.float` |
| `kato` | `fn.text`, `type.str` |
| `daftar` | `fn.list`, `type.list` |
| `peta` | `fn.map`, `type.map` |
| `baco` | `fn.read`, `mode.read` |
| `tulis` | `fn.write`, `mode.write` |
| `nambahkah` | `fn.append`, `mode.append` |

Evidence: `kerincilang.py:74-78` (`TYPE_NAMES`), `:597` (`MODES`), `:744-769` (`BUILTINS`).

The rule must be namespace-aware:

- **Lexer namespaces** (`kw.*`, `op.*`, `val.*`, reserved words) must be unique among themselves. A collision here is always an error.
- **Built-in names** must not equal a lexer word. Otherwise the lexer wins and the built-in is unreachable.
- **Output-only namespaces** (`type.*`) may share with anything; they are only returned as text.
- **Mode names** are string values, not lexed words, so they may share with built-ins and keywords.
- **User names** may shadow built-ins by design.

Rule 4 gestures at this ("active in the same position") but does not specify the matrix, and rule 3 as written would reject Siulak itself.

### B2. The ID catalogue double-counts true / false / null

`kw.*` is listed as 26 IDs, and that 26 includes `TRUE`, `FALSE`, `NULL` in `KEYWORDS`. The plan then adds a separate `val.*` group with true / false / null, and `type.null` as well. Pick one ownership model before writing `core/ids.json`:

- `kw.true`, `kw.false`, `kw.null` are the lexed words; `type.null` is output-only; drop `val.*`.
- Or keep `val.*`, remove them from `kw`, and make `kw` 23.

The current plan leaves three IDs for one word and then forbids duplicate words.

### B3. The required header conflicts with the existing API and tests

All 271 language tests call `run_source(src)` with no file and no header. If the header is required at the lexer/API level, every test breaks on day one. The plan's "required first line" needs an explicit API rule:

- `run_file(path)` and the CLI enforce the header.
- `run_source(src, dialect=...)` takes the dialect explicitly, for tests, embedding, the REPL, and `krc -c`.
- `do_import` (`kerincilang.py:786-814`) currently calls `tokenize(src)` directly at line 805. It must read the imported file's header first and build a separate module scope.
- `krc migrasi` must recurse into imports; otherwise "fix the header" leaves a project half-migrated.

Also decide the header's exact shape: line 1 literally, or first non-blank line after a shebang/BOM? Case sensitivity? `dialek` vs `dialect`?

### B4. The Koto Payang worksheet fails the plan's own rules

Counts from the filled sheet (287 numbered rows):

| Tier | Rows | Answers with spaces | Slash alternatives | Starts uppercase | Same as Indonesian | Blank |
|---|---:|---:|---:|---:|---:|---:|
| 1 Essential | 33 | 12 | 1 | 6 | 4 | 0 |
| 2 Common | 61 | 34 | 2 | 23 | 2 | 1 |
| 3 Future | 193 | 126 | 10 | 115 | 65 | 1 |

Across the whole sheet, 194 of 306 answer cells contain spaces. Examples that cannot be identifiers as written:

- `kalu laen` (else-if), `nga laen` (else)
- `samu dinga`, `iduak samu dinga`, `lebih nik dari`, `lebih nik atau samu dinga`
- `Netakka variabel`, `Netakka konstanta`
- `Awal blok kode`, `Akhir blok kode` (not translated at all)
- `bilangan buluak`, `bilangan bakoma/bilangan desimal`
- `impor/masukka` (two answers in one cell)
- `Meriksu apukah item adea daling daftar, peta ...` (a sentence, not a word)

`bool` is blank. Many answers start uppercase (`Lanjutka`, `Nytak`, `Netakka`), but identifiers are case-sensitive.

**Consequence:** add a normalization step and a second speaker pass before `baca_lembar_kerja.py` can produce a valid file. The phase 3 gate should be "a normalized CSV becomes a valid dialect file", not "a filled worksheet does".

### B5. The worksheet has no neutral ID column and uses Python vocabulary

The blank template has five columns: number, feature, Bahasa Indonesia, answer, notes. The filled Koto Payang sheet has four; the notes column was dropped.

Worse, the rows describe Python concepts, not KerinciLang IDs:

| Worksheet row | KerinciLang reality |
|---|---|
| `elif` | `kw.else` + `kw.if` (two tokens), no `kw.elif` |
| `def` | `kw.func` |
| `match` | `kw.switch` |
| `except` | `kw.catch` |
| `dict` | `type.map` |
| `type()` | `fn.mecem` |
| `sorted()` / `reversed()` | `fn.sort` / `fn.reverse` |
| `contains()` / `wait()` | `fn.contains` / `fn.wait` |
| `r` / `w` / `a` | `mode.read` / `mode.write` / `mode.append` |

There is no reliable row-to-ID mapping, and 193 Tier 3 rows have no ID at all. The plan says future vocabulary is allowed, but does not define where it is stored (it cannot go into `dialects/<code>.json`, which only accepts known IDs).

Fix: make CSV the canonical answer format with columns `id, tier, namespace, en, id_gloss, answer, notes, status`; generate the DOCX from it; require an `id` on every live row; store no-ID future rows in a separate `core/future.json`.

### B6. Message placeholders were translated

16 of 24 message rows changed the placeholders, although the plan and the worksheet both say placeholders must not change:

- `{name}` → `{namu}`
- `{message}` → `{pesan}`
- `{length}` → `{panja}`
- `{function}` → `{pungsi}`
- `{try}` → `{cubea}`, `{catch}` → `{tangkak}`

If the runtime formats the dialect's template with the neutral argument names, these templates raise `KeyError`. Add a hard validation rule: the placeholder set of every `msg.*` entry must equal the set declared in `core/ids.json`; placeholders are read-only in the worksheet (protect them in the DOCX or keep answers in CSV).

Also: the plan says "about 30 messages", but the code has **61 `LangError` raise sites and 59 unique message templates**, plus CLI/REPL text (`Kesalahan:`, `USAGE`, REPL banner). The catalogue inventory is roughly double the estimate.

### B7. "Round trip is lossless" contradicts renaming and fallback

The plan says:

- translating A to B and back to A gives the original file; and
- if a user's own name equals a keyword in the target dialect, the tool renames it and prints a warning.

Once renamed, the original name is gone; B to A cannot restore it. The English fallback introduces a second loss: if B lacks a word, the output contains the base word, which may map to a different source word on the way back. File-mode strings held in variables are a third loss: the translator only rewrites literals in `bukak` calls.

Pick one policy for phase 5:

1. **Refuse** translation when a lossless result is impossible, with a clear error (safest; keeps the strong gate).
2. Emit a rename manifest and relax the gate to "semantics + manifest".
3. Require the source program to be renamed before translation.

Recommendation: option 1 for 0.6, and revisit when the translator has a symbol table.

### B8. `core` version semantics are undefined

Every dialect file has `"core": "0.6"`, but the plan never says what the runtime does with it:

- Is it an exact version, a minimum, or advisory?
- What if the file has an ID the runtime does not know?
- What if the runtime has IDs the file does not (fallback, or reject)?
- What if a 0.7 runtime loads a 0.6 file?

Define this before the schema is frozen. Suggested: `core` is the minimum catalogue version; unknown IDs are a hard error; missing newer IDs fall back to the parent with a warning; older files are accepted; newer-than-runtime files warn.

### B9. The parser currently depends on dialect words

The plan says "the parser never sees a Siulak word", but `kerincilang.py` interpolates `KEYWORDS[...]` into parser and runtime errors at lines 221, 229, 257, 262, 392, and `ev` compares token text to `KEYWORDS["AND"]` / `KEYWORDS["OR"]` at lines 910-915. The refactor must:

- make token payloads neutral (`AND`, not `ngan`), and
- move every user-facing string into `msg.*` with arguments.

Until then, the parser is dialect-dependent and the message catalogue cannot be complete.

### B10. The single-file build and the wheel will not contain dialects

`build.py:28` copies only `kerincilang.py` into the zipapp; `pyproject.toml:17-18` installs only that module. As soon as `dialects/` and `core/` are data files, `krc.pyz` and `pip install .` will fail at runtime.

Fix before phase 1 ends:

- Turn the interpreter into a package (`kerincilang/__init__.py`, `kerincilang/data/...`), or explicitly copy data into the zipapp and declare `package-data`.
- Resolve data with `importlib.resources` (3.9+) or a zip-safe path helper.
- Add a packaging test: build the pyz, run it from a temp directory with no repo checkout, in both dialects.

This is also what makes "adding a dialect means adding a file" true for end users, not just for developers running from the repo.

## 3. High-risk gaps

1. **Output dialect across modules.** `show()` is global. With mixed-dialect imports, which dialect's `betul` / `salah` / type words does a `nyetak` use? Decide "dialect of the module executing the print", carry it on `Env` or a runtime context, and apply it to `kato`, `disatu`, `mecem`, `<guno>`, and `<builtin name>`.
2. **Warning channel and dedupe.** If fallback warnings go to stdout, every one of the 550 `hasil` comparisons changes. Send them to stderr, once per ID per run, and define the `--ketat` exit code. Add a golden test for the warning text.
3. **Message catalogue size.** 61 raise sites / 59 templates, plus CLI and REPL. Generate the inventory from the code rather than hand-counting.
4. **Comparison words are phrases.** Siulak uses underscores (`lebih_daripado`); Koto Payang wrote spaces. Decide: join with `_`, allow multi-word lexing (maximal munch), or symbols only. Add a `kind` column (`word`, `syntax-pattern`, `example`) to the worksheet.
5. **Case and Unicode.** 167 answers start uppercase. Identifiers are case-sensitive. Define lowercase, NFC normalization, allowed character classes, and no leading digit; enforce all of it in validation.
6. **`type.bool` is blank.** `mecem(betul)` currently returns the English placeholder `boolean`, and the test asserts it (`tests/test_kerincilang.py:71-72`). Decide whether Koto Payang ships with an English fallback and whether the Siulak test changes.
7. **Reserved words.** `kelihu` is hardcoded at line 70. There is no `reserved.*` group. Other dialects need their own reserved word or an explicit "none".
8. **`bukak` default mode.** `Berkas.mode` stores a dialect word and `need_handle` compares words. Store a neutral `mode.*` internally and translate only at the API boundary; otherwise changing dialect mid-run breaks open handles.
9. **Tutorial axes.** `sinkron_tutorial.py:125` and `test_tutorial.py:20` both glob `tutorial/**/*.md`. A new `tutorial/src/` with `{{kw.if}}` placeholders will be executed and fail. Also `tutorial/id/` is a prose language, not a dialect. Separate the two axes (prose language × code dialect) or generate code-only files; `krc-berkas` helper files also need headers.
10. **CLI precedence.** The header wins, but does `--dialek` serve as a fallback for a file with no header, or only for `-c` / the REPL? Decision 5 says the header is required; make the precedence table explicit. Also decide the header key spelling, line-1 rule, shebang/BOM handling, and whether `--dialek` is checked before or after the file is read.
11. **Dialect loading security.** `--dialek ../../x` must not read arbitrary files. Validate `^[a-z0-9-]+$`, resolve under `dialects/`, cap file size, reject malformed JSON and duplicate keys, and never execute dialect content.
12. **Governance and licence.** The schema has `contributors` but decision 7 requires a maintainer and a reviewer in the file. The repo is MIT (`pyproject.toml`, `LICENSE`), while the plan says dialect data is CC BY-SA 4.0. Define the scope (code MIT, `dialects/` + `core/ids.json` CC BY-SA) and add `maintainer`, `reviewer`, `sources`, and status-transition ownership.
13. **Section 9 conflicts with "tests unchanged".** Newline termination, better syntax errors, and redeclaring a variable are behavior changes. If they land in 0.6, the 271 tests and 550 blocks will change. Defer them to 0.7 or update the phase 1 gate.
14. **"Identical output" is impossible.** True/false/null words, type names, and messages are dialect-specific by design. Compare normalized output (map words back to IDs) and compare errors by message ID plus arguments, not by raw text.
15. **`buat_glosarium.py` hardcodes vocabulary** and asserts full coverage. It must become dialect-driven; `docs/02-vocabulary-worksheet.md` is Siulak's decision log and should become `dialects/siulak.md` provenance, not be discarded.
16. **Test imports.** `tests/test_kerincilang.py:8` imports `KEYWORDS`. Keep a Siulak compatibility shim or update the tests deliberately; do not let the refactor silently change the public import surface.
17. **Translator scope.** "A name the user declared is never rewritten" requires symbol resolution. Imported modules make this cross-file. Either restrict the translator to one file in 0.6 or build a real symbol table.
18. **CI cost.** 5 Python versions × 550 blocks × N dialects. Run the full dialect matrix on 3.12 and a smoke subset on the rest.

## 4. Koto Payang worksheet audit

What is usable:

- The speaker understood the task and supplied a complete Tier 1 pass in principle.
- The orthography is visibly consistent in its use of final `u` (`kalu`, `selamu`, `daling`, `baluikka`) and `nga` for "and".
- Several answers are clean single words: `kalu`, `ndik`, `selamu`, `daling`, `slese`, `baluikka`, `jeloehka`, `cocokka`, `iduak`, `nga`, `betiu`, `kusao`, `cubea`, `kecuali`, `timbaoka`, `panja`, `rentang`, `terurut`, `tebaluik`, `tambahka`, `pecah`, `basatau`, `bukuak`, `bacea`, `tulaih`, `tutamp`.

What must be fixed:

1. Normalize spaces to a single identifier (probably `_`) or change the lexer to allow phrases.
2. Lowercase all answers; decide whether capitalized forms are aliases.
3. Resolve alternatives (`impor/masukka`, `daftar/lis`, `bilangan bakoma/bilangan desimal`).
4. Translate the untranslated Tier 1 rows (`Awal blok kode`, `Akhir blok kode`) or mark them "use symbol".
5. Fill `bool` or mark it "no word; use English fallback".
6. Restore the notes column.
7. Re-ask the message rows with placeholders locked.
8. Add the missing `id` column and map each row to a `core/ids.json` ID.
9. Separate syntax patterns (`elif`, block markers) from single words.
10. Record the spelling rules in `dialects/koto-payang.md` before the next pass.

## 5. Recommended plan edits

1. Add a **Contracts** section: `core/ids.json` schema, dialect JSON schema, clash matrix, message placeholder rules, `core` version semantics.
2. Replace validation rules 3 and 4 with the namespace-aware matrix in B1.
3. Add **packaging** to phase 1 (B10); it is not a release-time concern.
4. Add a **`dialect-siulak-legacy`** module that freezes the 0.5 vocabulary so old programs, tests, and the tutorial keep working while Siulak is re-reviewed later.
5. Make **CSV canonical**, DOCX generated, and add a normalization + speaker-confirmation step (B4, B5).
6. Add `id`, `tier`, `namespace`, and `kind` columns; restore notes; add a `core/future.json` for Tier 3.
7. Add **placeholder validation** and make placeholders read-only (B6).
8. Define **warning channel, dedupe, and `--ketat`** (G2).
9. Define the **API split**: header for files, explicit dialect for `run_source` (B3).
10. Define the **output dialect** rule for mixed imports (G1).
11. Defer section 9 to 0.7 or accept test churn (G13).
12. Change equivalence tests to **normalized output** (G14).
13. Define the **translator lossless policy** (B7).
14. Add **dialect loading security** rules (G11).
15. Add a **packaging test** (B10).
16. Fix the **licence scope** and schema fields (G12).

## 6. Recommended first milestone

For the "Koto Payang first, other dialects and completed Siulak later" scope:

1. `core-ids` - neutral catalogue and interpreter refactor, with Siulak compatibility shims.
2. `dialect-model` - schema, loader, fallback, validation, completeness report.
3. `runtime-selection` - header, `--dialek`, per-module scopes, output words, messages, warnings.
4. `worksheet-pipeline` - canonical CSV, DOCX view, normalizer, placeholder checks.
5. `dialect-koto-payang` - normalized Koto Payang file, Tier 1 complete, reviewed.
6. `dialect-siulak-legacy` - frozen 0.5 vocabulary, draft status.
7. `cli-migration` - `krc migrasi`, precedence, REPL/-c, import recursion.
8. `translator` and `tutorial-multidialect` - after the first six are green.

The plan's phase 4 ("first dialects") shrinks to one dialect plus the frozen legacy one; that is the right trade for this round.

## 7. Decisions needed

See `SPEC.md` section "Open Questions". The blocking ones are:

1. First-release scope: Koto Payang only, with Siulak frozen as legacy draft?
2. Is the Koto Payang worksheet a first draft requiring a normalization pass?
3. How are multi-word concepts represented: underscore-joined identifiers, multi-word lexing, or symbols only?
4. Do the 271 tests and 550 blocks stay unchanged (freeze Siulak 0.5), or do they change with a Siulak re-review?
5. Are message placeholders neutral English (`{name}`, `{message}`) and re-asked, or translated?
6. Is CC BY-SA 4.0 limited to `dialects/` and `core/ids.json`, with code staying MIT?
7. Is section 9 deferred to 0.7?
8. Is the dialect code `koto-payang`?
