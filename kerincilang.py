"""KerinciLang: interpreter with Siulak-Kerinci keywords.

Run a file:  krc contoh.krc        (or: python3 kerincilang.py contoh.krc)
Start REPL:  krc
"""
import os
import re
import sys
import time

__version__ = "0.5.0"

# Function calls nest deeply in this interpreter. Python 3.11+ can safely go deeper
# than its default limit; older versions stay conservative.
if sys.version_info >= (3, 11):
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 12000))
    MAX_CALL_DEPTH = 400
else:
    MAX_CALL_DEPTH = 80
CALL_DEPTH = [0]

# internal name -> Kerinci word (Siulak dialect). Edit only the right-hand side.
KEYWORDS = {
    "VAR": "barang",       # variable
    "CONST": "tetap",      # constant
    "FUNC": "guno",        # function
    "RETURN": "balik",
    "IF": "kalu",
    "ELSE": "lain",        # "lain kalu" = else if
    "WHILE": "selamo",
    "FOR": "untuk",
    "IN": "alem",          # untuk x alem xs { ... }
    "SWITCH": "pilih",     # pilih x { kalu 1 { } lain { } }
    "IMPORT": "ambik",     # ambik "berkas"
    "TRY": "cubo",         # cubo { ... } tangkap pesan { ... }
    "CATCH": "tangkap",
    "RAISE": "ngangkat",   # ngangkat "pesan"
    "BREAK": "putuh",
    "CONTINUE": "lanjut",
    "PRINT": "nyetak",
    "INPUT": "tanyo",
    "TRUE": "betul",
    "FALSE": "salah",
    "NULL": "kosong",
    "AND": "ngan",
    "OR": "apo",
    "NOT": "idak",
    "BEGIN": "mulai",      # same as {
    "END": "habih",        # same as }
}
SURFACE = {word: name for name, word in KEYWORDS.items()}
assert len(SURFACE) == len(KEYWORDS), "Two keywords share the same word"

# Word forms of the comparison operators. They mean exactly the same as the symbols.
# Arithmetic words (tambah, kurang, kali, bagi) are NOT operators: they are built-in
# functions, so they stay usable as ordinary names too.
# Set ENABLE_WORD_OPERATORS = False to free these words for names as well.
ENABLE_WORD_OPERATORS = True
WORD_OPERATORS = {
    "samo": "==",
    "dak_samo": "!=",
    "lebih_daripado": ">",
    "kurang_daripado": "<",
    "lebih_samo": ">=",
    "kurang_samo": "<=",
}
assert not set(WORD_OPERATORS) & set(SURFACE), "A word is both a keyword and an operator"

# reserved for later versions: using these as names is an error today
RESERVED = {"kelihu"}     # "error": held back for a future feature (error values)

# names returned by mecem(x). The table has no Kerinci word for "boolean" yet:
# "boolean" below is a PLACEHOLDER: replace it when speakers supply a word.
TYPE_NAMES = {
    "int": "bilangan", "float": "pecahan", "str": "kato", "list": "daftar",
    "map": "peta", "func": KEYWORDS["FUNC"], "null": KEYWORDS["NULL"],
    "bool": "boolean", "file": "berkas",
}

TOKEN_SPEC = [
    ("COMMENT", r"#[^\n]*"),
    ("NUMBER",  r"\d+(\.\d+)?"),
    ("STRING",  r'"(?:[^"\\\n]|\\.)*"'),
    ("IDENT",   r"[^\W\d]\w*"),          # any Unicode letter; underscores allowed
    ("OP",      r"==|!=|<=|>=|[+\-*/%<>=(){}\[\],:]"),
    ("SKIP",    r"[ \t\r\n]+"),
    ("BAD",     r"."),
]
MASTER = re.compile("|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPEC))

# tokens that begin a statement; used to decide whether `return` has a value
STATEMENT_STARTS = {"VAR", "CONST", "FUNC", "IF", "ELSE", "WHILE", "FOR", "SWITCH", "TRY", "RAISE",
                    "IMPORT", "BREAK", "CONTINUE", "RETURN", "PRINT"}


class LangError(Exception):
    pass


ESCAPES = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}


def unescape(raw, line):
    """Turn \n \t \" \\ inside a text literal into the real characters."""
    def replace(m):
        c = m.group(1)
        if c not in ESCAPES:
            raise LangError(f"Baris {line}: urutan escape tidak dikenal: \\{c}")
        return ESCAPES[c]
    return re.sub(r"\\(.)", replace, raw)


