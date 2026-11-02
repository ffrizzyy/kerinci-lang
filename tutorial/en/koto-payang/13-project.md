# Lesson 13: Project: a gradebook

Time to combine everything: maps, lists, functions, `cocokka`, files, text and error handling in one useful program.

The program is a gradebook (*buku nilai*): it adds students' scores, shows everything with letter grades and the average, and saves to a file so the data is there the next time the program runs.

## Part 1: the module

We put the functions in a file of their own, `buku_nilai.krc`, to keep the main program tidy. The main program will load it with `impor`.

```krc-berkas buku_nilai.krc
# dialek: koto-payang
# buku_nilai.krc: functions for saving and calculating student scores

# load the data from the file; if the file does not exist yet, start with empty data
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
        # the file does not exist yet, that is fine
    }
    baluikka data
}

# save: one student per line, "name,score"
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

Notice that every function does one thing only. That makes a program easy to understand and to fix.

## Part 2: the main program

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

This example was run with these inputs: add Budi 80, add Sari 92, add Dewi with the score "abc" (refused by `cubea`/`kecuali`), show everything, then save and exit.

## Part 3: saved data

If `nilai.txt` already exists from earlier use, the program loads it. Suppose its contents are:

```krc-berkas nilai.txt
Budi,80
Sari,92
```

The same program immediately shows that data:

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

## Challenges

Extend this gradebook yourself:

1. Add a menu "4. Cari nilai seorang siswa" (look up one student's score) that checks with `contains` whether the name exists.
2. Also show the student with the highest score.
3. Refuse scores outside 0 to 100 with `timbaoka`.
4. Move more functions into the module.

## Congratulations!

You have now learned the whole of KerinciLang: displaying and input, barang and kinds of values, decisions and loops, lists and maps, functions, text, files, errors and modules. With these you can write useful programs.

To find any Kerinci word, open the [glossary](glossary.md). If you are a Kerinci speaker and you find a word that does not feel right, tell us using the instructions in [CONTRIBUTING.md](../../../CONTRIBUTING.md). This language belongs to its speakers.

---
*Generated from the Siulak lesson. Code and inline code use Koto Payang
(status: review).*
