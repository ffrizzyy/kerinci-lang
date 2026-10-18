# Lesson 5: Making decisions

A useful program can choose what to do. The Kerinci word for "if" is `kalu`, and for "otherwise" it is `lain`.

```krc
barang umur = 20
kalu umur lebih_daripado 17 {
    nyetak "Sudah dewasa"
} lain {
    nyetak "Belum dewasa"
}
```

```hasil
Sudah dewasa
```

The part inside `{ }` only runs if the condition is true.

## Comparing

| Word | Symbol | Meaning |
|---|---|---|
| `samo` | `==` | equal to |
| `dak_samo` | `!=` | not equal to |
| `lebih_daripado` | `>` | greater than |
| `kurang_daripado` | `<` | less than |
| `lebih_samo` | `>=` | greater than or equal to |
| `kurang_samo` | `<=` | less than or equal to |

The words and the symbols mean exactly the same thing, and they can be mixed. Use whichever you find more comfortable.

```krc
nyetak 5 lebih_daripado 3
nyetak 5 == 3
nyetak "a" samo "a"
nyetak 4 dak_samo 4
nyetak 3 kurang_samo 3
```

```hasil
betul
salah
betul
salah
betul
```

The result of a comparison is `betul` or `salah`.

Be careful: one `=` means **storing** into a barang, while two `==` (or the word `samo`) means **comparing**.

## Many choices: `lain kalu`

```krc
barang nilai = 72
kalu nilai lebih_samo 90 {
    nyetak "A"
} lain kalu nilai lebih_samo 80 {
    nyetak "B"
} lain kalu nilai lebih_samo 70 {
    nyetak "C"
} lain {
    nyetak "D"
}
```

```hasil
C
```

The computer checks from the top and stops at the first condition that is true.

## Combining conditions: `ngan`, `apo`, `idak`

| Word | Meaning | True when... |
|---|---|---|
| `ngan` | and | both sides are true |
| `apo` | or | at least one side is true |
| `idak` | not | that side is false |

```krc
barang umur = 25
barang punya_ktp = betul

kalu umur lebih_samo 17 ngan punya_ktp {
    nyetak "Boleh mendaftar"
}

kalu umur kurang_daripado 17 apo idak punya_ktp {
    nyetak "Belum boleh"
} lain {
    nyetak "Syarat lain terpenuhi"
}
```

```hasil
Boleh mendaftar
Syarat lain terpenuhi
```

## Values that count as false

In a condition, these values count as false: `salah`, `kosong`, `0`, `""` (empty text), `[]` (empty list) and `{}` (empty map). Every other value counts as true.

```krc
kalu "" { nyetak "ada isi" } lain { nyetak "teks kosong dianggap salah" }
kalu "halo" { nyetak "teks berisi dianggap benar" }
kalu 0 { nyetak "x" } lain { nyetak "nol dianggap salah" }
```

```hasil
teks kosong dianggap salah
teks berisi dianggap benar
nol dianggap salah
```

## Decisions inside decisions

```krc masukan=17
nyetak "Umur?"
barang umur = bilangan(tanyo())
kalu umur lebih_samo 17 {
    kalu umur lebih_samo 60 {
        nyetak "Lansia"
    } lain {
        nyetak "Dewasa"
    }
} lain {
    nyetak "Anak-anak atau remaja"
}
```

```hasil
Umur?
Dewasa
```

## Summary

- `kalu condition { ... } lain { ... }`; use `lain kalu` for extra choices.
- Comparisons: `samo`, `dak_samo`, `lebih_daripado`, `kurang_daripado`, `lebih_samo`, `kurang_samo`.
- Combine conditions with `ngan`, `apo`, `idak`.

## Exercises

1. Ask for a number; print "genap" (even) or "ganjil" (odd) (hint: `%`).
2. Ask for an age; print "anak" (child, under 13), "remaja" (teenager, 13 to 17) or "dewasa" (adult).
3. Ask for three numbers and print the largest.

Answers: [answers.md](answers.md#lesson-5). Continue to [Lesson 6](06-loops.md).
