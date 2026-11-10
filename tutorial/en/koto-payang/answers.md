# Answers to the exercises

Try the exercises yourself first. There are many correct ways, so your answer may differ from the one here as long as the result is the same.

## Lesson 1

**Exercise 1.1: Print your name.**

```krc
# dialek: koto-payang
nytak "Budi"
```

```hasil
Budi
```

**Exercise 1.2: Three lines of a poem with one `nytak`.**

```krc
# dialek: koto-payang
nytak "Gunung tinggi\nLembah dalam\nAir mengalir"
```

```hasil
Gunung tinggi
Lembah dalam
Air mengalir
```

**Exercise 1.3: A sentence with quotation marks.**

```krc
# dialek: koto-payang
nytak "Dia berkata \"selamat pagi\""
```

```hasil
Dia berkata "selamat pagi"
```

## Lesson 2

**Exercise 2.1: The barang `nama` and `kota`.**

```krc
# dialek: koto-payang
netakka_variabel nama = "Budi"
netakka_variabel kota = "Sungai Penuh"
nytak nama
nytak kota
```

```hasil
Budi
Sungai Penuh
```

**Exercise 2.2: Balance.**

```krc
# dialek: koto-payang
netakka_variabel saldo = 100
saldo = saldo + 50
nytak saldo
```

```hasil
150
```

**Exercise 2.3: The kinds of `"42"` and `42`.**

```krc
# dialek: koto-payang
nytak tipe("42")
nytak tipe(42)
```

```hasil
tulisan
bilangan_buluak
```

## Lesson 3

**Exercise 3.1: Area of a rectangle.**

```krc
# dialek: koto-payang
netakka_variabel p = 12
netakka_variabel l = 5
nytak "Luas: " + (p * l)
```

```hasil
Luas: 60
```

**Exercise 3.2: Remainder of 100 divided by 7.**

```krc
# dialek: koto-payang
nytak 100 % 7
```

```hasil
2
```

**Exercise 3.3: Celsius to Fahrenheit.**

```krc
# dialek: koto-payang
netakka_variabel celsius = 30
nytak celsius * 9 / 5 + 32
```

```hasil
86
```

## Lesson 4

**Exercise 4.1: Name and city.**

```krc masukan=Budi|Sungai Penuh
# dialek: koto-payang
nytak "Nama?"
netakka_variabel nama = masukka()
nytak "Kota?"
netakka_variabel kota = masukka()
nytak nama + " tinggal di " + kota
```

```hasil
Nama?
Kota?
Budi tinggal di Sungai Penuh
```

**Exercise 4.2: Average of two numbers.**

```krc masukan=7|10
# dialek: koto-payang
nytak "Bilangan pertama?"
netakka_variabel a = bilangan_buluak(masukka())
nytak "Bilangan kedua?"
netakka_variabel b = bilangan_buluak(masukka())
nytak "Rata-rata: " + bagi(a + b, 2)
```

```hasil
Bilangan pertama?
Bilangan kedua?
Rata-rata: 8.5
```

**Exercise 4.3: Area of a square.**

```krc masukan=6
# dialek: koto-payang
nytak "Panjang sisi?"
netakka_variabel sisi = bilangan_buluak(masukka())
nytak "Luas: " + (sisi * sisi)
```

```hasil
Panjang sisi?
Luas: 36
```

## Lesson 5

**Exercise 5.1: Even or odd.**

```krc masukan=7
# dialek: koto-payang
nytak "Bilangan?"
netakka_variabel n = bilangan_buluak(masukka())
kalu n % 2 samu_dinga 0 {
    nytak "genap"
} nga_laen {
    nytak "ganjil"
}
```

```hasil
Bilangan?
ganjil
```

**Exercise 5.2: Child, teenager or adult.**

```krc masukan=15
# dialek: koto-payang
nytak "Umur?"
netakka_variabel umur = bilangan_buluak(masukka())
kalu umur lebih_nik_dari 13 {
    nytak "anak"
} nga_laen kalu umur lebih_nik_atau_samu_dinga 17 {
    nytak "remaja"
} nga_laen {
    nytak "dewasa"
}
```

