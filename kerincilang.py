"""KerinciLang: interpreter with neutral IDs and dialect vocabularies.

The engine never contains a dialect word. Words come from a Vocabulary; today
there is one, LegacySiulak, which is the frozen Siulak 0.5 vocabulary.

Run a file:  krc contoh.krc        (or: python3 kerincilang.py contoh.krc)
Start REPL:  krc
"""
import json
import os
import re
import sys
import time

try:
    from importlib.resources import files as _resource_files
except ImportError:                                   # pragma: no cover - Python < 3.9
    _resource_files = None

__version__ = "0.5.0"

# Function calls nest deeply in this interpreter. Python 3.11+ can safely go deeper
# than its default limit; older versions stay conservative.
if sys.version_info >= (3, 11):
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 12000))
    MAX_CALL_DEPTH = 400
else:
    MAX_CALL_DEPTH = 80
CALL_DEPTH = [0]


# ---- the neutral catalogue ------------------------------------------------
def load_catalog():
    """Read core/ids.json from a checkout, a wheel, or dist/krc.pyz."""
    try:
        if _resource_files is not None:
            return json.loads(_resource_files("core").joinpath("ids.json")
                              .read_text(encoding="utf-8"))
    except (ImportError, ModuleNotFoundError, FileNotFoundError, OSError):
        pass
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "core", "ids.json"), encoding="utf-8") as handle:
        return json.load(handle)


CATALOG = load_catalog()
CORE_VERSION = CATALOG["core"]


# ---- messages and errors --------------------------------------------------
class Message:
    """A catalogue message plus the values for its placeholders."""
    __slots__ = ("id", "args")

    def __init__(self, id, args):
        self.id, self.args = id, dict(args)


def msg(id, **args):
    return Message(id, args)


class LangError(Exception):
    """A user-facing error.

    `Exception.args` stays `(text,)` because tests and tools read `e.args[0]`.
    The neutral identity lives in `msg_id` and `msg_args`.
    """

    def __init__(self, message, vocab=None):
        if isinstance(message, Message):
            self.msg_id = message.id
            self.msg_args = message.args
            vocabulary = vocab or current_vocab()
            try:
                self.text = vocabulary.message(message.id, message.args)
            except (KeyError, IndexError, ValueError):
                self.text = "[" + message.id + "] " + repr(message.args)
        else:
            self.msg_id = None
            self.msg_args = {}
            self.text = str(message)
        super().__init__(self.text)


# ---- the Siulak 0.5 vocabulary (frozen) -----------------------------------
# Word IDs in the order the original KEYWORDS table used, then the rest.
LEGACY_WORDS = {
    "kw.var": "barang", "kw.const": "tetap", "kw.func": "guno", "kw.return": "balik",
    "kw.if": "kalu", "kw.else": "lain", "kw.while": "selamo", "kw.for": "untuk",
    "kw.in": "alem", "kw.switch": "pilih", "kw.import": "ambik", "kw.try": "cubo",
    "kw.catch": "tangkap", "kw.raise": "ngangkat", "kw.break": "putuh",
    "kw.continue": "lanjut", "kw.print": "nyetak", "kw.input": "tanyo",
    "kw.true": "betul", "kw.false": "salah", "kw.null": "kosong", "kw.and": "ngan",
    "kw.or": "apo", "kw.not": "idak", "kw.begin": "mulai", "kw.end": "habih",
    # built-in function names
    "fn.length": "panjang", "fn.list": "daftar", "fn.add": "tambah", "fn.sub": "kurang",
    "fn.mul": "kali", "fn.div": "bagi", "fn.range": "jarak", "fn.append": "nambahkah",
    "fn.contains": "isi", "fn.sort": "milih", "fn.reverse": "pulang", "fn.int": "bilangan",
    "fn.float": "pecahan", "fn.text": "kato", "fn.type": "mecem", "fn.map": "peta",
    "fn.split": "pisah", "fn.join": "disatu", "fn.open": "bukak", "fn.read": "baco",
    "fn.write": "tulis", "fn.close": "tutup", "fn.delete": "hapus", "fn.wait": "nantik",
    # type names returned by mecem()
    "type.int": "bilangan", "type.float": "pecahan", "type.str": "kato",
    "type.list": "daftar", "type.map": "peta", "type.func": "guno", "type.null": "kosong",
    "type.bool": "boolean",                       # placeholder: no Kerinci word yet
    "type.file": "berkas",
    # file modes (string values, not lexed words)
    "mode.read": "baco", "mode.write": "tulis", "mode.append": "nambahkah",
    # reserved for a future feature: using it as a name is an error today
    "reserved.error": "kelihu",
}

