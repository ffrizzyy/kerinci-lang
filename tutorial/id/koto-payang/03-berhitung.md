# Pelajaran 3: Berhitung dan menyambung teks

## Operator hitung

| Operator | Arti | Contoh | Hasil |
|---|---|---|---|
| `+` | tambah | `7 + 3` | `10` |
| `-` | kurang | `7 - 3` | `4` |
| `*` | kali | `7 * 3` | `21` |
| `/` | bagi | `7 / 2` | `3.5` |
| `%` | sisa bagi | `7 % 3` | `1` |

```krc
# dialek: koto-payang
nytak 7 + 3
nytak 7 - 3
nytak 7 * 3
nytak 7 / 2
nytak 7 % 3
nytak 8 / 2
```

```hasil
10
4
21
3.5
1
4
```

Pembagian yang habis dibagi menghasilkan bilangan bulat (`8 / 2` adalah `4`). Kalau tidak habis, hasilnya desimal.

## Urutan perhitungan

Kali, bagi, dan sisa dikerjakan sebelum tambah dan kurang. Kurung `( )` mengubah urutan.

```krc
# dialek: koto-payang
nytak 2 + 3 * 4
nytak (2 + 3) * 4
nytak 10 - 2 - 3
```

```hasil
14
20
5
```

## Menghitung dengan barang

```krc
# dialek: koto-payang
netakka_variabel harga = 15000
netakka_variabel jumlah = 3
netakka_variabel total = harga * jumlah
nytak "Total: " + total
```

```hasil
Total: 45000
```

## Menyambung teks

Tanda `+` juga menyambung teks. Kalau salah satu sisinya teks, sisi lain otomatis diubah jadi teks.

```krc
# dialek: koto-payang
netakka_variabel depan = "Budi"
netakka_variabel belakang = "Santoso"
nytak depan + " " + belakang
nytak "Umur: " + 20
nytak "Benar? " + betiu
```

```hasil
Budi Santoso
Umur: 20
Benar? betiu
```

Hati-hati: urutan penting. Kalau kedua sisinya bilangan, `+` menjumlahkan, bukan menyambung.

```krc
# dialek: koto-payang
nytak 1 + 2 + "a"
nytak "a" + 1 + 2
```

```hasil
3a
a12
```

`panja` menghitung jumlah huruf dalam teks:

```krc
# dialek: koto-payang
nytak panja("kerinci")
```

```hasil
7
```

## Fungsi hitung

Setiap operator punya kata Kerinci sebagai fungsi: `tambah`, `kura`, `kali`, dan `bagi`. Hasilnya sama dengan operator.

```krc
# dialek: koto-payang
nytak tambah(2, 3)
nytak kura(10, 4)
nytak kali(6, 7)
nytak bagi(9, 2)
```

```hasil
5
6
42
4.5
```

## Kesalahan: membagi nol, jenis tidak cocok

```krc-error
# dialek: koto-payang
nytak 10 / 0
```

```hasil
Kesalahan: Pembagian dinga nol
```

```krc-error
# dialek: koto-payang
nytak "a" - 1
```

```hasil
Kesalahan: Operator ''-'' nyendak dipake kik "a" nga 1
```

## Ringkasan

- `+ - * / %` untuk berhitung; kurung mengatur urutan.
- `+` menyambung teks bila salah satu sisinya teks.
- `panja(teks)` menghitung huruf.
- `tambah`, `kura`, `kali`, `bagi` adalah versi fungsi.

## Latihan

1. Hitung luas persegi panjang 12 kali 5 dan cetak: `Luas: 60`.
2. Berapa sisa 100 dibagi 7?
3. Ubah suhu 30 derajat Celsius ke Fahrenheit dengan rumus `C * 9 / 5 + 32`.

Jawaban: [jawaban.md](jawaban.md#pelajaran-3). Lanjut ke [Pelajaran 4](04-bertanya.md).

---
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: approved).*
