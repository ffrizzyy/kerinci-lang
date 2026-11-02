# Pelajaran 0: Persiapan

KerinciLang adalah bahasa pemrograman yang kata-katanya diambil dari bahasa Kerinci dialek Koto Payang. Kamu menulis program dengan kata seperti `nytak`, `kalu`, `selamu`, dan `jeloehka`.

Tutorial ini ditulis dalam bahasa Indonesia, sedangkan semua kode dan istilah pemrogramannya memakai bahasa Kerinci. Daftar semua kata ada di [glosarium](glosarium.md).

## Yang kamu perlukan

1. Komputer dengan **Python 3.9 atau lebih baru** (disarankan 3.11 atau lebih baru).
2. Berkas `krc.pyz` (satu berkas, tanpa instalasi) atau proyek KerinciLang lengkap.
3. Aplikasi penyunting teks apa saja (Notepad, VS Code, dan sebagainya). Simpan program dalam berkas berakhiran `.krc`, dengan pengodean UTF-8.

## Cara menjalankan program

Dengan `krc.pyz`:

```bash
python3 krc.pyz halo.krc
```

Atau, kalau sudah memasang dengan `pip install .`:

```bash
krc halo.krc
```

## REPL: mencoba satu baris

Ketik `krc` (atau `python3 krc.pyz`) tanpa nama berkas untuk membuka REPL. Kamu bisa mengetik satu baris dan langsung melihat hasilnya. Tekan `Ctrl+D` untuk keluar.

```text
>>> nyetak 2 + 3
5
>>> barang nama = "Budi"
>>> nyetak "Halo, " + nama
Halo, Budi
```

Untuk mencoba kode pendek tanpa membuat berkas:

```bash
python3 krc.pyz -c 'nyetak "Halo"'
```

## Cara membaca tutorial ini

Setiap contoh kode adalah program lengkap yang bisa kamu salin dan jalankan. Hasilnya ditampilkan di bawahnya. Contoh seperti ini:

```krc
# dialek: koto-payang
nytak "Contoh"
```

```hasil
Contoh
```

Di akhir tiap pelajaran ada latihan. Jawabannya ada di [jawaban](jawaban.md), tetapi cobalah dulu sendiri.

Siap? Lanjut ke [Pelajaran 1](01-halo-dunia.md).

---
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: review).*
