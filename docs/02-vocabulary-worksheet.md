# 02. Vocabulary

Source: `tabel_kata_bahasa_pemrograman_kerinci.md` (Siulak dialect), plus decisions made while building.

## Decisions log

| Decision | Result |
|---|---|
| Speaker review (v0.5.0) | Every word and design choice in the checklist below was approved by Kerinci speakers. |
| `salah` was both "false" and "error" | `salah` = **false**. "error" = **`kelihu`** (reserved for a future feature, see below) |
| `kurang` was both "subtract" and "less than" | `kurang` = **subtract**. "less than" = **`kurang_daripado`** |
| greater than | **`lebih_daripado`** (replaces `lebih`) |
| true | **`betul`** (replaces `iyo`) |
| not | **`idak`** (replaces `nyado`) |
| else if | **`lain kalu`** (two words; `kalu_lain` is no longer used) |
| in (for loops) | **`alem`** (keyword): `untuk x alem xs { }` |
| `pilih` (v0.3) | multi-way choice keyword; each case is written with `kalu` |
| try | **`cubo`** (keyword): `cubo { ... } tangkap pesan { ... }` |
| catch | **`tangkap`** (keyword) |
| raise | **`ngangkat`** (keyword): `ngangkat "pesan"` |
| split | **`pisah`** (built-in): `pisah("a,b", ",")` |
| join | **`disatu`** (built-in): `disatu(["a", "b"], "-")` |
| file | **`berkas`**: confirmed as the type name returned by `mecem` for an open file |
| range | **`jarak`** (built-in): `jarak(5)` |
| append | **`nambahkah`** (built-in) |
| contains | **`isi`** (built-in) |
| sort | **`milih`** (built-in) |
| reverse | **`pulang`** (built-in) |

`kerincilang.py` asserts at startup that no two keywords share a word and that no operator word is also a keyword, so a clash like the earlier ones cannot slip through.

## Implemented keywords

| Internal | Meaning | Kerinci word | Status |
|---|---|---|---|
| `VAR` | variable | `barang` | ✅ |
| `CONST` | constant | `tetap` | ✅ |
| `FUNC` | function | `guno` | ✅ |
| `RETURN` | return | `balik` | ✅ |
| `IF` | if | `kalu` | ✅ |
| `ELSE` | else | `lain` | ✅ |
| (`ELSE` + `IF`) | else if | `lain kalu` | ✅ |
| `WHILE` | while | `selamo` | ✅ |
| `FOR` | for | `untuk` | ✅ v0.2 |
| `IN` | in | `alem` | ✅ v0.2.1 |
| `SWITCH` | choose | `pilih` | ✅ v0.3 |
| `IMPORT` | import | `ambik` | ✅ v0.3 |
| `TRY` | try | `cubo` | ✅ v0.5 |
| `CATCH` | catch | `tangkap` | ✅ v0.5 |
| `RAISE` | raise an error | `ngangkat` | ✅ v0.5 |
| `BREAK` | break | `putuh` | ✅ |
| `CONTINUE` | continue | `lanjut` | ✅ |
| `PRINT` | print | `nyetak` | ✅ |
| `INPUT` | input | `tanyo` | ✅ |
| `TRUE` | true | `betul` | ✅ |
| `FALSE` | false | `salah` | ✅ |
| `NULL` | null | `kosong` | ✅ |
| `AND` | and | `ngan` | ✅ |
| `OR` | or | `apo` | ✅ |
| `NOT` | not | `idak` | ✅ |
| `BEGIN` | begin block | `mulai` | ✅ same as `{` |
| `END` | end block | `habih` | ✅ same as `}` |

## Comparison words (implemented)

These are interchangeable with the symbols. Both styles work, even in the same program.

| Meaning | Word | Symbol |
|---|---|---|
| equal | `samo` | `==` |
| not equal | `dak_samo` | `!=` |
| greater than | `lebih_daripado` | `>` |
| less than | `kurang_daripado` | `<` |
| greater than or equal | `lebih_samo` | `>=` |
| less than or equal | `kurang_samo` | `<=` |

```
kalu umur lebih_daripado 17 { nyetak "Dewasa" }
kalu nilai samo 100 { nyetak "Sempurna" }
```

Set `ENABLE_WORD_OPERATORS = False` in `kerincilang.py` if you ever want these words free for variable names.

## Built-in functions (implemented)

They are ordinary names in a parent scope, not reserved words, so a program can still define its own `tambah` or `jarak`.

