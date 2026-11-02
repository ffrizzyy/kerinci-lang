"""Tests for `krc migrasi` and the CLI contract.

Run with: python3 tests/test_migration.py
"""
import builtins
import contextlib
import io
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipapp

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import kerincilang  # noqa: E402
from kerincilang import main  # noqa: E402

FAILED = []
EXAMPLES = os.path.join(ROOT, "examples")


def check(ok, label, detail=""):
    print("PASS" if ok else "FAIL", label, "" if ok else "-> " + str(detail))
    if not ok:
        FAILED.append(label)


def capture(fn, *args, **kwargs):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        result = fn(*args, **kwargs)
    return result, out.getvalue(), err.getvalue()


def write_bytes(path, data):
    pathlib.Path(path).write_bytes(data)
    return pathlib.Path(path)


def write_text(path, text):
    return write_bytes(path, text.encode("utf-8"))


def header_for(path):
    with open(path, encoding="utf-8") as handle:
        return handle.readline().rstrip("\r\n")


# ---- 1. single file -------------------------------------------------------
def test_single_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = write_text(os.path.join(tmp, "prog.krc"), "nyetak 6 * 7\n")
        original = path.read_bytes()

        code, out, err = capture(main, ["migrasi", str(path)])
        check(code == 0, "migrasi exits 0", (code, err))
        check(err == "", "migrasi is quiet on success", repr(err))
        check("added header" in out, "it reports the added header", repr(out))
        check(path.read_bytes() == b"# dialek: siulak\n" + original,
              "the header is prepended and the bytes are preserved",
              path.read_bytes()[:40])
        check(header_for(path) == "# dialek: siulak", "line 1 is the header",
              header_for(path))

        code, out, err = capture(main, [str(path)])
        check(code == 0 and out == "42\n",
              "the migrated file still runs the program", (code, out, err))


# ---- 2. idempotence -------------------------------------------------------
def test_idempotence():
    with tempfile.TemporaryDirectory() as tmp:
        path = write_text(os.path.join(tmp, "prog.krc"), "nyetak 1\n")
        capture(main, ["migrasi", str(path)])
        first = path.read_bytes()

        code, out, err = capture(main, ["migrasi", str(path)])
        check(code == 0, "a second migrasi exits 0", (code, err))
        check("already has a header" in out, "it reports the existing header",
              repr(out))
        check("0 migrated, 1 already had a header, 0 errors" in out,
              "the summary counts the skip", repr(out))
        check(path.read_bytes() == first, "the second run changes no bytes",
              (first, path.read_bytes()))


# ---- 3. imports -----------------------------------------------------------
def test_imports():
    with tempfile.TemporaryDirectory() as tmp:
        lib = write_text(os.path.join(tmp, "lib.krc"), "barang nilai = 7\n")
        program = write_text(os.path.join(tmp, "main.krc"),
                             'ambik "lib"\nnyetak nilai\n')
        code, before, err = capture(main, [str(program)])
        check(code == 0 and before == "7\n", "the headerless import runs first",
              (code, before, err))

        code, out, err = capture(main, ["migrasi", str(program)])
        check(code == 0, "migrasi follows the import", (code, err))
        check(header_for(program) == "# dialek: siulak",
              "the main file has a header", header_for(program))
        check(header_for(lib) == "# dialek: siulak",
              "the imported file has a header", header_for(lib))
        check("2 migrated" in out, "the summary counts both files", repr(out))

        code, after, err = capture(main, [str(program)])
        check(code == 0 and after == before,
              "the migrated project prints the same output", (code, after, before))


# ---- 4. recursive imports and dedupe -------------------------------------
def test_recursive_imports():
    with tempfile.TemporaryDirectory() as tmp:
        write_text(os.path.join(tmp, "c.krc"), "barang nilai = 3\n")
        write_text(os.path.join(tmp, "b.krc"),
                   'ambik "c"\nbarang dua = nilai + nilai\n')
        program = write_text(
            os.path.join(tmp, "a.krc"),
            'ambik "b"\nambik "./b"\nnyetak dua\n')
        code, out, err = capture(main, ["migrasi", str(program)])
        check(code == 0, "a chain of imports migrates", (code, err))
        for name in ("a.krc", "b.krc", "c.krc"):
            path = os.path.join(tmp, name)
            check(header_for(path) == "# dialek: siulak",
                  "%s has a header" % name, header_for(path))
        check("3 migrated" in out, "the shared file is visited once", repr(out))
        code, out, err = capture(main, [str(program)])
        check(code == 0 and out == "6\n", "the migrated chain still runs",
              (code, out, err))