def tokenize(src):
    tokens, line = [], 1
    for m in MASTER.finditer(src):
        kind, text = m.lastgroup, m.group()
        if kind in ("SKIP", "COMMENT"):
            line += text.count("\n")
            continue
        if kind == "BAD":
            raise LangError(f"Baris {line}: karakter tidak dikenal {text!r}")
        if kind == "IDENT" and ENABLE_WORD_OPERATORS and text in WORD_OPERATORS:
            kind, text = "OP", WORD_OPERATORS[text]
        elif kind == "IDENT" and text in RESERVED:
            raise LangError(f"Baris {line}: '{text}' adalah kata cadangan untuk fitur berikutnya")
        elif kind == "IDENT" and text in SURFACE:
            kind = SURFACE[text]
            if kind == "BEGIN":              # mulai ... habih are braces in Kerinci
                kind, text = "OP", "{"
            elif kind == "END":
                kind, text = "OP", "}"
        tokens.append((kind, text, line))
    tokens.append(("EOF", "", line))
    return tokens


class Parser:
    def __init__(self, tokens):
        self.t, self.i, self.loop_depth, self.func_depth = tokens, 0, 0, 0

    def kind(self): return self.t[self.i][0]
    def text(self): return self.t[self.i][1]
    def line(self): return self.t[self.i][2]

    def advance(self):
        tok = self.t[self.i]
        self.i += 1
        return tok

    def match(self, *wanted):
        if self.kind() in wanted or (self.kind() == "OP" and self.text() in wanted):
            return self.advance()
        return None

    def expect(self, what):
        tok = self.match(what)
        if not tok:
            raise LangError(f"Baris {self.line()}: diharapkan {what!r}, ditemukan {self.text()!r}")
        return tok

    def program(self):
        stmts = []
        while self.kind() != "EOF":
            stmts.append(self.statement())
        return stmts

    def block(self):
        self.expect("{")
        stmts = []
        while self.text() != "}" and self.kind() != "EOF":
            stmts.append(self.statement())
        self.expect("}")
        return stmts

    def loop_body(self):
        self.loop_depth += 1
        body = self.block()
        self.loop_depth -= 1
        return body

    def if_stmt(self):
        self.advance()                       # IF
        cond, then, other = self.expression(), self.block(), []
        if self.match("ELSE"):               # "lain kalu ..." chains, plain "lain { }" ends
            other = [self.if_stmt()] if self.kind() == "IF" else self.block()
        return ("if", cond, then, other)

    def statement(self):
        k = self.kind()
        if k in ("VAR", "CONST"):
            self.advance()
            name = self.expect("IDENT")[1]
            self.expect("=")
            return ("var", name, self.expression(), k == "CONST")
        if k == "FUNC":
            self.advance()
            name = self.expect("IDENT")[1]
            self.expect("(")
            params = []
            if self.text() != ")":
                params.append(self.expect("IDENT")[1])
                while self.match(","):
                    params.append(self.expect("IDENT")[1])
            self.expect(")")
            saved, self.loop_depth = self.loop_depth, 0
            self.func_depth += 1
            body = self.block()
            self.func_depth -= 1
            self.loop_depth = saved
            return ("func", name, params, body)
        if k == "IF":
            return self.if_stmt()
        if k == "WHILE":
            self.advance()
            cond = self.expression()
            return ("while", cond, self.loop_body())
        if k == "FOR":                       # untuk <name> alem <list | text> { ... }
            self.advance()
            var = self.expect("IDENT")[1]
            if not self.match("IN"):
                raise LangError(f"Baris {self.line()}: diharapkan '{KEYWORDS['IN']}' setelah nama, "
                                f"ditemukan {self.text()!r}")
            source = self.expression()
            return ("for", var, source, self.loop_body())
        if k == "TRY":                       # cubo { ... } tangkap pesan { ... }
            line = self.advance()[2]
            body = self.block()
            if not self.match("CATCH"):
                raise LangError(f"Baris {line}: blok '{KEYWORDS['TRY']}' harus diikuti "
                                f"'{KEYWORDS['CATCH']}' dan blok penanganan")
            name = self.advance()[1] if self.kind() == "IDENT" else None
            return ("try", body, name, self.block())
        if k == "RAISE":                     # ngangkat "pesan"
            self.advance()
            return ("raise", self.expression())
        if k == "SWITCH":                    # pilih x { kalu 1, 2 { } lain { } }
            self.advance()
            subject = self.expression()
            self.expect("{")
            clauses, default = [], None
            while self.kind() == "IF":
                self.advance()
                values = [self.expression()]
                while self.match(","):
                    values.append(self.expression())
                clauses.append((values, self.block()))
            if self.match("ELSE"):
                default = self.block()
            self.expect("}")
            return ("switch", subject, clauses, default)
        if k == "IMPORT":                    # ambik "berkas"
            self.advance()
            return ("import", self.expression())
        if k in ("BREAK", "CONTINUE"):
            line = self.advance()[2]
            if self.loop_depth == 0:
                raise LangError(f"Baris {line}: '{KEYWORDS[k]}' hanya boleh di dalam perulangan")
            return (k.lower(),)
        if k == "RETURN":
            line = self.advance()[2]
            if self.func_depth == 0:
                raise LangError(f"Baris {line}: '{KEYWORDS['RETURN']}' hanya boleh di dalam fungsi")
            if self.text() == "}" or self.kind() in STATEMENT_STARTS or self.kind() == "EOF":
                return ("return", None)
            return ("return", self.expression())
        if k == "PRINT":
            self.advance()
            return ("print", self.expression())
        if k == "IDENT" and self.t[self.i + 1][:2] == ("OP", "="):
            name = self.advance()[1]
            self.advance()
            return ("assign", name, self.expression())
        line = self.line()
        expr = self.expression()
        if self.kind() == "OP" and self.text() == "=":       # xs[0] = value
            if expr[0] != "index":
                raise LangError(f"Baris {line}: sisi kiri '=' harus nama atau elemen daftar")
            self.advance()
            return ("setindex", expr[1], expr[2], self.expression())
        return ("expr", expr)

    def binary(self, sub, ops):
        left = sub()
        while self.kind() in ops or (self.kind() == "OP" and self.text() in ops):
            op = self.advance()[1]
            left = ("bin", op, left, sub())
        return left

    def expression(self): return self.binary(self.and_, ("OR",))
    def and_(self):       return self.binary(self.equality, ("AND",))
    def equality(self):   return self.binary(self.comparison, ("==", "!="))
    def comparison(self): return self.binary(self.term, ("<", ">", "<=", ">="))
    def term(self):       return self.binary(self.factor, ("+", "-"))
    def factor(self):     return self.binary(self.unary, ("*", "/", "%"))

    def unary(self):
        if self.match("NOT"):
            return ("not", self.unary())
        if self.match("-"):
            return ("neg", self.unary())
        return self.call()

    def call(self):
        expr = self.primary()
        while True:
            if self.match("("):
                args = []
                if self.text() != ")":
                    args.append(self.expression())
                    while self.match(","):
                        args.append(self.expression())
                self.expect(")")
                expr = ("call", expr, args)
            elif self.match("["):
                index = self.expression()
                self.expect("]")
                expr = ("index", expr, index)
            else:
                return expr

    def primary(self):
        kind, text, line = self.advance()
        if kind == "NUMBER": return ("lit", float(text) if "." in text else int(text))
        if kind == "STRING": return ("lit", unescape(text[1:-1], line))
        if kind == "TRUE":   return ("lit", True)
        if kind == "FALSE":  return ("lit", False)
        if kind == "NULL":   return ("lit", None)
        if kind == "INPUT":
            self.expect("(")
            self.expect(")")
            return ("input",)
        if kind == "IDENT":  return ("name", text)
        if kind == "OP" and text == "(":
            e = self.expression()
            self.expect(")")
            return e
        if kind == "OP" and text == "[":
            items = []
            while not (self.kind() == "OP" and self.text() == "]") and self.kind() != "EOF":
                items.append(self.expression())
                if not self.match(","):
                    break
            self.expect("]")
            return ("list", items)
        if kind == "OP" and text == "{":     # peta literal: { "kunci": nilai, ... }
            pairs = []
            while not (self.kind() == "OP" and self.text() == "}") and self.kind() != "EOF":
                key = self.expression()
                self.expect(":")
                pairs.append((key, self.expression()))
                if not self.match(","):
                    break
            self.expect("}")
            return ("map", pairs)
        raise LangError(f"Baris {line}: tidak terduga {text!r}")


