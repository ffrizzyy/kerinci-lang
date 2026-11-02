# Pelajaran 6: Mengulang

Komputer paling hebat dalam mengerjakan hal yang sama berkali-kali tanpa bosan.

## `selamu`: ulangi selama syarat benar

```krc
# dialek: koto-payang
netakka_variabel i = 1
selamu i lebih_nik_atau_samu_dinga 5 {
    nytak i
    i = i + 1
}
```

```hasil
1
2
3
4
5
```

`selamu` memeriksa syarat. Kalau benar, isi `{ }` dijalankan, lalu syarat diperiksa lagi. Kalau lupa mengubah `i`, perulangan tidak akan pernah berhenti!

## `ndik ... daling`: untuk setiap anggota

`ndik x daling sesuatu { ... }` mengerjakan isi `{ }` sekali untuk tiap anggota. `daling` berarti "dalam".

```krc
# dialek: koto-payang
ndik buah daling ["pisang", "apel", "jeruk"] {
    nytak "Saya suka " + buah
}
```

```hasil
Saya suka pisang
Saya suka apel
Saya suka jeruk
```

Teks juga bisa diulang huruf demi huruf:

```krc
# dialek: koto-payang
ndik huruf daling "kerinci" {
    nytak huruf
}
```

```hasil
k
e
r
i
n
c
i
```

## `rentang`: menghitung

`rentang` membuat daftar bilangan, dan sangat cocok dipakai dengan `ndik`.

| Tulis | Hasil |
|---|---|
| `rentang(5)` | `[0, 1, 2, 3, 4]` |
| `rentang(2, 6)` | `[2, 3, 4, 5]` |
| `rentang(0, 10, 3)` | `[0, 3, 6, 9]` |

Perhatikan: bilangan terakhir **tidak** ikut. `rentang(5)` mulai dari 0 dan berhenti sebelum 5.

```krc
# dialek: koto-payang
ndik i daling rentang(1, 6) {
    nytak "Hitungan " + i
}
nytak rentang(0, 10, 3)
nytak rentang(5, 0, 0 - 1)
```

```hasil
Hitungan 1
Hitungan 2
Hitungan 3
Hitungan 4
Hitungan 5
[0, 3, 6, 9]
[5, 4, 3, 2, 1]
```

## `slese` dan `lanjutka`

- `slese` menghentikan perulangan sekarang juga.
- `lanjutka` melewati sisa isi perulangan dan langsung ke putaran berikutnya.

```krc
# dialek: koto-payang
ndik i daling rentang(1, 11) {
    kalu i % 2 samu_dinga 0 { lanjutka }
    kalu i lebih_geduang_dari 7 { slese }
    nytak i
}
```

```hasil
1
3
5
7
```

Ini mencetak bilangan ganjil dan berhenti setelah lewat 7.

> Hati-hati memakai `lanjutka` di dalam `selamu`: kalau penambahan `i = i + 1` ada **setelah** `lanjutka`, penambahan itu terlewati dan perulangan tidak pernah berhenti. Taruh penambahan di awal isi perulangan.

## Perulangan di dalam perulangan

```krc
# dialek: koto-payang
ndik baris daling rentang(1, 4) {
    netakka_variabel garis = ""
    ndik kolom daling rentang(1, 4) {
        garis = garis + (baris * kolom) + "\t"
    }
    nytak garis
}
```

```hasil
1	2	3	
2	4	6	
3	6	9	
```

## Contoh: menjumlahkan dan menebak

```krc
# dialek: koto-payang
netakka_variabel total = 0
ndik angka daling rentang(1, 101) {
    total = total + angka
}
nytak "Jumlah 1 sampai 100: " + total
```

```hasil
Jumlah 1 sampai 100: 5050
```

```krc masukan=50|80|77|25
# dialek: koto-payang
netakka_konstanta rahasia = 77
netakka_variabel tebakan = 0
netakka_variabel percobaan = 0
selamu tebakan iduak_samu_dinga rahasia {
    nytak "Tebak angka (1-100):"
    tebakan = bilangan_buluak(masukka())
    percobaan = percobaan + 1
    kalu tebakan lebih_nik_dari rahasia {
        nytak "Terlalu kecil"
    } nga_laen kalu tebakan lebih_geduang_dari rahasia {
        nytak "Terlalu besar"
    }
}
nytak "Benar! Percobaan: " + percobaan
```

```hasil
Tebak angka (1-100):
Terlalu kecil
Tebak angka (1-100):
Terlalu besar
Tebak angka (1-100):
Benar! Percobaan: 3
```

## Ringkasan

- `selamu syarat { }` mengulang selama syarat benar.
- `untuk x alem daftar { }` mengulang untuk setiap anggota.
- `rentang(a, b)` menghasilkan bilangan dari a sampai sebelum b.
- `slese` berhenti; `lanjutka` melompat ke putaran berikutnya.

## Latihan

1. Cetak bilangan 10 sampai 1 (hitung mundur).
2. Cetak tabel kali 7, dari 7 x 1 sampai 7 x 10.
3. Jumlahkan semua bilangan genap dari 1 sampai 50.

Jawaban: [jawaban.md](jawaban.md#pelajaran-6). Lanjut ke [Pelajaran 7](07-daftar.md).

---
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: review).*
