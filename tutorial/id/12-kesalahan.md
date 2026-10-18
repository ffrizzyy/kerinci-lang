# Pelajaran 12: Menangani kesalahan

Program bisa mengalami kesalahan di luar kendali kita: pengguna mengetik "abc" padahal diminta bilangan, berkas hilang, pembagi nol. Tanpa penanganan, program langsung berhenti. Dengan `cubo` dan `tangkap`, kamu bisa menyiapkan rencana cadangan.

## `cubo` dan `tangkap`

`cubo` berarti "coba", dan `tangkap` berarti "tangkap". Isi `cubo { }` dicoba. Kalau ada kesalahan, sisa isinya dilewati dan `tangkap { }` dijalankan. Pesan kesalahan tersimpan dalam barang yang kamu namai.

```krc
cubo {
    nyetak 10 / 0
    nyetak "tidak sampai sini"
} tangkap pesan {
    nyetak "Terjadi kesalahan: " + pesan
}
nyetak "Program tetap lanjut"
```

```hasil
Terjadi kesalahan: Pembagian dengan nol
Program tetap lanjut
```

Kalau tidak ada kesalahan, `tangkap` dilewati:

```krc
cubo {
    nyetak "semuanya baik"
} tangkap pesan {
    nyetak "tidak akan tercetak"
}
```

```hasil
semuanya baik
```

Nama pesan boleh dihilangkan kalau tidak diperlukan: `tangkap { ... }`. Tetapi `tangkap` wajib ada setelah `cubo`:

```krc-error
cubo {
    nyetak 1
}
```

```hasil
Kesalahan: Baris 1: blok 'cubo' harus diikuti 'tangkap' dan blok penanganan
```

## Meminta ulang masukan yang salah

```krc masukan=abc|dua|25
barang umur = kosong
selamo umur samo kosong {
    nyetak "Berapa umurmu?"
    cubo {
        umur = bilangan(tanyo())
    } tangkap {
        nyetak "Itu bukan bilangan, coba lagi."
    }
}
nyetak "Umurmu " + umur
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
guno ke_bilangan(teks) {
    cubo {
        balik bilangan(teks)
    } tangkap {
        balik kosong
    }
}

nyetak ke_bilangan("42")
nyetak ke_bilangan("abc")
```

```hasil
42
kosong
```

`balik`, `putuh`, dan `lanjut` bekerja normal di dalam `cubo`.

## Berkas yang mungkin tidak ada

```krc
barang isi_berkas = ""
cubo {
    isi_berkas = baco("tidak-ada.txt")
} tangkap {
    isi_berkas = "(berkas belum ada)"
}
nyetak isi_berkas
```

```hasil
(berkas belum ada)
```

## `ngangkat`: membuat kesalahan sendiri

`ngangkat` berarti "angkat" atau memunculkan kesalahan dengan pesan buatanmu. Ini berguna di dalam fungsi untuk menolak nilai yang tidak masuk akal.

```krc
guno bagi_aman(a, b) {
    kalu b samo 0 { ngangkat "pembagi tidak boleh nol" }
    balik a / b
}

cubo {
    nyetak bagi_aman(10, 2)
    nyetak bagi_aman(1, 0)
    nyetak "tidak sampai sini"
} tangkap pesan {
    nyetak "Gagal: " + pesan
}
```

```hasil
5
Gagal: pembagi tidak boleh nol
```

Kalau tidak ada `tangkap` yang menangkapnya, kesalahan itu menghentikan program, dengan pesanmu sebagai penjelasan:

```krc-error
nyetak "Mulai"
ngangkat "Aduh, ada yang salah"
nyetak "Tidak dicetak"
```

```hasil
Mulai
Kesalahan: Aduh, ada yang salah
```

## Menangkap lalu mengirim ulang

Di dalam `tangkap`, kamu boleh `ngangkat` lagi untuk meneruskan kesalahan ke penangkap yang lebih luar.

```krc
cubo {
    cubo {
        ngangkat "kesalahan dalam"
    } tangkap pesan {
        nyetak "Ditangkap di dalam: " + pesan
        ngangkat "dikirim ulang: " + pesan
    }
} tangkap pesan {
    nyetak "Ditangkap di luar: " + pesan
}
```

```hasil
Ditangkap di dalam: kesalahan dalam
Ditangkap di luar: dikirim ulang: kesalahan dalam
```

## Yang bisa dan tidak bisa ditangkap

- Bisa ditangkap: semua kesalahan saat program berjalan (pembagian nol, berkas tidak ada, kunci peta tidak ada, ubah jenis gagal, `ngangkat`, rekursi terlalu dalam).
- Tidak bisa: kesalahan penulisan (misalnya kurung yang tidak ditutup), karena program tidak pernah mulai berjalan.

## Ringkasan

- `cubo { ... } tangkap pesan { ... }` mencoba lalu menangkap.
- `ngangkat "pesan"` memunculkan kesalahan.
- Isi `tangkap` boleh `ngangkat` lagi.

## Latihan

1. Bagi dua bilangan dan cetak "tidak bisa dibagi nol" bila pembaginya 0.
2. Buat fungsi `periksa_umur(umur)` yang mengangkat kesalahan bila umur negatif.
3. Baca berkas yang mungkin tidak ada dan cetak "kosong" bila tidak ada.

Jawaban: [jawaban.md](jawaban.md#pelajaran-12). Lanjut ke [Pelajaran 13](13-proyek.md).
