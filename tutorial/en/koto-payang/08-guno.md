# Lesson 8: Guno, making your own functions

When a piece of a program is used again and again, wrap it in a **guno** (a function), give it a name, and call it whenever you like.

```krc
# dialek: koto-payang
jeloehka sapa(nama) {
    nytak "Halo, " + nama
}

sapa("Budi")
sapa("Sari")
```

```hasil
Halo, Budi
Halo, Sari
```

`jeloehka sapa(nama) { ... }` creates a function named `sapa` ("greet") that takes one ingredient (a **parameter**) named `nama`. `sapa("Budi")` calls it.

## `baluikka`: returning a result

`baluikka` sends a value back to the caller and ends the function.

```krc
# dialek: koto-payang
jeloehka kuadrat(x) {
    baluikka x * x
}

nytak kuadrat(5)
netakka_variabel hasil = kuadrat(3) + kuadrat(4)
nytak hasil
```

```hasil
25
25
```

A function without `baluikka` gives `kusao`.

```krc
# dialek: koto-payang
jeloehka diam() {
    netakka_variabel x = 1
}
nytak diam()
```

```hasil
kusao
```

## Several parameters

```krc
# dialek: koto-payang
jeloehka luas_persegi_panjang(panjang_sisi, lebar) {
    baluikka panjang_sisi * lebar
}
nytak luas_persegi_panjang(12, 5)
```

```hasil
60
```

The number of values given must equal the number of parameters:

```krc-error
# dialek: koto-payang
jeloehka tambah_dua(a, b) { baluikka a + b }
nytak tambah_dua(1)
```

```hasil
Kesalahan: Pungsi butuh 2 argumen, dibaguih 1
```

## Decisions inside a function

```krc
# dialek: koto-payang
jeloehka huruf_nilai(nilai) {
    kalu nilai lebih_geduang_atau_samu_dinga 90 { baluikka "A" }
    kalu nilai lebih_geduang_atau_samu_dinga 80 { baluikka "B" }
    kalu nilai lebih_geduang_atau_samu_dinga 70 { baluikka "C" }
    baluikka "D"
}

nytak huruf_nilai(95)
nytak huruf_nilai(72)
nytak huruf_nilai(40)
```

```hasil
A
C
D
```

## Functions and lists

```krc
# dialek: koto-payang
jeloehka rata_rata(daftar_nilai) {
    kalu panja(daftar_nilai) samu_dinga 0 { baluikka 0 }
    netakka_variabel total = 0
    ndik n daling daftar_nilai { total = total + n }
    baluikka bagi(total, panja(daftar_nilai))
}

nytak rata_rata([80, 70, 90])
nytak rata_rata([])
```

```hasil
80
0
```

## Scope

A barang created **inside** a function lives only inside that function. A function can read and change barang from outside that were created earlier.

```krc
# dialek: koto-payang
netakka_variabel hitungan = 0

jeloehka tambah_hitungan() {
    hitungan = hitungan + 1
}

tambah_hitungan()
tambah_hitungan()
nytak hitungan
```

```hasil
2
```

```krc-error
# dialek: koto-payang
jeloehka buat() {
    netakka_variabel rahasia = 42
}
buat()
nytak rahasia
```

```hasil
Kesalahan: namu lao dijeloehka: rahasia
```

## A function calling itself (recursion)

A function may call itself, as long as there is a stopping point.

```krc
# dialek: koto-payang
jeloehka faktorial(n) {
    kalu n lebih_nik_atau_samu_dinga 1 { baluikka 1 }
    baluikka n * faktorial(n - 1)
}

nytak faktorial(5)
nytak faktorial(10)
```

```hasil
120
3628800
```

Without a stopping point, the function calls itself forever, and KerinciLang stops it with an error message.

```krc-error
# dialek: koto-payang
jeloehka tak_berhenti() {
    baluikka tak_berhenti()
}
tak_berhenti()
```

```hasil
Kesalahan: Panggilan pungsi daling nia (lebih dari 400)
```

## Summary

- `jeloehka name(parameters) { ... }` creates a function; `name(values)` calls it.
- `baluikka value` returns the result.
- A barang inside a function lives only inside it.
- A function may call itself (recursion) if it has a stopping point.

## Exercises

1. Make a function `genap(n)` that returns `betiu` if `n` is even.
2. Make a function `terbesar(list)` that returns the largest item.
3. Make a function `balik_kata(text)` that returns the text reversed, without using `tebaluik` (hint: a loop).

Answers: [answers.md](answers.md#lesson-8). Continue to [Lesson 9](09-maps-and-pilih.md).

---
*Generated from the Siulak lesson. Code and inline code use Koto Payang
(status: approved).*
