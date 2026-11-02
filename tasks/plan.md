# Plan: dialect-siulak-legacy

Module: `dialect-siulak-legacy`. Spec: `SPEC-dialect-siulak-legacy.md`
(approved 2026-11-02). Depends on `core-ids` and `dialect-model`, both
implemented.

Goal: freeze the v0.5 Siulak vocabulary as a complete `draft` dialect, without
changing the runtime or any existing test expectation.

The oracle is unchanged: all six existing suites must stay green.

## Order

1. **Freeze data** - generate `dialects/siulak.json` from `LEGACY_WORDS`,
   `LEGACY_OPERATORS`, and the `msg.*` `id_gloss` values in `core/ids.json`.
   Use the exact metadata from the spec; 137 IDs; sorted keys; 2-space indent;
   final newline.

2. **Provenance note** - `dialects/siulak.md` records the freeze, the source
   files, the 69-word table, the message rule, the change policy, and the
   `type.bool` placeholder.

3. **Loader check** - `load_dialect("siulak")` must own every ID, report no
   fallbacks, and pass `validate_dialect`. No code change is expected.

4. **Equivalence test** - `tests/test_siulak_legacy.py` compares the file to the
   v0.5 tables and `DialectVocabulary` to `LegacySiulak` for all words,
   operators, modes, types, reserved word, and messages.

5. **Selection and gate** - the test runs a `# dialek: siulak` file, a
   `--dialek siulak` one-liner, checks that stderr has no fallback warning, and
   runs `cek_dialek --kode siulak` with and without `--ketat`.

6. **Docs** - mark the spec implemented, check off the todo, update the
   capability map, and add the freeze to the implementation/tooling docs.

## Verification

- `python tests/test_siulak_legacy.py` -> all pass.
- The six earlier suites, unchanged and green.
- `python tools/cek_dialek.py --semua` -> exit 0; `--kode siulak --ketat` -> 0.
- Both generators produce no diff; `python -m compileall -q .`.
- `python build.py`, then `dist/krc.pyz` from a temp directory.
- The new file is in the wheel/zipapp data because `dialects/*.json` is already
  packaged.

## Risks

- A typo in one word silently changes v0.5 output. The test compares every ID,
  so a typo fails.
- `type.bool` must stay `"boolean"`; "fixing" it is a later re-review.
- Messages must use `id_gloss` unchanged; placeholders are validated by the
  loader and the test.
- `LEGACY_WORDS` order is not file order; write sorted keys.
- `DialectVocabulary.operators()` is word -> symbol, like `LegacySiulak`; do not
  compare symbols only.
- Do not change `resolve_dialect` or the default `run_source()` vocabulary.
