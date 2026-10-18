# Changelog

All notable changes to KerinciLang. Versions below 1.0 may still change vocabulary after review by speakers.

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
