# Todo: dialect-model

Each item is done only when the listed check passes.

- [ ] T1 `OP_SYMBOLS` in `kerincilang.py`, derived from `LEGACY_OPERATORS`.
- [ ] T2 `dialects/loader.py` exists: `Problem`, `DialectError`, `Report`,
      `Dialect`, `DialectVocabulary`, `base_dialect`, `validate_dialect`,
      `load_dialect`, `available_dialects`.
- [ ] T3 `base_dialect()` resolves every live ID from `core/ids.json` and passes
      its own validation.
- [ ] T4 File reading: code pattern, path inside `root`, 1 MiB cap, duplicate
      keys rejected, UTF-8 only, object root.
- [ ] T5 Works from a checkout, a wheel, and `dist/krc.pyz` (default root via
      `importlib.resources`).
- [ ] T6 Parent chain resolves child -> parent -> base; a parent cycle names all
      members; a missing parent is `parent-missing`.
- [ ] T7 Every section 6 rule has a code and a test: `schema`, `code`,
      `core-version`, `word-empty`, `word-charset`, `word-case`, `unknown-id`,
      `wrong-namespace`, `message-placeholder`, `parent-missing`,
      `parent-cycle`, `reviewer-missing`, `source-missing`, `clash`, `path`,
      `size`, `json`.
- [ ] T8 Clash matrix: 12 Siulak overlaps accepted; `fn`/`kw` clash rejected
      with both IDs named.
- [ ] T9 `newer-core` warns and loads; an unknown ID is a hard error.
- [ ] T10 `DialectVocabulary` runs a program through
      `run_source(..., vocab=load_dialect(...).vocab)`.
- [ ] T11 `tools/cek_dialek.py` supports `--semua`, `--kode`, `--ketat`; exit
      0/1/2; `main(argv, root)` usable from tests.
- [ ] T12 `python tools/cek_dialek.py --semua` exits 0 on the empty `dialects/`.
- [ ] T13 `tests/test_dialects.py` passes; fixtures are temporary, none committed.
- [ ] T14 `tests/test_kerincilang.py` 271/271, `test_tutorial.py` 550 blocks,
      `test_ids.py` all pass, all unchanged.
- [ ] T15 `buat_glosarium.py` and `make_highlight.py` produce no diff;
      `build.py` and `dist/krc.pyz` still work from a clean temp directory.
- [ ] T16 `docs/04-implementation.md` documents dialect files; spec marked
      implemented; `CAPABILITY-MAP.md` points at `runtime-selection`.
- [ ] T17 `python -m compileall -q .` passes.

## Follow-ups (not part of dialect-model)

- `dialect-siulak-legacy`: freeze Siulak as `dialects/siulak.json` (`draft`).
- `dialect-koto-payang`: normalize the worksheet and write the first draft.
- `runtime-selection`: `# dialek:` header, `--dialek`, `--ketat`, per-module
  scopes.
- `cli-migration`: `krc migrasi`, precedence table, import recursion.
- `type.bool` still renders `boolean` in Siulak until a speaker review.
