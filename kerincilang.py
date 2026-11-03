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
import tempfile
import time

try:
    from importlib.resources import files as _resource_files
except ImportError:                                   # pragma: no cover - Python < 3.9
    _resource_files = None

__version__ = "0.6.0"

# `python kerincilang.py` runs this file as __main__. Registering the alias means
# a lazy `import kerincilang` (dialects.loader) reuses this module instead of
# loading a second copy of the engine.
if __name__ == "__main__":
    sys.modules.setdefault("kerincilang", sys.modules[__name__])

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

# The symbols are neutral (`==`, `<`, ...); only the words belong to a dialect.
# A dialect file supplies `op.*` words, and the loader pairs them with these.
OP_SYMBOLS = {id: symbol for id, (word, symbol) in LEGACY_OPERATORS.items()}

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
    """Push a vocabulary for the duration of a run or one function call."""

    def __init__(self, vocab):
        self.vocab = vocab

    def __enter__(self):
        _VOCAB_STACK.append(self.vocab)
        return self.vocab

    def __exit__(self, *exc):
        _VOCAB_STACK.pop()
        return False


# ---- run context (dialect selection) --------------------------------------
HEADER_HINT_RE = re.compile(r"^\s*#.*\bdialek\b", re.IGNORECASE)
HEADER_RE = re.compile(r"^\s*#\s*dialek\s*:\s*([a-z0-9-]+)\s*$")


class RunContext:
    """State shared by every file in one invocation."""

    def __init__(self, default_vocab=None, dialect_root=None, strict=False):
        self.default_vocab = default_vocab or LEGACY
        self.dialect_root = dialect_root
        self.strict = strict
        self.cache = {}          # dialect code -> Vocabulary
        self.warned = set()      # {(dialect code, ID)}
        self.strict_failed = False
        self.started = False


_CONTEXT_STACK = []


def current_context():
    return _CONTEXT_STACK[-1] if _CONTEXT_STACK else None


class use_context:
    def __init__(self, context):
        self.context = context

    def __enter__(self):
        _CONTEXT_STACK.append(self.context)
        return self.context

    def __exit__(self, *exc):
        _CONTEXT_STACK.pop()
        return False


def dialect_header(src):
    """The code on line 1, or None. A malformed header is an error, not a comment."""
    line = src.split("\n", 1)[0].rstrip("\r")
    if not HEADER_HINT_RE.match(line):
        return None
    match = HEADER_RE.match(line)
    if not match:
        raise LangError(msg("msg.dialect.header", line=1, text=line.strip()))
    return match.group(1)


def _gaps(dialect):
    """Tier 1 IDs an approved dialect still takes from the base."""
    if dialect.status != "approved":
        return []
    return [id for id, source in dialect.report.fallbacks
            if source == "base" and CATALOG["ids"][id]["tier"] == 1]


def _warn_fallback(context, code, id, word):
    key = (code, id)
    if key in context.warned:
        return
    context.warned.add(key)
    if id.startswith("msg."):
        print(f"warning: dialect {code}: {id} falls back to the base message",
              file=sys.stderr)
    else:
        print(f"warning: dialect {code}: {id} falls back to the base word {word!r}",
              file=sys.stderr)


def resolve_dialect(code, context=None):
    """Load one dialect for this run, or Siulak while it has no file yet."""
    context = context or current_context() or RunContext()
    if code in context.cache:
        return context.cache[code]

    from dialects.loader import DialectError, load_dialect

    try:
        dialect = load_dialect(code, root=context.dialect_root)
    except DialectError as err:
        if err.code == "missing" and code == "siulak":
            context.cache[code] = LEGACY
            return LEGACY
        if err.code == "missing":
            raise LangError(msg("msg.dialect.unknown", code=code))
        raise LangError(msg("msg.dialect.invalid", code=code,
                            detail=err.problems[0].message))

    vocab = dialect.vocab
    watch = getattr(vocab, "watch", None)
    if watch is not None:
        watch(lambda id, word: _warn_fallback(context, code, id, word))
    context.cache[code] = vocab

    if context.strict:
        gaps = _gaps(dialect)
        if gaps:
            context.strict_failed = True
            print(f"warning: strict: dialect {code} has {len(gaps)} tier-1 "
                  f"word(s) from the base: {', '.join(gaps)}", file=sys.stderr)
    return vocab


