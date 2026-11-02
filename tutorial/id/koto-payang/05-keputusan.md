# Pelajaran 5: Mengambil keputusan

Program yang berguna bisa memilih apa yang dikerjakan. Kata Kerinci untuk "jika" adalah `kalu`, dan untuk "kalau tidak" adalah `nga_laen`.

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

Bagian di dalam `{ }` hanya dijalankan kalau syaratnya benar.

## Membandingkan

| Kata | Simbol | Arti |
|---|---|---|
| `samu_dinga` | `==` | sama dengan |
| `iduak_samu_dinga` | `!=` | tidak sama dengan |
| `lebih_geduang_dari` | `>` | lebih besar dari |
| `lebih_nik_dari` | `<` | lebih kecil dari |
| `lebih_geduang_atau_samu_dinga` | `>=` | lebih besar atau sama |
| `lebih_nik_atau_samu_dinga` | `<=` | lebih kecil atau sama |

Kata dan simbol artinya sama persis, dan boleh dicampur. Pakai yang lebih nyaman.

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

Hasil perbandingan adalah `betiu` atau `salah`.

Hati-hati: satu `=` artinya **mengisi** barang, dua `==` (atau kata `samu_dinga`) artinya **membandingkan**.

## Banyak pilihan: `nga_laen kalu`

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

Komputer memeriksa dari atas dan berhenti pada syarat pertama yang benar.

## Menggabungkan syarat: `nga`, `atau`, `iduak`

| Kata | Arti | Benar kalau... |
|---|---|---|
| `nga` | dan | kedua sisi benar |
| `atau` | atau | salah satu sisi benar |
| `iduak` | bukan | sisi itu salah |

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

## Nilai yang dianggap salah

Dalam syarat, nilai ini dianggap salah: `salah`, `kusao`, `0`, `""` (teks kosong), `[]` (daftar kosong), dan `{}` (peta kosong). Semua nilai lain dianggap benar.

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

## Keputusan di dalam keputusan

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

## Ringkasan

- `kalu syarat { ... } nga_laen { ... }`; `nga_laen kalu` untuk pilihan tambahan.
- Perbandingan: `samu_dinga`, `iduak_samu_dinga`, `lebih_geduang_dari`, `lebih_nik_dari`, `lebih_geduang_atau_samu_dinga`, `lebih_nik_atau_samu_dinga`.
- Gabung syarat dengan `nga`, `atau`, `iduak`.

## Latihan

1. Tanyakan sebuah bilangan; cetak "genap" atau "ganjil" (petunjuk: `%`).
2. Tanyakan umur; cetak "anak" (di bawah 13), "remaja" (13 sampai 17), atau "dewasa".
3. Tanyakan tiga bilangan dan cetak yang terbesar.

Jawaban: [jawaban.md](jawaban.md#pelajaran-5). Lanjut ke [Pelajaran 6](06-perulangan.md).

---
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: review).*
