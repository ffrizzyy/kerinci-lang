# Pelajaran 7: Daftar

Satu barang bisa menyimpan banyak nilai sekaligus dalam sebuah **daftar**.

```krc
barang buah = ["pisang", "apel", "jeruk"]
nyetak buah
nyetak panjang(buah)
```

```hasil
["pisang", "apel", "jeruk"]
3
```

## Mengambil anggota

Setiap anggota punya nomor urut, dan **dimulai dari 0**.

```krc
barang buah = ["pisang", "apel", "jeruk"]
nyetak buah[0]
nyetak buah[2]
```

```hasil
pisang
jeruk
```

Anggota terakhir ada di nomor `panjang(buah) - 1`. Nomor di luar daftar adalah kesalahan:

```krc-error
barang buah = ["pisang", "apel"]
nyetak buah[5]
```

```hasil
Kesalahan: Indeks di luar jangkauan: 5 (panjang 2)
```

## Mengubah dan menambah

```krc
barang buah = ["pisang", "apel"]
buah[0] = "mangga"
nambahkah(buah, "jeruk")
nyetak buah
```

```hasil
["mangga", "apel", "jeruk"]
```

`nambahkah(daftar, nilai)` menambahkan nilai di **ujung** daftar dan mengubah daftar itu sendiri.

## Alat-alat daftar

| Tulis | Fungsinya |
|---|---|
| `panjang(d)` | jumlah anggota |
| `nambahkah(d, x)` | tambah `x` di ujung (mengubah `d`) |
| `isi(d, x)` | apakah `x` ada di `d`? (`betul`/`salah`) |
| `milih(d)` | salinan yang **terurut** (`d` tidak berubah) |
| `pulang(d)` | salinan yang **terbalik** (`d` tidak berubah) |
| `d1 + d2` | gabungan dua daftar (daftar baru) |

```krc
barang angka = [5, 2, 9, 1]
nyetak milih(angka)
nyetak pulang(angka)
nyetak angka
nyetak isi(angka, 9)
nyetak isi(angka, 7)
nyetak angka + [100, 200]
```

```hasil
[1, 2, 5, 9]
[1, 9, 2, 5]
[5, 2, 9, 1]
betul
salah
[5, 2, 9, 1, 100, 200]
```

## Daftar dan perulangan

```krc
barang nilai = [80, 65, 90, 55, 75]
barang total = 0
untuk n alem nilai {
    total = total + n
}
nyetak "Rata-rata: " + bagi(total, panjang(nilai))

barang tertinggi = nilai[0]
untuk n alem nilai {
    kalu n lebih_daripado tertinggi { tertinggi = n }
}
nyetak "Tertinggi: " + tertinggi
```

```hasil
Rata-rata: 73
Tertinggi: 90
```

Kalau butuh nomor urutnya, ulangi `jarak(panjang(daftar))`:

```krc
barang nama = ["Budi", "Sari", "Dewi"]
untuk i alem jarak(panjang(nama)) {
    nyetak (i + 1) + ". " + nama[i]
}
```

```hasil
1. Budi
2. Sari
3. Dewi
```

## Daftar di dalam daftar

```krc
barang papan = [[1, 2, 3], [4, 5, 6]]
nyetak papan[1][0]
papan[0][2] = 99
nyetak papan
```

```hasil
4
[[1, 2, 99], [4, 5, 6]]
```

## Hati-hati: daftar dibagi, bukan disalin

`barang b = a` tidak membuat salinan; `a` dan `b` menunjuk daftar yang sama.

```krc
barang a = [1, 2, 3]
barang b = a
b[0] = 100
nyetak a

barang c = a + []
c[0] = 5
nyetak a
nyetak c
```

```hasil
[100, 2, 3]
[100, 2, 3]
[5, 2, 3]
```

`a + []` membuat daftar baru, jadi itu cara menyalin.

## Ringkasan

- `[a, b, c]` membuat daftar; `d[0]` mengambil anggota pertama.
- `nambahkah`, `isi`, `milih`, `pulang`, `panjang`.
- Nomor mulai dari 0.
- `barang b = a` berbagi daftar yang sama.

## Latihan

1. Buat daftar lima nama, cetak tiap nama dengan nomornya.
2. Buat daftar bilangan dan cetak jumlah serta nilai terkecilnya.
3. Buat daftar baru yang berisi kuadrat dari 1 sampai 5.

Jawaban: [jawaban.md](jawaban.md#pelajaran-7). Lanjut ke [Pelajaran 8](08-guno.md).
