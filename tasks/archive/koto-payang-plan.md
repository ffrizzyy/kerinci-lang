# Plan: dialect-koto-payang

Module: `dialect-koto-payang`. Spec: `SPEC-dialect-koto-payang.md` (approved
2026-11-02). Depends on `worksheet-pipeline` and `runtime-selection`, both
implemented.

Goal: hand-map the Koto Payang worksheet into a `review` dialect with all 32
Tier 1 IDs, 53 reviewed Tier 2 IDs, 4 provisional drafts, and 48 documented base
fallbacks. No invented answers. The second speaker pass is a later step.

The oracle is unchanged: all eight existing suites must stay green.

## Order

1. **Skeleton** - `python tools/lembar_kerja.py buat --kode koto-payang` creates
   `dialects/src/koto-payang.csv` with 137 `todo` rows.

2. **Hand mapping** - fill `answer`, `notes`, and `status` from the spec's
   section 4-6 tables. Tier 1 is all `reviewed`. Tier 2 is 29 reviewed words,
   2 draft words, 24 reviewed messages, 2 draft messages. Everything else stays
   `todo` with the worksheet value in `notes`.

3. **Validate the sheet** - `periksa --siap` must pass `review` and fail
   `approved` with 51 unreviewed Tier 2 rows. Fix only real normalization or
   placeholder errors; never invent an answer.

4. **Export** - create the JSON skeleton, set the section 7 metadata
   (`status: review`, `reviewer: null`, sources, orthography, notes), then run
   `lembar_kerja.py json`. It must validate and produce 63 words + 26 messages.

5. **Provenance note** - `dialects/koto-payang.md` records provenance,
   orthography, mapping decisions, the review record, the 48 gap IDs, and the
   change policy.

6. **Tests** - `tests/test_koto_payang.py` checks the artifacts, metadata, tier
   counts, exact word/message maps, CSV statuses and readiness, selection,
   fallback warning, `--ketat`, and the `cek_dialek` gate.

7. **Docs** - mark the spec implemented, check off the todo, update the
   capability map, and add the Koto Payang workflow to the implementation and
   tooling docs.

## Verification

- `python tests/test_koto_payang.py` -> all pass.
- The eight earlier suites, unchanged and green.
- `python tools/cek_dialek.py --kode koto-payang` -> exit 0, exact summary.
- `python tools/cek_dialek.py --semua` -> exit 0.
- Both generators produce no diff; `python -m compileall -q .`.
- `python build.py`, then `dist/krc.pyz` runs Koto Payang from a temp directory.
- The JSON ships in the wheel/zipapp via the existing `dialects/*.json` package
  data; the CSV is working data and is not packaged.

## Risks

- The worksheet is a first draft: a gloss, alternative, or typo can look like an
  answer. The spec's status table is the contract; when in doubt, `todo`.
- Placeholders must be neutral English. A copied `{nama}` or `{pesan}` fails the
  loader.
- `kw.import` must be `impor`; `masukka` is `kw.input` and would clash.
- Multi-word answers use underscores; spaces fail the word regex.
- `type.float` and `type.null` are draft, not reviewed; do not promote them
  without a speaker.
- `status: review` keeps `cek_dialek --ketat` and runtime `--ketat` at exit 0;
  do not change the gate to make the module look more complete.
- The old DOCX is never parsed. Its 287 rows are not a data source for a script.
