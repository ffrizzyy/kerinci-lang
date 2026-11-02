# Spec: dialect-koto-payang

Status: **draft for approval.** Parent: `SPEC.md`. Capability map:
`dialect-koto-payang`.
Depends on: `worksheet-pipeline` (implemented) and `runtime-selection`
(implemented). Date: 2026-11-02.

## 1. Objective

Turn the first-draft Koto Payang worksheet into the first completed non-Siulak
dialect: a canonical CSV, a validated `dialects/koto-payang.json`, a provenance
and orthography note, and a review record.

This module targets **`status: review`**, not `approved`:

- all 32 Tier 1 IDs are normalized, mapped, and reviewed;
- 53 Tier 2 IDs are reviewed (29 words + 24 messages) and 4 more are mapped as
  provisional drafts (2 words + 2 messages);
- the remaining 51 Tier 2 IDs (47 `todo` + 4 `draft`) and the one Tier 3 ID fall
  back or wait for confirmation; the `todo` ones use the English base with the
  normal runtime warning;
- a second speaker pass fills those gaps and is the separate step that may move
  the file to `approved`.

The old `Translation Worksheet (Koto Payang).docx` is a linguistic first draft,
not an ingestible file. It has no ID column, alternatives, phrases, missing
placeholders, and 287 rows for 137 IDs. This module maps it by hand; it never
parses the DOCX automatically.

## 2. Scope

### In scope

- `dialects/src/koto-payang.csv`: 137 rows in the canonical worksheet schema.
- `dialects/koto-payang.json`: the validated `review` dialect.
- `dialects/koto-payang.md`: provenance, orthography, mapping decisions, review
  record, and the explicit gap list.
- `tests/test_koto_payang.py`: data, CSV, selection, warning, and gate checks.
- Documentation that marks the module implemented.

### Out of scope

- The second speaker pass, `approved` status, or a named reviewer.
- Inventing any word or message that is not in the worksheet. Missing IDs stay
  `todo` and fall back.
- Reading the DOCX automatically, or adding a `docx` importer.
- Changing the loader, runtime, worksheet tool, catalogue, or Siulak.
- Translating tutorial prose, the translator, or other dialects.

## 3. Canonical CSV

`dialects/src/koto-payang.csv` is UTF-8 without a BOM, LF line endings, with the
exact header:

```text
id,tier,namespace,en,id_gloss,answer,notes,status
```

- 137 data rows, one per catalogue ID, in `core/ids.json` order.
- The first five columns are copied from the catalogue and never edited by hand.
- `answer` is normalized (NFC, trim, lowercase, whitespace to `_`, one trailing
  `()` removed). Messages are NFC and trim only.
- `status` is one of `todo`, `draft`, `reviewed`, `rejected`.
- A `todo` row has an empty `answer`; the worksheet value, if any, goes in
  `notes` for the second pass.
- A `draft` row has a provisional answer that is merged into the JSON but is not
  speaker-confirmed.
- A `reviewed` row is normalized, unambiguous, and ready for the second pass.
- No answer contains `/`, `,`, a space, uppercase, or a non-identifier character
  after normalization. Alternatives are resolved in the mapping, never carried.

Counts after this module:

| Tier | Total | Reviewed | Draft | Todo |
|---|---|---|---|---|
| 1 | 32 | 32 | 0 | 0 |
| 2 | 104 | 53 | 4 | 47 |
| 3 | 1 | 0 | 0 | 1 |
| **All** | **137** | **85** | **4** | **48** |

`python3 tools/lembar_kerja.py periksa --kode koto-payang --siap` must report
the sheet ready for `review` and **not** ready for `approved` (Tier 2 has 51
unreviewed rows).

## 4. Tier 1 words (32, all reviewed)

Every Tier 1 ID has an answer. The two block aliases were left in Indonesian in
the worksheet; the user supplied `mulai` and `selesai` for this module.

