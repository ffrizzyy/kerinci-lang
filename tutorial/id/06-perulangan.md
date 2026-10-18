# Pelajaran 6: Mengulang

Komputer paling hebat dalam mengerjakan hal yang sama berkali-kali tanpa bosan.

## `selamo`: ulangi selama syarat benar

```krc
barang i = 1
selamo i kurang_samo 5 {
    nyetak i
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

`selamo` memeriksa syarat. Kalau benar, isi `{ }` dijalankan, lalu syarat diperiksa lagi. Kalau lupa mengubah `i`, perulangan tidak akan pernah berhenti!

## `untuk ... alem`: untuk setiap anggota

`untuk x alem sesuatu { ... }` mengerjakan isi `{ }` sekali untuk tiap anggota. `alem` berarti "dalam".

```krc
untuk buah alem ["pisang", "apel", "jeruk"] {
    nyetak "Saya suka " + buah
}
```

```hasil
Saya suka pisang
Saya suka apel
Saya suka jeruk
```

Teks juga bisa diulang huruf demi huruf:

```krc
untuk huruf alem "kerinci" {
    nyetak huruf
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

## `jarak`: menghitung

`jarak` membuat daftar bilangan, dan sangat cocok dipakai dengan `untuk`.

| Tulis | Hasil |
|---|---|
| `jarak(5)` | `[0, 1, 2, 3, 4]` |
| `jarak(2, 6)` | `[2, 3, 4, 5]` |
| `jarak(0, 10, 3)` | `[0, 3, 6, 9]` |

Perhatikan: bilangan terakhir **tidak** ikut. `jarak(5)` mulai dari 0 dan berhenti sebelum 5.

```krc
untuk i alem jarak(1, 6) {
    nyetak "Hitungan " + i
}
nyetak jarak(0, 10, 3)
nyetak jarak(5, 0, 0 - 1)
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

## `putuh` dan `lanjut`

- `putuh` menghentikan perulangan sekarang juga.
- `lanjut` melewati sisa isi perulangan dan langsung ke putaran berikutnya.

```krc
untuk i alem jarak(1, 11) {
    kalu i % 2 samo 0 { lanjut }
    kalu i lebih_daripado 7 { putuh }
    nyetak i
}
```

```hasil
1
3
5
7
```

Ini mencetak bilangan ganjil dan berhenti setelah lewat 7.

> Hati-hati memakai `lanjut` di dalam `selamo`: kalau penambahan `i = i + 1` ada **setelah** `lanjut`, penambahan itu terlewati dan perulangan tidak pernah berhenti. Taruh penambahan di awal isi perulangan.

## Perulangan di dalam perulangan

```krc
untuk baris alem jarak(1, 4) {
    barang garis = ""
    untuk kolom alem jarak(1, 4) {
        garis = garis + (baris * kolom) + "\t"
    }
    nyetak garis
}
```

```hasil
1	2	3	
2	4	6	
3	6	9	
```

## Contoh: menjumlahkan dan menebak

```krc
barang total = 0
untuk angka alem jarak(1, 101) {
    total = total + angka
}
nyetak "Jumlah 1 sampai 100: " + total
```

```hasil
Jumlah 1 sampai 100: 5050
```

```krc masukan=50|80|77|25
tetap rahasia = 77
barang tebakan = 0
barang percobaan = 0
selamo tebakan dak_samo rahasia {
    nyetak "Tebak angka (1-100):"
    tebakan = bilangan(tanyo())
    percobaan = percobaan + 1
    kalu tebakan kurang_daripado rahasia {
        nyetak "Terlalu kecil"
    } lain kalu tebakan lebih_daripado rahasia {
        nyetak "Terlalu besar"
    }
}
nyetak "Benar! Percobaan: " + percobaan
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

- `selamo syarat { }` mengulang selama syarat benar.
- `untuk x alem daftar { }` mengulang untuk setiap anggota.
- `jarak(a, b)` menghasilkan bilangan dari a sampai sebelum b.
- `putuh` berhenti; `lanjut` melompat ke putaran berikutnya.

## Latihan

1. Cetak bilangan 10 sampai 1 (hitung mundur).
2. Cetak tabel kali 7, dari 7 x 1 sampai 7 x 10.
3. Jumlahkan semua bilangan genap dari 1 sampai 50.

Jawaban: [jawaban.md](jawaban.md#pelajaran-6). Lanjut ke [Pelajaran 7](07-daftar.md).
