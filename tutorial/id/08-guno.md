# Pelajaran 8: Guno, membuat fungsi sendiri

Kalau satu potongan program dipakai berkali-kali, bungkus dalam sebuah **guno** (fungsi), beri nama, lalu panggil kapan pun.

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

`guno sapa(nama) { ... }` membuat fungsi bernama `sapa` yang menerima satu bahan (**parameter**) bernama `nama`. `sapa("Budi")` memanggilnya.

## `balik`: mengembalikan hasil

`balik` mengirim sebuah nilai kembali kepada pemanggil dan mengakhiri fungsi.

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

Fungsi tanpa `balik` menghasilkan `kosong`.

```krc
guno diam() {
    barang x = 1
}
nyetak diam()
```

```hasil
kosong
```

## Banyak parameter

```krc
guno luas_persegi_panjang(panjang_sisi, lebar) {
    balik panjang_sisi * lebar
}
nyetak luas_persegi_panjang(12, 5)
```

```hasil
60
```

Jumlah bahan yang diberikan harus sama dengan jumlah parameter:

```krc-error
guno tambah_dua(a, b) { balik a + b }
nyetak tambah_dua(1)
```

```hasil
Kesalahan: Fungsi butuh 2 argumen, diberi 1
```

## Keputusan di dalam fungsi

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

## Fungsi dan daftar

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

## Ruang lingkup

Barang yang dibuat **di dalam** fungsi hanya hidup di dalam fungsi itu. Fungsi bisa membaca dan mengubah barang dari luar yang sudah dibuat sebelumnya.

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

## Fungsi memanggil dirinya (rekursi)

Fungsi boleh memanggil dirinya sendiri, asal ada titik berhenti.

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

Tanpa titik berhenti, fungsi memanggil dirinya tanpa henti, dan KerinciLang menghentikannya dengan pesan kesalahan.

```krc-error
guno tak_berhenti() {
    balik tak_berhenti()
}
tak_berhenti()
```

```hasil
Kesalahan: Panggilan fungsi terlalu dalam (lebih dari 400). Mungkin fungsi memanggil dirinya tanpa henti?
```

## Ringkasan

- `guno nama(bahan) { ... }` membuat fungsi; `nama(nilai)` memanggilnya.
- `balik nilai` mengembalikan hasil.
- Barang di dalam fungsi hanya hidup di dalamnya.
- Fungsi boleh memanggil dirinya (rekursi) dengan titik berhenti.

## Latihan

1. Buat fungsi `genap(n)` yang mengembalikan `betul` kalau `n` genap.
2. Buat fungsi `terbesar(daftar)` yang mengembalikan anggota terbesar.
3. Buat fungsi `balik_kata(teks)` yang mengembalikan teks terbalik tanpa memakai `pulang` (petunjuk: perulangan).

Jawaban: [jawaban.md](jawaban.md#pelajaran-8). Lanjut ke [Pelajaran 9](09-peta-dan-pilih.md).
