# Tutorial KerinciLang (bahasa Indonesia)

> **Tutorial hasil bangun:** kode dan kode sebaris di bawah memakai Koto Payang (status: review). Teksnya berasal dari pelajaran bahasa Indonesia dialek Siulak.

*The main tutorial is in English: [../README.md](../../en/koto-payang/README.md). This folder is the same course in Indonesian.*

Belajar memprogram dengan kata-kata bahasa Kerinci. Tutorial ini ditulis dalam bahasa Indonesia; semua kode memakai kata Kerinci dialek Koto Payang.

**Edisi Koto Payang:** pelajaran yang sama dibuat dengan kode Koto Payang di `tutorial/en/koto-payang/` dan `tutorial/id/koto-payang/`. Koto Payang masih berstatus `review`; setiap indeks hasil bangun mencantumkan kata dasar yang masih dipinjam (`contains` dan `boolean`). Kata-kata itu bukan pengganti buatan.

## Daftar pelajaran

| # | Pelajaran | Kata baru |
|---|---|---|
| 0 | [Persiapan](00-persiapan.md) | cara menjalankan program |
| 1 | [Halo, dunia](01-halo-dunia.md) | `nytak`, `#` |
| 2 | [Barang](02-barang.md) | `netakka_variabel`, `netakka_konstanta`, `tipe` |
| 3 | [Berhitung dan menyambung teks](03-berhitung.md) | `+ - * / %`, `panja`, `tambah`, `kura`, `kali`, `bagi` |
| 4 | [Bertanya kepada pengguna](04-bertanya.md) | `masukka`, `bilangan_buluak`, `desimal`, `tulisan` |
| 5 | [Mengambil keputusan](05-keputusan.md) | `kalu`, `nga_laen`, `samu_dinga`, `nga`, `atau`, `iduak`, `betiu`, `salah` |
| 6 | [Mengulang](06-perulangan.md) | `selamu`, `ndik`, `daling`, `rentang`, `slese`, `lanjutka` |
| 7 | [Daftar](07-daftar.md) | `tambahka`, `contains`, `terurut`, `tebaluik` |
| 8 | [Guno: fungsi](08-guno.md) | `jeloehka`, `baluikka` |
| 9 | [Peta dan pilih](09-peta-dan-pilih.md) | `kamus`, `cocokka` |
| 10 | [Mengolah teks](10-teks.md) | `pecah`, `basatau` |
| 11 | [Berkas](11-berkas.md) | `bukuak`, `bacea`, `tulaih`, `tutamp`, `ngapih_berkas` |
| 12 | [Menangani kesalahan](12-kesalahan.md) | `cubea`, `kecuali`, `timbaoka` |
| 13 | [Proyek buku nilai](13-proyek.md) | `impor`, semua yang dipelajari |

Pendukung: [jawaban latihan](jawaban.md) dan [glosarium](glosarium.md) (semua kata Kerinci dengan artinya).

## Semua contoh sudah diuji

Setiap contoh kode dalam tutorial dijalankan secara otomatis, dan hasil yang tertulis dibandingkan dengan hasil sebenarnya. Kalau kamu mengubah bahasanya, jalankan:

```bash
python3 tools/sinkron_tutorial.py           # memeriksa semua contoh
python3 tools/sinkron_tutorial.py --tulis   # memperbarui hasil yang tertulis
```

## Menulis contoh baru

Blok kode di tutorial memakai jenis khusus:

| Tulis di awal blok | Artinya |
|---|---|
| ` ```krc ` | program yang harus berjalan tanpa kesalahan |
| ` ```krc masukan=a\|b ` | sama, dengan `a` dan `b` diketik ndik `tanyo()` |
| ` ```krc-error ` | program yang harus gagal; pesannya ditulis di blok `hasil` |
| ` ```krc-berkas nama.krc ` | berkas pendukung (tidak dijalankan) yang dipakai blok berikutnya |
| ` ```hasil ` | hasil yang diharapkan dari blok di atasnya (diisi otomatis oleh `--tulis`) |

## Versi bahasa Kerinci

Teks tutorial dalam bahasa Kerinci sebaiknya ditulis oleh penutur. Petunjuknya ada di [kerinci/README.md](../../kerinci/README.md).

## Kata dasar yang dipakai (review)

Koto Payang belum memiliki kata untuk hal berikut, jadi contoh yang dibangun memakai kata dasar Inggris. Kata ini akan berubah setelah dialek disetujui.

| ID | Kata | Arti |
|---|---|---|
| `fn.contains` | `contains` | Tells whether a list, map, or text holds a value. |
| `type.bool` | `boolean` | Type name returned by the type built-in. |

---
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: review).*
