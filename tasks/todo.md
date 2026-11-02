# Todo: worksheet-pipeline

Each item is done only when the listed check passes.

- [ ] T1 CSV paths and eight-column contract; `buat` writes 137 `todo` rows in
      tier/id order with the exact header.
- [ ] T2 `buat` refuses an existing CSV; `--paksa` replaces it.
- [ ] T3 `perbarui` restores a deleted row, refreshes the four catalogue columns,
      preserves answers, and errors on an unknown ID.
- [ ] T4 The reader reports `csv-bom`, `csv-header`, `csv-width`, `unknown-id`,
      `missing-id`, `duplicate-id` without a traceback.
- [ ] T5 Word normalization covers NFC, trim, case, whitespace, `()`, and rejects
      alternatives; message normalization preserves text and validates
      placeholders.
- [ ] T6 `periksa` reuses `validate_dialect`; a clash and an invalid word are
      reported by row and ID.
- [ ] T7 `periksa --tulis` writes only when there are no errors; warnings do not
      block.
- [ ] T8 `docx` writes an A4 landscape table with the six columns, grey read-only
      cells, and deterministic bytes.
- [ ] T9 `baca` round-trips answers and notes, downgrades a changed answer to
      `draft`, clears to `todo`, and never sets `reviewed`.
- [ ] T10 `baca` rejects a DOCX without an ID column, a duplicate ID, and a
      different header.
- [ ] T11 `json` merges only `draft`/`reviewed` answers, preserves metadata and
      `revision`, validates, and writes atomically; the result loads.
- [ ] T12 `json` writes nothing when validation fails.
- [ ] T13 `laporan` and `periksa --siap` agree on tier totals and readiness for
      `draft`, `review`, and `approved`.
- [ ] T14 CLI usage errors exit 2; `--help` documents all commands and flags.
- [ ] T15 `tests/test_worksheet.py` covers spec section 10.
- [ ] T16 All five existing suites stay green; `cek_dialek.py --semua` exits 0;
      both generators produce no diff.
- [ ] T17 `python -m compileall -q .`, `build.py`, and `dist/krc.pyz` from a temp
      directory pass.
- [ ] T18 Docs updated and the spec marked implemented.

## Follow-ups (not part of worksheet-pipeline)

- `dialect-koto-payang`: map the old docx by hand, fill the CSV, run the second
  speaker pass, and export `dialects/koto-payang.json`.
- `dialect-siulak-legacy`: freeze `dialects/siulak.json` as `draft`.
- `core/future.json` for rows without an ID.
- `buat_glosarium.py` becomes dialect-driven.
