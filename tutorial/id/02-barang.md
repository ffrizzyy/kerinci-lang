# Pelajaran 2: Barang, tempat menyimpan nilai

Program sering perlu mengingat sesuatu. Untuk itu kita membuat **barang** (variabel): wadah bernama yang berisi nilai.

```krc
barang umur = 20
nyetak umur
```

```hasil
20
```

Kata `barang` membuat wadah baru bernama `umur` dan mengisinya dengan `20`.

## Mengubah isi

Setelah dibuat, isi barang boleh diganti. Tulis namanya saja, tanpa `barang`.

```krc
barang umur = 20
umur = 21
nyetak umur
umur = umur + 1
nyetak umur
```

```hasil
21
22
```

Baris `umur = umur + 1` artinya: ambil isi `umur`, tambah 1, simpan lagi ke `umur`.

## Barang yang tidak berubah: `tetap`

Kalau nilainya tidak boleh berubah, pakai `tetap`.

```krc
tetap pi = 3.14
nyetak pi
```

```hasil
3.14
```

Mengubahnya akan menimbulkan kesalahan:

```krc-error
tetap pi = 3.14
pi = 3
```

```hasil
Kesalahan: 'pi' adalah konstanta ('tetap') dan tidak bisa diubah
```

## Aturan nama

- Boleh berisi huruf, angka, dan `_`, tetapi tidak boleh diawali angka.
- Huruf besar dan kecil dianggap beda: `Umur` dan `umur` adalah dua barang.
- Nama tidak boleh sama dengan kata khusus seperti `kalu` atau `selamo`.
- Pilih nama yang menjelaskan isinya: `umur_budi` lebih jelas daripada `x`.

Barang harus dibuat dulu sebelum dipakai:

```krc-error
nyetak jumlah
```

```hasil
Kesalahan: Nama belum didefinisikan: jumlah
```

## Jenis nilai

Setiap nilai punya jenis. Fungsi `mecem` memberi tahu jenisnya.

| Contoh | Jenis | Artinya |
|---|---|---|
| `42` | `bilangan` | bilangan bulat |
| `3.5` | `pecahan` | bilangan desimal |
| `"halo"` | `kato` | teks |
| `[1, 2]` | `daftar` | kumpulan berurutan (Pelajaran 7) |
| `{"a": 1}` | `peta` | kumpulan berpasangan (Pelajaran 9) |
| `betul`, `salah` | `boolean` | benar atau salah |
| `kosong` | `kosong` | tidak ada nilai |

```krc
nyetak mecem(42)
nyetak mecem(3.5)
nyetak mecem("halo")
nyetak mecem([1, 2])
nyetak mecem({"a": 1})
nyetak mecem(betul)
nyetak mecem(kosong)
```

```hasil
bilangan
pecahan
kato
daftar
peta
boolean
kosong
```

`betul` dan `salah` adalah nilai benar dan salah. `kosong` berarti "tidak ada isinya".

> Catatan: nama jenis untuk `betul` dan `salah` saat ini masih `boolean`, kata sementara dari bahasa Inggris, sampai penutur Kerinci menyumbangkan kata yang tepat.

## Ringkasan

- `barang nama = nilai` membuat barang; `nama = nilai` mengubahnya.
- `tetap` untuk nilai yang tidak boleh berubah.
- `mecem(x)` menyebut jenis nilai.

## Latihan

1. Buat barang `nama` dan `kota`, lalu cetak keduanya.
2. Buat barang `saldo` bernilai 100, tambah 50, lalu cetak.
3. Apa jenis nilai `"42"` dan `42`? Buktikan dengan `mecem`.

Jawaban: [jawaban.md](jawaban.md#pelajaran-2). Lanjut ke [Pelajaran 3](03-berhitung.md).
