"""Tests for `krc terjemah` and the lossless translator policy.

Run with: python3 tests/test_translator.py
"""
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

from kerincilang import main  # noqa: E402

FAILED = []
EXAMPLES = os.path.join(ROOT, "examples")
EXPECTED_IMPORT = "Perkakas versi 1.0\nRata-rata: 73\nTerbesar: 90\n"


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


def read_text(path):
    with open(path, encoding="utf-8", newline="") as handle:
        return handle.read()


def read_bytes(path):
    return pathlib.Path(path).read_bytes()


def headered(body, code="siulak"):
    return "# dialek: %s\n%s" % (code, body)


def translate(path, target="koto-payang", extra=()):
    return capture(main, ["terjemah", str(path), "--ke", target] + list(extra))


def translate_out(path, out, target="koto-payang", extra=()):
    return capture(main, ["terjemah", str(path), "--ke", target,
                          "--out", str(out)] + list(extra))


# ---- 1. basic translation -------------------------------------------------
def test_basic():
    with tempfile.TemporaryDirectory() as tmp:
        source = (
            "# dialek: siulak\n"
            "# barang tetap guno: komentar\n"
            "barang  nilai = 1   # dua spasi\n"
            "tetap tetap_nilai = 2\n"
            "guno ambil_besar(a, b) {\n"
            "    kalu a lebih_daripado b { balik a }\n"
            "    lain { balik b }\n"
            "}\n"
            "nyetak ambil_besar(nilai, tetap_nilai)\n"
            "nyetak betul ngan salah apo kosong\n"
        )
        expected = (
            "# dialek: koto-payang\n"
            "# barang tetap guno: komentar\n"
            "netakka_variabel  nilai = 1   # dua spasi\n"
            "netakka_konstanta tetap_nilai = 2\n"
            "jeloehka ambil_besar(a, b) {\n"
            "    kalu a lebih_geduang_dari b { baluikka a }\n"
            "    nga_laen { baluikka b }\n"
            "}\n"
            "nytak ambil_besar(nilai, tetap_nilai)\n"
            "nytak betiu nga salah atau kusao\n"
        )
        path = write_text(os.path.join(tmp, "prog.krc"), source)
        code, out, err = translate(path)
        check(code == 0, "basic translation exits 0", (code, err))
        check(err == "", "basic translation is quiet", repr(err))
        check(out == expected, "every word and gap is translated exactly",
              repr(out))
        check("terjemah:" not in out, "stdout mode prints no summary", repr(out))


# ---- 2. user names --------------------------------------------------------
def test_user_names():
    with tempfile.TemporaryDirectory() as tmp:
        source = (
            "# dialek: siulak\n"
            "barang berkas = 1\n"
            "tetap boolean = 2\n"
            "guno hitung(a, b) {\n"
            "    barang hasil = a + b\n"
            "    untuk x alem [1, 2] { hasil = hasil + x }\n"
            "    cubo { ngangkat \"x\" } tangkap pesan { hasil = hasil + 1 }\n"
            "    balik hasil\n"
            "}\n"
            "barang target = 0\n"
            "target = hitung(berkas, boolean)\n"
            "nyetak target\n"
        )
        path = write_text(os.path.join(tmp, "names.krc"), source)
        code, out, err = translate(path)
        check(code == 0, "user-name source translates", (code, err))
        for name in ("berkas", "boolean", "hitung", "a", "b", "hasil", "x",
                     "pesan", "target"):
            check(name in out, "user name %r is preserved" % name, repr(out))
        check("netakka_variabel berkas = 1" in out,
              "a non-guarded type word can be a user name", repr(out))
        check("netakka_konstanta boolean = 2" in out,
              "a shared type word can be a user name", repr(out))
        check("ndik x daling [1, 2]" in out, "the loop keyword changes",
              repr(out))
        check("kecuali pesan" in out, "the catch name and keyword change",
              repr(out))


# ---- 3. strings and comments ---------------------------------------------
def test_strings_and_comments():
    with tempfile.TemporaryDirectory() as tmp:
        source = (
            "# dialek: siulak\n"
            "# barang nyetak samo tulis kato\n"
            "nyetak \"barang nyetak samo tulis kato\"\n"
            "nyetak 1 + 2 * 3\n"
        )
        path = write_text(os.path.join(tmp, "strings.krc"), source)
        code, out, err = translate(path)
        check(code == 0, "string/comment source translates", (code, err))
        check("# barang nyetak samo tulis kato" in out,
              "a comment is byte-identical", repr(out))
        check('"barang nyetak samo tulis kato"' in out,
              "a string is byte-identical", repr(out))
        check("nytak 1 + 2 * 3" in out, "numbers and symbols are unchanged",
              repr(out))


