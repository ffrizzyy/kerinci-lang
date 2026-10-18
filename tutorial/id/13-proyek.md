# Pelajaran 13: Proyek buku nilai

Saatnya menggabungkan semuanya: peta, daftar, fungsi, `pilih`, berkas, teks, dan penanganan kesalahan menjadi satu program yang berguna.

Programnya adalah buku nilai: menambah nilai siswa, melihat semuanya dengan huruf mutu dan rata-rata, dan menyimpannya ke berkas supaya ada saat program dijalankan lagi.

## Bagian 1: modul

Fungsi-fungsi kita taruh di berkas sendiri, `buku_nilai.krc`, supaya program utama rapi. Nanti program utama memuatnya dengan `ambik`.

```krc-berkas buku_nilai.krc
# buku_nilai.krc: fungsi untuk menyimpan dan menghitung nilai siswa

# memuat data dari berkas; kalau berkas belum ada, mulai dari data kosong
guno muat(nama_berkas) {
    barang data = {}
    cubo {
        untuk baris alem bukak(nama_berkas) {
            kalu panjang(baris) lebih_daripado 0 {
                barang bagian = pisah(baris, ",")
                data[bagian[0]] = bilangan(bagian[1])
            }
        }
    } tangkap {
        # berkas belum ada, tidak apa-apa
    }
    balik data
}

# menyimpan: satu siswa per baris, "nama,nilai"
guno simpan(nama_berkas, data) {
    barang baris = []
    untuk nama alem data {
        nambahkah(baris, nama + "," + data[nama])
    }
    tulis(nama_berkas, disatu(baris, "\n"))
}

guno rata_rata(data) {
    kalu panjang(data) samo 0 { balik 0 }
    barang total = 0
    untuk nama alem data { total = total + data[nama] }
    balik bagi(total, panjang(data))
}

guno huruf(nilai) {
    pilih bilangan(bagi(nilai, 10)) {
        kalu 10, 9 { balik "A" }
        kalu 8 { balik "B" }
        kalu 7 { balik "C" }
        lain { balik "D" }
    }
}
```

Perhatikan bahwa setiap fungsi melakukan satu hal saja. Itu membuat program mudah dipahami dan diperbaiki.

## Bagian 2: program utama

```krc masukan=1|Budi|80|1|Sari|92|1|Dewi|abc|2|3
ambik "buku_nilai"

tetap berkas_nilai = "nilai.txt"
barang data = muat(berkas_nilai)

selamo betul {
    nyetak "--- Buku Nilai ---"
    nyetak "1. Tambah nilai"
    nyetak "2. Lihat semua"
    nyetak "3. Simpan dan keluar"
    barang pilihan = tanyo()
    pilih pilihan {
        kalu "1" {
            nyetak "Nama?"
            barang nama = tanyo()
            nyetak "Nilai?"
            cubo {
                data[nama] = bilangan(tanyo())
                nyetak "Tersimpan: " + nama
            } tangkap {
                nyetak "Nilai harus bilangan bulat."
            }
        }
        kalu "2" {
            untuk nama alem data {
                nyetak nama + ": " + data[nama] + " (" + huruf(data[nama]) + ")"
            }
            nyetak "Rata-rata: " + rata_rata(data)
        }
        kalu "3" {
            simpan(berkas_nilai, data)
            nyetak "Data disimpan. Sampai jumpa!"
            putuh
        }
        lain {
            nyetak "Pilihan tidak dikenal."
        }
    }
}
```

```hasil
--- Buku Nilai ---
1. Tambah nilai
2. Lihat semua
3. Simpan dan keluar
Nama?
Nilai?
Tersimpan: Budi
--- Buku Nilai ---
1. Tambah nilai
2. Lihat semua
3. Simpan dan keluar
Nama?
Nilai?
Tersimpan: Sari
--- Buku Nilai ---
1. Tambah nilai
2. Lihat semua
3. Simpan dan keluar
Nama?
Nilai?
Nilai harus bilangan bulat.
--- Buku Nilai ---
1. Tambah nilai
2. Lihat semua
3. Simpan dan keluar
Budi: 80 (B)
Sari: 92 (A)
Rata-rata: 86
--- Buku Nilai ---
1. Tambah nilai
2. Lihat semua
3. Simpan dan keluar
Data disimpan. Sampai jumpa!
```

Contoh ini dijalankan dengan masukan: tambah Budi 80, tambah Sari 92, tambah Dewi dengan nilai "abc" (ditolak oleh `cubo`/`tangkap`), lihat semua, lalu simpan dan keluar.

## Bagian 3: data tersimpan

Kalau `nilai.txt` sudah ada dari penggunaan sebelumnya, program memuatnya. Misalkan isi berkasnya:

```krc-berkas nilai.txt
Budi,80
Sari,92
```

Program yang sama langsung menampilkan data itu:

```krc masukan=2|3
ambik "buku_nilai"

tetap berkas_nilai = "nilai.txt"
barang data = muat(berkas_nilai)

selamo betul {
    nyetak "1. Tambah nilai  2. Lihat semua  3. Simpan dan keluar"
    barang pilihan = tanyo()
    pilih pilihan {
        kalu "2" {
            untuk nama alem data {
                nyetak nama + ": " + data[nama] + " (" + huruf(data[nama]) + ")"
            }
            nyetak "Rata-rata: " + rata_rata(data)
        }
        kalu "3" { putuh }
        lain { nyetak "Pilihan tidak dikenal." }
    }
}
nyetak "Selesai"
```

```hasil
1. Tambah nilai  2. Lihat semua  3. Simpan dan keluar
Budi: 80 (B)
Sari: 92 (A)
Rata-rata: 86
1. Tambah nilai  2. Lihat semua  3. Simpan dan keluar
Selesai
```

## Tantangan

Kembangkan sendiri buku nilai ini:

1. Tambah menu "4. Cari nilai seorang siswa" yang memeriksa dengan `isi` apakah namanya ada.
2. Tampilkan juga siswa dengan nilai tertinggi.
3. Tolak nilai di luar 0 sampai 100 dengan `ngangkat`.
4. Pisahkan lebih banyak fungsi ke dalam modul.

## Selamat!

Kamu sudah mempelajari seluruh KerinciLang: tampilan dan masukan, barang dan jenis nilai, keputusan dan perulangan, daftar dan peta, fungsi, teks, berkas, kesalahan, dan modul. Dengan bahan itu kamu bisa menulis program yang berguna.

Untuk menemukan kata Kerinci apa pun, buka [glosarium](glosarium.md). Kalau kamu penutur Kerinci dan menemukan kata yang kurang tepat, ceritakan lewat petunjuk di [CONTRIBUTING.md](../../CONTRIBUTING.md). Bahasa ini milik penuturnya.
