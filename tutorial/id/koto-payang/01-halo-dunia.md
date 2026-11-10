# Pelajaran 1: Halo, dunia

Program pertama hampir selalu menampilkan sapaan. Di KerinciLang, kata untuk "cetak" adalah `nytak`.

```krc
# dialek: koto-payang
nytak "Halo, dunia"
```

```hasil
Halo, dunia
```

Teks ditulis di antara tanda kutip ganda `"`. Angka ditulis tanpa tanda kutip.

## Beberapa baris

Setiap `nytak` menulis satu baris. Program berjalan dari atas ke bawah.

```krc
# dialek: koto-payang
nytak "Halo, dunia"
nytak "Saya belajar KerinciLang"
nytak 2026
```

```hasil
Halo, dunia
Saya belajar KerinciLang
2026
```

## Komentar

Tanda `#` membuat sisa baris menjadi komentar. Komputer mengabaikannya; komentar adalah catatan untuk manusia.

```krc
# dialek: koto-payang
# ini komentar, tidak dijalankan
nytak "Halo"   # komentar boleh juga di akhir baris
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
# dialek: koto-payang
nytak "baris satu\nbaris dua"
nytak "nama\tumur"
nytak "dia berkata \"halo\""
nytak "C:\\folder\\berkas.txt"
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
# dialek: koto-payang
nytak "Halo
```

```hasil
Kesalahan: Baris 2: karakter nga sidiak dikenal '"'
```

Dan di sini `nytak` tidak diberi apa pun untuk dicetak:

```krc-error
# dialek: koto-payang
nytak
```

```hasil
Kesalahan: Baris 3: dak nyengkao ''
```

## Ringkasan

- `nytak` menampilkan nilai.
- Teks memakai tanda kutip ganda; angka tidak.
- `#` membuat komentar.
- `\n` membuat baris baru dalam teks.

## Latihan

1. Cetak namamu.
2. Cetak tiga baris puisi pendek dengan satu `nytak` saja (petunjuk: `\n`).
3. Cetak kalimat yang memuat tanda kutip, misalnya: Dia berkata "selamat pagi".

Jawaban: [jawaban.md](jawaban.md#pelajaran-1). Lanjut ke [Pelajaran 2](02-barang.md).

---
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: approved).*
