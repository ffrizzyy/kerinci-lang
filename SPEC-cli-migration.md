# Spec: cli-migration

Status: **implemented 2026-11-02.** Parent: `SPEC.md`. Capability map:
`cli-migration`.
Depends on: `runtime-selection` (implemented) and `dialect-koto-payang`
(implemented). Date: 2026-11-02.

## 1. Objective

Give existing v0.5 programs a one-command, safe path to an explicit dialect
header, and finish the CLI contract that `runtime-selection` left open.

After this module:

- `krc migrasi FILE` adds `# dialek: siulak` as line 1 and recurses into the
  file's literal `ambik` imports.
- `krc migrasi DIR --semua` migrates every `.krc` under a directory.
- Re-running is a no-op: a file that already has a valid header is never
  rewritten.
- `--kering` reports what would change without writing.
- The command is idempotent, never executes the program, and refuses to touch a
  file it cannot migrate safely.
- `krc migrasi` works from a checkout, an installed wheel, and `dist/krc.pyz`.
- The CLI precedence, exit codes, `-c`, REPL, and `--help` are documented in
  one table and tested, so there is no second interpretation.

The old v0.5 examples gain their headers during this module, and their output
does not change.

## 2. Scope

### In scope

- `krc migrasi` and its option parsing, recursion, reporting, and exit codes.
- Header detection and safe, byte-preserving insertion.
- Static import discovery (literal `ambik "path"` only).
- `MIGRASI_USAGE`, the main `USAGE`, `--help`, and `krc migrasi --help`.
- Tightening CLI usage errors: unknown flags, extra arguments, `-c` without
  code.
- Migrating `examples/*.krc` and keeping their output identical.
- `tests/test_migration.py`.
- Doc updates for the command and the CLI table.

### Out of scope

- Making a header mandatory at runtime. `runtime-selection` D1 settled that a
  headerless file uses `--dialek`, then Siulak. Migration is opt-in.
- Changing the header syntax, the loader, the catalogue, or any Siulak word.
- Translating the CLI/REPL text into the message catalogue. That is a separate
  change to `core/ids.json` and every dialect.
- `krc terjemah` (`translator`), tutorial generation, or a dialect picker.
- Running or evaluating a program to discover imports.
- Following computed import names (`ambik nama`); they are reported, not
  guessed.
- Rewriting imports, adding blank lines, re-indenting, or normalizing content.
  The only write is a prefix.
- Formatting or fixing a file that does not parse.

## 3. Command

```bash
krc migrasi BERKAS...
krc migrasi DIR --semua
krc migrasi BERKAS... --dialek koto-payang
krc migrasi BERKAS... --kering
krc migrasi --help
```

`migrasi` is a subcommand and must be the first argument:

| Form | Meaning |
|---|---|
| `krc migrasi a.krc b.krc` | migrate these files and their literal imports |
| `krc migrasi examples --semua` | migrate every `.krc` under `examples/` |
| `--dialek KODE` | header to add; default `siulak` |
| `--kering` | report only; write nothing |
| `--help`, `-h` | print migration usage, exit 0 |

Rules:

- `--semua` and explicit files are mutually exclusive. With `--semua`, exactly
  one target directory is required.
- An explicit target must be a `.krc` file. A directory is only valid with
  `--semua`.
- Options may appear before or after the targets within the `migrasi`
  subcommand. The first `--help` short-circuits.
- An unknown option, a missing option value, no target, or a bad target is a
  usage error (exit 2) before any write.
- `--dialek CODE` is validated with `resolve_dialect` before any write. A
  missing or invalid dialect exits 2 and nothing is modified. `siulak` still
  resolves to `LegacySiulak` when its file is unavailable, matching runtime.
- `krc migrasi` never accepts `--ketat`; strictness is a run-time concern.

## 4. Header detection and writing

For each file, the whole file is read as bytes and decoded as UTF-8.

| Line 1 state | Action |
|---|---|
| valid `# dialek: CODE` | skip the write; still scan its imports |
| starts with `#` and contains `dialek` but is malformed | refuse: per-file error, no write |
| a UTF-8 BOM is present | refuse: per-file error, no write |
| anything else | migrate: prepend the header |