```hasil
Umur?
remaja
```

**Exercise 5.3: The largest of three numbers.**

```krc masukan=4|9|6
# dialek: koto-payang
netakka_variabel a = bilangan_buluak(masukka())
netakka_variabel b = bilangan_buluak(masukka())
netakka_variabel c = bilangan_buluak(masukka())
netakka_variabel terbesar = a
kalu b lebih_geduang_dari terbesar { terbesar = b }
kalu c lebih_geduang_dari terbesar { terbesar = c }
nytak "Terbesar: " + terbesar
```

```hasil
Terbesar: 9
```

## Lesson 6

**Exercise 6.1: Countdown from 10 to 1.**

```krc
# dialek: koto-payang
ndik i daling rentang(10, 0, 0 - 1) {
    nytak i
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
# dialek: koto-payang
ndik i daling rentang(1, 11) {
    nytak "7 x " + i + " = " + (7 * i)
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
# dialek: koto-payang
netakka_variabel total = 0
ndik i daling rentang(2, 51, 2) {
    total = total + i
}
nytak total
```

```hasil
650
```

## Lesson 7

**Exercise 7.1: Five names with numbers.**

```krc
# dialek: koto-payang
netakka_variabel nama = ["Budi", "Sari", "Dewi", "Andi", "Rina"]
ndik i daling rentang(panja(nama)) {
    nytak (i + 1) + ". " + nama[i]
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
# dialek: koto-payang
netakka_variabel angka = [14, 3, 27, 9, 21]
netakka_variabel jumlah = 0
netakka_variabel terkecil = angka[0]
ndik a daling angka {
    jumlah = jumlah + a
    kalu a lebih_nik_dari terkecil { terkecil = a }
}
nytak "Jumlah: " + jumlah
nytak "Terkecil: " + terkecil
```

```hasil
Jumlah: 74
Terkecil: 3
```

**Exercise 7.3: Squares of 1 to 5.**

```krc
# dialek: koto-payang
netakka_variabel kuadrat = []
ndik i daling rentang(1, 6) {
    tambahka(kuadrat, i * i)
}
nytak kuadrat
```

```hasil
[1, 4, 9, 16, 25]
```

## Lesson 8

**Exercise 8.1: The function `genap`.**

```krc
# dialek: koto-payang
jeloehka genap(n) {
    baluikka n % 2 samu_dinga 0
}
nytak genap(4)
nytak genap(7)
```

```hasil
betiu
salah
```

**Exercise 8.2: The function `terbesar`.**

```krc
# dialek: koto-payang
jeloehka terbesar(daftar_angka) {
    netakka_variabel hasil = daftar_angka[0]
    ndik a daling daftar_angka {
        kalu a lebih_geduang_dari hasil { hasil = a }
    }
    baluikka hasil
}
nytak terbesar([3, 9, 4])
```

```hasil
9
```

**Exercise 8.3: The function `balik_kata` without `tebaluik`.**

```krc
# dialek: koto-payang
jeloehka balik_kata(teks) {
    netakka_variabel hasil = ""
    ndik huruf daling teks {
        hasil = huruf + hasil
    }
    baluikka hasil
}
nytak balik_kata("kerinci")
```

```hasil
icnirek
```

## Lesson 9

**Exercise 9.1: Total price from a map.**

```krc
# dialek: koto-payang
netakka_variabel harga = {"kopi": 12000, "teh": 8000, "roti": 15000}
netakka_variabel total = 0
ndik barang_ini daling harga {
    total = total + harga[barang_ini]
}
nytak "Total: " + total
```

```hasil
Total: 35000
```

**Exercise 9.2: `nama_bulan` with `cocokka`.**

```krc
# dialek: koto-payang
jeloehka nama_bulan(n) {
    cocokka n {
        kalu 1 { baluikka "Januari" }
        kalu 2 { baluikka "Februari" }
        kalu 3 { baluikka "Maret" }
        nga_laen { baluikka "tidak dikenal" }
    }
}
nytak nama_bulan(2)
nytak nama_bulan(9)
```