# ---- 5. --semua -----------------------------------------------------------
def test_semua():
    with tempfile.TemporaryDirectory() as tmp:
        write_text(os.path.join(tmp, "a.krc"), "nyetak 1\n")
        sub = os.path.join(tmp, "sub")
        os.mkdir(sub)
        write_text(os.path.join(sub, "b.krc"), "nyetak 2\n")
        notes = write_text(os.path.join(tmp, "notes.txt"), "bukan kode\n")
        before = notes.read_bytes()

        code, out, err = capture(main, ["migrasi", "--semua", tmp])
        check(code == 0, "--semua exits 0", (code, err))
        check("2 migrated" in out, "--semua migrates both .krc files", repr(out))
        check(header_for(os.path.join(tmp, "a.krc")) == "# dialek: siulak",
              "the top-level file is migrated")
        check(header_for(os.path.join(sub, "b.krc")) == "# dialek: siulak",
              "the nested file is migrated")
        check(notes.read_bytes() == before, "a non-.krc file is untouched",
              notes.read_bytes())

        code, out, err = capture(main, ["migrasi", "--semua", tmp])
        check(code == 0 and "0 migrated, 2 already had a header" in out,
              "a second --semua run is a no-op", repr(out))


# ---- 6. --dialek ----------------------------------------------------------
def test_dialect_choice():
    with tempfile.TemporaryDirectory() as tmp:
        lib = write_text(os.path.join(tmp, "lib.krc"),
                         "netakka_variabel nilai = 7\n")
        program = write_text(os.path.join(tmp, "main.krc"),
                             'impor "lib"\nnytak nilai\n')
        code, out, err = capture(
            main, ["migrasi", "--dialek", "koto-payang", str(program)])
        check(code == 0, "migrasi --dialek koto-payang exits 0", (code, err))
        check(header_for(program) == "# dialek: koto-payang",
              "the chosen code is written", header_for(program))
        check(header_for(lib) == "# dialek: koto-payang",
              "the headerless import uses the same default", header_for(lib))

        code, out, err = capture(main, [str(program)])
        check(code == 0 and out == "7\n",
              "the migrated Koto Payang file runs without a flag",
              (code, out, err))
        check(err == "", "the Koto Payang run has no fallback warning", repr(err))


# ---- 7. --kering ----------------------------------------------------------
def test_dry_run():
    with tempfile.TemporaryDirectory() as tmp:
        program = write_text(os.path.join(tmp, "prog.krc"), "nyetak 1\n")
        before = program.read_bytes()
        code, out, err = capture(main, ["migrasi", "--kering", str(program)])
        check(code == 0, "--kering exits 0", (code, err))
        check("would add header" in out, "it reports the planned header",
              repr(out))
        check("1 would migrate" in out, "the summary uses the dry-run wording",
              repr(out))
        check(program.read_bytes() == before, "--kering writes nothing",
              program.read_bytes())


# ---- 8. refusals ----------------------------------------------------------
def test_refusals():
    with tempfile.TemporaryDirectory() as tmp:
        bom = write_bytes(os.path.join(tmp, "bom.krc"),
                          b"\xef\xbb\xbfnyetak 1\n")
        code, out, err = capture(main, ["migrasi", str(bom)])
        check(code == 1, "a BOM exits 1", (code, err))
        check("BOM" in err, "the BOM error is named", repr(err))
        check(bom.read_bytes().startswith(b"\xef\xbb\xbfnyetak"),
              "the BOM file is unchanged")

        malformed = write_text(os.path.join(tmp, "bad-header.krc"),
                               "#dialek koto-payang\nnyetak 1\n")
        before = malformed.read_bytes()
        code, out, err = capture(main, ["migrasi", str(malformed)])
        check(code == 1, "a malformed header exits 1", (code, err))
        check("header dialek" in err, "the malformed header is named", repr(err))
        check(malformed.read_bytes() == before,
              "a malformed header is not buried", malformed.read_bytes())

        broken = write_text(os.path.join(tmp, "broken.krc"), "nyetak (\n")
        before = broken.read_bytes()
        code, out, err = capture(main, ["migrasi", str(broken)])
        check(code == 1, "a parse error exits 1", (code, err))
        check("tidak bisa diurai" in err, "the parse error is reported",
              repr(err))
        check(broken.read_bytes() == before,
              "a parse error does not get a header", broken.read_bytes())

        unknown = write_text(os.path.join(tmp, "unknown.krc"),
                             "# dialek: hantu\nnyetak 1\n")
        before = unknown.read_bytes()
        code, out, err = capture(main, ["migrasi", str(unknown)])
        check(code == 1, "an unknown header dialect exits 1", (code, err))
        check(unknown.read_bytes() == before,
              "the unknown-header file is unchanged")

        dynamic = write_text(os.path.join(tmp, "dynamic.krc"),
                             'barang n = "lib"\nambik n\n')
        code, out, err = capture(main, ["migrasi", str(dynamic)])
        check(code == 1, "a non-literal import exits 1", (code, err))
        check("non-literal" in err, "the dynamic import is reported", repr(err))
        check(header_for(dynamic) == "# dialek: siulak",
              "the file itself is still migrated", header_for(dynamic))

        missing = write_text(os.path.join(tmp, "missing.krc"),
                             'ambik "nope"\n')
        code, out, err = capture(main, ["migrasi", str(missing)])
        check(code == 1, "a missing import exits 1", (code, err))
        check("impor tidak ditemukan" in err, "the missing import is named",
              repr(err))
        check(header_for(missing) == "# dialek: siulak",
              "the importing file is still migrated", header_for(missing))