def resolve_source_vocab(src, context=None):
    """The header wins; otherwise the run default (Siulak when nothing is set)."""
    context = context or current_context() or RunContext()
    code = dialect_header(src)
    if code is None:
        return context.default_vocab
    return resolve_dialect(code, context)


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


def _register_builtins(base, vocab):
    for fn_id, (arity, fn) in BUILTIN_IDS.items():
        base.vars[vocab.word(fn_id)] = ("builtin", fn_id, arity, fn)


def new_global(vocab=None):
    """Built-ins live in a parent scope, so programs can freely reuse their names."""
    vocab = vocab or current_vocab()
    base = Env(vocab=vocab)
    suspend = getattr(vocab, "suspend", None)
    if suspend is None:                 # a plain Vocabulary has nothing to silence
        _register_builtins(base, vocab)
    else:
        with suspend():                 # registering every built-in is not a "use"
            _register_builtins(base, vocab)
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
        context = current_context() or RunContext()
        module_vocab = resolve_source_vocab(src, context)
        module = new_global(module_vocab)
        LOADING.append(found)
        IMPORT_STACK.append(os.path.dirname(found))
        try:
            with use_vocab(module_vocab):
                run_block(Parser(tokenize(src, module_vocab), module_vocab).program(),
                          module)
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
            with use_vocab(local.vocab):     # the callee's dialect, not the caller's
                run_block(body, local)
        except ReturnSignal as r:
            return r.value
        except RecursionError:
            raise LangError(msg("msg.call.depth_short"))
        finally:
            CALL_DEPTH[0] -= 1
        return None
    raise LangError(msg("msg.runtime.unknown_expr", op=op))


def run_source(src, env=None, vocab=None, *, dialect_root=None):
    if not LOADING:
        LOADED.clear()                      # a fresh run re-reads imported files

    context = current_context()
    own_context = context is None
    if own_context:
        context = RunContext(vocab or (env.vocab if env is not None else LEGACY),
                             dialect_root)
    else:
        if vocab is not None:
            context.default_vocab = vocab
        if dialect_root is not None:
            context.dialect_root = dialect_root
    if own_context:
        _CONTEXT_STACK.append(context)
    try:
        src_vocab = resolve_source_vocab(src, context)
        if context.strict_failed and not context.started:
            return env                        # strict: don't run a failing file
        if env is None:
            env = new_global(src_vocab)
        else:
            env.vocab = src_vocab
        context.started = True
        with use_vocab(src_vocab):
            run_block(Parser(tokenize(src, src_vocab), src_vocab).program(), env)
        return env
    finally:
        if own_context:
            _CONTEXT_STACK.pop()


def run_file(path, env=None, vocab=None, *, dialect_root=None):
    """Run a .krc file; `ambik` paths are relative to that file."""
    with open(path, encoding="utf-8") as f:
        src = f.read()
    IMPORT_STACK.append(os.path.dirname(os.path.abspath(path)))
    try:
        return run_source(src, env, vocab, dialect_root=dialect_root)
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
  krc [--dialek KODE] [--ketat] berkas.krc   jalankan program
  krc [--dialek KODE] [--ketat] -c "kode"    jalankan satu potong kode
  krc [--dialek KODE]                        buka REPL interaktif
  krc migrasi BERKAS...                      tambahkan header dialek
  krc migrasi DIR --semua                    tambahkan header ke semua .krc
  krc terjemah BERKAS --ke KODE              terjemahkan ke dialek lain
  krc --version                              tampilkan versi
  krc --help                                 tampilkan bantuan ini

  --dialek KODE   dialek untuk berkas yang tidak punya header `# dialek:`
  --ketat         gagal (exit 2) bila dialek yang disetujui belum lengkap

  krc migrasi --help    bantuan untuk perintah migrasi
  krc terjemah --help   bantuan untuk perintah terjemah
"""

MIGRASI_USAGE = """Pemakaian:
  krc migrasi BERKAS...
  krc migrasi DIR --semua
  krc migrasi BERKAS... --dialek KODE
  krc migrasi BERKAS... --kering

  --dialek KODE   header yang ditambahkan (default: siulak)
  --semua         migrasi setiap berkas .krc di dalam DIR
  --kering        tampilkan rencana, jangan tulis apa pun
  -h, --help      tampilkan bantuan ini

Menambahkan `# dialek: KODE` sebagai baris pertama, lalu mengikuti impor
literal (`ambik "berkas"`) secara rekursif. Berkas yang sudah punya header
tidak ditulis ulang. Perintah ini tidak menjalankan program.

