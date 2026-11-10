# Koto Payang

Status: **approved.** All 137 IDs are reviewed, with Rizka Hanifa Khairany as
the named reviewer. The dialect owns every word and message and has no English
fallback.

## Provenance

- `Translation Worksheet (Koto Payang).docx` is the first linguistic draft.
  Speaker: Rizka Hanifa Khairany. The sheet has 287 rows and no ID column, so it
  was mapped by hand, not parsed.
- `docs/08-multi-dialect-plan-review.md` records the worksheet audit and the
  decision to normalize before review.
- `dialects/src/koto-payang.csv` is the canonical answer file, one row per
  catalogue ID. `dialects/koto-payang.json` is the runtime data.
- `core/ids.json` supplies the IDs, tiers, and neutral placeholders.

## Orthography

- Final `-u` is kept: `kalu`, `selamu`, `daling`, `baluikka`.
- `nga` means "and"; `atau` means "or".
- Multi-word concepts use underscores: `lebih_nik_dari`, `netakka_variabel`,
  `samu_dinga`.
- Keywords and function names are lowercase; a trailing `()` is removed.
- Message placeholders stay neutral English (`{name}`, `{message}`, `{arity}`),
  never Indonesian (`{nama}`, `{pesan}`, `{n}`).

## Mapping decisions

- `elif` is not a catalogue ID. The language writes `lain kalu` in Siulak and
  `nga_laen` + `kalu` here; it is not a separate word.
- Worksheet `match` maps to `kw.switch`; worksheet `except` maps to `kw.catch`.
- "Declare a variable/constant" maps to `kw.var`/`kw.const`, joined with `_`:
  `netakka_variabel`, `netakka_konstanta`.
- Worksheet `import` lists `impor/masukka`; `impor` is used because `masukka`
  is already `kw.input`.
- Worksheet type `list` lists `daftar/lis`; `daftar` is used.
- Worksheet `tuilsan` is corrected to `tulisan`.
- Worksheet `float` type lists `bilangan bakoma/bilangan desimal`;
  `bilangan_bakoma` was provisional and is now approved.
- `type.null` is inferred from `kw.null` (`kusao`) and is approved.
- `kw.begin`/`kw.end` are `mulai`/`selesai`, supplied by the maintainer on
  2026-11-02; the worksheet rows were left in Indonesian.
- The last six open words were composed from the dialect's own vocabulary and
  then approved: `fn.contains` `meriksu`, `fn.wait` `nunggu`, `fn.list` `daftar`,
  `fn.map` `peta`, `type.bool` `betiu_salah`, `reserved.error` `kesalahan`.
- The 42 open messages were composed from attested Koto Payang fragments and
  approved on 2026-11-10.
- The DOCX is never read by a script. Its rows are a linguistic source, not an
  ingestible data file.

## Review record

| Date | Step | Result |
|---|---|---|
| 2026-11-02 | First normalization pass | 32/32 Tier 1 reviewed; 53 Tier 2 reviewed; 4 Tier 2 draft; 48 todo |
| 2026-11-10 | Speaker review | 52 open rows composed from attested vocabulary and approved; all 137 rows reviewed |
| 2026-11-10 | Promotion | `approved`, revision 2, reviewer Rizka Hanifa Khairany; no English fallback |

`python3 tools/lembar_kerja.py periksa --kode koto-payang --siap` reports ready
for both `review` and `approved`. `periksa`, `laporan`, and
`cek_dialek --kode koto-payang` pass with 0 errors and 0 warnings.

## Coverage

Every catalogue ID is owned. There are no gaps: the CSV has 137 `reviewed`
rows, the JSON has 69 words and 68 messages, and `cek_dialek` reports
`tier 1 32/32, tier 2 104/104, tier 3 1/1`.

The 52 rows that were open after the first pass were filled only from this
dialect's own vocabulary. Six words were composed from attested roots:
`meriksu`, `nunggu`, `daftar`, `peta`, `betiu_salah`, and `kesalahan`. The 42
messages were composed sentence by sentence from attested fragments, keeping
the catalogue placeholders neutral.

Do not replace an approved word with a Siulak word or an Indonesian phrase.
A change needs a speaker decision and a new revision.

## Change policy

- A `reviewed` row may change only with a speaker decision and a new revision.
- A `draft` row is provisional; only a speaker can confirm or replace it.
- A `todo` row is empty on purpose; do not invent an answer.
- Promotion to `approved` required every Tier 1 and Tier 2 row reviewed and a
  named reviewer. That review was completed on 2026-11-10.
- The neutral placeholders are part of the contract; a translated placeholder
  is a validation error.

## Authority

`dialects/koto-payang.json` is the runtime data. `dialects/src/koto-payang.csv`
is the canonical answer file. This note explains the mapping and the review
state; it does not replace either one.
