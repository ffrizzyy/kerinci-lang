# Glossary

Every KerinciLang word in Kerinci (Siulak dialect), with its meaning in English and Indonesian. The meaning column explains **how the word is used in the programming language**. For the meaning, spelling and everyday use of a word in Kerinci itself, the speakers decide; see [CONTRIBUTING.md](../CONTRIBUTING.md).

## Special words (cannot be used as variable names)

| Kerinci | Meaning | Indonesian | Example |
|---|---|---|---|
| `barang` | variable: a named container that stores a value | variabel: wadah bernama untuk menyimpan nilai | `barang umur = 20` |
| `tetap` | constant: a variable that cannot be changed | konstanta: barang yang tidak boleh diubah | `tetap pi = 3.14` |
| `guno` | function: define your own function | membuat fungsi | `guno kuadrat(x) { balik x * x }` |
| `balik` | return: send a result back from a function | mengembalikan hasil dari fungsi | `balik x * x` |
| `kalu` | if | jika (percabangan) | `kalu x > 5 { ... }` |
| `lain` | else; `lain kalu` = else if | kalau tidak; `lain kalu` = jika lainnya | `kalu x > 5 { ... } lain { ... }` |
| `selamo` | while: repeat as long as a condition is true | perulangan selama syarat benar | `selamo i < 10 { ... }` |
| `untuk` | for: repeat for every item | perulangan untuk setiap anggota | `untuk x alem daftar { ... }` |
| `alem` | in (used with `untuk`) | dalam (dipakai bersama `untuk`) | `untuk x alem daftar { ... }` |
| `putuh` | break: leave a loop immediately | menghentikan perulangan | `kalu i > 7 { putuh }` |
| `lanjut` | continue: skip to the next round of a loop | lompat ke putaran berikutnya | `kalu i % 2 samo 0 { lanjut }` |
| `nyetak` | print | mencetak nilai | `nyetak "Halo"` |
| `tanyo` | input: read what the user types (always text) | membaca masukan pengguna (selalu teks) | `barang nama = tanyo()` |
| `betul` | true | benar | `barang ok = betul` |
| `salah` | false | salah | `barang ok = salah` |
| `kosong` | null: no value | tidak ada nilai | `barang x = kosong` |
| `ngan` | and | dan | `kalu a > 1 ngan b > 1 { ... }` |
| `apo` | or | atau | `kalu a > 1 apo b > 1 { ... }` |
| `idak` | not | bukan | `kalu idak ok { ... }` |
| `mulai` | begin a block, same as `{` | awal blok, sama dengan `{` | `kalu betul mulai ... habih` |
| `habih` | end a block, same as `}` | akhir blok, sama dengan `}` | `kalu betul mulai ... habih` |
| `pilih` | switch: choose one branch out of many | memilih satu cabang dari banyak | `pilih hari { kalu 1 { ... } lain { ... } }` |
| `ambik` | import: load another program file | mengambil (memuat) berkas program lain | `ambik "perkakas"` |
| `cubo` | try: run a block that might fail | mencoba blok yang mungkin gagal | `cubo { ... } tangkap pesan { ... }` |
| `tangkap` | catch: handle an error from `cubo` | menangani kesalahan dari `cubo` | `cubo { ... } tangkap pesan { ... }` |
| `ngangkat` | raise: signal an error with a message | memunculkan kesalahan dengan pesan | `ngangkat "pesan"` |

## Comparison words

Exactly the same as their symbols, and the two styles can be mixed.

| Kerinci | Meaning | Indonesian | Symbol | Example |
|---|---|---|---|---|
| `samo` | equal to | sama dengan | `==` | `kalu a samo b { ... }` |
| `dak_samo` | not equal to | tidak sama dengan | `!=` | `kalu a dak_samo b { ... }` |
| `lebih_daripado` | greater than | lebih besar dari | `>` | `kalu a lebih_daripado b { ... }` |
| `kurang_daripado` | less than | lebih kecil dari | `<` | `kalu a kurang_daripado b { ... }` |
| `lebih_samo` | greater than or equal to | lebih besar atau sama | `>=` | `kalu a lebih_samo b { ... }` |
| `kurang_samo` | less than or equal to | lebih kecil atau sama | `<=` | `kalu a kurang_samo b { ... }` |

## Built-in functions

These are ordinary names, not special words, so you may create your own variable or function with the same name; yours is used in your program.