# ---- 4. operators ---------------------------------------------------------
def test_operators():
    with tempfile.TemporaryDirectory() as tmp:
        source = (
            "# dialek: siulak\n"
            "kalu 1 samo 1 { nyetak \"sama\" }\n"
            "kalu 1 dak_samo 2 { nyetak \"beda\" }\n"
            "kalu 2 lebih_daripado 1 { nyetak \"gt\" }\n"
            "kalu 1 kurang_samo 2 { nyetak \"lt\" }\n"
            "kalu 1 == 1 { nyetak \"eq\" }\n"
            "kalu 1 != 2 { nyetak \"ne\" }\n"
            "kalu 1 < 2 { nyetak \"lt2\" }\n"
            "kalu 1 >= 1 { nyetak \"ge\" }\n"
            "kalu 1 == 1 mulai nyetak 1 habih\n"
        )
        path = write_text(os.path.join(tmp, "ops.krc"), source)
        code, out, err = translate(path)
        check(code == 0, "operator source translates", (code, err))
        check("1 samu_dinga 1" in out, "op.eq word changes", repr(out))
        check("1 iduak_samu_dinga 2" in out, "op.ne word changes", repr(out))
        check("2 lebih_geduang_dari 1" in out, "op.gt word changes",
              repr(out))
        check("1 lebih_nik_atau_samu_dinga 2" in out, "op.le word changes",
              repr(out))
        check("1 == 1" in out and "1 != 2" in out and "1 < 2" in out
              and "1 >= 1" in out, "symbol operators stay symbols", repr(out))
        check("kalu 1 == 1 mulai nytak 1 selesai" in out,
              "begin/end words translate and braces stay", repr(out))


# ---- 5. round trip --------------------------------------------------------
def test_round_trip():
    names = ("contoh.krc", "contoh-kesalahan.krc", "contoh-impor.krc",
             "contoh-teks.krc", "perkakas.krc")
    with tempfile.TemporaryDirectory() as tmp:
        for name in names:
            shutil.copyfile(os.path.join(EXAMPLES, name), os.path.join(tmp, name))
        shutil.copyfile(os.path.join(EXAMPLES, "perkakas.krc"),
                        os.path.join(tmp, "perkakas.krc"))
        for name in names:
            original = os.path.join(tmp, name)
            before = read_bytes(original)
            middle = os.path.join(tmp, "middle-" + name)
            final = os.path.join(tmp, "final-" + name)
            code, out, err = translate_out(original, middle)
            check(code == 0, "%s translates to Koto Payang" % name,
                  (code, err))
            code, out, err = translate_out(middle, final, target="siulak")
            check(code == 0, "%s translates back to Siulak" % name,
                  (code, err))
            check(read_bytes(final) == before,
                  "%s round-trips byte for byte" % name,
                  (before[:40], read_bytes(final)[:40]))

        plain = write_text(os.path.join(tmp, "plain.krc"), "nyetak 1\n")
        middle = os.path.join(tmp, "plain.mid.krc")
        final = os.path.join(tmp, "plain.final.krc")
        translate_out(plain, middle)
        translate_out(middle, final, target="siulak")
        check(read_bytes(final) == b"# dialek: siulak\nnyetak 1\n",
              "a headerless file gains one header and otherwise round-trips",
              read_bytes(final))


# ---- 6. same dialect ------------------------------------------------------
def test_same_dialect():
    with tempfile.TemporaryDirectory() as tmp:
        source = read_bytes(os.path.join(EXAMPLES, "contoh.krc"))
        path = write_bytes(os.path.join(tmp, "same.krc"), source)
        code, out, err = translate(path, target="siulak")
        check(code == 0, "same-dialect translation exits 0", (code, err))
        check(out.encode("utf-8") == source,
              "same-dialect translation is byte-identical", out[:40])

        plain = write_text(os.path.join(tmp, "plain.krc"), "nyetak 1\n")
        code, out, err = translate(plain, target="siulak")
        check(code == 0 and out == "# dialek: siulak\nnyetak 1\n",
              "same-dialect translation adds a header", (code, out, err))

        shadow = write_text(
            os.path.join(tmp, "shadow.krc"),
            headered("guno panjang(x) { balik x }\nnyetak panjang(5)\n"))
        code, out, err = translate(shadow, target="siulak")
        check(code == 0, "same-dialect built-in shadowing is allowed",
              (code, err))
        check(out == read_text(shadow),
              "the same-dialect shadow copy is unchanged", repr(out))


