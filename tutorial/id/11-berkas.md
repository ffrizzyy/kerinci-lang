# Pelajaran 11: Berkas

Sejauh ini, semua yang diingat programmu hilang saat program selesai. Dengan **berkas**, program bisa menyimpan data di disk dan membacanya lagi nanti.

## Cara tercepat: `tulis` dan `baco`

```krc
tulis("catatan.txt", "Belajar KerinciLang\nHari ini membuat program\n")
nyetak baco("catatan.txt")
```

```hasil
Belajar KerinciLang
Hari ini membuat program
```

- `tulis(nama, teks)` membuat berkas, atau **mengganti seluruh isinya** kalau sudah ada.
- `baco(nama)` membaca seluruh isi berkas sebagai satu teks.

## Membuka berkas: `bukak`, `tutup`

Untuk menulis sedikit-sedikit atau menambah di ujung, buka berkasnya dulu dengan `bukak(nama, mode)`. Selesai? `tutup(berkas)`.

| Mode | Arti |
|---|---|
| `"baco"` (bawaan) | membaca |
| `"tulis"` | menulis dari awal (isi lama hilang) |
| `"nambahkah"` | menulis di ujung (isi lama tetap) |

```krc
barang f = bukak("log.txt", "tulis")
tulis(f, "baris 1\n")
tulis(f, "baris 2\n")
tutup(f)

barang g = bukak("log.txt", "nambahkah")
tulis(g, "baris 3\n")
tutup(g)

nyetak baco("log.txt")
```

```hasil
baris 1
baris 2
baris 3
```

Biasakan menutup berkas dengan `tutup`, terutama sebelum membacanya kembali. (Berkas yang lupa ditutup akan ditutup otomatis saat program berakhir.)

## Membaca baris demi baris

`untuk ... alem` pada berkas yang dibuka memberikan satu baris sekali jalan, tanpa tanda baris barunya.

```krc
tulis("data.txt", "satu\ndua\ntiga\n")
barang nomor = 1
untuk baris alem bukak("data.txt") {
    nyetak nomor + ". " + baris
    nomor = nomor + 1
}
```

```hasil
1. satu
2. dua
3. tiga
```

## Menyimpan dan memuat daftar

Gabungkan dengan `disatu` dan `pisah` dari Pelajaran 10:

```krc
barang buah = ["pisang", "apel", "jeruk"]
tulis("buah.txt", disatu(buah, "\n"))

barang dibaca = pisah(baco("buah.txt"), "\n")
nyetak dibaca
nyetak panjang(dibaca)
```

```hasil
["pisang", "apel", "jeruk"]
3
```

Hati-hati: kalau teks berakhir dengan `\n`, `pisah(teks, "\n")` menghasilkan satu anggota kosong di ujung. Untuk berkas yang berakhir dengan baris baru, lebih aman memakai `untuk baris alem bukak(...)`.

## Menghapus berkas

```krc
tulis("sementara.txt", "x")
hapus("sementara.txt")
nyetak "Terhapus"
```

```hasil
Terhapus
```

`hapus` hanya menghapus berkas, bukan folder.

## Kalau berkasnya tidak ada

```krc-error
nyetak baco("tidak-ada.txt")
```

```hasil
Kesalahan: Berkas tidak ditemukan: tidak-ada.txt
```

Di Pelajaran 12 kamu akan belajar menangani kesalahan ini sehingga program tidak berhenti.

## Hal-hal penting

- Berkas adalah teks UTF-8.
- Nama berkas relatif terhadap folder tempat program dijalankan. Di Windows, tulis pemisah folder sebagai `/` (`"data/nilai.txt"`) atau ganda (`"data\\nilai.txt"`).
- `tulis(berkas, nilai)` menulis bilangan dan daftar juga, dengan tampilan seperti `nyetak`.
- Berkas hanya bisa dipakai selama terbuka. Memakai berkas yang sudah ditutup adalah kesalahan.

## Ringkasan

- `tulis(nama, teks)` dan `baco(nama)` untuk cara cepat.
- `bukak(nama, mode)` dengan mode `"baco"`, `"tulis"`, `"nambahkah"`, lalu `tutup`.
- `untuk baris alem bukak(nama)` untuk membaca per baris.
- `hapus(nama)` menghapus berkas.

## Latihan

1. Tulis tiga nama ke berkas, satu per baris, lalu baca dan cetak.
2. Hitung jumlah baris dalam sebuah berkas.
3. Tambahkan bilangan 1 sampai 5 ke berkas, satu per baris, memakai perulangan, lalu cetak isinya.

Jawaban: [jawaban.md](jawaban.md#pelajaran-11). Lanjut ke [Pelajaran 12](12-kesalahan.md).