# Word forms of the comparison operators, with the neutral symbol they mean.
LEGACY_OPERATORS = {
    "op.eq": ("samo", "=="),
    "op.ne": ("dak_samo", "!="),
    "op.gt": ("lebih_daripado", ">"),
    "op.lt": ("kurang_daripado", "<"),
    "op.ge": ("lebih_samo", ">="),
    "op.le": ("kurang_samo", "<="),
}

FILE_MODE_CHARS = {"mode.read": "r", "mode.write": "w", "mode.append": "a"}


class Vocabulary:
    """The seam between neutral IDs and one dialect's words."""

    code = "base"
    core = CORE_VERSION

    def word(self, id):
        raise NotImplementedError

    def message(self, id, args=None):
        raise NotImplementedError

    def mode_id(self, word):
        raise NotImplementedError

    def surface(self):
        raise NotImplementedError

    def operators(self):
        raise NotImplementedError

    def reserved(self):
        raise NotImplementedError


class LegacySiulak(Vocabulary):
    """The frozen Siulak 0.5 vocabulary. Output must match v0.5 byte for byte."""

    code = "siulak"
    core = CORE_VERSION

    def __init__(self, catalog=None):
        self.catalog = catalog or CATALOG
        self._words = dict(LEGACY_WORDS)
        self._operators = dict(LEGACY_OPERATORS)
        self._surface = {word: id for id, word in self._words.items()
                         if id.startswith("kw.")}
        self._operator_words = {id: pair[0] for id, pair in self._operators.items()}
        self._operator_symbols = {pair[0]: pair[1] for pair in self._operators.values()}
        self._modes = {word: id for id, word in self._words.items()
                       if id.startswith("mode.")}
        self._reserved = {word for id, word in self._words.items()
                          if id.startswith("reserved.")}
        self._templates = {id: entry["id_gloss"]
                           for id, entry in self.catalog["ids"].items()
                           if id.startswith("msg.")}

    def word(self, id):
        if id in self._words:
            return self._words[id]
        if id in self._operator_words:
            return self._operator_words[id]
        raise KeyError(id)

    def message(self, id, args=None):
        return self._templates[id].format(**(args or {}))

    def mode_id(self, word):
        return self._modes.get(word)

    def surface(self):
        return dict(self._surface)

    def operators(self):
        return dict(self._operator_symbols)

    def reserved(self):
        return set(self._reserved)


LEGACY = LegacySiulak()
_VOCAB_STACK = [LEGACY]


def current_vocab():
    """The vocabulary used for output and messages right now."""
    return _VOCAB_STACK[-1] if _VOCAB_STACK else LEGACY


class use_vocab:
    """Push a vocabulary for the duration of a run (M1: one per program)."""

    def __init__(self, vocab):
        self.vocab = vocab

    def __enter__(self):
        _VOCAB_STACK.append(self.vocab)
        return self.vocab

    def __exit__(self, *exc):
        _VOCAB_STACK.pop()
        return False


# ---- lexer ----------------------------------------------------------------
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
STATEMENT_STARTS = {"kw.var", "kw.const", "kw.func", "kw.if", "kw.else", "kw.while",
                    "kw.for", "kw.switch", "kw.try", "kw.raise", "kw.import",
                    "kw.break", "kw.continue", "kw.return", "kw.print"}


ESCAPES = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}


def unescape(raw, line):
    """Turn \n \t \" \\ inside a text literal into the real characters."""
    def replace(m):
        c = m.group(1)
        if c not in ESCAPES:
            raise LangError(msg("msg.syntax.escape", line=line, c=c))
        return ESCAPES[c]
    return re.sub(r"\\(.)", replace, raw)


def tokenize(src, vocab=None):
    vocab = vocab or current_vocab()
    surface = vocab.surface()
    operators = vocab.operators()
    reserved = vocab.reserved()
    tokens, line = [], 1
    for m in MASTER.finditer(src):
        kind, text = m.lastgroup, m.group()
        if kind in ("SKIP", "COMMENT"):
            line += text.count("\n")
            continue
        if kind == "BAD":
            raise LangError(msg("msg.syntax.bad_char", line=line, text=repr(text)))
        if kind == "IDENT" and ENABLE_WORD_OPERATORS and text in operators:
            kind, text = "OP", operators[text]
        elif kind == "IDENT" and text in reserved:
            raise LangError(msg("msg.syntax.reserved", line=line, text=text))
        elif kind == "IDENT" and text in surface:
            token_id = surface[text]
            if token_id == "kw.begin":           # mulai ... habih are braces in Kerinci
                kind, text = "OP", "{"
            elif token_id == "kw.end":
                kind, text = "OP", "}"
            else:
                kind, text = token_id, token_id
        tokens.append((kind, text, line))
    tokens.append(("EOF", "", line))
    return tokens


