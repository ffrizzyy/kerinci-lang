# Tutorial KerinciLang (bahasa Indonesia)

*The main tutorial is in English: [../README.md](../README.md). This folder is the same course in Indonesian.*

Belajar memprogram dengan kata-kata bahasa Kerinci. Tutorial ini ditulis dalam bahasa Indonesia; semua kode memakai kata Kerinci dialek Siulak.

**Edisi Koto Payang:** pelajaran yang sama dibuat dengan kode Koto Payang di `tutorial/en/koto-payang/` dan `tutorial/id/koto-payang/`. Koto Payang sudah `approved` dan memiliki semua ID, jadi setiap indeks hasil bangun memakai kata dialek itu sendiri tanpa kata dasar pinjaman.

## Daftar pelajaran

| # | Pelajaran | Kata baru |
|---|---|---|
| 0 | [Persiapan](00-persiapan.md) | cara menjalankan program |
| 1 | [Halo, dunia](01-halo-dunia.md) | `nyetak`, `#` |
| 2 | [Barang](02-barang.md) | `barang`, `tetap`, `mecem` |
| 3 | [Berhitung dan menyambung teks](03-berhitung.md) | `+ - * / %`, `panjang`, `tambah`, `kurang`, `kali`, `bagi` |
| 4 | [Bertanya kepada pengguna](04-bertanya.md) | `tanyo`, `bilangan`, `pecahan`, `kato` |
| 5 | [Mengambil keputusan](05-keputusan.md) | `kalu`, `lain`, `samo`, `ngan`, `apo`, `idak`, `betul`, `salah` |
| 6 | [Mengulang](06-perulangan.md) | `selamo`, `untuk`, `alem`, `jarak`, `putuh`, `lanjut` |
| 7 | [Daftar](07-daftar.md) | `nambahkah`, `isi`, `milih`, `pulang` |
| 8 | [Guno: fungsi](08-guno.md) | `guno`, `balik` |
| 9 | [Peta dan pilih](09-peta-dan-pilih.md) | `peta`, `pilih` |
| 10 | [Mengolah teks](10-teks.md) | `pisah`, `disatu` |
| 11 | [Berkas](11-berkas.md) | `bukak`, `baco`, `tulis`, `tutup`, `hapus` |
| 12 | [Menangani kesalahan](12-kesalahan.md) | `cubo`, `tangkap`, `ngangkat` |
| 13 | [Proyek buku nilai](13-proyek.md) | `ambik`, semua yang dipelajari |

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
| ` ```krc masukan=a\|b ` | sama, dengan `a` dan `b` diketik untuk `tanyo()` |
| ` ```krc-error ` | program yang harus gagal; pesannya ditulis di blok `hasil` |
| ` ```krc-berkas nama.krc ` | berkas pendukung (tidak dijalankan) yang dipakai blok berikutnya |
| ` ```hasil ` | hasil yang diharapkan dari blok di atasnya (diisi otomatis oleh `--tulis`) |

## Versi bahasa Kerinci

Teks tutorial dalam bahasa Kerinci sebaiknya ditulis oleh penutur. Petunjuknya ada di [kerinci/README.md](../kerinci/README.md).
