# Lesson 3: Arithmetic and joining text

## Arithmetic operators

| Operator | Meaning | Example | Result |
|---|---|---|---|
| `+` | add | `7 + 3` | `10` |
| `-` | subtract | `7 - 3` | `4` |
| `*` | multiply | `7 * 3` | `21` |
| `/` | divide | `7 / 2` | `3.5` |
| `%` | remainder | `7 % 3` | `1` |

```krc
nyetak 7 + 3
nyetak 7 - 3
nyetak 7 * 3
nyetak 7 / 2
nyetak 7 % 3
nyetak 8 / 2
```

```hasil
10
4
21
3.5
1
4
```

A division that comes out even gives a whole number (`8 / 2` is `4`). Otherwise the result is a decimal.

## Order of calculation

Multiply, divide and remainder are done before add and subtract. Parentheses `( )` change the order.

```krc
nyetak 2 + 3 * 4
nyetak (2 + 3) * 4
nyetak 10 - 2 - 3
```

```hasil
14
20
5
```

## Calculating with barang

```krc
barang harga = 15000
barang jumlah = 3
barang total = harga * jumlah
nyetak "Total: " + total
```

```hasil
Total: 45000
```

## Joining text

The `+` sign also joins text. If one side is text, the other side is automatically turned into text.

```krc
barang depan = "Budi"
barang belakang = "Santoso"
nyetak depan + " " + belakang
nyetak "Umur: " + 20
nyetak "Benar? " + betul
```

```hasil
Budi Santoso
Umur: 20
Benar? betul
```

Be careful: the order matters. If both sides are numbers, `+` adds them instead of joining.

```krc
nyetak 1 + 2 + "a"
nyetak "a" + 1 + 2
```

```hasil
3a
a12
```

`panjang` counts the letters in a text:

```krc
nyetak panjang("kerinci")
```

```hasil
7
```

## Arithmetic functions

Every operator also has a Kerinci word as a function: `tambah`, `kurang`, `kali` and `bagi`. The results are the same as with the operators.

```krc
nyetak tambah(2, 3)
nyetak kurang(10, 4)
nyetak kali(6, 7)
nyetak bagi(9, 2)
```

```hasil
5
6
42
4.5
```

## Errors: dividing by zero, mismatched kinds

```krc-error
nyetak 10 / 0
```

```hasil
Kesalahan: Pembagian dengan nol
```

```krc-error
nyetak "a" - 1
```

```hasil
Kesalahan: Operator '-' tidak bisa dipakai pada "a" dan 1
```

## Summary

- `+ - * / %` for calculating; parentheses control the order.
- `+` joins text when one side is text.
- `panjang(text)` counts letters.
- `tambah`, `kurang`, `kali`, `bagi` are the function versions.

## Exercises

1. Calculate the area of a rectangle 12 by 5 and print: `Luas: 60` ("luas" means area).
2. What is the remainder of 100 divided by 7?
3. Convert 30 degrees Celsius to Fahrenheit with the formula `C * 9 / 5 + 32`.

Answers: [answers.md](answers.md#lesson-3). Continue to [Lesson 4](04-asking-the-user.md).
