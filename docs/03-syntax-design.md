# 03. Language Reference

File extension: `.krc`. Encoding: UTF-8.

## Basics

- Comments start with `#` and run to the end of the line.
- Newlines and indentation do not matter.
- No semicolons.
- Blocks use `{ }` or `mulai ... habih`.
- Names (variables, functions) may contain any Unicode letter, digits and `_`, and cannot start with a digit.
- Keywords are lowercase and case-sensitive.

## Keywords

The words below are the **Siulak** list, frozen at v0.5 for compatibility.
Another dialect may spell them differently; the grammar and meaning are the
same. Do not read this list as a standard that another dialect must copy.

`barang` `tetap` `guno` `balik` `kalu` `lain` `selamo` `untuk` `alem` `pilih` `ambik` `cubo` `tangkap` `ngangkat` `putuh` `lanjut` `nyetak` `tanyo` `betul` `salah` `kosong` `ngan` `apo` `idak` `mulai` `habih`

Comparison words: `samo` `dak_samo` `lebih_daripado` `kurang_daripado` `lebih_samo` `kurang_samo`

Reserved for later: `kelihu` (error)

Built-in functions: `daftar` `peta` `panjang` `bilangan` `pecahan` `kato` `mecem` `jarak` `nambahkah` `isi` `milih` `pulang` `pisah` `disatu` `bukak` `baco` `tulis` `tutup` `hapus` `nantik` `tambah` `kurang` `kali` `bagi`


## Choosing a dialect

Siulak is the default. A file may choose another dialect on line 1:

```
# dialek: koto-payang
nytak "halo"
```

- The header must be the first line; a `# dialek:` line anywhere else is an
  ordinary comment.
- A malformed header on line 1 is an error, not a silent comment.
- `krc --dialek CODE file.krc` sets the default for files without a header.
  The header wins over `--dialek`, and Siulak is used when neither is present.
- `krc --ketat` fails (exit 2) when an approved dialect still borrows Tier 1
  words from the base.
- A function keeps the dialect it was written in; an imported file uses its own
  header, or the run default when it has none.

The lessons in `tutorial/` are written in Siulak. The same course is generated
with Koto Payang code in `tutorial/en/koto-payang/` and
`tutorial/id/koto-payang/`. Koto Payang is at `status: review`, so the generated
indexes list the English base words its lessons still use (`contains` and
`boolean`); they are not invented replacements, and a second speaker pass is
required before approval.

To add a dialect, follow [`09-adding-a-dialect.md`](09-adding-a-dialect.md).
A dialect is a data file with its own speakers; it never borrows another
dialect's words to fill a gap.

## Migrating old programs

A v0.5 program may have no dialect header. Add one, together with headers for
its literal imports:

```bash
krc migrasi examples/contoh.krc
krc migrasi examples --semua
krc migrasi program.krc --dialek koto-payang
krc migrasi program.krc --kering
```

- The default header is `# dialek: siulak`; `--dialek` chooses another code.
- `migrasi` follows literal `ambik "path"` imports recursively and never runs
  the program.
- A file that already has a valid header is never rewritten, so a second run is
  a no-op.
- `--kering` reports what would change without writing.
- It refuses a UTF-8 BOM, a malformed line-1 header, a syntax error, an unknown
  header dialect, and a computed import. The affected file is left unchanged.
- Exit 0 is success, 1 is a refused or failed file, and 2 is a usage error.

## Translating between dialects

`krc terjemah` rewrites one file's dialect words without running it:

```bash
krc terjemah program.krc --ke koto-payang --out program.kot
krc terjemah program.krc --ke koto-payang              # stdout
krc terjemah old.krc --dari siulak --ke koto-payang    # headerless input
krc terjemah program.krc --ke koto-payang --out out.krc --kering
```

- The source is the file's line-1 header, then `--dari`, then Siulak. `--ke`
  is always required and must name a valid dialect.
- Only keywords, word operators, built-in names, the header, and the direct
  second argument of `bukak` change. User names, comments, strings, numbers,
  spacing, and line endings are preserved byte for byte.
- The command refuses rather than guesses: a used ID the target does not own,
  a user name that collides with a target keyword/operator/built-in/reserved
  word, a user name that shadows a source built-in, or a mode/type string that
  cannot be translated losslessly. A refusal writes nothing.
