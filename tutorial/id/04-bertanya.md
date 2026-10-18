# Pelajaran 4: Bertanya kepada pengguna

`tanyo()` menunggu pengguna mengetik sesuatu, lalu mengembalikannya sebagai teks.

```krc masukan=Budi
nyetak "Siapa namamu?"
barang nama = tanyo()
nyetak "Halo, " + nama
```

```hasil
Siapa namamu?
Halo, Budi
```

(Contoh ini dijalankan dengan masukan `Budi`, seolah-olah pengguna mengetik "Budi".)

## Masukan selalu berupa teks

Walau pengguna mengetik angka, `tanyo()` memberikan **teks**. Ini jebakan umum:

```krc masukan=20
nyetak "Umur?"
barang umur = tanyo()
nyetak mecem(umur)
nyetak umur + 1
```

```hasil
Umur?
kato
201
```

`"20" + 1` menyambung teks, hasilnya `"201"`. Untuk menghitung, ubah dulu jadi bilangan dengan `bilangan`.

```krc masukan=20
nyetak "Umur?"
barang umur = bilangan(tanyo())
nyetak mecem(umur)
nyetak "Tahun depan: " + (umur + 1)
```

```hasil
Umur?
bilangan
Tahun depan: 21
```

## Fungsi pengubah jenis

| Fungsi | Mengubah menjadi | Contoh | Hasil |
|---|---|---|---|
| `bilangan(x)` | bilangan bulat | `bilangan("42")` | `42` |
| `bilangan(x)` | (desimal dipotong) | `bilangan(3.7)` | `3` |
| `pecahan(x)` | desimal | `pecahan("2.5")` | `2.5` |
| `kato(x)` | teks | `kato(12)` | `"12"` |

```krc
nyetak bilangan("42") + 1
nyetak bilangan(3.7)
nyetak pecahan("2.5") * 2
nyetak kato(12) + "!"
```

```hasil
43
3
5.0
12!
```

## Kalau masukan tidak bisa diubah

Mengubah "dua puluh" menjadi bilangan tidak mungkin, dan programmu berhenti dengan pesan kesalahan:

```krc-error masukan=dua puluh
barang umur = bilangan(tanyo())
nyetak umur
```

```hasil
Kesalahan: Tidak bisa mengubah "dua puluh" menjadi bilangan
```

Di [Pelajaran 12](12-kesalahan.md) kamu akan belajar menangani kesalahan seperti ini dengan baik.

## Contoh: kalkulator kecil

```krc masukan=8|5
nyetak "Bilangan pertama?"
barang a = bilangan(tanyo())
nyetak "Bilangan kedua?"
barang b = bilangan(tanyo())
nyetak a + " + " + b + " = " + (a + b)
nyetak a + " * " + b + " = " + (a * b)
```

```hasil
Bilangan pertama?
Bilangan kedua?
8 + 5 = 13
8 * 5 = 40
```

## Ringkasan

- `tanyo()` membaca satu baris sebagai teks.
- `bilangan`, `pecahan`, dan `kato` mengubah jenis.
- Ubah masukan sebelum menghitung.

## Latihan

1. Tanyakan nama dan kota, lalu cetak: `Budi tinggal di Sungai Penuh`.
2. Tanyakan dua bilangan dan cetak rata-ratanya.
3. Tanyakan panjang sisi persegi, cetak luasnya.

Jawaban: [jawaban.md](jawaban.md#pelajaran-4). Lanjut ke [Pelajaran 5](05-keputusan.md).
