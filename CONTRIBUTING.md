# Contributing

KerinciLang exists to help preserve the Kerinci language. Because of that, **Kerinci speakers, not programmers, decide whether a word is right.** The most valuable help comes from speakers, and you do not need to know how to program.

*Ringkasan dalam bahasa Indonesia ada di bagian bawah.*

## The main rule about words

- New words and corrections must come from **the dictionary or from speakers**. They must never be guessed, invented, or machine-translated.
- Decisions about words are recorded in [`docs/02-vocabulary-worksheet.md`](docs/02-vocabulary-worksheet.md) (the "Decisions log"), with their source.
- If speakers disagree, write the disagreement down; do not hide it. The reference dialect is **Siulak**.
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
python3 tests/test_kerincilang.py   # the language tests
python3 tests/test_tutorial.py      # every tutorial example, plus glossary coverage
python3 build.py                    # runs all tests, then builds dist/krc.pyz
```

- **All tests must pass** before you send a change. CI runs them on Python 3.9 to 3.13.
- **Adding or changing a word:** edit the value in the `KEYWORDS` table (or `WORD_OPERATORS`, `BUILTINS`) in `kerincilang.py`, then run `python3 make_highlight.py`, `python3 tools/buat_glosarium.py` (it fails if a word is missing from the glossary) and `python3 tools/sinkron_tutorial.py --tulis`. Finally run all the tests. The full recipe is in [`docs/04-implementation.md`](docs/04-implementation.md).
- **New features** need tests (in `tests/test_kerincilang.py`), notes in [`docs/03-syntax-design.md`](docs/03-syntax-design.md), and an entry in [`CHANGELOG.md`](CHANGELOG.md).
- Keep the project's character: one interpreter file, no dependencies, clear error messages.
- Do not add new Kerinci words in code without a source from the dictionary or a speaker. If a feature needs a word that does not exist, use a clearly marked placeholder (like `boolean` in `TYPE_NAMES`) and open a "Kata yang belum ada" issue.

## Conduct

This language belongs to its speakers. Respect speakers and elders, accept corrections openly, and never talk down to a beginner's question.

---

## Ringkasan dalam bahasa Indonesia

KerinciLang dibuat untuk melestarikan bahasa Kerinci, jadi **penutur bahasa Kerinci yang menentukan apakah sebuah kata benar**, bukan pembuat program. Kamu tidak perlu bisa memprogram untuk membantu.

- **Penutur:** periksa kata-katanya di [`tutorial/id/glosarium.md`](tutorial/id/glosarium.md), usulkan koreksi atau kata untuk hal yang belum punya nama lewat templat issue, tulis tutorial dalam bahasa Kerinci ([`tutorial/kerinci/README.md`](tutorial/kerinci/README.md)), atau terjemahkan pesan kesalahan interpreter yang sekarang masih berbahasa Indonesia.
- **Aturan kosakata:** kata baru dan koreksi harus berasal dari kamus atau penutur, tidak boleh ditebak atau diterjemahkan mesin. Keputusan dicatat di `docs/02-vocabulary-worksheet.md` beserta sumbernya. Dialek acuan adalah Siulak.
- **Pemrogram:** semua tes harus lulus (`python3 tests/test_kerincilang.py` dan `python3 tests/test_tutorial.py`); fitur baru perlu tes, dokumentasi, dan catatan di `CHANGELOG.md`; pertahankan satu berkas interpreter tanpa dependensi.