- Same-dialect translation is a validated copy. A headerless file gains one
  header; a file translated A -> B -> A keeps its original bytes.
- Imports are not followed. Each imported file keeps its own header, so a
  translated main file can still import a module in another dialect.
- `--out` is atomic and may not equal the input; `--kering` previews without
  writing. Exit 0 is success, 1 is a refused file, and 2 is a usage error.

Only the words change, not the grammar. A dialect may spell the keywords and
built-ins differently, but braces, operators, values, and the program structure
are the same.

## Values

| Type | Example | Notes |
|---|---|---|
| Number | `42`, `3.14` | Integer or decimal |
| String | `"halo"` | Double quotes, one line; escapes `\n` `\t` `\"` `\\` |
| Boolean | `betul`, `salah` | Printed using the Kerinci words |
| Null | `kosong` | |
| List | `[1, "dua", betul]` | Can hold any values, including lists |
| Map | `{"nama": "Budi", "umur": 20}` | Keys are text or whole numbers; keeps the order you wrote |
| Function | `guno f() { }` | First-class; closures supported |

Falsy values: `salah`, `kosong`, `0`, `""`, `[]`, `{}`. Everything else is truthy.

## Programs by feature

### Print
```
nyetak "Halo, dunia"
nyetak 1 + 2
```

### Variables and constants
```
barang umur = 20
umur = umur + 1

tetap pi = 3.14
pi = 3          # Kesalahan: 'pi' adalah konstanta
```
A name must be declared with `barang` or `tetap` before it is assigned.

### Strings
```
barang nama = "Budi"
nyetak "Halo, " + nama
nyetak "Umur: " + 20
```
`+` joins when either side is a string.

### Conditions
```
barang nilai = 70
kalu nilai >= 80 {
    nyetak "Bagus"
} lain kalu nilai >= 60 {
    nyetak "Cukup"
} lain {
    nyetak "Ulang"
}
```

### Comparison words
```
kalu umur lebih_daripado 17 { nyetak "Dewasa" }
kalu nilai samo 100 { nyetak "Sempurna" }
kalu nama dak_samo "Budi" { nyetak "Bukan Budi" }
kalu i kurang_daripado 10 { nyetak "Kecil" }
```
Words and symbols mean the same thing and can be mixed.

### Logic
```
kalu umur lebih_daripado 17 ngan idak (umur > 60) {
    nyetak "Dewasa"
}
nyetak salah apo betul
```

### Loops
```
barang i = 1
selamo i <= 10 {
    kalu i samo 3 { lanjut }     # skip 3
    kalu i == 6 { putuh }      # stop at 6
    nyetak i
    i = i + 1
}
```
Careful: `lanjut` skips the rest of the loop body, so put the increment *before* it (or at the top of the body) to avoid an endless loop.

### Lists
```
barang nilai = [80, 65, 90]
nyetak nilai              # [80, 65, 90]
nyetak nilai[0]           # 80  (positions start at 0)
nilai[1] = 70             # change an element
nyetak panjang(nilai)     # 3
nyetak nilai + [100]      # [80, 70, 90, 100]  (joins, makes a new list)
nyetak [[1, 2], [3, 4]][1][0]   # 3
```
- `daftar(1, 2, 3)` builds the same list as `[1, 2, 3]`.
- Text can be indexed too (`"halo"[1]` is `"a"`) but not changed.
- Printing a list shows text in quotes, and `betul`, `salah`, `kosong` in Kerinci.
- Positions must be whole numbers from `0` to `panjang(x) - 1`. Negative positions are an error.
- To add an element to the end, use `nambahkah(xs, nilaiBaru)`. It changes the list itself.
- `xs + [nilaiBaru]` instead makes a new list and leaves `xs` as it was.
- `isi(xs, 3)` tells you whether `3` is in the list (`betul` or `salah`).
- `milih(xs)` gives a sorted copy and `pulang(xs)` a reversed copy; the original stays unchanged.

### For loops (`untuk ... alem`)
```
untuk n alem [80, 65, 90] { nyetak n }          # each element
untuk c alem "halo" { nyetak c }                 # each letter
untuk i alem jarak(5) { nyetak i }               # 0, 1, 2, 3, 4
untuk i alem jarak(1, 4) { nyetak i }            # 1, 2, 3
untuk i alem jarak(0, 10, 3) { nyetak i }        # 0, 3, 6, 9
untuk i alem jarak(panjang(nilai)) { nyetak nilai[i] }   # by position
```
Form: `untuk <name> alem <list or text> { ... }`. The name exists only inside the loop, and `putuh` and `lanjut` work as in `selamo`. To repeat something a number of times, loop over `jarak(n)`; `untuk i alem 5` is an error that tells you this. `alem` is now a reserved word.

