"""Tests for the neutral ID catalogue, the vocabulary seam, and packaging.

Run with: python3 tests/test_ids.py
"""
import ast
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipapp

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import kerincilang  # noqa: E402
from kerincilang import (  # noqa: E402
    CATALOG, LEGACY, LEGACY_OPERATORS, LEGACY_WORDS, Vocabulary,
    close_all_files, current_vocab, run_source, show,
)

FAILED = []


def check(ok, label, detail=""):
    print("PASS" if ok else "FAIL", label, "" if ok else "-> " + str(detail))
    if not ok:
        FAILED.append(label)


IDS = CATALOG["ids"]
SAMPLE = {"line": 1, "c": "q", "text": "'x'", "what": "'IDENT'", "word": "w",
          "try_word": "t", "catch_word": "c", "name": "n", "var_word": "v",
          "const_word": "k", "op": "o", "left": "l", "right": "r", "key": "k",
          "index": 1, "length": 2, "range_fn": "r", "for_word": "f", "in_word": "i",
          "fn": "f", "count": 1, "max": 9, "value": "v", "target": "t", "path": "p",
          "reason": "r", "read": "r", "write": "w", "append": "a", "kw": "k",
          "message": "m", "arity": 1, "open_fn": "o", "mode": "m", "separator": "s"}


# ---- catalogue integrity --------------------------------------------------
def test_catalogue():
    check(CATALOG["core"] == "0.6", "catalogue core version", CATALOG["core"])
    required = {"namespace", "tier", "en", "id_gloss", "description", "example",
                "arity", "placeholders"}
    bad = [id for id, entry in IDS.items() if set(entry) != required]
    check(not bad, "every ID has exactly the required fields", bad)

    allowed = {"kw", "op", "fn", "type", "mode", "msg", "reserved"}
    bad = [id for id, entry in IDS.items()
           if entry["namespace"] not in allowed or entry["namespace"] != id.split(".")[0]]
    check(not bad, "namespace matches the ID prefix", bad)
    check("val" not in {entry["namespace"] for entry in IDS.values()},
          "val.* is not used (decision D1)")

    bad = [id for id, entry in IDS.items() if entry["tier"] not in (1, 2, 3)]
    check(not bad, "every tier is 1, 2, or 3", bad)

    bad = []
    for id, entry in IDS.items():
        if id.startswith("fn."):
            if not (entry["arity"] is None or isinstance(entry["arity"], int)):
                bad.append(id)
        elif entry["arity"] is not None:
            bad.append(id)
    check(not bad, "arity is an int for fn.* and null elsewhere", bad)

    name = re.compile(r"^[a-z][a-z0-9_]*$")
    bad = []
    for id, entry in IDS.items():
        if not isinstance(entry["placeholders"], list):
            bad.append(id)
            continue
        for placeholder in entry["placeholders"]:
            if not name.match(placeholder):
                bad.append((id, placeholder))
    check(not bad, "placeholder names are well formed", bad)

    bad = []
    for id, entry in IDS.items():
        if not isinstance(entry["placeholders"], list):
            continue
        found_id = set(re.findall(r"\{([a-z][a-z0-9_]*)\}", entry["id_gloss"]))
        found_en = set(re.findall(r"\{([a-z][a-z0-9_]*)\}", entry["en"]))
        if found_id != set(entry["placeholders"]) or found_en != set(entry["placeholders"]):
            bad.append(id)
    check(not bad, "en and id_gloss use exactly the declared placeholders", bad)

    bad = []
    for id, entry in IDS.items():
        if not id.startswith("msg."):
            continue
        args = {p: str(SAMPLE.get(p, "x")) for p in entry["placeholders"]}
        try:
            rendered = entry["id_gloss"].format(**args)
        except (KeyError, IndexError, ValueError) as err:
            bad.append((id, str(err)))
            continue
        if "{" in rendered or "}" in rendered:
            bad.append((id, "unfilled placeholder"))
    check(not bad, "every message renders with sample arguments", bad)

    counts = {}
    for entry in IDS.values():
        counts[entry["namespace"]] = counts.get(entry["namespace"], 0) + 1
    expected = {"kw": 26, "op": 6, "fn": 24, "type": 9, "mode": 3, "reserved": 1}
    for namespace, count in expected.items():
        check(counts.get(namespace) == count,
              "namespace %s has %d IDs" % (namespace, count), counts.get(namespace))
    check(counts.get("msg", 0) >= 60, "the message catalogue covers every raise site",
          counts.get("msg"))


