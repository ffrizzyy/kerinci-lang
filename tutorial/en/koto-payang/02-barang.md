# Lesson 2: Barang, a place to keep values

Programs often need to remember things. For that we create a **barang** (a variable): a named container that holds a value.

```krc
# dialek: koto-payang
netakka_variabel umur = 20
nytak umur
```

```hasil
20
```

The word `netakka_variabel` creates a new container named `umur` ("age") and fills it with `20`.

## Changing the contents

Once created, the contents of a barang may be replaced. Write just its name, without `netakka_variabel`.

```krc
# dialek: koto-payang
netakka_variabel umur = 20
umur = 21
nytak umur
umur = umur + 1
nytak umur
```

```hasil
21
22
```

The line `umur = umur + 1` means: take the contents of `umur`, add 1, and store the result back in `umur`.

## A barang that does not change: `netakka_konstanta`

If the value must never change, use `netakka_konstanta`.

```krc
# dialek: koto-payang
netakka_konstanta pi = 3.14
nytak pi
```

```hasil
3.14
```

Trying to change it causes an error:

```krc-error
# dialek: koto-payang
netakka_konstanta pi = 3.14
pi = 3
```

```hasil
Kesalahan: 'pi' adalah konstanta ('netakka_konstanta') nga dak bisa diubuah
```

## Rules for names

- A name may contain letters, digits and `_`, but must not start with a digit.
- Upper and lower case are different: `Umur` and `umur` are two different barang.
- A name cannot be the same as a special word such as `kalu` or `selamu`.
- Choose names that describe the contents: `umur_budi` is clearer than `x`.

A barang must be created before it is used:

```krc-error
# dialek: koto-payang
nytak jumlah
```

```hasil
Kesalahan: namu lao dijeloehka: jumlah
```

## Kinds of values

Every value has a kind. The function `tipe` tells you which.

| Example | Kind | Meaning |
|---|---|---|
| `42` | `bilangan_buluak` | whole number |
| `3.5` | `bilangan_bakoma` | decimal number |
| `"halo"` | `tulisan` | text |
| `[1, 2]` | `daftar` | an ordered collection (Lesson 7) |
| `{"a": 1}` | `kamus` | a collection of pairs (Lesson 9) |
| `betiu`, `salah` | `boolean` | true or false |
| `kusao` | `kusao` | no value |

```krc
# dialek: koto-payang
nytak tipe(42)
nytak tipe(3.5)
nytak tipe("halo")
nytak tipe([1, 2])
nytak tipe({"a": 1})
nytak tipe(betiu)
nytak tipe(kusao)
```

```hasil
bilangan_buluak
bilangan_bakoma
tulisan
daftar
kamus
boolean
kusao
```

`betiu` and `salah` are the values true and false. `kusao` means "nothing in it".

> Note: the kind name for `betiu` and `salah` is currently `boolean`, a temporary English word, until Kerinci speakers contribute the right word.

## Summary

- `netakka_variabel name = value` creates a barang; `name = value` changes it.
- `netakka_konstanta` is for values that must not change.
- `tipe(x)` names the kind of a value.

## Exercises

1. Create the barang `nama` and `kota`, then print both.
2. Create a barang `saldo` (balance) with the value 100, add 50, then print it.
3. What kinds are the values `"42"` and `42`? Prove it with `tipe`.

Answers: [answers.md](answers.md#lesson-2). Continue to [Lesson 3](03-arithmetic.md).

---
*Generated from the Siulak lesson. Code and inline code use Koto Payang
(status: review).*
