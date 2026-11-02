# Pelajaran 12: Menangani kesalahan

Program bisa mengalami kesalahan di luar kendali kita: pengguna mengetik "abc" padahal diminta bilangan, berkas hilang, pembagi nol. Tanpa penanganan, program langsung berhenti. Dengan `cubea` dan `kecuali`, kamu bisa menyiapkan rencana cadangan.

## `cubea` dan `kecuali`

`cubea` berarti "coba", dan `kecuali` berarti "tangkap". Isi `cubea { }` dicoba. Kalau ada kesalahan, sisa isinya dilewati dan `kecuali { }` dijalankan. Pesan kesalahan tersimpan dalam barang yang kamu namai.

```krc
# dialek: koto-payang
cubea {
    nytak 10 / 0
    nytak "tidak sampai sini"
} kecuali pesan {
    nytak "Terjadi kesalahan: " + pesan
}
nytak "Program tetap lanjut"
```

```hasil
Terjadi kesalahan: Pembagian dinga nol
Program tetap lanjut
```

Kalau tidak ada kesalahan, `kecuali` dilewati:

```krc
# dialek: koto-payang
cubea {
    nytak "semuanya baik"
} kecuali pesan {
    nytak "tidak akan tercetak"
}
```

```hasil
semuanya baik
```

Nama pesan boleh dihilangkan kalau tidak diperlukan: `kecuali { ... }`. Tetapi `kecuali` wajib ada setelah `cubea`:

```krc-error
# dialek: koto-payang
cubea {
    nytak 1
}
```

```hasil
Kesalahan: Baris 2: blok 'cubea' harus dinga 'kecuali' nga blok penanganan
```

## Meminta ulang masukan yang salah

```krc masukan=abc|dua|25
# dialek: koto-payang
netakka_variabel umur = kusao
selamu umur samu_dinga kusao {
    nytak "Berapa umurmu?"
    cubea {
        umur = bilangan_buluak(masukka())
    } kecuali {
        nytak "Itu bukan bilangan, coba lagi."
    }
}
nytak "Umurmu " + umur
```

```hasil
Berapa umurmu?
Itu bukan bilangan, coba lagi.
Berapa umurmu?
Itu bukan bilangan, coba lagi.
Berapa umurmu?
Umurmu 25
```

## Memberi nilai cadangan

```krc
# dialek: koto-payang
jeloehka ke_bilangan(teks) {
    cubea {
        baluikka bilangan_buluak(teks)
    } kecuali {
        baluikka kusao
    }
}

nytak ke_bilangan("42")
nytak ke_bilangan("abc")
```

```hasil
42
kusao
```

`baluikka`, `slese`, dan `lanjutka` bekerja normal di dalam `cubea`.

## Berkas yang mungkin tidak ada

```krc
# dialek: koto-payang
netakka_variabel isi_berkas = ""
cubea {
    isi_berkas = bacea("tidak-ada.txt")
} kecuali {
    isi_berkas = "(berkas belum ada)"
}
nytak isi_berkas
```

```hasil
(berkas belum ada)
```

## `timbaoka`: membuat kesalahan sendiri

`timbaoka` berarti "angkat" atau memunculkan kesalahan dengan pesan buatanmu. Ini berguna di dalam fungsi untuk menolak nilai yang tidak masuk akal.

```krc
# dialek: koto-payang
jeloehka bagi_aman(a, b) {
    kalu b samu_dinga 0 { timbaoka "pembagi tidak boleh nol" }
    baluikka a / b
}

cubea {
    nytak bagi_aman(10, 2)
    nytak bagi_aman(1, 0)
    nytak "tidak sampai sini"
} kecuali pesan {
    nytak "Gagal: " + pesan
}
```

```hasil
5
Gagal: pembagi tidak boleh nol
```

Kalau tidak ada `kecuali` yang menangkapnya, kesalahan itu menghentikan program, dengan pesanmu sebagai penjelasan:

```krc-error
# dialek: koto-payang
nytak "Mulai"
timbaoka "Aduh, ada yang salah"
nytak "Tidak dicetak"
```

```hasil
Mulai
Kesalahan: Aduh, ada yang salah
```

## Menangkap lalu mengirim ulang

Di dalam `kecuali`, kamu boleh `timbaoka` lagi untuk meneruskan kesalahan ke penangkap yang lebih luar.

```krc
# dialek: koto-payang
cubea {
    cubea {
        timbaoka "kesalahan dalam"
    } kecuali pesan {
        nytak "Ditangkap di dalam: " + pesan
        timbaoka "dikirim ulang: " + pesan
    }
} kecuali pesan {
    nytak "Ditangkap di luar: " + pesan
}
```

```hasil
Ditangkap di dalam: kesalahan dalam
Ditangkap di luar: dikirim ulang: kesalahan dalam
```

## Yang bisa dan tidak bisa ditangkap

- Bisa ditangkap: semua kesalahan saat program berjalan (pembagian nol, berkas tidak ada, kunci peta tidak ada, ubah jenis gagal, `timbaoka`, rekursi terlalu dalam).
- Tidak bisa: kesalahan penulisan (misalnya kurung yang tidak ditutup), karena program tidak pernah mulai berjalan.

## Ringkasan

- `cubea { ... } kecuali pesan { ... }` mencoba lalu menangkap.
- `timbaoka "pesan"` memunculkan kesalahan.
- Isi `kecuali` boleh `timbaoka` lagi.

## Latihan

1. Bagi dua bilangan dan cetak "tidak bisa dibagi nol" bila pembaginya 0.
2. Buat fungsi `periksa_umur(umur)` yang mengangkat kesalahan bila umur negatif.
3. Baca berkas yang mungkin tidak ada dan cetak "kosong" bila tidak ada.

Jawaban: [jawaban.md](jawaban.md#pelajaran-12). Lanjut ke [Pelajaran 13](13-proyek.md).

---
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: review).*
