# Lesson 11: Files

So far, everything your program remembered disappeared when it finished. With **files** (*berkas*), a program can keep data on disk and read it again later.

## The quickest way: `tulaih` and `bacea`

```krc
# dialek: koto-payang
tulaih("catatan.txt", "Belajar KerinciLang\nHari ini membuat program\n")
nytak bacea("catatan.txt")
```

```hasil
Belajar KerinciLang
Hari ini membuat program
```

- `tulaih(name, text)` creates a file, or **replaces all of its contents** if it already exists.
- `bacea(name)` reads the whole file as one text.

## Opening a file: `bukuak`, `tutamp`

To write a little at a time, or to add at the end, open the file first with `bukuak(name, mode)`. Finished? `tutamp(file)`.

| Mode | Meaning |
|---|---|
| `"baco"` (default) | reading |
| `"tulis"` | writing from the start (old contents are lost) |
| `"nambahkah"` | writing at the end (old contents stay) |

```krc
# dialek: koto-payang
netakka_variabel f = bukuak("log.txt", "tulaih")
tulaih(f, "baris 1\n")
tulaih(f, "baris 2\n")
tutamp(f)

netakka_variabel g = bukuak("log.txt", "tambah")
tulaih(g, "baris 3\n")
tutamp(g)

nytak bacea("log.txt")
```

```hasil
baris 1
baris 2
baris 3
```

Get into the habit of closing files with `tutamp`, especially before reading them back. (A file you forget to close is closed automatically when the program ends.)

## Reading line by line

`ndik ... daling` on an opened file gives one line at a time, without its line-break mark.

```krc
# dialek: koto-payang
tulaih("data.txt", "satu\ndua\ntiga\n")
netakka_variabel nomor = 1
ndik baris daling bukuak("data.txt") {
    nytak nomor + ". " + baris
    nomor = nomor + 1
}
```

```hasil
1. satu
2. dua
3. tiga
```

## Saving and loading a list

Combine this with `basatau` and `pecah` from Lesson 10:

```krc
# dialek: koto-payang
netakka_variabel buah = ["pisang", "apel", "jeruk"]
tulaih("buah.txt", basatau(buah, "\n"))

netakka_variabel dibaca = pecah(bacea("buah.txt"), "\n")
nytak dibaca
nytak panja(dibaca)
```

```hasil
["pisang", "apel", "jeruk"]
3
```

Careful: if a text ends with `\n`, `pecah(text, "\n")` gives one empty item at the end. For files that end with a line break, it is safer to use `ndik line daling bukuak(...)`.

## Deleting a file

```krc
# dialek: koto-payang
tulaih("sementara.txt", "x")
ngapih_berkas("sementara.txt")
nytak "Terhapus"
```

```hasil
Terhapus
```

`ngapih_berkas` only deletes files, not folders.

## When the file does not exist

```krc-error
# dialek: koto-payang
nytak bacea("tidak-ada.txt")
```

```hasil
Kesalahan: Sidiak besuao berkas: tidak-ada.txt
```

In [Lesson 12](12-errors.md) you will learn to handle this error so that the program does not stop.

## Important things

- Files are UTF-8 text.
- A file name is relative to the folder where the program is run. On Windows, write folder separators as `/` (`"data/nilai.txt"`) or doubled (`"data\\nilai.txt"`).
- `tulaih(file, value)` also writes numbers and lists, looking the way `nytak` shows them.
- A file can only be used while it is open. Using a file that has been closed is an error.

## Summary

- `tulaih(name, text)` and `bacea(name)` are the quick way.
- `bukuak(name, mode)` with mode `"baco"`, `"tulis"` or `"nambahkah"`, then `tutamp`.
- `ndik line daling bukuak(name)` reads line by line.
- `ngapih_berkas(name)` deletes a file.

## Exercises

1. Write three names to a file, one per line, then read and print them.
2. Count the number of lines in a file.
3. Add the numbers 1 to 5 to a file, one per line, using a loop, then print its contents.

Answers: [answers.md](answers.md#lesson-11). Continue to [Lesson 12](12-errors.md).

---
*Generated from the Siulak lesson. Code and inline code use Koto Payang
(status: review).*