| Meaning | Name | Example | Result |
|---|---|---|---|
| list | `daftar` | `daftar(1, 2, 3)` | `[1, 2, 3]` (same as the literal) |
| length | `panjang` | `panjang([5, 6])`, `panjang("halo")`, `panjang({"a": 1})` | `2`, `4`, `1` |
| range | `jarak` | `jarak(4)`, `jarak(2, 5)`, `jarak(0, 10, 3)` | `[0, 1, 2, 3]`, `[2, 3, 4]`, `[0, 3, 6, 9]` |
| append | `nambahkah` | `nambahkah(xs, 4)` | adds `4` to `xs` itself; returns `kosong` |
| contains | `isi` | `isi([1, 2, 3], 2)`, `isi("halo", "al")` | `betul`, `betul` |
| sort | `milih` | `milih([3, 1, 2])` | `[1, 2, 3]` (new list) |
| reverse | `pulang` | `pulang([1, 2, 3])`, `pulang("abc")` | `[3, 2, 1]`, `"cba"` (new list or text) |
| integer | `bilangan` | `bilangan("42")`, `bilangan(3.7)` | `42`, `3` (decimals are cut off) |
| decimal | `pecahan` | `pecahan("2.5")`, `pecahan(3)` | `2.5`, `3.0` |
| string | `kato` | `kato(12)`, `kato([1, 2])` | `"12"`, `"[1, 2]"` |
| type | `mecem` | `mecem(5)`, `mecem("a")` | `"bilangan"`, `"kato"` |
| map | `peta` | `peta()`, `peta(["a", 1], ["b", 2])` | `{}`, `{"a": 1, "b": 2}` (the literal `{"a": 1}` also works) |
| split | `pisah` | `pisah("a,b", ",")`, `pisah("a  b")` | `["a", "b"]`, `["a", "b"]` (no separator: splits on spaces; empty separator: one piece per letter) |
| join | `disatu` | `disatu(["a", "b"], "-")`, `disatu([1, 2])` | `"a-b"`, `"12"` (non-text items are shown as `nyetak` would; separator is optional) |
| open file | `bukak` | `bukak("a.txt")`, `bukak("a.txt", "tulis")` | a file; modes are the words `"baco"` (default), `"tulis"`, `"nambahkah"` |
| read | `baco` | `baco("a.txt")`, `baco(f)` | the whole text of a file (by name or open file) |
| write | `tulis` | `tulis("a.txt", "isi")`, `tulis(f, "isi")` | `kosong`; by name it replaces the file |
| close | `tutup` | `tutup(f)` | `kosong` (closing twice is fine) |
| delete | `hapus` | `hapus("a.txt")` | `kosong`; **files only** |
| wait | `nantik` | `nantik(0.5)` | pauses 0.5 seconds (0 to 3600) |
| add | `tambah` | `tambah(2, 3)` | `5` (same as `+`) |
| subtract | `kurang` | `kurang(5, 2)` | `3` |
| multiply | `kali` | `kali(2, 3)` | `6` |
| divide | `bagi` | `bagi(7, 2)` | `3.5` (`bagi(6, 2)` gives `3`) |

Design choices: only `nambahkah` changes a list in place. `milih` and `pulang` return a new list and leave the original alone. `jarak` makes at most 1,000,000 numbers.

**Why arithmetic words are functions and not operators:** making them operators broke programs that used `kali` or `tambah` as function names ("times", "add"). As built-ins, they exist but never take the names away.

## Types returned by `mecem`

| Value | Result |
|---|---|
| whole number | `bilangan` |
| decimal | `pecahan` |
| text | `kato` |
| list | `daftar` |
| map | `peta` |
| function | `guno` |
| null | `kosong` |
| open file | `berkas` |
| true / false | `boolean` ⚠️ **placeholder**: the table has no Kerinci word for "boolean". Change `TYPE_NAMES["bool"]` in `kerincilang.py` when speakers supply one. |

## Error handling: `cubo`, `tangkap`, `ngangkat`

```
cubo {
    nyetak baco("tidak-ada.txt")
} tangkap pesan {
    nyetak "Gagal: " + pesan
}

guno periksa(x) {
    kalu x kurang_daripado 0 { ngangkat "tidak boleh negatif" }
    balik x
}
```

- `cubo { ... }` is the protected block (try).
- `tangkap pesan { ... }` runs if anything inside failed; the error text is in `pesan`. The name is optional: `tangkap { ... }`.
- `tangkap` is required after every `cubo`, so errors are never silently swallowed.
- `ngangkat expression` raises an error with that text (any non-text value is shown as `nyetak` would). Inside `tangkap`, `ngangkat` passes the error outwards.

`cubo` catches every run-time error (division by zero, wrong conversions, missing keys, missing files, too-deep recursion, `ngangkat`). It does not catch syntax errors, which are found before the program runs. `balik`, `putuh` and `lanjut` pass straight through a `cubo` block as normal.