```hasil
Februari
tidak dikenal
```

**Exercise 9.3: Counting the letters in "kerinci".**

```krc
# dialek: koto-payang
netakka_variabel jumlah = {}
ndik huruf daling "kerinci" {
    kalu meriksu(jumlah, huruf) {
        jumlah[huruf] = jumlah[huruf] + 1
    } nga_laen {
        jumlah[huruf] = 1
    }
}
nytak jumlah
```

```hasil
{"k": 1, "e": 1, "r": 1, "i": 2, "n": 1, "c": 1}
```

## Lesson 10

**Exercise 10.1: Number of words.**

```krc
# dialek: koto-payang
nytak panja(pecah("saya belajar bahasa kerinci hari ini"))
```

```hasil
6
```

**Exercise 10.2: Palindrome or not.**

```krc
# dialek: koto-payang
jeloehka kabar_palindrom(kata) {
    kalu kata samu_dinga tebaluik(kata) {
        nytak kata + ": palindrom"
    } nga_laen {
        nytak kata + ": bukan"
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
# dialek: koto-payang
nytak basatau(pecah("a,b,c", ","), "-")
```

```hasil
a-b-c
```

## Lesson 11

**Exercise 11.1: Three names in a file.**

```krc
# dialek: koto-payang
tulaih("nama.txt", basatau(["Budi", "Sari", "Dewi"], "\n") + "\n")
nytak bacea("nama.txt")
```

```hasil
Budi
Sari
Dewi
```

**Exercise 11.2: Counting lines.**

```krc
# dialek: koto-payang
tulaih("data.txt", "satu\ndua\ntiga\nempat\n")
netakka_variabel jumlah = 0
ndik baris daling bukuak("data.txt") {
    jumlah = jumlah + 1
}
nytak "Jumlah baris: " + jumlah
```

```hasil
Jumlah baris: 4
```

**Exercise 11.3: The numbers 1 to 5 in a file.**

```krc
# dialek: koto-payang
netakka_variabel f = bukuak("angka.txt", "tulaih")
ndik i daling rentang(1, 6) {
    tulaih(f, i + "\n")
}
tutamp(f)
nytak bacea("angka.txt")
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
# dialek: koto-payang
netakka_variabel a = bilangan_buluak(masukka())
netakka_variabel b = bilangan_buluak(masukka())
cubea {
    nytak a / b
} kecuali {
    nytak "tidak bisa dibagi nol"
}
```

```hasil
tidak bisa dibagi nol
```

**Exercise 12.2: The function `periksa_umur`.**

```krc
# dialek: koto-payang
jeloehka periksa_umur(umur) {
    kalu umur lebih_nik_dari 0 {
        timbaoka "umur tidak boleh negatif"
    }
    baluikka umur
}

cubea {
    nytak periksa_umur(20)
    nytak periksa_umur(0 - 5)
} kecuali pesan {
    nytak "Ditolak: " + pesan
}
```

```hasil
20
Ditolak: umur tidak boleh negatif
```

**Exercise 12.3: A file that might not exist.**

```krc
# dialek: koto-payang
cubea {
    nytak bacea("tidak-ada.txt")
} kecuali {
    nytak "kosong"
}
```

```hasil
kosong
```

## Lesson 13

The challenges in this lesson have no single answer. Here is an example for challenge 3 (refusing scores outside 0 to 100), which you can place as a function in the module:

```krc
# dialek: koto-payang
jeloehka periksa_nilai(nilai) {
    kalu nilai lebih_nik_dari 0 atau nilai lebih_geduang_dari 100 {
        timbaoka "nilai harus antara 0 dan 100"
    }
    baluikka nilai
}

cubea {
    nytak periksa_nilai(85)
    nytak periksa_nilai(120)
} kecuali pesan {
    nytak "Ditolak: " + pesan
}
```

```hasil
85
Ditolak: nilai harus antara 0 dan 100
```

---
*Generated from the Siulak lesson. Code and inline code use Koto Payang
(status: approved).*