`jarak` follows these rules: `jarak(n)` counts from `0` up to `n - 1`; `jarak(a, b)` from `a` up to `b - 1`; `jarak(a, b, langkah)` steps by `langkah` (negative steps count down, step `0` is an error). Arguments must be whole numbers.

### Built-in functions
```
nyetak panjang("halo")          # 4
nyetak jarak(1, 4)              # [1, 2, 3]
barang buah = ["pisang", "apel"]
nambahkah(buah, "jeruk")        # buah is now ["pisang", "apel", "jeruk"]
nyetak isi(buah, "apel")        # betul
nyetak isi("halo", "al")        # betul
nyetak milih(buah)              # ["apel", "jeruk", "pisang"]
nyetak pulang(buah)             # ["jeruk", "apel", "pisang"]
nyetak pulang("abc")            # cba
nyetak tambah(2, 3)             # 5
nyetak bagi(7, 2)               # 3.5
```
These are ordinary names. You may define your own `guno tambah(a, b) { ... }` or `barang jarak = 3` and it replaces the built-in inside your program. `milih` only sorts values that can be compared (all numbers or all text); a mixed list is an error.

### Converting types
```
nyetak bilangan("42") + 1     # 43
nyetak bilangan(3.7)          # 3  (decimals are cut off, not rounded)
nyetak pecahan("2.5") * 2     # 5.0
nyetak kato(12) + "!"         # 12!
nyetak mecem(5)               # bilangan
nyetak mecem("a")             # kato
```
`tanyo()` always returns text, so convert it before doing arithmetic:
```
nyetak "Umur?"
barang umur = bilangan(tanyo())
nyetak "Tahun depan: " + (umur + 1)
```
`bilangan` accepts whole-number text (`"42"`, `" 7 "`, `"-3"`) and numbers; `"3.5"` or `"abc"` is an error (use `bilangan(pecahan("3.5"))` for that). `mecem(x)` returns the type as text, so you can write `kalu mecem(x) samo "kato" { ... }`.

### Maps (`peta`)
```
barang siswa = {"Budi": 80, "Sari": 92}
nyetak siswa["Budi"]              # 80
siswa["Dewi"] = 65                # add a new key
siswa["Budi"] = 85                # change a value
nyetak panjang(siswa)             # 3
nyetak isi(siswa, "Sari")         # betul  (is it a key?)
untuk nama alem siswa {           # loops over the keys, in order
    nyetak nama + ": " + siswa[nama]
}
barang kosongan = {}              # empty map (same as peta())
```
- Keys must be text or whole numbers. A missing key is an error (`Kunci tidak ditemukan`), so check with `isi` first.
- Values can be anything, including lists and other maps: `murid["alamat"]["kota"]`.
- Maps, like lists, are shared: `barang b = a` makes `b` another name for the same map.
- `peta(["a", 1], ["b", 2])` builds a map from pairs.

### Choosing with `pilih`
```
barang hari = "sabtu"
pilih hari {
    kalu "sabtu", "minggu" { nyetak "libur" }
    kalu "jumat" { nyetak "hampir libur" }
    lain { nyetak "kerja" }
}
```
`pilih` compares the value with each `kalu` in order, runs the first one that matches (several values can be separated by commas), and skips the rest. There is no fall-through, and `lain` is optional. `balik`, `putuh` and `lanjut` work inside a `pilih` as they do elsewhere.

### Functions
```
guno kali(a, b) {
    balik a * b
}
nyetak kali(6, 7)
```

### Recursion
```
guno fakt(n) {
    kalu n kurang_samo 1 { balik 1 }
    balik n * fakt(n - 1)
}
nyetak fakt(5)
```

### Closures
```
guno buat() {
    barang n = 0
    guno tambah() {
        n = n + 1
        balik n
    }
    balik tambah
}
barang hitung = buat()
hitung()
nyetak hitung()      # 2
```

### Input
```
nyetak "Siapa namamu?"
barang nama = tanyo()
nyetak "Halo, " + nama
```
`tanyo()` always returns a string.