class Parser:
    def __init__(self, tokens, vocab=None):
        self.t, self.i, self.loop_depth, self.func_depth = tokens, 0, 0, 0
        self.vocab = vocab or current_vocab()

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

    def label(self, what):
        """The user-facing name of an expected token."""
        if isinstance(what, str) and (what.startswith("kw.") or what.startswith("op.")):
            return self.vocab.word(what)
        return what

    def display(self, kind, text):
        """The user-facing spelling of a token that was found."""
        if kind.startswith("kw.") or kind.startswith("op."):
            return self.vocab.word(kind)
        return text

    def expect(self, what):
        tok = self.match(what)
        if not tok:
            raise LangError(msg("msg.syntax.expected",
                                line=self.line(),
                                what=repr(self.label(what)),
                                text=repr(self.display(self.kind(), self.text()))))
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
        self.advance()                       # if
        cond, then, other = self.expression(), self.block(), []
        if self.match("kw.else"):            # "else if ..." chains, plain "else { }" ends
            other = [self.if_stmt()] if self.kind() == "kw.if" else self.block()
        return ("if", cond, then, other)

    def statement(self):
        k = self.kind()
        if k in ("kw.var", "kw.const"):
            self.advance()
            name = self.expect("IDENT")[1]
            self.expect("=")
            return ("var", name, self.expression(), k == "kw.const")
        if k == "kw.func":
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
        if k == "kw.if":
            return self.if_stmt()
        if k == "kw.while":
            self.advance()
            cond = self.expression()
            return ("while", cond, self.loop_body())
        if k == "kw.for":                    # for <name> in <list | text> { ... }
            self.advance()
            var = self.expect("IDENT")[1]
            if not self.match("kw.in"):
                raise LangError(msg("msg.syntax.expected_after_name",
                                    line=self.line(),
                                    word=self.vocab.word("kw.in"),
                                    text=repr(self.display(self.kind(), self.text()))))
            source = self.expression()
            return ("for", var, source, self.loop_body())
        if k == "kw.try":                    # try { ... } catch name { ... }
            line = self.advance()[2]
            body = self.block()
            if not self.match("kw.catch"):
                raise LangError(msg("msg.syntax.try_requires_catch",
                                    line=line,
                                    try_word=self.vocab.word("kw.try"),
                                    catch_word=self.vocab.word("kw.catch")))
            name = self.advance()[1] if self.kind() == "IDENT" else None
            return ("try", body, name, self.block())
        if k == "kw.raise":                  # raise "message"
            self.advance()
            return ("raise", self.expression())
        if k == "kw.switch":                 # switch x { if 1, 2 { } else { } }
            self.advance()
            subject = self.expression()
            self.expect("{")
            clauses, default = [], None
            while self.kind() == "kw.if":
                self.advance()
                values = [self.expression()]
                while self.match(","):
                    values.append(self.expression())
                clauses.append((values, self.block()))
            if self.match("kw.else"):
                default = self.block()
            self.expect("}")
            return ("switch", subject, clauses, default)
        if k == "kw.import":                 # import "file"
            self.advance()
            return ("import", self.expression())
        if k in ("kw.break", "kw.continue"):
            line = self.advance()[2]
            if self.loop_depth == 0:
                raise LangError(msg("msg.loop.break_outside", line=line,
                                    word=self.vocab.word(k)))
            return (k.split(".", 1)[1],)
        if k == "kw.return":
            line = self.advance()[2]
            if self.func_depth == 0:
                raise LangError(msg("msg.func.return_outside", line=line,
                                    word=self.vocab.word("kw.return")))
            if self.text() == "}" or self.kind() in STATEMENT_STARTS or self.kind() == "EOF":
                return ("return", None)
            return ("return", self.expression())
        if k == "kw.print":
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
                raise LangError(msg("msg.syntax.assign_target", line=line))
            self.advance()
            return ("setindex", expr[1], expr[2], self.expression())
        return ("expr", expr)

    def binary(self, sub, ops):
        left = sub()
        while self.kind() in ops or (self.kind() == "OP" and self.text() in ops):
            op = self.advance()[1]
            left = ("bin", op, left, sub())
        return left

    def expression(self): return self.binary(self.and_, ("kw.or",))
    def and_(self):       return self.binary(self.equality, ("kw.and",))
    # Comparison tokens carry the neutral symbol, whether written as a word or a
    # symbol, so the parser works on symbols the same way it always has.
    def equality(self):   return self.binary(self.comparison, ("==", "!="))
    def comparison(self): return self.binary(self.term, ("<", ">", "<=", ">="))
    def term(self):       return self.binary(self.factor, ("+", "-"))
    def factor(self):     return self.binary(self.unary, ("*", "/", "%"))

    def unary(self):
        if self.match("kw.not"):
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
        if kind == "kw.true":  return ("lit", True)
        if kind == "kw.false": return ("lit", False)
        if kind == "kw.null":  return ("lit", None)
        if kind == "kw.input":
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
        if kind == "OP" and text == "{":     # map literal: { "key": value, ... }
            pairs = []
            while not (self.kind() == "OP" and self.text() == "}") and self.kind() != "EOF":
                key = self.expression()
                self.expect(":")
                pairs.append((key, self.expression()))
                if not self.match(","):
                    break
            self.expect("}")
            return ("map", pairs)
        raise LangError(msg("msg.syntax.unexpected", line=line,
                            text=repr(self.display(kind, text))))


