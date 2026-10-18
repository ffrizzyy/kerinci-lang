# Pelajaran 5: Mengambil keputusan

Program yang berguna bisa memilih apa yang dikerjakan. Kata Kerinci untuk "jika" adalah `kalu`, dan untuk "kalau tidak" adalah `lain`.

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

Bagian di dalam `{ }` hanya dijalankan kalau syaratnya benar.

## Membandingkan

| Kata | Simbol | Arti |
|---|---|---|
| `samo` | `==` | sama dengan |
| `dak_samo` | `!=` | tidak sama dengan |
| `lebih_daripado` | `>` | lebih besar dari |
| `kurang_daripado` | `<` | lebih kecil dari |
| `lebih_samo` | `>=` | lebih besar atau sama |
| `kurang_samo` | `<=` | lebih kecil atau sama |

Kata dan simbol artinya sama persis, dan boleh dicampur. Pakai yang lebih nyaman.

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

Hasil perbandingan adalah `betul` atau `salah`.

Hati-hati: satu `=` artinya **mengisi** barang, dua `==` (atau kata `samo`) artinya **membandingkan**.

## Banyak pilihan: `lain kalu`

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

Komputer memeriksa dari atas dan berhenti pada syarat pertama yang benar.

## Menggabungkan syarat: `ngan`, `apo`, `idak`

| Kata | Arti | Benar kalau... |
|---|---|---|
| `ngan` | dan | kedua sisi benar |
| `apo` | atau | salah satu sisi benar |
| `idak` | bukan | sisi itu salah |

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

## Nilai yang dianggap salah

Dalam syarat, nilai ini dianggap salah: `salah`, `kosong`, `0`, `""` (teks kosong), `[]` (daftar kosong), dan `{}` (peta kosong). Semua nilai lain dianggap benar.

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

## Keputusan di dalam keputusan

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

## Ringkasan

- `kalu syarat { ... } lain { ... }`; `lain kalu` untuk pilihan tambahan.
- Perbandingan: `samo`, `dak_samo`, `lebih_daripado`, `kurang_daripado`, `lebih_samo`, `kurang_samo`.
- Gabung syarat dengan `ngan`, `apo`, `idak`.

## Latihan

1. Tanyakan sebuah bilangan; cetak "genap" atau "ganjil" (petunjuk: `%`).
2. Tanyakan umur; cetak "anak" (di bawah 13), "remaja" (13 sampai 17), atau "dewasa".
3. Tanyakan tiga bilangan dan cetak yang terbesar.

Jawaban: [jawaban.md](jawaban.md#pelajaran-5). Lanjut ke [Pelajaran 6](06-perulangan.md).
