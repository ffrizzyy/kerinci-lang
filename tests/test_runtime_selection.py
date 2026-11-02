"""Tests for runtime dialect selection: header, precedence, imports, CLI, strict.

Run with: python3 tests/test_runtime_selection.py
"""
import contextlib
import io
import json
import os
import pathlib
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import kerincilang  # noqa: E402
from kerincilang import (  # noqa: E402
    LangError, current_context, dialect_header, main, resolve_source_vocab,
    run_file, run_source,
)

FAILED = []
IDS = kerincilang.CATALOG["ids"]


def check(ok, label, detail=""):
    print("PASS" if ok else "FAIL", label, "" if ok else "-> " + str(detail))
    if not ok:
        FAILED.append(label)


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
        "words": {},
        "messages": {},
    }
    data.update(over)
    return data


def write(root, code, data=None, raw=None):
    path = pathlib.Path(root) / (code + ".json")
    path.write_text(raw if raw is not None else json.dumps(data, ensure_ascii=False),
                    encoding="utf-8")
    return path


def write_text(root, name, text):
    path = pathlib.Path(root) / name
    path.write_text(text, encoding="utf-8")
    return path


def capture(fn, *args, **kwargs):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        result = fn(*args, **kwargs)
    return result, out.getvalue(), err.getvalue()


# Two dialects with disjoint surface words, so output names the running module.
DUA = {
    "kw.print": "cetak_dua",
    "kw.var": "barang_dua",
    "kw.func": "fungsi_dua",
    "kw.return": "balik_dua",
    "kw.if": "kalu_dua",
    "kw.true": "betul_dua",
    "kw.false": "salah_dua",
    "kw.null": "kosong_dua",
    "fn.type": "mecem_dua",
    "type.int": "bulat_dua",
}
DUA_MSGS = {"msg.value.div_zero": "Nol dua!"}
SATU = {
    "kw.print": "cetak_satu",
    "kw.var": "barang_satu",
    "kw.func": "fungsi_satu",
    "kw.return": "balik_satu",
    "fn.type": "mecem_satu",
    "type.int": "bulat_satu",
}
SATU_MSGS = {"msg.value.div_zero": "Nol satu!"}

B_SRC = """# dialek: dua
fungsi_dua halo() {
  cetak_dua "dari-b"
}
fungsi_dua tipe() {
  balik_dua mecem_dua(1)
}
fungsi_dua gagal() {
  balik_dua 1 / 0
}
"""


def full_tier_one():
    return {id: "w_" + id.replace(".", "_")
            for id, entry in IDS.items() if entry["tier"] == 1}


# ---- the header -----------------------------------------------------------
def test_header():
    check(dialect_header("# dialek: koto-payang\nx\n") == "koto-payang",
          "a header on line 1 is read", dialect_header("# dialek: koto-payang"))
    check(dialect_header("#dialek:dua\n") == "dua",
          "spacing is flexible", dialect_header("#dialek:dua"))
    check(dialect_header('nyetak "a"\n# dialek: dua\n') is None,
          "a header on line 2 is not a header",
          dialect_header('nyetak "a"\n# dialek: dua\n'))
    check(dialect_header("nyetak 1\n") is None,
          "a program without a header has none", None)

    with tempfile.TemporaryDirectory() as tmp:
        write(tmp, "dua", valid(code="dua", name="Dua", words=DUA, messages=DUA_MSGS))
        try:
            run_source("# dialek: ../x\nnyetak 1\n", dialect_root=tmp)
            check(False, "a malformed header is an error", "no error")
        except LangError as err:
            check(err.msg_id == "msg.dialect.header",
                  "a malformed header is msg.dialect.header", err.msg_id)
            check("tidak valid" in str(err), "the header text is reported", str(err))

        for bad in ("# dialek: Uji", "# dialek: dua extra", "# dialek:",
                    "# Dialek: dua", "# dialek dua", "# catatan: dialek dua"):
            try:
                run_source(bad + "\nnyetak 1\n", dialect_root=tmp)
                check(False, "a bad header is rejected: %r" % bad, "no error")
            except LangError as err:
                check(err.msg_id == "msg.dialect.header",
                      "a bad header is msg.dialect.header: %r" % bad, err.msg_id)

        _, out, _ = capture(run_source, '# catatan biasa\nnyetak "ok"\n')
        check(out == "ok\n", "a line-1 comment without 'dialek' is a comment",
              repr(out))