class ReturnSignal(Exception):
    def __init__(self, value): self.value = value
class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass


class Env:
    def __init__(self, parent=None, vocab=None):
        self.vars, self.consts, self.parent = {}, set(), parent
        self.vocab = vocab or (parent.vocab if parent else current_vocab())

    def lookup(self, name):
        env = self
        while env:
            if name in env.vars:
                return env
            env = env.parent
        return None

    def declare(self, name, value, const=False):
        if name in self.consts:
            raise LangError(msg("msg.name.already_const", name=name), vocab=self.vocab)
        self.vars[name] = value
        if const:
            self.consts.add(name)

    def get(self, name):
        env = self.lookup(name)
        if not env:
            raise LangError(msg("msg.name.undefined", name=name), vocab=self.vocab)
        return env.vars[name]

    def assign(self, name, value):
        env = self.lookup(name)
        if not env:
            raise LangError(msg("msg.name.undeclared", name=name,
                                var_word=self.vocab.word("kw.var")), vocab=self.vocab)
        if name in env.consts:
            raise LangError(msg("msg.name.constant", name=name,
                                const_word=self.vocab.word("kw.const")), vocab=self.vocab)
        env.vars[name] = value


def show(v, vocab=None, nested=False):
    vocab = vocab or current_vocab()
    if v is None:  return vocab.word("kw.null")
    if v is True:  return vocab.word("kw.true")
    if v is False: return vocab.word("kw.false")
    if isinstance(v, list):
        return "[" + ", ".join(show(x, vocab, True) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{show(k, vocab, True)}: {show(x, vocab, True)}"
                               for k, x in v.items()) + "}"
    if isinstance(v, str) and nested:
        return f'"{v}"'
    if isinstance(v, Berkas):
        return f'<{vocab.word("type.file")} "{v.path}">'
    if isinstance(v, tuple) and v and v[0] == "closure":
        return f"<{vocab.word('kw.func')}>"
    if isinstance(v, tuple) and v and v[0] == "builtin":
        return f"<{vocab.word('kw.func')} {vocab.word(v[1])}>"
    return str(v)


def binary_op(o, l, r, vocab=None):
    """Shared by operators (+ - * / ...) and the built-ins add/subtract/..."""
    vocab = vocab or current_vocab()
    try:
        if o == "+":
            if isinstance(l, str) or isinstance(r, str):
                return show(l, vocab) + show(r, vocab)
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
        raise LangError(msg("msg.value.div_zero"))
    except TypeError:
        raise LangError(msg("msg.value.operator", op=repr(o),
                            left=show(l, vocab, True), right=show(r, vocab, True)))


def check_key(k):
    if isinstance(k, bool) or not isinstance(k, (str, int)):
        raise LangError(msg("msg.value.key_type"))


def get_item(obj, idx):
    if isinstance(obj, dict):
        check_key(idx)
        if idx not in obj:
            raise LangError(msg("msg.value.key_missing", key=show(idx, None, True)))
        return obj[idx]
    check_index(obj, idx)
    return obj[idx]


