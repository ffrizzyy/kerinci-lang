"""Writes the glossary in two languages from the table below:

  tutorial/glossary.md        English (main)
  tutorial/id/glosarium.md    Indonesian

The script stops with an error if a keyword, built-in function, or comparison word in
kerincilang.py is missing from the table, so the glossary cannot fall out of date.
    python3 tools/buat_glosarium.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import kerincilang  # noqa: E402

# (Kerinci word, Indonesian meaning, English meaning, example)
KEYWORDS = [
    ("barang", "variabel: wadah bernama untuk menyimpan nilai", "variable: a named container that stores a value", "barang umur = 20"),
    ("tetap", "konstanta: barang yang tidak boleh diubah", "constant: a variable that cannot be changed", "tetap pi = 3.14"),
    ("guno", "membuat fungsi", "function: define your own function", "guno kuadrat(x) { balik x * x }"),
    ("balik", "mengembalikan hasil dari fungsi", "return: send a result back from a function", "balik x * x"),
    ("kalu", "jika (percabangan)", "if", "kalu x > 5 { ... }"),
    ("lain", "kalau tidak; `lain kalu` = jika lainnya", "else; `lain kalu` = else if", "kalu x > 5 { ... } lain { ... }"),
    ("selamo", "perulangan selama syarat benar", "while: repeat as long as a condition is true", "selamo i < 10 { ... }"),
    ("untuk", "perulangan untuk setiap anggota", "for: repeat for every item", "untuk x alem daftar { ... }"),
    ("alem", "dalam (dipakai bersama `untuk`)", "in (used with `untuk`)", "untuk x alem daftar { ... }"),
    ("putuh", "menghentikan perulangan", "break: leave a loop immediately", "kalu i > 7 { putuh }"),
    ("lanjut", "lompat ke putaran berikutnya", "continue: skip to the next round of a loop", "kalu i % 2 samo 0 { lanjut }"),
    ("nyetak", "mencetak nilai", "print", 'nyetak "Halo"'),
    ("tanyo", "membaca masukan pengguna (selalu teks)", "input: read what the user types (always text)", "barang nama = tanyo()"),
    ("betul", "benar", "true", "barang ok = betul"),
    ("salah", "salah", "false", "barang ok = salah"),
    ("kosong", "tidak ada nilai", "null: no value", "barang x = kosong"),
    ("ngan", "dan", "and", "kalu a > 1 ngan b > 1 { ... }"),
    ("apo", "atau", "or", "kalu a > 1 apo b > 1 { ... }"),
    ("idak", "bukan", "not", "kalu idak ok { ... }"),
    ("mulai", "awal blok, sama dengan `{`", "begin a block, same as `{`", "kalu betul mulai ... habih"),
    ("habih", "akhir blok, sama dengan `}`", "end a block, same as `}`", "kalu betul mulai ... habih"),
    ("pilih", "memilih satu cabang dari banyak", "switch: choose one branch out of many", 'pilih hari { kalu 1 { ... } lain { ... } }'),
    ("ambik", "mengambil (memuat) berkas program lain", "import: load another program file", 'ambik "perkakas"'),
    ("cubo", "mencoba blok yang mungkin gagal", "try: run a block that might fail", "cubo { ... } tangkap pesan { ... }"),
    ("tangkap", "menangani kesalahan dari `cubo`", "catch: handle an error from `cubo`", "cubo { ... } tangkap pesan { ... }"),
    ("ngangkat", "memunculkan kesalahan dengan pesan", "raise: signal an error with a message", 'ngangkat "pesan"'),
]
COMPARISONS = [
    ("samo", "sama dengan", "equal to", "==", "kalu a samo b { ... }"),
    ("dak_samo", "tidak sama dengan", "not equal to", "!=", "kalu a dak_samo b { ... }"),
    ("lebih_daripado", "lebih besar dari", "greater than", ">", "kalu a lebih_daripado b { ... }"),
    ("kurang_daripado", "lebih kecil dari", "less than", "<", "kalu a kurang_daripado b { ... }"),
    ("lebih_samo", "lebih besar atau sama", "greater than or equal to", ">=", "kalu a lebih_samo b { ... }"),
    ("kurang_samo", "lebih kecil atau sama", "less than or equal to", "<=", "kalu a kurang_samo b { ... }"),
]
FUNCTIONS = [
    ("daftar", "membuat daftar dari nilai-nilai", "list: build a list from values", "daftar(1, 2, 3)"),
    ("peta", "membuat peta (kunci dan nilai)", "map / dictionary: build a map from pairs", 'peta(["a", 1], ["b", 2])'),
    ("panjang", "jumlah anggota daftar, peta, atau huruf dalam teks", "length: number of items in a list or map, or letters in a text", 'panjang("kerinci")'),
    ("jarak", "daftar bilangan berurutan", "range: a list of consecutive numbers", "jarak(1, 6)"),
    ("nambahkah", "menambah anggota di ujung daftar", "append: add an item at the end of a list", 'nambahkah(daftar, "x")'),
    ("isi", "memeriksa apakah ada di dalam daftar, peta (kunci), atau teks", "contains: is it in the list, map (as a key), or text?", 'isi(daftar, "x")'),
    ("milih", "salinan daftar yang terurut", "sort: a sorted copy of a list", "milih([3, 1, 2])"),
    ("pulang", "salinan daftar atau teks yang terbalik", "reverse: a reversed copy of a list or text", 'pulang("abc")'),
    ("pisah", "memecah teks menjadi daftar", "split: break a text into a list", 'pisah("a,b", ",")'),
    ("disatu", "menyatukan daftar menjadi teks", "join: join a list into one text", 'disatu(["a", "b"], "-")'),
    ("bilangan", "mengubah menjadi bilangan bulat", "integer: convert to a whole number", 'bilangan("42")'),
    ("pecahan", "mengubah menjadi bilangan desimal", "decimal: convert to a decimal number", 'pecahan("2.5")'),
    ("kato", "mengubah menjadi teks", "string: convert to text", "kato(12)"),
    ("mecem", "menyebut jenis nilai", "type: name the type of a value", 'mecem("a")'),
    ("tambah", "penjumlahan sebagai fungsi", "add, as a function", "tambah(2, 3)"),
    ("kurang", "pengurangan sebagai fungsi", "subtract, as a function", "kurang(5, 2)"),
    ("kali", "perkalian sebagai fungsi", "multiply, as a function", "kali(2, 3)"),
    ("bagi", "pembagian sebagai fungsi", "divide, as a function", "bagi(7, 2)"),
    ("bukak", "membuka berkas", "open a file", 'bukak("a.txt", "tulis")'),
    ("baco", "membaca seluruh isi berkas; juga mode `\"baco\"`", "read a whole file; also the file mode `\"baco\"`", 'baco("a.txt")'),
    ("tulis", "menulis ke berkas; juga mode `\"tulis\"`", "write to a file; also the file mode `\"tulis\"`", 'tulis("a.txt", "isi")'),
    ("tutup", "menutup berkas", "close a file", "tutup(f)"),
    ("hapus", "menghapus berkas", "delete a file", 'hapus("a.txt")'),
    ("nantik", "menunggu sekian detik", "wait for some seconds", "nantik(2)"),
]
RESERVED = [("kelihu", "kesalahan (disimpan untuk fitur berikutnya)", "error (held back for a future feature)")]

# (message as the interpreter prints it, English meaning)  [the messages are in Indonesian for now]
MESSAGES = [
    ("Kesalahan: ...", "Error: ... (every error message starts like this)"),
    ("Baris N: ...", "Line N: ..."),
    ("Dalam 'modul': ...", "In 'module': ... (the error happened inside an imported file)"),
    ("Nama belum didefinisikan: x", "Name not defined: x (you used a variable that does not exist)"),
    ("Nama belum dideklarasikan: x (pakai 'barang' dulu)", "Name not declared: x (create it with 'barang' first)"),
    ("'x' adalah konstanta ('tetap') dan tidak bisa diubah", "'x' is a constant and cannot be changed"),
    ("Pembagian dengan nol", "Division by zero"),
    ("Operator '-' tidak bisa dipakai pada \"a\" dan 1", "Operator '-' cannot be used on \"a\" and 1"),
    ("Tidak bisa mengubah \"abc\" menjadi bilangan", "Cannot convert \"abc\" to a whole number"),
    ("Indeks di luar jangkauan: 5 (panjang 2)", "Index out of range: 5 (length 2)"),
    ("Indeks harus bilangan bulat", "The index must be a whole number"),
    ("Kunci tidak ditemukan: \"k\"", "Key not found: \"k\" (in a map)"),
    ("Kunci peta harus teks atau bilangan bulat", "Map keys must be text or whole numbers"),
    ("Teks tidak bisa diubah per huruf", "Text cannot be changed letter by letter"),
    ("Fungsi butuh 2 argumen, diberi 1", "The function needs 2 arguments, given 1"),
    ("Yang dipanggil bukan fungsi", "What you called is not a function"),
    ("Panggilan fungsi terlalu dalam (lebih dari 400)...", "Function calls nested too deeply (more than 400)... (a function probably calls itself forever)"),
    ("Berkas tidak ditemukan: nama", "File not found: nama"),
    ("Berkas sudah ditutup: nama", "File already closed: nama"),
    ("Berkas ini dibuka untuk 'tulis', tidak bisa dipakai oleh 'baco'", "This file was opened for 'tulis', so 'baco' cannot use it"),
    ("Baris N: karakter tidak dikenal '\"'", "Line N: unrecognised character '\"' (often a missing closing quote)"),
    ("Baris N: tidak terduga ''", "Line N: unexpected '' (something is missing, such as a value after `nyetak`)"),
    ("Baris N: diharapkan '}', ditemukan ''", "Line N: expected '}', found '' (a block was not closed)"),
    ("Baris N: 'balik' hanya boleh di dalam fungsi", "Line N: 'balik' is only allowed inside a function"),
    ("Baris N: 'putuh' hanya boleh di dalam perulangan", "Line N: 'putuh' is only allowed inside a loop"),
    ("Baris N: blok 'cubo' harus diikuti 'tangkap' dan blok penanganan", "Line N: a 'cubo' block must be followed by 'tangkap' and a handler block"),
    ("Impor melingkar: x", "Circular import: x (two files import each other)"),
]

# ---- the glossary must cover everything in the language
covered = {k[0] for k in KEYWORDS} | {c[0] for c in COMPARISONS} | {f[0] for f in FUNCTIONS} | {r[0] for r in RESERVED}
needed = set(kerincilang.KEYWORDS.values()) | set(kerincilang.WORD_OPERATORS) | set(kerincilang.BUILTINS) | set(kerincilang.RESERVED)
if needed - covered:
    sys.exit("The glossary is missing: " + ", ".join(sorted(needed - covered)))
if covered - needed:
    sys.exit("The glossary has words that are not in the language: " + ", ".join(sorted(covered - needed)))


def build(lang):
    en = lang == "en"
    t = (lambda e, i: e if en else i)
    contrib = "../CONTRIBUTING.md" if en else "../../CONTRIBUTING.md"
    out = [t("# Glossary", "# Glosarium"), "",
           t("Every KerinciLang word in Kerinci (Siulak dialect), with its meaning in English and Indonesian. "
             "The meaning column explains **how the word is used in the programming language**. For the meaning, spelling and everyday "
             f"use of a word in Kerinci itself, the speakers decide; see [CONTRIBUTING.md]({contrib}).",
             "Semua kata KerinciLang dalam bahasa Kerinci (dialek Siulak), dengan arti dalam bahasa Indonesia dan Inggris. "
             "Kolom arti menjelaskan **cara kata itu dipakai dalam bahasa pemrograman**. Untuk makna, ejaan, dan pemakaian "
             f"sehari-hari dalam bahasa Kerinci, penuturlah yang menentukan. Lihat [CONTRIBUTING.md]({contrib})."), "",
           t("## Special words (cannot be used as variable names)", "## Kata khusus (tidak boleh dipakai sebagai nama barang)"), "",
           t("| Kerinci | Meaning | Indonesian | Example |", "| Kerinci | Arti | English | Contoh |"), "|---|---|---|---|"]
    for k, i, e, x in KEYWORDS:
        out.append(f"| `{k}` | {e if en else i} | {i if en else e} | `{x}` |")
    out += ["", t("## Comparison words", "## Kata perbandingan"), "",
            t("Exactly the same as their symbols, and the two styles can be mixed.", "Sama persis dengan simbolnya, dan boleh dicampur."), "",
            t("| Kerinci | Meaning | Indonesian | Symbol | Example |", "| Kerinci | Arti | English | Simbol | Contoh |"), "|---|---|---|---|---|"]
    for k, i, e, s, x in COMPARISONS:
        out.append(f"| `{k}` | {e if en else i} | {i if en else e} | `{s}` | `{x}` |")
    out += ["", t("## Built-in functions", "## Fungsi bawaan"), "",
            t("These are ordinary names, not special words, so you may create your own variable or function with the same name; yours is used in your program.",
              "Ini nama biasa, bukan kata khusus, jadi kamu boleh membuat barang atau fungsi dengan nama yang sama; milikmu akan dipakai di programmu."), "",
            t("| Kerinci | Meaning | Indonesian | Example |", "| Kerinci | Arti | English | Contoh |"), "|---|---|---|---|"]
    for k, i, e, x in FUNCTIONS:
        out.append(f"| `{k}` | {e if en else i} | {i if en else e} | `{x}` |")
    out += ["", t("## Reserved words", "## Kata yang dicadangkan"), "",
            t("Not used yet, but they cannot be used as names, so that programs do not break in a later version.",
              "Belum dipakai, tetapi tidak boleh dipakai sebagai nama supaya program tidak rusak di versi berikutnya."), "",
            t("| Kerinci | Meaning | Indonesian |", "| Kerinci | Arti | English |"), "|---|---|---|"]
    for k, i, e in RESERVED:
        out.append(f"| `{k}` | {e if en else i} | {i if en else e} |")
    out += ["", t("## Type names returned by `mecem`", "## Nama jenis dari `mecem`"), "",
            t("| Value | `mecem` result |", "| Nilai | Hasil `mecem` |"), "|---|---|",
            t("| whole number | `bilangan` |", "| bilangan bulat | `bilangan` |"),
            t("| decimal number | `pecahan` |", "| desimal | `pecahan` |"),
            t("| text | `kato` |", "| teks | `kato` |"),
            "| " + t("list", "daftar") + " | `daftar` |",
            "| " + t("map", "peta") + " | `peta` |",
            "| " + t("function", "fungsi") + " | `guno` |",
            "| " + t("no value", "tidak ada nilai") + " | `kosong` |",
            "| " + t("open file", "berkas terbuka") + " | `berkas` |",
            t("| `betul` / `salah` | `boolean` (a temporary English word, waiting for a Kerinci word) |",
              "| `betul` / `salah` | `boolean` (kata sementara dari bahasa Inggris; menunggu kata Kerinci) |"), ""]
    if en:
        out += ["## Error messages", "",
                "The interpreter's messages are currently written in **Indonesian** (translating them into Kerinci is a task for speakers). "
                "Here is what the common ones mean. Words in `'quotes'` inside a message are KerinciLang words.", "",
                "| Message | Meaning |", "|---|---|"]
        for m, e in MESSAGES:
            out.append(f"| `{m}` | {e} |")
        out.append("")
    return "\n".join(out)


(ROOT / "tutorial" / "glossary.md").write_text(build("en"), encoding="utf-8")
languages = "English"
if (ROOT / "tutorial" / "id").is_dir():            # the Indonesian copy is optional
    (ROOT / "tutorial" / "id" / "glosarium.md").write_text(build("id"), encoding="utf-8")
    languages = "English + Indonesian"
print(f"glossary written ({languages}): {len(KEYWORDS)} special words, "
      f"{len(COMPARISONS)} comparisons, {len(FUNCTIONS)} functions")
