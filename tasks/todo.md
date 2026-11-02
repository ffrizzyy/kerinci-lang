# Todo: core-ids

Each item is done only when the listed check passes.

- [x] T1 `core/ids.json` exists, parses, and covers the full inventory
      (134 IDs: 26 kw, 6 op, 24 fn, 9 type, 3 mode, 65 msg, 1 reserved).
      Check: `tests/test_ids.py` catalogue cases.
- [x] T2 `core/__init__.py` and `dialects/__init__.py` exist (data packages).
- [x] T3 `Vocabulary` + `LegacySiulak` + `current_vocab`/`use_vocab` in place.
- [x] T4 `LangError` carries `msg_id`/`msg_args` and renders at construction;
      `args[0]` stays the rendered text.
- [x] T5 Lexer emits neutral token kinds; keyword text is the ID; word operators
      become the neutral symbol.
- [x] T6 Parser compares IDs only; `display()`/`label()` used for error text.
- [x] T7 Runtime: `Env.vocab`, `show(v, vocab)`, `new_global(vocab)`,
      builtins by `fn.*`, modes by `mode.*`, `mecem` by `type.*`.
- [x] T8 No literal user message left in the engine (AST scan in `test_ids.py`).
- [x] T9 Compatibility exports generated from `LegacySiulak`, same keys/values.
- [x] T10 `tests/test_kerincilang.py` 271/271, unchanged.
- [x] T11 `tests/test_tutorial.py` 550 blocks, unchanged.
- [x] T12 `tools/buat_glosarium.py` and `make_highlight.py` produce no diff.
- [x] T13 `build.py` and `pyproject.toml` ship `core/` + `dialects/`.
- [x] T14 `dist/krc.pyz` runs from a clean temp directory; `pip install . --target`
      runs from a clean temp directory.
- [x] T15 `tests/test_ids.py` passes: integrity, matrix, placeholders,
      synthetic vocabularies, AST scans, packaging.
- [x] T16 `docs/04-implementation.md` documents the seam and the M1 limit.
- [x] T17 `python -m compileall -q .` passes.

## Follow-ups (not part of core-ids)

- `dialect-model`: load `dialects/*.json`, parent fallback, validation, report.
- `runtime-selection`: per-module vocabulary, `# dialek:` header, `--ketat`.
- `cli-migration`: `krc migrasi`, precedence table, import recursion.
- `type.bool` still returns the placeholder `boolean` in Siulak until a word
  is supplied; do not change it without a Siulak re-review.