# ---- 7. target gaps -------------------------------------------------------
def test_target_gaps():
    cases = [
        ("nantik(0.5)\n", "fn.wait"),
        ("barang x = daftar(1, 2)\n", "fn.list"),
        ("barang x = peta()\n", "fn.map"),
        ("nyetak isi([1], 1)\n", "fn.contains"),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        for index, (body, token_id) in enumerate(cases):
            path = write_text(os.path.join(tmp, "gap%d.krc" % index),
                              headered(body))
            out_path = os.path.join(tmp, "gap%d.out.krc" % index)
            code, out, err = translate_out(path, out_path)
            check(code == 1, "a missing target ID exits 1", (index, code, err))
            check(token_id in err, "the missing ID is named", (index, err))
            check(not os.path.exists(out_path),
                  "a refused translation writes no output", out_path)

        for name, token_id in (("contoh-berkas.krc", "fn.wait"),
                               ("contoh-daftar.krc", "fn.contains"),
                               ("contoh-peta.krc", "fn.contains")):
            source = os.path.join(EXAMPLES, name)
            before = read_bytes(source)
            out_path = os.path.join(tmp, "example-" + name)
            code, out, err = translate_out(source, out_path)
            check(code == 1, "%s is refused by Koto Payang" % name,
                  (code, err))
            check(token_id in err, "%s names %s" % (name, token_id), err)
            check(read_bytes(source) == before,
                  "%s is unchanged" % name)
            check(not os.path.exists(out_path),
                  "%s writes no output" % name)


# ---- 8. collisions and shadowing -----------------------------------------
def test_collisions():
    cases = [
        ("barang ndik = 1\nnyetak ndik\n", "kw.for", "kata kunci"),
        ("barang samu_dinga = 1\nnyetak samu_dinga\n", "op.eq", "operator"),
        ("barang panja = 1\nnyetak panja\n", "fn.length", "bawaan"),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        for index, (body, token_id, label) in enumerate(cases):
            path = write_text(os.path.join(tmp, "coll%d.krc" % index),
                              headered(body))
            code, out, err = translate(path)
            check(code == 1, "a target collision exits 1", (index, code, err))
            check(token_id in err, "the collision names the target ID",
                  (index, err))
            check(label in err, "the collision names the namespace",
                  (index, err))

        shadow = write_text(
            os.path.join(tmp, "shadow.krc"),
            headered("guno panjang(x) { balik x }\nnyetak panjang(1)\n"))
        code, out, err = translate(shadow)
        check(code == 1, "source built-in shadowing exits 1", (code, err))
        check("panjang" in err and "fn.length" in err,
              "shadowing names the name and the built-in", err)


# ---- 9. mode and type strings --------------------------------------------
def test_mode_and_type_strings():
    with tempfile.TemporaryDirectory() as tmp:
        mode = write_text(os.path.join(tmp, "mode.krc"),
                          headered('bukak("a.txt", "nambahkah")\n'))
        code, out, err = translate(mode)
        check(code == 0, "a direct mode argument translates", (code, err))
        check('bukuak("a.txt", "tambah")' in out,
              "the mode word and the call name translate", repr(out))

        for index, body in enumerate((
                'barang m = "nambahkah"\n',
                'baco("nambahkah")\n',
                'nyetak "nambahkah"\n')):
            path = write_text(os.path.join(tmp, "badmode%d.krc" % index),
                              headered(body))
            code, out, err = translate(path)
            check(code == 1, "a non-direct mode string is refused",
                  (index, code, err))
            check("string mode" in err, "the mode refusal is named",
                  (index, err))

        type_case = write_text(
            os.path.join(tmp, "type.krc"),
            headered('kalu mecem(1) samo "bilangan" { nyetak 1 }\n'))
        code, out, err = translate(type_case)
        check(code == 1, "a differing type string is refused", (code, err))
        check("string tipe" in err and "bilangan" in err,
              "the type refusal is named", err)

        shared = write_text(os.path.join(tmp, "shared.krc"),
                            headered('nyetak "daftar"\n'))
        code, out, err = translate(shared)
        check(code == 0, "a shared type word is allowed", (code, err))
        check('nytak "daftar"' in out, "the shared type word is unchanged",
              repr(out))

        data = write_text(os.path.join(tmp, "data.krc"),
                          headered('nyetak "barang"\n'))
        code, out, err = translate(data)
        check(code == 0 and '"barang"' in out,
              "ordinary string data is unchanged", (code, out, err))


# ---- 10. headers and refusals --------------------------------------------
def test_headers_and_refusals():
    with tempfile.TemporaryDirectory() as tmp:
        spaced = write_text(os.path.join(tmp, "spaced.krc"),
                            "  # dialek: siulak\nnyetak 1\n")
        code, out, err = translate(spaced)
        check(code == 0 and out.startswith("  # dialek: koto-payang\n"),
              "a header keeps its leading whitespace", (code, out, err))

        refusals = [
            ("malformed.krc", b"#dialek koto-payang\nnyetak 1\n",
             "header dialek"),
            ("unknown.krc", b"# dialek: hantu\nnyetak 1\n", "hantu"),
            ("bom.krc", b"\xef\xbb\xbfnyetak 1\n", "BOM"),
            ("binary.krc", b"\xff\xfe\x00", "UTF-8"),
            ("broken.krc", b"# dialek: siulak\nnyetak (\n", "tidak terduga"),
        ]
        for name, data, needle in refusals:
            path = write_bytes(os.path.join(tmp, name), data)
            out_path = os.path.join(tmp, "out-" + name)
            code, out, err = translate_out(path, out_path)
            check(code == 1, "%s exits 1" % name, (code, err))
            check(needle in err, "%s names the problem" % name, err)
            check(read_bytes(path) == data, "%s is unchanged" % name)
            check(not os.path.exists(out_path), "%s writes no output" % name)

        declared = write_text(
            os.path.join(tmp, "declared.krc"),
            "# dialek: koto-payang\nnytak 1\n")
        code, out, err = translate(declared, target="siulak",
                                   extra=["--dari", "siulak"])
        check(code == 0 and out == "# dialek: siulak\nnyetak 1\n",
              "a header wins over --dari", (code, out, err))

        code, out, err = translate(declared, target="siulak",
                                   extra=["--dari", "hantu"])
        check(code == 2, "--dari is validated even when a header wins",
              (code, out, err))

        sentinel = write_text(os.path.join(tmp, "sentinel.krc"), "keep me\n")
        bad = write_text(os.path.join(tmp, "bad.krc"),
                         "#dialek koto-payang\nnyetak 1\n")
        code, out, err = translate_out(bad, sentinel)
        check(code == 1, "a refusal with an existing --out exits 1",
              (code, err))
        check(read_text(sentinel) == "keep me\n",
              "a refusal leaves the existing output untouched",
              read_text(sentinel))


# ---- 11. line endings and bytes ------------------------------------------
def test_line_endings():
    with tempfile.TemporaryDirectory() as tmp:
        crlf = write_bytes(os.path.join(tmp, "crlf.krc"),
                           b"# dialek: siulak\r\nnyetak 1\r\n")
        code, out, err = translate(crlf)
        check(code == 0, "a CRLF file translates", (code, err))
        check(out == "# dialek: koto-payang\r\nnytak 1\r\n",
              "CRLF is preserved and the header uses CRLF", repr(out))
        check("\r\r\n" not in out, "stdout does not add a second CR",
              repr(out))

        tail = write_bytes(os.path.join(tmp, "tail.krc"),
                           b"# dialek: siulak\nnyetak 1")
        code, out, err = translate(tail)
        check(code == 0 and out == "# dialek: koto-payang\nnytak 1",
              "a missing final newline is preserved", (code, out, err))

        plain = write_bytes(os.path.join(tmp, "plain.krc"),
                            b"nyetak 1\r\n")
        code, out, err = translate(plain)
        check(code == 0 and out == "# dialek: koto-payang\r\nnytak 1\r\n",
              "a headerless CRLF file gets a CRLF header", (code, out, err))

        spacing = write_bytes(os.path.join(tmp, "spacing.krc"),
                              b"# dialek: siulak\n\tbarang\tx\t=\t1\n")
        code, out, err = translate(spacing)
        check(code == 0 and "\tnetakka_variabel\tx\t=\t1" in out,
              "tabs and repeated spaces are preserved", (code, out, err))


# ---- 12. CLI and output ---------------------------------------------------
def test_cli():
    with tempfile.TemporaryDirectory() as tmp:
        source = write_text(os.path.join(tmp, "prog.krc"),
                            headered("nyetak 1\n"))

        code, out, err = translate(source)
        check(code == 0 and "terjemah:" not in out,
              "stdout mode prints only the source", (code, out, err))

        out_path = os.path.join(tmp, "written.krc")
        code, out, err = translate_out(source, out_path)
        check(code == 0, "--out exits 0", (code, err))
        check("terjemah: wrote" in out, "--out prints a summary", repr(out))
        check("(siulak -> koto-payang)" in out,
              "the summary names both dialects", repr(out))
        check(read_bytes(out_path).startswith(b"# dialek: koto-payang\n"),
              "--out writes the header", read_bytes(out_path)[:30])

        dry_path = os.path.join(tmp, "dry.krc")
        code, out, err = translate_out(source, dry_path, extra=["--kering"])
        check(code == 0, "--kering exits 0", (code, err))
        check("terjemah: would write" in out,
              "--kering uses the would-write wording", repr(out))
        check(not os.path.exists(dry_path), "--kering writes nothing")

        overwrite = write_text(os.path.join(tmp, "overwrite.krc"), "old\n")
        code, out, err = translate_out(source, overwrite)
        check(code == 0 and read_text(overwrite).startswith(
            "# dialek: koto-payang\n"),
              "an existing output is replaced atomically", (code, err))

        code, out, err = translate(source, extra=["--out", source])
        check(code == 2, "--out equal to the input exits 2", (code, err))

        code, out, err = translate(source, extra=["--kering"])
        check(code == 2, "--kering without --out exits 2", (code, err))

        cases = [
            (["terjemah", str(source)], "a missing --ke"),
            (["terjemah", str(source), "--ke", "hantu"], "an unknown target"),
            (["terjemah", str(source), "--ke", "koto-payang",
              "--dari", "hantu"], "an unknown --dari"),
            (["terjemah", str(source), "--ke"], "a missing --ke value"),
            (["terjemah", str(source), "--ke="], "an empty --ke value"),
            (["terjemah", str(source), "--ke", "koto-payang",
              "--out"], "a missing --out value"),
            (["terjemah", str(source), "--ke", "koto-payang",
              "--dari"], "a missing --dari value"),
            (["terjemah", str(source), "--ke", "koto-payang",
              "--nope"], "an unknown option"),
            (["terjemah", str(source), str(source), "--ke", "koto-payang"],
             "extra arguments"),
            (["terjemah", str(source), "--ke", "koto-payang",
              "--ketat"], "--ketat"),
            (["terjemah"], "no input"),
        ]
        for argv, label in cases:
            code, out, err = capture(main, argv)
            check(code == 2, "%s exits 2" % label, (code, out, err))

        notes = write_text(os.path.join(tmp, "notes.txt"), "x")
        code, out, err = capture(
            main, ["terjemah", str(notes), "--ke", "koto-payang"])
        check(code == 2, "a non-.krc input exits 2", (code, err))

        missing = os.path.join(tmp, "missing.krc")
        code, out, err = capture(
            main, ["terjemah", missing, "--ke", "koto-payang"])
        check(code == 2, "a missing input exits 2", (code, err))

        code, out, err = capture(
            main, ["terjemah", str(source),
                   "--ke=" + "koto-payang", "--out=" + out_path])
        check(code == 0 and "terjemah: wrote" in out,
              "the --flag=value forms work", (code, out, err))

        code, out, err = capture(main, ["terjemah", "--help"])
        check(code == 0, "terjemah --help exits 0", (code, err))
        for flag in ("--ke", "--dari", "--out", "--kering"):
            check(flag in out, "%s is documented" % flag, repr(out))

        bad_out = os.path.join(tmp, "no-such-dir", "out.krc")
        code, out, err = translate_out(source, bad_out)
        check(code == 1, "an unwritable --out exits 1", (code, err))


# ---- 13. imports and packaging -------------------------------------------
def test_imports_and_packaging():
    with tempfile.TemporaryDirectory() as tmp:
        lib = write_text(os.path.join(tmp, "lib.krc"),
                         headered("barang nilai = 7\n"))
        program = write_text(
            os.path.join(tmp, "main.krc"),
            headered('ambik "lib"\nnyetak nilai\n'))
        lib_before = read_bytes(lib)
        code, before, err = capture(main, [str(program)])
        check(code == 0 and before == "7\n", "the mixed-import source runs",
              (code, before, err))

        translated = os.path.join(tmp, "main.koto.krc")
        code, out, err = translate_out(program, translated)
        check(code == 0, "the mixed-import main translates", (code, err))
        check('impor "lib"' in read_text(translated),
              "the import keyword changes and the path stays",
              read_text(translated))
        check(read_bytes(lib) == lib_before, "the imported file is untouched")
        code, after, err = capture(main, [translated])
        check(code == 0 and after == before,
              "the translated mixed-dialect program prints the same output",
              (code, after, before))

        moved = os.path.join(tmp, "elsewhere")
        os.mkdir(moved)
        code, out, err = translate_out(program, os.path.join(moved, "main.krc"))
        check(code == 0, "a moved output still translates", (code, err))
        check("impor 'lib' tidak ditemukan" in err,
              "a moved output warns about a broken literal import", err)

        copy_main = os.path.join(tmp, "contoh-impor.krc")
        shutil.copyfile(os.path.join(EXAMPLES, "contoh-impor.krc"), copy_main)
        shutil.copyfile(os.path.join(EXAMPLES, "perkakas.krc"),
                        os.path.join(tmp, "perkakas.krc"))
        code, expected, err = capture(main, [copy_main])
        check(code == 0 and expected == EXPECTED_IMPORT,
              "the import example runs before translation",
              (code, expected, err))
        translated_example = os.path.join(tmp, "contoh-impor.koto.krc")
        code, out, err = translate_out(copy_main, translated_example)
        check(code == 0, "the import example translates", (code, err))
        code, actual, err = capture(main, [translated_example])
        check(code == 0 and actual == expected,
              "the translated import example keeps its output",
              (code, actual, expected))

        build = pathlib.Path(tmp) / "app"
        build.mkdir()
        shutil.copy(os.path.join(ROOT, "kerincilang.py"),
                    build / "kerincilang.py")
        shutil.copytree(os.path.join(ROOT, "core"), build / "core")
        shutil.copytree(os.path.join(ROOT, "dialects"), build / "dialects",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (build / "__main__.py").write_text(
            "import sys\nfrom kerincilang import main\nsys.exit(main())\n",
            encoding="utf-8")
        pyz = pathlib.Path(tmp) / "krc.pyz"
        zipapp.create_archive(str(build), str(pyz),
                              interpreter="/usr/bin/env python3")

        work = pathlib.Path(tmp) / "clean"
        work.mkdir()
        source = work / "prog.krc"
        source.write_bytes(b"nyetak 6 * 7\n")
        result = subprocess.run(
            [sys.executable, str(pyz), "terjemah", str(source),
             "--ke", "koto-payang", "--out", str(work / "prog.koto.krc")],
            cwd=str(work), capture_output=True, text=True, encoding="utf-8")
        check(result.returncode == 0, "the zipapp runs terjemah",
              (result.returncode, result.stdout, result.stderr))
        check(read_bytes(work / "prog.koto.krc").startswith(
            b"# dialek: koto-payang\n"),
              "the zipapp writes the target header",
              read_bytes(work / "prog.koto.krc")[:30])
        result = subprocess.run(
            [sys.executable, str(pyz), str(work / "prog.koto.krc")],
            cwd=str(work), capture_output=True, text=True, encoding="utf-8")
        check(result.returncode == 0 and result.stdout == "42\n",
              "the zipapp runs the translated file",
              (result.returncode, result.stdout, result.stderr))


def main_test():
    test_basic()
    test_user_names()
    test_strings_and_comments()
    test_operators()
    test_round_trip()
    test_same_dialect()
    test_target_gaps()
    test_collisions()
    test_mode_and_type_strings()
    test_headers_and_refusals()
    test_line_endings()
    test_cli()
    test_imports_and_packaging()
    print("\nFAILED:" if FAILED else "\nALL PASSED", len(FAILED) or "")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main_test())