The header is exactly `# dialek: <code>` and is inserted **before every byte of
the original file**. No blank line is added. The rest of the file is preserved
verbatim, including comments, trailing whitespace, and a missing final newline.

The inserted line ending is the first newline sequence found in the file
(`\r\n` or `\n`); a file with no newline gets `\n`. A CRLF file stays CRLF.

The write is atomic: a temporary file in the same directory is written and
`os.replace()`d over the original. A failed write leaves the original untouched
and is a per-file error.

`dialect_header()` remains the runtime authority for line 1. Migration uses the
same `HEADER_HINT_RE` / `HEADER_RE` idea, so a line the runtime would reject is
never silently buried under a new header.

## 5. Import recursion

A program is migrated together with the files it imports, because a headerless
import is the same problem as a headerless main file.

Algorithm:

1. Start from the explicit targets, or from every `.krc` under the `--semua`
   directory (sorted, recursive, skipping `__pycache__` and `.git`).
2. Visit each real path at most once per invocation (a visited set normalizes
   `a`, `./a`, and `a.krc`).
3. Read and inspect line 1 (section 4).
4. Parse the file **without executing it** with its effective dialect: the
   existing header if present, otherwise the `--dialek` code (default
   `siulak`). Use `tokenize` + `Parser(...).program()`.
5. Collect every `("import", expression)` node anywhere in the AST. Import
   statements inside blocks or functions still count because they can run.
6. For `("import", ("lit", "name"))`, resolve `name` exactly like `do_import`:
   relative to the importing file, the exact path first, then `name + ".krc"`.
   Recurse into the found file.
7. For any other import expression, report `cannot follow a non-literal import`
   and mark the run failed (exit 1). The file itself is still migrated.
8. A literal import that does not resolve is reported and marks the run failed;
   the importing file itself is still migrated. The user can fix the path and
   re-run; the command is idempotent.
9. Parse errors, an unknown header dialect, a malformed header, and a BOM are
   per-file errors: that file is not written, and its imports are not scanned
   through it. Other files continue.

A cycle is not a special error: the visited set breaks it, and the runtime's
`msg.import.circular` remains the runtime's job. Migration does not validate
that the program runs, only that it can be parsed and its imports followed.

## 6. Reporting and exit codes

Migration output is **toolchain text**, in English, like `cek_dialek.py` and
`lembar_kerja.py`. It is not program output and not a `msg.*` catalogue entry.
stdout stays reserved for the program only when a program runs; `migrasi` is a
tooling command.

One line per file on stdout:

```text
migrasi: added header to examples/contoh.krc
migrasi: already has a header: examples/perkakas.krc
migrasi: would add header to examples/baru.krc
```

Errors go to stderr:

```text
migrasi: error: examples/buruk.krc: line 1 declares a malformed dialect header
migrasi: error: examples/impor.krc: cannot follow a non-literal import
migrasi: error: examples/main.krc: import not found: lib
```

A final summary goes to stdout:

```text
migrasi: 3 migrated, 1 already had a header, 0 errors
```

With `--kering`, `migrated` becomes `would migrate` and no file is written.

| Situation | Exit |
|---|---|
| every target succeeded, including already-headered files | 0 |
| at least one per-file error (BOM, malformed header, parse error, unknown header dialect, unresolved/dynamic import, read/write failure) | 1 |
| usage error (unknown option, missing value, no target, both `--semua` and a file, a non-`.krc` target) | 2 |
| `--dialek` code missing or invalid, checked before any write | 2 |
| a target path does not exist, or a `--semua` target is not a directory | 2 |

`--kering` with a per-file error still exits 1.

## 7. CLI precedence, `-c`, REPL, and `--help`

This module does not change the `runtime-selection` behavior. It documents and
tests it:

| Invocation | Dialect source |
|---|---|
| `krc FILE` | line 1 header, else `--dialek`, else Siulak |
| `krc --dialek CODE FILE` | line 1 header wins over `--dialek` |
| `krc -c "..."` | `--dialek`, else Siulak |
| `krc --dialek CODE -c "..."` | `--dialek` |
| `krc` (REPL) | `--dialek`, else Siulak |
| an imported file | its own header, else the run default (not the importer) |

