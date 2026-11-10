# Pelajaran 11: Berkas

Sejauh ini, semua yang diingat programmu hilang saat program selesai. Dengan **berkas**, program bisa menyimpan data di disk dan membacanya lagi nanti.

## Cara tercepat: `tulaih` dan `bacea`

```krc
# dialek: koto-payang
tulaih("catatan.txt", "Belajar KerinciLang\nHari ini membuat program\n")
nytak bacea("catatan.txt")
```

```hasil
Belajar KerinciLang
Hari ini membuat program
```

- `tulaih(nama, teks)` membuat berkas, atau **mengganti seluruh isinya** kalau sudah ada.
- `bacea(nama)` membaca seluruh isi berkas sebagai satu teks.

## Membuka berkas: `bukuak`, `tutamp`

Untuk menulis sedikit-sedikit atau menambah di ujung, buka berkasnya dulu dengan `bukuak(nama, mode)`. Selesai? `tutamp(berkas)`.

| Mode | Arti |
|---|---|
| `"baco"` (bawaan) | membaca |
| `"tulis"` | menulis dari awal (isi lama hilang) |
| `"nambahkah"` | menulis di ujung (isi lama tetap) |

```krc
# dialek: koto-payang
netakka_variabel f = bukuak("log.txt", "tulaih")
tulaih(f, "baris 1\n")
tulaih(f, "baris 2\n")
tutamp(f)

netakka_variabel g = bukuak("log.txt", "tambah")
tulaih(g, "baris 3\n")
tutamp(g)

nytak bacea("log.txt")
```

```hasil
baris 1
baris 2
baris 3
```

Biasakan menutup berkas dengan `tutamp`, terutama sebelum membacanya kembali. (Berkas yang lupa ditutup akan ditutup otomatis saat program berakhir.)

## Membaca baris demi baris

`ndik ... daling` pada berkas yang dibuka memberikan satu baris sekali jalan, tanpa tanda baris barunya.

```krc
# dialek: koto-payang
tulaih("data.txt", "satu\ndua\ntiga\n")
netakka_variabel nomor = 1
ndik baris daling bukuak("data.txt") {
    nytak nomor + ". " + baris
    nomor = nomor + 1
}
```

```hasil
1. satu
2. dua
3. tiga
```

## Menyimpan dan memuat daftar

Gabungkan dengan `basatau` dan `pecah` dari Pelajaran 10:

```krc
# dialek: koto-payang
netakka_variabel buah = ["pisang", "apel", "jeruk"]
tulaih("buah.txt", basatau(buah, "\n"))

netakka_variabel dibaca = pecah(bacea("buah.txt"), "\n")
nytak dibaca
nytak panja(dibaca)
```

```hasil
["pisang", "apel", "jeruk"]
3
```

Hati-hati: kalau teks berakhir dengan `\n`, `pecah(teks, "\n")` menghasilkan satu anggota kosong di ujung. Untuk berkas yang berakhir dengan baris baru, lebih aman memakai `ndik baris daling bukuak(...)`.

## Menghapus berkas

```krc
# dialek: koto-payang
tulaih("sementara.txt", "x")
ngapih_berkas("sementara.txt")
nytak "Terhapus"
```

```hasil
Terhapus
```

`ngapih_berkas` hanya menghapus berkas, bukan folder.

## Kalau berkasnya tidak ada

```krc-error
# dialek: koto-payang
nytak bacea("tidak-ada.txt")
```

```hasil
Kesalahan: Sidiak besuao berkas: tidak-ada.txt
```

Di Pelajaran 12 kamu akan belajar menangani kesalahan ini sehingga program tidak berhenti.

## Hal-hal penting

- Berkas adalah teks UTF-8.
- Nama berkas relatif terhadap folder tempat program dijalankan. Di Windows, tulis pemisah folder sebagai `/` (`"data/nilai.txt"`) atau ganda (`"data\\nilai.txt"`).
- `tulaih(berkas, nilai)` menulis bilangan dan daftar juga, dengan tampilan seperti `nytak`.
- Berkas hanya bisa dipakai selama terbuka. Memakai berkas yang sudah ditutup adalah kesalahan.

## Ringkasan

- `tulaih(nama, teks)` dan `bacea(nama)` untuk cara cepat.
- `bukuak(nama, mode)` dengan mode `"baco"`, `"tulis"`, `"nambahkah"`, lalu `tutamp`.
- `ndik baris daling bukuak(nama)` untuk membaca per baris.
- `ngapih_berkas(nama)` menghapus berkas.

## Latihan

1. Tulis tiga nama ke berkas, satu per baris, lalu baca dan cetak.
2. Hitung jumlah baris dalam sebuah berkas.
3. Tambahkan bilangan 1 sampai 5 ke berkas, satu per baris, memakai perulangan, lalu cetak isinya.

Jawaban: [jawaban.md](jawaban.md#pelajaran-11). Lanjut ke [Pelajaran 12](12-kesalahan.md).

---
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: approved).*
