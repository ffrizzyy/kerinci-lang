# Plan: worksheet-pipeline

Module: `worksheet-pipeline`. Spec: `SPEC-worksheet-pipeline.md` (approved
2026-11-02).
Depends on `core-ids` and `dialect-model`; `dialect-model` is implemented.

Goal: one canonical CSV per dialect, one validator, one reviewable DOCX, and an
export that fills an existing dialect skeleton. `core/ids.json` stays read-only.

The oracle is unchanged: all five existing suites must stay green.

## Order

1. **CSV contract** - `dialects/src/<code>.csv` with the eight columns, one row
   per catalogue ID, tier/id order, atomic writes. `buat` creates a blank sheet;
   `perbarui` restores missing rows and refreshes the read-only columns.

2. **Reader** - strict header, width, BOM, encoding, duplicate, unknown and
   missing ID checks. Problems carry a 1-based data row, the ID, a code, and a
   message. No traceback for a bad file.

3. **Normalizer** - words: NFC, trim, lowercase, whitespace to `_`, one trailing
   `()` removed, then the loader's `^[a-z][a-z0-9_]*$`. Messages: NFC and trim
   only, placeholders untouched. Alternatives are errors, never guesses.

4. **Validator** - build a synthetic draft dialect from accepted answers and
   call `validate_dialect`, so words, messages, and clashes have one source of
   truth. Add status, answer, catalogue-value, and readiness checks.

5. **DOCX writer** - standard library only, six columns, grey read-only columns,
   repeating header, A4 landscape, fixed ZIP timestamps. Same CSV -> same bytes.

6. **DOCX reader** - map by header, require the six columns, compare with the
   current CSV, change only `answer`/`notes`, downgrade a changed answer to
   `draft`, never set `reviewed`.

7. **Export** - `json` copies metadata unchanged, merges `draft`/`reviewed`
   answers into `words`/`messages`, validates, writes atomically. The readiness
   gate applies when the skeleton is `review` or `approved`.

8. **Reports** - `laporan` prints tier counts, missing tier-1 IDs, errors, and
   readiness; `periksa --siap` reuses the same calculation.

9. **CLI** - the seven subcommands, `--kode`, `--csv`, `--docx`, `--json`,
   `--paksa`, `--tulis`, `--siap`; exit 0/1/2; `--help`.

10. **Tests** - `tests/test_worksheet.py` covers spec section 10, with temp
    directories and explicit paths.

11. **Docs** - `docs/05-tooling-and-docs.md` gains the worksheet workflow;
    `docs/04-implementation.md` records the tool at `dialects/src/`; the spec is
    marked implemented.

## Verification

- `python tests/test_worksheet.py` -> all pass.
- The five existing suites, unchanged and green.
- `python tools/cek_dialek.py --semua` -> exit 0.
- Both generators produce no diff; `python -m compileall -q .`.
- `python build.py`, then `dist/krc.pyz` from a temp directory.
- No third-party package is imported by the tool.

## Risks

- The old docx cannot be ingested: no ID column, 287 rows for 137 IDs. The
  reader accepts only sheets this tool generated; Koto Payang is mapped by hand.
- A `baca` write must not invent `reviewed`; only a human changes that status.
- `periksa` must never mutate `core/ids.json` or a skeleton's metadata.
- DOCX is a ZIP: cap uncompressed size and entry count, read only
  `word/document.xml`, and never follow relationships.
- Deterministic DOCX bytes need fixed ZIP timestamps and a fixed entry order.
- `json` must fail before writing when the merged file would not validate.
