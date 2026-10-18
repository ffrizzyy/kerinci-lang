# Answers to the exercises

Try the exercises yourself first. There are many correct ways, so your answer may differ from the one here as long as the result is the same.

## Lesson 1

**Exercise 1.1: Print your name.**

```krc
nyetak "Budi"
```

```hasil
Budi
```

**Exercise 1.2: Three lines of a poem with one `nyetak`.**

```krc
nyetak "Gunung tinggi\nLembah dalam\nAir mengalir"
```

```hasil
Gunung tinggi
Lembah dalam
Air mengalir
```

**Exercise 1.3: A sentence with quotation marks.**

```krc
nyetak "Dia berkata \"selamat pagi\""
```

```hasil
Dia berkata "selamat pagi"
```

## Lesson 2

**Exercise 2.1: The barang `nama` and `kota`.**

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

**Exercise 2.2: Balance.**

```krc
barang saldo = 100
saldo = saldo + 50
nyetak saldo
```

```hasil
150
```

**Exercise 2.3: The kinds of `"42"` and `42`.**

```krc
nyetak mecem("42")
nyetak mecem(42)
```

```hasil
kato
bilangan
```

## Lesson 3

**Exercise 3.1: Area of a rectangle.**

```krc
barang p = 12
barang l = 5
nyetak "Luas: " + (p * l)
```

```hasil
Luas: 60
```

**Exercise 3.2: Remainder of 100 divided by 7.**

```krc
nyetak 100 % 7
```

```hasil
2
```

**Exercise 3.3: Celsius to Fahrenheit.**

```krc
barang celsius = 30
nyetak celsius * 9 / 5 + 32
```

```hasil
86
```

## Lesson 4

**Exercise 4.1: Name and city.**

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

**Exercise 4.2: Average of two numbers.**

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

**Exercise 4.3: Area of a square.**

```krc masukan=6
nyetak "Panjang sisi?"
barang sisi = bilangan(tanyo())
nyetak "Luas: " + (sisi * sisi)
```

```hasil
Panjang sisi?
Luas: 36
```

## Lesson 5

**Exercise 5.1: Even or odd.**

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

**Exercise 5.2: Child, teenager or adult.**

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

**Exercise 5.3: The largest of three numbers.**

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

## Lesson 6

**Exercise 6.1: Countdown from 10 to 1.**

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

**Exercise 6.2: The 7 times table.**

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

**Exercise 6.3: Sum of the even numbers from 1 to 50.**

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

## Lesson 7

**Exercise 7.1: Five names with numbers.**

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

**Exercise 7.2: Sum and smallest value.**

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

**Exercise 7.3: Squares of 1 to 5.**

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

## Lesson 8

**Exercise 8.1: The function `genap`.**

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

**Exercise 8.2: The function `terbesar`.**

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

**Exercise 8.3: The function `balik_kata` without `pulang`.**

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

## Lesson 9

**Exercise 9.1: Total price from a map.**

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

**Exercise 9.2: `nama_bulan` with `pilih`.**

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

**Exercise 9.3: Counting the letters in "kerinci".**

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

## Lesson 10

**Exercise 10.1: Number of words.**

```krc
nyetak panjang(pisah("saya belajar bahasa kerinci hari ini"))
```

```hasil
6
```

**Exercise 10.2: Palindrome or not.**

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

**Exercise 10.3: "a,b,c" becomes "a-b-c".**

```krc
nyetak disatu(pisah("a,b,c", ","), "-")
```

```hasil
a-b-c
```

## Lesson 11

**Exercise 11.1: Three names in a file.**

```krc
tulis("nama.txt", disatu(["Budi", "Sari", "Dewi"], "\n") + "\n")
nyetak baco("nama.txt")
```

```hasil
Budi
Sari
Dewi
```

**Exercise 11.2: Counting lines.**

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

**Exercise 11.3: The numbers 1 to 5 in a file.**

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

## Lesson 12

**Exercise 12.1: Safe division.**

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

**Exercise 12.2: The function `periksa_umur`.**

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

**Exercise 12.3: A file that might not exist.**

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

## Lesson 13

The challenges in this lesson have no single answer. Here is an example for challenge 3 (refusing scores outside 0 to 100), which you can place as a function in the module:

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
