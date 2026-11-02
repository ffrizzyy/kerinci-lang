# Lesson 6: Repeating

Computers are best at doing the same thing many times without getting bored.

## `selamu`: repeat while a condition is true

```krc
# dialek: koto-payang
netakka_variabel i = 1
selamu i lebih_nik_atau_samu_dinga 5 {
    nytak i
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

`selamu` checks the condition. If it is true, the body `{ }` runs, and then the condition is checked again. If you forget to change `i`, the loop never ends!

## `ndik ... daling`: for every item

`ndik x daling something { ... }` runs the body `{ }` once for every item. `daling` means "in".

```krc
# dialek: koto-payang
ndik buah daling ["pisang", "apel", "jeruk"] {
    nytak "Saya suka " + buah
}
```

```hasil
Saya suka pisang
Saya suka apel
Saya suka jeruk
```

Text can also be repeated letter by letter:

```krc
# dialek: koto-payang
ndik huruf daling "kerinci" {
    nytak huruf
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

## `rentang`: counting

`rentang` makes a list of numbers, and it goes very well with `ndik`.

| Write | Result |
|---|---|
| `rentang(5)` | `[0, 1, 2, 3, 4]` |
| `rentang(2, 6)` | `[2, 3, 4, 5]` |
| `rentang(0, 10, 3)` | `[0, 3, 6, 9]` |

Notice: the last number is **not** included. `rentang(5)` starts at 0 and stops before 5.

```krc
# dialek: koto-payang
ndik i daling rentang(1, 6) {
    nytak "Hitungan " + i
}
nytak rentang(0, 10, 3)
nytak rentang(5, 0, 0 - 1)
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

## `slese` and `lanjutka`

- `slese` stops the loop right now.
- `lanjutka` skips the rest of the body and goes straight to the next round.

```krc
# dialek: koto-payang
ndik i daling rentang(1, 11) {
    kalu i % 2 samu_dinga 0 { lanjutka }
    kalu i lebih_geduang_dari 7 { slese }
    nytak i
}
```

```hasil
1
3
5
7
```

This prints the odd numbers and stops once it passes 7.

> Be careful with `lanjutka` inside `selamu`: if the line `i = i + 1` comes **after** `lanjutka`, it gets skipped and the loop never ends. Put the increment at the start of the body.

## Loops inside loops

```krc
# dialek: koto-payang
ndik baris daling rentang(1, 4) {
    netakka_variabel garis = ""
    ndik kolom daling rentang(1, 4) {
        garis = garis + (baris * kolom) + "\t"
    }
    nytak garis
}
```

```hasil
1	2	3	
2	4	6	
3	6	9	
```

## Examples: adding up and guessing

```krc
# dialek: koto-payang
netakka_variabel total = 0
ndik angka daling rentang(1, 101) {
    total = total + angka
}
nytak "Jumlah 1 sampai 100: " + total
```

```hasil
Jumlah 1 sampai 100: 5050
```

```krc masukan=50|80|77|25
# dialek: koto-payang
netakka_konstanta rahasia = 77
netakka_variabel tebakan = 0
netakka_variabel percobaan = 0
selamu tebakan iduak_samu_dinga rahasia {
    nytak "Tebak angka (1-100):"
    tebakan = bilangan_buluak(masukka())
    percobaan = percobaan + 1
    kalu tebakan lebih_nik_dari rahasia {
        nytak "Terlalu kecil"
    } nga_laen kalu tebakan lebih_geduang_dari rahasia {
        nytak "Terlalu besar"
    }
}
nytak "Benar! Percobaan: " + percobaan
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

- `selamu condition { }` repeats while the condition is true.
- `ndik x daling list { }` repeats for every item.
- `rentang(a, b)` gives the numbers from a up to (not including) b.
- `slese` stops; `lanjutka` jumps to the next round.

## Exercises

1. Print the numbers 10 down to 1 (a countdown).
2. Print the 7 times table, from 7 x 1 to 7 x 10.
3. Add up all the even numbers from 1 to 50.

Answers: [answers.md](answers.md#lesson-6). Continue to [Lesson 7](07-lists.md).

---
*Generated from the Siulak lesson. Code and inline code use Koto Payang
(status: review).*
