# Lesson 7: Lists

One barang can hold many values at once in a **list** (*daftar*).

```krc
# dialek: koto-payang
netakka_variabel buah = ["pisang", "apel", "jeruk"]
nytak buah
nytak panja(buah)
```

```hasil
["pisang", "apel", "jeruk"]
3
```

## Getting an item

Every item has a position number, and the numbering **starts at 0**.

```krc
# dialek: koto-payang
netakka_variabel buah = ["pisang", "apel", "jeruk"]
nytak buah[0]
nytak buah[2]
```

```hasil
pisang
jeruk
```

The last item is at position `panja(buah) - 1` ("buah" means fruit). A position outside the list is an error:

```krc-error
# dialek: koto-payang
netakka_variabel buah = ["pisang", "apel"]
nytak buah[5]
```

```hasil
Kesalahan: Indeks kik luwua jangkauan: 5 (panja 2)
```

## Changing and adding

```krc
# dialek: koto-payang
netakka_variabel buah = ["pisang", "apel"]
buah[0] = "mangga"
tambahka(buah, "jeruk")
nytak buah
```

```hasil
["mangga", "apel", "jeruk"]
```

`tambahka(list, value)` adds the value at the **end** of the list and changes the list itself.

## List tools

| Write | What it does |
|---|---|
| `panja(d)` | number of items |
| `tambahka(d, x)` | add `x` at the end (changes `d`) |
| `meriksu(d, x)` | is `x` in `d`? (`betiu`/`salah`) |
| `terurut(d)` | a **sorted** copy (`d` is unchanged) |
| `tebaluik(d)` | a **reversed** copy (`d` is unchanged) |
| `d1 + d2` | the two lists joined (a new list) |

```krc
# dialek: koto-payang
netakka_variabel angka = [5, 2, 9, 1]
nytak terurut(angka)
nytak tebaluik(angka)
nytak angka
nytak meriksu(angka, 9)
nytak meriksu(angka, 7)
nytak angka + [100, 200]
```

```hasil
[1, 2, 5, 9]
[1, 9, 2, 5]
[5, 2, 9, 1]
betiu
salah
[5, 2, 9, 1, 100, 200]
```

## Lists and loops

```krc
# dialek: koto-payang
netakka_variabel nilai = [80, 65, 90, 55, 75]
netakka_variabel total = 0
ndik n daling nilai {
    total = total + n
}
nytak "Rata-rata: " + bagi(total, panja(nilai))

netakka_variabel tertinggi = nilai[0]
ndik n daling nilai {
    kalu n lebih_geduang_dari tertinggi { tertinggi = n }
}
nytak "Tertinggi: " + tertinggi
```

```hasil
Rata-rata: 73
Tertinggi: 90
```

If you need the position numbers, loop over `rentang(panja(list))`:

```krc
# dialek: koto-payang
netakka_variabel nama = ["Budi", "Sari", "Dewi"]
ndik i daling rentang(panja(nama)) {
    nytak (i + 1) + ". " + nama[i]
}
```

```hasil
1. Budi
2. Sari
3. Dewi
```

## Lists inside lists

```krc
# dialek: koto-payang
netakka_variabel papan = [[1, 2, 3], [4, 5, 6]]
nytak papan[1][0]
papan[0][2] = 99
nytak papan
```

```hasil
4
[[1, 2, 99], [4, 5, 6]]
```

## Careful: lists are shared, not copied

`netakka_variabel b = a` does not make a copy; `a` and `b` point to the same list.

```krc
# dialek: koto-payang
netakka_variabel a = [1, 2, 3]
netakka_variabel b = a
b[0] = 100
nytak a

netakka_variabel c = a + []
c[0] = 5
nytak a
nytak c
```

```hasil
[100, 2, 3]
[100, 2, 3]
[5, 2, 3]
```

`a + []` makes a new list, so that is how you copy.

## Summary

- `[a, b, c]` makes a list; `d[0]` gets the first item.
- `tambahka`, `meriksu`, `terurut`, `tebaluik`, `panja`.
- Positions start at 0.
- `netakka_variabel b = a` shares the same list.

## Exercises

1. Make a list of five names and print each name with its number.
2. Make a list of numbers and print their sum and the smallest value.
3. Make a new list that holds the squares of 1 to 5.

Answers: [answers.md](answers.md#lesson-7). Continue to [Lesson 8](08-guno.md).

---
*Generated from the Siulak lesson. Code and inline code use Koto Payang
(status: approved).*
