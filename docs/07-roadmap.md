# 07. Roadmap and Checklists

## Done

- [x] Language name: KerinciLang, extension `.krc`
- [x] Siulak vocabulary table provided (47 entries)
- [x] Core language: variables, constants, arithmetic, strings, logic, `kalu`/`lain kalu`/`lain`, `selamo`, `putuh`, `lanjut`, functions, closures, `nyetak`, `tanyo`
- [x] `mulai` / `habih` as block delimiters
- [x] Keyword uniqueness check at startup
- [x] 271 language checks + 550 baseline tutorial code blocks + the generated Koto Payang trees
- [x] Conflicts resolved: `salah` = false, `kelihu` = error (reserved); try/catch/raise = `cubo`/`tangkap`/`ngangkat`; `kurang` = subtract, `kurang_daripado` / `lebih_daripado` = less / greater than
- [x] Comparison words (`samo`, `dak_samo`, `lebih_daripado`, `kurang_daripado`, `lebih_samo`, `kurang_samo`)
- [x] VS Code syntax highlighting generated as a union of every dialect's words
- [x] Example programs in `examples/`
- [x] `krc` command (`pip install .`), single-file build `dist/krc.pyz`, multi-line REPL, `-c`, `--version`, clean exit codes

## Milestone 1: Vocabulary review by speakers (done)

- [x] Send the keyword list to Siulak speakers for review
- [x] Speakers approved every item in the checklist (see `02`)
- [ ] Record the dictionary bibliography in `02` and credit it in `README.md` and `LICENSE-DOCS.md`

## Milestone 2: first public release (v0.5)

- [x] Tutorial: 13 lessons, answers, glossary in English and Indonesian; every code sample tested
- [x] `LICENSE` (MIT), `LICENSE-DOCS.md` (CC BY-SA 4.0), `CONTRIBUTING.md`, `CHANGELOG.md`
- [x] Repository layout, `.gitignore`, CI workflow, issue templates
- [ ] Replace the copyright holder in `LICENSE`; add the full CC BY-SA 4.0 text; credit the dictionary (see `06`)
- [ ] Translate the error messages and REPL banner into Kerinci with speakers
- [ ] Create the public repository and push; attach `dist/krc.pyz` to a `v0.5` release

## Milestone 3: v0.2, data (done)

- [x] `daftar` literals, indexing and element assignment
- [x] `panjang()` and `daftar()` built-ins
- [x] `untuk` loop over lists, text and counts
- [x] Arithmetic built-ins: `tambah`, `kurang`, `kali`, `bagi`
- [x] Exact division gives whole numbers (`6 / 3` is `3`)
- [x] Words from speakers: `alem`, `jarak`, `nambahkah`, `isi`, `milih`, `pulang` (v0.2.1)
- [ ] Speaker review of the v0.2.1 words (checklist in `02`)
- [ ] Newline-terminated statements (removes the `-2` ambiguity)
- [x] String escapes (`\n`, `\t`, `\"`, `\\`) (done in v0.4)

## Milestone 4: v0.3, types and modules (done)

- [x] `bilangan`, `pecahan`, `kato` conversions
- [x] `mecem` (type of a value)
- [x] `peta` maps (literals, indexing, iteration, `panjang`, `isi`)
- [x] `pilih` multi-way choice
- [x] `ambik` imports (relative paths, run-once, circular check)
- [x] `balik` outside a function is a clean error
- [ ] Kerinci word for "boolean" (placeholder in `mecem`)
- [ ] Speaker review of the v0.3 words (checklist in `02`)

## Milestone 5: v0.4 and v0.5, files, time, errors, text (done)

- [x] `bukak`, `baco`, `tulis`, `tutup`, `hapus` (UTF-8 text files, three modes, line-by-line reading)
- [x] `nantik`
- [x] Error handling: `cubo { } tangkap pesan { }` and `ngangkat "pesan"` (words from speakers)
- [x] `pisah` and `disatu` for splitting and joining text
- [x] Runaway recursion gives a clear error instead of crashing
- [x] `berkas` confirmed as the type name for open files
- [ ] A word for "boolean" (placeholder in `mecem`)
- [ ] Decide what `kelihu` ("error") should be used for

## Milestone 6: Community

- [ ] Classroom pilot in a school
- [x] Tutorial in English (13 lessons) and Indonesian (`tutorial/id/`)
- [ ] Tutorial prose in Kerinci (needs speakers: `tutorial/kerinci/README.md`)
- [ ] Recruit a co-maintainer from the community

## Milestone 7: Deepen the culture

- [ ] Prototype grammar-inspired features with speakers
- [ ] Investigate Incung script support
- [ ] Browser playground (transpile to JavaScript), so people can try the language without installing Python
- [ ] More text tools (uppercase/lowercase, find, replace, trim), random numbers, dates (all need words)

## Milestone 8: v0.6.0, multi-dialect (done; release pending)

- [x] Neutral ID catalogue in `core/ids.json`; the engine compares IDs, never words
- [x] Dialect loader and validation: `dialects/<code>.json`, parents, fallbacks, status gates
- [x] `# dialek:` header, `--dialek`, per-file vocabulary, fallback warnings, `--ketat`
- [x] `krc migrasi` for old programs and their literal imports
- [x] `krc terjemah` for a lossless rewrite between dialects
- [x] Worksheet pipeline (`lembar_kerja.py buat/rangka/periksa/laporan/json`) and the canonical CSVs
- [x] Siulak frozen at its v0.5 vocabulary as `dialects/siulak.json` (`draft`)
- [x] Koto Payang at `status: review`: 32/32 Tier 1, 57/104 Tier 2, 0/1 Tier 3
- [x] Generated English and Indonesian Koto Payang tutorial trees, every block tested
- [x] One union VS Code grammar, `docs/09-adding-a-dialect.md`, and `RELEASING.md`
- [ ] Koto Payang Tier 2 vocabulary (optional; the dialect is included at `review`)
- [ ] Semurup, Sungai Liuk, Rawang: speaker-approved files first, then the new-dialect guide
- [x] Tag and publish `v0.6.0`

## Weekly rhythm

| Day | Focus |
|---|---|
| Mon | Vocabulary or speaker feedback |
| Wed | Code (one feature) |
| Fri | Docs or tutorial |
| Weekend | Test with a friend or student |
