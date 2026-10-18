# Lesson 1: Hello, world

The first program is almost always a greeting. In KerinciLang the word for "print" is `nyetak`.

```krc
nyetak "Halo, dunia"
```

```hasil
Halo, dunia
```

Text is written between double quotation marks `"`. Numbers are written without quotation marks.

## Several lines

Each `nyetak` writes one line. The program runs from top to bottom.

```krc
nyetak "Halo, dunia"
nyetak "Saya belajar KerinciLang"
nyetak 2026
```

```hasil
Halo, dunia
Saya belajar KerinciLang
2026
```

## Comments

The `#` sign turns the rest of the line into a comment. The computer ignores it; a comment is a note for humans.

```krc
# this is a comment, it is not run
nyetak "Halo"   # a comment may also come at the end of a line
```

```hasil
Halo
```

## Special characters inside text

Inside text, the `\` sign has a special meaning:

| Write | Result |
|---|---|
| `\n` | start a new line |
| `\t` | a tab (a wide gap) |
| `\"` | a quotation mark |
| `\\` | one `\` sign |

```krc
nyetak "baris satu\nbaris dua"
nyetak "nama\tumur"
nyetak "dia berkata \"halo\""
nyetak "C:\\folder\\berkas.txt"
```

```hasil
baris satu
baris dua
nama	umur
dia berkata "halo"
C:\folder\berkas.txt
```

## Your first error

Everyone makes mistakes. An error message tells you what needs fixing. Here the closing quotation mark was forgotten:

```krc-error
nyetak "Halo
```

```hasil
Kesalahan: Baris 1: karakter tidak dikenal '"'
```

And here `nyetak` is given nothing to print:

```krc-error
nyetak
```

```hasil
Kesalahan: Baris 2: tidak terduga ''
```

## Summary

- `nyetak` displays a value.
- Text uses double quotation marks; numbers do not.
- `#` makes a comment.
- `\n` makes a new line inside text.

The messages (`Kesalahan: ...`) are in Indonesian for now; the [glossary](glossary.md#error-messages) explains what each one means.

## Exercises

1. Print your name.
2. Print three lines of a short poem with a single `nyetak` (hint: `\n`).
3. Print a sentence that contains quotation marks, for example: He said "good morning".

Answers: [answers.md](answers.md#lesson-1). Continue to [Lesson 2](02-barang.md).
