# Lesson 10: Working with text

Text is much like a list of letters. Many list tools work on text too.

## Letter by letter

```krc
# dialek: koto-payang
netakka_variabel kata = "kerinci"
nytak kata[0]
nytak kata[panja(kata) - 1]
nytak panja(kata)
nytak tebaluik(kata)
nytak contains(kata, "rin")
nytak contains(kata, "xyz")
```

```hasil
k
i
7
icnirek
betiu
salah
```

Text cannot be changed letter by letter. Make a new text instead:

```krc-error
# dialek: koto-payang
netakka_variabel kata = "abc"
kata[0] = "x"
```

```hasil
Kesalahan: Tulisan nyendak diubuah per huruf
```

## `pecah`: breaking text apart

`pecah(text, separator)` breaks a text into a list.

```krc
# dialek: koto-payang
nytak pecah("a,b,c", ",")
nytak pecah("a,,b", ",")
nytak pecah("a--b--c", "--")
nytak pecah("abc", "")
```

```hasil
["a", "b", "c"]
["a", "", "b"]
["a", "b", "c"]
["a", "b", "c"]
```

Without a separator, `pecah` breaks at spaces and drops empty pieces, which is perfect for splitting a sentence into words.

```krc
# dialek: koto-payang
nytak pecah("belajar   bahasa kerinci")
```

```hasil
["belajar", "bahasa", "kerinci"]
```

## `basatau`: joining a list

`basatau(list, separator)` is the opposite of `pecah`: it joins the items of a list into one text.

```krc
# dialek: koto-payang
nytak basatau(["a", "b", "c"], "-")
nytak basatau([1, 2, 3], ", ")
nytak basatau(["a", "b"])
nytak basatau(pecah("a b c"), "_")
```

```hasil
a-b-c
1, 2, 3
ab
a_b_c
```

## Example: playing with a sentence

```krc
# dialek: koto-payang
netakka_variabel kalimat = "belajar bahasa pemrograman kerinci"
netakka_variabel kata_kata = pecah(kalimat)

nytak "Jumlah kata: " + panja(kata_kata)
nytak "Terbalik: " + basatau(tebaluik(kata_kata), " ")
nytak "Terurut: " + basatau(terurut(kata_kata), ", ")
```

```hasil
Jumlah kata: 4
Terbalik: kerinci pemrograman bahasa belajar
Terurut: bahasa, belajar, kerinci, pemrograman
```

## Example: counting vowels

```krc
# dialek: koto-payang
netakka_variabel vokal = "aiueo"
netakka_variabel jumlah = 0
ndik huruf daling "pemrograman kerinci" {
    kalu contains(vokal, huruf) {
        jumlah = jumlah + 1
    }
}
nytak "Jumlah huruf hidup: " + jumlah
```

```hasil
Jumlah huruf hidup: 7
```

## Example: palindromes

A palindrome reads the same forwards and backwards.

```krc
# dialek: koto-payang
jeloehka palindrom(kata) {
    baluikka kata samu_dinga tebaluik(kata)
}

nytak palindrom("katak")
nytak palindrom("kerinci")
```

```hasil
betiu
salah
```

## Example: data separated by punctuation

```krc
# dialek: koto-payang
netakka_variabel data = "Budi,80;Sari,92;Dewi,65"
netakka_variabel nilai = {}
ndik pasangan daling pecah(data, ";") {
    netakka_variabel bagian = pecah(pasangan, ",")
    nilai[bagian[0]] = bilangan_buluak(bagian[1])
}
nytak nilai
```

```hasil
{"Budi": 80, "Sari": 92, "Dewi": 65}
```

## Summary

- Text can be indexed (`t[0]`), measured (`panja`), reversed (`tebaluik`) and searched (`contains`).
- `pecah` breaks text into a list; `basatau` joins a list into text.
- Text cannot be changed letter by letter.

## Exercises

1. Count the words in "saya belajar bahasa kerinci hari ini".
2. Make a function `kabar_palindrom(kata)` that prints "palindrom" or "bukan" (not one) for "malam" and "kerinci".
3. Turn "a,b,c" into "a-b-c".

Answers: [answers.md](answers.md#lesson-10). Continue to [Lesson 11](11-files.md).

---
*Generated from the Siulak lesson. Code and inline code use Koto Payang
(status: review).*
