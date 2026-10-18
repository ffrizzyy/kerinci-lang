# Lesson 2: Barang, a place to keep values

Programs often need to remember things. For that we create a **barang** (a variable): a named container that holds a value.

```krc
barang umur = 20
nyetak umur
```

```hasil
20
```

The word `barang` creates a new container named `umur` ("age") and fills it with `20`.

## Changing the contents

Once created, the contents of a barang may be replaced. Write just its name, without `barang`.

```krc
barang umur = 20
umur = 21
nyetak umur
umur = umur + 1
nyetak umur
```

```hasil
21
22
```

The line `umur = umur + 1` means: take the contents of `umur`, add 1, and store the result back in `umur`.

## A barang that does not change: `tetap`

If the value must never change, use `tetap`.

```krc
tetap pi = 3.14
nyetak pi
```

```hasil
3.14
```

Trying to change it causes an error:

```krc-error
tetap pi = 3.14
pi = 3
```

```hasil
Kesalahan: 'pi' adalah konstanta ('tetap') dan tidak bisa diubah
```

## Rules for names

- A name may contain letters, digits and `_`, but must not start with a digit.
- Upper and lower case are different: `Umur` and `umur` are two different barang.
- A name cannot be the same as a special word such as `kalu` or `selamo`.
- Choose names that describe the contents: `umur_budi` is clearer than `x`.

A barang must be created before it is used:

```krc-error
nyetak jumlah
```

```hasil
Kesalahan: Nama belum didefinisikan: jumlah
```

## Kinds of values

Every value has a kind. The function `mecem` tells you which.

| Example | Kind | Meaning |
|---|---|---|
| `42` | `bilangan` | whole number |
| `3.5` | `pecahan` | decimal number |
| `"halo"` | `kato` | text |
| `[1, 2]` | `daftar` | an ordered collection (Lesson 7) |
| `{"a": 1}` | `peta` | a collection of pairs (Lesson 9) |
| `betul`, `salah` | `boolean` | true or false |
| `kosong` | `kosong` | no value |

```krc
nyetak mecem(42)
nyetak mecem(3.5)
nyetak mecem("halo")
nyetak mecem([1, 2])
nyetak mecem({"a": 1})
nyetak mecem(betul)
nyetak mecem(kosong)
```

```hasil
bilangan
pecahan
kato
daftar
peta
boolean
kosong
```

`betul` and `salah` are the values true and false. `kosong` means "nothing in it".

> Note: the kind name for `betul` and `salah` is currently `boolean`, a temporary English word, until Kerinci speakers contribute the right word.

## Summary

- `barang name = value` creates a barang; `name = value` changes it.
- `tetap` is for values that must not change.
- `mecem(x)` names the kind of a value.

## Exercises

1. Create the barang `nama` and `kota`, then print both.
2. Create a barang `saldo` (balance) with the value 100, add 50, then print it.
3. What kinds are the values `"42"` and `42`? Prove it with `mecem`.

Answers: [answers.md](answers.md#lesson-2). Continue to [Lesson 3](03-arithmetic.md).
