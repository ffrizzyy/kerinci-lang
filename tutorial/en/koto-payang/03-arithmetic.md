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
# dialek: koto-payang
nytak 7 + 3
nytak 7 - 3
nytak 7 * 3
nytak 7 / 2
nytak 7 % 3
nytak 8 / 2
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
# dialek: koto-payang
nytak 2 + 3 * 4
nytak (2 + 3) * 4
nytak 10 - 2 - 3
```

```hasil
14
20
5
```

## Calculating with barang

```krc
# dialek: koto-payang
netakka_variabel harga = 15000
netakka_variabel jumlah = 3
netakka_variabel total = harga * jumlah
nytak "Total: " + total
```

```hasil
Total: 45000
```

## Joining text

The `+` sign also joins text. If one side is text, the other side is automatically turned into text.

```krc
# dialek: koto-payang
netakka_variabel depan = "Budi"
netakka_variabel belakang = "Santoso"
nytak depan + " " + belakang
nytak "Umur: " + 20
nytak "Benar? " + betiu
```

```hasil
Budi Santoso
Umur: 20
Benar? betiu
```

Be careful: the order matters. If both sides are numbers, `+` adds them instead of joining.

```krc
# dialek: koto-payang
nytak 1 + 2 + "a"
nytak "a" + 1 + 2
```

```hasil
3a
a12
```

`panja` counts the letters in a text:

```krc
# dialek: koto-payang
nytak panja("kerinci")
```

```hasil
7
```

## Arithmetic functions

Every operator also has a Kerinci word as a function: `tambah`, `kura`, `kali` and `bagi`. The results are the same as with the operators.

```krc
# dialek: koto-payang
nytak tambah(2, 3)
nytak kura(10, 4)
nytak kali(6, 7)
nytak bagi(9, 2)
```

```hasil
5
6
42
4.5
```

## Errors: dividing by zero, mismatched kinds

```krc-error
# dialek: koto-payang
nytak 10 / 0
```

```hasil
Kesalahan: Pembagian dinga nol
```

```krc-error
# dialek: koto-payang
nytak "a" - 1
```

```hasil
Kesalahan: Operator ''-'' nyendak dipake kik "a" nga 1
```

## Summary

- `+ - * / %` for calculating; parentheses control the order.
- `+` joins text when one side is text.
- `panja(text)` counts letters.
- `tambah`, `kura`, `kali`, `bagi` are the function versions.

## Exercises

1. Calculate the area of a rectangle 12 by 5 and print: `Luas: 60` ("luas" means area).
2. What is the remainder of 100 divided by 7?
3. Convert 30 degrees Celsius to Fahrenheit with the formula `C * 9 / 5 + 32`.

Answers: [answers.md](answers.md#lesson-3). Continue to [Lesson 4](04-asking-the-user.md).

---
*Generated from the Siulak lesson. Code and inline code use Koto Payang
(status: review).*
