# Pelajaran 2: Barang, tempat menyimpan nilai

Program sering perlu mengingat sesuatu. Untuk itu kita membuat **barang** (variabel): wadah bernama yang berisi nilai.

```krc
# dialek: koto-payang
netakka_variabel umur = 20
nytak umur
```

```hasil
20
```

Kata `netakka_variabel` membuat wadah baru bernama `umur` dan mengisinya dengan `20`.

## Mengubah isi

Setelah dibuat, isi barang boleh diganti. Tulis namanya saja, tanpa `netakka_variabel`.

```krc
# dialek: koto-payang
netakka_variabel umur = 20
umur = 21
nytak umur
umur = umur + 1
nytak umur
```

```hasil
21
22
```

Baris `umur = umur + 1` artinya: ambil isi `umur`, tambah 1, simpan lagi ke `umur`.

## Barang yang tidak berubah: `netakka_konstanta`

Kalau nilainya tidak boleh berubah, pakai `netakka_konstanta`.

```krc
# dialek: koto-payang
netakka_konstanta pi = 3.14
nytak pi
```

```hasil
3.14
```

Mengubahnya akan menimbulkan kesalahan:

```krc-error
# dialek: koto-payang
netakka_konstanta pi = 3.14
pi = 3
```

```hasil
Kesalahan: 'pi' adalah konstanta ('netakka_konstanta') nga dak bisa diubuah
```

## Aturan nama

- Boleh berisi huruf, angka, dan `_`, tetapi tidak boleh diawali angka.
- Huruf besar dan kecil dianggap beda: `Umur` dan `umur` adalah dua barang.
- Nama tidak boleh sama dengan kata khusus seperti `kalu` atau `selamu`.
- Pilih nama yang menjelaskan isinya: `umur_budi` lebih jelas daripada `x`.

Barang harus dibuat dulu sebelum dipakai:

```krc-error
# dialek: koto-payang
nytak jumlah
```

```hasil
Kesalahan: namu lao dijeloehka: jumlah
```

## Jenis nilai

Setiap nilai punya jenis. Fungsi `tipe` memberi tahu jenisnya.

| Contoh | Jenis | Artinya |
|---|---|---|
| `42` | `bilangan_buluak` | bilangan bulat |
| `3.5` | `bilangan_bakoma` | bilangan desimal |
| `"halo"` | `tulisan` | teks |
| `[1, 2]` | `daftar` | kumpulan berurutan (Pelajaran 7) |
| `{"a": 1}` | `kamus` | kumpulan berpasangan (Pelajaran 9) |
| `betiu`, `salah` | `betiu_salah` | benar atau salah |
| `kusao` | `kusao` | tidak ada nilai |

```krc
# dialek: koto-payang
nytak tipe(42)
nytak tipe(3.5)
nytak tipe("halo")
nytak tipe([1, 2])
nytak tipe({"a": 1})
nytak tipe(betiu)
nytak tipe(kusao)
```

```hasil
bilangan_buluak
bilangan_bakoma
tulisan
daftar
kamus
betiu_salah
kusao
```

`betiu` dan `salah` adalah nilai benar dan salah. `kusao` berarti "tidak ada isinya".

> Catatan: nama jenis untuk `betiu` dan `salah` saat ini masih `betiu_salah`, kata sementara dari bahasa Inggris, sampai penutur Kerinci menyumbangkan kata yang tepat.

## Ringkasan

- `netakka_variabel nama = nilai` membuat barang; `nama = nilai` mengubahnya.
- `netakka_konstanta` untuk nilai yang tidak boleh berubah.
- `tipe(x)` menyebut jenis nilai.

## Latihan

1. Buat barang `nama` dan `kota`, lalu cetak keduanya.
2. Buat barang `saldo` bernilai 100, tambah 50, lalu cetak.
3. Apa jenis nilai `"42"` dan `42`? Buktikan dengan `tipe`.

Jawaban: [jawaban.md](jawaban.md#pelajaran-2). Lanjut ke [Pelajaran 3](03-berhitung.md).

---
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: approved).*
