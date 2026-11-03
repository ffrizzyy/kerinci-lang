# KerinciLang tutorial

> **Generated tutorial:** the code and inline code below use Koto Payang (status: review). The prose is the English Siulak lesson.

Learn to program with words from the Kerinci language. The explanations are in English; all the code uses Kerinci words (Koto Payang dialect).

## Lessons

| # | Lesson | New words |
|---|---|---|
| 0 | [Setup](00-setup.md) | how to run a program |
| 1 | [Hello, world](01-hello-world.md) | `nytak`, `#` |
| 2 | [Barang (variables)](02-barang.md) | `netakka_variabel`, `netakka_konstanta`, `tipe` |
| 3 | [Arithmetic and joining text](03-arithmetic.md) | `+ - * / %`, `panja`, `tambah`, `kura`, `kali`, `bagi` |
| 4 | [Asking the user](04-asking-the-user.md) | `masukka`, `bilangan_buluak`, `desimal`, `tulisan` |
| 5 | [Making decisions](05-decisions.md) | `kalu`, `nga_laen`, `samu_dinga`, `nga`, `atau`, `iduak`, `betiu`, `salah` |
| 6 | [Repeating](06-loops.md) | `selamu`, `ndik`, `daling`, `rentang`, `slese`, `lanjutka` |
| 7 | [Lists](07-lists.md) | `tambahka`, `contains`, `terurut`, `tebaluik` |
| 8 | [Guno: functions](08-guno.md) | `jeloehka`, `baluikka` |
| 9 | [Maps and pilih](09-maps-and-pilih.md) | `kamus`, `cocokka` |
| 10 | [Working with text](10-text.md) | `pecah`, `basatau` |
| 11 | [Files](11-files.md) | `bukuak`, `bacea`, `tulaih`, `tutamp`, `ngapih_berkas` |
| 12 | [Handling errors](12-errors.md) | `cubea`, `kecuali`, `timbaoka` |
| 13 | [Project: a gradebook](13-project.md) | `impor`, everything you learned |

Also: [answers to the exercises](answers.md) and the [glossary](glossary.md) (every Kerinci word with its meaning, plus a table that explains the interpreter's error messages).

**Indonesian version:** the same lessons are available in Indonesian in [id/](../../id/koto-payang/README.md).

**Koto Payang edition:** the same lessons are generated with Koto Payang code in `tutorial/en/koto-payang/` and `tutorial/id/koto-payang/`. Koto Payang is at `status: review`; each generated index lists the base words its lessons still borrow (`contains` and `boolean`). Those are not invented replacements.

## Every example has been tested

Every code example in the tutorial is run automatically, and the output printed under it is compared with the real output. After changing the language, run:

```bash
python3 tools/sinkron_tutorial.py           # check every example
python3 tools/sinkron_tutorial.py --tulis   # refresh the printed outputs
```

## Writing new examples

Code blocks in the tutorial use special kinds (the name goes right after the three backticks):

| Start of the block | Meaning |
|---|---|
| ` ```krc ` | a program that must run without error |
| ` ```krc masukan=a\|b ` | the same, with the lines `a` and `b` typed in for `tanyo()` (*masukan* means input) |
| ` ```krc-error ` | a program that must fail; its message goes in the `hasil` block |
| ` ```krc-berkas name.krc ` | a helper file (not run) that later blocks in the same lesson can use |
| ` ```hasil ` | the expected output (*hasil* means result) of the block above it; filled in by `--tulis` |

## A version in Kerinci

The explanations should be written in Kerinci by speakers. The guide is in [kerinci/README.md](../../kerinci/README.md).

## Base words used (review)

Koto Payang does not own these words yet, so the generated examples use the neutral English base word. They will change when the dialect is approved.

| ID | Word | Meaning |
|---|---|---|
| `fn.contains` | `contains` | Tells whether a list, map, or text holds a value. |
| `type.bool` | `boolean` | Type name returned by the type built-in. |

---
*Generated from the Siulak lesson. Code and inline code use Koto Payang
(status: review).*
