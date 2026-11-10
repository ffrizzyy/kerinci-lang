# Lesson 12: Handling errors

Programs can run into errors beyond our control: the user types "abc" when a number was asked for, a file is missing, a divisor is zero. Without handling, the program simply stops. With `cubea` and `kecuali` you can prepare a backup plan.

## `cubea` and `kecuali`

`cubea` means "try", and `kecuali` means "catch". The body of `cubea { }` is tried. If there is an error, the rest of it is skipped and `kecuali { }` runs. The error message is kept in a barang that you name.

```krc
# dialek: koto-payang
cubea {
    nytak 10 / 0
    nytak "tidak sampai sini"
} kecuali pesan {
    nytak "Terjadi kesalahan: " + pesan
}
nytak "Program tetap lanjut"
```

```hasil
Terjadi kesalahan: Pembagian dinga nol
Program tetap lanjut
```

If there is no error, `kecuali` is skipped:

```krc
# dialek: koto-payang
cubea {
    nytak "semuanya baik"
} kecuali pesan {
    nytak "tidak akan tercetak"
}
```

```hasil
semuanya baik
```

The message name may be left out if you do not need it: `kecuali { ... }`. But `kecuali` is required after `cubea`:

```krc-error
# dialek: koto-payang
cubea {
    nytak 1
}
```

```hasil
Kesalahan: Baris 2: blok 'cubea' harus dinga 'kecuali' nga blok penanganan
```

## Asking again after wrong input

```krc masukan=abc|dua|25
# dialek: koto-payang
netakka_variabel umur = kusao
selamu umur samu_dinga kusao {
    nytak "Berapa umurmu?"
    cubea {
        umur = bilangan_buluak(masukka())
    } kecuali {
        nytak "Itu bukan bilangan, coba lagi."
    }
}
nytak "Umurmu " + umur
```

```hasil
Berapa umurmu?
Itu bukan bilangan, coba lagi.
Berapa umurmu?
Itu bukan bilangan, coba lagi.
Berapa umurmu?
Umurmu 25
```

## Giving a fallback value

```krc
# dialek: koto-payang
jeloehka ke_bilangan(teks) {
    cubea {
        baluikka bilangan_buluak(teks)
    } kecuali {
        baluikka kusao
    }
}

nytak ke_bilangan("42")
nytak ke_bilangan("abc")
```

```hasil
42
kusao
```

`baluikka`, `slese` and `lanjutka` work normally inside `cubea`.

## A file that might not exist

```krc
# dialek: koto-payang
netakka_variabel isi_berkas = ""
cubea {
    isi_berkas = bacea("tidak-ada.txt")
} kecuali {
    isi_berkas = "(berkas belum ada)"
}
nytak isi_berkas
```

```hasil
(berkas belum ada)
```

## `timbaoka`: making your own error

`timbaoka` means "raise": it signals an error with a message of your own. This is useful inside functions to reject values that make no sense.

```krc
# dialek: koto-payang
jeloehka bagi_aman(a, b) {
    kalu b samu_dinga 0 { timbaoka "pembagi tidak boleh nol" }
    baluikka a / b
}

cubea {
    nytak bagi_aman(10, 2)
    nytak bagi_aman(1, 0)
    nytak "tidak sampai sini"
} kecuali pesan {
    nytak "Gagal: " + pesan
}
```

```hasil
5
Gagal: pembagi tidak boleh nol
```

If no `kecuali` catches it, the error stops the program, with your message as the explanation:

```krc-error
# dialek: koto-payang
nytak "Mulai"
timbaoka "Aduh, ada yang salah"
nytak "Tidak dicetak"
```

```hasil
Mulai
Kesalahan: Aduh, ada yang salah
```

## Catching and passing on

Inside `kecuali`, you may `timbaoka` again to pass the error on to an outer catcher.

```krc
# dialek: koto-payang
cubea {
    cubea {
        timbaoka "kesalahan dalam"
    } kecuali pesan {
        nytak "Ditangkap di dalam: " + pesan
        timbaoka "dikirim ulang: " + pesan
    }
} kecuali pesan {
    nytak "Ditangkap di luar: " + pesan
}
```

```hasil
Ditangkap di dalam: kesalahan dalam
Ditangkap di luar: dikirim ulang: kesalahan dalam
```

## What can and cannot be caught

- Can be caught: every error that happens while the program runs (division by zero, a missing file, a missing map key, a failed conversion, `timbaoka`, recursion that is too deep).
- Cannot be caught: mistakes in how the program is written (for example an unclosed parenthesis), because then the program never starts running.

## Summary

- `cubea { ... } kecuali message { ... }` tries, then catches.
- `timbaoka "message"` raises an error.
- The body of `kecuali` may `timbaoka` again.

## Exercises

1. Divide two numbers and print "tidak bisa dibagi nol" (cannot divide by zero) when the divisor is 0.
2. Make a function `periksa_umur(umur)` ("check age") that raises an error when the age is negative.
3. Read a file that might not exist and print "kosong" (empty) if it does not.

Answers: [answers.md](answers.md#lesson-12). Continue to [Lesson 13](13-project.md).

---
*Generated from the Siulak lesson. Code and inline code use Koto Payang
(status: approved).*
