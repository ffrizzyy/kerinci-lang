# Lesson 0: Setup

KerinciLang is a programming language whose words come from the Kerinci language, Siulak dialect. You write programs with words like `nyetak`, `kalu`, `selamo` and `guno`.

This tutorial is written in English, while all the code and programming terms use Kerinci. A list of every word is in the [glossary](glossary.md).

## What you need

1. A computer with **Python 3.9 or newer** (3.11 or newer is recommended).
2. The single file `krc.pyz` (no installation) or the full KerinciLang project.
3. Any text editor (Notepad, VS Code, and so on). Save programs in files ending in `.krc`, encoded as UTF-8.

## How to run a program

With `krc.pyz`:

```bash
python3 krc.pyz halo.krc
```

Or, if you installed it with `pip install .`:

```bash
krc halo.krc
```

## The REPL: trying one line

Type `krc` (or `python3 krc.pyz`) with no file name to open the REPL. You can type one line and see the result straight away. Press `Ctrl+D` to leave.

```text
>>> nyetak 2 + 3
5
>>> barang nama = "Budi"
>>> nyetak "Halo, " + nama
Halo, Budi
```

To try a short piece of code without creating a file:

```bash
python3 krc.pyz -c 'nyetak "Halo"'
```

## How to read this tutorial

Every code example is a complete program that you can copy and run. Its output is shown underneath. An example like this:

```krc
nyetak "Contoh"
```

```hasil
Contoh
```

Each lesson ends with exercises. The answers are in [answers](answers.md), but try them yourself first.

## About the example words

On Windows, type `python` or `py` where this tutorial says `python3`.

The keywords are Kerinci, but the names and messages inside the example programs are mostly **Indonesian**, the everyday language of the people the tutorial was first written for. Here are the words you will meet most often:

| Word | Meaning | Word | Meaning |
|---|---|---|---|
| `nama` | name | `kota` | city |
| `umur` | age | `nilai` | score, value |
| `siswa` | student | `buah` | fruit |
| `harga` | price | `jumlah` | amount, count |
| `kata` | word | `kalimat` | sentence |
| `hari` | day | `pesan` | message |
| `halo` | hello | `sapa` | greet |
| `luas` | area | `rata_rata` | average |
| `tebak` | guess | `rahasia` | secret |
| `terbesar` | largest | `terkecil` | smallest |

You will also see the names Budi, Sari, Dewi, Andi and Rina (common Indonesian first names), and the fruits `pisang` (banana), `apel` (apple), `jeruk` (orange) and `mangga` (mango). Whenever a lesson needs a word that matters, it explains it.

The messages the interpreter prints when something goes wrong (`Kesalahan: ...`) are also Indonesian for now. The [glossary](glossary.md#error-messages) translates all the common ones.

Ready? Continue to [Lesson 1](01-hello-world.md).
