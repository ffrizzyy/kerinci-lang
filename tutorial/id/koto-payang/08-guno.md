# Pelajaran 8: Guno, membuat fungsi sendiri

Kalau satu potongan program dipakai berkali-kali, bungkus dalam sebuah **guno** (fungsi), beri nama, lalu panggil kapan pun.

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

`jeloehka sapa(nama) { ... }` membuat fungsi bernama `sapa` yang menerima satu bahan (**parameter**) bernama `nama`. `sapa("Budi")` memanggilnya.

## `baluikka`: mengembalikan hasil

`baluikka` mengirim sebuah nilai kembali kepada pemanggil dan mengakhiri fungsi.

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

Fungsi tanpa `baluikka` menghasilkan `kusao`.

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

## Banyak parameter

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

Jumlah bahan yang diberikan harus sama dengan jumlah parameter:

```krc-error
# dialek: koto-payang
jeloehka tambah_dua(a, b) { baluikka a + b }
nytak tambah_dua(1)
```

```hasil
Kesalahan: Pungsi butuh 2 argumen, dibaguih 1
```

## Keputusan di dalam fungsi

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

## Fungsi dan daftar

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

## Ruang lingkup

Barang yang dibuat **di dalam** fungsi hanya hidup di dalam fungsi itu. Fungsi bisa membaca dan mengubah barang dari luar yang sudah dibuat sebelumnya.

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

## Fungsi memanggil dirinya (rekursi)

Fungsi boleh memanggil dirinya sendiri, asal ada titik berhenti.

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

Tanpa titik berhenti, fungsi memanggil dirinya tanpa henti, dan KerinciLang menghentikannya dengan pesan kesalahan.

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

## Ringkasan

- `jeloehka nama(bahan) { ... }` membuat fungsi; `nama(nilai)` memanggilnya.
- `baluikka nilai` mengembalikan hasil.
- Barang di dalam fungsi hanya hidup di dalamnya.
- Fungsi boleh memanggil dirinya (rekursi) dengan titik berhenti.

## Latihan

1. Buat fungsi `genap(n)` yang mengembalikan `betiu` kalau `n` genap.
2. Buat fungsi `terbesar(daftar)` yang mengembalikan anggota terbesar.
3. Buat fungsi `balik_kata(teks)` yang mengembalikan teks terbalik tanpa memakai `tebaluik` (petunjuk: perulangan).

Jawaban: [jawaban.md](jawaban.md#pelajaran-8). Lanjut ke [Pelajaran 9](09-peta-dan-pilih.md).

---
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: review).*
