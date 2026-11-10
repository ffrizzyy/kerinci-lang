# Lesson 5: Making decisions

A useful program can choose what to do. The Kerinci word for "if" is `kalu`, and for "otherwise" it is `nga_laen`.

```krc
# dialek: koto-payang
netakka_variabel umur = 20
kalu umur lebih_geduang_dari 17 {
    nytak "Sudah dewasa"
} nga_laen {
    nytak "Belum dewasa"
}
```

```hasil
Sudah dewasa
```

The part inside `{ }` only runs if the condition is true.

## Comparing

| Word | Symbol | Meaning |
|---|---|---|
| `samu_dinga` | `==` | equal to |
| `iduak_samu_dinga` | `!=` | not equal to |
| `lebih_geduang_dari` | `>` | greater than |
| `lebih_nik_dari` | `<` | less than |
| `lebih_geduang_atau_samu_dinga` | `>=` | greater than or equal to |
| `lebih_nik_atau_samu_dinga` | `<=` | less than or equal to |

The words and the symbols mean exactly the same thing, and they can be mixed. Use whichever you find more comfortable.

```krc
# dialek: koto-payang
nytak 5 lebih_geduang_dari 3
nytak 5 == 3
nytak "a" samu_dinga "a"
nytak 4 iduak_samu_dinga 4
nytak 3 lebih_nik_atau_samu_dinga 3
```

```hasil
betiu
salah
betiu
salah
betiu
```

The result of a comparison is `betiu` or `salah`.

Be careful: one `=` means **storing** into a barang, while two `==` (or the word `samu_dinga`) means **comparing**.

## Many choices: `nga_laen kalu`

```krc
# dialek: koto-payang
netakka_variabel nilai = 72
kalu nilai lebih_geduang_atau_samu_dinga 90 {
    nytak "A"
} nga_laen kalu nilai lebih_geduang_atau_samu_dinga 80 {
    nytak "B"
} nga_laen kalu nilai lebih_geduang_atau_samu_dinga 70 {
    nytak "C"
} nga_laen {
    nytak "D"
}
```

```hasil
C
```

The computer checks from the top and stops at the first condition that is true.

## Combining conditions: `nga`, `atau`, `iduak`

| Word | Meaning | True when... |
|---|---|---|
| `nga` | and | both sides are true |
| `atau` | or | at least one side is true |
| `iduak` | not | that side is false |

```krc
# dialek: koto-payang
netakka_variabel umur = 25
netakka_variabel punya_ktp = betiu

kalu umur lebih_geduang_atau_samu_dinga 17 nga punya_ktp {
    nytak "Boleh mendaftar"
}

kalu umur lebih_nik_dari 17 atau iduak punya_ktp {
    nytak "Belum boleh"
} nga_laen {
    nytak "Syarat lain terpenuhi"
}
```

```hasil
Boleh mendaftar
Syarat lain terpenuhi
```

## Values that count as false

In a condition, these values count as false: `salah`, `kusao`, `0`, `""` (empty text), `[]` (empty list) and `{}` (empty map). Every other value counts as true.

```krc
# dialek: koto-payang
kalu "" { nytak "ada isi" } nga_laen { nytak "teks kosong dianggap salah" }
kalu "halo" { nytak "teks berisi dianggap benar" }
kalu 0 { nytak "x" } nga_laen { nytak "nol dianggap salah" }
```

```hasil
teks kosong dianggap salah
teks berisi dianggap benar
nol dianggap salah
```

## Decisions inside decisions

```krc masukan=17
# dialek: koto-payang
nytak "Umur?"
netakka_variabel umur = bilangan_buluak(masukka())
kalu umur lebih_geduang_atau_samu_dinga 17 {
    kalu umur lebih_geduang_atau_samu_dinga 60 {
        nytak "Lansia"
    } nga_laen {
        nytak "Dewasa"
    }
} nga_laen {
    nytak "Anak-anak atau remaja"
}
```

```hasil
Umur?
Dewasa
```

## Summary

- `kalu condition { ... } nga_laen { ... }`; use `nga_laen kalu` for extra choices.
- Comparisons: `samu_dinga`, `iduak_samu_dinga`, `lebih_geduang_dari`, `lebih_nik_dari`, `lebih_geduang_atau_samu_dinga`, `lebih_nik_atau_samu_dinga`.
- Combine conditions with `nga`, `atau`, `iduak`.

## Exercises

1. Ask for a number; print "genap" (even) or "ganjil" (odd) (hint: `%`).
2. Ask for an age; print "anak" (child, under 13), "remaja" (teenager, 13 to 17) or "dewasa" (adult).
3. Ask for three numbers and print the largest.

Answers: [answers.md](answers.md#lesson-5). Continue to [Lesson 6](06-loops.md).

---
*Generated from the Siulak lesson. Code and inline code use Koto Payang
(status: approved).*
