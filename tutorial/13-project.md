# Lesson 13: Project: a gradebook

Time to combine everything: maps, lists, functions, `pilih`, files, text and error handling in one useful program.

The program is a gradebook (*buku nilai*): it adds students' scores, shows everything with letter grades and the average, and saves to a file so the data is there the next time the program runs.

## Part 1: the module

We put the functions in a file of their own, `buku_nilai.krc`, to keep the main program tidy. The main program will load it with `ambik`.

```krc-berkas buku_nilai.krc
# buku_nilai.krc: functions for saving and calculating student scores

# load the data from the file; if the file does not exist yet, start with empty data
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
        # the file does not exist yet, that is fine
    }
    balik data
}

# save: one student per line, "name,score"
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

Notice that every function does one thing only. That makes a program easy to understand and to fix.

## Part 2: the main program

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

This example was run with these inputs: add Budi 80, add Sari 92, add Dewi with the score "abc" (refused by `cubo`/`tangkap`), show everything, then save and exit.

## Part 3: saved data

If `nilai.txt` already exists from earlier use, the program loads it. Suppose its contents are:

```krc-berkas nilai.txt
Budi,80
Sari,92
```

The same program immediately shows that data:

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

## Challenges

Extend this gradebook yourself:

1. Add a menu "4. Cari nilai seorang siswa" (look up one student's score) that checks with `isi` whether the name exists.
2. Also show the student with the highest score.
3. Refuse scores outside 0 to 100 with `ngangkat`.
4. Move more functions into the module.

## Congratulations!

You have now learned the whole of KerinciLang: displaying and input, barang and kinds of values, decisions and loops, lists and maps, functions, text, files, errors and modules. With these you can write useful programs.

To find any Kerinci word, open the [glossary](glossary.md). If you are a Kerinci speaker and you find a word that does not feel right, tell us using the instructions in [CONTRIBUTING.md](../CONTRIBUTING.md). This language belongs to its speakers.