| ID | Koto Payang | Source |
|---|---|---|
| `kw.var` | `netakka_variabel` | worksheet row 12; underscore-joined phrase |
| `kw.const` | `netakka_konstanta` | row 13; underscore-joined phrase |
| `kw.func` | `jeloehka` | row 10 |
| `kw.return` | `baluikka` | row 9 |
| `kw.if` | `kalu` | row 1 |
| `kw.else` | `nga_laen` | row 3; two words joined |
| `kw.while` | `selamu` | row 5 |
| `kw.for` | `ndik` | row 4 |
| `kw.in` | `daling` | row 6 |
| `kw.switch` | `cocokka` | row 11; `match` maps to `switch` |
| `kw.import` | `impor` | row 33; first alternative; `masukka` is `kw.input` |
| `kw.try` | `cubea` | row 30 |
| `kw.catch` | `kecuali` | row 31; `except` maps to `catch` |
| `kw.raise` | `timbaoka` | row 32 |
| `kw.break` | `slese` | row 7 |
| `kw.continue` | `lanjutka` | row 8; lowercase |
| `kw.print` | `nytak` | row 28; `()` removed, lowercase |
| `kw.input` | `masukka` | row 29; `()` removed |
| `kw.true` | `betiu` | row 19 |
| `kw.false` | `salah` | row 20 |
| `kw.null` | `kusao` | row 21 |
| `kw.and` | `nga` | row 17 |
| `kw.or` | `atau` | row 18 |
| `kw.not` | `iduak` | row 16 |
| `kw.begin` | `mulai` | user-supplied 2026-11-02 |
| `kw.end` | `selesai` | user-supplied 2026-11-02 |
| `op.eq` | `samu_dinga` | row 22 |
| `op.ne` | `iduak_samu_dinga` | row 23 |
| `op.gt` | `lebih_geduang_dari` | row 25 |
| `op.lt` | `lebih_nik_dari` | row 24 |
| `op.ge` | `lebih_geduang_atau_samu_dinga` | row 27 |
| `op.le` | `lebih_nik_atau_samu_dinga` | row 26 |

`kw.begin` and `kw.end` keep the `{`/`}` symbols as the primary block syntax;
the words are the dialect aliases.

## 5. Tier 2 and 3 words (37)

### 5.1 Built-in functions (24)

| ID | Answer | Status | Source |
|---|---|---|---|
| `fn.add` | `tambah` | reviewed | row 43 |
| `fn.sub` | `kura` | reviewed | row 44 |
| `fn.mul` | `kali` | reviewed | row 45 |
| `fn.div` | `bagi` | reviewed | row 46 |
| `fn.length` | `panja` | reviewed | row 47 |
| `fn.range` | `rentang` | reviewed | row 48 |
| `fn.sort` | `terurut` | reviewed | row 49 |
| `fn.reverse` | `tebaluik` | reviewed | row 50 |
| `fn.int` | `bilangan_buluak` | reviewed | row 51 |
| `fn.float` | `desimal` | reviewed | row 52 |
| `fn.text` | `tulisan` | reviewed | row 53 |
| `fn.append` | `tambahka` | reviewed | row 54 |
| `fn.split` | `pecah` | reviewed | row 55 |
| `fn.join` | `basatau` | reviewed | row 56 |
| `fn.open` | `bukuak` | reviewed | row 59 |
| `fn.read` | `bacea` | reviewed | row 60 |
| `fn.write` | `tulaih` | reviewed | row 61 |
| `fn.close` | `tutamp` | reviewed | row 62 |
| `fn.delete` | `ngapih_berkas` | reviewed | row 63; phrase joined |
| `fn.type` | `tipe` | reviewed | row 40; `()` removed |
| `fn.list` | *(empty)* | todo | no worksheet row for `list()` |
| `fn.map` | *(empty)* | todo | no worksheet row for `map()` |
| `fn.contains` | *(empty)* | todo | row 57 is a gloss, not a name |
| `fn.wait` | *(empty)* | todo | row 58 is a gloss, not a name |

### 5.2 Types (9)

| ID | Answer | Status | Source |
|---|---|---|---|
| `type.int` | `bilangan_buluak` | reviewed | row 34 |
| `type.float` | `bilangan_bakoma` | draft | row 35; first alternative |
| `type.str` | `tulisan` | reviewed | row 36; typo `tuilsan` corrected |
| `type.bool` | *(empty)* | todo | row 37 is blank |
| `type.list` | `daftar` | reviewed | row 38; `lis` rejected |
| `type.map` | `kamus` | reviewed | row 39; `dict` maps to `map` |
| `type.func` | `pungsi` | reviewed | row 41 |
| `type.file` | `berkas` | reviewed | row 42 |
| `type.null` | `kusao` | draft | no row; inferred from `kw.null` |

