# Lesson 12: Handling errors

Programs can run into errors beyond our control: the user types "abc" when a number was asked for, a file is missing, a divisor is zero. Without handling, the program simply stops. With `cubo` and `tangkap` you can prepare a backup plan.

## `cubo` and `tangkap`

`cubo` means "try", and `tangkap` means "catch". The body of `cubo { }` is tried. If there is an error, the rest of it is skipped and `tangkap { }` runs. The error message is kept in a barang that you name.

```krc
cubo {
    nyetak 10 / 0
    nyetak "tidak sampai sini"
} tangkap pesan {
    nyetak "Terjadi kesalahan: " + pesan
}
nyetak "Program tetap lanjut"
```

```hasil
Terjadi kesalahan: Pembagian dengan nol
Program tetap lanjut
```

If there is no error, `tangkap` is skipped:

```krc
cubo {
    nyetak "semuanya baik"
} tangkap pesan {
    nyetak "tidak akan tercetak"
}
```

```hasil
semuanya baik
```

The message name may be left out if you do not need it: `tangkap { ... }`. But `tangkap` is required after `cubo`:

```krc-error
cubo {
    nyetak 1
}
```

```hasil
Kesalahan: Baris 1: blok 'cubo' harus diikuti 'tangkap' dan blok penanganan
```

## Asking again after wrong input

```krc masukan=abc|dua|25
barang umur = kosong
selamo umur samo kosong {
    nyetak "Berapa umurmu?"
    cubo {
        umur = bilangan(tanyo())
    } tangkap {
        nyetak "Itu bukan bilangan, coba lagi."
    }
}
nyetak "Umurmu " + umur
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
guno ke_bilangan(teks) {
    cubo {
        balik bilangan(teks)
    } tangkap {
        balik kosong
    }
}

nyetak ke_bilangan("42")
nyetak ke_bilangan("abc")
```

```hasil
42
kosong
```

`balik`, `putuh` and `lanjut` work normally inside `cubo`.

## A file that might not exist

```krc
barang isi_berkas = ""
cubo {
    isi_berkas = baco("tidak-ada.txt")
} tangkap {
    isi_berkas = "(berkas belum ada)"
}
nyetak isi_berkas
```

```hasil
(berkas belum ada)
```

## `ngangkat`: making your own error

`ngangkat` means "raise": it signals an error with a message of your own. This is useful inside functions to reject values that make no sense.

```krc
guno bagi_aman(a, b) {
    kalu b samo 0 { ngangkat "pembagi tidak boleh nol" }
    balik a / b
}

cubo {
    nyetak bagi_aman(10, 2)
    nyetak bagi_aman(1, 0)
    nyetak "tidak sampai sini"
} tangkap pesan {
    nyetak "Gagal: " + pesan
}
```

```hasil
5
Gagal: pembagi tidak boleh nol
```

If no `tangkap` catches it, the error stops the program, with your message as the explanation:

```krc-error
nyetak "Mulai"
ngangkat "Aduh, ada yang salah"
nyetak "Tidak dicetak"
```

```hasil
Mulai
Kesalahan: Aduh, ada yang salah
```

## Catching and passing on

Inside `tangkap`, you may `ngangkat` again to pass the error on to an outer catcher.

```krc
cubo {
    cubo {
        ngangkat "kesalahan dalam"
    } tangkap pesan {
        nyetak "Ditangkap di dalam: " + pesan
        ngangkat "dikirim ulang: " + pesan
    }
} tangkap pesan {
    nyetak "Ditangkap di luar: " + pesan
}
```

```hasil
Ditangkap di dalam: kesalahan dalam
Ditangkap di luar: dikirim ulang: kesalahan dalam
```

## What can and cannot be caught

- Can be caught: every error that happens while the program runs (division by zero, a missing file, a missing map key, a failed conversion, `ngangkat`, recursion that is too deep).
- Cannot be caught: mistakes in how the program is written (for example an unclosed parenthesis), because then the program never starts running.

## Summary

- `cubo { ... } tangkap message { ... }` tries, then catches.
- `ngangkat "message"` raises an error.
- The body of `tangkap` may `ngangkat` again.

## Exercises

1. Divide two numbers and print "tidak bisa dibagi nol" (cannot divide by zero) when the divisor is 0.
2. Make a function `periksa_umur(umur)` ("check age") that raises an error when the age is negative.
3. Read a file that might not exist and print "kosong" (empty) if it does not.

Answers: [answers.md](answers.md#lesson-12). Continue to [Lesson 13](13-project.md).
