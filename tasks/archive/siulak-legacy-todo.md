# Todo: dialect-siulak-legacy

Each item is done only when the listed check passes.

- [x] T1 `dialects/siulak.json` has the spec metadata, `status: draft`,
      `revision: 1`, `reviewer: null`, `parent: null`.
- [x] T2 All 69 word IDs match `LEGACY_WORDS` and `LEGACY_OPERATORS`; no extra
      or missing word ID.
- [x] T3 All 68 `msg.*` templates equal `id_gloss`; placeholders match.
- [x] T4 `load_dialect("siulak")` has no problems, `fallbacks == []`,
      `missing() == []`, and tiers `32/32`, `104/104`, `1/1`.
- [x] T5 `dialects/siulak.md` records provenance, the 69-word table, the
      message rule, the change policy, and the `type.bool` placeholder.
- [x] T6 `tests/test_siulak_legacy.py` proves `DialectVocabulary` equals
      `LegacySiulak` for every word and message.
- [x] T7 A `# dialek: siulak` file and `--dialek siulak` run with v0.5 output
      and no fallback warning.
- [x] T8 `cek_dialek --kode siulak` and `--ketat` exit 0; `--semua` exits 0.
- [x] T9 All six earlier suites stay green, unchanged.
- [x] T10 `python -m compileall -q .`, `build.py`, and `dist/krc.pyz` from a temp
      directory pass; both generators produce no diff.
- [x] T11 Docs updated; the spec is marked implemented.

## Follow-ups (not part of dialect-siulak-legacy)

- `dialect-koto-payang`: map the old worksheet by hand, fill the CSV, run the
  second speaker pass, export `dialects/koto-payang.json`.
- A real Siulak re-review changes this file in a new revision and may change
  `type.bool`.