# ---- the vocabulary seam --------------------------------------------------
def test_legacy_covers_catalogue():
    missing = []
    for id, entry in IDS.items():
        if entry["namespace"] == "msg":
            continue
        try:
            LEGACY.word(id)
        except KeyError:
            missing.append(id)
    check(not missing, "LegacySiulak maps every live word ID", missing)

    known = dict(LEGACY_WORDS)
    known.update({id: pair[0] for id, pair in LEGACY_OPERATORS.items()})
    unknown = [id for id in known if id not in IDS]
    check(not unknown, "no legacy word points at an unknown ID", unknown)


def test_namespace_matrix():
    kw_words = [LEGACY.word(id) for id in IDS if id.startswith("kw.")]
    op_words = [LEGACY.word(id) for id in IDS if id.startswith("op.")]
    fn_words = [LEGACY.word(id) for id in IDS if id.startswith("fn.")]

    check(len(set(kw_words)) == len(kw_words), "keyword words are unique")
    check(len(set(op_words)) == len(op_words), "comparison words are unique")
    check(not set(kw_words) & set(op_words), "keywords and comparison words are disjoint")
    check(not set(fn_words) & set(kw_words), "built-in words are disjoint from keywords")
    check(not set(fn_words) & set(op_words),
          "built-in words are disjoint from comparison words")

    # These overlaps are intentional in Siulak 0.5 and must stay allowed.
    for word in ("guno", "kosong", "kato", "peta", "bilangan", "daftar", "pecahan"):
        namespaces = {id.split(".")[0] for id, entry in IDS.items()
                      if entry["namespace"] != "msg" and LEGACY.word(id) == word}
        check(len(namespaces) > 1, "overlap allowed: %r spans %s" % (word, sorted(namespaces)))

    check(len(set(LEGACY.surface().values())) == len(LEGACY.surface()),
          "the legacy surface map is one word per keyword")


# ---- a synthetic dialect proves the engine is neutral ---------------------
class Synthetic(Vocabulary):
    code = "synthetic"

    def __init__(self, prefix="z", truth=None, types=None):
        truth, types = truth or {}, types or {}
        self._words = {}
        for id, entry in IDS.items():
            namespace = entry["namespace"]
            short = id.split(".", 1)[1]
            if namespace == "kw":
                self._words[id] = truth.get(id, prefix + short)
            elif namespace == "fn":
                self._words[id] = prefix + short
            elif namespace in ("type", "mode", "reserved"):
                self._words[id] = types.get(id, prefix + short)
        self._operators = {id: (prefix + id.split(".", 1)[1], symbol)
                           for id, (word, symbol) in LEGACY_OPERATORS.items()}
        self._modes = {word: id for id, word in self._words.items()
                       if id.startswith("mode.")}
        self._reserved = {word for id, word in self._words.items()
                          if id.startswith("reserved.")}
        self._templates = {id: entry["en"] for id, entry in IDS.items()
                           if id.startswith("msg.")}

    def word(self, id):
        if id in self._words:
            return self._words[id]
        if id in self._operators:
            return self._operators[id][0]
        raise KeyError(id)

    def message(self, id, args=None):
        return self._templates[id].format(**(args or {}))

    def mode_id(self, word):
        return self._modes.get(word)

    def surface(self):
        return {self._words[id]: id for id in self._words if id.startswith("kw.")}

    def operators(self):
        return {pair[0]: pair[1] for pair in self._operators.values()}

    def reserved(self):
        return set(self._reserved)


def run_capture(src, vocab=None):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        run_source(src, vocab=vocab)
    return buf.getvalue()


