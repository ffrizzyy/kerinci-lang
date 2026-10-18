# Lesson 10: Working with text

Text is much like a list of letters. Many list tools work on text too.

## Letter by letter

```krc
barang kata = "kerinci"
nyetak kata[0]
nyetak kata[panjang(kata) - 1]
nyetak panjang(kata)
nyetak pulang(kata)
nyetak isi(kata, "rin")
nyetak isi(kata, "xyz")
```

```hasil
k
i
7
icnirek
betul
salah
```

Text cannot be changed letter by letter. Make a new text instead:

```krc-error
barang kata = "abc"
kata[0] = "x"
```

```hasil
Kesalahan: Teks tidak bisa diubah per huruf
```

## `pisah`: breaking text apart

`pisah(text, separator)` breaks a text into a list.

```krc
nyetak pisah("a,b,c", ",")
nyetak pisah("a,,b", ",")
nyetak pisah("a--b--c", "--")
nyetak pisah("abc", "")
```

```hasil
["a", "b", "c"]
["a", "", "b"]
["a", "b", "c"]
["a", "b", "c"]
```

Without a separator, `pisah` breaks at spaces and drops empty pieces, which is perfect for splitting a sentence into words.

```krc
nyetak pisah("belajar   bahasa kerinci")
```

```hasil
["belajar", "bahasa", "kerinci"]
```

## `disatu`: joining a list

`disatu(list, separator)` is the opposite of `pisah`: it joins the items of a list into one text.

```krc
nyetak disatu(["a", "b", "c"], "-")
nyetak disatu([1, 2, 3], ", ")
nyetak disatu(["a", "b"])
nyetak disatu(pisah("a b c"), "_")
```

```hasil
a-b-c
1, 2, 3
ab
a_b_c
```

## Example: playing with a sentence

```krc
barang kalimat = "belajar bahasa pemrograman kerinci"
barang kata_kata = pisah(kalimat)

nyetak "Jumlah kata: " + panjang(kata_kata)
nyetak "Terbalik: " + disatu(pulang(kata_kata), " ")
nyetak "Terurut: " + disatu(milih(kata_kata), ", ")
```

```hasil
Jumlah kata: 4
Terbalik: kerinci pemrograman bahasa belajar
Terurut: bahasa, belajar, kerinci, pemrograman
```

## Example: counting vowels

```krc
barang vokal = "aiueo"
barang jumlah = 0
untuk huruf alem "pemrograman kerinci" {
    kalu isi(vokal, huruf) {
        jumlah = jumlah + 1
    }
}
nyetak "Jumlah huruf hidup: " + jumlah
```

```hasil
Jumlah huruf hidup: 7
```

## Example: palindromes

A palindrome reads the same forwards and backwards.

```krc
guno palindrom(kata) {
    balik kata samo pulang(kata)
}

nyetak palindrom("katak")
nyetak palindrom("kerinci")
```

```hasil
betul
salah
```

## Example: data separated by punctuation

```krc
barang data = "Budi,80;Sari,92;Dewi,65"
barang nilai = {}
untuk pasangan alem pisah(data, ";") {
    barang bagian = pisah(pasangan, ",")
    nilai[bagian[0]] = bilangan(bagian[1])
}
nyetak nilai
```

```hasil
{"Budi": 80, "Sari": 92, "Dewi": 65}
```

## Summary

- Text can be indexed (`t[0]`), measured (`panjang`), reversed (`pulang`) and searched (`isi`).
- `pisah` breaks text into a list; `disatu` joins a list into text.
- Text cannot be changed letter by letter.

## Exercises

1. Count the words in "saya belajar bahasa kerinci hari ini".
2. Make a function `kabar_palindrom(kata)` that prints "palindrom" or "bukan" (not one) for "malam" and "kerinci".
3. Turn "a,b,c" into "a-b-c".

Answers: [answers.md](answers.md#lesson-10). Continue to [Lesson 11](11-files.md).
