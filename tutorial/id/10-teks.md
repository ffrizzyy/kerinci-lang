# Pelajaran 10: Mengolah teks

Teks mirip daftar huruf. Banyak alat daftar bekerja juga pada teks.

## Huruf demi huruf

```krc
barang kata = "kerinci"
nyetak kata[0]
nyetak kata[panjang(kata) - 1]
nyetak panjang(kata)
nyetak pulang(kata)
nyetak isi(kata, "rin")
nyetak isi(kata, "xyz")
```

```hasil
k
i
7
icnirek
betul
salah
```

Teks tidak bisa diubah per huruf. Buat teks baru sebagai gantinya:

```krc-error
barang kata = "abc"
kata[0] = "x"
```

```hasil
Kesalahan: Teks tidak bisa diubah per huruf
```

## `pisah`: memecah teks

`pisah(teks, pemisah)` memecah teks menjadi daftar.

```krc
nyetak pisah("a,b,c", ",")
nyetak pisah("a,,b", ",")
nyetak pisah("a--b--c", "--")
nyetak pisah("abc", "")
```

```hasil
["a", "b", "c"]
["a", "", "b"]
["a", "b", "c"]
["a", "b", "c"]
```

Tanpa pemisah, `pisah` memecah di spasi dan membuang bagian kosong, sangat cocok untuk memecah kalimat menjadi kata.

```krc
nyetak pisah("belajar   bahasa kerinci")
```

```hasil
["belajar", "bahasa", "kerinci"]
```

## `disatu`: menyatukan daftar

`disatu(daftar, pemisah)` adalah kebalikan `pisah`: ia menyambung anggota daftar menjadi satu teks.

```krc
nyetak disatu(["a", "b", "c"], "-")
nyetak disatu([1, 2, 3], ", ")
nyetak disatu(["a", "b"])
nyetak disatu(pisah("a b c"), "_")
```

```hasil
a-b-c
1, 2, 3
ab
a_b_c
```

## Contoh: memanipulasi kalimat

```krc
barang kalimat = "belajar bahasa pemrograman kerinci"
barang kata_kata = pisah(kalimat)

nyetak "Jumlah kata: " + panjang(kata_kata)
nyetak "Terbalik: " + disatu(pulang(kata_kata), " ")
nyetak "Terurut: " + disatu(milih(kata_kata), ", ")
```

```hasil
Jumlah kata: 4
Terbalik: kerinci pemrograman bahasa belajar
Terurut: bahasa, belajar, kerinci, pemrograman
```

## Contoh: menghitung huruf hidup

```krc
barang vokal = "aiueo"
barang jumlah = 0
untuk huruf alem "pemrograman kerinci" {
    kalu isi(vokal, huruf) {
        jumlah = jumlah + 1
    }
}
nyetak "Jumlah huruf hidup: " + jumlah
```

```hasil
Jumlah huruf hidup: 7
```

## Contoh: palindrom

Palindrom dibaca sama dari depan maupun belakang.

```krc
guno palindrom(kata) {
    balik kata samo pulang(kata)
}

nyetak palindrom("katak")
nyetak palindrom("kerinci")
```

```hasil
betul
salah
```

## Contoh: data dipisah tanda baca

```krc
barang data = "Budi,80;Sari,92;Dewi,65"
barang nilai = {}
untuk pasangan alem pisah(data, ";") {
    barang bagian = pisah(pasangan, ",")
    nilai[bagian[0]] = bilangan(bagian[1])
}
nyetak nilai
```

```hasil
{"Budi": 80, "Sari": 92, "Dewi": 65}
```

## Ringkasan

- Teks bisa diindeks (`t[0]`), diukur (`panjang`), dibalik (`pulang`), dan dicari (`isi`).
- `pisah` memecah teks menjadi daftar; `disatu` menyatukan daftar menjadi teks.
- Teks tidak bisa diubah per huruf.

## Latihan

1. Hitung jumlah kata dalam "saya belajar bahasa kerinci hari ini".
2. Buat fungsi `kabar_palindrom(kata)` yang mencetak "palindrom" atau "bukan" untuk "malam" dan "kerinci".
3. Ubah "a,b,c" menjadi "a-b-c".

Jawaban: [jawaban.md](jawaban.md#pelajaran-10). Lanjut ke [Pelajaran 11](11-berkas.md).
