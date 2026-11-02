"""Tests for the dialect file model: loading, inheritance, validation, the CLI.

Run with: python3 tests/test_dialects.py
"""
import contextlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipapp

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import cek_dialek  # noqa: E402
import kerincilang  # noqa: E402
from dialects import loader  # noqa: E402
from dialects.loader import (  # noqa: E402
    DialectError, base_dialect, load_dialect, validate_dialect, available_dialects,
)
from kerincilang import run_source  # noqa: E402

FAILED = []
IDS = kerincilang.CATALOG["ids"]


def check(ok, label, detail=""):
    print("PASS" if ok else "FAIL", label, "" if ok else "-> " + str(detail))
    if not ok:
        FAILED.append(label)


def codes_of(problems):
    return [p.code for p in problems]


def blocking(problems):
    return [p for p in problems if p.blocking]


def valid(**over):
    """A minimal, valid draft dialect."""
    data = {
        "code": "uji",
        "name": "Uji",
        "status": "draft",
        "core": "0.6",
        "revision": 1,
        "parent": None,
        "license": "CC BY-SA 4.0",
        "maintainer": "Penguji",
        "reviewer": None,
        "sources": ["uji, 2026"],
        "orthography": "test spelling",
        "words": {"kw.print": "cetak"},
        "messages": {},
    }
    data.update(over)
    return data


def write(root, code, data=None, raw=None):
    path = pathlib.Path(root) / (code + ".json")
    path.write_text(raw if raw is not None else json.dumps(data, ensure_ascii=False),
                    encoding="utf-8")
    return path


def capture(fn, *args, **kwargs):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = fn(*args, **kwargs)
    return result, buf.getvalue()


def run_cli(argv, root):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        code = cek_dialek.main(argv, root=root)
    return code, buf.getvalue()


# ---- the synthesized base -------------------------------------------------
def test_base():
    base = base_dialect()
    check(base.code == "base", "the base code is 'base'", base.code)
    check(base.status == "approved", "the base is approved", base.status)
    check(base.data["parent"] is None, "the base has no parent", base.data["parent"])

    problems = validate_dialect(base.data, filename="base")
    check(not blocking(problems), "the synthesized base passes every rule",
          [str(p) for p in problems])

    missing = []
    for id, entry in IDS.items():
        try:
            if id.startswith("msg."):
                base.vocab.message(id, {p: "x" for p in entry["placeholders"]})
            else:
                base.vocab.word(id)
        except KeyError:
            missing.append(id)
    check(not missing, "the base resolves every live ID", missing)

    check(base.vocab.word("kw.if") == "if", "base kw.if is 'if'",
          base.vocab.word("kw.if"))
    check(base.vocab.word("op.gt") == "greater_than",
          "base op.gt is normalized", base.vocab.word("op.gt"))
    check(base.vocab.word("kw.begin") == "begin_block",
          "base kw.begin is normalized", base.vocab.word("kw.begin"))
    check(base.vocab.word("fn.int") == "whole_number",
          "base fn.int is normalized", base.vocab.word("fn.int"))
    check(base.vocab.message("msg.value.div_zero", {}) == "Division by zero",
          "base messages are English", base.vocab.message("msg.value.div_zero", {}))

    check(base.report.tiers() == {1: (32, 32), 2: (104, 104), 3: (1, 1)},
          "base tier totals match the catalogue", base.report.tiers())
    check(base.report.missing() == [], "the base has no fallbacks", base.report.missing())

    _, out = capture(run_source, 'print 1 + 1', vocab=base.vocab)
    check(out == "2\n", "a program runs in the base vocabulary", repr(out))

    _, out = capture(run_source, 'if 1 greater_than 0 { print "yes" }',
                     vocab=base.vocab)
    check(out == "yes\n", "base comparison words work", repr(out))

    _, out = capture(run_source, 'print true', vocab=base.vocab)
    check(out == "true\n", "base true/false/null print neutrally", repr(out))


