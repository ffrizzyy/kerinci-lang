# Todo: worksheet-pipeline

Status: **implemented and green 2026-11-02.** `tests/test_worksheet.py` covers
this list; the five earlier suites are unchanged.

Each item is done only when the listed check passes.

- [x] T1 CSV paths and eight-column contract; `buat` writes 137 `todo` rows in
      tier/id order with the exact header.
- [x] T2 `buat` refuses an existing CSV; `--paksa` replaces it.
- [x] T3 `perbarui` restores a deleted row, refreshes the four catalogue columns,
      preserves answers, and errors on an unknown ID.
- [x] T4 The reader reports `csv-bom`, `csv-header`, `csv-width`, `unknown-id`,
      `missing-id`, `duplicate-id` without a traceback.
- [x] T5 Word normalization covers NFC, trim, case, whitespace, `()`, and rejects
      alternatives; message normalization preserves text and validates
      placeholders.
- [x] T6 `periksa` reuses `validate_dialect`; a clash and an invalid word are
      reported by row and ID.
- [x] T7 `periksa --tulis` writes only when there are no errors; warnings do not
      block.
- [x] T8 `docx` writes an A4 landscape table with the six columns, grey read-only
      cells, and deterministic bytes.
- [x] T9 `baca` round-trips answers and notes, downgrades a changed answer to
      `draft`, clears to `todo`, and never sets `reviewed`.
- [x] T10 `baca` rejects a DOCX without an ID column, a duplicate ID, and a
      different header.
- [x] T11 `json` merges only `draft`/`reviewed` answers, preserves metadata and
      `revision`, validates, and writes atomically; the result loads.
- [x] T12 `json` writes nothing when validation fails.
- [x] T13 `laporan` and `periksa --siap` agree on tier totals and readiness for
      `draft`, `review`, and `approved`.
- [x] T14 CLI usage errors exit 2; `--help` documents all commands and flags.
- [x] T15 `tests/test_worksheet.py` covers spec section 10.
- [x] T16 All five existing suites stay green; `cek_dialek.py --semua` exits 0;
      both generators produce no diff.
- [x] T17 `python -m compileall -q .`, `build.py`, and `dist/krc.pyz` from a temp
      directory pass.
- [x] T18 Docs updated and the spec marked implemented.

## Follow-ups (not part of worksheet-pipeline)

- `dialect-koto-payang`: map the old docx by hand, fill the CSV, run the second
  speaker pass, and export `dialects/koto-payang.json`.
- `dialect-siulak-legacy`: freeze `dialects/siulak.json` as `draft`.
- `core/future.json` for rows without an ID.
- `buat_glosarium.py` becomes dialect-driven.
