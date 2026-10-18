# Jawaban latihan

Cobalah mengerjakan sendiri dulu. Ada banyak cara benar, jadi jawabanmu boleh berbeda dari di sini selama hasilnya sama.

## Pelajaran 1

**Latihan 1.1: Cetak namamu.**

```krc
nyetak "Budi"
```

```hasil
Budi
```

**Latihan 1.2: Tiga baris puisi dengan satu `nyetak`.**

```krc
nyetak "Gunung tinggi\nLembah dalam\nAir mengalir"
```

```hasil
Gunung tinggi
Lembah dalam
Air mengalir
```

**Latihan 1.3: Kalimat dengan tanda kutip.**

```krc
nyetak "Dia berkata \"selamat pagi\""
```

```hasil
Dia berkata "selamat pagi"
```

## Pelajaran 2

**Latihan 2.1: Barang `nama` dan `kota`.**

```krc
barang nama = "Budi"
barang kota = "Sungai Penuh"
nyetak nama
nyetak kota
```

```hasil
Budi
Sungai Penuh
```

**Latihan 2.2: Saldo.**

```krc
barang saldo = 100
saldo = saldo + 50
nyetak saldo
```

```hasil
150
```

**Latihan 2.3: Jenis `"42"` dan `42`.**

```krc
nyetak mecem("42")
nyetak mecem(42)
```

```hasil
kato
bilangan
```

## Pelajaran 3

**Latihan 3.1: Luas persegi panjang.**

```krc
barang p = 12
barang l = 5
nyetak "Luas: " + (p * l)
```

```hasil
Luas: 60
```

**Latihan 3.2: Sisa 100 dibagi 7.**

```krc
nyetak 100 % 7
```

```hasil
2
```

**Latihan 3.3: Celsius ke Fahrenheit.**

```krc
barang celsius = 30
nyetak celsius * 9 / 5 + 32
```

```hasil
86
```

## Pelajaran 4

**Latihan 4.1: Nama dan kota.**

```krc masukan=Budi|Sungai Penuh
nyetak "Nama?"
barang nama = tanyo()
nyetak "Kota?"
barang kota = tanyo()
nyetak nama + " tinggal di " + kota
```

```hasil
Nama?
Kota?
Budi tinggal di Sungai Penuh
```

**Latihan 4.2: Rata-rata dua bilangan.**

```krc masukan=7|10
nyetak "Bilangan pertama?"
barang a = bilangan(tanyo())
nyetak "Bilangan kedua?"
barang b = bilangan(tanyo())
nyetak "Rata-rata: " + bagi(a + b, 2)
```

```hasil
Bilangan pertama?
Bilangan kedua?
Rata-rata: 8.5
```

**Latihan 4.3: Luas persegi.**

```krc masukan=6
nyetak "Panjang sisi?"
barang sisi = bilangan(tanyo())
nyetak "Luas: " + (sisi * sisi)
```

```hasil
Panjang sisi?
Luas: 36
```

## Pelajaran 5

**Latihan 5.1: Genap atau ganjil.**

```krc masukan=7
nyetak "Bilangan?"
barang n = bilangan(tanyo())
kalu n % 2 samo 0 {
    nyetak "genap"
} lain {
    nyetak "ganjil"
}
```

```hasil
Bilangan?
ganjil
```

**Latihan 5.2: Anak, remaja, atau dewasa.**

```krc masukan=15
nyetak "Umur?"
barang umur = bilangan(tanyo())
kalu umur kurang_daripado 13 {
    nyetak "anak"
} lain kalu umur kurang_samo 17 {
    nyetak "remaja"
} lain {
    nyetak "dewasa"
}
```

```hasil
Umur?
remaja
```

**Latihan 5.3: Yang terbesar dari tiga bilangan.**

```krc masukan=4|9|6
barang a = bilangan(tanyo())
barang b = bilangan(tanyo())
barang c = bilangan(tanyo())
barang terbesar = a
kalu b lebih_daripado terbesar { terbesar = b }
kalu c lebih_daripado terbesar { terbesar = c }
nyetak "Terbesar: " + terbesar
```