Exit: 0 berhasil, 1 satu berkas ditolak, 2 kesalahan pemakaian."""

TERJEMAH_USAGE = """Pemakaian:
  krc terjemah BERKAS --ke KODE
  krc terjemah BERKAS --ke KODE --out BERKAS-BARU
  krc terjemah BERKAS --ke KODE --out BERKAS-BARU --kering
  krc terjemah BERKAS --ke KODE --dari KODE

  --ke KODE       dialek tujuan (wajib)
  --dari KODE     dialek sumber bila berkas tidak punya header (default: siulak)
  --out BERKAS    tulis hasil ke berkas ini; tanpa --out, hasil ke stdout
  --kering        dengan --out, periksa saja dan jangan tulis apa pun
  -h, --help      tampilkan bantuan ini

Menerjemahkan kata kunci, operator kata, nama bawaan, dan argumen mode `bukak`
langsung. Nama buatan pengguna, komentar, teks, angka, dan tata letak tidak
diubah. Perintah menolak terjemahan bila dialek tujuan tidak memiliki ID yang
dipakai, bila nama pengguna bentrok dengan kata tujuan, atau bila string mode/
tipe tidak bisa diterjemahkan tanpa mengubah arti. Perintah ini tidak
menjalankan program.

Exit: 0 berhasil, 1 berkas ditolak, 2 kesalahan pemakaian."""

OPENERS, CLOSERS = {"(", "{", "["}, {")", "}", "]"}


def is_incomplete(src, vocab=None):
    """True while a ( { [ or block is still open, so the REPL keeps reading."""
    depth = 0
    for kind, text, _ in tokenize(src, vocab):
        if kind == "OP":
            depth += text in OPENERS
            depth -= text in CLOSERS
    return depth > 0


def repl(vocab=None):
    env = new_global(vocab)
    context = current_context()
    if context is not None:
        context.started = True          # a strict failure must not swallow input
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


def _parse_argv(argv):
    """Split flags from the file/code arguments; `-c` keeps its code intact."""
    dialect, strict, rest = None, False, []
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--dialek":
            if index + 1 >= len(argv):
                raise ValueError("--dialek butuh kode dialek")
            dialect = argv[index + 1]
            index += 2
            continue
        if arg.startswith("--dialek="):
            dialect = arg.split("=", 1)[1]
            if not dialect:
                raise ValueError("--dialek butuh kode dialek")
            index += 1
            continue
        if arg == "--ketat":
            strict = True
            index += 1
            continue
        if arg == "-c":
            rest.append(arg)
            if index + 1 < len(argv):
                rest.append(argv[index + 1])
                index += 2
            else:
                index += 1
            continue
        if arg.startswith("-") and arg not in ("-h", "--help", "-V", "--version"):
            raise ValueError("opsi tidak dikenal: %s" % arg)
        rest.append(arg)
        index += 1
    return dialect, strict, rest


# ---- krc migrasi ----------------------------------------------------------
def _migrasi_options(argv):
    """Parse the migrasi subcommand; the normal-run flags do not apply."""
    options = {"dialect": None, "dry": False, "semua": False,
               "help": False, "targets": []}
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg in ("-h", "--help"):
            options["help"] = True
            return options
        if arg == "--dialek":
            if index + 1 >= len(argv):
                raise ValueError("--dialek butuh kode dialek")
            options["dialect"] = argv[index + 1]
            index += 2
            continue
        if arg.startswith("--dialek="):
            code = arg.split("=", 1)[1]
            if not code:
                raise ValueError("--dialek butuh kode dialek")
            options["dialect"] = code
            index += 1
            continue
        if arg == "--semua":
            options["semua"] = True
            index += 1
            continue
        if arg == "--kering":
            options["dry"] = True
            index += 1
            continue
        if arg in ("--ketat", "-c", "-V", "--version"):
            raise ValueError("%s tidak berlaku untuk migrasi" % arg)
        if arg.startswith("-"):
            raise ValueError("opsi tidak dikenal: %s" % arg)
        options["targets"].append(arg)
        index += 1
    return options


def _migrasi_display(path):
    try:
        relative = os.path.relpath(path)
    except ValueError:                       # different drive on Windows
        return path
    return path if relative.startswith("..") else relative


def _migrasi_newline(text):
    index = text.find("\n")
    if index > 0 and text[index - 1] == "\r":
        return "\r\n"
    return "\n"


def _migrasi_write(path, raw, header):
    """Atomically put `header` before the original bytes."""
    directory = os.path.dirname(path) or "."
    try:
        mode = os.stat(path).st_mode
    except OSError:
        mode = None
    handle, temporary = tempfile.mkstemp(prefix=".krc-migrasi-", dir=directory)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(header.encode("utf-8"))
            stream.write(raw)
        if mode is not None:
            os.chmod(temporary, mode)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _migrasi_imports(node):
    """Literal `ambik` names and whether a non-literal import was found."""
    literals, dynamic = [], []

    def walk(value):
        if isinstance(value, tuple):
            if value and value[0] == "import":
                expression = value[1]
                if (isinstance(expression, tuple) and len(expression) == 2
                        and expression[0] == "lit"
                        and isinstance(expression[1], str)):
                    literals.append(expression[1])
                else:
                    dynamic.append(True)
                return
            for item in value[1:]:
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(node)
    return literals, bool(dynamic)


def _migrasi_resolve_import(base, name):
    path = os.path.join(base, name)
    candidates = [path] if path.endswith(".krc") else [path, path + ".krc"]
    for candidate in candidates:
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)
    return None


def _migrasi_walk(root):
    for directory, subdirectories, files in os.walk(root):
        subdirectories[:] = sorted(
            name for name in subdirectories if name not in ("__pycache__", ".git"))
        for name in sorted(files):
            if name.endswith(".krc"):
                yield os.path.join(directory, name)


def _migrasi_visit(path, context, dry_run, report):
    real = os.path.realpath(os.path.abspath(path))
    key = os.path.normcase(real)
    if key in report["seen"]:
        return
    report["seen"].add(key)
    display = _migrasi_display(real)

    try:
        with open(real, "rb") as stream:
            raw = stream.read()
    except OSError as err:
        report["errors"].append((display, "tidak bisa dibaca: %s" % err))
        return
    if raw.startswith(b"\xef\xbb\xbf"):
        report["errors"].append(
            (display, "tidak bisa dimigrasi: berkas memakai BOM UTF-8"))
        return
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as err:
        report["errors"].append((display, "bukan teks UTF-8: %s" % err))
        return

    line = text.split("\n", 1)[0].rstrip("\r")
    code = None
    has_header = False
    if HEADER_HINT_RE.match(line):
        match = HEADER_RE.match(line)
        if not match:
            report["errors"].append(
                (display, "baris 1 memuat header dialek yang tidak valid"))
            return
        code = match.group(1)
        has_header = True

    try:
        vocab = (resolve_dialect(code, context) if has_header
                 else context.default_vocab)
    except LangError as err:
        report["errors"].append(
            (display, "dialek header tidak bisa dimuat: %s" % err))
        return

    try:
        program = Parser(tokenize(text, vocab), vocab).program()
    except LangError as err:
        report["errors"].append((display, "tidak bisa diurai: %s" % err))
        return

    literals, dynamic = _migrasi_imports(program)
    if dynamic:
        report["errors"].append(
            (display, "impor non-literal tidak bisa diikuti"))

    if has_header:
        report["skipped"].append(display)
    else:
        header = "# dialek: %s%s" % (context.default_vocab.code,
                                     _migrasi_newline(text))
        if dry_run:
            report["migrated"].append(display)
        else:
            try:
                _migrasi_write(real, raw, header)
            except OSError as err:
                report["errors"].append((display, "tidak bisa ditulis: %s" % err))
                return
            report["migrated"].append(display)

    base = os.path.dirname(real)
    for name in literals:
        target = _migrasi_resolve_import(base, name)
        if target is None:
            report["errors"].append(
                (display, "impor tidak ditemukan: %s" % name))
            continue
        _migrasi_visit(target, context, dry_run, report)


def migrasi_main(argv=None, dialect_root=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        options = _migrasi_options(argv)
    except ValueError as err:
        print("migrasi: %s" % err, file=sys.stderr)
        return 2
    if options["help"]:
        print(MIGRASI_USAGE)
        return 0

    targets = options["targets"]
    if options["semua"]:
        if len(targets) != 1:
            print("migrasi: --semua butuh tepat satu direktori", file=sys.stderr)
            return 2
        if not os.path.isdir(targets[0]):
            print("migrasi: bukan direktori: %s" % targets[0], file=sys.stderr)
            return 2
    else:
        if not targets:
            print("migrasi: butuh berkas .krc", file=sys.stderr)
            return 2
        for target in targets:
            if not os.path.isfile(target):
                print("migrasi: berkas tidak ditemukan: %s" % target,
                      file=sys.stderr)
                return 2
            if not target.endswith(".krc"):
                print("migrasi: bukan berkas .krc: %s" % target,
                      file=sys.stderr)
                return 2

    context = RunContext(LEGACY, dialect_root, False)
    try:
        context.default_vocab = resolve_dialect(options["dialect"] or "siulak",
                                               context)
    except LangError as err:
        print("migrasi: %s" % err, file=sys.stderr)
        return 2

    report = {"migrated": [], "skipped": [], "errors": [], "seen": set()}
    try:
        with use_context(context):
            if options["semua"]:
                for path in _migrasi_walk(targets[0]):
                    _migrasi_visit(path, context, options["dry"], report)
            else:
                for path in targets:
                    _migrasi_visit(path, context, options["dry"], report)
    finally:
        close_all_files()

    for path in report["migrated"]:
        if options["dry"]:
            print("migrasi: would add header to %s" % path)
        else:
            print("migrasi: added header to %s" % path)
    for path in report["skipped"]:
        print("migrasi: already has a header: %s" % path)
    for path, message in report["errors"]:
        print("migrasi: error: %s: %s" % (path, message), file=sys.stderr)
    suffix = "" if len(report["errors"]) == 1 else "s"
    print("migrasi: %d %s, %d already had a header, %d error%s"
          % (len(report["migrated"]),
             "would migrate" if options["dry"] else "migrated",
             len(report["skipped"]), len(report["errors"]), suffix))
    return 1 if report["errors"] else 0


# ---- krc terjemah ---------------------------------------------------------
class _TerjemahRefusal(Exception):
    """A translation that would not be lossless."""


def _terjemah_words(vocab):
    """Every non-message word of one vocabulary, without fallback notifications."""
    dialect = getattr(vocab, "dialect", None)
    if dialect is not None:
        return dict(dialect.words)
    return {id: vocab.word(id) for id in CATALOG["ids"]
            if not id.startswith("msg.")}


def _terjemah_maps(words):
    maps = {}
    for prefix in ("kw.", "op.", "fn.", "reserved.", "mode.", "type."):
        maps[prefix] = {word: id for id, word in words.items()
                        if id.startswith(prefix)}
    return maps


def _terjemah_owns(vocab, id):
    """True when the target chain supplies the ID itself, not the English base."""
    dialect = getattr(vocab, "dialect", None)
    if dialect is None or dialect.code == "base":
        return True
    return id not in dialect.base_ids


def _terjemah_symbols(program):
    """Every name the file declares, from the AST."""
    names = set()

    def walk(value):
        if isinstance(value, tuple) and value:
            tag = value[0]
            if tag in ("var", "assign") and len(value) > 1 and isinstance(value[1], str):
                names.add(value[1])
            elif tag == "func" and len(value) > 2:
                names.add(value[1])
                names.update(name for name in value[2] if isinstance(name, str))
            elif tag == "for" and len(value) > 1 and isinstance(value[1], str):
                names.add(value[1])
            elif tag == "try" and len(value) > 2 and isinstance(value[2], str):
                names.add(value[2])
            for item in value[1:]:
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(program)
    return names


def _terjemah_header_parts(text):
    """(code, match) for a valid line-1 header, or (None, None)."""
    line = text.split("\n", 1)[0].rstrip("\r")
    if not HEADER_HINT_RE.match(line):
        return None, None
    match = HEADER_RE.match(line)
    if not match:
        raise _TerjemahRefusal("baris 1 memuat header dialek yang tidak valid")
    return match.group(1), match


def _terjemah_header_text(text, match, code):
    """Replace the header code in place, or prepend a new header."""
    if match is None:
        return "# dialek: %s%s%s" % (code, _migrasi_newline(text), text)
    return text[:match.start(1)] + code + text[match.end(1):]


def _terjemah_apply(text, edits):
    if not edits:
        return text
    pieces, last = [], 0
    for start, end, replacement in sorted(edits):
        if start < last:
            raise _TerjemahRefusal("internal: tumpang tindih hasil terjemahan")
        pieces.append(text[last:start])
        pieces.append(replacement)
        last = end
    pieces.append(text[last:])
    return "".join(pieces)


def _terjemah_stdout(text):
    """Write exact bytes, avoiding Windows' newline translation on stdout."""
    data = text.encode("utf-8")
    stream = getattr(sys.stdout, "buffer", None)
    if stream is None:
        sys.stdout.write(text)
        return
    sys.stdout.flush()
    stream.write(data)
    stream.flush()


def _terjemah_write(path, text):
    """Atomically write UTF-8 text, preserving the destination's mode."""
    directory = os.path.dirname(os.path.abspath(path)) or "."
    try:
        mode = os.stat(path).st_mode
    except OSError:
        mode = None
    handle, temporary = tempfile.mkstemp(prefix=".krc-terjemah-", dir=directory)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(text.encode("utf-8"))
        if mode is not None:
            os.chmod(temporary, mode)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def rewrite_dialect_words(text, source_vocab, target_vocab):
    """Map code words by neutral ID for a tutorial build.

    Unlike `terjemah`, this never refuses: a target without a word uses its
    base fallback. Comments, ordinary strings, user names, and formatting are
    untouched. Returns the new text and the set of IDs that were used.
    """
    edits, used, _problems, _lines = _terjemah_scan(
        text, _terjemah_words(source_vocab), _terjemah_words(target_vocab))
    return _terjemah_apply(text, edits), used


def dialect_declared_names(text, vocab):
    """The names a snippet declares, parsed with `vocab`; never runs it."""
    program = Parser(tokenize(text, vocab), vocab).program()
    return _terjemah_symbols(program)


def _terjemah_scan(text, source_words, target_words):
    """Classify every token and return edits, used IDs, and string refusals."""
    source = _terjemah_maps(source_words)
    target = _terjemah_maps(target_words)
    edits, used, problems = [], set(), []
    lines = {}
    stack = []                      # {"call": bool, "open": bool, "arg": int}
    previous = None
    line = 1

    for match in MASTER.finditer(text):
        kind, piece = match.lastgroup, match.group()
        if kind in ("SKIP", "COMMENT"):
            line += piece.count("\n")
            continue
        if kind == "BAD":
            continue                       # tokenize() already rejected the file
        start, end = match.start(), match.end()

        if kind == "IDENT":
            lines.setdefault(piece, line)
            keyword = source["kw."].get(piece)
            operator = source["op."].get(piece)
            reserved = source["reserved."].get(piece)
            builtin = source["fn."].get(piece)
            if keyword is not None:
                token_id = keyword
            elif operator is not None:
                token_id = operator
            elif reserved is not None:
                token_id = None            # unreachable: tokenize() refuses it
            elif builtin is not None:
                token_id = builtin
            else:
                token_id = None
            if token_id is not None:
                used.add(token_id)
                replacement = target_words[token_id]
                if replacement != piece:
                    edits.append((start, end, replacement))
        elif kind == "STRING":
            value = unescape(piece[1:-1], line)
            mode_id = source["mode."].get(value)
            type_id = source["type."].get(value)
            top = stack[-1] if stack else None
            if mode_id is not None:
                if top is not None and top["open"] and top["arg"] == 1:
                    used.add(mode_id)
                    replacement = target_words[mode_id]
                    if replacement != value:
                        edits.append((start, end, '"%s"' % replacement))
                elif target_words[mode_id] != value:
                    problems.append(
                        "baris %d: string mode %r tidak bisa diterjemahkan "
                        "di posisi ini" % (line, value))
            elif type_id is not None and target_words[type_id] != value:
                problems.append(
                    "baris %d: string tipe %r tidak bisa diterjemahkan "
                    "di posisi ini" % (line, value))
        elif kind == "OP":
            if piece in ("(", "[", "{"):
                is_call = (piece == "(" and previous is not None
                           and previous[0] == "IDENT")
                is_open = (is_call and source["fn."].get(previous[1]) == "fn.open")
                stack.append({"call": is_call, "open": is_open, "arg": 0})
            elif piece in (")", "]", "}"):
                if stack:
                    stack.pop()
            elif piece == "," and stack and stack[-1]["call"]:
                stack[-1]["arg"] += 1

        previous = (kind, piece, line)
    return edits, used, problems, lines


def _terjemah_translate(text, program, source_vocab, target_vocab,
                        header_match):
    """Return (new_text, warnings) or raise `_TerjemahRefusal`."""
    source_words = _terjemah_words(source_vocab)
    target_words = _terjemah_words(target_vocab)

    if source_vocab.code == target_vocab.code:
        return _terjemah_header_text(text, header_match, target_vocab.code), []

    edits, used, problems, lines = _terjemah_scan(text, source_words, target_words)
    symbols = _terjemah_symbols(program)
    source = _terjemah_maps(source_words)
    target = _terjemah_maps(target_words)

    for token_id in sorted(used):
        if not _terjemah_owns(target_vocab, token_id):
            problems.append("dialek tujuan %s tidak memiliki %s"
                            % (target_vocab.code, token_id))

    for name in sorted(symbols):
        if name in source["fn."]:
            problems.append(
                "nama pengguna %r menutupi bawaan %s; terjemahkan manual"
                % (name, source["fn."][name]))

    guarded = {}
    for prefix, label in (("kw.", "kata kunci"), ("op.", "operator"),
                          ("fn.", "bawaan"), ("reserved.", "kata simpanan")):
        for word, token_id in target[prefix].items():
            guarded.setdefault(word, (label, token_id))
    for name in sorted(symbols):
        if name in source["fn."]:
            continue
        if name in guarded:
            label, token_id = guarded[name]
            problems.append(
                "baris %d: nama pengguna %r bentrok dengan %s %s di dialek %s"
                % (lines.get(name, 1), name, label, token_id, target_vocab.code))

    if problems:
        raise _TerjemahRefusal("\n".join(problems))

    translated = _terjemah_apply(text, edits)
    return _terjemah_header_text(translated, header_match,
                                 target_vocab.code), []


def _terjemah_import_warnings(program, output):
    """Warn when a moved output would no longer find a literal import."""
    literals, _dynamic = _migrasi_imports(program)
    base = os.path.dirname(os.path.abspath(output))
    warnings = []
    for name in literals:
        if _migrasi_resolve_import(base, name) is None:
            warnings.append("impor %r tidak ditemukan dari direktori hasil"
                            % name)
    return warnings


def _terjemah_options(argv):
    options = {"ke": None, "dari": None, "out": None, "dry": False,
               "help": False, "targets": []}
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg in ("-h", "--help"):
            options["help"] = True
            return options
        matched = False
        for flag, key in (("--ke", "ke"), ("--dari", "dari"), ("--out", "out")):
            if arg == flag:
                if index + 1 >= len(argv):
                    raise ValueError("%s butuh nilai" % flag)
                options[key] = argv[index + 1]
                index += 2
                matched = True
                break
            if arg.startswith(flag + "="):
                value = arg.split("=", 1)[1]
                if not value:
                    raise ValueError("%s butuh nilai" % flag)
                options[key] = value
                index += 1
                matched = True
                break
        if matched:
            continue
        if arg == "--kering":
            options["dry"] = True
            index += 1
            continue
        if arg in ("--ketat", "--dialek", "--semua", "-c", "-V", "--version"):
            raise ValueError("%s tidak berlaku untuk terjemah" % arg)
        if arg.startswith("-"):
            raise ValueError("opsi tidak dikenal: %s" % arg)
        options["targets"].append(arg)
        index += 1
    return options


def terjemah_main(argv=None, dialect_root=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        options = _terjemah_options(argv)
    except ValueError as err:
        print("terjemah: %s" % err, file=sys.stderr)
        return 2
    if options["help"]:
        print(TERJEMAH_USAGE)
        return 0
    if not options["ke"]:
        print("terjemah: --ke KODE wajib diisi", file=sys.stderr)
        return 2
    targets = options["targets"]
    if len(targets) != 1:
        print("terjemah: butuh tepat satu berkas .krc", file=sys.stderr)
        return 2
    path = targets[0]
    if not os.path.isfile(path):
        print("terjemah: berkas tidak ditemukan: %s" % path, file=sys.stderr)
        return 2
    if not path.endswith(".krc"):
        print("terjemah: bukan berkas .krc: %s" % path, file=sys.stderr)
        return 2
    if options["dry"] and not options["out"]:
        print("terjemah: --kering butuh --out", file=sys.stderr)
        return 2
    if options["out"]:
        try:
            same = (os.path.normcase(os.path.realpath(path))
                    == os.path.normcase(os.path.realpath(options["out"])))
        except OSError:
            same = False
        if same:
            print("terjemah: --out tidak boleh sama dengan berkas masukan",
                  file=sys.stderr)
            return 2

    context = RunContext(LEGACY, dialect_root, False)
    with use_context(context):
        try:
            target_vocab = resolve_dialect(options["ke"], context)
        except LangError as err:
            print("terjemah: %s" % err, file=sys.stderr)
            return 2
        if options["dari"]:
            try:
                context.default_vocab = resolve_dialect(options["dari"], context)
            except LangError as err:
                print("terjemah: %s" % err, file=sys.stderr)
                return 2

        try:
            with open(path, "rb") as stream:
                raw = stream.read()
        except OSError as err:
            print("terjemah: error: %s: %s" % (path, err), file=sys.stderr)
            return 1
        if raw.startswith(b"\xef\xbb\xbf"):
            print("terjemah: error: %s: berkas memakai BOM UTF-8" % path,
                  file=sys.stderr)
            return 1
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as err:
            print("terjemah: error: %s: bukan teks UTF-8: %s" % (path, err),
                  file=sys.stderr)
            return 1

        try:
            header_code, header_match = _terjemah_header_parts(text)
            if header_code is None:
                source_vocab = context.default_vocab
            else:
                source_vocab = resolve_dialect(header_code, context)
            program = Parser(tokenize(text, source_vocab), source_vocab).program()
            result, warnings = _terjemah_translate(
                text, program, source_vocab, target_vocab, header_match)
            if options["out"]:
                warnings.extend(_terjemah_import_warnings(program, options["out"]))
        except _TerjemahRefusal as err:
            for line in str(err).splitlines():
                print("terjemah: error: %s: %s" % (path, line), file=sys.stderr)
            return 1
        except LangError as err:
            print("terjemah: error: %s: %s" % (path, err), file=sys.stderr)
            return 1

        for warning in warnings:
            print("terjemah: warning: %s: %s" % (path, warning),
                  file=sys.stderr)

        if not options["out"]:
            try:
                _terjemah_stdout(result)
            except BrokenPipeError:
                return 0
            return 0
        if options["dry"]:
            print("terjemah: would write %s (%s -> %s)"
                  % (options["out"], source_vocab.code, target_vocab.code))
            return 0
        try:
            _terjemah_write(options["out"], result)
        except OSError as err:
            print("terjemah: error: %s: %s" % (options["out"], err),
                  file=sys.stderr)
            return 1
        print("terjemah: wrote %s (%s -> %s)"
              % (options["out"], source_vocab.code, target_vocab.code))
        return 0


def main(argv=None, dialect_root=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "migrasi":
        return migrasi_main(argv[1:], dialect_root)
    if argv and argv[0] == "terjemah":
        return terjemah_main(argv[1:], dialect_root)
    try:
        dialect_code, strict, rest = _parse_argv(argv)
    except ValueError as err:
        print(f"Kesalahan: {err}", file=sys.stderr)
        return 2
    if rest and rest[0] in ("-h", "--help"):
        print(USAGE)
        return 0
    if rest and rest[0] in ("-V", "--version"):
        print(f"KerinciLang {__version__}")
        return 0
    if rest and rest[0] == "-c":
        if len(rest) != 2:
            print("Kesalahan: -c butuh satu potong kode", file=sys.stderr)
            return 2
    elif len(rest) > 1:
        print("Kesalahan: argumen terlalu banyak", file=sys.stderr)
        return 2

    context = RunContext(LEGACY, dialect_root, strict)
    try:
        with use_context(context):
            if dialect_code is not None:
                try:
                    context.default_vocab = resolve_dialect(dialect_code, context)
                except LangError as err:
                    print(f"Kesalahan: {err}", file=sys.stderr)
                    return 2
            try:
                if not rest:
                    code = repl(context.default_vocab)
                    return 2 if context.strict_failed else code
                if rest[0] == "-c":
                    if len(rest) < 2:
                        print("Kesalahan: -c butuh kode", file=sys.stderr)
                        return 2
                    run_source(rest[1], vocab=context.default_vocab)
                else:
                    run_file(rest[0], vocab=context.default_vocab)
            except LangError as err:
                print(f"Kesalahan: {err}", file=sys.stderr)
                return 1
            except FileNotFoundError:
                print(f"Kesalahan: berkas tidak ditemukan: {rest[0]}", file=sys.stderr)
                return 2
            except UnicodeDecodeError:
                print("Kesalahan: berkas harus berupa teks UTF-8", file=sys.stderr)
                return 2
            except KeyboardInterrupt:
                print("\nDihentikan.", file=sys.stderr)
                return 130
            except BrokenPipeError:          # e.g. `krc program.krc | head`
                sys.stderr.close()
                return 0
    finally:
        close_all_files()
    if context.strict_failed:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