class ReturnSignal(Exception):
    def __init__(self, value): self.value = value
class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass


class Env:
    def __init__(self, parent=None):
        self.vars, self.consts, self.parent = {}, set(), parent

    def lookup(self, name):
        env = self
        while env:
            if name in env.vars:
                return env
            env = env.parent
        return None

    def declare(self, name, value, const=False):
        if name in self.consts:
            raise LangError(f"'{name}' sudah dideklarasikan sebagai konstanta")
        self.vars[name] = value
        if const:
            self.consts.add(name)

    def get(self, name):
        env = self.lookup(name)
        if not env:
            raise LangError(f"Nama belum didefinisikan: {name}")
        return env.vars[name]

    def assign(self, name, value):
        env = self.lookup(name)
        if not env:
            raise LangError(f"Nama belum dideklarasikan: {name} (pakai '{KEYWORDS['VAR']}' dulu)")
        if name in env.consts:
            raise LangError(f"'{name}' adalah konstanta ('{KEYWORDS['CONST']}') dan tidak bisa diubah")
        env.vars[name] = value


def show(v, nested=False):
    if v is None:  return KEYWORDS["NULL"]
    if v is True:  return KEYWORDS["TRUE"]
    if v is False: return KEYWORDS["FALSE"]
    if isinstance(v, list):
        return "[" + ", ".join(show(x, True) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{show(k, True)}: {show(x, True)}" for k, x in v.items()) + "}"
    if isinstance(v, str) and nested:
        return f'"{v}"'
    if isinstance(v, Berkas):
        return f'<{TYPE_NAMES["file"]} "{v.path}">'
    if isinstance(v, tuple) and v and v[0] == "closure":
        return f"<{KEYWORDS['FUNC']}>"
    if isinstance(v, tuple) and v and v[0] == "builtin":
        return f"<{KEYWORDS['FUNC']} {v[1]}>"
    return str(v)


