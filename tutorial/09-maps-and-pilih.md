# Lesson 9: Maps and pilih

## Maps: pairs of keys and values

A **map** (*peta*) stores pairs: every value has a **key** (a name) for finding it. Where a list is searched by number, a map is searched by name.

```krc
barang siswa = {"Budi": 80, "Sari": 92}
nyetak siswa
nyetak siswa["Sari"]
```

```hasil
{"Budi": 80, "Sari": 92}
92
```

## Changing and adding

Writing to an existing key replaces its value; a new key is added.

```krc
barang siswa = {"Budi": 80}
siswa["Budi"] = 85
siswa["Dewi"] = 65
nyetak siswa
nyetak panjang(siswa)
```

```hasil
{"Budi": 85, "Dewi": 65}
2
```

Keys may be text or whole numbers. Values may be anything, even a list or another map.

## Checking for a key

Getting a key that does not exist is an error, so check first with `isi`.

```krc-error
barang siswa = {"Budi": 80}
nyetak siswa["Andi"]
```

```hasil
Kesalahan: Kunci tidak ditemukan: "Andi"
```

```krc
barang siswa = {"Budi": 80}
kalu isi(siswa, "Andi") {
    nyetak siswa["Andi"]
} lain {
    nyetak "Andi tidak ada"
}
```

```hasil
Andi tidak ada
```

## Seeing everything

`untuk` on a map gives the **keys**, in the order they were written.

```krc
barang siswa = {"Budi": 80, "Sari": 92, "Dewi": 65}
untuk nama alem siswa {
    nyetak nama + ": " + siswa[nama]
}
```

```hasil
Budi: 80
Sari: 92
Dewi: 65
```

## Example: counting words

```krc
barang kalimat = "kalu kalu lain kalu lain"
barang jumlah = {}
untuk kata alem pisah(kalimat) {
    kalu isi(jumlah, kata) {
        jumlah[kata] = jumlah[kata] + 1
    } lain {
        jumlah[kata] = 1
    }
}
nyetak jumlah
```

```hasil
{"kalu": 3, "lain": 2}
```

## Maps inside maps

```krc
barang murid = {
    "nama": "Budi",
    "nilai": [80, 90],
    "alamat": {"kota": "Sungai Penuh"}
}
nambahkah(murid["nilai"], 100)
nyetak murid
nyetak murid["alamat"]["kota"]
```

```hasil
{"nama": "Budi", "nilai": [80, 90, 100], "alamat": {"kota": "Sungai Penuh"}}
Sungai Penuh
```

## `pilih`: choosing one out of many

When one value is compared with many possibilities, `pilih` is tidier than a long chain of `lain kalu`.

```krc
barang hari = 3
pilih hari {
    kalu 1 { nyetak "Senin" }
    kalu 2 { nyetak "Selasa" }
    kalu 3 { nyetak "Rabu" }
    lain { nyetak "Hari lain" }
}
```

```hasil
Rabu
```

One `kalu` may hold several values, separated by commas:

```krc
barang hari = "minggu"
pilih hari {
    kalu "sabtu", "minggu" { nyetak "libur" }
    lain { nyetak "kerja" }
}
```

```hasil
libur
```

`pilih` runs **only one** branch, the first that matches, and then it is finished. `lain` is for when nothing matches, and may be left out.

## Summary

- `{"key": value}` makes a map; `p["key"]` gets a value; `p["key"] = x` changes or adds.
- `isi(p, key)` checks for a key; `untuk k alem p` goes through the keys.
- `pilih x { kalu a { } kalu b, c { } lain { } }` chooses one branch.

## Exercises

1. Make a map `harga` ("price") for three items and print the total price.
2. Make a function `nama_bulan(n)` using `pilih` for months 1 to 3 (and "tidak dikenal", meaning unknown, for anything else).
3. Count how many times each letter appears in the word "kerinci".

Answers: [answers.md](answers.md#lesson-9). Continue to [Lesson 10](10-text.md).
