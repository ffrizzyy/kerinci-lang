# Lesson 4: Asking the user

`tanyo()` waits for the user to type something, then gives it back as text.

```krc masukan=Budi
nyetak "Siapa namamu?"
barang nama = tanyo()
nyetak "Halo, " + nama
```

```hasil
Siapa namamu?
Halo, Budi
```

(This example was run with the input `Budi`, as if the user had typed "Budi".)

## Input is always text

Even if the user types a number, `tanyo()` gives you **text**. This is a common trap:

```krc masukan=20
nyetak "Umur?"
barang umur = tanyo()
nyetak mecem(umur)
nyetak umur + 1
```

```hasil
Umur?
kato
201
```

`"20" + 1` joins text, so the result is `"201"`. To calculate, first turn the text into a number with `bilangan`.

```krc masukan=20
nyetak "Umur?"
barang umur = bilangan(tanyo())
nyetak mecem(umur)
nyetak "Tahun depan: " + (umur + 1)
```

```hasil
Umur?
bilangan
Tahun depan: 21
```

## Conversion functions

| Function | Converts to | Example | Result |
|---|---|---|---|
| `bilangan(x)` | whole number | `bilangan("42")` | `42` |
| `bilangan(x)` | (decimals are cut off) | `bilangan(3.7)` | `3` |
| `pecahan(x)` | decimal | `pecahan("2.5")` | `2.5` |
| `kato(x)` | text | `kato(12)` | `"12"` |

```krc
nyetak bilangan("42") + 1
nyetak bilangan(3.7)
nyetak pecahan("2.5") * 2
nyetak kato(12) + "!"
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
barang umur = bilangan(tanyo())
nyetak umur
```

```hasil
Kesalahan: Tidak bisa mengubah "dua puluh" menjadi bilangan
```

In [Lesson 12](12-errors.md) you will learn to handle errors like this gracefully.

## Example: a small calculator

```krc masukan=8|5
nyetak "Bilangan pertama?"
barang a = bilangan(tanyo())
nyetak "Bilangan kedua?"
barang b = bilangan(tanyo())
nyetak a + " + " + b + " = " + (a + b)
nyetak a + " * " + b + " = " + (a * b)
```

```hasil
Bilangan pertama?
Bilangan kedua?
8 + 5 = 13
8 * 5 = 40
```

## Summary

- `tanyo()` reads one line as text.
- `bilangan`, `pecahan` and `kato` convert between kinds.
- Convert input before calculating with it.

## Exercises

1. Ask for a name and a city, then print: `Budi tinggal di Sungai Penuh` ("lives in").
2. Ask for two numbers and print their average.
3. Ask for the length of a square's side and print its area.

Answers: [answers.md](answers.md#lesson-4). Continue to [Lesson 5](05-decisions.md).
