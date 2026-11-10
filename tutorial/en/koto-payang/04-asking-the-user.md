# Lesson 4: Asking the user

`masukka()` waits for the user to type something, then gives it back as text.

```krc masukan=Budi
# dialek: koto-payang
nytak "Siapa namamu?"
netakka_variabel nama = masukka()
nytak "Halo, " + nama
```

```hasil
Siapa namamu?
Halo, Budi
```

(This example was run with the input `Budi`, as if the user had typed "Budi".)

## Input is always text

Even if the user types a number, `masukka()` gives you **text**. This is a common trap:

```krc masukan=20
# dialek: koto-payang
nytak "Umur?"
netakka_variabel umur = masukka()
nytak tipe(umur)
nytak umur + 1
```

```hasil
Umur?
tulisan
201
```

`"20" + 1` joins text, so the result is `"201"`. To calculate, first turn the text into a number with `bilangan_buluak`.

```krc masukan=20
# dialek: koto-payang
nytak "Umur?"
netakka_variabel umur = bilangan_buluak(masukka())
nytak tipe(umur)
nytak "Tahun depan: " + (umur + 1)
```

```hasil
Umur?
bilangan_buluak
Tahun depan: 21
```

## Conversion functions

| Function | Converts to | Example | Result |
|---|---|---|---|
| `bilangan_buluak(x)` | whole number | `bilangan_buluak("42")` | `42` |
| `bilangan_buluak(x)` | (decimals are cut off) | `bilangan_buluak(3.7)` | `3` |
| `desimal(x)` | decimal | `desimal("2.5")` | `2.5` |
| `tulisan(x)` | text | `tulisan(12)` | `"12"` |

```krc
# dialek: koto-payang
nytak bilangan_buluak("42") + 1
nytak bilangan_buluak(3.7)
nytak desimal("2.5") * 2
nytak tulisan(12) + "!"
```

```hasil
43
3
5.0
12!
```

## When the input cannot be converted

Turning "dua puluh" ("twenty") into a number is impossible, and your program stops with an error message:

```krc-error masukan=dua puluh
# dialek: koto-payang
netakka_variabel umur = bilangan_buluak(masukka())
nytak umur
```

```hasil
Kesalahan: Nynendak ngubuoah "dua puluh" jadi bilangan_buluak
```

In [Lesson 12](12-errors.md) you will learn to handle errors like this gracefully.

## Example: a small calculator

```krc masukan=8|5
# dialek: koto-payang
nytak "Bilangan pertama?"
netakka_variabel a = bilangan_buluak(masukka())
nytak "Bilangan kedua?"
netakka_variabel b = bilangan_buluak(masukka())
nytak a + " + " + b + " = " + (a + b)
nytak a + " * " + b + " = " + (a * b)
```

```hasil
Bilangan pertama?
Bilangan kedua?
8 + 5 = 13
8 * 5 = 40
```

## Summary

- `masukka()` reads one line as text.
- `bilangan_buluak`, `desimal` and `tulisan` convert between kinds.
- Convert input before calculating with it.

## Exercises

1. Ask for a name and a city, then print: `Budi tinggal di Sungai Penuh` ("lives in").
2. Ask for two numbers and print their average.
3. Ask for the length of a square's side and print its area.

Answers: [answers.md](answers.md#lesson-4). Continue to [Lesson 5](05-decisions.md).

---
*Generated from the Siulak lesson. Code and inline code use Koto Payang
(status: approved).*