```hasil
Terbesar: 9
```

## Pelajaran 6

**Latihan 6.1: Hitung mundur 10 sampai 1.**

```krc
untuk i alem jarak(10, 0, 0 - 1) {
    nyetak i
}
```

```hasil
10
9
8
7
6
5
4
3
2
1
```

**Latihan 6.2: Tabel kali 7.**

```krc
untuk i alem jarak(1, 11) {
    nyetak "7 x " + i + " = " + (7 * i)
}
```

```hasil
7 x 1 = 7
7 x 2 = 14
7 x 3 = 21
7 x 4 = 28
7 x 5 = 35
7 x 6 = 42
7 x 7 = 49
7 x 8 = 56
7 x 9 = 63
7 x 10 = 70
```

**Latihan 6.3: Jumlah bilangan genap 1 sampai 50.**

```krc
barang total = 0
untuk i alem jarak(2, 51, 2) {
    total = total + i
}
nyetak total
```

```hasil
650
```

## Pelajaran 7

**Latihan 7.1: Lima nama dengan nomor.**

```krc
barang nama = ["Budi", "Sari", "Dewi", "Andi", "Rina"]
untuk i alem jarak(panjang(nama)) {
    nyetak (i + 1) + ". " + nama[i]
}
```

```hasil
1. Budi
2. Sari
3. Dewi
4. Andi
5. Rina
```

**Latihan 7.2: Jumlah dan nilai terkecil.**

```krc
barang angka = [14, 3, 27, 9, 21]
barang jumlah = 0
barang terkecil = angka[0]
untuk a alem angka {
    jumlah = jumlah + a
    kalu a kurang_daripado terkecil { terkecil = a }
}
nyetak "Jumlah: " + jumlah
nyetak "Terkecil: " + terkecil
```

```hasil
Jumlah: 74
Terkecil: 3
```

**Latihan 7.3: Kuadrat 1 sampai 5.**

```krc
barang kuadrat = []
untuk i alem jarak(1, 6) {
    nambahkah(kuadrat, i * i)
}
nyetak kuadrat
```

```hasil
[1, 4, 9, 16, 25]
```

## Pelajaran 8

**Latihan 8.1: Fungsi `genap`.**

```krc
guno genap(n) {
    balik n % 2 samo 0
}
nyetak genap(4)
nyetak genap(7)
```

```hasil
betul
salah
```

**Latihan 8.2: Fungsi `terbesar`.**

```krc
guno terbesar(daftar_angka) {
    barang hasil = daftar_angka[0]
    untuk a alem daftar_angka {
        kalu a lebih_daripado hasil { hasil = a }
    }
    balik hasil
}
nyetak terbesar([3, 9, 4])
```

```hasil
9
```

**Latihan 8.3: Fungsi `balik_kata` tanpa `pulang`.**

```krc
guno balik_kata(teks) {
    barang hasil = ""
    untuk huruf alem teks {
        hasil = huruf + hasil
    }
    balik hasil
}
nyetak balik_kata("kerinci")
```

```hasil
icnirek
```

## Pelajaran 9

**Latihan 9.1: Total harga dari peta.**

```krc
barang harga = {"kopi": 12000, "teh": 8000, "roti": 15000}
barang total = 0
untuk barang_ini alem harga {
    total = total + harga[barang_ini]
}
nyetak "Total: " + total
```

```hasil
Total: 35000
```

**Latihan 9.2: `nama_bulan` dengan `pilih`.**

```krc
guno nama_bulan(n) {
    pilih n {
        kalu 1 { balik "Januari" }
        kalu 2 { balik "Februari" }
        kalu 3 { balik "Maret" }
        lain { balik "tidak dikenal" }
    }
}
nyetak nama_bulan(2)
nyetak nama_bulan(9)
```

```hasil
Februari
tidak dikenal
```

