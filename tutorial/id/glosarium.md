# Glosarium

Semua kata KerinciLang dalam bahasa Kerinci (dialek Siulak), dengan arti dalam bahasa Indonesia dan Inggris. Kolom arti menjelaskan **cara kata itu dipakai dalam bahasa pemrograman**. Untuk makna, ejaan, dan pemakaian sehari-hari dalam bahasa Kerinci, penuturlah yang menentukan. Lihat [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Kata khusus (tidak boleh dipakai sebagai nama barang)

| Kerinci | Arti | English | Contoh |
|---|---|---|---|
| `barang` | variabel: wadah bernama untuk menyimpan nilai | variable: a named container that stores a value | `barang umur = 20` |
| `tetap` | konstanta: barang yang tidak boleh diubah | constant: a variable that cannot be changed | `tetap pi = 3.14` |
| `guno` | membuat fungsi | function: define your own function | `guno kuadrat(x) { balik x * x }` |
| `balik` | mengembalikan hasil dari fungsi | return: send a result back from a function | `balik x * x` |
| `kalu` | jika (percabangan) | if | `kalu x > 5 { ... }` |
| `lain` | kalau tidak; `lain kalu` = jika lainnya | else; `lain kalu` = else if | `kalu x > 5 { ... } lain { ... }` |
| `selamo` | perulangan selama syarat benar | while: repeat as long as a condition is true | `selamo i < 10 { ... }` |
| `untuk` | perulangan untuk setiap anggota | for: repeat for every item | `untuk x alem daftar { ... }` |
| `alem` | dalam (dipakai bersama `untuk`) | in (used with `untuk`) | `untuk x alem daftar { ... }` |
| `putuh` | menghentikan perulangan | break: leave a loop immediately | `kalu i > 7 { putuh }` |
| `lanjut` | lompat ke putaran berikutnya | continue: skip to the next round of a loop | `kalu i % 2 samo 0 { lanjut }` |
| `nyetak` | mencetak nilai | print | `nyetak "Halo"` |
| `tanyo` | membaca masukan pengguna (selalu teks) | input: read what the user types (always text) | `barang nama = tanyo()` |
| `betul` | benar | true | `barang ok = betul` |
| `salah` | salah | false | `barang ok = salah` |
| `kosong` | tidak ada nilai | null: no value | `barang x = kosong` |
| `ngan` | dan | and | `kalu a > 1 ngan b > 1 { ... }` |
| `apo` | atau | or | `kalu a > 1 apo b > 1 { ... }` |
| `idak` | bukan | not | `kalu idak ok { ... }` |
| `mulai` | awal blok, sama dengan `{` | begin a block, same as `{` | `kalu betul mulai ... habih` |
| `habih` | akhir blok, sama dengan `}` | end a block, same as `}` | `kalu betul mulai ... habih` |
| `pilih` | memilih satu cabang dari banyak | switch: choose one branch out of many | `pilih hari { kalu 1 { ... } lain { ... } }` |
| `ambik` | mengambil (memuat) berkas program lain | import: load another program file | `ambik "perkakas"` |
| `cubo` | mencoba blok yang mungkin gagal | try: run a block that might fail | `cubo { ... } tangkap pesan { ... }` |
| `tangkap` | menangani kesalahan dari `cubo` | catch: handle an error from `cubo` | `cubo { ... } tangkap pesan { ... }` |
| `ngangkat` | memunculkan kesalahan dengan pesan | raise: signal an error with a message | `ngangkat "pesan"` |

## Kata perbandingan

Sama persis dengan simbolnya, dan boleh dicampur.

| Kerinci | Arti | English | Simbol | Contoh |
|---|---|---|---|---|
| `samo` | sama dengan | equal to | `==` | `kalu a samo b { ... }` |
| `dak_samo` | tidak sama dengan | not equal to | `!=` | `kalu a dak_samo b { ... }` |
| `lebih_daripado` | lebih besar dari | greater than | `>` | `kalu a lebih_daripado b { ... }` |
| `kurang_daripado` | lebih kecil dari | less than | `<` | `kalu a kurang_daripado b { ... }` |
| `lebih_samo` | lebih besar atau sama | greater than or equal to | `>=` | `kalu a lebih_samo b { ... }` |
| `kurang_samo` | lebih kecil atau sama | less than or equal to | `<=` | `kalu a kurang_samo b { ... }` |

## Fungsi bawaan

Ini nama biasa, bukan kata khusus, jadi kamu boleh membuat barang atau fungsi dengan nama yang sama; milikmu akan dipakai di programmu.

| Kerinci | Arti | English | Contoh |
|---|---|---|---|
| `daftar` | membuat daftar dari nilai-nilai | list: build a list from values | `daftar(1, 2, 3)` |
| `peta` | membuat peta (kunci dan nilai) | map / dictionary: build a map from pairs | `peta(["a", 1], ["b", 2])` |
| `panjang` | jumlah anggota daftar, peta, atau huruf dalam teks | length: number of items in a list or map, or letters in a text | `panjang("kerinci")` |
| `jarak` | daftar bilangan berurutan | range: a list of consecutive numbers | `jarak(1, 6)` |
| `nambahkah` | menambah anggota di ujung daftar | append: add an item at the end of a list | `nambahkah(daftar, "x")` |
| `isi` | memeriksa apakah ada di dalam daftar, peta (kunci), atau teks | contains: is it in the list, map (as a key), or text? | `isi(daftar, "x")` |
| `milih` | salinan daftar yang terurut | sort: a sorted copy of a list | `milih([3, 1, 2])` |
| `pulang` | salinan daftar atau teks yang terbalik | reverse: a reversed copy of a list or text | `pulang("abc")` |
| `pisah` | memecah teks menjadi daftar | split: break a text into a list | `pisah("a,b", ",")` |
| `disatu` | menyatukan daftar menjadi teks | join: join a list into one text | `disatu(["a", "b"], "-")` |
| `bilangan` | mengubah menjadi bilangan bulat | integer: convert to a whole number | `bilangan("42")` |
| `pecahan` | mengubah menjadi bilangan desimal | decimal: convert to a decimal number | `pecahan("2.5")` |
| `kato` | mengubah menjadi teks | string: convert to text | `kato(12)` |
| `mecem` | menyebut jenis nilai | type: name the type of a value | `mecem("a")` |
| `tambah` | penjumlahan sebagai fungsi | add, as a function | `tambah(2, 3)` |
| `kurang` | pengurangan sebagai fungsi | subtract, as a function | `kurang(5, 2)` |
| `kali` | perkalian sebagai fungsi | multiply, as a function | `kali(2, 3)` |
| `bagi` | pembagian sebagai fungsi | divide, as a function | `bagi(7, 2)` |
| `bukak` | membuka berkas | open a file | `bukak("a.txt", "tulis")` |
| `baco` | membaca seluruh isi berkas; juga mode `"baco"` | read a whole file; also the file mode `"baco"` | `baco("a.txt")` |
| `tulis` | menulis ke berkas; juga mode `"tulis"` | write to a file; also the file mode `"tulis"` | `tulis("a.txt", "isi")` |
| `tutup` | menutup berkas | close a file | `tutup(f)` |
| `hapus` | menghapus berkas | delete a file | `hapus("a.txt")` |
| `nantik` | menunggu sekian detik | wait for some seconds | `nantik(2)` |

## Kata yang dicadangkan

Belum dipakai, tetapi tidak boleh dipakai sebagai nama supaya program tidak rusak di versi berikutnya.

| Kerinci | Arti | English |
|---|---|---|
| `kelihu` | kesalahan (disimpan untuk fitur berikutnya) | error (held back for a future feature) |

## Nama jenis dari `mecem`

| Nilai | Hasil `mecem` |
|---|---|
| bilangan bulat | `bilangan` |
| desimal | `pecahan` |
| teks | `kato` |
| daftar | `daftar` |
| peta | `peta` |
| fungsi | `guno` |
| tidak ada nilai | `kosong` |
| berkas terbuka | `berkas` |
| `betul` / `salah` | `boolean` (kata sementara dari bahasa Inggris; menunggu kata Kerinci) |