# ---- loading and running --------------------------------------------------
def test_minimal_load_and_run():
    with tempfile.TemporaryDirectory() as tmp:
        write(tmp, "uji", valid())
        dialect = load_dialect("uji", root=tmp)

        check(dialect.code == "uji" and dialect.status == "draft",
              "a minimal dialect loads", (dialect.code, dialect.status))
        check(dialect.vocab.word("kw.print") == "cetak",
              "the file's word wins", dialect.vocab.word("kw.print"))
        check(dialect.vocab.word("kw.if") == "if",
              "a missing word falls back to the base", dialect.vocab.word("kw.if"))
        check(("kw.if", "base") in dialect.report.fallbacks,
              "the base fallback is recorded", dialect.report.fallbacks[:3])
        check(dialect.report.tiers()[1] == (1, 32),
              "tier 1 counts only the file's own words", dialect.report.tiers()[1])
        check(("fn.length", 2) in dialect.report.missing(),
              "missing() lists a base word", dialect.report.missing()[:3])

        _, out = capture(run_source, "cetak 1 + 1", vocab=dialect.vocab)
        check(out == "2\n", "a program runs in the dialect", repr(out))

        _, out = capture(run_source, 'if 1 equal 1 { cetak "yes" }',
                         vocab=dialect.vocab)
        check(out == "yes\n", "the base's words and operators run too", repr(out))


def test_message_override():
    with tempfile.TemporaryDirectory() as tmp:
        write(tmp, "uji", valid(messages={"msg.value.div_zero": "Nol!"}))
        dialect = load_dialect("uji", root=tmp)
        try:
            run_source("cetak 1 / 0", vocab=dialect.vocab)
            check(False, "the dialect's message is used", "no error")
        except kerincilang.LangError as err:
            check(str(err) == "Nol!", "the dialect's message is used", str(err))
            check(err.msg_id == "msg.value.div_zero", "msg_id survives", err.msg_id)
        check(dialect.vocab.message("msg.value.key_type", {})
              == "Map keys must be text or whole numbers",
              "an unoverridden message stays English",
              dialect.vocab.message("msg.value.key_type", {}))


def test_parent_chain():
    with tempfile.TemporaryDirectory() as tmp:
        write(tmp, "induk", valid(code="induk", name="Induk",
                                  words={"kw.print": "cetak_induk",
                                         "fn.length": "panjang_induk"}))
        write(tmp, "anak", valid(code="anak", name="Anak", parent="induk",
                                 words={"kw.var": "barang_anak"}))
        child = load_dialect("anak", root=tmp)

        check(child.vocab.word("kw.var") == "barang_anak",
              "the child's own word wins", child.vocab.word("kw.var"))
        check(child.vocab.word("kw.print") == "cetak_induk",
              "the parent supplies a missing word", child.vocab.word("kw.print"))
        check(child.vocab.word("fn.length") == "panjang_induk",
              "the parent supplies a built-in word", child.vocab.word("fn.length"))
        check(child.vocab.word("kw.if") == "if",
              "the base is the last fallback", child.vocab.word("kw.if"))
        check(("kw.print", "induk") in child.report.fallbacks,
              "a parent fallback is recorded", child.report.fallbacks)
        check(("kw.if", "base") in child.report.fallbacks,
              "a base fallback is recorded", child.report.fallbacks)
        check(child.report.tiers()[1] == (1, 32),
              "a parent's words do not count as the file's own",
              child.report.tiers()[1])

        # A child may override a parent.
        write(tmp, "anak", valid(code="anak", name="Anak", parent="induk",
                                 words={"kw.print": "cetak_anak"}))
        again = load_dialect("anak", root=tmp)
        check(again.vocab.word("kw.print") == "cetak_anak",
              "a child overrides a parent", again.vocab.word("kw.print"))

        # An explicit parent of "base" is allowed and terminal.
        write(tmp, "dasar", valid(code="dasar", name="Dasar", parent="base"))
        dasar = load_dialect("dasar", root=tmp)
        check(dasar.vocab.word("kw.print") == "cetak",
              "parent 'base' is accepted", dasar.vocab.word("kw.print"))