def test_headerless_is_siulak():
    _, out, err = capture(run_source, 'nyetak "halo"\n')
    check(out == "halo\n", "a headerless program still runs in Siulak", repr(out))
    check(err == "", "a headerless program prints no warnings", repr(err))

    _, again, _ = capture(run_source, 'nyetak "halo"\n')
    check(out == again, "headerless output is unchanged run to run", (out, again))


def test_header_selects_dialect():
    with tempfile.TemporaryDirectory() as tmp:
        write(tmp, "dua", valid(code="dua", name="Dua", words=DUA, messages=DUA_MSGS))
        _, out, err = capture(run_source,
                              '# dialek: dua\ncetak_dua "halo"\n',
                              dialect_root=tmp)
        check(out == "halo\n", "a header selects a temp dialect", repr(out))
        check(err == "", "a dialect used as declared warns only on real gaps",
              repr(err))


# ---- precedence: header > --dialek > Siulak -------------------------------
def test_precedence():
    with tempfile.TemporaryDirectory() as tmp:
        write(tmp, "dua", valid(code="dua", name="Dua", words=DUA, messages=DUA_MSGS))
        write(tmp, "satu", valid(code="satu", name="Satu", words=SATU, messages=SATU_MSGS))

        plain = write_text(tmp, "plain.krc", 'cetak_dua "default"\n')
        code, out, err = capture(main, ["--dialek", "dua", str(plain)],
                                 dialect_root=tmp)
        check(code == 0 and out == "default\n",
              "--dialek sets the default for a headerless file", (code, out, err))

        code, out, err = capture(main, ["--dialek", "dua", "-c",
                                        'cetak_dua "potong"'],
                                 dialect_root=tmp)
        check(code == 0 and out == "potong\n",
              "--dialek applies to -c", (code, out, err))

        declared = write_text(tmp, "declared.krc",
                              '# dialek: dua\ncetak_dua "header"\n')
        code, out, err = capture(main, ["--dialek", "satu", str(declared)],
                                 dialect_root=tmp)
        check(code == 0 and out == "header\n",
              "a header wins over --dialek", (code, out, err))

        code, out, err = capture(main, ["--dialek", "satu", "-c",
                                        'cetak_satu "satu"'],
                                 dialect_root=tmp)
        check(code == 0 and out == "satu\n",
              "--dialek satu loads its own words", (code, out, err))


# ---- imports and per-call vocabulary -------------------------------------
def _import_fixture(tmp):
    write(tmp, "dua", valid(code="dua", name="Dua", words=DUA, messages=DUA_MSGS))
    write(tmp, "satu", valid(code="satu", name="Satu", words=SATU, messages=SATU_MSGS))
    write_text(tmp, "b.krc", B_SRC)


def test_import_header_and_cross_dialect_call():
    with tempfile.TemporaryDirectory() as tmp:
        _import_fixture(tmp)
        main_src = ('# dialek: satu\n'
                    'import "b"\n'
                    'cetak_satu "dari-a"\n'
                    'halo()\n'
                    'cetak_satu "lagi-a"\n')
        write_text(tmp, "a.krc", main_src)
        code, out, err = capture(main, [os.path.join(tmp, "a.krc")],
                                 dialect_root=tmp)
        check(code == 0, "a mixed-dialect import runs", (code, out, err))
        check(out == "dari-a\ndari-b\nlagi-a\n",
              "the import's header wins and the caller is restored", repr(out))

        env, _, _ = capture(run_file, os.path.join(tmp, "a.krc"),
                            dialect_root=tmp)
        vocab_a = env.vocab
        check(vocab_a.code == "satu", "the importer keeps its own dialect",
              vocab_a.code)


def test_mecem_inside_callee():
    with tempfile.TemporaryDirectory() as tmp:
        _import_fixture(tmp)
        write_text(tmp, "a.krc",
                   '# dialek: satu\nimport "b"\ncetak_satu tipe()\n')
        code, out, err = capture(main, [os.path.join(tmp, "a.krc")],
                                 dialect_root=tmp)
        check(code == 0 and out == "bulat_dua\n",
              "mecem inside B returns B's type word", (code, out, err))


