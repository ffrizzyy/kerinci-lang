# KerinciLang

**A programming language with words from the Kerinci language, written in several dialects, built to help preserve and promote it.**

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

The sample above is **Siulak**, the first dialect. Programs are written with words such as `barang` (variable), `guno` (function), `kalu` (if), `selamo` (while), `nyetak` (print), and `cubo` / `tangkap` (try / catch an error). Every Siulak word is listed, with its meaning, in the [glossary](tutorial/glossary.md).

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

## Choosing a dialect

Siulak is used when a file has no dialect header. Any other dialect is named on
line 1:

```krc
# dialek: koto-payang
```

The header must be the first line. `krc --dialek CODE file.krc` sets the default
for files without a header, and the header wins over the flag. A dialect that
does not own a word falls back to the neutral English base and warns once per
ID on stderr; stdout stays clean. To add a dialect, follow
[`docs/09-adding-a-dialect.md`](docs/09-adding-a-dialect.md). It is data, not a
Python change.

## Learn

The **[tutorial](tutorial/README.md)** has 13 lessons, from "Hello, world" to a gradebook project, with exercises, answers and a [glossary](tutorial/glossary.md). The explanations are in English and the code uses Kerinci. Every code example is run automatically by the tests. An [Indonesian version](tutorial/id/README.md) is included. The same course is generated with Koto Payang code in [English](tutorial/en/koto-payang/README.md) and [Indonesian](tutorial/id/koto-payang/README.md); Koto Payang is still under review.

More example programs are in [`examples/`](examples/). The full language reference is [`docs/03-syntax-design.md`](docs/03-syntax-design.md).

## What the language can do

Variables and constants, numbers, text (with `pisah` / `disatu` to split and join), lists and maps, `kalu` / `lain kalu` / `lain`, `pilih`, `selamo` and `untuk` loops, functions (with recursion and closures), reading input, reading and writing files, error handling (`cubo` / `tangkap` / `ngangkat`), and splitting a program across files (`ambik`). It has 26 special words, 6 comparison words and 24 built-in functions. The interpreter is a single Python file with no dependencies.

## Status

Version **0.6.0**. The multi-dialect engine is complete and tested (271 language
checks and 550 baseline tutorial blocks), but dialect coverage is a separate,
speaker-gated axis.

| Dialect | Code | Status | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|---|---|
| Siulak | `siulak` | `draft` (frozen v0.5) | 32/32 | 104/104 | 1/1 |
| Koto Payang | `koto-payang` | `review` | 32/32 | 57/104 | 0/1 |

Siulak owns every ID but stays `draft` because 0.6 freezes the approved v0.5
vocabulary instead of running a new approval pass. Its 271 language tests and
550 tutorial blocks are the compatibility oracle; no Siulak word or tutorial
output changed in 0.6.

Koto Payang owns 89 of the 137 neutral IDs and falls back to the English base
for the other 48. It is included at `status: review`: its Tier 1 vocabulary is
complete, and its remaining Tier 2 rows are recorded as open rather than
guessed. The generated tutorial names the two base words its lessons actually
use (`contains` and `boolean`) instead of inventing replacements. The checklist
Siulak speakers worked through is in
[`docs/02-vocabulary-worksheet.md`](docs/02-vocabulary-worksheet.md); the Koto
Payang record is in [`dialects/koto-payang.md`](dialects/koto-payang.md).

Semurup, Sungai Liuk, and Rawang are **not in this release**. No
speaker-approved file exists for them. The guide for adding one is
[`docs/09-adding-a-dialect.md`](docs/09-adding-a-dialect.md).

The Siulak messages (for example `Kesalahan: Pembagian dengan nol`) are written
in Indonesian for now. The [glossary](tutorial/glossary.md#error-messages)
explains the common ones, and translating them into Kerinci is a good task for
speakers.

## Help

If you speak Kerinci, you can help even if you have never programmed: suggest words for things that have no name yet, or write the tutorial in Kerinci. Read **[CONTRIBUTING.md](CONTRIBUTING.md)**. If you want to add a dialect, read **[docs/09-adding-a-dialect.md](docs/09-adding-a-dialect.md)**; before a release, maintainers follow **[RELEASING.md](RELEASING.md)**. The design documents are in [`docs/`](docs/README.md).

## Vocabulary sources and credit

The vocabulary comes from a dictionary of the Siulak dialect and from Kerinci speakers. *(The dictionary's title and authors, and the names of speakers who agreed to be credited, are to be added in [LICENSE-DOCS.md](LICENSE-DOCS.md) before publication.)*

## Licence

Code: [MIT](LICENSE). Documentation, tutorial and vocabulary tables: [CC BY-SA 4.0](LICENSE-DOCS.md).

---

*Bahasa Indonesia:* KerinciLang adalah bahasa pemrograman dengan kata-kata bahasa Kerinci dalam beberapa dialek, dibuat untuk melestarikan bahasa tersebut. Tutorial lengkap dalam bahasa Indonesia ada di [`tutorial/id/`](tutorial/id/README.md), dan petunjuk untuk penutur yang ingin membantu ada di [CONTRIBUTING.md](CONTRIBUTING.md#ringkasan-dalam-bahasa-indonesia). Panduan menambah dialek ada di [`docs/09-adding-a-dialect.md`](docs/09-adding-a-dialect.md).
