# Plan: runtime-selection

Module: `runtime-selection`. Spec: `SPEC-runtime-selection.md` (approved 2026-11-02).
Depends on `dialect-model` (commit `60f9335`).

Goal: a program chooses its dialect per file. `# dialek: koto-payang` on line 1,
`--dialek` as the default, Siulak when nothing is declared. A function keeps the
dialect it was written in.

The oracle is unchanged: `tests/test_kerincilang.py` (271),
`tests/test_tutorial.py` (550), `tests/test_ids.py`, `tests/test_dialects.py`.
None may be edited.

## Order

1. **Catalogue** - add three Tier 2 messages to `core/ids.json`:
   `msg.dialect.header`, `msg.dialect.unknown`, `msg.dialect.invalid`, with
   neutral placeholders. `test_ids.py` keeps the catalogue honest.

2. **Header** - `dialect_header(src)` reads line 1 only. A matching line returns
   the code; a `#` line containing `dialek` that does not match raises
   `msg.dialect.header`; everything else is `None`. The lexer stays untouched
   because the header is already a comment.

3. **Run context** - `RunContext` (default vocab, `dialect_root`, strict flag,
   dialect cache, warned set, strict failure). Pushed by `run_file`/`main`,
   created on demand by a bare `run_source`, so the public API keeps working.

4. **Resolver** - `resolve_source_vocab(src, context)`: header wins, else the
   context default. The loader is imported lazily inside the resolver (no
   circular import). `missing` -> `msg.dialect.unknown`; any other
   `DialectError` -> `msg.dialect.invalid` with the first problem.

5. **Per-call vocabulary** - `ev()`'s call branch wraps the body in
   `use_vocab(closure_env.vocab)`. Nested cross-dialect calls push and pop, so
   output, `mecem`, file modes, and errors follow the executing module.

6. **Imports** - `do_import` resolves the imported file's header before running
   it and builds that module's globals with its own vocabulary. A module is
   cached by path per run, as today.

7. **CLI** - `--dialek CODE` and `--ketat`. `--dialek` loads once, before the
   run; a failure exits 2. `--ketat` checks the selected dialect before the
   program starts, and later-loaded dialects as they load; any failure exits 2.
   `USAGE` gains both flags.

8. **Warnings** - `warn_fallback(code, id, kind, word)` prints to stderr once per
   `(dialect, id)` per run. English, never fatal, no catalogue ID.

9. **Tests** - `tests/test_runtime_selection.py`: every positive and negative in
   spec section 12, with temp dialect JSONs and `dialect_root`.

10. **Docs** - `docs/04-implementation.md` and `docs/03-syntax-design.md` record
    the header and precedence; the spec is marked implemented.

## Verification

- `python tests/test_runtime_selection.py` -> all pass.
- The other four suites, unchanged and green.
- `python tools/cek_dialek.py --semua` -> exit 0.
- `python tools/buat_glosarium.py`, `python make_highlight.py` -> no diff.
- `python build.py`, then `dist/krc.pyz` from a temp directory.
- `python -m compileall -q .`.

## Risks

- Per-call vocabulary changes the engine's call path; every existing test must
  stay byte-identical. `use_vocab` is a stack, so push/pop must be paired even
  when a call raises (`finally`).
- `LOADED` must stay keyed by path: the run default is constant, so a file's
  dialect is fixed for the run.
- A malformed header must be an error, not a silent comment, or a typo would run
  Siulak without telling anyone.
- `--ketat` must never weaken to a warning, and must not change output of the
  program itself.
- Warning text is not a language message; it must not enter `core/ids.json`.
