# Spec: runtime-selection

Status: **draft for approval.** Parent: `SPEC.md`. Capability map:
`runtime-selection`.
Depends on: `dialect-model` (implemented, commit `60f9335`). Date: 2026-11-02.

## 1. Objective

Let a program choose its dialect at run time, per file, without changing a single
Siulak 0.5 program.

After this module:

- A file can start with `# dialek: koto-payang`.
- `krc --dialek koto-payang` selects the default for files that declare nothing.
- An imported file may use a different dialect from its importer.
- A function keeps the dialect it was written in when it is called from another.
- A selected dialect that falls back to the base is reported on stderr, and
  `--ketat` makes an incomplete `approved` dialect a failure.
- No header means Siulak, so the 271 + 550 cases stay byte-identical.

## 2. Scope

### In scope

- The `# dialek:` header and its validation.
- Precedence: header, then `--dialek`, then Siulak.
- `--dialek` for a file, `-c`, and the REPL.
- `--ketat`.
- Per-module and per-call vocabulary context.
- Fallback warnings and their deduplication.
- `tests/test_runtime_selection.py`.
- Three new catalogue messages.

### Out of scope

- `dialects/siulak.json` (`dialect-siulak-legacy`).
- `dialects/koto-payang.json` (`dialect-koto-payang`).
- Worksheet generation, `krc migrasi`, `krc terjemah`.
- A dialect picker UI, `--daftar-dialek`, per-line dialect switches.
- Changing any existing message text or Siulak output.

## 3. The header

The **first line** of a source may be:

```
# dialek: koto-payang
```

Rules:

| Case | Result |
|---|---|
| Line 1 matches `^#\s*dialek\s*:\s*([a-z0-9-]+)\s*$` | that code is the file's dialect |
| Line 1 starts with `#` and contains `dialek` but does not match | `msg.dialect.header`, with the line text |
| Anywhere else | an ordinary comment; ignored |
| Line 1 is anything else | no header |

The header stays a comment for the lexer, so `tokenize()` is untouched. A file
with no header uses the run's default.

The code is validated by `load_dialect`, so `# dialek: ../x` fails the code
pattern and is reported as `msg.dialect.header`.

## 4. Precedence (decision D1)

```
per-file header   >   --dialek   >   Siulak (LegacySiulak)
```

- The header is the file's own declaration and always wins for that file.
- `--dialek` is the **default** for files that declare nothing. It is how the
  REPL, `-c`, and headerless projects choose a dialect.
- Siulak remains the default so every existing program keeps running.

A headerless file imported by another file also uses the run default, **not** the
importer's dialect (decision D3). Mixed-dialect projects declare a header where
they need one. This keeps `LOADED` keyed by path and makes a file's dialect a
property of the file alone.

## 5. Per-module and per-call context (decision D4)

Output words belong to the code that is running, not to the value:

| Site | Vocabulary used |
|---|---|
| `nyetak` / `show()` | the module running the statement |
| `mecem()` | the module calling it |
| `bukak(path, "baco")` | the module passing the mode word |
| an error message | the module that raised it (rendered at construction) |
| a function body | the module that **defined** the function |

A function value already carries its defining `Env`; `Env.vocab` is inherited from
it, so a call can push that vocabulary with `use_vocab` for the duration of the
body. Nested calls push again, so A -> B -> A restores correctly.

`new_global(vocab)` already registers built-ins under that vocabulary's words, so
a module's globals refer to its own names.

Unchanged by design: a returned value is printed by the caller's words. `betul`
returned by a Koto Payang function and printed in Siulak is `betul` (the same
value); a `type.*` name is produced where `mecem` is called.

## 6. Run context

One `RunContext` per invocation:

```python
class RunContext:
    default_vocab      # Vocabulary for files without a header
    dialect_root       # test-only override for `dialects/`
    strict             # --ketat
    cache              # code -> Dialect, loaded once per run
    warned             # {(code, id)} already printed
    strict_failed      # an approved dialect was incomplete
```

It is pushed on a stack by `run_file`/`main` and restored afterwards, the same
pattern as `use_vocab`. A bare `run_source()` call creates a one-shot context so
the public API keeps working.

The loader is imported lazily inside the resolver, never at module import time,
because `dialects.loader` imports `kerincilang` (decision D8).

## 7. CLI (decision D6)

```
krc --dialek koto-payang program.krc
krc --dialek koto-payang -c 'nyetak "halo"'
krc --dialek koto-payang                # REPL
krc --ketat --dialek koto-payang program.krc
```

| Situation | Exit |
|---|---|
| normal run | 0, or 1 on a program error (unchanged) |
| `--dialek` missing a value, or an unknown flag | 2 |
| the selected dialect does not exist, or fails validation | 2, before running |
| header names a missing or invalid dialect | 1 (a program error) |
| `--ketat` and an `approved` dialect has a Tier 1 base fallback | 2 |

`--ketat` checks the selected dialect before the program starts. A dialect loaded
later from an imported file is checked as it loads; if the program is already
running it finishes, then the exit code is 2. A failure is never silent.

`USAGE` gains the two flags and one example.

## 8. Warnings (decision D5)

When an ID resolves from the base instead of the dialect or a parent, print one
line to **stderr**:

```
warning: dialect koto-payang: kw.in falls back to the base word "in"
warning: dialect koto-payang: msg.value.div_zero falls back to the base message
```