def check_index(obj, idx):
    if not isinstance(obj, (list, str)):
        raise LangError(msg("msg.value.index_kind"))
    if isinstance(idx, bool) or not isinstance(idx, int):
        raise LangError(msg("msg.value.index_type"))
    if idx < 0 or idx >= len(obj):
        raise LangError(msg("msg.value.index_range", index=idx, length=len(obj)))


def iterate(v):
    vocab = current_vocab()
    if isinstance(v, Berkas):               # for line in file { ... } reads line by line
        need_handle(v, ("mode.read",), "kw.for")
        return read_from(v.handle, v.path, as_lines=True)
    if isinstance(v, (list, str, dict)):
        return list(v)                      # a map gives its keys
    if isinstance(v, int) and not isinstance(v, bool):
        raise LangError(msg("msg.loop.use_range",
                            range_fn=vocab.word("fn.range"),
                            for_word=vocab.word("kw.for"),
                            in_word=vocab.word("kw.in")))
    raise LangError(msg("msg.loop.not_iterable", for_word=vocab.word("kw.for")))


# ---- built-in functions: ID -> (number of arguments or None for any, python function)
def b_panjang(x):
    if isinstance(x, (list, str, dict)):
        return len(x)
    raise LangError(msg("msg.fn.length_kind", fn=current_vocab().word("fn.length")))


MAX_JARAK = 1_000_000


def b_jarak(*args):
    vocab = current_vocab()
    fn = vocab.word("fn.range")
    if not 1 <= len(args) <= 3:
        raise LangError(msg("msg.fn.range_arity", fn=fn, count=len(args)))
    if any(isinstance(a, bool) or not isinstance(a, int) for a in args):
        raise LangError(msg("msg.fn.range_args", fn=fn))
    if len(args) == 3 and args[2] == 0:
        raise LangError(msg("msg.fn.range_step", fn=fn))
    r = range(*args)
    if len(r) > MAX_JARAK:
        raise LangError(msg("msg.fn.range_too_big", max=MAX_JARAK))
    return list(r)


def need_list(fn_id, x):
    if not isinstance(x, list):
        raise LangError(msg("msg.fn.list_only", fn=current_vocab().word(fn_id)))


def b_nambahkah(xs, value):
    need_list("fn.append", xs)
    xs.append(value)                      # changes the list itself
    return None


def b_isi(container, item):
    vocab = current_vocab()
    if isinstance(container, dict):         # for a map: is it a key?
        try:
            return item in container
        except TypeError:
            return False
    if isinstance(container, list):
        return item in container
    if isinstance(container, str):
        if not isinstance(item, str):
            raise LangError(msg("msg.fn.contains_type"))
        return item in container
    raise LangError(msg("msg.fn.contains_kind", fn=vocab.word("fn.contains")))


def b_milih(xs):
    need_list("fn.sort", xs)
    try:
        return sorted(xs)                 # returns a new list; the original is unchanged
    except TypeError:
        raise LangError(msg("msg.fn.sort_type"))


def b_pulang(x):
    if isinstance(x, list):
        return x[::-1]                    # new list
    if isinstance(x, str):
        return x[::-1]
    raise LangError(msg("msg.fn.reverse_kind", fn=current_vocab().word("fn.reverse")))


def cannot_convert(x, target_id):
    raise LangError(msg("msg.value.convert", value=show(x, None, True),
                        target=current_vocab().word(target_id)))


def b_bilangan(x):
    if isinstance(x, bool):
        cannot_convert(x, "fn.int")
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        try:
            return int(x)                   # cuts off the decimals: 3.7 -> 3, -3.7 -> -3
        except (OverflowError, ValueError):
            cannot_convert(x, "fn.int")
    if isinstance(x, str) and re.fullmatch(r"\s*[+-]?[0-9]+\s*", x):
        return int(x)
    cannot_convert(x, "fn.int")


def b_pecahan(x):
    if isinstance(x, bool):
        cannot_convert(x, "fn.float")
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str) and re.fullmatch(r"\s*[+-]?[0-9]+(\.[0-9]+)?\s*", x):
        return float(x)
    cannot_convert(x, "fn.float")


def b_mecem(x):
    vocab = current_vocab()
    if x is None:                return vocab.word("type.null")
    if isinstance(x, bool):      return vocab.word("type.bool")
    if isinstance(x, int):       return vocab.word("type.int")
    if isinstance(x, float):     return vocab.word("type.float")
    if isinstance(x, str):       return vocab.word("type.str")
    if isinstance(x, list):      return vocab.word("type.list")
    if isinstance(x, dict):      return vocab.word("type.map")
    if isinstance(x, Berkas):    return vocab.word("type.file")
    return vocab.word("type.func")


