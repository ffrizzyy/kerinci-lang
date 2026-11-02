# Pelajaran 4: Bertanya kepada pengguna

`masukka()` menunggu pengguna mengetik sesuatu, lalu mengembalikannya sebagai teks.

```krc masukan=Budi
# dialek: koto-payang
nytak "Siapa namamu?"
netakka_variabel nama = masukka()
nytak "Halo, " + nama
```

```hasil
Siapa namamu?
Halo, Budi
```

(Contoh ini dijalankan dengan masukan `Budi`, seolah-olah pengguna mengetik "Budi".)

## Masukan selalu berupa teks

Walau pengguna mengetik angka, `masukka()` memberikan **teks**. Ini jebakan umum:

```krc masukan=20
# dialek: koto-payang
nytak "Umur?"
netakka_variabel umur = masukka()
nytak tipe(umur)
nytak umur + 1
```

```hasil
Umur?
tulisan
201
```

`"20" + 1` menyambung teks, hasilnya `"201"`. Untuk menghitung, ubah dulu jadi bilangan dengan `bilangan_buluak`.

```krc masukan=20
# dialek: koto-payang
nytak "Umur?"
netakka_variabel umur = bilangan_buluak(masukka())
nytak tipe(umur)
nytak "Tahun depan: " + (umur + 1)
```

```hasil
Umur?
bilangan_buluak
Tahun depan: 21
```

## Fungsi pengubah jenis

| Fungsi | Mengubah menjadi | Contoh | Hasil |
|---|---|---|---|
| `bilangan_buluak(x)` | bilangan bulat | `bilangan_buluak("42")` | `42` |
| `bilangan_buluak(x)` | (desimal dipotong) | `bilangan_buluak(3.7)` | `3` |
| `desimal(x)` | desimal | `desimal("2.5")` | `2.5` |
| `tulisan(x)` | teks | `tulisan(12)` | `"12"` |

```krc
# dialek: koto-payang
nytak bilangan_buluak("42") + 1
nytak bilangan_buluak(3.7)
nytak desimal("2.5") * 2
nytak tulisan(12) + "!"
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
# dialek: koto-payang
netakka_variabel umur = bilangan_buluak(masukka())
nytak umur
```

```hasil
Kesalahan: Nynendak ngubuoah "dua puluh" jadi bilangan_buluak
```

Di [Pelajaran 12](12-kesalahan.md) kamu akan belajar menangani kesalahan seperti ini dengan baik.

## Contoh: kalkulator kecil

```krc masukan=8|5
# dialek: koto-payang
nytak "Bilangan pertama?"
netakka_variabel a = bilangan_buluak(masukka())
nytak "Bilangan kedua?"
netakka_variabel b = bilangan_buluak(masukka())
nytak a + " + " + b + " = " + (a + b)
nytak a + " * " + b + " = " + (a * b)
```

```hasil
Bilangan pertama?
Bilangan kedua?
8 + 5 = 13
8 * 5 = 40
```

## Ringkasan

- `masukka()` membaca satu baris sebagai teks.
- `bilangan_buluak`, `desimal`, dan `tulisan` mengubah jenis.
- Ubah masukan sebelum menghitung.

## Latihan

1. Tanyakan nama dan kota, lalu cetak: `Budi tinggal di Sungai Penuh`.
2. Tanyakan dua bilangan dan cetak rata-ratanya.
3. Tanyakan panjang sisi persegi, cetak luasnya.

Jawaban: [jawaban.md](jawaban.md#pelajaran-4). Lanjut ke [Pelajaran 5](05-keputusan.md).

---
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: review).*