def test_available_dialects():
    with tempfile.TemporaryDirectory() as tmp:
        for name in ("a", "b"):
            write(tmp, name, valid(code=name))
        (pathlib.Path(tmp) / "__init__.py").write_text("", encoding="utf-8")
        (pathlib.Path(tmp) / "notes.md").write_text("hi", encoding="utf-8")
        write(tmp, "base", valid(code="base"))
        (pathlib.Path(tmp) / "Bad.json").write_text("{}", encoding="utf-8")
        check(available_dialects(root=tmp) == ["a", "b"],
              "available_dialects lists usable codes only",
              available_dialects(root=tmp))
    check(available_dialects() == [],
          "the committed dialects/ has no dialect files yet",
          available_dialects())


# ---- validation: one code at a time --------------------------------------
def test_schema_rules():
    def expect(label, change, expected):
        data = valid()
        change(data)
        got = codes_of(validate_dialect(data, filename=data.get("code")))
        check(expected in got, label, got)

    expect("unknown top-level key is an error",
           lambda d: d.update({"extra": 1}), "schema")
    expect("missing required field is an error",
           lambda d: d.pop("name"), "schema")
    expect("wrong field type is an error",
           lambda d: d.update({"revision": "1"}), "schema")
    expect("a bool is not a revision",
           lambda d: d.update({"revision": True}), "schema")
    expect("an unknown status is an error",
           lambda d: d.update({"status": "bogus"}), "schema")
    expect("an empty name is an error",
           lambda d: d.update({"name": "  "}), "schema")
    expect("a non-object dialect is an error",
           lambda d: d.clear(), "schema")

    data = valid(code="lain")
    got = codes_of(validate_dialect(data, filename="uji"))
    check("code" in got, "the code must match the filename", got)

    data = valid(code="Uji")
    got = codes_of(validate_dialect(data, filename=None))
    check("code" in got, "the code must match [a-z0-9-]+", got)

    data = valid(core="0.6.1")
    got = codes_of(validate_dialect(data, filename="uji"))
    check("core-version" in got, "core must be MAJOR.MINOR", got)


def test_word_rules():
    def expect(label, word, expected):
        data = valid(words={"kw.if": word})
        got = codes_of(validate_dialect(data, filename="uji"))
        ok = (expected not in got) if expected is None else (expected in got)
        check(ok, label, got)

    expect("an empty word is an error", "   ", "word-empty")
    expect("a hyphen is an error", "ka-lu", "word-charset")
    expect("a leading digit is an error", "1kalu", "word-charset")
    expect("uppercase is reported as a case problem", "Kalu", "word-case")
    expect("a valid word is accepted", "kalu_baru", None)

    data = valid(words={"kw.if": "kalu", "kw.nope": "nope"})
    got = codes_of(validate_dialect(data, filename="uji"))
    check("unknown-id" in got, "an unknown word ID is an error", got)

    data = valid(words={"msg.value.div_zero": "x"})
    got = codes_of(validate_dialect(data, filename="uji"))
    check("wrong-namespace" in got, "a msg.* ID in words is an error", got)

    data = valid(messages={"kw.if": "x"})
    got = codes_of(validate_dialect(data, filename="uji"))
    check("wrong-namespace" in got, "a non-msg ID in messages is an error", got)

    data = valid(messages={"msg.value.div_zero": "Nol oleh {who}"})
    got = codes_of(validate_dialect(data, filename="uji"))
    check("message-placeholder" in got, "placeholders must match the catalogue", got)

    data = valid(messages={"msg.value.operator": "Operator {op} pada {left} dan {right}"})
    got = codes_of(validate_dialect(data, filename="uji"))
    check("message-placeholder" not in got, "matching placeholders are accepted", got)

    data = valid(words={"kw.if": 3})
    got = codes_of(validate_dialect(data, filename="uji"))
    check("schema" in got, "a non-text word is a schema error", got)