`SPEC.md` section 5 says `krc FILE` "never" uses `--dialek` and that `-c`/REPL
"require the flag". Those lines conflict with the approved `runtime-selection`
D1 precedence and with the requirement that `krc -c` keeps working. This module
treats the table above as authoritative: the header wins when present, and
`--dialek` is the default for headerless files, `-c`, and the REPL. Siulak stays
the default, so every v0.5 invocation keeps working. The parent spec's intent is
kept: no file's own header is ever overridden by the flag.

CLI cleanup in this module:

- An unknown option (an argument starting with `-` that is not `-c`, `-h`,
  `--help`, `-V`, `--version`, `--dialek`, `--dialek=`, or `--ketat`) is a usage
  error (exit 2), not a filename.
- More than one positional argument for a normal run is a usage error. `-c`
  takes exactly one code argument.
- `-c` without a code stays exit 2.
- A missing file, a non-UTF-8 file, and an unknown `--dialek` stay exit 2. A
  program error, including a malformed header, stays exit 1.
- `USAGE` gains the `migrasi` line; `--help` still exits 0.

## 8. Examples

`examples/*.krc` are migrated with:

```bash
python kerincilang.py migrasi --semua examples
```

All eight files gain `# dialek: siulak` as line 1. `contoh-impor.krc` and
`perkakas.krc` both get the header, so the import is explicit too. Running each
example before and after produces the same stdout. No example is otherwise
edited.

`build.py` copies the migrated examples to `dist/` as before; no packaging
change is needed because `migrasi` lives in `kerincilang.py`.

## 9. Tests: `tests/test_migration.py`

Plain-Python style, all work in `tempfile.TemporaryDirectory()`.

1. **Single file.** A headerless program gains `# dialek: siulak\n` as line 1;
   the original bytes follow unchanged; the migrated file runs and prints the
   same output.
2. **Idempotence.** A second run reports "already has a header", exits 0, and
   leaves the bytes identical.
3. **Imports.** A main file imports `lib` (no extension); both gain headers;
   the migrated main still runs and shares the module's names.
4. **Recursive import.** `a` imports `b`, `b` imports `c`; all three gain
   headers; a shared file reached twice is visited once.
5. **`--semua`.** A nested tree with `.krc` and non-`.krc` files: every `.krc`
   is migrated, non-`.krc` files are untouched, order is deterministic.
6. **`--dialek koto-payang`.** A headerless `nytak ...` program gains
   `# dialek: koto-payang`, and the migrated file runs with no `--dialek` flag.
   A headerless import is parsed with the same default.
7. **`--kering`.** Reports "would add header", writes nothing, exits 0.
8. **Refusals.** A BOM, a malformed line-1 header, a syntax error, an unknown
   header dialect, a non-literal import, and a missing literal import are each
   reported; the affected file is unchanged; the exit code is 1. A parse-error
   file does not get a header.
9. **Line endings and preservation.** A CRLF file gains a CRLF header; a file
   with no final newline keeps that property; comments and content are
   byte-identical after the prefix.
10. **Usage.** No target, both `--semua` and a file, `--semua` on a file,
    non-`.krc` explicit target, unknown option, and `--dialek hantu` all exit 2
    with no writes. `migrasi --help` exits 0 and documents the flags.
11. **Packaging.** A zipapp containing `kerincilang.py`, `core/`, `dialects/`,
    and a `__main__.py` runs `migrasi` from a directory with no checkout and
    exits 0.
12. **Examples.** Every `examples/*.krc` starts with a valid header, and
    `contoh-impor.krc` runs with its expected output.
13. **CLI table.** Header beats `--dialek`; `--dialek` is the default for a
    headerless file, `-c`, and the REPL; an imported headerless file uses the
    run default. Unknown flags and extra arguments exit 2.

## 10. Boundaries

### Always

- Add exactly one line and preserve the rest of the file byte for byte.
- Follow literal imports recursively; report what cannot be followed.
- Keep migration idempotent and atomic.
- Keep `krc migrasi` out of program execution: parse only.
- Keep the existing suites, expected outputs, and tutorial blocks unchanged.
- Keep toolchain output on stdout/stderr separate from program output.

### Ask first

- Making a header mandatory at runtime.
- Changing `--dialek` precedence, the header syntax, or the default dialect.
- Following computed imports by executing code.
- Rewriting file content beyond the header prefix.
- Adding catalogue IDs for CLI text.
- Changing the Siulak freeze or a Koto Payang answer.

