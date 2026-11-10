# Lesson 9: Maps and pilih

## Maps: pairs of keys and values

A **map** (*peta*) stores pairs: every value has a **key** (a name) for finding it. Where a list is searched by number, a map is searched by name.

```krc
# dialek: koto-payang
netakka_variabel siswa = {"Budi": 80, "Sari": 92}
nytak siswa
nytak siswa["Sari"]
```

```hasil
{"Budi": 80, "Sari": 92}
92
```

## Changing and adding

Writing to an existing key replaces its value; a new key is added.

```krc
# dialek: koto-payang
netakka_variabel siswa = {"Budi": 80}
siswa["Budi"] = 85
siswa["Dewi"] = 65
nytak siswa
nytak panja(siswa)
```

```hasil
{"Budi": 85, "Dewi": 65}
2
```

Keys may be text or whole numbers. Values may be anything, even a list or another map.

## Checking for a key

Getting a key that does not exist is an error, so check first with `meriksu`.

```krc-error
# dialek: koto-payang
netakka_variabel siswa = {"Budi": 80}
nytak siswa["Andi"]
```

```hasil
Kesalahan: sidiak besuao kuncai: "Andi"
```

```krc
# dialek: koto-payang
netakka_variabel siswa = {"Budi": 80}
kalu meriksu(siswa, "Andi") {
    nytak siswa["Andi"]
} nga_laen {
    nytak "Andi tidak ada"
}
```

```hasil
Andi tidak ada
```

## Seeing everything

`ndik` on a map gives the **keys**, in the order they were written.

```krc
# dialek: koto-payang
netakka_variabel siswa = {"Budi": 80, "Sari": 92, "Dewi": 65}
ndik nama daling siswa {
    nytak nama + ": " + siswa[nama]
}
```

```hasil
Budi: 80
Sari: 92
Dewi: 65
```

## Example: counting words

```krc
# dialek: koto-payang
netakka_variabel kalimat = "kalu kalu lain kalu lain"
netakka_variabel jumlah = {}
ndik kata daling pecah(kalimat) {
    kalu meriksu(jumlah, kata) {
        jumlah[kata] = jumlah[kata] + 1
    } nga_laen {
        jumlah[kata] = 1
    }
}
nytak jumlah
```

```hasil
{"kalu": 3, "lain": 2}
```

## Maps inside maps

```krc
# dialek: koto-payang
netakka_variabel murid = {
    "nama": "Budi",
    "nilai": [80, 90],
    "alamat": {"kota": "Sungai Penuh"}
}
tambahka(murid["nilai"], 100)
nytak murid
nytak murid["alamat"]["kota"]
```

```hasil
{"nama": "Budi", "nilai": [80, 90, 100], "alamat": {"kota": "Sungai Penuh"}}
Sungai Penuh
```

## `cocokka`: choosing one out of many

When one value is compared with many possibilities, `cocokka` is tidier than a long chain of `nga_laen kalu`.

```krc
# dialek: koto-payang
netakka_variabel hari = 3
cocokka hari {
    kalu 1 { nytak "Senin" }
    kalu 2 { nytak "Selasa" }
    kalu 3 { nytak "Rabu" }
    nga_laen { nytak "Hari lain" }
}
```

```hasil
Rabu
```

One `kalu` may hold several values, separated by commas:

```krc
# dialek: koto-payang
netakka_variabel hari = "minggu"
cocokka hari {
    kalu "sabtu", "minggu" { nytak "libur" }
    nga_laen { nytak "kerja" }
}
```

```hasil
libur
```

`cocokka` runs **only one** branch, the first that matches, and then it is finished. `nga_laen` is for when nothing matches, and may be left out.

## Summary

- `{"key": value}` makes a map; `p["key"]` gets a value; `p["key"] = x` changes or adds.
- `meriksu(p, key)` checks for a key; `ndik k daling p` goes through the keys.
- `cocokka x { kalu a { } kalu b, c { } nga_laen { } }` chooses one branch.

## Exercises

1. Make a map `harga` ("price") for three items and print the total price.
2. Make a function `nama_bulan(n)` using `cocokka` for months 1 to 3 (and "tidak dikenal", meaning unknown, for anything else).
3. Count how many times each letter appears in the word "kerinci".

Answers: [answers.md](answers.md#lesson-9). Continue to [Lesson 10](10-text.md).

---
*Generated from the Siulak lesson. Code and inline code use Koto Payang
(status: approved).*