- Once per `(dialect, id)` per run. A loop that prints a boolean a thousand times
  warns once.
- Warnings are toolchain output, not language messages: English, no catalogue ID.
  They are for the person maintaining the dialect.
- They never change the exit code. `--ketat` is the gate (section 7).
- `--ketat` pre-checks the selected dialect, so a complete dialect stays quiet.

## 9. API

```python
run_source(src, env=None, vocab=None, *, dialect_root=None)
run_file(path, env=None, vocab=None, *, dialect_root=None)
main(argv=None, dialect_root=None)

resolve_source_vocab(src, context)   # header -> vocab for this source
current_context()                    # the active RunContext
```

`dialect_root` is a developer/test argument, never a CLI value, matching
`load_dialect(root=...)`.

`DialectError` from a header is converted to `LangError`:

| `DialectError.code` | `LangError` message |
|---|---|
| `missing` | `msg.dialect.unknown` (`{code}`) |
| anything else | `msg.dialect.invalid` (`{code}`, `{detail}`) |

## 10. New catalogue messages (decision D7)

| ID | `id_gloss` (Indonesian) | `en` | Placeholders |
|---|---|---|---|
| `msg.dialect.header` | `Baris {line}: header dialek tidak valid: {text}` | `Line {line}: invalid dialect header: {text}` | `line`, `text` |
| `msg.dialect.unknown` | `Dialek tidak dikenal: {code}` | `Unknown dialect: {code}` | `code` |
| `msg.dialect.invalid` | `Dialek {code} tidak valid: {detail}` | `Dialect {code} is not valid: {detail}` | `code`, `detail` |

These are new Tier 2 text and are marked for the next speaker pass. Their
placeholders follow the neutral-name rule. `tests/test_ids.py` already checks
placeholder agreement, so the catalogue stays consistent.

## 11. Boundaries

### Always

- Default to Siulak when nothing is declared.
- Validate a header, never ignore a malformed one.
- Keep the dialect of a function attached to the function.
- Warn once per `(dialect, id)` per run.
- Keep `dialect_root` out of the command line.

### Ask first

- Changing the precedence order.
- Allowing a header on any line other than the first.
- Making a headerless import inherit the importer's dialect.
- Adding a `--daftar-dialek` command.
- Changing warning language or format.

### Never

- Break a headerless program's output.
- Execute dialect data.
- Let a missing dialect fall back to Siulak silently.
- Print the same warning once per loop iteration.
- Add a per-dialect Python file.

## 12. Testing (`tests/test_runtime_selection.py`)

Fixtures are temp dialect JSON files; `dialect_root` points the run at them.

Positive:

1. A headerless program still runs in Siulak, byte-identical.
2. A header selects a temp dialect and its words appear in output.
3. `--dialek` sets the default for a headerless file.
4. A header wins over `--dialek`.
5. An imported file's header selects its dialect; the importer keeps its own.
6. A function from dialect B prints B's words when called from A.
7. `mecem` inside B returns B's type words.
8. An error raised inside B uses B's message.
9. `# dialek:` on line 2 is an ordinary comment.
10. `--ketat` passes a complete approved dialect.
11. `--ketat` exits 2 for an approved dialect with a Tier 1 gap.
12. `--ketat` exits 2 for an imported approved dialect with a gap, after the run.
13. Warnings are printed once for a loop, and a clean dialect prints none.
14. `--dialek hantu` exits 2 before running.

Negative: a malformed header, an unknown header code, an invalid dialect file,
and a header code that fails the pattern each produce their message.

Also: `tests/test_kerincilang.py`, `test_tutorial.py`, `test_ids.py`, and
`test_dialects.py` stay green and unchanged.

## 13. Success criteria

1. `# dialek: koto-payang` on line 1 changes the words of that file only.
2. Precedence is header > `--dialek` > Siulak, with a test per level.
3. A cross-dialect call prints in the callee's words and restores the caller's.
4. `--ketat` returns 2 exactly for the documented cases.
5. Warnings are stderr-only, once per `(dialect, id)` per run, and never change
   the exit code.
6. All existing suites stay green, unedited.
7. `python -m compileall -q .` passes; `dist/krc.pyz` still runs from a temp
   directory.

## 14. Decisions

| # | Decision | Recommendation |
|---|---|---|
| D1 | Precedence is per-file header > `--dialek` > Siulak. | Yes; the header describes the file. |
| D2 | The header is line 1 only; a malformed one on line 1 is an error. | Yes; a typo must not silently run Siulak. |
| D3 | A headerless import uses the run default, not the importer's dialect. | Yes; a file's dialect stays a property of the file. |
| D4 | Per-call vocabulary: a function body runs in its defining dialect. | Yes; otherwise a library's output changes with its caller. |
| D5 | Warnings are English, stderr, once per `(dialect, id)` per run, never fatal. | Yes; they are toolchain output. |
| D6 | A bad `--dialek` is a configuration error, exit 2. | Yes; matches a missing file. |
| D7 | Three new `msg.dialect.*` IDs, flagged for speaker review. | Yes; the catalogue stays the only source of text. |
| D8 | `dialect_root` is a test-only keyword; the loader is imported lazily. | Yes; no circular import, no CLI path. |

## 15. Next step

On approval: write `tasks/plan.md` and `tasks/todo.md` for `runtime-selection`,
then implement. `worksheet-pipeline` and `dialect-siulak-legacy` follow, then
`dialect-koto-payang`.