# ---- 9. line endings and preservation ------------------------------------
def test_preservation():
    with tempfile.TemporaryDirectory() as tmp:
        crlf = write_bytes(os.path.join(tmp, "crlf.krc"),
                           b"nyetak 1\r\nnyetak 2\r\n")
        code, out, err = capture(main, ["migrasi", str(crlf)])
        check(code == 0, "a CRLF file migrates", (code, err))
        check(crlf.read_bytes() == b"# dialek: siulak\r\nnyetak 1\r\nnyetak 2\r\n",
              "the header uses CRLF and the rest is intact", crlf.read_bytes())

        no_newline = write_bytes(os.path.join(tmp, "tail.krc"), b"nyetak 3")
        code, out, err = capture(main, ["migrasi", str(no_newline)])
        check(code == 0, "a file without a final newline migrates", (code, err))
        check(no_newline.read_bytes() == b"# dialek: siulak\nnyetak 3",
              "the missing final newline is preserved", no_newline.read_bytes())

        commented = write_text(os.path.join(tmp, "comment.krc"),
                               "# judul\n# catatan\nnyetak 4\n")
        raw = commented.read_bytes()
        capture(main, ["migrasi", str(commented)])
        check(commented.read_bytes() == b"# dialek: siulak\n" + raw,
              "comments are preserved verbatim", commented.read_bytes())


# ---- 10. usage ------------------------------------------------------------
def test_usage():
    with tempfile.TemporaryDirectory() as tmp:
        program = write_text(os.path.join(tmp, "prog.krc"), "nyetak 1\n")
        before = program.read_bytes()
        text = write_text(os.path.join(tmp, "notes.txt"), "x")

        cases = [
            (["migrasi"], "no target"),
            (["migrasi", "--semua"], "--semua without a directory"),
            (["migrasi", "--semua", str(program)], "--semua on a file"),
            (["migrasi", str(text)], "a non-.krc target"),
            (["migrasi", str(program), "--ketat"], "--ketat"),
            (["migrasi", str(program), "--dialek", "hantu"], "an unknown dialect"),
            (["migrasi", str(program), "--dialek"], "a missing dialect value"),
            (["migrasi", "--nope", str(program)], "an unknown option"),
        ]
        for argv, label in cases:
            code, out, err = capture(main, argv)
            check(code == 2, "%s exits 2" % label, (code, out, err))
        check(program.read_bytes() == before,
              "no usage error writes to the file", program.read_bytes())

        code, out, err = capture(main, ["migrasi", "--help"])
        check(code == 0, "migrasi --help exits 0", (code, err))
        check("--semua" in out and "--kering" in out and "--dialek" in out,
              "migrasi --help documents the flags", repr(out))

        code, out, err = capture(main, ["--nope"])
        check(code == 2, "an unknown normal-run option exits 2", (code, err))
        code, out, err = capture(main, ["-c", "nyetak 1", "extra"])
        check(code == 2, "extra arguments after -c exit 2", (code, err))
        code, out, err = capture(main, ["-c"])
        check(code == 2, "-c without code exits 2", (code, err))