def binary_op(o, l, r):
    """Shared by operators (+ - * / ...) and the built-ins tambah/kurang/kali/bagi."""
    try:
        if o == "+":
            if isinstance(l, str) or isinstance(r, str):
                return show(l) + show(r)
            return l + r                                    # numbers add, lists join
        if o == "/":
            if isinstance(l, int) and isinstance(r, int) and r != 0 and l % r == 0:
                return l // r                               # 6 / 3 is 2, not 2.0
            return l / r
        return {"-": lambda: l - r, "*": lambda: l * r, "%": lambda: l % r,
                "==": lambda: l == r, "!=": lambda: l != r,
                "<": lambda: l < r, ">": lambda: l > r,
                "<=": lambda: l <= r, ">=": lambda: l >= r}[o]()
    except ZeroDivisionError:
        raise LangError("Pembagian dengan nol")
    except TypeError:
        raise LangError(f"Operator {o!r} tidak bisa dipakai pada {show(l, True)} dan {show(r, True)}")


def check_key(k):
    if isinstance(k, bool) or not isinstance(k, (str, int)):
        raise LangError("Kunci peta harus teks atau bilangan bulat")


def get_item(obj, idx):
    if isinstance(obj, dict):
        check_key(idx)
        if idx not in obj:
            raise LangError(f"Kunci tidak ditemukan: {show(idx, True)}")
        return obj[idx]
    check_index(obj, idx)
    return obj[idx]


def check_index(obj, idx):
    if not isinstance(obj, (list, str)):
        raise LangError("Hanya daftar, peta, dan teks yang bisa diindeks")
    if isinstance(idx, bool) or not isinstance(idx, int):
        raise LangError("Indeks harus bilangan bulat")
    if idx < 0 or idx >= len(obj):
        raise LangError(f"Indeks di luar jangkauan: {idx} (panjang {len(obj)})")


def iterate(v):
    if isinstance(v, Berkas):               # untuk baris alem berkas { ... } reads line by line
        need_handle(v, ("baco",), KEYWORDS["FOR"])
        return read_from(v.handle, v.path, as_lines=True)
    if isinstance(v, (list, str, dict)):
        return list(v)                      # a peta gives its keys
    if isinstance(v, int) and not isinstance(v, bool):
        raise LangError(f"Untuk mengulang beberapa kali, pakai jarak(n): "
                        f"{KEYWORDS['FOR']} i {KEYWORDS['IN']} jarak(5)")
    raise LangError(f"Nilai ini tidak bisa diulang dengan '{KEYWORDS['FOR']}'")


# ---- built-in functions: name -> (number of arguments or None for any, python function)
def b_panjang(x):
    if isinstance(x, (list, str, dict)):
        return len(x)
    raise LangError("'panjang' hanya untuk daftar, peta, dan teks")


MAX_JARAK = 1_000_000


def b_jarak(*args):
    if not 1 <= len(args) <= 3:
        raise LangError(f"Fungsi jarak butuh 1 sampai 3 argumen, diberi {len(args)}")
    if any(isinstance(a, bool) or not isinstance(a, int) for a in args):
        raise LangError("Argumen jarak harus bilangan bulat")
    if len(args) == 3 and args[2] == 0:
        raise LangError("Langkah jarak tidak boleh 0")
    r = range(*args)
    if len(r) > MAX_JARAK:
        raise LangError(f"Jarak terlalu besar (maksimal {MAX_JARAK})")
    return list(r)


def need_list(name, x):
    if not isinstance(x, list):
        raise LangError(f"'{name}' hanya untuk daftar")


def b_nambahkah(xs, value):
    need_list("nambahkah", xs)
    xs.append(value)                      # changes the list itself
    return None