def test_error_inside_callee():
    with tempfile.TemporaryDirectory() as tmp:
        _import_fixture(tmp)
        write_text(tmp, "a.krc",
                   '# dialek: satu\nimport "b"\ngagal()\n')
        try:
            run_file(os.path.join(tmp, "a.krc"), dialect_root=tmp)
            check(False, "an error inside B is raised", "no error")
        except LangError as err:
            check(str(err) == "Nol dua!",
                  "an error inside B uses B's message", str(err))
            check(err.msg_id == "msg.value.div_zero", "msg_id survives the call",
                  err.msg_id)


# ---- run context ----------------------------------------------------------
def test_context_lifetime():
    check(current_context() is None, "no context leaks outside a run",
          current_context())
    try:
        run_source('# dialek: hantu\nnyetak 1\n')
    except LangError:
        pass
    check(current_context() is None, "a failed run leaves no context",
          current_context())

    with tempfile.TemporaryDirectory() as tmp:
        write(tmp, "dua", valid(code="dua", name="Dua", words=DUA, messages=DUA_MSGS))
        context = kerincilang.RunContext(dialect_root=tmp)
        vocab = resolve_source_vocab('# dialek: dua\n', context)
        check(vocab.code == "dua", "resolve_source_vocab reads the header",
              vocab.code)
        check(resolve_source_vocab("nyetak 1\n", context).code == "siulak",
              "a headerless source uses the context default", None)


# ---- --ketat --------------------------------------------------------------
def test_strict():
    with tempfile.TemporaryDirectory() as tmp:
        write(tmp, "penuh", valid(code="penuh", name="Penuh", status="approved",
                                  reviewer="Pengulas",
                                  words=full_tier_one()))
        program = write_text(tmp, "prog.krc", 'w_kw_print "ok"\n')
        code, out, err = capture(main,
                                 ["--ketat", "--dialek", "penuh", str(program)],
                                 dialect_root=tmp)
        check(code == 0 and out == "ok\n",
              "--ketat passes a complete approved dialect", (code, out, err))
        check(err == "", "a complete dialect is quiet in strict mode", repr(err))

        gap_words = {id: word for id, word in full_tier_one().items()
                     if id != "kw.in"}
        write(tmp, "lubang", valid(code="lubang", name="Lubang", status="approved",
                                   reviewer="Pengulas", words=gap_words))
        code, out, err = capture(main,
                                 ["--ketat", "--dialek", "lubang", str(program)],
                                 dialect_root=tmp)
        check(code == 2, "--ketat exits 2 for a tier-1 gap", (code, out, err))
        check(out == "", "a failing strict dialect does not run", repr(out))
        check("strict:" in err and "kw.in" in err,
              "the strict failure names the gap", repr(err))

        gap = write_text(tmp, "gap.krc", '# dialek: lubang\nw_kw_print "gap"\n')
        top = write_text(tmp, "top.krc", 'ambik "gap"\nnyetak "ran"\n')
        code, out, err = capture(main, ["--ketat", str(top)], dialect_root=tmp)
        check(code == 2, "--ketat exits 2 for an imported gapped dialect",
              (code, out, err))
        check(out == "gap\nran\n",
              "the program still runs before the exit code", repr(out))
        check("kw.in" in err, "the imported gap is named", repr(err))


