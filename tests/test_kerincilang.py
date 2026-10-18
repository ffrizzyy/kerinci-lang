"""Run with: python3 tests/test_kerincilang.py"""
import contextlib
import io
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kerincilang import run_source, run_file, close_all_files, LangError, KEYWORDS, MAX_CALL_DEPTH  # noqa: E402
import tempfile  # noqa: E402


def output_of(src):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        run_source(src)
    return buf.getvalue()


OK_CASES = [
    ("ngangkat caught", r'cubo { ngangkat "rusak" } tangkap e { nyetak "tertangkap: " + e }', "tertangkap: rusak\n"),
    ("ngangkat number", r'cubo { ngangkat 42 } tangkap e { nyetak e }', "42\n"),
    ("ngangkat expression", r'cubo { ngangkat "kode " + 7 } tangkap e { nyetak e }', "kode 7\n"),
    ("ngangkat in function", r'guno periksa(x) { kalu x lebih_daripado 10 { ngangkat "terlalu besar" } balik x } cubo { nyetak periksa(5) nyetak periksa(50) } tangkap e { nyetak e }', "5\nterlalu besar\n"),
    ("ngangkat rethrow", r'cubo { cubo { ngangkat "a" } tangkap e { ngangkat e + "b" } } tangkap e { nyetak e }', "ab\n"),
    ("ngangkat stops function", r'guno f() { ngangkat "x" nyetak "tidak" } cubo { f() } tangkap { nyetak "ok" }', "ok\n"),
    ("tangkap without name", r'cubo { ngangkat "x" } tangkap { nyetak "ok" }', "ok\n"),
    ("pisah comma",   'nyetak pisah("a,b,c", ",")',                   '["a", "b", "c"]\n'),
    ("pisah spaces",  'nyetak pisah("  satu  dua tiga ")',            '["satu", "dua", "tiga"]\n'),
    ("pisah keeps empty", 'nyetak pisah("a,,b", ",")',                '["a", "", "b"]\n'),
    ("pisah chars",   'nyetak pisah("abc", "")',                      '["a", "b", "c"]\n'),
    ("pisah long separator", 'nyetak pisah("a--b--c", "--")',         '["a", "b", "c"]\n'),
    ("pisah lines",   r'nyetak pisah("a\nb\nc", "\n")',               '["a", "b", "c"]\n'),
    ("disatu",        'nyetak disatu(["a", "b", "c"], ", ")',         "a, b, c\n"),
    ("disatu default", 'nyetak disatu(["a", "b"])',                   "ab\n"),
    ("disatu numbers", 'nyetak disatu([1, 2, 3], "-")',               "1-2-3\n"),
    ("disatu empty",  'nyetak panjang(disatu([], ","))',              "0\n"),
    ("pisah disatu roundtrip", 'nyetak disatu(pisah("a b c"), "_")',  "a_b_c\n"),
    ("reverse words", 'nyetak disatu(pulang(pisah("satu dua tiga")), " ")', "tiga dua satu\n"),
    ("sort words",    'nyetak disatu(milih(pisah("pisang apel jeruk")), ", ")', "apel, jeruk, pisang\n"),
    ("kelihu catches",  r'cubo { nyetak 1 / 0 } tangkap e { nyetak "gagal: " + e }', "gagal: Pembagian dengan nol\n"),
    ("kelihu no error", r'cubo { nyetak "ok" } tangkap e { nyetak "gagal" }', "ok\n"),
    ("kelihu no name",  r'cubo { nyetak x } tangkap { nyetak "gagal" }', "gagal\n"),
    ("kelihu nested",   r'cubo { cubo { nyetak 1 / 0 } tangkap { nyetak "dalam" } nyetak "lanjut" } tangkap { nyetak "luar" }', "dalam\nlanjut\n"),
    ("kelihu handler fails", r'cubo { cubo { nyetak 1 / 0 } tangkap { nyetak x } } tangkap e { nyetak "luar" }', "luar\n"),
    ("kelihu return",   r'guno f() { cubo { balik 1 } tangkap { balik 2 } } nyetak f()', "1\n"),
    ("kelihu break",    r'selamo betul { cubo { putuh } tangkap { } } nyetak "selesai"', "selesai\n"),
    ("kelihu conversion", r'cubo { nyetak bilangan("abc") } tangkap e { nyetak e }', 'Tidak bisa mengubah "abc" menjadi bilangan\n'),
    ("kelihu missing key", r'barang p = {} cubo { nyetak p["a"] } tangkap e { nyetak e }', 'Kunci tidak ditemukan: "a"\n'),
    ("kelihu keeps effects", r'barang n = 0 cubo { n = 1 nyetak 1 / 0 } tangkap { } nyetak n', "1\n"),
    ("kelihu in loop",  r'untuk i alem [1, 0, 2] { cubo { nyetak 10 / i } tangkap { nyetak "nol" } }', "10\nnol\n5\n"),
    ("kelihu infinite recursion", r'guno f() { balik f() } cubo { f() } tangkap e { nyetak "terlalu dalam" } nyetak "hidup"', "terlalu dalam\nhidup\n"),
    ("recursion depth 50", r'guno jumlah(n) { kalu n samo 0 { balik 0 } balik n + jumlah(n - 1) } nyetak jumlah(50)', "1275\n"),
    ("recursion deep",  r'guno jumlah(n) { kalu n samo 0 { balik 0 } balik n + jumlah(n - 1) } nyetak jumlah(%d)' % (MAX_CALL_DEPTH - 20),
                        "%d\n" % sum(range(MAX_CALL_DEPTH - 19))),
    ("escape newline", r'nyetak "a\nb"', "a\nb\n"),
    ("escape tab",     r'nyetak "a\tb"', "a\tb\n"),
    ("escape quote",   r'nyetak "kata \"kutip\""', 'kata "kutip"\n'),
    ("escape backslash", r'nyetak "garis \\ miring"', "garis \\ miring\n"),
    ("escape length",  r'nyetak panjang("a\nb")', "3\n"),
    ("nantik",         "nyetak nantik(0.01)", "kosong\n"),
    ("nantik int",     "nantik(0) nyetak 1", "1\n"),
    ("bilangan text",  'nyetak bilangan("42") + 1',            "43\n"),
    ("bilangan spaces", 'nyetak bilangan(" 7 ")',               "7\n"),
    ("bilangan float", "nyetak bilangan(3.7)",                  "3\n"),
    ("bilangan negative", "nyetak bilangan(0 - 3.7)",           "-3\n"),
    ("bilangan int",   "nyetak bilangan(5)",                    "5\n"),
    ("pecahan text",   'nyetak pecahan("2.5") * 2',             "5.0\n"),
    ("pecahan int",    "nyetak pecahan(3)",                     "3.0\n"),
    ("kato number",    'nyetak kato(12) + kato(betul)',         "12betul\n"),
    ("kato list",      'nyetak kato([1, "a"])',                 '[1, "a"]\n'),
    ("mecem all types", 'nyetak mecem(1) nyetak mecem(1.5) nyetak mecem("a") nyetak mecem([]) nyetak mecem({}) nyetak mecem(kosong) nyetak mecem(betul) nyetak mecem(panjang)',
                        "bilangan\npecahan\nkato\ndaftar\npeta\nkosong\nboolean\nguno\n"),
    ("mecem compare",  'kalu mecem("a") samo "kato" { nyetak 1 }', "1\n"),
    ("convert input style", 'barang umur = bilangan("20") nyetak umur + 1', "21\n"),
    ("peta print",     'nyetak {"a": 1, "b": 2}',               '{"a": 1, "b": 2}\n'),
    ("peta empty",     "nyetak {}",                             "{}\n"),
    ("peta get",       'barang p = {"a": 1} nyetak p["a"]',     "1\n"),
    ("peta set new",   'barang p = {} p["x"] = 5 nyetak p',     '{"x": 5}\n'),
    ("peta update",    'barang p = {"a": 1} p["a"] = 2 nyetak p["a"]', "2\n"),
    ("peta number key", 'barang p = {1: "satu"} nyetak p[1]',   "satu\n"),
    ("peta iterate",   'barang p = {"a": 1, "b": 2} untuk k alem p { nyetak k + "=" + p[k] }', "a=1\nb=2\n"),
    ("peta panjang",   'nyetak panjang({"a": 1, "b": 2})',      "2\n"),
    ("peta isi",       'barang p = {"a": 1} nyetak isi(p, "a") ngan idak isi(p, "z")', "betul\n"),
    ("peta nested set", 'barang p = {"l": [1, 2]} p["l"][0] = 9 nyetak p', '{"l": [9, 2]}\n'),
    ("peta in list",   'nyetak [{"a": 1}]',                     '[{"a": 1}]\n'),
    ("peta falsy",     "kalu {} { nyetak 1 } lain { nyetak 2 }", "2\n"),
    ("peta builtin",   'nyetak peta(["a", 1], ["b", 2])',       '{"a": 1, "b": 2}\n'),
    ("peta builtin empty", "nyetak peta()",                     "{}\n"),
    ("peta trailing comma", 'nyetak {"a": 1,}',                 '{"a": 1}\n'),
    ("peta equality",  'nyetak {"a": 1} samo {"a": 1}',         "betul\n"),
    ("peta shared",    'barang a = {} barang b = a b["k"] = 1 nyetak a', '{"k": 1}\n'),
    ("peta in function", 'guno f() { balik {"x": 1} } nyetak f()["x"]', "1\n"),
    ("pilih match",    'pilih 2 { kalu 1 { nyetak "satu" } kalu 2 { nyetak "dua" } lain { nyetak "lain" } }', "dua\n"),
    ("pilih default",  'pilih 9 { kalu 1 { nyetak "satu" } lain { nyetak "lain" } }', "lain\n"),
    ("pilih no match", 'pilih 9 { kalu 1 { nyetak "satu" } } nyetak "selesai"', "selesai\n"),
    ("pilih many values", 'pilih "sabtu" { kalu "sabtu", "minggu" { nyetak "libur" } lain { nyetak "kerja" } }', "libur\n"),
    ("pilih no fallthrough", 'pilih 1 { kalu 1 { nyetak "a" } kalu 1 { nyetak "b" } }', "a\n"),
    ("pilih in loop",  "untuk i alem jarak(4) { pilih i { kalu 1 { lanjut } kalu 3 { putuh } lain { nyetak i } } }", "0\n2\n"),
    ("pilih mulai/habih", 'pilih 1 mulai kalu 1 mulai nyetak "ok" habih habih', "ok\n"),
    ("pilih return",   'guno f(x) { pilih x { kalu 1 { balik "satu" } lain { balik "lain" } } } nyetak f(1)', "satu\n"),
    ("pilih text",     'pilih "b" { kalu "a" { nyetak 1 } kalu "b" { nyetak 2 } }', "2\n"),
    ("pilih expression", 'barang x = 5 pilih x * 2 { kalu 10 { nyetak "sepuluh" } }', "sepuluh\n"),
    ("jarak 1",        "nyetak jarak(4)",                      "[0, 1, 2, 3]\n"),
    ("jarak 2",        "nyetak jarak(2, 5)",                   "[2, 3, 4]\n"),
    ("jarak step",     "nyetak jarak(0, 10, 3)",               "[0, 3, 6, 9]\n"),
    ("jarak descending", "nyetak jarak(3, 0, 0 - 1)",           "[3, 2, 1]\n"),
    ("jarak empty",    "nyetak jarak(0)",                      "[]\n"),
    ("untuk alem jarak", "barang t = 0 untuk i alem jarak(1, 5) { t = t + i } nyetak t", "10\n"),
    ("nambahkah",      "barang x = [1] nambahkah(x, 2) nyetak x", "[1, 2]\n"),
    ("nambahkah returns kosong", "barang x = [] nyetak nambahkah(x, 1)", "kosong\n"),
    ("nambahkah in loop", "barang x = [] untuk i alem jarak(3) { nambahkah(x, i * i) } nyetak x", "[0, 1, 4]\n"),
    ("isi list",       "nyetak isi([1, 2, 3], 2) ngan idak isi([1, 2, 3], 9)", "betul\n"),
    ("isi text",       'nyetak isi("halo", "al")',             "betul\n"),
    ("milih numbers",  "nyetak milih([3, 1, 2])",              "[1, 2, 3]\n"),
    ("milih text",     'nyetak milih(["b", "a"])',             '["a", "b"]\n'),
    ("milih keeps original", "barang x = [2, 1] barang y = milih(x) nyetak x", "[2, 1]\n"),
    ("pulang list",    "nyetak pulang([1, 2, 3])",             "[3, 2, 1]\n"),
    ("pulang text",    'nyetak pulang("abc")',                 "cba\n"),
    ("pulang keeps original", "barang x = [1, 2] barang y = pulang(x) nyetak x", "[1, 2]\n"),
    ("list print",      "nyetak [1, 2, 3]",                     "[1, 2, 3]\n"),
    ("list quoting",    'nyetak ["a", betul, kosong]',          '["a", betul, kosong]\n'),
    ("empty list",      "nyetak []",                            "[]\n"),
    ("trailing comma",  "nyetak [1, 2,]",                       "[1, 2]\n"),
    ("index",           "barang x = [10, 20, 30] nyetak x[1]",  "20\n"),
    ("index expr",      "barang x = [10, 20, 30] barang i = 1 nyetak x[i + 1]", "30\n"),
    ("nested list",     "barang m = [[1, 2], [3, 4]] nyetak m[1][0]", "3\n"),
    ("index assign",    "barang x = [1, 2] x[0] = 9 nyetak x",  "[9, 2]\n"),
    ("string index",    'nyetak "halo"[1]',                     "a\n"),
    ("panjang",         'nyetak panjang([1, 2, 3]) + panjang("abcd")', "7\n"),
    ("list concat",     "nyetak [1] + [2, 3]",                  "[1, 2, 3]\n"),
    ("daftar builtin",  "nyetak daftar(1, 2) samo [1, 2]",      "betul\n"),
    ("shared reference", "barang a = [1] barang b = a b[0] = 9 nyetak a", "[9]\n"),
    ("empty list falsy", "kalu [] { nyetak 1 } lain { nyetak 2 }", "2\n"),
    ("const list mutable", "tetap x = [1] x[0] = 5 nyetak x",  "[5]\n"),
    ("untuk list",      "untuk x alem [1, 2, 3] { nyetak x * 2 }",   "2\n4\n6\n"),
    ("untuk number",    "untuk i alem jarak(3) { nyetak i }",               "0\n1\n2\n"),
    ("untuk string",    'untuk c alem "ab" { nyetak c }',            "a\nb\n"),
    ("untuk break/continue", "untuk i alem jarak(10) { kalu i samo 2 { lanjut } kalu i samo 4 { putuh } nyetak i }", "0\n1\n3\n"),
    ("untuk sum",       "barang jumlah = 0 untuk x alem [1, 2, 3, 4] { jumlah = jumlah + x } nyetak jumlah", "10\n"),
    ("untuk panjang",   'barang x = ["a", "b"] untuk i alem jarak(panjang(x)) { nyetak x[i] }', "a\nb\n"),
    ("list in function", "guno ganda(xs) { barang hasil = [] untuk x alem xs { hasil = hasil + [x * 2] } balik hasil } nyetak ganda([1, 2, 3])", "[2, 4, 6]\n"),
    ("tambah",          "nyetak tambah(2, 3)",                  "5\n"),
    ("kurang kali",     "nyetak kurang(5, 2) + kali(2, 3)",     "9\n"),
    ("bagi exact",      "nyetak bagi(6, 2)",                    "3\n"),
    ("bagi fraction",   "nyetak bagi(7, 2)",                    "3.5\n"),
    ("division exact",  "nyetak 6 / 3",                         "2\n"),
    ("shadow builtin",  "guno panjang(x) { balik 99 } nyetak panjang([1])", "99\n"),
    ("show builtin",    "nyetak panjang",                       "<guno panjang>\n"),
    ("precedence",      "nyetak 1 + 2 * 3",                     "7\n"),
    ("parentheses",     "nyetak (1 + 2) * 3",                   "9\n"),
    ("string concat",   'nyetak "umur " + 5',                   "umur 5\n"),
    ("booleans",        "nyetak betul ngan salah",                "salah\n"),
    ("or",              "nyetak salah apo betul",                 "betul\n"),
    ("not",             "nyetak idak salah",                   "betul\n"),
    ("null",            "nyetak kosong",                        "kosong\n"),
    ("else",            "kalu salah { nyetak 1 } lain { nyetak 2 }", "2\n"),
    ("lain kalu",       "kalu salah { nyetak 1 } lain kalu betul { nyetak 2 } lain { nyetak 3 }", "2\n"),
    ("lain kalu chain", "barang n = 5 kalu n < 3 { nyetak 1 } lain kalu n < 6 { nyetak 2 } lain kalu n < 9 { nyetak 3 } lain { nyetak 4 }", "2\n"),
    ("word compare",    "nyetak 5 lebih_daripado 3 ngan 2 kurang_daripado 4", "betul\n"),
    ("word equal",      "nyetak 3 samo 3 ngan 3 dak_samo 4", "betul\n"),
    ("word >= <=",      "nyetak 3 lebih_samo 3 ngan 3 kurang_samo 3", "betul\n"),
    ("arithmetic words are names", "guno tambah(a, b) { balik a + b } barang kurang = 1 nyetak tambah(2, 3) + kurang", "6\n"),
    ("while",           "barang i = 0 selamo i < 3 { nyetak i i = i + 1 }", "0\n1\n2\n"),
    ("break/continue",  "barang i = 0 selamo i < 9 { i = i + 1 kalu i == 2 { lanjut } kalu i == 4 { putuh } nyetak i }", "1\n3\n"),
    ("function",        "guno kali(a, b) { balik a * b } nyetak kali(6, 7)", "42\n"),
    ("recursion",       "guno f(n) { kalu n <= 1 { balik 1 } balik n * f(n - 1) } nyetak f(5)", "120\n"),
    ("closure",         "guno buat() { barang n = 0 guno tambah() { n = n + 1 balik n } balik tambah } barang c = buat() c() nyetak c()", "2\n"),
    ("bare return",     "guno f() { balik } nyetak f()",         "kosong\n"),
    ("const read",      "tetap pi = 3 nyetak pi",                "3\n"),
    ("unicode name",    "barang naïve = 1 nyetak naïve",         "1\n"),
    ("mulai/habih",    "kalu betul mulai nyetak 1 habih lain mulai nyetak 2 habih", "1\n"),
    ("comment",         "# komentar\nnyetak 1",                  "1\n"),
]

