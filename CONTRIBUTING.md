# Contributing

KerinciLang exists to help preserve the Kerinci language. Because of that, **Kerinci speakers, not programmers, decide whether a word is right.** The most valuable help comes from speakers, and you do not need to know how to program.

*Ringkasan dalam bahasa Indonesia ada di bagian bawah.*

## The main rule about words

- New words and corrections must come from **the dictionary or from speakers**. They must never be guessed, invented, or machine-translated.
- Decisions about words are recorded in the worksheet for that dialect and in [`docs/02-vocabulary-worksheet.md`](docs/02-vocabulary-worksheet.md) (the Siulak "Decisions log"), with their source.
- Each dialect has its own speakers and its own file. There is **no standard dialect**. Siulak is the first dialect and is frozen at its v0.5 vocabulary for compatibility; Koto Payang is the next, at `review`.
- If speakers disagree, write the disagreement down in the dialect's notes file; do not hide it.
- Ask permission before naming anyone as a contributor.

## If you speak Kerinci

1. **Check the words.** Open [`tutorial/glossary.md`](tutorial/glossary.md) for every word, its meaning in the language, and an example. The questions that speakers have already approved, and the two still open, are in the "Things to check with speakers" section of [`docs/02-vocabulary-worksheet.md`](docs/02-vocabulary-worksheet.md).
2. **Tell us what you find** through an issue ("Koreksi kosakata" for a correction, or "Kata yang belum ada" for a missing word), or send it straight to the maintainers if you do not use GitHub. Just write the word, what it does, and your suggestion.
3. **Write the tutorial in Kerinci.** Instructions are in [`tutorial/kerinci/README.md`](tutorial/kerinci/README.md).
4. **Translate the error messages.** The interpreter's messages are in Indonesian for now (the list is in the "Error messages" table of [`tutorial/glossary.md`](tutorial/glossary.md#error-messages)).
5. **Suggest words for things that have no name yet**: upper and lower case, finding a position in text, replacing part of a text, random numbers, dates, and so on. See "Words still missing" in `docs/02-vocabulary-worksheet.md`.

## If you teach or learn

- Try the [tutorial](tutorial/README.md) in a class or on your own, and tell us which parts are confusing.
- Report words that feel strange to Kerinci-speaking students.

## If you program

Thank you! A few guidelines:

```bash
python3 build.py                    # every offline check, then dist/krc.pyz
python3 tools/cek_dialek.py --semua # validate every dialect file
python3 tests/test_release.py       # wheel build/install/run (before a release)
```

- **All tests must pass** before you send a change. CI runs them on Python 3.9 to 3.13.
- **Adding or correcting a word:** the runtime reads `dialects/<code>.json`, and the canonical answers live in `dialects/src/<code>.csv`. The `KEYWORDS` names in `kerincilang.py` are read-only compatibility exports; do not use them to add a dialect word. Follow [`docs/09-adding-a-dialect.md`](docs/09-adding-a-dialect.md): scaffold, fill the worksheet, run `lembar_kerja.py`, then regenerate the grammar and tutorial. Siulak is frozen; a new Siulak word is a product decision, not a drive-by edit.
- **New features** need tests (in `tests/test_kerincilang.py`), notes in [`docs/03-syntax-design.md`](docs/03-syntax-design.md), and an entry in [`CHANGELOG.md`](CHANGELOG.md).
- Keep the project's character: one interpreter file, no dependencies, clear error messages.
- Do not add new Kerinci words in code without a source from the dictionary or a speaker. If a feature needs a word that does not exist, use a clearly marked fallback (such as `boolean` in the neutral base) and open a "Kata yang belum ada" issue.

## If you add a dialect

Read [`docs/09-adding-a-dialect.md`](docs/09-adding-a-dialect.md) from start to
finish. It covers the worksheet, the status ladder, the tutorial tree, the
editor grammar, and the tests. A dialect is data, not a Python change, and it
never borrows another dialect's words to fill a gap. Before a release, follow
[`RELEASING.md`](RELEASING.md).

## Conduct

This language belongs to its speakers. Respect speakers and elders, accept corrections openly, and never talk down to a beginner's question.

---

## Ringkasan dalam bahasa Indonesia

KerinciLang dibuat untuk melestarikan bahasa Kerinci, jadi **penutur bahasa Kerinci yang menentukan apakah sebuah kata benar**, bukan pembuat program. Kamu tidak perlu bisa memprogram untuk membantu.

- **Penutur:** periksa kata-katanya di [`tutorial/id/glosarium.md`](tutorial/id/glosarium.md), usulkan koreksi atau kata untuk hal yang belum punya nama lewat templat issue, tulis tutorial dalam bahasa Kerinci ([`tutorial/kerinci/README.md`](tutorial/kerinci/README.md)), atau terjemahkan pesan kesalahan interpreter yang sekarang masih berbahasa Indonesia.
- **Aturan kosakata:** kata baru dan koreksi harus berasal dari kamus atau penutur, tidak boleh ditebak atau diterjemahkan mesin. Keputusan dicatat di lembar kerja dialek itu dan di `docs/02-vocabulary-worksheet.md` beserta sumbernya. Tidak ada dialek acuan; Siulak adalah dialek pertama dan dibekukan pada kosakata v0.5. Panduan menambah dialek ada di `docs/09-adding-a-dialect.md`.
- **Pemrogram:** semua pemeriksaan offline harus lulus (`python3 build.py`), dan `python3 tools/cek_dialek.py --semua` harus bersih; fitur baru perlu tes, dokumentasi, dan catatan di `CHANGELOG.md`; pertahankan satu berkas interpreter tanpa dependensi.
