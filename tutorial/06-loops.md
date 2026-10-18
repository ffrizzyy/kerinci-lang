# Lesson 6: Repeating

Computers are best at doing the same thing many times without getting bored.

## `selamo`: repeat while a condition is true

```krc
barang i = 1
selamo i kurang_samo 5 {
    nyetak i
    i = i + 1
}
```

```hasil
1
2
3
4
5
```

`selamo` checks the condition. If it is true, the body `{ }` runs, and then the condition is checked again. If you forget to change `i`, the loop never ends!

## `untuk ... alem`: for every item

`untuk x alem something { ... }` runs the body `{ }` once for every item. `alem` means "in".

```krc
untuk buah alem ["pisang", "apel", "jeruk"] {
    nyetak "Saya suka " + buah
}
```

```hasil
Saya suka pisang
Saya suka apel
Saya suka jeruk
```

Text can also be repeated letter by letter:

```krc
untuk huruf alem "kerinci" {
    nyetak huruf
}
```

```hasil
k
e
r
i
n
c
i
```

## `jarak`: counting

`jarak` makes a list of numbers, and it goes very well with `untuk`.

| Write | Result |
|---|---|
| `jarak(5)` | `[0, 1, 2, 3, 4]` |
| `jarak(2, 6)` | `[2, 3, 4, 5]` |
| `jarak(0, 10, 3)` | `[0, 3, 6, 9]` |

Notice: the last number is **not** included. `jarak(5)` starts at 0 and stops before 5.

```krc
untuk i alem jarak(1, 6) {
    nyetak "Hitungan " + i
}
nyetak jarak(0, 10, 3)
nyetak jarak(5, 0, 0 - 1)
```

```hasil
Hitungan 1
Hitungan 2
Hitungan 3
Hitungan 4
Hitungan 5
[0, 3, 6, 9]
[5, 4, 3, 2, 1]
```

## `putuh` and `lanjut`

- `putuh` stops the loop right now.
- `lanjut` skips the rest of the body and goes straight to the next round.

```krc
untuk i alem jarak(1, 11) {
    kalu i % 2 samo 0 { lanjut }
    kalu i lebih_daripado 7 { putuh }
    nyetak i
}
```

```hasil
1
3
5
7
```

This prints the odd numbers and stops once it passes 7.

> Be careful with `lanjut` inside `selamo`: if the line `i = i + 1` comes **after** `lanjut`, it gets skipped and the loop never ends. Put the increment at the start of the body.

## Loops inside loops

```krc
untuk baris alem jarak(1, 4) {
    barang garis = ""
    untuk kolom alem jarak(1, 4) {
        garis = garis + (baris * kolom) + "\t"
    }
    nyetak garis
}
```

```hasil
1	2	3	
2	4	6	
3	6	9	
```

## Examples: adding up and guessing

```krc
barang total = 0
untuk angka alem jarak(1, 101) {
    total = total + angka
}
nyetak "Jumlah 1 sampai 100: " + total
```

```hasil
Jumlah 1 sampai 100: 5050
```

```krc masukan=50|80|77|25
tetap rahasia = 77
barang tebakan = 0
barang percobaan = 0
selamo tebakan dak_samo rahasia {
    nyetak "Tebak angka (1-100):"
    tebakan = bilangan(tanyo())
    percobaan = percobaan + 1
    kalu tebakan kurang_daripado rahasia {
        nyetak "Terlalu kecil"
    } lain kalu tebakan lebih_daripado rahasia {
        nyetak "Terlalu besar"
    }
}
nyetak "Benar! Percobaan: " + percobaan
```

```hasil
Tebak angka (1-100):
Terlalu kecil
Tebak angka (1-100):
Terlalu besar
Tebak angka (1-100):
Benar! Percobaan: 3
```

## Summary

- `selamo condition { }` repeats while the condition is true.
- `untuk x alem list { }` repeats for every item.
- `jarak(a, b)` gives the numbers from a up to (not including) b.
- `putuh` stops; `lanjut` jumps to the next round.

## Exercises

1. Print the numbers 10 down to 1 (a countdown).
2. Print the 7 times table, from 7 x 1 to 7 x 10.
3. Add up all the even numbers from 1 to 50.

Answers: [answers.md](answers.md#lesson-6). Continue to [Lesson 7](07-lists.md).