**`kelihu` ("error") is reserved.** It is not used yet, but using it as a name is an error so no program breaks later. A possible use is error values (a caught error carrying more than text, e.g. a kind and a message). That needs a design decision with speakers.

## Words still missing

| Concept | Today | Notes |
|---|---|---|
| uppercase / lowercase text | not available | needed for case-insensitive comparison |
| find a position in text or a list | not available | e.g. where `"rin"` starts in `"kerinci"` |
| replace part of a text | not available | |
| trim spaces around text | not available | |
| does a file exist | try to open it inside `cubo` | a word like "ada" would be simpler |
| rename / copy a file | not available | |
| keys / values of a map | `untuk k alem p` gives keys; `p[k]` gives a value | words would allow `kunci(p)`, `nilai(p)` |
| remove from a list or map | not available | `hapus` is taken by files |
| boolean (type name) | placeholder `boolean` | see the `mecem` table |
| maximum / minimum / sum | not available | easy to add once there are words |
| random number | not available | needed for games |
| current date and time | not available | |
| index / position | `xs[0]` | brackets work; a word form is optional |
| "case" inside `pilih` | `kalu` is reused | e.g. `pilih x { kalu 1 { } }` |

## Things to check with speakers

Words and design choices that were put to Kerinci speakers, grouped by when they were added.

**Status (v0.5.0): the speaker review is complete and every item below was approved.** The two questions that remain open are listed at the end.

**Core (v0.1)**
- [x] Does `idak betul` read naturally?
- [x] Is `apo` (or) easy to confuse with the question word in everyday Siulak?
- [x] Is `lain kalu` the form people would write for "else if"?
- [x] Are `mulai` / `habih` the natural words for begin/end?
- [x] Are `betul` / `salah` / `kosong` the natural words for true / false / null?

**Lists, loops, comparisons (v0.2)**
- [x] Do `alem` and `jarak` read naturally in `untuk i alem jarak(5) { }`?
- [x] `milih` (sort) and the word `pilih` (choose) differ by one letter. Is that confusing in practice, or do speakers hear them as clearly different?
- [x] `isi(daftar, yang_dicari)`: is this argument order natural? (The alternative is `isi(yang_dicari, daftar)`.)
- [x] `nambahkah` returns `kosong` because it changes the list in place. Fine, or would speakers expect the new list back?
- [x] `pulang` for reverse and `balik` for return: any confusion?
- [x] Are `tambah`, `kurang`, `kali`, `bagi` good names for the arithmetic functions? Is `daftar(...)` natural for creating a list?
- [x] `lebih_samo` / `kurang_samo` (kept from the original table) and `lebih_daripado` / `kurang_daripado`: should the first pair follow the second pattern?

**Maps, choosing, imports (v0.3)**
- [x] `pilih x { kalu 1 { } lain { } }`: is reusing `kalu` for each case natural, or is there a better word for "case"?
- [x] `ambik "berkas"`: is `ambik` natural for importing a file?
- [x] `bilangan(3.7)` gives `3` (cuts the decimals). Would speakers expect rounding instead?
- [x] Type names from `mecem` (`bilangan`, `pecahan`, `kato`, `daftar`, `peta`, `guno`, `kosong`, `berkas`): confirm they read well.

**Files and errors (v0.4, v0.5)**
- [x] File modes are written with existing words: `bukak("a.txt", "tulis")` to write and `bukak("a.txt", "nambahkah")` to append. Natural, or confusing next to the functions of the same names?
- [x] `baco(x)` returns the whole text at once. Is that what speakers expect from "read"?
- [x] `hapus` deletes files. Is that the right word, or should it also mean "remove from a list"?
- [x] `cubo { } tangkap pesan { }` and `ngangkat "pesan"`: do these read naturally? Is `tangkap` the word speakers would pick for "catch"?
- [x] `pisah(teks, pemisah)` and `disatu(daftar, pemisah)`: natural names and argument order?

**Still open**
- [ ] A Kerinci word for "boolean". `mecem(betul)` still returns the temporary English word `boolean` (`TYPE_NAMES["bool"]` in `kerincilang.py`).
- [ ] What should `kelihu` ("error") be used for, now that it is reserved? (For example, error values that carry more than a message.)

## Changing a word

Edit the right-hand side of `KEYWORDS` (or `WORD_OPERATORS`) in `kerincilang.py`, then:

```bash
python3 make_highlight.py
python3 tests/test_kerincilang.py
```

The tests and `contoh.krc` contain Kerinci words, so update them when you rename a keyword.

## Dictionary bibliography

| Dictionary | Author / publisher | Year | URL | Notes |
|---|---|---|---|---|
| (add the dictionary you used) | | | | Siulak dialect |