def test_review_metadata():
    data = valid(status="approved", reviewer=None)
    got = codes_of(validate_dialect(data, filename="uji"))
    check("reviewer-missing" in got, "an approved dialect needs a reviewer", got)

    data = valid(status="approved", reviewer="Pengulas")
    got = codes_of(validate_dialect(data, filename="uji"))
    check("reviewer-missing" not in got, "a reviewer satisfies the rule", got)

    data = valid(status="review", sources=[])
    got = codes_of(validate_dialect(data, filename="uji"))
    check("source-missing" in got, "a non-draft dialect needs sources", got)

    data = valid(status="draft", sources=[])
    got = codes_of(validate_dialect(data, filename="uji"))
    check("source-missing" not in got, "a draft may have no sources", got)


def test_parent_rules():
    with tempfile.TemporaryDirectory() as tmp:
        write(tmp, "uji", valid(parent="hantu"))
        try:
            load_dialect("uji", root=tmp)
            check(False, "a missing parent is an error", "no error")
        except DialectError as err:
            check(err.code == "parent-missing", "a missing parent is parent-missing",
                  err.code)

        write(tmp, "a", valid(code="a", parent="b"))
        write(tmp, "b", valid(code="b", parent="a"))
        try:
            load_dialect("a", root=tmp)
            check(False, "a parent cycle is an error", "no error")
        except DialectError as err:
            check(err.code == "parent-cycle", "a parent cycle is parent-cycle", err.code)
            check("a" in str(err) and "b" in str(err),
                  "the cycle names every member", str(err))

        write(tmp, "diri", valid(code="diri", parent="diri"))
        try:
            load_dialect("diri", root=tmp)
            check(False, "a self parent is an error", "no error")
        except DialectError as err:
            check(err.code == "parent-cycle", "a self parent is a cycle", err.code)


def test_clash_matrix():
    data = valid(words={"kw.if": "samo", "op.eq": "samo"})
    got = codes_of(validate_dialect(data, filename="uji"))
    check("clash" in got, "kw and op may not share a word", got)

    data = valid(words={"kw.if": "daftar", "fn.list": "daftar"})
    problems = validate_dialect(data, filename="uji")
    got = codes_of(problems)
    check("clash" in got, "kw and fn may not share a word", got)
    detail = " ".join(p.message for p in problems if p.code == "clash")
    check("kw.if" in detail and "fn.list" in detail,
          "the clash names both IDs", detail)

    data = valid(words={"kw.if": "samo", "type.int": "samo"})
    got = codes_of(validate_dialect(data, filename="uji"))
    check("clash" not in got, "type may share with kw", got)

    data = valid(words={"kw.var": "baco", "mode.read": "baco"})
    got = codes_of(validate_dialect(data, filename="uji"))
    check("clash" not in got, "mode may share with kw", got)

    data = valid(words={"reserved.error": "samo", "op.eq": "samo"})
    got = codes_of(validate_dialect(data, filename="uji"))
    check("clash" in got, "reserved and op may not share a word", got)

    # The full Siulak 0.5 word table must pass: its overlaps cross into type/mode.
    siulak = dict(kerincilang.LEGACY_WORDS)
    siulak.update({id: pair[0] for id, pair in kerincilang.LEGACY_OPERATORS.items()})
    data = valid(code="siulak", name="Siulak", words=siulak,
                 messages={id: entry["id_gloss"] for id, entry in IDS.items()
                           if id.startswith("msg.")})
    problems = validate_dialect(data, filename="siulak")
    check(not blocking(problems), "the whole Siulak word table passes the matrix",
          [str(p) for p in blocking(problems)])


def test_clash_across_parents():
    with tempfile.TemporaryDirectory() as tmp:
        write(tmp, "induk", valid(code="induk", words={"fn.list": "samo"}))
        write(tmp, "anak", valid(code="anak", parent="induk", words={"op.eq": "samo"}))
        try:
            load_dialect("anak", root=tmp)
            check(False, "a clash introduced by the merge is caught", "no error")
        except DialectError as err:
            check(err.code == "clash", "a merged clash is a clash", err.code)