### 5.3 Modes and reserved (4)

| ID | Answer | Status | Source |
|---|---|---|---|
| `mode.read` | `bacea` | reviewed | row 64 |
| `mode.write` | `tulaih` | reviewed | row 65 |
| `mode.append` | `tambah` | reviewed | row 66 |
| `reserved.error` | *(empty)* | todo | no worksheet row |

## 6. Messages (26 mapped, 42 todo)

The worksheet's Indonesian placeholders (`{pesan}`, `{nama}`, `{n}`, ...) are
replaced with the catalogue's neutral names (`{message}`, `{name}`, `{arity}`,
...). The Koto Payang surrounding text is kept. A message is `reviewed` only
when this substitution changes no wording and no meaning.

| ID | Koto Payang template | Status |
|---|---|---|
| `msg.import.in_module` | `daling modul '{name}': {message}` | reviewed |
| `msg.name.undefined` | `namu lao dijeloehka: {name}` | reviewed |
| `msg.name.undeclared` | `namu lao ditetakka: {name} (maki '{var_word}' duliu)` | reviewed |
| `msg.name.constant` | `'{name}' adalah konstanta ('{const_word}') nga dak bisa diubuah` | draft |
| `msg.value.div_zero` | `Pembagian dinga nol` | reviewed |
| `msg.value.operator` | `Operator '{op}' nyendak dipake kik {left} nga {right}` | reviewed |
| `msg.value.convert` | `Nynendak ngubuoah {value} jadi {target}` | draft |
| `msg.value.index_range` | `Indeks kik luwua jangkauan: {index} (panja {length})` | reviewed |
| `msg.value.index_type` | `Indeks harus bilangan buluak` | reviewed |
| `msg.value.key_missing` | `sidiak besuao kuncai: {key}` | reviewed |
| `msg.value.key_type` | `Kuncai peta harus tulisan atau bilangan buluak` | reviewed |
| `msg.value.text_immutable` | `Tulisan nyendak diubuah per huruf` | reviewed |
| `msg.call.arity` | `Pungsi butuh {arity} argumen, dibaguih {count}` | reviewed |
| `msg.call.not_function` | `Nga diimbua iduak pungsi` | reviewed |
| `msg.call.depth` | `Panggilan pungsi daling nia (lebih dari {max})` | reviewed |
| `msg.file.not_found` | `Sidiak besuao berkas: {path}` | reviewed |
| `msg.file.closed` | `Berkas lah ditutamp {path}` | reviewed |
| `msg.file.wrong_mode` | `Berkas inih dibukuak ndik '{mode}', dak buluih dipake oleh '{fn}'` | reviewed |
| `msg.syntax.bad_char` | `Baris {line}: karakter nga sidiak dikenal {text}` | reviewed |
| `msg.syntax.unexpected` | `Baris {line}: dak nyengkao {text}` | reviewed |
| `msg.syntax.expected` | `Baris {line}: diharaok {what}, basuao {text}` | reviewed |
| `msg.func.return_outside` | `Baris {line}: '{word}' hanya buluih daling pungsi` | reviewed |
| `msg.loop.break_outside` | `Baris {line}: '{word}' hanya buluih daling pangulangan` | reviewed |
| `msg.syntax.try_requires_catch` | `Baris {line}: blok '{try_word}' harus dinga '{catch_word}' nga blok penanganan` | reviewed |
| `msg.import.circular` | `Impor melingkar: {name}` | reviewed |
| `msg.syntax.escape` | `Baris {line}: urutan escape nga sidiak dikenal: \{c}` | reviewed |

The remaining 42 message IDs are `todo`; they fall back to the English base. They
are the gaps for the second pass:

