# Pelajaran 3: Berhitung dan menyambung teks

## Operator hitung

| Operator | Arti | Contoh | Hasil |
|---|---|---|---|
| `+` | tambah | `7 + 3` | `10` |
| `-` | kurang | `7 - 3` | `4` |
| `*` | kali | `7 * 3` | `21` |
| `/` | bagi | `7 / 2` | `3.5` |
| `%` | sisa bagi | `7 % 3` | `1` |

```krc
nyetak 7 + 3
nyetak 7 - 3
nyetak 7 * 3
nyetak 7 / 2
nyetak 7 % 3
nyetak 8 / 2
```

```hasil
10
4
21
3.5
1
4
```

Pembagian yang habis dibagi menghasilkan bilangan bulat (`8 / 2` adalah `4`). Kalau tidak habis, hasilnya desimal.

## Urutan perhitungan

Kali, bagi, dan sisa dikerjakan sebelum tambah dan kurang. Kurung `( )` mengubah urutan.

```krc
nyetak 2 + 3 * 4
nyetak (2 + 3) * 4
nyetak 10 - 2 - 3
```

```hasil
14
20
5
```

## Menghitung dengan barang

```krc
barang harga = 15000
barang jumlah = 3
barang total = harga * jumlah
nyetak "Total: " + total
```

```hasil
Total: 45000
```

## Menyambung teks

Tanda `+` juga menyambung teks. Kalau salah satu sisinya teks, sisi lain otomatis diubah jadi teks.

```krc
barang depan = "Budi"
barang belakang = "Santoso"
nyetak depan + " " + belakang
nyetak "Umur: " + 20
nyetak "Benar? " + betul
```

```hasil
Budi Santoso
Umur: 20
Benar? betul
```

Hati-hati: urutan penting. Kalau kedua sisinya bilangan, `+` menjumlahkan, bukan menyambung.

```krc
nyetak 1 + 2 + "a"
nyetak "a" + 1 + 2
```

```hasil
3a
a12
```

`panjang` menghitung jumlah huruf dalam teks:

```krc
nyetak panjang("kerinci")
```

```hasil
7
```

## Fungsi hitung

Setiap operator punya kata Kerinci sebagai fungsi: `tambah`, `kurang`, `kali`, dan `bagi`. Hasilnya sama dengan operator.

```krc
nyetak tambah(2, 3)
nyetak kurang(10, 4)
nyetak kali(6, 7)
nyetak bagi(9, 2)
```

```hasil
5
6
42
4.5
```

## Kesalahan: membagi nol, jenis tidak cocok

```krc-error
nyetak 10 / 0
```

```hasil
Kesalahan: Pembagian dengan nol
```

```krc-error
nyetak "a" - 1
```

```hasil
Kesalahan: Operator '-' tidak bisa dipakai pada "a" dan 1
```

## Ringkasan

- `+ - * / %` untuk berhitung; kurung mengatur urutan.
- `+` menyambung teks bila salah satu sisinya teks.
- `panjang(teks)` menghitung huruf.
- `tambah`, `kurang`, `kali`, `bagi` adalah versi fungsi.

## Latihan

1. Hitung luas persegi panjang 12 kali 5 dan cetak: `Luas: 60`.
2. Berapa sisa 100 dibagi 7?
3. Ubah suhu 30 derajat Celsius ke Fahrenheit dengan rumus `C * 9 / 5 + 32`.

Jawaban: [jawaban.md](jawaban.md#pelajaran-3). Lanjut ke [Pelajaran 4](04-bertanya.md).
