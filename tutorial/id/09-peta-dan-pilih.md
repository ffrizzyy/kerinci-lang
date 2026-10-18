# Pelajaran 9: Peta dan pilih

## Peta: pasangan kunci dan nilai

**Peta** menyimpan pasangan: tiap nilai punya **kunci** (nama) untuk mencarinya. Kalau daftar dicari dengan nomor, peta dicari dengan nama.

```krc
barang siswa = {"Budi": 80, "Sari": 92}
nyetak siswa
nyetak siswa["Sari"]
```

```hasil
{"Budi": 80, "Sari": 92}
92
```

## Mengubah dan menambah

Menulis ke kunci yang sudah ada mengganti nilainya; kunci baru ditambahkan.

```krc
barang siswa = {"Budi": 80}
siswa["Budi"] = 85
siswa["Dewi"] = 65
nyetak siswa
nyetak panjang(siswa)
```

```hasil
{"Budi": 85, "Dewi": 65}
2
```

Kunci boleh berupa teks atau bilangan bulat. Nilainya boleh apa saja, bahkan daftar atau peta lain.

## Memeriksa kunci

Mengambil kunci yang tidak ada adalah kesalahan, jadi periksa dulu dengan `isi`.

```krc-error
barang siswa = {"Budi": 80}
nyetak siswa["Andi"]
```

```hasil
Kesalahan: Kunci tidak ditemukan: "Andi"
```

```krc
barang siswa = {"Budi": 80}
kalu isi(siswa, "Andi") {
    nyetak siswa["Andi"]
} lain {
    nyetak "Andi tidak ada"
}
```

```hasil
Andi tidak ada
```

## Melihat semua isi

`untuk` pada peta memberikan **kunci**, berurutan sesuai penulisan.

```krc
barang siswa = {"Budi": 80, "Sari": 92, "Dewi": 65}
untuk nama alem siswa {
    nyetak nama + ": " + siswa[nama]
}
```

```hasil
Budi: 80
Sari: 92
Dewi: 65
```

## Contoh: menghitung kata

```krc
barang kalimat = "kalu kalu lain kalu lain"
barang jumlah = {}
untuk kata alem pisah(kalimat) {
    kalu isi(jumlah, kata) {
        jumlah[kata] = jumlah[kata] + 1
    } lain {
        jumlah[kata] = 1
    }
}
nyetak jumlah
```

```hasil
{"kalu": 3, "lain": 2}
```

## Peta di dalam peta

```krc
barang murid = {
    "nama": "Budi",
    "nilai": [80, 90],
    "alamat": {"kota": "Sungai Penuh"}
}
nambahkah(murid["nilai"], 100)
nyetak murid
nyetak murid["alamat"]["kota"]
```

```hasil
{"nama": "Budi", "nilai": [80, 90, 100], "alamat": {"kota": "Sungai Penuh"}}
Sungai Penuh
```

## `pilih`: memilih satu dari banyak

Bila satu nilai dibandingkan dengan banyak kemungkinan, `pilih` lebih rapi daripada `lain kalu` berderet.

```krc
barang hari = 3
pilih hari {
    kalu 1 { nyetak "Senin" }
    kalu 2 { nyetak "Selasa" }
    kalu 3 { nyetak "Rabu" }
    lain { nyetak "Hari lain" }
}
```

```hasil
Rabu
```

Satu `kalu` boleh memuat beberapa nilai, dipisahkan koma:

```krc
barang hari = "minggu"
pilih hari {
    kalu "sabtu", "minggu" { nyetak "libur" }
    lain { nyetak "kerja" }
}
```

```hasil
libur
```

`pilih` menjalankan **hanya satu** cabang yang cocok (cabang pertama), lalu selesai. `lain` untuk keadaan kalau tidak ada yang cocok, dan boleh dihilangkan.

## Ringkasan

- `{"kunci": nilai}` membuat peta; `p["kunci"]` mengambil; `p["kunci"] = x` mengubah atau menambah.
- `isi(p, kunci)` memeriksa kunci; `untuk k alem p` melintasi kunci.
- `pilih x { kalu a { } kalu b, c { } lain { } }` memilih satu cabang.

## Latihan

1. Buat peta `harga` untuk tiga barang dan cetak total harganya.
2. Buat fungsi `nama_bulan(n)` dengan `pilih` untuk bulan 1 sampai 3 (dan "tidak dikenal" untuk lainnya).
3. Hitung berapa kali tiap huruf muncul di kata "kerinci".

Jawaban: [jawaban.md](jawaban.md#pelajaran-9). Lanjut ke [Pelajaran 10](10-teks.md).
