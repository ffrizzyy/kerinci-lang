# Lesson 1: Hello, world

The first program is almost always a greeting. In KerinciLang the word for "print" is `nytak`.

```krc
# dialek: koto-payang
nytak "Halo, dunia"
```

```hasil
Halo, dunia
```

Text is written between double quotation marks `"`. Numbers are written without quotation marks.

## Several lines

Each `nytak` writes one line. The program runs from top to bottom.

```krc
# dialek: koto-payang
nytak "Halo, dunia"
nytak "Saya belajar KerinciLang"
nytak 2026
```

```hasil
Halo, dunia
Saya belajar KerinciLang
2026
```

## Comments

The `#` sign turns the rest of the line into a comment. The computer ignores it; a comment is a note for humans.

```krc
# dialek: koto-payang
# this is a comment, it is not run
nytak "Halo"   # a comment may also come at the end of a line
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
# dialek: koto-payang
nytak "baris satu\nbaris dua"
nytak "nama\tumur"
nytak "dia berkata \"halo\""
nytak "C:\\folder\\berkas.txt"
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
# dialek: koto-payang
nytak "Halo
```

```hasil
Kesalahan: Baris 2: karakter nga sidiak dikenal '"'
```

And here `nytak` is given nothing to print:

```krc-error
# dialek: koto-payang
nytak
```

```hasil
Kesalahan: Baris 3: dak nyengkao ''
```

## Summary

- `nytak` displays a value.
- Text uses double quotation marks; numbers do not.
- `#` makes a comment.
- `\n` makes a new line inside text.

The messages (`Kesalahan: ...`) are in Indonesian for now; the [glossary](glossary.md#error-messages) explains what each one means.

## Exercises

1. Print your name.
2. Print three lines of a short poem with a single `nytak` (hint: `\n`).
3. Print a sentence that contains quotation marks, for example: He said "good morning".

Answers: [answers.md](answers.md#lesson-1). Continue to [Lesson 2](02-barang.md).

---
*Generated from the Siulak lesson. Code and inline code use Koto Payang
(status: approved).*
