# Todo: core-ids

Each item is done only when the listed check passes.

- [ ] T1 `core/ids.json` exists, parses, and covers the full inventory.
      Check: `tests/test_ids.py` catalogue cases.
- [ ] T2 `core/__init__.py` and `dialects/__init__.py` exist (data packages).
- [ ] T3 `Vocabulary` + `LegacySiulak` + `current_vocab`/`use_vocab` in place.
- [ ] T4 `LangError` carries `msg_id`/`args` and renders at construction.
- [ ] T5 Lexer emits neutral token kinds and symbol text for `op.*`.
- [ ] T6 Parser compares IDs only; `display()` used for error text.
- [ ] T7 Runtime: `Env.vocab`, `show(v, vocab)`, `new_global(vocab)`,
      builtins by `fn.*`, modes by `mode.*`, `mecem` by `type.*`.
- [ ] T8 No f-string / literal user message left in the engine (AST scan).
- [ ] T9 Compatibility exports generated from `LegacySiulak`, same keys/values.
- [ ] T10 `tests/test_kerincilang.py` 271/271, unchanged.
- [ ] T11 `tests/test_tutorial.py` 550 blocks, unchanged.
- [ ] T12 `tools/buat_glosarium.py` and `make_highlight.py` produce no diff.
- [ ] T13 `build.py` and `pyproject.toml` ship `core/` + `dialects/`.
- [ ] T14 `dist/krc.pyz` runs from a clean temp directory.
- [ ] T15 `tests/test_ids.py` passes: integrity, matrix, placeholders,
      synthetic vocabularies, AST scans, packaging.
- [ ] T16 `docs/04-implementation.md` documents the seam and the M1 limit.
- [ ] T17 `python -m compileall -q .` passes.
