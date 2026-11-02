# Pelajaran 7: Daftar

Satu barang bisa menyimpan banyak nilai sekaligus dalam sebuah **daftar**.

```krc
# dialek: koto-payang
netakka_variabel buah = ["pisang", "apel", "jeruk"]
nytak buah
nytak panja(buah)
```

```hasil
["pisang", "apel", "jeruk"]
3
```

## Mengambil anggota

Setiap anggota punya nomor urut, dan **dimulai dari 0**.

```krc
# dialek: koto-payang
netakka_variabel buah = ["pisang", "apel", "jeruk"]
nytak buah[0]
nytak buah[2]
```

```hasil
pisang
jeruk
```

Anggota terakhir ada di nomor `panja(buah) - 1`. Nomor di luar daftar adalah kesalahan:

```krc-error
# dialek: koto-payang
netakka_variabel buah = ["pisang", "apel"]
nytak buah[5]
```

```hasil
Kesalahan: Indeks kik luwua jangkauan: 5 (panja 2)
```

## Mengubah dan menambah

```krc
# dialek: koto-payang
netakka_variabel buah = ["pisang", "apel"]
buah[0] = "mangga"
tambahka(buah, "jeruk")
nytak buah
```

```hasil
["mangga", "apel", "jeruk"]
```

`nambahkah(daftar, nilai)` menambahkan nilai di **ujung** daftar dan mengubah daftar itu sendiri.

## Alat-alat daftar

| Tulis | Fungsinya |
|---|---|
| `panja(d)` | jumlah anggota |
| `tambahka(d, x)` | tambah `x` di ujung (mengubah `d`) |
| `contains(d, x)` | apakah `x` ada di `d`? (`betiu`/`salah`) |
| `terurut(d)` | salinan yang **terurut** (`d` tidak berubah) |
| `tebaluik(d)` | salinan yang **terbalik** (`d` tidak berubah) |
| `d1 + d2` | gabungan dua daftar (daftar baru) |

```krc
# dialek: koto-payang
netakka_variabel angka = [5, 2, 9, 1]
nytak terurut(angka)
nytak tebaluik(angka)
nytak angka
nytak contains(angka, 9)
nytak contains(angka, 7)
nytak angka + [100, 200]
```

```hasil
[1, 2, 5, 9]
[1, 9, 2, 5]
[5, 2, 9, 1]
betiu
salah
[5, 2, 9, 1, 100, 200]
```

## Daftar dan perulangan

```krc
# dialek: koto-payang
netakka_variabel nilai = [80, 65, 90, 55, 75]
netakka_variabel total = 0
ndik n daling nilai {
    total = total + n
}
nytak "Rata-rata: " + bagi(total, panja(nilai))

netakka_variabel tertinggi = nilai[0]
ndik n daling nilai {
    kalu n lebih_geduang_dari tertinggi { tertinggi = n }
}
nytak "Tertinggi: " + tertinggi
```

```hasil
Rata-rata: 73
Tertinggi: 90
```

Kalau butuh nomor urutnya, ulangi `jarak(panjang(daftar))`:

```krc
# dialek: koto-payang
netakka_variabel nama = ["Budi", "Sari", "Dewi"]
ndik i daling rentang(panja(nama)) {
    nytak (i + 1) + ". " + nama[i]
}
```

```hasil
1. Budi
2. Sari
3. Dewi
```

## Daftar di dalam daftar

```krc
# dialek: koto-payang
netakka_variabel papan = [[1, 2, 3], [4, 5, 6]]
nytak papan[1][0]
papan[0][2] = 99
nytak papan
```

```hasil
4
[[1, 2, 99], [4, 5, 6]]
```

## Hati-hati: daftar dibagi, bukan disalin

`netakka_variabel b = a` tidak membuat salinan; `a` dan `b` menunjuk daftar yang sama.

```krc
# dialek: koto-payang
netakka_variabel a = [1, 2, 3]
netakka_variabel b = a
b[0] = 100
nytak a

netakka_variabel c = a + []
c[0] = 5
nytak a
nytak c
```

```hasil
[100, 2, 3]
[100, 2, 3]
[5, 2, 3]
```

`a + []` membuat daftar baru, jadi itu cara menyalin.

## Ringkasan

- `[a, b, c]` membuat daftar; `d[0]` mengambil anggota pertama.
- `tambahka`, `contains`, `terurut`, `tebaluik`, `panja`.
- Nomor mulai dari 0.
- `netakka_variabel b = a` berbagi daftar yang sama.

## Latihan

1. Buat daftar lima nama, cetak tiap nama dengan nomornya.
2. Buat daftar bilangan dan cetak jumlah serta nilai terkecilnya.
3. Buat daftar baru yang berisi kuadrat dari 1 sampai 5.

Jawaban: [jawaban.md](jawaban.md#pelajaran-7). Lanjut ke [Pelajaran 8](08-guno.md).

---
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: review).*