ERROR_CASES = [
    ("ngangkat uncaught", 'ngangkat "boom"'),
    ("ngangkat without value", "ngangkat"),
    ("old kelihu syntax", "kelihu { nyetak 1 } lain { }"),
    ("stray tangkap", "tangkap { }"),
    ("pisah number", "nyetak pisah(5)"),
    ("pisah bad separator", 'nyetak pisah("a", 1)'),
    ("pisah no args", "nyetak pisah()"),
    ("disatu not list", 'nyetak disatu("abc")'),
    ("disatu bad separator", 'nyetak disatu(["a"], 1)'),
    ("kelihu without lain", "cubo { nyetak 1 }"),
    ("kelihu name out of scope", r'cubo { nyetak 1 / 0 } tangkap e { } nyetak e'),
    ("kelihu block var out of scope", r'cubo { barang z = 1 } tangkap { } nyetak z'),
    ("unknown escape",  r'nyetak "a\q"'),
    ("infinite recursion", "guno f() { balik f() } f()"),
    ("nantik negative", "nantik(0 - 1)"),
    ("nantik text",     'nantik("a")'),
    ("nantik too long", "nantik(7200)"),
    ("nantik bool",     "nantik(betul)"),
    ("bukak bad mode",  'bukak("x.txt", "xyz")'),
    ("bukak mode not text", 'bukak("x.txt", 5)'),
    ("bukak path not text", "bukak(5)"),
    ("bukak no args",   "bukak()"),
    ("bukak missing",   'bukak("/tidak/ada/sama/sekali.txt")'),
    ("baco missing",    'baco("/tidak/ada/sama/sekali.txt")'),
    ("hapus missing",   'hapus("/tidak/ada/sama/sekali.txt")'),
    ("hapus not text",  "hapus(5)"),
    ("tutup not file",  "tutup(5)"),
    ("baco number",     "baco(5)"),
    ("bilangan abc",   'nyetak bilangan("abc")'),
    ("bilangan decimal text", 'nyetak bilangan("3.5")'),
    ("bilangan bool",  "nyetak bilangan(betul)"),
    ("bilangan list",  "nyetak bilangan([1])"),
    ("pecahan abc",    'nyetak pecahan("x")'),
    ("pecahan null",   "nyetak pecahan(kosong)"),
    ("mecem no args",  "nyetak mecem()"),
    ("peta missing key", 'barang p = {} nyetak p["a"]'),
    ("peta list key",  "barang p = {} p[[1]] = 2"),
    ("peta literal list key", "nyetak {[1]: 2}"),
    ("peta float key", "nyetak {1.5: 1}"),
    ("peta missing colon", 'nyetak {"a" 1}'),
    ("peta + peta",    "nyetak {} + {}"),
    ("peta bad pair",  "nyetak peta(1)"),
    ("peta pair length", "nyetak peta([1, 2, 3])"),
    ("pilih missing brace", "pilih 1 kalu 1 { }"),
    ("pilih bad content", "pilih 1 { nyetak 1 }"),
    ("balik outside function", "balik 1"),
    ("balik in loop only", "selamo betul { balik 1 }"),
    ("jarak step 0",   "nyetak jarak(0, 5, 0)"),
    ("jarak float",    "nyetak jarak(1.5)"),
    ("jarak no args",  "nyetak jarak()"),
    ("jarak 4 args",   "nyetak jarak(1, 2, 3, 4)"),
    ("jarak too big",  "nyetak jarak(10000000)"),
    ("untuk without alem", "untuk x [1] { }"),
    ("untuk over number", "untuk i alem 5 { }"),
    ("alem as a name", "barang alem = 1"),
    ("nambahkah non-list", "nambahkah(5, 1)"),
    ("isi on number",  "nyetak isi(5, 1)"),
    ("isi text with number", 'nyetak isi("abc", 1)'),
    ("milih mixed",    'nyetak milih([1, "a"])'),
    ("milih non-list", "nyetak milih(5)"),
    ("pulang number",  "nyetak pulang(5)"),
    ("index out of range", "barang x = [1] nyetak x[1]"),
    ("negative index",  "barang x = [1] nyetak x[0 - 1]"),
    ("index not int",   'barang x = [1] nyetak x["a"]'),
    ("index non-list",  "barang n = 5 nyetak n[0]"),
    ("string assign",   'barang s = "ab" s[0] = "x"'),
    ("panjang number",  "nyetak panjang(5)"),
    ("builtin arg count", "nyetak panjang(1, 2)"),
    ("untuk non-iterable", "untuk x alem betul { nyetak x }"),
    ("untuk var scope", "untuk i alem jarak(2) { } nyetak i"),
    ("bad assign target", "5 = 3"),
    ("list + number",   "nyetak [1] + 1"),
    ("minus on text",   'nyetak -"a"'),
    ("undefined",       "nyetak x"),
    ("undeclared",      "x = 1"),
    ("const assign",    "tetap a = 1 a = 2"),
    ("div zero",        "nyetak 1 / 0"),
    ("bad arg count",   "guno f(a) { balik a } f(1, 2)"),
    ("not a function",  "barang a = 1 a()"),
    ("break outside",   "putuh"),
    ("reserved kelihu", "barang kelihu = 1"),
    ("bad character",   "nyetak @"),
    ("missing brace",   "kalu betul { nyetak 1"),
    ("type error",      'nyetak "a" - 1'),
]