**Latihan 9.3: Menghitung huruf dalam "kerinci".**

```krc
barang jumlah = {}
untuk huruf alem "kerinci" {
    kalu isi(jumlah, huruf) {
        jumlah[huruf] = jumlah[huruf] + 1
    } lain {
        jumlah[huruf] = 1
    }
}
nyetak jumlah
```

```hasil
{"k": 1, "e": 1, "r": 1, "i": 2, "n": 1, "c": 1}
```

## Pelajaran 10

**Latihan 10.1: Jumlah kata.**

```krc
nyetak panjang(pisah("saya belajar bahasa kerinci hari ini"))
```

```hasil
6
```

**Latihan 10.2: Palindrom atau bukan.**

```krc
guno kabar_palindrom(kata) {
    kalu kata samo pulang(kata) {
        nyetak kata + ": palindrom"
    } lain {
        nyetak kata + ": bukan"
    }
}
kabar_palindrom("malam")
kabar_palindrom("kerinci")
```

```hasil
malam: palindrom
kerinci: bukan
```

**Latihan 10.3: "a,b,c" menjadi "a-b-c".**

```krc
nyetak disatu(pisah("a,b,c", ","), "-")
```

```hasil
a-b-c
```

## Pelajaran 11

**Latihan 11.1: Tiga nama ke berkas.**

```krc
tulis("nama.txt", disatu(["Budi", "Sari", "Dewi"], "\n") + "\n")
nyetak baco("nama.txt")
```

```hasil
Budi
Sari
Dewi
```

**Latihan 11.2: Menghitung baris.**

```krc
tulis("data.txt", "satu\ndua\ntiga\nempat\n")
barang jumlah = 0
untuk baris alem bukak("data.txt") {
    jumlah = jumlah + 1
}
nyetak "Jumlah baris: " + jumlah
```

```hasil
Jumlah baris: 4
```

**Latihan 11.3: Bilangan 1 sampai 5 ke berkas.**

```krc
barang f = bukak("angka.txt", "tulis")
untuk i alem jarak(1, 6) {
    tulis(f, i + "\n")
}
tutup(f)
nyetak baco("angka.txt")
```

```hasil
1
2
3
4
5
```

## Pelajaran 12

**Latihan 12.1: Pembagian aman.**

```krc masukan=10|0
barang a = bilangan(tanyo())
barang b = bilangan(tanyo())
cubo {
    nyetak a / b
} tangkap {
    nyetak "tidak bisa dibagi nol"
}
```

```hasil
tidak bisa dibagi nol
```

**Latihan 12.2: Fungsi `periksa_umur`.**

```krc
guno periksa_umur(umur) {
    kalu umur kurang_daripado 0 {
        ngangkat "umur tidak boleh negatif"
    }
    balik umur
}

cubo {
    nyetak periksa_umur(20)
    nyetak periksa_umur(0 - 5)
} tangkap pesan {
    nyetak "Ditolak: " + pesan
}
```

```hasil
20
Ditolak: umur tidak boleh negatif
```

**Latihan 12.3: Berkas yang mungkin tidak ada.**

```krc
cubo {
    nyetak baco("tidak-ada.txt")
} tangkap {
    nyetak "kosong"
}
```

```hasil
kosong
```

## Pelajaran 13

Tantangan di pelajaran ini tidak punya jawaban tunggal. Contoh untuk tantangan 3 (menolak nilai di luar 0 sampai 100), yang bisa kamu taruh sebagai fungsi di modul:

```krc
guno periksa_nilai(nilai) {
    kalu nilai kurang_daripado 0 apo nilai lebih_daripado 100 {
        ngangkat "nilai harus antara 0 dan 100"
    }
    balik nilai
}

cubo {
    nyetak periksa_nilai(85)
    nyetak periksa_nilai(120)
} tangkap pesan {
    nyetak "Ditolak: " + pesan
}
```

```hasil
85
Ditolak: nilai harus antara 0 dan 100
```