def b_isi(container, item):
    if isinstance(container, dict):         # for a peta: is it a key?
        try:
            return item in container
        except TypeError:
            return False
    if isinstance(container, list):
        return item in container
    if isinstance(container, str):
        if not isinstance(item, str):
            raise LangError("Untuk mencari dalam teks, yang dicari juga harus teks")
        return item in container
    raise LangError("'isi' hanya untuk daftar, peta, dan teks")


def b_milih(xs):
    need_list("milih", xs)
    try:
        return sorted(xs)                 # returns a new list; the original is unchanged
    except TypeError:
        raise LangError("Daftar berisi nilai yang tidak bisa dibandingkan, jadi tidak bisa diurutkan")


def b_pulang(x):
    if isinstance(x, list):
        return x[::-1]                    # new list
    if isinstance(x, str):
        return x[::-1]
    raise LangError("'pulang' hanya untuk daftar dan teks")


def cannot_convert(x, target):
    raise LangError(f"Tidak bisa mengubah {show(x, True)} menjadi {target}")


def b_bilangan(x):
    if isinstance(x, bool):
        cannot_convert(x, "bilangan")
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        try:
            return int(x)                   # cuts off the decimals: 3.7 -> 3, -3.7 -> -3
        except (OverflowError, ValueError):
            cannot_convert(x, "bilangan")
    if isinstance(x, str) and re.fullmatch(r"\s*[+-]?[0-9]+\s*", x):
        return int(x)
    cannot_convert(x, "bilangan")


def b_pecahan(x):
    if isinstance(x, bool):
        cannot_convert(x, "pecahan")
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str) and re.fullmatch(r"\s*[+-]?[0-9]+(\.[0-9]+)?\s*", x):
        return float(x)
    cannot_convert(x, "pecahan")


def b_mecem(x):
    if x is None:                return TYPE_NAMES["null"]
    if isinstance(x, bool):      return TYPE_NAMES["bool"]
    if isinstance(x, int):       return TYPE_NAMES["int"]
    if isinstance(x, float):     return TYPE_NAMES["float"]
    if isinstance(x, str):       return TYPE_NAMES["str"]
    if isinstance(x, list):      return TYPE_NAMES["list"]
    if isinstance(x, dict):      return TYPE_NAMES["map"]
    if isinstance(x, Berkas):    return TYPE_NAMES["file"]
    return TYPE_NAMES["func"]


def b_peta(*pairs):
    result = {}
    for pair in pairs:
        if not (isinstance(pair, list) and len(pair) == 2):
            raise LangError("Setiap pasangan peta harus berupa daftar [kunci, nilai]")
        check_key(pair[0])
        result[pair[0]] = pair[1]
    return result


class Berkas:
    """An open file. Made by bukak(), used with baco / tulis, closed with tutup."""
    def __init__(self, path, mode, handle):
        self.path, self.mode, self.handle, self.closed = path, mode, handle, False


OPEN_FILES = []
MODES = {"baco": "r", "tulis": "w", "nambahkah": "a"}   # the mode is given as one of these words
MAX_NANTIK = 3600


def file_error(err, path):
    if isinstance(err, FileNotFoundError):
        return LangError(f"Berkas tidak ditemukan: {path}")
    if isinstance(err, PermissionError):
        return LangError(f"Tidak punya izin untuk berkas: {path}")
    if isinstance(err, IsADirectoryError):
        return LangError(f"Ini folder, bukan berkas: {path}")
    return LangError(f"Kesalahan berkas {path}: {err.strerror or err}")


def need_path(x, verb):
    if not isinstance(x, str):
        raise LangError(f"'{verb}' butuh nama berkas berupa teks")
    return x


def need_handle(x, allowed, verb):
    if not isinstance(x, Berkas):
        raise LangError(f"'{verb}' butuh berkas yang dibuka dengan bukak")
    if x.closed:
        raise LangError(f"Berkas sudah ditutup: {x.path}")
    if x.mode not in allowed:
        raise LangError(f"Berkas ini dibuka untuk '{x.mode}', tidak bisa dipakai oleh '{verb}'")
    return x


def close_all_files():
    for f in list(OPEN_FILES):
        try:
            f.handle.close()
        except OSError:
            pass
        f.closed = True
    OPEN_FILES.clear()


def b_bukak(*args):
    if not 1 <= len(args) <= 2:
        raise LangError(f"Fungsi bukak butuh 1 atau 2 argumen, diberi {len(args)}")
    path = need_path(args[0], "bukak")
    mode = args[1] if len(args) == 2 else "baco"
    if not isinstance(mode, str) or mode not in MODES:
        raise LangError('Mode harus "baco", "tulis", atau "nambahkah", bukan ' + show(mode, True))
    try:
        handle = open(path, MODES[mode], encoding="utf-8", newline=None if mode == "baco" else "\n")
    except OSError as err:
        raise file_error(err, path)
    f = Berkas(path, mode, handle)
    OPEN_FILES.append(f)
    return f


