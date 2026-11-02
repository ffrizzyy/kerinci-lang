# Todo: runtime-selection

Each item is done only when the listed check passes.

- [x] T1 Three `msg.dialect.*` IDs in `core/ids.json`; `test_ids.py` green.
- [x] T2 `dialect_header(src)` accepts line 1, rejects a malformed one, ignores
      later lines.
- [x] T3 `RunContext` + `current_context()`; a bare `run_source()` still works.
- [x] T4 `resolve_source_vocab`: header > default; the loader is imported lazily.
- [x] T5 A header error becomes `msg.dialect.header` / `unknown` / `invalid`.
- [x] T6 A call pushes its closure's vocabulary and restores the caller's, even
      on error.
- [x] T7 `do_import` gives each module its own vocabulary.
- [x] T8 `--dialek` works for a file, `-c`, and the REPL; a bad value exits 2.
- [x] T9 `--ketat` exits 2 for an approved Tier 1 gap, including an imported
      dialect.
- [x] T10 Warnings are stderr, once per `(dialect, id)` per run, never fatal.
- [x] T11 `USAGE` documents both flags.
- [x] T12 `tests/test_runtime_selection.py` covers spec section 12.
- [x] T13 `tests/test_kerincilang.py` 271/271, `test_tutorial.py` 550 blocks,
      `test_ids.py` and `test_dialects.py` all pass. Only `test_dialects.py`'s
      base tier-2 total moved 101 -> 104 for the three approved IDs; no program
      expectation changed.
- [x] T14 `cek_dialek.py --semua` exits 0; both generators produce no diff;
      `build.py` and `dist/krc.pyz` work from a clean temp directory.
- [x] T15 Docs updated; spec marked implemented; `CAPABILITY-MAP.md` points at
      the next module.
- [x] T16 `python -m compileall -q .` passes.

## Follow-ups (not part of runtime-selection)

- `worksheet-pipeline`: generate the normalization worksheet from the docx.
- `dialect-siulak-legacy`: freeze Siulak as `dialects/siulak.json` (`draft`).
- `dialect-koto-payang`: the first real non-Siulak dialect.
- `cli-migration`: `krc migrasi`, precedence table, import recursion.
- `type.bool` still renders `boolean` in Siulak until a speaker review.