failed = 0
for name, src, expected in OK_CASES:
    try:
        got = output_of(src)
    except Exception as e:
        got = f"EXCEPTION {e!r}"
    ok = got == expected
    failed += not ok
    print("PASS" if ok else "FAIL", name, "" if ok else f"-> {got!r}")

for name, src in ERROR_CASES:
    try:
        output_of(src)
        print("FAIL", name, "(no error raised)")
        failed += 1
    except LangError as e:
        print("PASS", name, f"[{e}]")

# ---- imports (ambik): each case is (name, {filename: source}, main file, expected output or None for error)
IMPORT_CASES = [
    ("import functions and constants",
     {"alat.krc": 'guno kuadrat(x) { balik x * x }\ntetap versi = "1.0"\nbarang rahasia = 5\nguno lihat() { balik rahasia }'},
     'ambik "alat"\nnyetak kuadrat(4)\nnyetak versi\nnyetak lihat()', "16\n1.0\n5\n"),
    ("import with extension",
     {"a.krc": "barang x = 7"}, 'ambik "a.krc" nyetak x', "7\n"),
    ("import runs once",
     {"m.krc": 'nyetak "dimuat"'}, 'ambik "m" ambik "m" nyetak "selesai"', "dimuat\nselesai\n"),
    ("import from subfolder",
     {"sub/b.krc": 'ambik "c"\nguno dua() { balik tiga() + 1 }', "sub/c.krc": "guno tiga() { balik 3 }"},
     'ambik "sub/b" nyetak dua()', "4\n"),
    ("imported constant stays constant",
     {"k.krc": "tetap pi = 3"}, 'ambik "k" pi = 4', None),
    ("import missing file",  {}, 'ambik "tidak_ada"', None),
    ("import not text",      {}, "ambik 5", None),
    ("import circular",
     {"x.krc": 'ambik "y"', "y.krc": 'ambik "x"'}, 'ambik "x"', None),
    ("error inside module",
     {"rusak.krc": "nyetak tidakAda"}, 'ambik "rusak"', None),
]