### Never

- Execute the program to discover imports.
- Add a header above a malformed header, a BOM, or a syntax error.
- Rewrite a file that already has a valid header.
- Invent an import path from a variable or a guess.
- Format, re-indent, normalize, or re-encode the original content.
- Change a test expectation, tutorial output, or Siulak word to make this pass.

## 11. Success criteria

1. `krc migrasi FILE` adds `# dialek: siulak` to the file and every literal
   import; the migrated program prints the same output.
2. A second run changes no bytes and exits 0.
3. `krc migrasi --semua DIR` migrates a whole tree; `--kering` writes nothing.
4. `--dialek koto-payang` writes that header and the migrated file runs without
   a flag.
5. A BOM, malformed header, parse error, unknown header dialect, or unfollowable
   import is reported, leaves the file untouched, and exits 1.
6. Usage errors exit 2 before any write; an unknown `--dialek` exits 2.
7. `krc migrasi` works in `dist/krc.pyz` and the installed wheel.
8. All nine suites are green; `examples/*.krc` carry headers; docs and
   `CAPABILITY-MAP.md` mark the module implemented.

## 12. Decisions

| # | Decision | Recommendation |
|---|---|---|
| D1 | Default header code is `siulak`; `--dialek` overrides the default. | Yes: v0.5 programs are Siulak. |
| D2 | Headerless files remain valid at runtime; migration is opt-in. | Yes: `runtime-selection` D1; no regression. |
| D3 | `-c` and the REPL keep Siulak as the default; `--dialek` is optional. | Yes: keeps `krc -c` and the REPL working; documents the parent-spec conflict. |
| D4 | Only literal `ambik "path"` imports are followed. | Yes: no execution, no guessing. A dynamic import fails the run. |
| D5 | Migration output is English toolchain text, not a `msg.*` entry. | Yes: no catalogue or dialect churn. |
| D6 | Refuse BOM, malformed header, and parse errors instead of repairing. | Yes: no silent content changes. |
| D7 | Prefix-only, byte-preserving, atomic writes. | Yes: the smallest possible diff. |
| D8 | Migrate `examples/` as the worked example. | Yes: the parent spec asks for it. |
| D9 | Implement `migrasi` in `kerincilang.py`. | Yes: it works in the wheel and zipapp without a packaging change. |

## 13. Next step

On approval: archive the current plan/todo, write `tasks/plan.md` and
`tasks/todo.md`, implement `migrasi` and the CLI cleanup, add
`tests/test_migration.py`, migrate `examples/`, then run all nine suites,
`cek_dialek --semua`, the generators, `compileall`, `build.py`, and
`dist/krc.pyz` from a temp directory. Update the docs and the capability map.

## 14. Implementation log

Implemented 2026-11-02 as specified.

- `kerincilang.py` now dispatches `migrasi`, parses the subcommand, and adds
  the header recursively. `migrasi` stays in the engine, so the wheel and
  `dist/krc.pyz` need no packaging change.
- `--dialek` defaults to `siulak`; `--semua`, `--kering`, and
  `migrasi --help` work as specified. `USAGE` documents the subcommand.
- The CLI now rejects unknown options, extra positional arguments, and a `-c`
  without a code with exit 2. `-h`, `--help`, `-V`, and `--version` remain
  valid.
- Writes are prefix-only and atomic; CRLF and a missing final newline are
  preserved. BOMs, malformed headers, parse errors, and unknown header
  dialects are refused without touching the file.
- Literal `ambik` imports are parsed, not executed, and followed by real path;
  dynamic and missing imports are reported with exit 1.
- All eight `examples/*.krc` gained `# dialek: siulak`; their output is
  unchanged. A second `migrasi --semua examples` reports eight skips.
- `tests/test_migration.py` has 91 checks covering the thirteen groups,
  including the zipapp, the examples, and the CLI precedence table.
- All nine suites are green; `cek_dialek --semua`, both generators,
  `compileall`, `build.py`, and `dist/krc.pyz migrasi` from a temp directory
  pass.
- No catalogue, dialect, loader, or worksheet file changed. No existing test
  expectation changed.
