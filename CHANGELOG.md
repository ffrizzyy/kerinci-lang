# Changelog

All notable changes to KerinciLang. Versions below 1.0 may still change vocabulary after review by speakers.

## 0.6.0 (2026-11-02)

One language, many dialects. A program written in any dialect means the same
thing and runs on the same interpreter. Dialects are data, not code: a new
dialect is a JSON file with its own speakers, worksheet, and notes. An
incomplete dialect falls back to the neutral English base and warns once per
missing ID; it never invents or borrows a word. There is no standard dialect.

| Dialect | Code | Status | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|---|---|
| Siulak | `siulak` | `draft` (frozen v0.5) | 32/32 | 104/104 | 1/1 |
| Koto Payang | `koto-payang` | `review` | 32/32 | 57/104 | 0/1 |

Siulak owns every ID but stays `draft` because this release freezes the
approved v0.5 vocabulary for compatibility instead of running a new approval
pass. Koto Payang owns 89 of the 137 IDs; a second speaker pass is required
before `approved`.

**New**
- `core/ids.json`: neutral IDs, tiers, namespaces, arities, and message
  placeholders. The engine compares IDs, never words.
- Dialect loader and validation: `dialects/<code>.json`, parent chains, status
  gates, the neutral base, and one deterministic error list.
- Per-file selection: a line-1 `# dialek: <code>` header, `--dialek CODE`, and
  fallbacks. Header > `--dialek` > Siulak.
- `--ketat` and `cek_dialek.py --ketat`: fail an `approved` dialect that still
  takes a Tier 1 word from the base.
- `krc migrasi`: add a header to old programs and their literal imports,
  without running them.
- `krc terjemah`: rewrite one file between dialects losslessly; refuse rather
  than guess.
- Worksheet pipeline: `tools/lembar_kerja.py buat`, `rangka`, `perbarui`,
  `periksa`, `docx`, `baca`, `laporan`, and `json`. `rangka` creates a valid
  `draft` JSON skeleton and notes stub.
- Generated English and Indonesian Koto Payang tutorial trees, with every block
  run and compared against the Siulak baseline.
- One union VS Code grammar that highlights every dialect's valid words, and
  `vscode-extension/README.md`.
- `docs/09-adding-a-dialect.md`, the executable contributor guide, and
  `RELEASING.md`, the release checklist.

**Compatibility**
- Existing v0.5 programs still run. A file without a header uses Siulak.
- `krc migrasi` adds the header, including to literal imports.
- No Siulak word, message, example, or tutorial output changed. The 550
  baseline tutorial blocks and the 271 language checks are the oracle.

**Fallbacks**
- A missing word uses the English base and prints one warning per ID on stderr.
  Stdout stays clean and the exit code does not change.
- `--ketat` exits 2 only for an `approved` dialect with a Tier 1 fallback.
- Koto Payang's generated tutorial lists the two base words its lessons use:
  `contains` and `boolean`.

**Not in this release**
- Semurup, Sungai Liuk, and Rawang are **not included**. No speaker-approved
  file exists for them. `docs/09-adding-a-dialect.md` is the path to add one;
  they are not stubbed, renamed, guessed, or copied from Siulak.

**Tests**
- 271 language checks, 550 baseline tutorial blocks, the dialect and worksheet
  suites, the migration suite, the 173-check translator suite, the generated
  tutorial suite, and the offline docs/release suite.
- `tests/test_release.py` is the separate wheel smoke: it builds a clean-copy
  wheel, checks its contents and the absence of CSV/bytecode, installs it, and
  runs both dialects from outside the checkout.

## 0.5.0 (2026-10-17)

**Review:** every word in the vocabulary checklist was reviewed and approved by Kerinci speakers. Two questions remain open: a word for "boolean", and what `kelihu` should be used for.

**New words (from Kerinci speakers)**
- `cubo` / `tangkap` for try / catch, and `ngangkat` to raise an error. **Breaking:** replaces the provisional `kelihu { } lain e { }` from 0.4. `kelihu` ("error") is now reserved.
- `pisah(teks, pemisah)` splits text; `disatu(daftar, pemisah)` joins a list.
- `berkas` confirmed as the file type name returned by `mecem`.

**Tutorial and documentation**
- 13-lesson tutorial in English (with an Indonesian copy in `tutorial/id/`), with answers and a glossary. All 550 code blocks are run by the test suite, and the printed output is checked against the real output.
- Guide for Kerinci speakers who want to write the tutorial prose in Kerinci.

**Project**
- `GETTING-STARTED.md`: a step-by-step guide for a newly unzipped copy.
- Repository layout (`docs/`, `examples/`, `tutorial/`, `tools/`), licences (MIT for code, CC BY-SA 4.0 for docs), `CONTRIBUTING.md`, CI workflow for Python 3.9 to 3.13, issue templates for vocabulary corrections.

## 0.4.0

- Files: `bukak`, `baco`, `tulis`, `tutup`, `hapus`; modes `"baco"`, `"tulis"`, `"nambahkah"`; line-by-line reading with `untuk ... alem`.
- `nantik` (wait).
- Error handling (provisional syntax `kelihu { } lain e { }`).
- Text escapes `\n`, `\t`, `\"`, `\\`.
- Runaway recursion gives a clear error instead of crashing (limit 400 calls on Python 3.11+, 80 before).

## 0.3.0

- Type conversion `bilangan`, `pecahan`, `kato`; `mecem` (type of a value).
- Maps (`peta`): literals, indexing, iteration.
- `pilih` multi-way choice; `ambik` imports (relative paths, each file runs once, circular imports detected).
- `balik` outside a function is a clean error.

## 0.2.1

- `alem` (in), `jarak` (range), `nambahkah`, `isi`, `milih`, `pulang`.
- **Breaking:** loops are written `untuk x alem xs { }`; counting uses `untuk i alem jarak(5) { }`.

## 0.2.0

- Lists, indexing, `untuk` loops, `panjang`, `daftar`, and the arithmetic functions `tambah`, `kurang`, `kali`, `bagi`.
- The `krc` command, a multi-line REPL, `-c`, `--version`, and a single-file build (`krc.pyz`).

## 0.1.0

- First working language: variables (`barang`, `tetap`), arithmetic, text, `kalu` / `lain kalu` / `lain`, `selamo`, `putuh`, `lanjut`, functions (`guno`, `balik`), `nyetak`, `tanyo`, comparison words, `mulai` / `habih`.