```text
msg.call.builtin_arity        msg.call.depth_short
msg.dialect.header            msg.dialect.invalid
msg.dialect.unknown           msg.file.handle_required
msg.file.io                   msg.file.is_dir
msg.file.mode_invalid         msg.file.not_utf8
msg.file.path_type            msg.file.permission
msg.fn.contains_kind          msg.fn.contains_type
msg.fn.join_arity             msg.fn.length_kind
msg.fn.list_only              msg.fn.open_arity
msg.fn.range_args             msg.fn.range_arity
msg.fn.range_step             msg.fn.range_too_big
msg.fn.reverse_kind           msg.fn.sort_type
msg.fn.split_arity            msg.fn.split_kind
msg.fn.wait_number            msg.fn.wait_range
msg.import.not_found          msg.import.not_text
msg.loop.not_iterable         msg.loop.use_range
msg.name.already_const        msg.runtime.too_deep
msg.runtime.unknown_expr      msg.syntax.assign_target
msg.syntax.expected_after_name msg.syntax.reserved
msg.value.index_kind          msg.value.map_pair
msg.value.neg_type            msg.value.separator
```

Placeholder sets are checked by the loader and by the test. At no point does a
message use an Indonesian placeholder name.

## 7. `dialects/koto-payang.json`

UTF-8 JSON, 2-space indent, keys sorted, final newline. Metadata:

| Field | Value |
|---|---|
| `code` | `koto-payang` |
| `name` | `Koto Payang` |
| `status` | `review` |
| `core` | `0.6` |
| `revision` | `1` |
| `parent` | `null` |
| `license` | `CC BY-SA 4.0` |
| `maintainer` | `KerinciLang core` |
| `reviewer` | `null` |
| `sources` | `["Translation Worksheet (Koto Payang), 2026", "docs/08-multi-dialect-plan-review.md", "dialects/src/koto-payang.csv"]` |
| `orthography` | `Koto Payang spelling: final -u (kalu, selamu, daling); nga for and; multi-word concepts use underscores (lebih_nik_dari).` |
| `notes` | `Tier 1 review complete; Tier 2 second speaker pass pending. Missing IDs fall back to the English base.` |

`words` contains the 63 owned word IDs (32 Tier 1 + 29 reviewed Tier 2 + 2 draft
Tier 2); `messages` contains the 26 owned message IDs. The 48 `todo` IDs are
absent, so the loader resolves them from `base`.

Expected report:

```text
tiers:      {1: (32, 32), 2: (57, 104), 3: (0, 1)}
fallbacks:  48 (all source "base")
missing:    48
problems:   []
```

`dialects/koto-payang.md` records:

1. provenance and the speaker name from the worksheet (Rizka Hanifa Khairany);
2. the orthography rules;
3. the mapping decisions (`elif` is not an ID; `match` → `switch`;
   `except` → `catch`; declaration phrases; the `impor`/`masukka` choice; the
   `daftar`/`lis` choice; typo corrections);
4. the review record: first pass normalized 2026-11-02, `status: review`,
   `reviewer: null`, second speaker pass pending;
5. the 48-ID gap summary and the instruction not to invent answers;
6. the change policy and authority (`koto-payang.json` is runtime data).

## 8. Runtime behavior

No code change is expected:

- `load_dialect("koto-payang")` succeeds with no blocking problems.
- `# dialek: koto-payang` and `--dialek koto-payang` select the file.
- A program using only owned IDs runs with no fallback warning.
- A program using a missing ID (for example `list(1, 2)` for `fn.list`) falls
  back to the base word once and warns once per `(dialect, id)`.
- `--ketat` exits 0 because all Tier 1 IDs are owned. The runtime strict check
  is Tier 1 only, so the Tier 2 gaps do not fail it. `cek_dialek --ketat` also
  exits 0 for a `review` dialect.
- `python3 tools/cek_dialek.py --kode koto-payang` prints
  `koto-payang: tier 1 32/32, tier 2 57/104, tier 3 0/1` and exits 0.
- `python3 tools/cek_dialek.py --semua` exits 0.
- The JSON and MD ship in the wheel and the zipapp because `dialects/*.json` is
  already package data. The CSV is working data, not packaged.

## 9. Tests: `tests/test_koto_payang.py`

Plain-Python style, `tempfile` for temporary programs.

1. **Artifacts and load.** CSV, JSON, and MD exist; the JSON is sorted, indented,
   LF, no BOM; `load_dialect` reports no problems.
2. **Metadata.** Exact fields from section 7; `status: review`, `reviewer: null`.
3. **Completeness.** `tiers()` is `{1: (32, 32), 2: (57, 104), 3: (0, 1)}`;
   `fallbacks` and `missing()` are exactly the 48 expected IDs; no extra owned
   ID.
