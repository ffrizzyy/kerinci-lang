# Pelajaran 9: Peta dan pilih

## Peta: pasangan kunci dan nilai

**Peta** menyimpan pasangan: tiap nilai punya **kunci** (nama) untuk mencarinya. Kalau daftar dicari dengan nomor, peta dicari dengan nama.

```krc
# dialek: koto-payang
netakka_variabel siswa = {"Budi": 80, "Sari": 92}
nytak siswa
nytak siswa["Sari"]
```

```hasil
{"Budi": 80, "Sari": 92}
92
```

## Mengubah dan menambah

Menulis ke kunci yang sudah ada mengganti nilainya; kunci baru ditambahkan.

```krc
# dialek: koto-payang
netakka_variabel siswa = {"Budi": 80}
siswa["Budi"] = 85
siswa["Dewi"] = 65
nytak siswa
nytak panja(siswa)
```

```hasil
{"Budi": 85, "Dewi": 65}
2
```

Kunci boleh berupa teks atau bilangan bulat. Nilainya boleh apa saja, bahkan daftar atau peta lain.

## Memeriksa kunci

Mengambil kunci yang tidak ada adalah kesalahan, jadi periksa dulu dengan `meriksu`.

```krc-error
# dialek: koto-payang
netakka_variabel siswa = {"Budi": 80}
nytak siswa["Andi"]
```

```hasil
Kesalahan: sidiak besuao kuncai: "Andi"
```

```krc
# dialek: koto-payang
netakka_variabel siswa = {"Budi": 80}
kalu meriksu(siswa, "Andi") {
    nytak siswa["Andi"]
} nga_laen {
    nytak "Andi tidak ada"
}
```

```hasil
Andi tidak ada
```

## Melihat semua isi

`ndik` pada peta memberikan **kunci**, berurutan sesuai penulisan.

```krc
# dialek: koto-payang
netakka_variabel siswa = {"Budi": 80, "Sari": 92, "Dewi": 65}
ndik nama daling siswa {
    nytak nama + ": " + siswa[nama]
}
```

```hasil
Budi: 80
Sari: 92
Dewi: 65
```

## Contoh: menghitung kata

```krc
# dialek: koto-payang
netakka_variabel kalimat = "kalu kalu lain kalu lain"
netakka_variabel jumlah = {}
ndik kata daling pecah(kalimat) {
    kalu meriksu(jumlah, kata) {
        jumlah[kata] = jumlah[kata] + 1
    } nga_laen {
        jumlah[kata] = 1
    }
}
nytak jumlah
```

```hasil
{"kalu": 3, "lain": 2}
```

## Peta di dalam peta

```krc
# dialek: koto-payang
netakka_variabel murid = {
    "nama": "Budi",
    "nilai": [80, 90],
    "alamat": {"kota": "Sungai Penuh"}
}
tambahka(murid["nilai"], 100)
nytak murid
nytak murid["alamat"]["kota"]
```

```hasil
{"nama": "Budi", "nilai": [80, 90, 100], "alamat": {"kota": "Sungai Penuh"}}
Sungai Penuh
```

## `cocokka`: memilih satu dari banyak

Bila satu nilai dibandingkan dengan banyak kemungkinan, `cocokka` lebih rapi daripada `nga_laen kalu` berderet.

```krc
# dialek: koto-payang
netakka_variabel hari = 3
cocokka hari {
    kalu 1 { nytak "Senin" }
    kalu 2 { nytak "Selasa" }
    kalu 3 { nytak "Rabu" }
    nga_laen { nytak "Hari lain" }
}
```

```hasil
Rabu
```

Satu `kalu` boleh memuat beberapa nilai, dipisahkan koma:

```krc
# dialek: koto-payang
netakka_variabel hari = "minggu"
cocokka hari {
    kalu "sabtu", "minggu" { nytak "libur" }
    nga_laen { nytak "kerja" }
}
```

```hasil
libur
```

`cocokka` menjalankan **hanya satu** cabang yang cocok (cabang pertama), lalu selesai. `nga_laen` untuk keadaan kalau tidak ada yang cocok, dan boleh dihilangkan.

## Ringkasan

- `{"kunci": nilai}` membuat peta; `p["kunci"]` mengambil; `p["kunci"] = x` mengubah atau menambah.
- `meriksu(p, kunci)` memeriksa kunci; `ndik k daling p` melintasi kunci.
- `cocokka x { kalu a { } kalu b, c { } nga_laen { } }` memilih satu cabang.

## Latihan

1. Buat peta `harga` untuk tiga barang dan cetak total harganya.
2. Buat fungsi `nama_bulan(n)` dengan `cocokka` untuk bulan 1 sampai 3 (dan "tidak dikenal" untuk lainnya).
3. Hitung berapa kali tiap huruf muncul di kata "kerinci".

Jawaban: [jawaban.md](jawaban.md#pelajaran-9). Lanjut ke [Pelajaran 10](10-teks.md).

---
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: approved).*
