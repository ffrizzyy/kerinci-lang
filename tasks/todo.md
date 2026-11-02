# Todo: dialect-koto-payang

Each item is done only when the listed check passes.

- [x] T1 `dialects/src/koto-payang.csv` has 137 rows and the exact header.
- [x] T2 Tier 1 is 32/32 `reviewed`; the 32 answers equal the spec's section 4.
- [x] T3 Tier 2 has 53 reviewed, 4 draft, 47 todo; the answers equal sections
      5-6 and every todo keeps the worksheet value in `notes`.
- [x] T4 `periksa --siap` passes `review` and fails `approved` with 51
      unreviewed Tier 2 rows.
- [x] T5 `dialects/koto-payang.json` has the section 7 metadata and owns exactly
      63 words + 26 messages.
- [x] T6 `load_dialect("koto-payang")` has no problems, tiers
      `32/32, 57/104, 0/1`, and exactly the 48 expected fallbacks.
- [x] T7 `dialects/koto-payang.md` records provenance, orthography, mapping
      decisions, the review record, and the 48 gaps.
- [x] T8 `tests/test_koto_payang.py` proves the word and message maps, the CSV
      counts, selection with no warning, and a missing-ID warning.
- [x] T9 `cek_dialek --kode koto-payang`, `--ketat`, and `--semua` exit 0; the
      summary is exact.
- [x] T10 All eight earlier suites stay green, unchanged except no further test
      edits.
- [x] T11 `compileall`, `build.py`, and `dist/krc.pyz` from a temp directory
      pass; both generators produce no diff.
- [x] T12 Docs updated; the spec is marked implemented.

## Follow-ups (not part of dialect-koto-payang)

- Second speaker pass: fill the 42 todo messages and 6 todo words, confirm the
  4 drafts, then re-run `periksa --siap` and promote to `approved` with a named
  reviewer.
- The translator and tutorial modules depend on this reviewed dialect.