4. **Word mapping.** Every owned word equals the section 4/5 table; the 32 Tier
   1 IDs are all owned; `type.bool`, `fn.list`, `fn.map`, `fn.contains`,
   `fn.wait`, and `reserved.error` are absent.
5. **Message mapping.** Every owned template equals section 6; placeholders
   match the catalogue; the 42 todo IDs are absent.
6. **CSV contract.** 137 rows; first five columns mirror the catalogue; the
   status counts are 85/4/48; every Tier 1 row is `reviewed`; no answer has a
   slash, comma, space, uppercase, or trailing `()`; `periksa --siap` says ready
   for `review` and not ready for `approved`.
7. **Selection and fallback.** A Koto Payang program prints the expected output
   with no warnings; a missing-ID program prints the base word and one warning;
   header and `--dialek` agree; `--ketat` exits 0.
8. **Gate.** `cek_dialek --kode koto-payang`, `--ketat`, and `--semua` exit 0;
   the summary is exact.
9. **No regression.** The eight earlier suites stay green; `compileall`,
   `build.py`, and `dist/krc.pyz` from a temp directory pass; both generators
   produce no diff.

The test reads the committed CSV/JSON; it never writes into `dialects/`.

## 10. Boundaries

### Always

- Map only what the worksheet or the user supplied; never invent a word or
  message.
- Keep neutral placeholders.
- Keep `status: review` and `reviewer: null` until the second pass.
- Document every alternative and every gap.
- Keep all existing suites and expected outputs unchanged.

### Ask first

- Promoting the file to `approved`, naming a reviewer, or claiming Tier 2 is
  reviewed.
- Filling a `todo` with a guessed word or message.
- Changing the worksheet schema, the loader, the gate, or the CSV tool.
- Changing a Siulak word, test expectation, or tutorial output.

### Never

- Auto-ingest the DOCX.
- Copy a Siulak word into Koto Payang to close a gap.
- Carry `/`, `,`, spaces, uppercase, or Indonesian placeholders into the JSON.
- Mark a row `reviewed` when it is a gloss, an alternative, or a typo guess.
- Edit an existing test to make this module pass.

## 11. Success criteria

1. The three artifacts exist and are committed.
2. Tier 1 is 32/32 reviewed; `cek_dialek --kode koto-payang` reports it and
   exits 0.
3. The JSON owns exactly 89 IDs (63 words + 26 messages) and falls back for
   exactly 48; every fallback is listed in the MD.
4. A Koto Payang program runs with its own words, types, modes, and mapped
   messages; a missing ID warns once and still runs.
5. `periksa --siap` passes `review` and fails `approved` with the Tier 2 count.
6. All eight suites, `compileall`, `build.py`, and `dist/krc.pyz` pass.
7. The review record makes the next step unambiguous: 42 messages, 6 words, and
   2 type/message drafts remain for the second speaker pass.

## 12. Decisions

| # | Decision | Recommendation |
|---|---|---|
| D1 | Target `review`, not `approved`. | Yes: Tier 1 complete; Tier 2 needs a speaker. |
| D2 | Hand-map the DOCX; no importer. | Yes: it has no IDs and too many ambiguities. |
| D3 | Underscore-join multi-word answers. | Yes: `netakka_variabel`, `samu_dinga`, `lebih_nik_dari`. |
| D4 | Keep neutral English placeholders. | Yes: the worksheet's Indonesian placeholders are rewritten. |
| D5 | Missing IDs stay `todo` and fall back. | Yes: no invented Koto Payang. |
| D6 | `kw.import` = `impor`, not `masukka`. | Yes: `masukka` is already `kw.input`. |
| D7 | `kw.begin` = `mulai`, `kw.end` = `selesai`. | User-supplied 2026-11-02. |
| D8 | The second pass is a separate, explicit step. | Yes: it may promote the file to `approved`. |

## 13. Next step

On approval: archive the current plan/todo, write `tasks/plan.md` and
`tasks/todo.md`, create the CSV skeleton, fill the mapping by hand, export the
JSON with `lembar_kerja.py json`, write the MD and tests, then run all eight
suites, `cek_dialek`, the generators, `compileall`, `build.py`, and
`dist/krc.pyz` from a temp directory.
