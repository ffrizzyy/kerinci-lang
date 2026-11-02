# Plan: core-ids

Module: `core-ids`. Spec: `SPEC-core-ids.md` (approved 2026-11-02).
Goal: freeze the neutral ID catalogue and move the engine onto neutral IDs, while
Siulak v0.5 behavior and output stay byte-identical.

The oracle is the existing test suite: `tests/test_kerincilang.py` (271 cases) and
`tests/test_tutorial.py` (550 blocks). Neither file may be edited.

## Order

1. **Catalogue** - `core/ids.json`, `core/__init__.py`, `dialects/__init__.py`.
   Every live ID with `namespace`, `tier`, `en`, `id_gloss`, `description`,
   `example`, `arity`, `placeholders`.

2. **Message inventory** - turn all 61 `LangError` raise sites and the four
   `file_error` returns into `msg.*` entries whose `id_gloss` renders exactly the
   v0.5 text. No f-string user messages left in the engine.

3. **Vocabulary seam** - `Vocabulary` protocol, `LegacySiulak`, `current_vocab()`,
   `use_vocab()`. `Env.vocab`. Optional `vocab` argument on
   `run_source`/`run_file`/`tokenize`/`new_global`/`show`.

4. **Lexer** - token kinds become IDs (`kw.if`, `op.eq`); comparison token text is
   the neutral symbol; begin/end still lex to `{`/`}`.

5. **Parser** - compare IDs, never words. `display()` is the only place a token
   becomes a dialect word for an error message.

6. **Runtime** - `LangError` renders at construction and carries `msg_id`/`args`.
   Built-ins register under `vocab.word(fn_id)`. `show`, `mecem`, `bukak`, file
   modes, and `iterate` all read the active vocabulary.

7. **Compatibility layer** - generate `KEYWORDS`, `SURFACE`, `WORD_OPERATORS`,
   `BUILTINS`, `TYPE_NAMES`, `MODES`, `RESERVED`, `ENABLE_WORD_OPERATORS` from
   `LegacySiulak`; never hand-maintain a second table.

8. **Packaging** - `core/` and `dialects/` as data packages; `build.py` and
   `pyproject.toml` include them.

9. **Tests** - new `tests/test_ids.py`: catalogue integrity, namespace matrix,
   placeholder agreement, two synthetic vocabularies, AST scans, packaging.

10. **Docs** - `docs/04-implementation.md` records the seam and the M1 limit.

## Verification

- `python tests/test_kerincilang.py` -> 271/271, no edits.
- `python tests/test_tutorial.py` -> 550 blocks, no edits.
- `python tools/buat_glosarium.py` -> no diff.
- `python make_highlight.py` -> no diff.
- `python build.py` then run `dist/krc.pyz` from a temp directory.
- `python tests/test_ids.py` -> all pass.
- `python -m compileall -q .`.

## Risks

- Message text drift: every `msg.*` `id_gloss` is checked by the suites; if a
  template renders differently, the suites fail.
- `e.args[0]` is used by tests; `LangError` must keep a plain string as `args[0]`.
- Built-ins are called without an `Env`, so they read the active vocabulary.
  M1 has a single vocabulary per run; `runtime-selection` will push per module.
- `type.bool` is still the placeholder `boolean`; do not change it here.