def test_core_warning():
    with tempfile.TemporaryDirectory() as tmp:
        write(tmp, "uji", valid(core="9.9"))
        dialect = load_dialect("uji", root=tmp)
        warnings = [p for p in dialect.report.problems if p.code == "newer-core"]
        check(len(warnings) == 1, "a newer core warns", dialect.report.problems)
        check(warnings and warnings[0].severity == "warning",
              "newer-core is a warning, not an error",
              warnings[0].severity if warnings else None)
        check(warnings and not warnings[0].blocking, "a warning does not block", None)


def test_unknown_id_in_parent_is_hard():
    with tempfile.TemporaryDirectory() as tmp:
        write(tmp, "induk", valid(code="induk", words={"kw.nope": "nope"}))
        write(tmp, "anak", valid(code="anak", parent="induk"))
        try:
            load_dialect("anak", root=tmp)
            check(False, "an unknown ID in a parent is a hard error", "no error")
        except DialectError as err:
            check(err.code == "unknown-id", "an unknown ID in a parent is unknown-id",
                  err.code)


# ---- security: path, size, JSON ------------------------------------------
def test_file_security():
    with tempfile.TemporaryDirectory() as tmp:
        for bad in ("../uji", "uji/../uji", "Uji", "uji.json", "", "a b"):
            try:
                load_dialect(bad, root=tmp)
                check(False, "a bad code is rejected: %r" % bad, "no error")
            except DialectError as err:
                check(err.code == "path", "a bad code is a path error: %r" % bad, err.code)

        try:
            load_dialect("hantu", root=tmp)
            check(False, "a missing file is an error", "no error")
        except DialectError as err:
            check(err.code == "missing", "a missing file is 'missing'", err.code)

        write(tmp, "rusak", raw="{")
        try:
            load_dialect("rusak", root=tmp)
            check(False, "malformed JSON is an error", "no error")
        except DialectError as err:
            check(err.code == "json", "malformed JSON is a json error", err.code)

        write(tmp, "ganda", raw='{"code": "ganda", "code": "ganda"}')
        try:
            load_dialect("ganda", root=tmp)
            check(False, "a duplicate key is an error", "no error")
        except DialectError as err:
            check(err.code == "json", "a duplicate key is a json error", err.code)

        write(tmp, "larik", raw="[]")
        try:
            load_dialect("larik", root=tmp)
            check(False, "a non-object root is an error", "no error")
        except DialectError as err:
            check(err.code == "json", "a non-object root is a json error", err.code)

        big = '{"x": "' + "a" * (loader.MAX_BYTES + 1) + '"}'
        write(tmp, "besar", raw=big)
        try:
            load_dialect("besar", root=tmp)
            check(False, "a file over 1 MiB is an error", "no error")
        except DialectError as err:
            check(err.code == "size", "a file over 1 MiB is a size error", err.code)

        # A valid file inside the root still loads.
        write(tmp, "baik", valid(code="baik"))
        check(load_dialect("baik", root=tmp).code == "baik",
              "a valid file in a temp root loads", None)

    check(base_dialect().code == "base", "the base needs no file", None)


# ---- the CLI --------------------------------------------------------------
def _full_tier_one():
    words = {}
    for id, entry in IDS.items():
        if entry["tier"] == 1:
            words[id] = "w_" + id.replace(".", "_")
    return words


