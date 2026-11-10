# Pelajaran 10: Mengolah teks

Teks mirip daftar huruf. Banyak alat daftar bekerja juga pada teks.

## Huruf demi huruf

```krc
# dialek: koto-payang
netakka_variabel kata = "kerinci"
nytak kata[0]
nytak kata[panja(kata) - 1]
nytak panja(kata)
nytak tebaluik(kata)
nytak meriksu(kata, "rin")
nytak meriksu(kata, "xyz")
```

```hasil
k
i
7
icnirek
betiu
salah
```

Teks tidak bisa diubah per huruf. Buat teks baru sebagai gantinya:

```krc-error
# dialek: koto-payang
netakka_variabel kata = "abc"
kata[0] = "x"
```

```hasil
Kesalahan: Tulisan nyendak diubuah per huruf
```

## `pecah`: memecah teks

`pecah(teks, pemisah)` memecah teks menjadi daftar.

```krc
# dialek: koto-payang
nytak pecah("a,b,c", ",")
nytak pecah("a,,b", ",")
nytak pecah("a--b--c", "--")
nytak pecah("abc", "")
```

```hasil
["a", "b", "c"]
["a", "", "b"]
["a", "b", "c"]
["a", "b", "c"]
```

Tanpa pemisah, `pecah` memecah di spasi dan membuang bagian kosong, sangat cocok untuk memecah kalimat menjadi kata.

```krc
# dialek: koto-payang
nytak pecah("belajar   bahasa kerinci")
```

```hasil
["belajar", "bahasa", "kerinci"]
```

## `basatau`: menyatukan daftar

`basatau(daftar, pemisah)` adalah kebalikan `pecah`: ia menyambung anggota daftar menjadi satu teks.

```krc
# dialek: koto-payang
nytak basatau(["a", "b", "c"], "-")
nytak basatau([1, 2, 3], ", ")
nytak basatau(["a", "b"])
nytak basatau(pecah("a b c"), "_")
```

```hasil
a-b-c
1, 2, 3
ab
a_b_c
```

## Contoh: memanipulasi kalimat

```krc
# dialek: koto-payang
netakka_variabel kalimat = "belajar bahasa pemrograman kerinci"
netakka_variabel kata_kata = pecah(kalimat)

nytak "Jumlah kata: " + panja(kata_kata)
nytak "Terbalik: " + basatau(tebaluik(kata_kata), " ")
nytak "Terurut: " + basatau(terurut(kata_kata), ", ")
```

```hasil
Jumlah kata: 4
Terbalik: kerinci pemrograman bahasa belajar
Terurut: bahasa, belajar, kerinci, pemrograman
```

## Contoh: menghitung huruf hidup

```krc
# dialek: koto-payang
netakka_variabel vokal = "aiueo"
netakka_variabel jumlah = 0
ndik huruf daling "pemrograman kerinci" {
    kalu meriksu(vokal, huruf) {
        jumlah = jumlah + 1
    }
}
nytak "Jumlah huruf hidup: " + jumlah
```

```hasil
Jumlah huruf hidup: 7
```

## Contoh: palindrom

Palindrom dibaca sama dari depan maupun belakang.

```krc
# dialek: koto-payang
jeloehka palindrom(kata) {
    baluikka kata samu_dinga tebaluik(kata)
}

nytak palindrom("katak")
nytak palindrom("kerinci")
```

```hasil
betiu
salah
```

## Contoh: data dipisah tanda baca

```krc
# dialek: koto-payang
netakka_variabel data = "Budi,80;Sari,92;Dewi,65"
netakka_variabel nilai = {}
ndik pasangan daling pecah(data, ";") {
    netakka_variabel bagian = pecah(pasangan, ",")
    nilai[bagian[0]] = bilangan_buluak(bagian[1])
}
nytak nilai
```

```hasil
{"Budi": 80, "Sari": 92, "Dewi": 65}
```

## Ringkasan

- Teks bisa diindeks (`t[0]`), diukur (`panja`), dibalik (`tebaluik`), dan dicari (`meriksu`).
- `pecah` memecah teks menjadi daftar; `basatau` menyatukan daftar menjadi teks.
- Teks tidak bisa diubah per huruf.

## Latihan

1. Hitung jumlah kata dalam "saya belajar bahasa kerinci hari ini".
2. Buat fungsi `kabar_palindrom(kata)` yang mencetak "palindrom" atau "bukan" untuk "malam" dan "kerinci".
3. Ubah "a,b,c" menjadi "a-b-c".

Jawaban: [jawaban.md](jawaban.md#pelajaran-10). Lanjut ke [Pelajaran 11](11-berkas.md).

---
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: approved).*