| Kerinci | Meaning | Indonesian | Example |
|---|---|---|---|
| `daftar` | list: build a list from values | membuat daftar dari nilai-nilai | `daftar(1, 2, 3)` |
| `peta` | map / dictionary: build a map from pairs | membuat peta (kunci dan nilai) | `peta(["a", 1], ["b", 2])` |
| `panjang` | length: number of items in a list or map, or letters in a text | jumlah anggota daftar, peta, atau huruf dalam teks | `panjang("kerinci")` |
| `jarak` | range: a list of consecutive numbers | daftar bilangan berurutan | `jarak(1, 6)` |
| `nambahkah` | append: add an item at the end of a list | menambah anggota di ujung daftar | `nambahkah(daftar, "x")` |
| `isi` | contains: is it in the list, map (as a key), or text? | memeriksa apakah ada di dalam daftar, peta (kunci), atau teks | `isi(daftar, "x")` |
| `milih` | sort: a sorted copy of a list | salinan daftar yang terurut | `milih([3, 1, 2])` |
| `pulang` | reverse: a reversed copy of a list or text | salinan daftar atau teks yang terbalik | `pulang("abc")` |
| `pisah` | split: break a text into a list | memecah teks menjadi daftar | `pisah("a,b", ",")` |
| `disatu` | join: join a list into one text | menyatukan daftar menjadi teks | `disatu(["a", "b"], "-")` |
| `bilangan` | integer: convert to a whole number | mengubah menjadi bilangan bulat | `bilangan("42")` |
| `pecahan` | decimal: convert to a decimal number | mengubah menjadi bilangan desimal | `pecahan("2.5")` |
| `kato` | string: convert to text | mengubah menjadi teks | `kato(12)` |
| `mecem` | type: name the type of a value | menyebut jenis nilai | `mecem("a")` |
| `tambah` | add, as a function | penjumlahan sebagai fungsi | `tambah(2, 3)` |
| `kurang` | subtract, as a function | pengurangan sebagai fungsi | `kurang(5, 2)` |
| `kali` | multiply, as a function | perkalian sebagai fungsi | `kali(2, 3)` |
| `bagi` | divide, as a function | pembagian sebagai fungsi | `bagi(7, 2)` |
| `bukak` | open a file | membuka berkas | `bukak("a.txt", "tulis")` |
| `baco` | read a whole file; also the file mode `"baco"` | membaca seluruh isi berkas; juga mode `"baco"` | `baco("a.txt")` |
| `tulis` | write to a file; also the file mode `"tulis"` | menulis ke berkas; juga mode `"tulis"` | `tulis("a.txt", "isi")` |
| `tutup` | close a file | menutup berkas | `tutup(f)` |
| `hapus` | delete a file | menghapus berkas | `hapus("a.txt")` |
| `nantik` | wait for some seconds | menunggu sekian detik | `nantik(2)` |

## Reserved words

Not used yet, but they cannot be used as names, so that programs do not break in a later version.

| Kerinci | Meaning | Indonesian |
|---|---|---|
| `kelihu` | error (held back for a future feature) | kesalahan (disimpan untuk fitur berikutnya) |

## Type names returned by `mecem`

| Value | `mecem` result |
|---|---|
| whole number | `bilangan` |
| decimal number | `pecahan` |
| text | `kato` |
| list | `daftar` |
| map | `peta` |
| function | `guno` |
| no value | `kosong` |
| open file | `berkas` |
| `betul` / `salah` | `boolean` (a temporary English word, waiting for a Kerinci word) |

## Error messages

The interpreter's messages are currently written in **Indonesian** (translating them into Kerinci is a task for speakers). Here is what the common ones mean. Words in `'quotes'` inside a message are KerinciLang words.

| Message | Meaning |
|---|---|
| `Kesalahan: ...` | Error: ... (every error message starts like this) |
| `Baris N: ...` | Line N: ... |
| `Dalam 'modul': ...` | In 'module': ... (the error happened inside an imported file) |
| `Nama belum didefinisikan: x` | Name not defined: x (you used a variable that does not exist) |
| `Nama belum dideklarasikan: x (pakai 'barang' dulu)` | Name not declared: x (create it with 'barang' first) |
| `'x' adalah konstanta ('tetap') dan tidak bisa diubah` | 'x' is a constant and cannot be changed |
| `Pembagian dengan nol` | Division by zero |
| `Operator '-' tidak bisa dipakai pada "a" dan 1` | Operator '-' cannot be used on "a" and 1 |
| `Tidak bisa mengubah "abc" menjadi bilangan` | Cannot convert "abc" to a whole number |
| `Indeks di luar jangkauan: 5 (panjang 2)` | Index out of range: 5 (length 2) |
| `Indeks harus bilangan bulat` | The index must be a whole number |
| `Kunci tidak ditemukan: "k"` | Key not found: "k" (in a map) |
| `Kunci peta harus teks atau bilangan bulat` | Map keys must be text or whole numbers |
| `Teks tidak bisa diubah per huruf` | Text cannot be changed letter by letter |
| `Fungsi butuh 2 argumen, diberi 1` | The function needs 2 arguments, given 1 |
| `Yang dipanggil bukan fungsi` | What you called is not a function |
| `Panggilan fungsi terlalu dalam (lebih dari 400)...` | Function calls nested too deeply (more than 400)... (a function probably calls itself forever) |
| `Berkas tidak ditemukan: nama` | File not found: nama |
| `Berkas sudah ditutup: nama` | File already closed: nama |
| `Berkas ini dibuka untuk 'tulis', tidak bisa dipakai oleh 'baco'` | This file was opened for 'tulis', so 'baco' cannot use it |
| `Baris N: karakter tidak dikenal '"'` | Line N: unrecognised character '"' (often a missing closing quote) |
| `Baris N: tidak terduga ''` | Line N: unexpected '' (something is missing, such as a value after `nyetak`) |
| `Baris N: diharapkan '}', ditemukan ''` | Line N: expected '}', found '' (a block was not closed) |
| `Baris N: 'balik' hanya boleh di dalam fungsi` | Line N: 'balik' is only allowed inside a function |
| `Baris N: 'putuh' hanya boleh di dalam perulangan` | Line N: 'putuh' is only allowed inside a loop |
| `Baris N: blok 'cubo' harus diikuti 'tangkap' dan blok penanganan` | Line N: a 'cubo' block must be followed by 'tangkap' and a handler block |
| `Impor melingkar: x` | Circular import: x (two files import each other) |
