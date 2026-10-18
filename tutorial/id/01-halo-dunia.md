# Pelajaran 1: Halo, dunia

Program pertama hampir selalu menampilkan sapaan. Di KerinciLang, kata untuk "cetak" adalah `nyetak`.

```krc
nyetak "Halo, dunia"
```

```hasil
Halo, dunia
```

Teks ditulis di antara tanda kutip ganda `"`. Angka ditulis tanpa tanda kutip.

## Beberapa baris

Setiap `nyetak` menulis satu baris. Program berjalan dari atas ke bawah.

```krc
nyetak "Halo, dunia"
nyetak "Saya belajar KerinciLang"
nyetak 2026
```

```hasil
Halo, dunia
Saya belajar KerinciLang
2026
```

## Komentar

Tanda `#` membuat sisa baris menjadi komentar. Komputer mengabaikannya; komentar adalah catatan untuk manusia.

```krc
# ini komentar, tidak dijalankan
nyetak "Halo"   # komentar boleh juga di akhir baris
```

```hasil
Halo
```

## Karakter khusus dalam teks

Di dalam teks, tanda `\` punya arti khusus:

| Tulis | Hasil |
|---|---|
| `\n` | pindah ke baris baru |
| `\t` | tab (jarak lebar) |
| `\"` | tanda kutip |
| `\\` | satu tanda `\` |

```krc
nyetak "baris satu\nbaris dua"
nyetak "nama\tumur"
nyetak "dia berkata \"halo\""
nyetak "C:\\folder\\berkas.txt"
```

```hasil
baris satu
baris dua
nama	umur
dia berkata "halo"
C:\folder\berkas.txt
```

## Kesalahan pertama

Semua orang membuat kesalahan. Pesan kesalahan memberi tahu apa yang perlu diperbaiki. Di sini tanda kutip penutup lupa ditulis:

```krc-error
nyetak "Halo
```

```hasil
Kesalahan: Baris 1: karakter tidak dikenal '"'
```

Dan di sini `nyetak` tidak diberi apa pun untuk dicetak:

```krc-error
nyetak
```

```hasil
Kesalahan: Baris 2: tidak terduga ''
```

## Ringkasan

- `nyetak` menampilkan nilai.
- Teks memakai tanda kutip ganda; angka tidak.
- `#` membuat komentar.
- `\n` membuat baris baru dalam teks.

## Latihan

1. Cetak namamu.
2. Cetak tiga baris puisi pendek dengan satu `nyetak` saja (petunjuk: `\n`).
3. Cetak kalimat yang memuat tanda kutip, misalnya: Dia berkata "selamat pagi".

Jawaban: [jawaban.md](jawaban.md#pelajaran-1). Lanjut ke [Pelajaran 2](02-barang.md).
