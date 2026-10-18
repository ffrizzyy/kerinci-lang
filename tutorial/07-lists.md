# Lesson 7: Lists

One barang can hold many values at once in a **list** (*daftar*).

```krc
barang buah = ["pisang", "apel", "jeruk"]
nyetak buah
nyetak panjang(buah)
```

```hasil
["pisang", "apel", "jeruk"]
3
```

## Getting an item

Every item has a position number, and the numbering **starts at 0**.

```krc
barang buah = ["pisang", "apel", "jeruk"]
nyetak buah[0]
nyetak buah[2]
```

```hasil
pisang
jeruk
```

The last item is at position `panjang(buah) - 1` ("buah" means fruit). A position outside the list is an error:

```krc-error
barang buah = ["pisang", "apel"]
nyetak buah[5]
```

```hasil
Kesalahan: Indeks di luar jangkauan: 5 (panjang 2)
```

## Changing and adding

```krc
barang buah = ["pisang", "apel"]
buah[0] = "mangga"
nambahkah(buah, "jeruk")
nyetak buah
```

```hasil
["mangga", "apel", "jeruk"]
```

`nambahkah(list, value)` adds the value at the **end** of the list and changes the list itself.

## List tools

| Write | What it does |
|---|---|
| `panjang(d)` | number of items |
| `nambahkah(d, x)` | add `x` at the end (changes `d`) |
| `isi(d, x)` | is `x` in `d`? (`betul`/`salah`) |
| `milih(d)` | a **sorted** copy (`d` is unchanged) |
| `pulang(d)` | a **reversed** copy (`d` is unchanged) |
| `d1 + d2` | the two lists joined (a new list) |

```krc
barang angka = [5, 2, 9, 1]
nyetak milih(angka)
nyetak pulang(angka)
nyetak angka
nyetak isi(angka, 9)
nyetak isi(angka, 7)
nyetak angka + [100, 200]
```

```hasil
[1, 2, 5, 9]
[1, 9, 2, 5]
[5, 2, 9, 1]
betul
salah
[5, 2, 9, 1, 100, 200]
```

## Lists and loops

```krc
barang nilai = [80, 65, 90, 55, 75]
barang total = 0
untuk n alem nilai {
    total = total + n
}
nyetak "Rata-rata: " + bagi(total, panjang(nilai))

barang tertinggi = nilai[0]
untuk n alem nilai {
    kalu n lebih_daripado tertinggi { tertinggi = n }
}
nyetak "Tertinggi: " + tertinggi
```

```hasil
Rata-rata: 73
Tertinggi: 90
```

If you need the position numbers, loop over `jarak(panjang(list))`:

```krc
barang nama = ["Budi", "Sari", "Dewi"]
untuk i alem jarak(panjang(nama)) {
    nyetak (i + 1) + ". " + nama[i]
}
```

```hasil
1. Budi
2. Sari
3. Dewi
```

## Lists inside lists

```krc
barang papan = [[1, 2, 3], [4, 5, 6]]
nyetak papan[1][0]
papan[0][2] = 99
nyetak papan
```

```hasil
4
[[1, 2, 99], [4, 5, 6]]
```

## Careful: lists are shared, not copied

`barang b = a` does not make a copy; `a` and `b` point to the same list.

```krc
barang a = [1, 2, 3]
barang b = a
b[0] = 100
nyetak a

barang c = a + []
c[0] = 5
nyetak a
nyetak c
```

```hasil
[100, 2, 3]
[100, 2, 3]
[5, 2, 3]
```

`a + []` makes a new list, so that is how you copy.

## Summary

- `[a, b, c]` makes a list; `d[0]` gets the first item.
- `nambahkah`, `isi`, `milih`, `pulang`, `panjang`.
- Positions start at 0.
- `barang b = a` shares the same list.

## Exercises

1. Make a list of five names and print each name with its number.
2. Make a list of numbers and print their sum and the smallest value.
3. Make a new list that holds the squares of 1 to 5.

Answers: [answers.md](answers.md#lesson-7). Continue to [Lesson 8](08-guno.md).
