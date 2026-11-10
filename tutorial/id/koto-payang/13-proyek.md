# Pelajaran 13: Proyek buku nilai

Saatnya menggabungkan semuanya: peta, daftar, fungsi, `cocokka`, berkas, teks, dan penanganan kesalahan menjadi satu program yang berguna.

Programnya adalah buku nilai: menambah nilai siswa, melihat semuanya dengan huruf mutu dan rata-rata, dan menyimpannya ke berkas supaya ada saat program dijalankan lagi.

## Bagian 1: modul

Fungsi-fungsi kita taruh di berkas sendiri, `buku_nilai.krc`, supaya program utama rapi. Nanti program utama memuatnya dengan `impor`.

```krc-berkas buku_nilai.krc
# dialek: koto-payang
# buku_nilai.krc: fungsi untuk menyimpan dan menghitung nilai siswa

# memuat data dari berkas; kalau berkas belum ada, mulai dari data kosong
jeloehka muat(nama_berkas) {
    netakka_variabel data = {}
    cubea {
        ndik baris daling bukuak(nama_berkas) {
            kalu panja(baris) lebih_geduang_dari 0 {
                netakka_variabel bagian = pecah(baris, ",")
                data[bagian[0]] = bilangan_buluak(bagian[1])
            }
        }
    } kecuali {
        # berkas belum ada, tidak apa-apa
    }
    baluikka data
}

# menyimpan: satu siswa per baris, "nama,nilai"
jeloehka simpan(nama_berkas, data) {
    netakka_variabel baris = []
    ndik nama daling data {
        tambahka(baris, nama + "," + data[nama])
    }
    tulaih(nama_berkas, basatau(baris, "\n"))
}

jeloehka rata_rata(data) {
    kalu panja(data) samu_dinga 0 { baluikka 0 }
    netakka_variabel total = 0
    ndik nama daling data { total = total + data[nama] }
    baluikka bagi(total, panja(data))
}

jeloehka huruf(nilai) {
    cocokka bilangan_buluak(bagi(nilai, 10)) {
        kalu 10, 9 { baluikka "A" }
        kalu 8 { baluikka "B" }
        kalu 7 { baluikka "C" }
        nga_laen { baluikka "D" }
    }
}
```

Perhatikan bahwa setiap fungsi melakukan satu hal saja. Itu membuat program mudah dipahami dan diperbaiki.

## Bagian 2: program utama

```krc masukan=1|Budi|80|1|Sari|92|1|Dewi|abc|2|3
# dialek: koto-payang
impor "buku_nilai"

netakka_konstanta berkas_nilai = "nilai.txt"
netakka_variabel data = muat(berkas_nilai)

selamu betiu {
    nytak "--- Buku Nilai ---"
    nytak "1. Tambah nilai"
    nytak "2. Lihat semua"
    nytak "3. Simpan dan keluar"
    netakka_variabel pilihan = masukka()
    cocokka pilihan {
        kalu "1" {
            nytak "Nama?"
            netakka_variabel nama = masukka()
            nytak "Nilai?"
            cubea {
                data[nama] = bilangan_buluak(masukka())
                nytak "Tersimpan: " + nama
            } kecuali {
                nytak "Nilai harus bilangan bulat."
            }
        }
        kalu "2" {
            ndik nama daling data {
                nytak nama + ": " + data[nama] + " (" + huruf(data[nama]) + ")"
            }
            nytak "Rata-rata: " + rata_rata(data)
        }
        kalu "3" {
            simpan(berkas_nilai, data)
            nytak "Data disimpan. Sampai jumpa!"
            slese
        }
        nga_laen {
            nytak "Pilihan tidak dikenal."
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

Contoh ini dijalankan dengan masukan: tambah Budi 80, tambah Sari 92, tambah Dewi dengan nilai "abc" (ditolak oleh `cubea`/`kecuali`), lihat semua, lalu simpan dan keluar.

## Bagian 3: data tersimpan

Kalau `nilai.txt` sudah ada dari penggunaan sebelumnya, program memuatnya. Misalkan isi berkasnya:

```krc-berkas nilai.txt
Budi,80
Sari,92
```

Program yang sama langsung menampilkan data itu:

```krc masukan=2|3
# dialek: koto-payang
impor "buku_nilai"

netakka_konstanta berkas_nilai = "nilai.txt"
netakka_variabel data = muat(berkas_nilai)

selamu betiu {
    nytak "1. Tambah nilai  2. Lihat semua  3. Simpan dan keluar"
    netakka_variabel pilihan = masukka()
    cocokka pilihan {
        kalu "2" {
            ndik nama daling data {
                nytak nama + ": " + data[nama] + " (" + huruf(data[nama]) + ")"
            }
            nytak "Rata-rata: " + rata_rata(data)
        }
        kalu "3" { slese }
        nga_laen { nytak "Pilihan tidak dikenal." }
    }
}
nytak "Selesai"
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

1. Tambah menu "4. Cari nilai seorang siswa" yang memeriksa dengan `meriksu` apakah namanya ada.
2. Tampilkan juga siswa dengan nilai tertinggi.
3. Tolak nilai di luar 0 sampai 100 dengan `timbaoka`.
4. Pisahkan lebih banyak fungsi ke dalam modul.

## Selamat!

Kamu sudah mempelajari seluruh KerinciLang: tampilan dan masukan, barang dan jenis nilai, keputusan dan perulangan, daftar dan peta, fungsi, teks, berkas, kesalahan, dan modul. Dengan bahan itu kamu bisa menulis program yang berguna.

Untuk menemukan kata Kerinci apa pun, buka [glosarium](glosarium.md). Kalau kamu penutur Kerinci dan menemukan kata yang kurang tepat, ceritakan lewat petunjuk di [CONTRIBUTING.md](../../../CONTRIBUTING.md). Bahasa ini milik penuturnya.

---
*Dibuat dari pelajaran Siulak. Kode dan kode sebaris memakai Koto Payang
(status: approved).*
