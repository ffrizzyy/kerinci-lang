# Lesson 8: Guno, making your own functions

When a piece of a program is used again and again, wrap it in a **guno** (a function), give it a name, and call it whenever you like.

```krc
guno sapa(nama) {
    nyetak "Halo, " + nama
}

sapa("Budi")
sapa("Sari")
```

```hasil
Halo, Budi
Halo, Sari
```

`guno sapa(nama) { ... }` creates a function named `sapa` ("greet") that takes one ingredient (a **parameter**) named `nama`. `sapa("Budi")` calls it.

## `balik`: returning a result

`balik` sends a value back to the caller and ends the function.

```krc
guno kuadrat(x) {
    balik x * x
}

nyetak kuadrat(5)
barang hasil = kuadrat(3) + kuadrat(4)
nyetak hasil
```

```hasil
25
25
```

A function without `balik` gives `kosong`.

```krc
guno diam() {
    barang x = 1
}
nyetak diam()
```

```hasil
kosong
```

## Several parameters

```krc
guno luas_persegi_panjang(panjang_sisi, lebar) {
    balik panjang_sisi * lebar
}
nyetak luas_persegi_panjang(12, 5)
```

```hasil
60
```

The number of values given must equal the number of parameters:

```krc-error
guno tambah_dua(a, b) { balik a + b }
nyetak tambah_dua(1)
```

```hasil
Kesalahan: Fungsi butuh 2 argumen, diberi 1
```

## Decisions inside a function

```krc
guno huruf_nilai(nilai) {
    kalu nilai lebih_samo 90 { balik "A" }
    kalu nilai lebih_samo 80 { balik "B" }
    kalu nilai lebih_samo 70 { balik "C" }
    balik "D"
}

nyetak huruf_nilai(95)
nyetak huruf_nilai(72)
nyetak huruf_nilai(40)
```

```hasil
A
C
D
```

## Functions and lists

```krc
guno rata_rata(daftar_nilai) {
    kalu panjang(daftar_nilai) samo 0 { balik 0 }
    barang total = 0
    untuk n alem daftar_nilai { total = total + n }
    balik bagi(total, panjang(daftar_nilai))
}

nyetak rata_rata([80, 70, 90])
nyetak rata_rata([])
```

```hasil
80
0
```

## Scope

A barang created **inside** a function lives only inside that function. A function can read and change barang from outside that were created earlier.

```krc
barang hitungan = 0

guno tambah_hitungan() {
    hitungan = hitungan + 1
}

tambah_hitungan()
tambah_hitungan()
nyetak hitungan
```

```hasil
2
```

```krc-error
guno buat() {
    barang rahasia = 42
}
buat()
nyetak rahasia
```

```hasil
Kesalahan: Nama belum didefinisikan: rahasia
```

## A function calling itself (recursion)

A function may call itself, as long as there is a stopping point.

```krc
guno faktorial(n) {
    kalu n kurang_samo 1 { balik 1 }
    balik n * faktorial(n - 1)
}

nyetak faktorial(5)
nyetak faktorial(10)
```

```hasil
120
3628800
```

Without a stopping point, the function calls itself forever, and KerinciLang stops it with an error message.

```krc-error
guno tak_berhenti() {
    balik tak_berhenti()
}
tak_berhenti()
```

```hasil
Kesalahan: Panggilan fungsi terlalu dalam (lebih dari 400). Mungkin fungsi memanggil dirinya tanpa henti?
```

## Summary

- `guno name(parameters) { ... }` creates a function; `name(values)` calls it.
- `balik value` returns the result.
- A barang inside a function lives only inside it.
- A function may call itself (recursion) if it has a stopping point.

## Exercises

1. Make a function `genap(n)` that returns `betul` if `n` is even.
2. Make a function `terbesar(list)` that returns the largest item.
3. Make a function `balik_kata(text)` that returns the text reversed, without using `pulang` (hint: a loop).

Answers: [answers.md](answers.md#lesson-8). Continue to [Lesson 9](09-maps-and-pilih.md).