def b_peta(*pairs):
    result = {}
    for pair in pairs:
        if not (isinstance(pair, list) and len(pair) == 2):
            raise LangError(msg("msg.value.map_pair"))
        check_key(pair[0])
        result[pair[0]] = pair[1]
    return result


class Berkas:
    """An open file. Made by open(), used with read/write, closed with close."""
    def __init__(self, path, mode, handle):
        self.path, self.mode, self.handle, self.closed = path, mode, handle, False


OPEN_FILES = []
MAX_NANTIK = 3600


def file_error(err, path):
    if isinstance(err, FileNotFoundError):
        return LangError(msg("msg.file.not_found", path=path))
    if isinstance(err, PermissionError):
        return LangError(msg("msg.file.permission", path=path))
    if isinstance(err, IsADirectoryError):
        return LangError(msg("msg.file.is_dir", path=path))
    return LangError(msg("msg.file.io", path=path, reason=err.strerror or err))


def need_path(x, fn_id):
    if not isinstance(x, str):
        raise LangError(msg("msg.file.path_type", fn=current_vocab().word(fn_id)))
    return x


def need_handle(x, allowed, fn_id):
    vocab = current_vocab()
    fn = vocab.word(fn_id)
    if not isinstance(x, Berkas):
        raise LangError(msg("msg.file.handle_required", fn=fn,
                            open_fn=vocab.word("fn.open")))
    if x.closed:
        raise LangError(msg("msg.file.closed", path=x.path))
    if x.mode not in allowed:
        raise LangError(msg("msg.file.wrong_mode", mode=vocab.word(x.mode), fn=fn))
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
    vocab = current_vocab()
    fn = vocab.word("fn.open")
    if not 1 <= len(args) <= 2:
        raise LangError(msg("msg.fn.open_arity", fn=fn, count=len(args)))
    path = need_path(args[0], "fn.open")
    mode_id = "mode.read"
    if len(args) == 2:
        mode_id = vocab.mode_id(args[1]) if isinstance(args[1], str) else None
        if mode_id is None:
            raise LangError(msg("msg.file.mode_invalid",
                                read=vocab.word("mode.read"),
                                write=vocab.word("mode.write"),
                                append=vocab.word("mode.append"),
                                value=show(args[1], vocab, True)))
    try:
        handle = open(path, FILE_MODE_CHARS[mode_id], encoding="utf-8",
                      newline=None if mode_id == "mode.read" else "\n")
    except OSError as err:
        raise file_error(err, path)
    f = Berkas(path, mode_id, handle)
    OPEN_FILES.append(f)
    return f


def read_from(handle, path, as_lines=False):
    try:
        if as_lines:
            return [line[:-1] if line.endswith("\n") else line for line in handle]
        return handle.read()
    except UnicodeDecodeError:
        raise LangError(msg("msg.file.not_utf8", path=path))
    except OSError as err:
        raise file_error(err, path)


def b_baco(x):
    if isinstance(x, str):                       # read("name.txt") reads a whole file
        try:
            with open(x, encoding="utf-8") as handle:
                return read_from(handle, x)
        except OSError as err:
            raise file_error(err, x)
    need_handle(x, ("mode.read",), "fn.read")
    return read_from(x.handle, x.path)


