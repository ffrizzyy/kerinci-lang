# Siulak (legacy 0.5)

Status: **frozen draft.** This is the v0.5 vocabulary, kept as data so existing
programs, tests, and the tutorial keep working. It is not a 0.6 re-review.

## Provenance

- `docs/02-vocabulary-worksheet.md` is the decision log and records the v0.5
  speaker review.
- `kerincilang.py` holds the frozen `LEGACY_WORDS` and `LEGACY_OPERATORS` tables.
- `core/ids.json` supplies the neutral IDs, tiers, and the Indonesian `id_gloss`
  templates used for messages.
- `dialects/siulak.json` is the runtime data. `tests/test_siulak_legacy.py` locks
  it to those sources.

## Freeze policy

- Every ID in the 0.6 catalogue is owned by `siulak.json`; there is no English
  fallback.
- Words, operators, types, modes, the reserved word, and messages are copied
  exactly from v0.5.
- `type.bool` is the English placeholder `boolean`; it is recorded here as a
  known gap, not fixed in this module.
- A change needs a Siulak speaker review and a new `revision`. Renaming,
  normalizing, or marking the file `review` or `approved` is a separate module.
- `status` stays `draft` and `reviewer` stays `null` until that review.

## Words

The 69 word IDs, grouped by namespace. The JSON is sorted by ID; this table is
grouped for review.

| ID | Word | Namespace | Note |
|---|---|---|---|
| `kw.and` | `ngan` | `kw` |  |
| `kw.begin` | `mulai` | `kw` | same as `{` / `}` |
| `kw.break` | `putuh` | `kw` |  |
| `kw.catch` | `tangkap` | `kw` |  |
| `kw.const` | `tetap` | `kw` |  |
| `kw.continue` | `lanjut` | `kw` |  |
| `kw.else` | `lain` | `kw` |  |
| `kw.end` | `habih` | `kw` | same as `{` / `}` |
| `kw.false` | `salah` | `kw` |  |
| `kw.for` | `untuk` | `kw` |  |
| `kw.func` | `guno` | `kw` |  |
| `kw.if` | `kalu` | `kw` |  |
| `kw.import` | `ambik` | `kw` |  |
| `kw.in` | `alem` | `kw` |  |
| `kw.input` | `tanyo` | `kw` |  |
| `kw.not` | `idak` | `kw` |  |
| `kw.null` | `kosong` | `kw` |  |
| `kw.or` | `apo` | `kw` |  |
| `kw.print` | `nyetak` | `kw` |  |
| `kw.raise` | `ngangkat` | `kw` |  |
| `kw.return` | `balik` | `kw` |  |
| `kw.switch` | `pilih` | `kw` |  |
| `kw.true` | `betul` | `kw` |  |
| `kw.try` | `cubo` | `kw` |  |
| `kw.var` | `barang` | `kw` |  |
| `kw.while` | `selamo` | `kw` |  |
| `op.eq` | `samo` | `op` |  |
| `op.ge` | `lebih_samo` | `op` |  |
| `op.gt` | `lebih_daripado` | `op` |  |
| `op.le` | `kurang_samo` | `op` |  |
| `op.lt` | `kurang_daripado` | `op` |  |
| `op.ne` | `dak_samo` | `op` |  |
| `fn.add` | `tambah` | `fn` |  |
| `fn.append` | `nambahkah` | `fn` |  |
| `fn.close` | `tutup` | `fn` |  |
| `fn.contains` | `isi` | `fn` |  |
| `fn.delete` | `hapus` | `fn` |  |
| `fn.div` | `bagi` | `fn` |  |
| `fn.float` | `pecahan` | `fn` |  |
| `fn.int` | `bilangan` | `fn` |  |
| `fn.join` | `disatu` | `fn` |  |
| `fn.length` | `panjang` | `fn` |  |
| `fn.list` | `daftar` | `fn` |  |
| `fn.map` | `peta` | `fn` |  |
| `fn.mul` | `kali` | `fn` |  |
| `fn.open` | `bukak` | `fn` |  |
| `fn.range` | `jarak` | `fn` |  |
| `fn.read` | `baco` | `fn` |  |
| `fn.reverse` | `pulang` | `fn` |  |
| `fn.sort` | `milih` | `fn` |  |
| `fn.split` | `pisah` | `fn` |  |
| `fn.sub` | `kurang` | `fn` |  |
| `fn.text` | `kato` | `fn` |  |
| `fn.type` | `mecem` | `fn` |  |
| `fn.wait` | `nantik` | `fn` |  |
| `fn.write` | `tulis` | `fn` |  |
| `type.bool` | `boolean` | `type` | English placeholder; no Kerinci word yet |
| `type.file` | `berkas` | `type` |  |
| `type.float` | `pecahan` | `type` |  |
| `type.func` | `guno` | `type` |  |
| `type.int` | `bilangan` | `type` |  |
| `type.list` | `daftar` | `type` |  |
| `type.map` | `peta` | `type` |  |
| `type.null` | `kosong` | `type` |  |
| `type.str` | `kato` | `type` |  |
| `mode.append` | `nambahkah` | `mode` |  |
| `mode.read` | `baco` | `mode` |  |
| `mode.write` | `tulis` | `mode` |  |
| `reserved.error` | `kelihu` | `reserved` | reserved; using it as a name is an error |

## Messages

All 68 `msg.*` templates are the Indonesian `id_gloss` strings from
`core/ids.json`, copied unchanged. Placeholders such as `{name}` stay neutral
English; `tests/test_siulak_legacy.py` checks the placeholder set for every
message.

## Change policy

A word or message may change only in a new revision after a Siulak speaker
review. Normalization, renaming, and "fixing" v0.5 quirks are out of scope.
`type.bool` is the first known item for that review.

## Authority

`dialects/siulak.json` is the runtime data. `docs/02-vocabulary-worksheet.md` is
the decision history. This file explains the freeze; it does not replace either
one.