import_failed = 0
for name, files, main_src, expected in IMPORT_CASES:
    with tempfile.TemporaryDirectory() as tmp:
        for rel, content in files.items():
            path = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        main_path = os.path.join(tmp, "utama.krc")
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(main_src)
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                run_file(main_path)
            got, error = buf.getvalue(), None
        except LangError as e:
            got, error = None, str(e)
    if expected is None:
        ok = error is not None
        print("PASS" if ok else "FAIL", "import:", name, f"[{error}]" if ok else "(no error raised)")
    else:
        ok = got == expected and error is None
        print("PASS" if ok else "FAIL", "import:", name, "" if ok else f"-> {got!r} {error}")
    import_failed += not ok
failed += import_failed

# ---- files: @P@ in the source is replaced by a path inside a temporary folder
FILE_CASES = [
    ("write and read by name",
     r'tulis("@P@/a.txt", "halo") nyetak baco("@P@/a.txt")', "halo\n"),
    ("write handle then read handle",
     r'barang f = bukak("@P@/a.txt", "tulis") tulis(f, "satu\ndua\n") tutup(f) barang g = bukak("@P@/a.txt") nyetak baco(g) tutup(g)',
     "satu\ndua\n\n"),
    ("default mode is baco",
     r'tulis("@P@/a.txt", "x") barang g = bukak("@P@/a.txt") nyetak baco(g)', "x\n"),
    ("append mode",
     r'barang f = bukak("@P@/a.txt", "nambahkah") tulis(f, "a") tutup(f) barang g = bukak("@P@/a.txt", "nambahkah") tulis(g, "b") tutup(g) nyetak baco("@P@/a.txt")',
     "ab\n"),
    ("write mode replaces",
     r'tulis("@P@/a.txt", "lama") barang f = bukak("@P@/a.txt", "tulis") tulis(f, "baru") tutup(f) nyetak baco("@P@/a.txt")',
     "baru\n"),
    ("loop over lines",
     r'tulis("@P@/a.txt", "satu\ndua\ntiga\n") barang f = bukak("@P@/a.txt") untuk b alem f { nyetak "> " + b } tutup(f)',
     "> satu\n> dua\n> tiga\n"),
    ("last line without newline",
     r'tulis("@P@/a.txt", "satu\ndua") untuk b alem bukak("@P@/a.txt") { nyetak b }', "satu\ndua\n"),
    ("count lines",
     r'tulis("@P@/a.txt", "a\nb\nc\n") barang n = 0 untuk b alem bukak("@P@/a.txt") { n = n + 1 } nyetak n', "3\n"),
    ("write numbers and lists",
     r'tulis("@P@/a.txt", 42) nyetak baco("@P@/a.txt") tulis("@P@/a.txt", [1, "a"]) nyetak baco("@P@/a.txt")',
     '42\n[1, "a"]\n'),
    ("unicode round trip",
     r'tulis("@P@/a.txt", "bahasa Kerinci: é ñ 日本") nyetak baco("@P@/a.txt")', "bahasa Kerinci: é ñ 日本\n"),
    ("empty file",
     r'tulis("@P@/a.txt", "") nyetak panjang(baco("@P@/a.txt"))', "0\n"),
    ("read twice gives empty second time",
     r'tulis("@P@/a.txt", "x") barang f = bukak("@P@/a.txt") nyetak baco(f) nyetak panjang(baco(f))', "x\n0\n"),
    ("tutup twice is fine",
     r'barang f = bukak("@P@/a.txt", "tulis") tutup(f) tutup(f) nyetak "ok"', "ok\n"),
    ("hapus then missing",
     r'tulis("@P@/a.txt", "x") hapus("@P@/a.txt") cubo { baco("@P@/a.txt") nyetak "ada" } tangkap { nyetak "hilang" }', "hilang\n"),
    ("mecem file",
     r'nyetak mecem(bukak("@P@/a.txt", "tulis"))', "berkas\n"),
    ("file error message",
     r'cubo { baco("@P@/tidak-ada.txt") } tangkap e { nyetak panjang(e) > 10 }', "betul\n"),
    ("list of lines into a peta",
     r'tulis("@P@/d.txt", "a=1\nb=2\n") barang p = {} untuk b alem bukak("@P@/d.txt") { p[b] = panjang(b) } nyetak p',
     '{"a=1": 3, "b=2": 3}\n'),
    ("write in a loop",
     r'barang f = bukak("@P@/a.txt", "tulis") untuk i alem jarak(1, 4) { tulis(f, kato(i) + "\n") } tutup(f) nyetak baco("@P@/a.txt")',
     "1\n2\n3\n\n"),
    ("files closed at program end",
     r'barang f = bukak("@P@/a.txt", "tulis") tulis(f, "tersimpan")', ""),
]
FILE_ERRORS = [
    ("read from write handle",   r'barang f = bukak("@P@/a.txt", "tulis") baco(f)'),
    ("write to read handle",     r'tulis("@P@/a.txt", "x") barang f = bukak("@P@/a.txt") tulis(f, "y")'),
    ("use closed handle",        r'barang f = bukak("@P@/a.txt", "tulis") tutup(f) tulis(f, "x")'),
    ("loop over closed handle",  r'tulis("@P@/a.txt", "x") barang f = bukak("@P@/a.txt") tutup(f) untuk b alem f { }'),
    ("loop over write handle",   r'barang f = bukak("@P@/a.txt", "tulis") untuk b alem f { }'),
    ("open a folder",            r'baco("@P@")'),
    ("delete a folder",          r'hapus("@P@")'),
    ("write into missing folder", r'tulis("@P@/tidak/ada/a.txt", "x")'),
]