### Importing files (`ambik`)
`perkakas.krc`:
```
tetap versi = "1.0"
guno kuadrat(x) { balik x * x }
```
Main program:
```
ambik "perkakas"
nyetak versi            # 1.0
nyetak kuadrat(4)       # 16
```
- The path is relative to the file that contains the `ambik`; `.krc` may be left out; subfolders work (`ambik "alat/matematika"`).
- Every top-level name in the file (functions, variables, constants) becomes available to the importer. Imported functions keep access to their own file's private names.
- A file runs only once per program, even if several files import it. Circular imports are an error.
- An error inside an imported file is reported as `Dalam 'perkakas': ...`.

### Special characters in text
```
nyetak "baris satu\nbaris dua"      # \n starts a new line
nyetak "kolom\tkolom"               # \t is a tab
nyetak "dia berkata \"halo\""       # \" is a quote inside text
nyetak "C:\\folder\\berkas.txt"     # \\ is one backslash
```
Any other backslash sequence (like `\q`) is an error. A text literal still has to fit on one line; use `\n` for line breaks.

### Splitting and joining text
```
nyetak pisah("a,b,c", ",")            # ["a", "b", "c"]
nyetak pisah("a,,b", ",")             # ["a", "", "b"]   (empty pieces are kept)
nyetak pisah("belajar  kerinci")      # ["belajar", "kerinci"]   (no separator: splits on spaces)
nyetak pisah("abc", "")               # ["a", "b", "c"]  (empty separator: one piece per letter)
nyetak disatu(["a", "b", "c"], "-")   # a-b-c
nyetak disatu([1, 2, 3], ", ")        # 1, 2, 3
nyetak disatu(["a", "b"])             # ab   (separator is optional)
```
`pisah(teks, pemisah)` makes a list from a text; `disatu(daftar, pemisah)` is its opposite. Items that are not text are written as `nyetak` would show them.

### Files
```
tulis("catatan.txt", "baris 1\nbaris 2\n")      # create or replace a whole file
nyetak baco("catatan.txt")                      # read a whole file as text

barang f = bukak("catatan.txt", "nambahkah")    # open to add at the end
tulis(f, "baris 3\n")
tutup(f)

untuk baris alem bukak("catatan.txt") {         # read line by line
    nyetak baris
}
hapus("catatan.txt")                            # delete the file
```
| Call | What it does |
|---|---|
| `bukak(nama)` or `bukak(nama, "baco")` | open for reading |
| `bukak(nama, "tulis")` | open for writing (starts from an empty file) |
| `bukak(nama, "nambahkah")` | open for writing at the end of the file |
| `baco(x)` | `x` is a name or a file opened for reading: the rest of the text |
| `tulis(x, nilai)` | `x` is a name (replaces the file) or a file opened for writing; non-text values are written as `nyetak` would show them |
| `tutup(f)` | close a file (safe to repeat) |
| `hapus(nama)` | delete a file (not folders) |
| `untuk b alem f` | one line at a time, without the line break |

Files are UTF-8 text. All files still open when the program ends are closed automatically, but closing them yourself with `tutup` is good practice, especially before reading a file you just wrote. Using a file after `tutup`, reading from a file opened for writing, or the reverse is an error.

On Windows, write folder separators as `/` (`"data/nilai.txt"`) or double them (`"data\\nilai.txt"`).

### Waiting
```
nyetak "Mulai"
nantik(2)          # pause for 2 seconds (decimals allowed: nantik(0.5))
nyetak "Selesai"
```
`nantik` accepts 0 to 3600 seconds.

### Handling errors (`cubo`, `tangkap`, `ngangkat`)
```
cubo {
    barang umur = bilangan(tanyo())
    nyetak "Tahun depan: " + (umur + 1)
} tangkap pesan {
    nyetak "Masukan salah: " + pesan
}
```
If anything inside the `cubo` block fails, the rest of that block is skipped and the `tangkap` block runs, with the error text in `pesan` (the name is optional: `tangkap { ... }`). The `tangkap` block is required. Changes made before the failure stay (a variable assigned earlier keeps its new value), and `cubo` blocks can be nested. `balik`, `putuh` and `lanjut` work through a `cubo` block normally. Variables declared inside either block, and `pesan`, exist only inside it.