def test_cli():
    with tempfile.TemporaryDirectory() as tmp:
        code, out = run_cli(["--semua"], tmp)
        check(code == 0 and out.strip() == "",
              "--semua on an empty directory exits 0", (code, out))

        write(tmp, "uji", valid())
        code, out = run_cli(["--semua"], tmp)
        check(code == 0, "--semua on a valid draft exits 0", (code, out))
        check("uji: tier 1 1/32" in out, "the tier summary is printed", out)

        code, out = run_cli(["--kode", "uji"], tmp)
        check(code == 0, "--kode checks one dialect", (code, out))

        code, out = run_cli(["--kode", "hantu"], tmp)
        check(code == 1, "a missing dialect exits 1", (code, out))

        # A valid approved dialect with every tier-1 word passes --ketat.
        approved = dict(valid(code="penuh", name="Penuh", status="approved",
                              reviewer="Pengulas", words=_full_tier_one()))
        write(tmp, "penuh", approved)
        code, out = run_cli(["--kode", "penuh", "--ketat"], tmp)
        check(code == 0, "a complete approved dialect passes --ketat", (code, out))

        # Approved with one tier-1 word from the base fails --ketat (exit 2).
        gap = dict(approved)
        gap["code"] = "lubang"
        gap["words"] = {id: w for id, w in _full_tier_one().items() if id != "kw.in"}
        write(tmp, "lubang", gap)
        code, out = run_cli(["--kode", "lubang", "--ketat"], tmp)
        check(code == 2, "an approved tier-1 gap exits 2 in strict mode", (code, out))
        check("kw.in" in out, "the strict failure names the gap", out)

        code, out = run_cli(["--kode", "lubang"], tmp)
        check(code == 0, "the same gap is fine without --ketat", (code, out))

        # A newer core fails --ketat (exit 2) but loads normally (exit 0).
        write(tmp, "maju", valid(code="maju", core="9.9"))
        code, out = run_cli(["--kode", "maju"], tmp)
        check(code == 0, "a newer core only warns by default", (code, out))
        check("newer-core" in out, "the warning is printed", out)
        code, out = run_cli(["--kode", "maju", "--ketat"], tmp)
        check(code == 2, "a newer core exits 2 in strict mode", (code, out))

        # A validation error exits 1 even in strict mode.
        write(tmp, "rusak", valid(code="rusak", words={"kw.if": "ka-lu"}))
        code, out = run_cli(["--kode", "rusak", "--ketat"], tmp)
        check(code == 1, "a validation error exits 1", (code, out))
        check("word-charset" in out, "the problem code is printed", out)

        code, _ = run_cli(["--salah"], tmp)
        check(code == 1, "an unknown argument exits 1", code)

        code, out = run_cli(["--help"], tmp)
        check(code == 0 and "--ketat" in out, "--help exits 0", (code, out))


# ---- packaging: the default root works from a zipapp ---------------------
def test_zipapp_default_root():
    with tempfile.TemporaryDirectory() as build:
        source = pathlib.Path(build) / "src"
        source.mkdir()
        shutil.copy(os.path.join(ROOT, "kerincilang.py"), source / "kerincilang.py")
        shutil.copytree(os.path.join(ROOT, "core"), source / "core")
        shutil.copytree(os.path.join(ROOT, "dialects"), source / "dialects",
                        ignore=shutil.ignore_patterns("__pycache__"))
        with open(source / "dialects" / "uji.json", "w", encoding="utf-8") as handle:
            json.dump(valid(), handle)
        (source / "__main__.py").write_text(
            "from dialects import loader\n"
            "d = loader.load_dialect('uji')\n"
            "print(d.code, d.vocab.word('kw.print'), loader.available_dialects())\n",
            encoding="utf-8")
        pyz = pathlib.Path(build) / "krc.pyz"
        zipapp.create_archive(str(source), str(pyz), interpreter="/usr/bin/env python3")

        work = pathlib.Path(build) / "elsewhere"
        work.mkdir()
        result = subprocess.run([sys.executable, str(pyz)], cwd=str(work),
                                capture_output=True, text=True)
        check(result.returncode == 0
              and result.stdout == "uji cetak ['uji']\n",
              "load_dialect works from a zipapp with no checkout",
              (result.returncode, result.stdout, result.stderr))


def test_engine_default_is_unchanged():
    check(kerincilang.current_vocab().code == "siulak",
          "loading a dialect does not change the active vocabulary",
          kerincilang.current_vocab().code)


def main():
    test_base()
    test_minimal_load_and_run()
    test_message_override()
    test_parent_chain()
    test_available_dialects()
    test_schema_rules()
    test_word_rules()
    test_review_metadata()
    test_parent_rules()
    test_clash_matrix()
    test_clash_across_parents()
    test_core_warning()
    test_unknown_id_in_parent_is_hard()
    test_file_security()
    test_cli()
    test_zipapp_default_root()
    test_engine_default_is_unchanged()
    print("\nFAILED:" if FAILED else "\nALL PASSED", len(FAILED) or "")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