file_failed = 0
for name, src, expected in FILE_CASES:
    with tempfile.TemporaryDirectory() as tmp:
        folder = tmp.replace("\\", "/")
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                run_source(src.replace("@P@", folder))
            got = buf.getvalue()
        except Exception as e:
            got = f"EXCEPTION {e!r}"
        finally:
            close_all_files()
        if name == "files closed at program end":
            run_file_path = os.path.join(tmp, "p.krc")
            with open(run_file_path, "w", encoding="utf-8") as f:
                f.write(src.replace("@P@", folder))
            run_file(run_file_path)          # run_file closes files when the program ends
            with open(os.path.join(tmp, "a.txt"), encoding="utf-8") as f:
                got = f.read() if True else got
            expected = "tersimpan"
    ok = got == expected
    file_failed += not ok
    print("PASS" if ok else "FAIL", "file:", name, "" if ok else f"-> {got!r}")
for name, src in FILE_ERRORS:
    with tempfile.TemporaryDirectory() as tmp:
        folder = tmp.replace("\\", "/")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                run_source(src.replace("@P@", folder))
            print("FAIL", "file:", name, "(no error raised)")
            file_failed += 1
        except LangError as e:
            print("PASS", "file:", name, f"[{e.args[0].replace(folder, '<tmp>')}]")
        finally:
            close_all_files()
failed += file_failed

print("\nKeywords unique:", len(set(KEYWORDS.values())) == len(KEYWORDS))
print("FAILED:" if failed else "ALL PASSED", failed or "")
sys.exit(1 if failed else 0)