# ---- 11. packaging --------------------------------------------------------
def test_zipapp():
    with tempfile.TemporaryDirectory() as build:
        source = pathlib.Path(build) / "src"
        source.mkdir()
        shutil.copy(os.path.join(ROOT, "kerincilang.py"),
                    source / "kerincilang.py")
        shutil.copytree(os.path.join(ROOT, "core"), source / "core")
        shutil.copytree(os.path.join(ROOT, "dialects"), source / "dialects",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (source / "__main__.py").write_text(
            "import sys\nfrom kerincilang import main\nsys.exit(main())\n",
            encoding="utf-8")
        pyz = pathlib.Path(build) / "krc.pyz"
        zipapp.create_archive(str(source), str(pyz),
                              interpreter="/usr/bin/env python3")

        work = pathlib.Path(build) / "elsewhere"
        work.mkdir()
        program = work / "prog.krc"
        program.write_bytes(b"nyetak 1 + 1\n")
        result = subprocess.run(
            [sys.executable, str(pyz), "migrasi", str(program)],
            cwd=str(work), capture_output=True, text=True, encoding="utf-8")
        check(result.returncode == 0, "the zipapp runs migrasi",
              (result.returncode, result.stdout, result.stderr))
        check(program.read_bytes().startswith(b"# dialek: siulak\n"),
              "the zipapp adds the header", program.read_bytes()[:30])
        result = subprocess.run(
            [sys.executable, str(pyz), str(program)],
            cwd=str(work), capture_output=True, text=True, encoding="utf-8")
        check(result.returncode == 0 and result.stdout == "2\n",
              "the zipapp runs the migrated file",
              (result.returncode, result.stdout, result.stderr))


# ---- 12. examples ---------------------------------------------------------
EXPECTED_IMPORT = "Perkakas versi 1.0\nRata-rata: 73\nTerbesar: 90\n"


def test_examples():
    paths = sorted(pathlib.Path(EXAMPLES).glob("*.krc"))
    check(len(paths) == 8, "there are eight examples", len(paths))
    for path in paths:
        first = path.read_text(encoding="utf-8").split("\n", 1)[0].rstrip("\r")
        check(first == "# dialek: siulak", "%s carries a header" % path.name,
              first)

    code, out, err = capture(main, [os.path.join(EXAMPLES, "contoh-impor.krc")])
    check(code == 0 and out == EXPECTED_IMPORT,
          "the migrated import example prints the same output", (code, out, err))


# ---- 13. CLI table --------------------------------------------------------
def test_cli_table():
    with tempfile.TemporaryDirectory() as tmp:
        declared = write_text(
            os.path.join(tmp, "declared.krc"),
            "# dialek: koto-payang\nnytak 42\n")
        code, out, err = capture(main, ["--dialek", "siulak", str(declared)])
        check(code == 0 and out == "42\n",
              "a header wins over --dialek", (code, out, err))

        plain = write_text(os.path.join(tmp, "plain.krc"), "nytak 43\n")
        code, out, err = capture(main, ["--dialek", "koto-payang", str(plain)])
        check(code == 0 and out == "43\n",
              "--dialek is the default for a headerless file", (code, out, err))

        code, out, err = capture(
            main, ["--dialek", "koto-payang", "-c", "nytak 44"])
        check(code == 0 and out == "44\n", "--dialek applies to -c",
              (code, out, err))

        lib = write_text(os.path.join(tmp, "lib.krc"), "nyetak 45\n")
        imported = write_text(
            os.path.join(tmp, "imported.krc"),
            '# dialek: koto-payang\nimpor "lib"\n')
        code, out, err = capture(main, ["--dialek", "siulak", str(imported)])
        check(code == 0 and out == "45\n",
              "a headerless import uses the run default, not the importer",
              (code, out, err))

        answers = iter(["nytak 46"])

        def fake_input(prompt=""):
            try:
                return next(answers)
            except StopIteration:
                raise EOFError

        original = builtins.input
        builtins.input = fake_input
        try:
            code, out, err = capture(main, ["--dialek", "koto-payang"])
        finally:
            builtins.input = original
        check(code == 0 and "46" in out, "the REPL uses --dialek",
              (code, out, err))


def main_test():
    test_single_file()
    test_idempotence()
    test_imports()
    test_recursive_imports()
    test_semua()
    test_dialect_choice()
    test_dry_run()
    test_refusals()
    test_preservation()
    test_usage()
    test_zipapp()
    test_examples()
    test_cli_table()
    print("\nFAILED:" if FAILED else "\nALL PASSED", len(FAILED) or "")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main_test())