def test_synthetic_program():
    v = Synthetic()
    w = v.word
    with tempfile.TemporaryDirectory() as tmp:
        folder = tmp.replace("\\", "/")
        src = "\n".join([
            '%s xs = %s(1, 2, 3)' % (w("kw.var"), w("fn.list")),
            '%s %s(xs)' % (w("kw.print"), w("fn.type")),
            '%s m = %s(%s("a", 1))' % (w("kw.var"), w("fn.map"), w("fn.list")),
            '%s m["a"]' % w("kw.print"),
            '%s add(a, b) { %s a + b }' % (w("kw.func"), w("kw.return")),
            '%s add(2, 3)' % w("kw.print"),
            '%s xs[0] %s 1 { %s "one" } %s { %s "other" }'
            % (w("kw.if"), w("op.eq"), w("kw.print"), w("kw.else"), w("kw.print")),
            '%s i %s xs { %s i }' % (w("kw.for"), w("kw.in"), w("kw.print")),
            '%s n = 0' % w("kw.var"),
            '%s xs[0] %s 5 { %s "looping" xs[0] = 5 }'
            % (w("kw.while"), w("op.lt"), w("kw.print")),
            '%s { %s "boom" } %s e { %s e }'
            % (w("kw.try"), w("kw.raise"), w("kw.catch"), w("kw.print")),
            '%s %s' % (w("kw.print"), w("kw.true")),
            '%s %s' % (w("kw.print"), w("kw.false")),
            '%s %s' % (w("kw.print"), w("kw.null")),
            '%s %s %s %s "block" %s'
            % (w("kw.if"), w("kw.true"), w("kw.begin"), w("kw.print"), w("kw.end")),
            '%s %s %s %s { %s "and" }'
            % (w("kw.if"), w("kw.true"), w("kw.and"), w("kw.true"), w("kw.print")),
            '%s %s %s { %s "or" }'
            % (w("kw.if"), w("kw.not"), w("kw.false"), w("kw.print")),
            '%s %s %s %s { %s "or2" }'
            % (w("kw.if"), w("kw.false"), w("kw.or"), w("kw.true"), w("kw.print")),
            '%s f = %s("%s/a.txt", "%s")'
            % (w("kw.var"), w("fn.open"), folder, w("mode.write")),
            '%s(f, "hi")' % w("fn.write"),
            '%s(f)' % w("fn.close"),
            '%s %s("%s/a.txt")' % (w("kw.print"), w("fn.read"), folder),
            '%s %s(%s(1, 2, 3, 4, 5))'
            % (w("kw.print"), w("fn.length"), w("fn.list")),
            '%s %s("a,b", ",")' % (w("kw.print"), w("fn.split")),
            '%s %s(%s("a", "b"), "-")'
            % (w("kw.print"), w("fn.join"), w("fn.list")),
            '%s %s(%s(1, 2))' % (w("kw.print"), w("fn.sort"), w("fn.list")),
            '%s %s(%s(1, 2))' % (w("kw.print"), w("fn.reverse"), w("fn.list")),
            '%s %s(3)' % (w("kw.print"), w("fn.range")),
            '%s %s("42")' % (w("kw.print"), w("fn.int")),
            '%s %s("2.5")' % (w("kw.print"), w("fn.float")),
            '%s %s(1)' % (w("kw.print"), w("fn.text")),
            '%s %s(%s())' % (w("kw.print"), w("fn.length"), w("fn.map")),
        ])
        got = run_capture(src, vocab=v)
        close_all_files()
    expected = "\n".join([
        w("type.list"), "1", "5", "one", "1", "2", "3", "looping", "boom",
        w("kw.true"), w("kw.false"), w("kw.null"), "block", "and", "or", "or2",
        "hi", "5", '["a", "b"]', "a-b", "[1, 2]", "[2, 1]", "[0, 1, 2]",
        "42", "2.5", "1", "0",
    ]) + "\n"
    check(got == expected, "a fully synthetic dialect runs the whole language",
          repr(got) if got != expected else "")

    check(show(True, v) == w("kw.true") and show(False, v) == w("kw.false")
          and show(None, v) == w("kw.null"),
          "show() uses the active vocabulary")
    check(current_vocab().code == "siulak", "the vocabulary stack is balanced after a run")


def test_second_synthetic_dialect():
    v = Synthetic(
        prefix="q",
        truth={"kw.true": "benar", "kw.false": "salah", "kw.null": "nihil"},
        types={"type.int": "angka", "type.str": "teks", "type.bool": "logika",
               "type.list": "senarai", "type.map": "kamus", "type.float": "desimal",
               "type.null": "nihil", "type.file": "fail", "type.func": "fungsi"},
    )
    w = v.word
    src = "\n".join([
        '%s %s(1)' % (w("kw.print"), w("fn.type")),
        '%s %s("%s")' % (w("kw.print"), w("fn.type"), "x"),
        '%s %s(%s)' % (w("kw.print"), w("fn.type"), w("kw.true")),
        '%s %s' % (w("kw.print"), w("kw.true")),
        '%s %s' % (w("kw.print"), w("kw.false")),
        '%s %s' % (w("kw.print"), w("kw.null")),
    ])
    got = run_capture(src, vocab=v)
    expected = "\n".join(["angka", "teks", "logika", "benar", "salah", "nihil"]) + "\n"
    check(got == expected, "a second dialect changes output words", repr(got))

    # Errors come from the dialect too: the neutral English template here.
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            run_source("%s 1 / 0" % w("kw.print"), vocab=v)
        check(False, "division by zero raises", "no error")
    except kerincilang.LangError as err:
        check(str(err) == "Division by zero", "error text comes from the dialect", str(err))
        check(err.msg_id == "msg.value.div_zero", "LangError keeps msg_id", err.msg_id)
        check(err.args[0] == "Division by zero", "LangError.args[0] is still the text")

    # The same program in Siulak keeps the Indonesian text.
    try:
        run_source("nyetak 1 / 0")
        check(False, "siulak division by zero raises", "no error")
    except kerincilang.LangError as err:
        check(str(err) == "Pembagian dengan nol", "siulak keeps the v0.5 message", str(err))