# ---- warnings -------------------------------------------------------------
def test_warnings():
    with tempfile.TemporaryDirectory() as tmp:
        write(tmp, "ribut", valid(code="ribut", name="Ribut",
                                  words={"kw.print": "cetak_ribut"}))
        program = write_text(tmp, "loop.krc",
                             "# dialek: ribut\n" + "cetak_ribut true\n" * 3)
        code, out, err = capture(main, [str(program)], dialect_root=tmp)
        check(code == 0, "a warning never changes the exit code", (code, err))
        check(out == "true\ntrue\ntrue\n", "the loop still prints", repr(out))
        check(err.count("kw.true falls back") == 1,
              "a fallback warns once per (dialect, id) per run", repr(err))
        check(err.startswith("warning: dialect ribut:"),
              "warnings are English stderr lines", repr(err))

        write(tmp, "bersih", valid(code="bersih", name="Bersih",
                                   words={"kw.print": "cetak_bersih",
                                          "kw.true": "betul_bersih"}))
        _, out, err = capture(run_source,
                              '# dialek: bersih\ncetak_bersih betul_bersih\n',
                              dialect_root=tmp)
        check(out == "betul_bersih\n", "the clean dialect prints", repr(out))
        check(err == "", "a clean dialect prints no warnings", repr(err))

        write(tmp, "pesan", valid(code="pesan", name="Pesan",
                                  words={"kw.print": "cetak_pesan"}))
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                run_source('# dialek: pesan\ncetak_pesan 1 / 0\n',
                           dialect_root=tmp)
                check(False, "a base message error is raised", "no error")
            except LangError:
                pass
        check(err.getvalue().count("msg.value.div_zero falls back") == 1,
              "a base message warns once when used", repr(err.getvalue()))

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                run_source('# dialek: dua\ncetak_dua 1 / 0\n', dialect_root=tmp)
                check(False, "an overridden message error is raised", "no error")
            except LangError:
                pass
        check("falls back" not in err.getvalue(),
              "an overridden message does not warn", repr(err.getvalue()))


# ---- negatives ------------------------------------------------------------
def test_negative_headers():
    with tempfile.TemporaryDirectory() as tmp:
        write(tmp, "dua", valid(code="dua", name="Dua", words=DUA, messages=DUA_MSGS))
        try:
            run_source('# dialek: hantu\nnyetak 1\n', dialect_root=tmp)
            check(False, "an unknown header code is an error", "no error")
        except LangError as err:
            check(err.msg_id == "msg.dialect.unknown",
                  "an unknown code is msg.dialect.unknown", err.msg_id)
            check("hantu" in str(err), "the unknown code is named", str(err))

        write(tmp, "rusak", valid(code="rusak", name="Rusak",
                                  words={"kw.if": "ka-lu"}))
        try:
            run_source('# dialek: rusak\nnyetak 1\n', dialect_root=tmp)
            check(False, "an invalid dialect file is an error", "no error")
        except LangError as err:
            check(err.msg_id == "msg.dialect.invalid",
                  "an invalid file is msg.dialect.invalid", err.msg_id)
            check("rusak" in str(err), "the invalid code is named", str(err))

        header = write_text(tmp, "bad.krc", '# dialek: ../x\nnyetak 1\n')
        code, out, err = capture(main, [str(header)], dialect_root=tmp)
        check(code == 1 and out == "",
              "a bad header is a program error (exit 1)", (code, out, err))
        check("header dialek" in err, "the header error reaches stderr", repr(err))


def test_cli_errors():
    with tempfile.TemporaryDirectory() as tmp:
        program = write_text(tmp, "prog.krc", 'nyetak "ran"\n')
        code, out, err = capture(main, ["--dialek", "hantu", str(program)],
                                 dialect_root=tmp)
        check(code == 2, "--dialek hantu exits 2", (code, err))
        check(out == "", "--dialek hantu runs nothing", repr(out))
        check("hantu" in err, "--dialek hantu names the code", repr(err))

        code, _, err = capture(main, ["--dialek"], dialect_root=tmp)
        check(code == 2, "--dialek without a value exits 2", (code, err))
        check("butuh kode dialek" in err, "the missing value is explained", repr(err))

        code, _, err = capture(main, ["--dialek="], dialect_root=tmp)
        check(code == 2, "--dialek= exits 2", (code, err))

        code, _, err = capture(main, ["--salah"], dialect_root=tmp)
        check(code == 2, "an unknown flag exits 2", (code, err))

        code, out, err = capture(main, ["--help"], dialect_root=tmp)
        check(code == 0 and "--dialek" in out and "--ketat" in out,
              "USAGE documents both flags", (code, out))


def main_test():
    test_header()
    test_headerless_is_siulak()
    test_header_selects_dialect()
    test_precedence()
    test_import_header_and_cross_dialect_call()
    test_mecem_inside_callee()
    test_error_inside_callee()
    test_context_lifetime()
    test_strict()
    test_warnings()
    test_negative_headers()
    test_cli_errors()
    print("\nFAILED:" if FAILED else "\nALL PASSED", len(FAILED) or "")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main_test())
