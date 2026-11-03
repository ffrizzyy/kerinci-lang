# Koto Payang

Status: **review.** Tier 1 is complete; Tier 2 is partly mapped. The dialect is
included at this status, with no named reviewer. The open Tier 2 rows fall back
to the English base.

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
  `bilangan_bakoma` is provisional (`draft`).
- `type.null` is inferred from `kw.null` (`kusao`) and is provisional.
- `kw.begin`/`kw.end` are `mulai`/`selesai`, supplied by the maintainer on
  2026-11-02; the worksheet rows were left in Indonesian.
- The DOCX is never read by a script. Its rows are a linguistic source, not an
  ingestible data file.

## Review record

| Date | Step | Result |
|---|---|---|
| 2026-11-02 | First normalization pass | 32/32 Tier 1 reviewed; 53 Tier 2 reviewed; 4 Tier 2 draft; 48 todo |
| — | Current state | Included at `review`; 51 Tier 2 rows remain open |

`reviewer` is `null`. `python3 tools/lembar_kerja.py periksa --kode koto-payang
--siap` passes for `review` and reports `approved` as not ready (51 Tier 2 rows
unreviewed).

## Gaps (48)

Six words and forty-two messages still use the English base. They are `todo` in
the CSV:

```text
fn.list  fn.map  fn.contains  fn.wait  type.bool  reserved.error

msg.call.builtin_arity         msg.call.depth_short
msg.dialect.header             msg.dialect.invalid
msg.dialect.unknown            msg.file.handle_required
msg.file.io                    msg.file.is_dir
msg.file.mode_invalid          msg.file.not_utf8
msg.file.path_type             msg.file.permission
msg.fn.contains_kind           msg.fn.contains_type
msg.fn.join_arity              msg.fn.length_kind
msg.fn.list_only               msg.fn.open_arity
msg.fn.range_args              msg.fn.range_arity
msg.fn.range_step              msg.fn.range_too_big
msg.fn.reverse_kind            msg.fn.sort_type
msg.fn.split_arity             msg.fn.split_kind
msg.fn.wait_number             msg.fn.wait_range
msg.import.not_found           msg.import.not_text
msg.loop.not_iterable          msg.loop.use_range
msg.name.already_const         msg.runtime.too_deep
msg.runtime.unknown_expr       msg.syntax.assign_target
msg.syntax.expected_after_name  msg.syntax.reserved
msg.value.index_kind           msg.value.map_pair
msg.value.neg_type             msg.value.separator
```

Do not fill a gap with a guessed word, a Siulak word, or an Indonesian phrase.
An open row stays on the English fallback until a speaker supplies an answer.

## Change policy

- A `reviewed` row may change only with a speaker decision and a new revision.
- A `draft` row is provisional; only a speaker can confirm or replace it.
- A `todo` row is empty on purpose; do not invent an answer.
- Promoting to `approved` requires every Tier 1 and Tier 2 row reviewed and a
  named reviewer. That is a separate change.
- The neutral placeholders are part of the contract; a translated placeholder
  is a validation error.

## Authority

`dialects/koto-payang.json` is the runtime data. `dialects/src/koto-payang.csv`
is the canonical answer file. This note explains the mapping and the review
state; it does not replace either one.