# ---- the engine contains no dialect word and no stray message ID ----------
def test_ast_scans():
    path = os.path.join(ROOT, "kerincilang.py")
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())

    offenders, msg_ids = [], []

    def walk(node, function):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function = node.name
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "LangError":
                arg = node.args[0] if node.args else None
                is_msg = (isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name)
                          and arg.func.id == "msg")
                if not is_msg and function != "run":
                    offenders.append((function, getattr(node, "lineno", 0)))
            if node.func.id == "msg":
                arg = node.args[0] if node.args else None
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    msg_ids.append(arg.value)
                else:
                    offenders.append((function, "non-literal msg id"))
        for child in ast.iter_child_nodes(node):
            walk(child, function)

    walk(tree, "<module>")
    check(not offenders, "every internal LangError is built from a catalogue message",
          offenders)
    check(all(id in IDS for id in msg_ids), "every msg() ID exists in the catalogue",
          sorted({id for id in msg_ids if id not in IDS}))
    check(len(set(msg_ids)) >= 60, "the catalogue is actually used", len(set(msg_ids)))


# ---- packaging: the data travels with the program -------------------------
def test_packaging():
    with tempfile.TemporaryDirectory() as build:
        build = os.path.abspath(build)
        source = os.path.join(build, "src")
        os.makedirs(source)
        shutil.copy(os.path.join(ROOT, "kerincilang.py"), os.path.join(source, "kerincilang.py"))
        shutil.copytree(os.path.join(ROOT, "core"), os.path.join(source, "core"))
        shutil.copytree(os.path.join(ROOT, "dialects"), os.path.join(source, "dialects"))
        with open(os.path.join(source, "__main__.py"), "w", encoding="utf-8") as handle:
            handle.write("import sys\nfrom kerincilang import main\nsys.exit(main())\n")
        pyz = os.path.join(build, "krc.pyz")
        zipapp.create_archive(source, pyz, interpreter="/usr/bin/env python3")

        work = os.path.join(build, "elsewhere")
        os.makedirs(work)
        program = os.path.join(work, "p.krc")
        with open(program, "w", encoding="utf-8") as handle:
            handle.write('nyetak "dari pyz"\nnyetak mecem(1)\n')

        result = subprocess.run([sys.executable, pyz, program], cwd=work,
                                capture_output=True, text=True)
        check(result.returncode == 0 and result.stdout == "dari pyz\nbilangan\n",
              "krc.pyz runs from a directory with no checkout",
              (result.returncode, result.stdout, result.stderr))

        result = subprocess.run([sys.executable, pyz, "-c", "nyetak 1 + 1"], cwd=work,
                                capture_output=True, text=True)
        check(result.returncode == 0 and result.stdout == "2\n",
              "krc.pyz handles -c", (result.returncode, result.stdout, result.stderr))


# ---- the single-file entry point still works ------------------------------
def test_entry_point():
    result = subprocess.run([sys.executable, os.path.join(ROOT, "kerincilang.py"),
                             "-c", "nyetak mecem(betul)"],
                            cwd=tempfile.gettempdir(), capture_output=True, text=True)
    check(result.returncode == 0 and result.stdout == "boolean\n",
          "python kerincilang.py still runs", (result.returncode, result.stdout,
                                               result.stderr))


def main():
    test_catalogue()
    test_legacy_covers_catalogue()
    test_namespace_matrix()
    test_synthetic_program()
    test_second_synthetic_dialect()
    test_ast_scans()
    test_packaging()
    test_entry_point()
    print("\nFAILED:" if FAILED else "\nALL PASSED", len(FAILED) or "")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