To report your own error, use `ngangkat`:
```
guno periksa(umur) {
    kalu umur kurang_daripado 0 { ngangkat "umur tidak boleh negatif" }
    balik umur
}
```
`ngangkat` takes any value and uses it as the message (non-text is shown as `nyetak` would show it). If nothing catches it, the program stops with `Kesalahan: <your message>`. Inside `tangkap`, `ngangkat pesan` passes the error on to an outer `cubo`.

The word `kelihu` ("error") is reserved for a future feature and cannot be used as a name.

Function calls may nest up to 400 levels deep (80 on Python older than 3.11). Beyond that you get the error `Panggilan fungsi terlalu dalam`, which `cubo` can catch.

### Using mulai / habih
```
guno sapa(nama)
mulai
    nyetak "Halo, " + nama
habih
```

## Operators

| Precedence (low to high) | Operators |
|---|---|
| 1 | `apo` |
| 2 | `ngan` |
| 3 | `==` `!=` and the words `samo` `dak_samo` |
| 4 | `<` `>` `<=` `>=` and the words `kurang_daripado` `lebih_daripado` `kurang_samo` `lebih_samo` |
| 5 | `+` `-` |
| 6 | `*` `/` `%` |
| 7 | `idak`, unary `-` |
| 8 | call `f(x)` and index `xs[i]` |

`ngan` and `apo` short-circuit.

## Grammar (EBNF)

```ebnf
program      = { statement } ;

statement    = var_decl | assignment | index_assign | func_decl | if_stmt
             | while_stmt | for_stmt | switch_stmt | import_stmt | try_stmt | raise_stmt | break_stmt | continue_stmt | return_stmt | print_stmt | expr_stmt ;

var_decl     = ( "barang" | "tetap" ) IDENT "=" expression ;
assignment   = IDENT "=" expression ;
index_assign = call "[" expression "]" "=" expression ;
func_decl    = "guno" IDENT "(" [ params ] ")" block ;
params       = IDENT { "," IDENT } ;
if_stmt      = "kalu" expression block [ "lain" ( if_stmt | block ) ] ;
               (* "lain kalu ..." is "lain" followed by another if_stmt *)
while_stmt   = "selamo" expression block ;
for_stmt     = "untuk" IDENT "alem" expression block ;
switch_stmt  = "pilih" expression "{" { "kalu" expression { "," expression } block }
               [ "lain" block ] "}" ;
import_stmt  = "ambik" expression ;
try_stmt     = "cubo" block "tangkap" [ IDENT ] block ;
raise_stmt   = "ngangkat" expression ;
break_stmt   = "putuh" ;            (* only inside selamo or untuk *)
continue_stmt= "lanjut" ;           (* only inside selamo or untuk *)
return_stmt  = "balik" [ expression ] ;   (* only inside guno *)
print_stmt   = "nyetak" expression ;
expr_stmt    = expression ;
block        = ( "{" | "mulai" ) { statement } ( "}" | "habih" ) ;

expression   = and_expr { "apo" and_expr } ;
and_expr     = equality { "ngan" equality } ;
equality     = comparison { ( "==" | "!=" | "samo" | "dak_samo" ) comparison } ;
comparison   = term { ( "<" | ">" | "<=" | ">="
                      | "kurang_daripado" | "lebih_daripado"
                      | "kurang_samo" | "lebih_samo" ) term } ;
term         = factor { ( "+" | "-" ) factor } ;
factor       = unary { ( "*" | "/" | "%" ) unary } ;
unary        = ( "idak" | "-" ) unary | call ;
call         = primary { "(" [ arguments ] ")" | "[" expression "]" } ;
arguments    = expression { "," expression } ;
primary      = NUMBER | STRING | "betul" | "salah" | "kosong"
             | "tanyo" "(" ")" | IDENT | "(" expression ")"
             | "[" [ expression { "," expression } [ "," ] ] "]"
             | "{" [ pair { "," pair } [ "," ] ] "}" ;
pair         = expression ":" expression ;
```

## Error messages

Messages are currently in Indonesian, with the keyword names shown in Kerinci:

| Situation | Message |
|---|---|
| Unknown name | `Nama belum didefinisikan: x` |
| Assign without declaring | `Nama belum dideklarasikan: x (pakai 'barang' dulu)` |
| Change a constant | `'pi' adalah konstanta ('tetap') dan tidak bisa diubah` |
| Divide by zero | `Pembagian dengan nol` |
| Wrong argument count | `Fungsi butuh 1 argumen, diberi 2` |
| Call a non-function | `Yang dipanggil bukan fungsi` |
| `putuh`/`lanjut` outside a loop | `Baris 1: 'putuh' hanya boleh di dalam perulangan` |
| Syntax error | `Baris 3: diharapkan '}', ditemukan ''` |
| `balik` outside a function | `Baris 1: 'balik' hanya boleh di dalam fungsi` |
| Bad conversion | `Tidak bisa mengubah "abc" menjadi bilangan` |
| Missing map key | `Kunci tidak ditemukan: "Andi"` |
| Missing file |  `Berkas tidak ditemukan: catatan.txt` |
| Using a closed file | `Berkas sudah ditutup: catatan.txt` |
| Wrong file mode | `Berkas ini dibuka untuk 'tulis', tidak bisa dipakai oleh 'baco'` |
| `cubo` without `tangkap` | `Baris 1: blok 'cubo' harus diikuti 'tangkap' dan blok penanganan` |
| Your own error with `ngangkat` | `Kesalahan: <your message>` |
| Unknown escape | `Baris 1: urutan escape tidak dikenal: \q` |
| Recursion too deep | `Panggilan fungsi terlalu dalam (lebih dari 400)...` |
| Missing import file | `Berkas tidak ditemukan: perkakas` |
| Circular import | `Impor melingkar: x` |

Kerinci translations of these messages are a good task for speakers (see `06`).

## Known gotchas

- **Newlines are ignored.** `x = 1` followed on the next line by `-2` parses as `x = 1 - 2`. Wrap in parentheses or restructure.
- **`lanjut` and counters.** See the loop example above.
- **`tanyo()` returns text.** There is no number conversion yet (planned with `bilangan` in v0.3).
- **Lists are shared, not copied.** After `barang b = a`, changing `b[0]` also changes `a`. To copy, write `barang b = a + []`.
- **A line starting with `[` continues the line before it** (because newlines are ignored): `barang x = y` followed by `[1, 2]` on the next line parses as `y[1, 2]`. Start such a line with a keyword, or wrap it in `nyetak`.
- **Division.** `/` and `bagi` give a whole number when the division is exact (`6 / 3` is `3`) and a decimal otherwise (`7 / 2` is `3.5`).
- **Constants and lists.** `tetap xs = [1]` stops you from reassigning `xs`, but the elements can still be changed (`xs[0] = 5`).
- **`{` is a map at the start of an expression and a block after one.** `barang p = {"a": 1}` is a map; `kalu x { ... }` is a block. `kalu {} { ... }` works too, but is rarely useful.
- **`bilangan` cuts decimals.** `bilangan(3.7)` is `3` and `bilangan(0 - 3.7)` is `-3`.
- **Imports share names.** If two imported files define the same name, the later one wins (constants give an error instead).
- **`mecem(betul)` returns `boolean`**, which is an English placeholder until speakers supply a word (see `02`).
- **`balik` is only allowed inside a function**, and `putuh` / `lanjut` only inside a loop; both are caught before the program runs.
- **Write and read in the right order.** A file you are still writing to may not show all its text until you call `tutup`. Close it before reading it back.
- **Reading twice.** After `baco(f)` on an open file, a second `baco(f)` returns empty text; the file has been read to its end. Reading by name (`baco("a.txt")`) always starts from the beginning.
- **`cubo` is a statement, not an expression.** It cannot be used inside another expression.
- **Errors inside a handler** are not caught by the same `cubo`; put another one around it.
- **`pisah(teks, "\n")` and the last line.** If a text ends with a line break, the last piece is empty. For files, `untuk b alem bukak(...)` avoids this.
- **Scope.** `kalu` and `selamo` bodies get their own scope, so a `barang` declared inside is not visible after the block. Assign to an outer variable declared beforehand instead.

## Ideas inspired by Kerinci grammar (later)

| Idea | Status |
|---|---|
| Arithmetic words as built-in functions | Done in v0.2 |
| List helpers (`nambahkah`, `isi`, `milih`, `pulang`) and `jarak` | Done in v0.2.1 |
| Postfix chaining (modifier after noun), e.g. `daftar urut balik` | Research with speakers |
| Reduplication as repetition or plural marker | Research with speakers |
| Incung script keywords | Check Unicode and font support |
