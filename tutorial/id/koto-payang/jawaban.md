# Jawaban latihan

Cobalah mengerjakan sendiri dulu. Ada banyak cara benar, jadi jawabanmu boleh berbeda dari di sini selama hasilnya sama.

## Pelajaran 1

**Latihan 1.1: Cetak namamu.**

```krc
# dialek: koto-payang
nytak "Budi"
```

```hasil
Budi
```

**Latihan 1.2: Tiga baris puisi dengan satu `nytak`.**

```krc
# dialek: koto-payang
nytak "Gunung tinggi\nLembah dalam\nAir mengalir"
```

```hasil
Gunung tinggi
Lembah dalam
Air mengalir
```

**Latihan 1.3: Kalimat dengan tanda kutip.**

```krc
# dialek: koto-payang
nytak "Dia berkata \"selamat pagi\""
```

```hasil
Dia berkata "selamat pagi"
```

## Pelajaran 2

**Latihan 2.1: Barang `nama` dan `kota`.**

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

**Latihan 2.2: Saldo.**

```krc
# dialek: koto-payang
netakka_variabel saldo = 100
saldo = saldo + 50
nytak saldo
```

```hasil
150
```

**Latihan 2.3: Jenis `"42"` dan `42`.**

```krc
# dialek: koto-payang
nytak tipe("42")
nytak tipe(42)
```

```hasil
tulisan
bilangan_buluak
```

## Pelajaran 3

**Latihan 3.1: Luas persegi panjang.**

```krc
# dialek: koto-payang
netakka_variabel p = 12
netakka_variabel l = 5
nytak "Luas: " + (p * l)
```

```hasil
Luas: 60
```

**Latihan 3.2: Sisa 100 dibagi 7.**

```krc
# dialek: koto-payang
nytak 100 % 7
```

```hasil
2
```

**Latihan 3.3: Celsius ke Fahrenheit.**

```krc
# dialek: koto-payang
netakka_variabel celsius = 30
nytak celsius * 9 / 5 + 32
```

```hasil
86
```

## Pelajaran 4

**Latihan 4.1: Nama dan kota.**

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

**Latihan 4.2: Rata-rata dua bilangan.**

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

**Latihan 4.3: Luas persegi.**

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

## Pelajaran 5

**Latihan 5.1: Genap atau ganjil.**

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

**Latihan 5.2: Anak, remaja, atau dewasa.**

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

**Latihan 5.3: Yang terbesar dari tiga bilangan.**

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

## Pelajaran 6

**Latihan 6.1: Hitung mundur 10 sampai 1.**

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

**Latihan 6.2: Tabel kali 7.**

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

**Latihan 6.3: Jumlah bilangan genap 1 sampai 50.**

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

## Pelajaran 7

**Latihan 7.1: Lima nama dengan nomor.**

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

**Latihan 7.2: Jumlah dan nilai terkecil.**

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

**Latihan 7.3: Kuadrat 1 sampai 5.**

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

## Pelajaran 8

**Latihan 8.1: Fungsi `genap`.**

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

**Latihan 8.2: Fungsi `terbesar`.**

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

**Latihan 8.3: Fungsi `balik_kata` tanpa `tebaluik`.**

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

## Pelajaran 9

**Latihan 9.1: Total harga dari peta.**

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

**Latihan 9.2: `nama_bulan` dengan `cocokka`.**

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

**Latihan 9.3: Menghitung huruf dalam "kerinci".**

```krc
# dialek: koto-payang
netakka_variabel jumlah = {}
ndik huruf daling "kerinci" {
    kalu contains(jumlah, huruf) {
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

## Pelajaran 10

**Latihan 10.1: Jumlah kata.**

```krc
# dialek: koto-payang
nytak panja(pecah("saya belajar bahasa kerinci hari ini"))
```

```hasil
6
```

**Latihan 10.2: Palindrom atau bukan.**

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

**Latihan 10.3: "a,b,c" menjadi "a-b-c".**

```krc
# dialek: koto-payang
nytak basatau(pecah("a,b,c", ","), "-")
```

```hasil
a-b-c
```

## Pelajaran 11

**Latihan 11.1: Tiga nama ke berkas.**

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

**Latihan 11.2: Menghitung baris.**

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

**Latihan 11.3: Bilangan 1 sampai 5 ke berkas.**

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

## Pelajaran 12

**Latihan 12.1: Pembagian aman.**

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

**Latihan 12.2: Fungsi `periksa_umur`.**

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

**Latihan 12.3: Berkas yang mungkin tidak ada.**

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

## Pelajaran 13

Tantangan di pelajaran ini tidak punya jawaban tunggal. Contoh untuk tantangan 3 (menolak nilai di luar 0 sampai 100), yang bisa kamu taruh sebagai fungsi di modul:

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
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: review).*