def read_from(handle, path, as_lines=False):
    try:
        if as_lines:
            return [line[:-1] if line.endswith("\n") else line for line in handle]
        return handle.read()
    except UnicodeDecodeError:
        raise LangError(f"Berkas bukan teks UTF-8: {path}")
    except OSError as err:
        raise file_error(err, path)


def b_baco(x):
    if isinstance(x, str):                       # baco("nama.txt") reads a whole file
        try:
            with open(x, encoding="utf-8") as handle:
                return read_from(handle, x)
        except OSError as err:
            raise file_error(err, x)
    need_handle(x, ("baco",), "baco")
    return read_from(x.handle, x.path)


def b_tulis(x, value):
    text = value if isinstance(value, str) else show(value)
    try:
        if isinstance(x, str):                   # tulis("nama.txt", teks) replaces the whole file
            with open(x, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
        else:
            need_handle(x, ("tulis", "nambahkah"), "tulis")
            x.handle.write(text)
    except OSError as err:
        raise file_error(err, x if isinstance(x, str) else x.path)
    return None


def b_tutup(x):
    if not isinstance(x, Berkas):
        raise LangError("'tutup' butuh berkas yang dibuka dengan bukak")
    if not x.closed:
        x.handle.close()
        x.closed = True
        if x in OPEN_FILES:
            OPEN_FILES.remove(x)
    return None


def b_hapus(path):
    need_path(path, "hapus")
    try:
        os.remove(path)
    except OSError as err:
        raise file_error(err, path)
    return None


def b_nantik(seconds):
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
        raise LangError("'nantik' butuh bilangan detik")
    if seconds < 0 or seconds > MAX_NANTIK:
        raise LangError(f"Waktu nantik harus antara 0 dan {MAX_NANTIK} detik")
    time.sleep(seconds)
    return None


def b_pisah(*args):
    if not 1 <= len(args) <= 2:
        raise LangError(f"Fungsi pisah butuh 1 atau 2 argumen, diberi {len(args)}")
    text = args[0]
    if not isinstance(text, str):
        raise LangError("'pisah' hanya untuk teks")
    if len(args) == 1:
        return text.split()                       # on any spaces; no empty pieces
    sep = args[1]
    if not isinstance(sep, str):
        raise LangError("Pemisah harus berupa teks")
    if sep == "":
        return list(text)                         # one piece per character
    return text.split(sep)


def b_disatu(*args):
    if not 1 <= len(args) <= 2:
        raise LangError(f"Fungsi disatu butuh 1 atau 2 argumen, diberi {len(args)}")
    need_list("disatu", args[0])
    sep = args[1] if len(args) == 2 else ""
    if not isinstance(sep, str):
        raise LangError("Pemisah harus berupa teks")
    return sep.join(show(x) for x in args[0])


BUILTINS = {
    "panjang": (1, b_panjang),
    "daftar":  (None, lambda *items: list(items)),
    "tambah":  (2, lambda a, b: binary_op("+", a, b)),
    "kurang":  (2, lambda a, b: binary_op("-", a, b)),
    "kali":    (2, lambda a, b: binary_op("*", a, b)),
    "bagi":    (2, lambda a, b: binary_op("/", a, b)),
    "jarak":     (None, b_jarak),      # jarak(5) = [0..4], jarak(2, 5) = [2..4], jarak(0, 10, 3)
    "nambahkah": (2, b_nambahkah),     # append (changes the list)
    "isi":       (2, b_isi),           # contains: isi(daftar_atau_teks, yang_dicari)
    "milih":     (1, b_milih),         # sort (new list)
    "pulang":    (1, b_pulang),        # reverse (new list or text)
    "bilangan":  (1, b_bilangan),      # to whole number: bilangan("42"), bilangan(3.7)
    "pecahan":   (1, b_pecahan),       # to decimal: pecahan("2.5")
    "kato":      (1, lambda x: show(x)),   # to text
    "mecem":     (1, b_mecem),         # type name of a value
    "peta":      (None, b_peta),       # peta() or peta(["a", 1], ["b", 2])
    "pisah":     (None, b_pisah),      # pisah("a,b", ",") = ["a", "b"]; pisah("a b") splits on spaces
    "disatu":    (None, b_disatu),     # disatu(["a", "b"], ", ") = "a, b"
    "bukak":     (None, b_bukak),      # bukak("a.txt") or bukak("a.txt", "tulis")
    "baco":      (1, b_baco),          # read a whole file (handle or name)
    "tulis":     (2, b_tulis),         # write text to a file (handle or name)
    "tutup":     (1, b_tutup),         # close a file
    "hapus":     (1, b_hapus),         # delete a file
    "nantik":    (1, b_nantik),        # wait this many seconds
}


def new_global():
    """Built-ins live in a parent scope, so programs can freely reuse their names."""
    base = Env()
    for name, (arity, fn) in BUILTINS.items():
        base.vars[name] = ("builtin", name, arity, fn)
    return Env(base)


# ---- imports (ambik)
IMPORT_STACK = []     # directory of the file being run, innermost last
LOADING = []          # files currently being loaded (to catch circular imports)
LOADED = {}           # file path -> module scope (each file runs once per program)


def do_import(name, env):
    if not isinstance(name, str):
        raise LangError(f"'{KEYWORDS['IMPORT']}' butuh nama berkas berupa teks")
    base = IMPORT_STACK[-1] if IMPORT_STACK else os.getcwd()
    path = os.path.join(base, name)
    candidates = [path] if path.endswith(".krc") else [path, path + ".krc"]
    found = next((c for c in candidates if os.path.isfile(c)), None)
    if not found:
        raise LangError(f"Berkas tidak ditemukan: {name}")
    found = os.path.abspath(found)
    if found in LOADING:
        raise LangError(f"Impor melingkar: {name}")
    if found not in LOADED:
        with open(found, encoding="utf-8") as f:
            src = f.read()
        module = new_global()
        LOADING.append(found)
        IMPORT_STACK.append(os.path.dirname(found))
        try:
            run_block(Parser(tokenize(src)).program(), module)
        except LangError as err:
            raise LangError(f"Dalam '{name}': {err}")
        finally:
            IMPORT_STACK.pop()
            LOADING.pop()
        LOADED[found] = module
    module = LOADED[found]
    for key, value in module.vars.items():          # every top-level name is shared
        env.declare(key, value, key in module.consts)


def run_block(stmts, env):
    for s in stmts:
        run(s, env)


def run(s, env):
    op = s[0]
    if op == "var":        env.declare(s[1], ev(s[2], env), s[3])
    elif op == "assign":   env.assign(s[1], ev(s[2], env))
    elif op == "setindex":
        obj, idx, value = ev(s[1], env), ev(s[2], env), ev(s[3], env)
        if isinstance(obj, str):
            raise LangError("Teks tidak bisa diubah per huruf")
        if isinstance(obj, dict):
            check_key(idx)
        else:
            check_index(obj, idx)
        obj[idx] = value
    elif op == "print":    print(show(ev(s[1], env)))
    elif op == "expr":     ev(s[1], env)
    elif op == "func":     env.declare(s[1], ("closure", s[2], s[3], env))
    elif op == "if":       run_block(s[2] if ev(s[1], env) else s[3], Env(env))
    elif op == "while":
        while ev(s[1], env):
            try:
                run_block(s[2], Env(env))
            except BreakSignal:
                break
            except ContinueSignal:
                continue
    elif op == "for":
        for item in iterate(ev(s[2], env)):
            local = Env(env)
            local.vars[s[1]] = item
            try:
                run_block(s[3], local)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
    elif op == "raise":
        value = ev(s[1], env)
        raise LangError(value if isinstance(value, str) else show(value))
    elif op == "try":
        try:
            run_block(s[1], Env(env))
        except (LangError, RecursionError) as err:
            local = Env(env)
            if s[2]:
                local.vars[s[2]] = str(err) if isinstance(err, LangError) else "Terlalu dalam"
            run_block(s[3], local)
    elif op == "switch":
        subject = ev(s[1], env)
        for values, body in s[2]:
            if any(binary_op("==", subject, ev(v, env)) for v in values):
                run_block(body, Env(env))
                break
        else:
            if s[3] is not None:
                run_block(s[3], Env(env))
    elif op == "import":   do_import(ev(s[1], env), env)
    elif op == "break":    raise BreakSignal()
    elif op == "continue": raise ContinueSignal()
    elif op == "return":   raise ReturnSignal(None if s[1] is None else ev(s[1], env))


def ev(e, env):
    op = e[0]
    if op == "lit":   return e[1]
    if op == "name":  return env.get(e[1])
    if op == "input":
        try:
            return input()
        except EOFError:
            return ""
    if op == "neg":
        v = ev(e[1], env)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise LangError(f"Tanda minus hanya untuk bilangan, bukan {show(v, True)}")
        return -v
    if op == "not":   return not ev(e[1], env)
    if op == "list":  return [ev(x, env) for x in e[1]]
    if op == "map":
        result = {}
        for key_expr, value_expr in e[1]:
            key = ev(key_expr, env)
            check_key(key)
            result[key] = ev(value_expr, env)
        return result
    if op == "index":
        return get_item(ev(e[1], env), ev(e[2], env))
    if op == "bin":
        o = e[1]
        if o == KEYWORDS["AND"]:
            l = ev(e[2], env)
            return l and ev(e[3], env)
        if o == KEYWORDS["OR"]:
            l = ev(e[2], env)
            return l or ev(e[3], env)
        return binary_op(o, ev(e[2], env), ev(e[3], env))
    if op == "call":
        fn = ev(e[1], env)
        args = [ev(a, env) for a in e[2]]
        if isinstance(fn, tuple) and fn[0] == "builtin":
            _, name, arity, impl = fn
            if arity is not None and len(args) != arity:
                raise LangError(f"Fungsi {name} butuh {arity} argumen, diberi {len(args)}")
            return impl(*args)
        if not (isinstance(fn, tuple) and fn[0] == "closure"):
            raise LangError("Yang dipanggil bukan fungsi")
        _, params, body, closure = fn
        if len(args) != len(params):
            raise LangError(f"Fungsi butuh {len(params)} argumen, diberi {len(args)}")
        local = Env(closure)
        local.vars.update(zip(params, args))
        if CALL_DEPTH[0] >= MAX_CALL_DEPTH:
            raise LangError(f"Panggilan fungsi terlalu dalam (lebih dari {MAX_CALL_DEPTH}). "
                            f"Mungkin fungsi memanggil dirinya tanpa henti?")
        CALL_DEPTH[0] += 1
        try:
            run_block(body, local)
        except ReturnSignal as r:
            return r.value
        except RecursionError:
            raise LangError("Panggilan fungsi terlalu dalam")
        finally:
            CALL_DEPTH[0] -= 1
        return None
    raise LangError(f"Ekspresi tidak dikenal: {op}")


def run_source(src, env=None):
    if not LOADING:
        LOADED.clear()                      # a fresh run re-reads imported files
    env = env or new_global()
    run_block(Parser(tokenize(src)).program(), env)
    return env


def run_file(path, env=None):
    """Run a .krc file; `ambik` paths are relative to that file."""
    with open(path, encoding="utf-8") as f:
        src = f.read()
    IMPORT_STACK.append(os.path.dirname(os.path.abspath(path)))
    try:
        return run_source(src, env)
    finally:
        IMPORT_STACK.pop()
        close_all_files()


USAGE = f"""KerinciLang {__version__}

Pemakaian:
  krc                  buka REPL interaktif
  krc berkas.krc       jalankan program
  krc -c "kode"        jalankan satu potong kode
  krc --version        tampilkan versi
  krc --help           tampilkan bantuan ini
"""

OPENERS, CLOSERS = {"(", "{", "["}, {")", "}", "]"}


def is_incomplete(src):
    """True while a ( { [ or 'mulai' block is still open, so the REPL keeps reading."""
    depth = 0
    for kind, text, _ in tokenize(src):
        if kind == "OP":
            depth += text in OPENERS
            depth -= text in CLOSERS
    return depth > 0


def repl():
    env = new_global()
    print(f"KerinciLang {__version__}. Ctrl+D untuk keluar.")
    buffer = ""
    while True:
        try:
            line = input("... " if buffer else ">>> ")
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
            buffer = ""
            continue
        buffer += line + "\n"
        try:
            if is_incomplete(buffer):
                continue
            run_source(buffer, env)
        except LangError as err:
            print(f"Kesalahan: {err}")
        buffer = ""


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] in ("-h", "--help"):
        print(USAGE)
        return 0
    if argv and argv[0] in ("-V", "--version"):
        print(f"KerinciLang {__version__}")
        return 0
    try:
        if not argv:
            return repl()
        if argv[0] == "-c":
            if len(argv) < 2:
                print("Kesalahan: -c butuh kode", file=sys.stderr)
                return 2
            run_source(argv[1])
        else:
            run_file(argv[0])
    except LangError as err:
        print(f"Kesalahan: {err}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"Kesalahan: berkas tidak ditemukan: {argv[0]}", file=sys.stderr)
        return 2
    except UnicodeDecodeError:
        print("Kesalahan: berkas harus berupa teks UTF-8", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nDihentikan.", file=sys.stderr)
        return 130
    except BrokenPipeError:                  # e.g. `krc program.krc | head`
        sys.stderr.close()
        return 0
    finally:
        close_all_files()
    return 0


if __name__ == "__main__":
    sys.exit(main())
