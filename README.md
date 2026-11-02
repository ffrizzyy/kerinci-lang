# KerinciLang

**A programming language whose words come from the Kerinci language (Siulak dialect), built to help preserve and promote it.**

```
barang buah = ["pisang", "apel", "jeruk"]

guno sapa(nama) {
    kalu nama samo "apel" {
        nyetak "Halo, apel!"
    } lain {
        nyetak "Halo, " + nama
    }
}

untuk b alem milih(buah) {
    sapa(b)
}

cubo {
    nyetak baco("tidak-ada.txt")
} tangkap pesan {
    nyetak "Gagal: " + pesan
}
```

Programs are written with words such as `barang` (variable), `guno` (function), `kalu` (if), `selamo` (while), `nyetak` (print), and `cubo` / `tangkap` (try / catch an error). Every word is listed, with its meaning, in the [glossary](tutorial/glossary.md).

## Get started

New to this folder? Follow **[GETTING-STARTED.md](GETTING-STARTED.md)**: it takes you from unzipping to running your first program, step by step.

The short version (you need **Python 3.9 or newer**, 3.11+ recommended):

```bash
python3 dist/krc.pyz examples/contoh.krc      # run an example program
python3 dist/krc.pyz                          # interactive prompt (REPL)
python3 dist/krc.pyz -c 'nyetak "Halo"'       # run one line
```

(On Windows, use `python` or `py` instead of `python3`.) You can also install a `krc` command with `pip install .`, or run `python3 kerincilang.py` straight from the source file.

Old programs without a dialect header still run. To make their dialect explicit
and migrate their imports:

```bash
python3 dist/krc.pyz migrasi examples --semua
python3 dist/krc.pyz migrasi program.krc --kering   # preview only
```

To rewrite a program in another dialect without running it:

```bash
python3 dist/krc.pyz terjemah program.krc --ke koto-payang --out program.kot
python3 dist/krc.pyz terjemah program.krc --ke koto-payang   # print to stdout
```

The translator changes only dialect words, the header, and the direct mode
argument of `bukak`; it preserves names, comments, strings, and formatting, and
it refuses rather than guesses when the target dialect cannot express the
program losslessly.

## Learn

The **[tutorial](tutorial/README.md)** has 13 lessons, from "Hello, world" to a gradebook project, with exercises, answers and a [glossary](tutorial/glossary.md). The explanations are in English and the code uses Kerinci. Every code example is run automatically by the tests. An [Indonesian version](tutorial/id/README.md) is included.

More example programs are in [`examples/`](examples/). The full language reference is [`docs/03-syntax-design.md`](docs/03-syntax-design.md).

## What the language can do

Variables and constants, numbers, text (with `pisah` / `disatu` to split and join), lists and maps, `kalu` / `lain kalu` / `lain`, `pilih`, `selamo` and `untuk` loops, functions (with recursion and closures), reading input, reading and writing files, error handling (`cubo` / `tangkap` / `ngangkat`), and splitting a program across files (`ambik`). It has 26 special words, 6 comparison words and 24 built-in functions. The interpreter is a single Python file with no dependencies.

## Status

Version **0.5.0**. The language is complete and tested (271 language tests, plus 550 tutorial code blocks). **The vocabulary has been reviewed and approved by Kerinci speakers.** Two questions remain open: a Kerinci word for "boolean" (the type name that `mecem` returns for `betul` and `salah` is still the temporary English word `boolean`), and what the reserved word `kelihu` ("error") should be used for. The checklist that speakers worked through is in [`docs/02-vocabulary-worksheet.md`](docs/02-vocabulary-worksheet.md).

The interpreter's own messages (for example `Kesalahan: Pembagian dengan nol`) are written in Indonesian for now. The [glossary](tutorial/glossary.md#error-messages) explains the common ones, and translating them into Kerinci is a good task for speakers.

## Help

If you speak Kerinci, you can help even if you have never programmed: suggest words for things that have no name yet, or write the tutorial in Kerinci. Read **[CONTRIBUTING.md](CONTRIBUTING.md)**. The design documents are in [`docs/`](docs/README.md).

## Vocabulary sources and credit

The vocabulary comes from a dictionary of the Siulak dialect and from Kerinci speakers. *(The dictionary's title and authors, and the names of speakers who agreed to be credited, are to be added in [LICENSE-DOCS.md](LICENSE-DOCS.md) before publication.)*

## Licence

Code: [MIT](LICENSE). Documentation, tutorial and vocabulary tables: [CC BY-SA 4.0](LICENSE-DOCS.md).

---

*Bahasa Indonesia:* KerinciLang adalah bahasa pemrograman dengan kata-kata bahasa Kerinci dialek Siulak, dibuat untuk melestarikan bahasa tersebut. Tutorial lengkap dalam bahasa Indonesia ada di [`tutorial/id/`](tutorial/id/README.md), dan petunjuk untuk penutur yang ingin membantu ada di [CONTRIBUTING.md](CONTRIBUTING.md#ringkasan-dalam-bahasa-indonesia).
