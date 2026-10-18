# Lesson 11: Files

So far, everything your program remembered disappeared when it finished. With **files** (*berkas*), a program can keep data on disk and read it again later.

## The quickest way: `tulis` and `baco`

```krc
tulis("catatan.txt", "Belajar KerinciLang\nHari ini membuat program\n")
nyetak baco("catatan.txt")
```

```hasil
Belajar KerinciLang
Hari ini membuat program
```

- `tulis(name, text)` creates a file, or **replaces all of its contents** if it already exists.
- `baco(name)` reads the whole file as one text.

## Opening a file: `bukak`, `tutup`

To write a little at a time, or to add at the end, open the file first with `bukak(name, mode)`. Finished? `tutup(file)`.

| Mode | Meaning |
|---|---|
| `"baco"` (default) | reading |
| `"tulis"` | writing from the start (old contents are lost) |
| `"nambahkah"` | writing at the end (old contents stay) |

```krc
barang f = bukak("log.txt", "tulis")
tulis(f, "baris 1\n")
tulis(f, "baris 2\n")
tutup(f)

barang g = bukak("log.txt", "nambahkah")
tulis(g, "baris 3\n")
tutup(g)

nyetak baco("log.txt")
```

```hasil
baris 1
baris 2
baris 3
```

Get into the habit of closing files with `tutup`, especially before reading them back. (A file you forget to close is closed automatically when the program ends.)

## Reading line by line

`untuk ... alem` on an opened file gives one line at a time, without its line-break mark.

```krc
tulis("data.txt", "satu\ndua\ntiga\n")
barang nomor = 1
untuk baris alem bukak("data.txt") {
    nyetak nomor + ". " + baris
    nomor = nomor + 1
}
```

```hasil
1. satu
2. dua
3. tiga
```

## Saving and loading a list

Combine this with `disatu` and `pisah` from Lesson 10:

```krc
barang buah = ["pisang", "apel", "jeruk"]
tulis("buah.txt", disatu(buah, "\n"))

barang dibaca = pisah(baco("buah.txt"), "\n")
nyetak dibaca
nyetak panjang(dibaca)
```

```hasil
["pisang", "apel", "jeruk"]
3
```

Careful: if a text ends with `\n`, `pisah(text, "\n")` gives one empty item at the end. For files that end with a line break, it is safer to use `untuk line alem bukak(...)`.

## Deleting a file

```krc
tulis("sementara.txt", "x")
hapus("sementara.txt")
nyetak "Terhapus"
```

```hasil
Terhapus
```

`hapus` only deletes files, not folders.

## When the file does not exist

```krc-error
nyetak baco("tidak-ada.txt")
```

```hasil
Kesalahan: Berkas tidak ditemukan: tidak-ada.txt
```

In [Lesson 12](12-errors.md) you will learn to handle this error so that the program does not stop.

## Important things

- Files are UTF-8 text.
- A file name is relative to the folder where the program is run. On Windows, write folder separators as `/` (`"data/nilai.txt"`) or doubled (`"data\\nilai.txt"`).
- `tulis(file, value)` also writes numbers and lists, looking the way `nyetak` shows them.
- A file can only be used while it is open. Using a file that has been closed is an error.

## Summary

- `tulis(name, text)` and `baco(name)` are the quick way.
- `bukak(name, mode)` with mode `"baco"`, `"tulis"` or `"nambahkah"`, then `tutup`.
- `untuk line alem bukak(name)` reads line by line.
- `hapus(name)` deletes a file.

## Exercises

1. Write three names to a file, one per line, then read and print them.
2. Count the number of lines in a file.
3. Add the numbers 1 to 5 to a file, one per line, using a loop, then print its contents.

Answers: [answers.md](answers.md#lesson-11). Continue to [Lesson 12](12-errors.md).