def b_tulis(x, value):
    text = value if isinstance(value, str) else show(value)
    try:
        if isinstance(x, str):                   # write("name.txt", text) replaces the file
            with open(x, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
        else:
            need_handle(x, ("mode.write", "mode.append"), "fn.write")
            x.handle.write(text)
    except OSError as err:
        raise file_error(err, x if isinstance(x, str) else x.path)
    return None


def b_tutup(x):
    vocab = current_vocab()
    if not isinstance(x, Berkas):
        raise LangError(msg("msg.file.handle_required", fn=vocab.word("fn.close"),
                            open_fn=vocab.word("fn.open")))
    if not x.closed:
        x.handle.close()
        x.closed = True
        if x in OPEN_FILES:
            OPEN_FILES.remove(x)
    return None


def b_hapus(path):
    need_path(path, "fn.delete")
    try:
        os.remove(path)
    except OSError as err:
        raise file_error(err, path)
    return None


def b_nantik(seconds):
    vocab = current_vocab()
    fn = vocab.word("fn.wait")
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
        raise LangError(msg("msg.fn.wait_number", fn=fn))
    if seconds < 0 or seconds > MAX_NANTIK:
        raise LangError(msg("msg.fn.wait_range", fn=fn, max=MAX_NANTIK))
    time.sleep(seconds)
    return None


def b_pisah(*args):
    vocab = current_vocab()
    fn = vocab.word("fn.split")
    if not 1 <= len(args) <= 2:
        raise LangError(msg("msg.fn.split_arity", fn=fn, count=len(args)))
    text = args[0]
    if not isinstance(text, str):
        raise LangError(msg("msg.fn.split_kind", fn=fn))
    if len(args) == 1:
        return text.split()                       # on any spaces; no empty pieces
    sep = args[1]
    if not isinstance(sep, str):
        raise LangError(msg("msg.value.separator"))
    if sep == "":
        return list(text)                         # one piece per character
    return text.split(sep)


def b_disatu(*args):
    vocab = current_vocab()
    fn = vocab.word("fn.join")
    if not 1 <= len(args) <= 2:
        raise LangError(msg("msg.fn.join_arity", fn=fn, count=len(args)))
    need_list("fn.join", args[0])
    sep = args[1] if len(args) == 2 else ""
    if not isinstance(sep, str):
        raise LangError(msg("msg.value.separator"))
    return sep.join(show(x, vocab) for x in args[0])


BUILTIN_IDS = {
    "fn.length": (1, b_panjang),
    "fn.list":   (None, lambda *items: list(items)),
    "fn.add":    (2, lambda a, b: binary_op("+", a, b)),
    "fn.sub":    (2, lambda a, b: binary_op("-", a, b)),
    "fn.mul":    (2, lambda a, b: binary_op("*", a, b)),
    "fn.div":    (2, lambda a, b: binary_op("/", a, b)),
    "fn.range":    (None, b_jarak),
    "fn.append":   (2, b_nambahkah),
    "fn.contains": (2, b_isi),
    "fn.sort":     (1, b_milih),
    "fn.reverse":  (1, b_pulang),
    "fn.int":      (1, b_bilangan),
    "fn.float":    (1, b_pecahan),
    "fn.text":     (1, lambda x: show(x)),
    "fn.type":     (1, b_mecem),
    "fn.map":      (None, b_peta),
    "fn.split":    (None, b_pisah),
    "fn.join":     (None, b_disatu),
    "fn.open":     (None, b_bukak),
    "fn.read":     (1, b_baco),
    "fn.write":    (2, b_tulis),
    "fn.close":    (1, b_tutup),
    "fn.delete":   (1, b_hapus),
    "fn.wait":     (1, b_nantik),
}


def new_global(vocab=None):
    """Built-ins live in a parent scope, so programs can freely reuse their names."""
    vocab = vocab or current_vocab()
    base = Env(vocab=vocab)
    for fn_id, (arity, fn) in BUILTIN_IDS.items():
        base.vars[vocab.word(fn_id)] = ("builtin", fn_id, arity, fn)
    return Env(base, vocab=vocab)


# ---- imports --------------------------------------------------------------
IMPORT_STACK = []     # directory of the file being run, innermost last
LOADING = []          # files currently being loaded (to catch circular imports)
LOADED = {}           # file path -> module scope (each file runs once per program)


def do_import(name, env):
    vocab = env.vocab
    if not isinstance(name, str):
        raise LangError(msg("msg.import.not_text", kw=vocab.word("kw.import")))
    base = IMPORT_STACK[-1] if IMPORT_STACK else os.getcwd()
    path = os.path.join(base, name)
    candidates = [path] if path.endswith(".krc") else [path, path + ".krc"]
    found = next((c for c in candidates if os.path.isfile(c)), None)
    if not found:
        raise LangError(msg("msg.import.not_found", name=name))
    found = os.path.abspath(found)
    if found in LOADING:
        raise LangError(msg("msg.import.circular", name=name))
    if found not in LOADED:
        with open(found, encoding="utf-8") as f:
            src = f.read()
        module = new_global(vocab)
        LOADING.append(found)
        IMPORT_STACK.append(os.path.dirname(found))
        try:
            with use_vocab(vocab):
                run_block(Parser(tokenize(src, vocab), vocab).program(), module)
        except LangError as err:
            raise LangError(msg("msg.import.in_module", name=name, message=str(err)))
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
            raise LangError(msg("msg.value.text_immutable"))
        if isinstance(obj, dict):
            check_key(idx)
        else:
            check_index(obj, idx)
        obj[idx] = value
    elif op == "print":    print(show(ev(s[1], env), env.vocab))
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
        raise LangError(value if isinstance(value, str) else show(value, env.vocab))
    elif op == "try":
        try:
            run_block(s[1], Env(env))
        except (LangError, RecursionError) as err:
            local = Env(env)
            if s[2]:
                local.vars[s[2]] = (str(err) if isinstance(err, LangError)
                                    else env.vocab.message("msg.runtime.too_deep"))
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
            raise LangError(msg("msg.value.neg_type", value=show(v, env.vocab, True)))
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
        if o == "kw.and":
            l = ev(e[2], env)
            return l and ev(e[3], env)
        if o == "kw.or":
            l = ev(e[2], env)
            return l or ev(e[3], env)
        return binary_op(o, ev(e[2], env), ev(e[3], env), env.vocab)
    if op == "call":
        fn = ev(e[1], env)
        args = [ev(a, env) for a in e[2]]
        vocab = env.vocab
        if isinstance(fn, tuple) and fn[0] == "builtin":
            _, fn_id, arity, impl = fn
            if arity is not None and len(args) != arity:
                raise LangError(msg("msg.call.builtin_arity", fn=vocab.word(fn_id),
                                    arity=arity, count=len(args)))
            return impl(*args)
        if not (isinstance(fn, tuple) and fn[0] == "closure"):
            raise LangError(msg("msg.call.not_function"))
        _, params, body, closure = fn
        if len(args) != len(params):
            raise LangError(msg("msg.call.arity", arity=len(params), count=len(args)))
        local = Env(closure)
        local.vars.update(zip(params, args))
        if CALL_DEPTH[0] >= MAX_CALL_DEPTH:
            raise LangError(msg("msg.call.depth", max=MAX_CALL_DEPTH))
        CALL_DEPTH[0] += 1
        try:
            run_block(body, local)
        except ReturnSignal as r:
            return r.value
        except RecursionError:
            raise LangError(msg("msg.call.depth_short"))
        finally:
            CALL_DEPTH[0] -= 1
        return None
    raise LangError(msg("msg.runtime.unknown_expr", op=op))


def run_source(src, env=None, vocab=None):
    if not LOADING:
        LOADED.clear()                      # a fresh run re-reads imported files
    if env is None:
        env = new_global(vocab)
    elif vocab is not None:
        env.vocab = vocab
    with use_vocab(env.vocab):
        run_block(Parser(tokenize(src, env.vocab), env.vocab).program(), env)
    return env


def run_file(path, env=None, vocab=None):
    """Run a .krc file; `ambik` paths are relative to that file."""
    with open(path, encoding="utf-8") as f:
        src = f.read()
    IMPORT_STACK.append(os.path.dirname(os.path.abspath(path)))
    try:
        return run_source(src, env, vocab)
    finally:
        IMPORT_STACK.pop()
        close_all_files()


# ---- compatibility views (Siulak 0.5 shape) -------------------------------
# These exist so tests, tools, and the VS Code grammar keep working unchanged.
# They are generated from LEGACY_WORDS; do not hand-maintain a second table.
KEYWORDS = {id.split(".", 1)[1].upper(): word
            for id, word in LEGACY_WORDS.items() if id.startswith("kw.")}
SURFACE = {word: name for name, word in KEYWORDS.items()}
assert len(SURFACE) == len(KEYWORDS), "Two keywords share the same word"

ENABLE_WORD_OPERATORS = True
WORD_OPERATORS = {word: symbol for word, symbol in LEGACY_OPERATORS.values()}
assert not set(WORD_OPERATORS) & set(SURFACE), "A word is both a keyword and an operator"

RESERVED = {word for id, word in LEGACY_WORDS.items() if id.startswith("reserved.")}

TYPE_NAMES = {id.split(".", 1)[1]: word
              for id, word in LEGACY_WORDS.items() if id.startswith("type.")}

MODES = {LEGACY_WORDS[id]: char for id, char in FILE_MODE_CHARS.items()}

BUILTINS = {LEGACY_WORDS[id]: spec for id, spec in BUILTIN_IDS.items()}


USAGE = f"""KerinciLang {__version__}

Pemakaian:
  krc                  buka REPL interaktif
  krc berkas.krc       jalankan program
  krc -c "kode"        jalankan satu potong kode
  krc --version        tampilkan versi
  krc --help           tampilkan bantuan ini
"""

OPENERS, CLOSERS = {"(", "{", "["}, {")", "}", "]"}


def is_incomplete(src, vocab=None):
    """True while a ( { [ or block is still open, so the REPL keeps reading."""
    depth = 0
    for kind, text, _ in tokenize(src, vocab):
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
            if is_incomplete(buffer, env.vocab):
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
