"""Tests for the worksheet pipeline.

Run with: python3 tests/test_worksheet.py
"""
import contextlib
import copy
import csv
import io
import json
import os
import pathlib
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import lembar_kerja as lembar  # noqa: E402

FAILED = []
TEMP = tempfile.TemporaryDirectory()
BASE = pathlib.Path(TEMP.name)
W = lembar.W


def check(ok, label, detail=""):
    print("PASS" if ok else "FAIL", label, "" if ok else "-> " + str(detail))
    if not ok:
        FAILED.append(label)


def workdir(name):
    path = BASE / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = lembar.main(list(args))
    return code, out.getvalue(), err.getvalue()


def read_rows(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    return list(csv.DictReader(io.StringIO(text, newline="")))


def write_rows(path, rows):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=lembar.COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows([{column: row.get(column, "") for column in lembar.COLUMNS}
                      for row in rows])
    pathlib.Path(path).write_bytes(out.getvalue().encode("utf-8"))


def find_row(rows, ident):
    for row in rows:
        if row["id"] == ident:
            return row
    raise AssertionError("no row %r" % ident)


def set_row(rows, ident, **values):
    find_row(rows, ident).update(values)


def new_csv(name, code="uji"):
    folder = workdir(name)
    path = folder / (code + ".csv")
    result, out, err = run("buat", "--kode", code, "--csv", str(path))
    assert result == 0, (result, out, err)
    return path


def mutate_csv(name, change, code="uji"):
    path = new_csv(name, code)
    rows = read_rows(path)
    change(rows)
    write_rows(path, rows)
    return path


def skeleton(path, status="draft", code="uji", **over):
    data = {
        "code": code,
        "name": "Uji",
        "status": status,
        "core": "0.6",
        "revision": 7,
        "parent": None,
        "license": "CC BY-SA 4.0",
        "maintainer": "Penguji",
        "reviewer": "Penguji" if status == "approved" else None,
        "sources": ["uji, 2026"],
        "orthography": "test spelling",
        "words": {},
        "messages": {},
    }
    data.update(over)
    pathlib.Path(path).write_text(json.dumps(data, ensure_ascii=False),
                                  encoding="utf-8")
    return data


def periksa(path, *extra):
    return run("periksa", "--kode", "uji", "--csv", str(path), *extra)


def expect_code(label, path, code, result=1):
    got, out, err = periksa(path)
    check(got == result and code in out, label,
          "exit %r, output %r, stderr %r" % (got, out, err))


# 1. buat: exact header, 137 rows, tier/id order, all todo.
def test_buat():
    path = new_csv("buat")
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    check(lines[0] == "id,tier,namespace,en,id_gloss,answer,notes,status",
          "buat writes the exact header", lines[0])
    rows = read_rows(path)
    check(len(rows) == 137, "buat writes 137 rows", len(rows))
    check([row["id"] for row in rows] == lembar.ORDERED_IDS,
          "buat writes tier/id order")
    check(all(row["status"] == "todo" for row in rows),
          "buat writes todo rows")
    check(all(row["answer"] == "" and row["notes"] == "" for row in rows),
          "buat leaves answers and notes empty")
    check(text.endswith("\n") and "\r" not in text,
          "buat writes LF with a final newline")


# 2. buat refuses an existing CSV; --paksa replaces it.
def test_buat_refuses():
    path = new_csv("buat-refuse")
    rows = read_rows(path)
    set_row(rows, "kw.if", answer="kalu", status="draft")
    write_rows(path, rows)
    result, out, err = run("buat", "--kode", "uji", "--csv", str(path))
    check(result == 1 and "already exists" in out,
          "buat refuses an existing CSV", (result, out))
    check(find_row(read_rows(path), "kw.if")["answer"] == "kalu",
          "a refused buat leaves the answers alone")
    result, out, err = run("buat", "--kode", "uji", "--csv", str(path),
                           "--paksa")
    check(result == 0, "buat --paksa succeeds", (result, out))
    check(all(row["status"] == "todo" and row["answer"] == ""
              for row in read_rows(path)),
          "buat --paksa clears the answers")


# 3. perbarui restores, refreshes, preserves, and refuses an unknown row.
def test_perbarui():
    path = new_csv("perbarui")
    rows = read_rows(path)
    set_row(rows, "kw.if", answer="kalu", status="draft")
    set_row(rows, "kw.if", en="stale")
    rows = [row for row in rows if row["id"] != "kw.else"]
    write_rows(path, rows)
    result, out, err = run("perbarui", "--kode", "uji", "--csv", str(path))
    check(result == 0, "perbarui succeeds", (result, out))
    rows = read_rows(path)
    check(find_row(rows, "kw.if")["answer"] == "kalu",
          "perbarui preserves an answer")
    check(find_row(rows, "kw.if")["en"] == lembar.IDS["kw.if"]["en"],
          "perbarui refreshes a catalogue column")
    check(find_row(rows, "kw.else")["status"] == "todo",
          "perbarui restores a deleted row as todo")

    rows = read_rows(path)
    extra = dict(find_row(rows, "kw.if"))
    extra["id"] = "zzz.bogus"
    rows.append(extra)
    write_rows(path, rows)
    before = path.read_bytes()
    result, out, err = run("perbarui", "--kode", "uji", "--csv", str(path))
    check(result == 1 and "unknown-id" in out,
          "perbarui refuses an unknown row", (result, out))
    check(path.read_bytes() == before,
          "a refused perbarui writes nothing")


# 4. periksa accepts a minimal sheet.
def test_minimal():
    path = new_csv("minimal")
    result, out, err = periksa(path)
    check(result == 0 and "0 errors" in out,
          "periksa accepts a minimal sheet", (result, out))


# 5. Every structure/answer code has a failing fixture.
def test_codes():
    path = new_csv("code-header")
    path.write_text("id,tier,namespace,en,id_gloss,answer,notes\n",
                    encoding="utf-8")
    expect_code("csv-header is reported", path, "csv-header")

    path = new_csv("code-width")
    path.write_bytes(path.read_bytes() + b"a,b,c\n")
    expect_code("csv-width is reported", path, "csv-width")

    path = new_csv("code-bom")
    path.write_bytes(b"\xef\xbb\xbf" + path.read_bytes())
    expect_code("csv-bom is reported", path, "csv-bom")

    path = mutate_csv("code-unknown", lambda rows: rows.append(
        dict(find_row(rows, "kw.if"), id="zzz.bogus")))
    expect_code("unknown-id is reported", path, "unknown-id")

    path = mutate_csv("code-missing", lambda rows: rows.remove(
        find_row(rows, "kw.else")))
    expect_code("missing-id is reported", path, "missing-id")

    path = mutate_csv("code-duplicate", lambda rows: rows.append(
        dict(find_row(rows, "kw.if"))))
    expect_code("duplicate-id is reported", path, "duplicate-id")

    path = mutate_csv("code-catalogue",
                      lambda rows: set_row(rows, "kw.if", en="stale"))
    expect_code("catalogue-value is reported", path, "catalogue-value")

    path = mutate_csv("code-status",
                      lambda rows: set_row(rows, "kw.if", status="nope"))
    expect_code("status is reported", path, "status")

    path = mutate_csv("code-empty", lambda rows: set_row(
        rows, "kw.if", status="draft", answer=""))
    expect_code("answer-empty is reported", path, "answer-empty")

    path = mutate_csv("code-choice", lambda rows: set_row(
        rows, "kw.if", status="draft", answer="kalu/lamun"))
    expect_code("answer-choice is reported", path, "answer-choice")

    path = mutate_csv("code-formula", lambda rows: set_row(
        rows, "kw.if", notes="=1+1"))
    result, out, err = periksa(path)
    check(result == 0 and "csv-formula" in out
          and "1 warning" in out,
          "csv-formula is a warning and exits 0", (result, out))


# 6. Word normalization.
def test_words():
    check(lembar.normalize_word("  Kalu   Laen ") == "kalu_laen",
          "word: NFC, trim, case, whitespace", lembar.normalize_word("  Kalu   Laen "))
    check(lembar.normalize_word("Nyetak()") == "nyetak",
          "word: one trailing () is removed")
    check(lembar.normalize_word("BETUL") == "betul",
          "word: uppercase is lowered")

    path = mutate_csv("word-charset", lambda rows: set_row(
        rows, "kw.if", status="draft", answer="ka-lu"))
    expect_code("word-charset: hyphen", path, "word-charset")

    path = mutate_csv("word-choice", lambda rows: set_row(
        rows, "kw.import", status="draft", answer="impor/masukka"))
    expect_code("answer-choice: slash", path, "answer-choice")

    path = mutate_csv("word-digit", lambda rows: set_row(
        rows, "kw.if", status="draft", answer="1kalu"))
    expect_code("word-charset: leading digit", path, "word-charset")


# 7. Message normalization and placeholders.
def test_messages():
    check(lembar.normalize_message("  Nama  Tidak  Dikenal: {name}  ")
          == "Nama  Tidak  Dikenal: {name}",
          "message: trim and case are preserved")

    path = mutate_csv("message-valid", lambda rows: set_row(
        rows, "msg.name.undefined", status="draft",
        answer="  Nama  Tidak  Dikenal: {name}  "))
    result, out, err = periksa(path, "--tulis")
    check(result == 0, "a valid message passes", (result, out))
    check(find_row(read_rows(path), "msg.name.undefined")["answer"]
          == "Nama  Tidak  Dikenal: {name}",
          "message normalization preserves internal spaces")

    path = mutate_csv("message-renamed", lambda rows: set_row(
        rows, "msg.name.undefined", status="draft",
        answer="Nama tidak dikenal: {nama}"))
    expect_code("message-placeholder: renamed", path, "message-placeholder")


# 8. Clash names both IDs.
def test_clash():
    def change(rows):
        set_row(rows, "kw.if", status="draft", answer="kalu")
        set_row(rows, "op.eq", status="draft", answer="kalu")
    path = mutate_csv("clash", change)
    result, out, err = periksa(path)
    check(result == 1 and "clash" in out and "kw.if" in out
          and "op.eq" in out,
          "clash names both IDs", (result, out))


# 9. periksa --tulis writes only without errors.
def test_tulis():
    path = mutate_csv("tulis", lambda rows: set_row(
        rows, "kw.if", status="draft", answer="  Kalu   Laen "))
    result, out, err = periksa(path, "--tulis")
    check(result == 0, "periksa --tulis succeeds", (result, out))
    check(find_row(read_rows(path), "kw.if")["answer"] == "kalu_laen",
          "periksa --tulis writes the normalized answer")

    path = mutate_csv("tulis-error", lambda rows: set_row(
        rows, "kw.if", status="draft", answer="ka-lu"))
    before = path.read_bytes()
    result, out, err = periksa(path, "--tulis")
    check(result == 1 and path.read_bytes() == before,
          "periksa --tulis leaves the file alone on an error", (result, out))


# 10. DOCX is readable, deterministic, and has no extra entries.
def test_docx():
    folder = workdir("docx")
    csv_path = folder / "uji.csv"
    docx_path = folder / "uji.docx"
    run("buat", "--kode", "uji", "--csv", str(csv_path))
    result, out, err = run("docx", "--kode", "uji", "--csv", str(csv_path),
                           "--docx", str(docx_path))
    check(result == 0, "docx writes", (result, out))
    first = docx_path.read_bytes()
    answers, findings = lembar.read_docx(docx_path)
    check(not findings and len(answers) == 137,
          "docx reads back 137 IDs", (findings, len(answers)))
    result, out, err = run("docx", "--kode", "uji", "--csv", str(csv_path),
                           "--docx", str(docx_path), "--paksa")
    check(result == 0 and docx_path.read_bytes() == first,
          "docx bytes are deterministic", (result, out))
    with zipfile.ZipFile(io.BytesIO(first)) as archive:
        names = archive.namelist()
    check(names == ["[Content_Types].xml", "_rels/.rels",
                    "word/document.xml"],
          "docx has only the three expected entries", names)


# 11. baca round trip.
def test_baca():
    folder = workdir("baca")
    csv_path = folder / "uji.csv"
    docx_source = folder / "source.csv"
    docx_path = folder / "uji.docx"
    run("buat", "--kode", "uji", "--csv", str(csv_path))
    run("buat", "--kode", "uji", "--csv", str(docx_source))

    rows = read_rows(csv_path)
    set_row(rows, "kw.if", answer="kalu", status="draft")
    set_row(rows, "kw.print", answer="cetak", status="reviewed")
    set_row(rows, "kw.var", answer="", status="todo")
    set_row(rows, "kw.else", answer="lama", status="reviewed")
    set_row(rows, "kw.for", answer="lama", status="reviewed")
    write_rows(csv_path, rows)

    source = read_rows(docx_source)
    set_row(source, "kw.if", answer="kalu", status="draft")
    set_row(source, "kw.print", answer="cetak", status="reviewed",
            notes="new\nnote")
    set_row(source, "kw.var", answer="baru", status="draft")
    set_row(source, "kw.else", answer="baru", status="draft")
    set_row(source, "kw.for", answer="", status="todo")
    write_rows(docx_source, source)
    run("docx", "--kode", "uji", "--csv", str(docx_source),
        "--docx", str(docx_path))

    result, out, err = run("baca", "--kode", "uji", "--csv", str(csv_path),
                           "--docx", str(docx_path))
    check(result == 0 and "no changes" not in out,
          "baca reports changes", (result, out))
    result, out, err = run("baca", "--kode", "uji", "--csv", str(csv_path),
                           "--docx", str(docx_path), "--tulis")
    check(result == 0, "baca --tulis succeeds", (result, out))

    rows = read_rows(csv_path)
    check(find_row(rows, "kw.if")["answer"] == "kalu"
          and find_row(rows, "kw.if")["status"] == "draft",
          "baca keeps an unchanged answer")
    check(find_row(rows, "kw.print")["answer"] == "cetak"
          and find_row(rows, "kw.print")["status"] == "reviewed"
          and find_row(rows, "kw.print")["notes"] == "new\nnote",
          "baca keeps an approval when only the note changed")
    check(find_row(rows, "kw.var")["answer"] == "baru"
          and find_row(rows, "kw.var")["status"] == "draft",
          "baca turns a new answer into draft")
    check(find_row(rows, "kw.else")["answer"] == "baru"
          and find_row(rows, "kw.else")["status"] == "draft",
          "baca downgrades a changed answer")
    check(find_row(rows, "kw.for")["answer"] == ""
          and find_row(rows, "kw.for")["status"] == "todo",
          "baca clears an empty answer to todo")
    check(all(find_row(rows, ident)["status"] != "reviewed"
              for ident in ("kw.var", "kw.else", "kw.for")),
          "baca never invents reviewed")


# 12. baca rejects a DOCX with no ID column or a duplicate ID.
def rewrite_document(docx_path, change):
    with zipfile.ZipFile(docx_path) as archive:
        entries = [(info.filename, archive.read(info.filename))
                   for info in archive.infolist()]
    root = ET.fromstring(dict(entries)["word/document.xml"])
    change(root)
    document = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, data in entries:
            if name == "word/document.xml":
                data = document
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, data)
    docx_path.write_bytes(buffer.getvalue())


def test_baca_errors():
    folder = workdir("baca-errors")
    csv_path = folder / "uji.csv"
    docx_path = folder / "uji.docx"
    run("buat", "--kode", "uji", "--csv", str(csv_path))
    run("docx", "--kode", "uji", "--csv", str(csv_path),
        "--docx", str(docx_path))

    def drop_id(root):
        table = root.find(".//" + W + "tbl")
        cell = table.find(W + "tr").find(W + "tc")
        cell.find(".//" + W + "t").text = "Fake"

    no_id = folder / "no-id.docx"
    no_id.write_bytes(docx_path.read_bytes())
    rewrite_document(no_id, drop_id)
    result, out, err = run("baca", "--kode", "uji", "--csv", str(csv_path),
                           "--docx", str(no_id))
    check(result == 1 and "docx-format" in out and "ID column" in out,
          "baca rejects a DOCX without an ID column", (result, out))

    def duplicate_id(root):
        table = root.find(".//" + W + "tbl")
        rows = table.findall(W + "tr")
        table.append(copy.deepcopy(rows[1]))

    duplicate = folder / "duplicate.docx"
    duplicate.write_bytes(docx_path.read_bytes())
    rewrite_document(duplicate, duplicate_id)
    result, out, err = run("baca", "--kode", "uji", "--csv", str(csv_path),
                           "--docx", str(duplicate))
    check(result == 1 and "docx-format" in out
          and "more than once" in out,
          "baca rejects a duplicate ID", (result, out))

    def add_old_table(root):
        body = root.find(W + "body")
        table = body.find(W + "tbl")
        other = copy.deepcopy(table)
        other.find(W + "tr").find(W + "tc").find(".//" + W + "t").text = "#"
        body.append(other)

    old_sheet = folder / "old-sheet.docx"
    old_sheet.write_bytes(docx_path.read_bytes())
    rewrite_document(old_sheet, add_old_table)
    result, out, err = run("baca", "--kode", "uji", "--csv", str(csv_path),
                           "--docx", str(old_sheet))
    check(result == 1 and "second table" in out,
          "baca rejects a pasted second sheet", (result, out))

    def change_header(root):
        table = root.find(".//" + W + "tbl")
        header = table.find(W + "tr")
        cells = header.findall(W + "tc")
        cells[-1].find(".//" + W + "t").text = "Comments"

    bad_header = folder / "bad-header.docx"
    bad_header.write_bytes(docx_path.read_bytes())
    rewrite_document(bad_header, change_header)
    result, out, err = run("baca", "--kode", "uji", "--csv", str(csv_path),
                           "--docx", str(bad_header))
    check(result == 1 and "table header" in out,
          "baca rejects a different header", (result, out))


# 13. json merges accepted answers and keeps metadata.
def test_json():
    folder = workdir("json")
    csv_path = folder / "uji.csv"
    skeleton_path = folder / "uji.json"
    run("buat", "--kode", "uji", "--csv", str(csv_path))
    rows = read_rows(csv_path)
    set_row(rows, "kw.if", answer="kalu", status="draft")
    set_row(rows, "kw.print", answer="cetak", status="reviewed")
    set_row(rows, "kw.else", answer="lain", status="rejected")
    set_row(rows, "kw.var", answer="", status="todo")
    set_row(rows, "msg.name.undefined", answer="Nama tidak dikenal: {name}",
            status="draft")
    write_rows(csv_path, rows)
    original = skeleton(skeleton_path, status="draft", name="Koto Payang",
                        revision=9, orthography="spelling")
    result, out, err = run("json", "--kode", "uji", "--csv", str(csv_path),
                           "--json", str(skeleton_path))
    check(result == 0, "json exports", (result, out))
    data = json.loads(skeleton_path.read_text(encoding="utf-8"))
    check(set(data["words"]) == {"kw.if", "kw.print"},
          "json merges words and omits todo/rejected", sorted(data["words"]))
    check(set(data["messages"]) == {"msg.name.undefined"},
          "json merges messages", sorted(data["messages"]))
    check(all(data[key] == original[key] for key in
              ("name", "status", "core", "revision", "parent", "license",
               "maintainer", "reviewer", "sources", "orthography")),
          "json preserves metadata and revision")
    from dialects import loader
    dialect = loader.load_dialect("uji", root=folder)
    check(dialect.code == "uji" and dialect.words["kw.if"] == "kalu",
          "the exported file loads")


# 14. json writes nothing when validation fails.
def test_json_invalid():
    folder = workdir("json-invalid")
    csv_path = folder / "uji.csv"
    skeleton_path = folder / "uji.json"
    run("buat", "--kode", "uji", "--csv", str(csv_path))
    rows = read_rows(csv_path)
    set_row(rows, "kw.if", answer="kalu", status="draft")
    set_row(rows, "op.eq", answer="kalu", status="draft")
    write_rows(csv_path, rows)
    skeleton(skeleton_path)
    before = skeleton_path.read_bytes()
    result, out, err = run("json", "--kode", "uji", "--csv", str(csv_path),
                           "--json", str(skeleton_path))
    check(result == 1 and "clash" in out,
          "json refuses a clash", (result, out))
    check(skeleton_path.read_bytes() == before,
          "a refused json writes nothing")


# 15. laporan prints counts, gaps, and readiness.
def test_laporan():
    path = mutate_csv("laporan", lambda rows: set_row(
        rows, "kw.if", answer="kalu", status="reviewed"))
    result, out, err = run("laporan", "--kode", "uji", "--csv", str(path))
    check(result == 0, "laporan exits 0", (result, out))
    check("uji: 137 ids" in out, "laporan prints the ID total", out)
    check("tier 1: 1/32 answered, 1 reviewed" in out,
          "laporan prints tier 1", out)
    check("missing tier 1:" in out and "kw.and" in out,
          "laporan lists missing tier-1 IDs", out)
    check("ready for review: no (tier 1 has 31 unreviewed)" in out,
          "laporan prints review readiness", out)
    check("ready for approved: no" in out,
          "laporan prints approved readiness", out)


# 16. --siap applies the readiness gate.
def review_all_tier1(rows):
    for row in rows:
        if lembar.IDS[row["id"]]["tier"] == 1:
            row["answer"] = row["id"].replace(".", "_")
            row["status"] = "reviewed"


def test_siap():
    folder = workdir("siap")
    draft_csv = new_csv("siap-draft")
    draft_skeleton = folder / "draft.json"
    skeleton(draft_skeleton, status="draft")
    result, out, err = periksa(draft_csv, "--siap", "--json",
                               str(draft_skeleton))
    check(result == 0, "a draft skeleton passes with unreviewed rows",
          (result, out))

    review_csv = new_csv("siap-review")
    review_skeleton = folder / "review.json"
    skeleton(review_skeleton, status="review")
    result, out, err = periksa(review_csv, "--siap", "--json",
                               str(review_skeleton))
    check(result == 1 and "not ready for review" in out,
          "a review skeleton fails with an unreviewed tier 1", (result, out))

    ready_csv = mutate_csv("siap-ready", review_all_tier1)
    result, out, err = periksa(ready_csv, "--siap", "--json",
                               str(review_skeleton))
    check(result == 0, "a review skeleton passes when tier 1 is reviewed",
          (result, out))

    approved_skeleton = folder / "approved.json"
    skeleton(approved_skeleton, status="approved")
    result, out, err = periksa(ready_csv, "--siap", "--json",
                               str(approved_skeleton))
    check(result == 1 and "not ready for approved" in out
          and "tier 2" in out,
          "an approved skeleton fails with an unreviewed tier 2",
          (result, out))


# 17. Usage errors exit 2.
def test_usage():
    cases = [
        ("no --kode", ()),
        ("unknown subcommand", ("nope", "--kode", "uji")),
        ("unknown flag", ("periksa", "--kode", "uji", "--bogus")),
    ]
    for label, args in cases:
        result, out, err = run(*args)
        check(result == 2 and "lembar_kerja:" in err,
              "usage error: " + label, (result, out, err))
    result, out, err = run("--help")
    check(result == 0 and "Usage:" in out and "periksa" in out,
          "--help documents the commands", (result, out))


def main():
    tests = [
        test_buat,
        test_buat_refuses,
        test_perbarui,
        test_minimal,
        test_codes,
        test_words,
        test_messages,
        test_clash,
        test_tulis,
        test_docx,
        test_baca,
        test_baca_errors,
        test_json,
        test_json_invalid,
        test_laporan,
        test_siap,
        test_usage,
    ]
    for test in tests:
        test()
    print()
    if FAILED:
        print("%d FAILED: %s" % (len(FAILED), ", ".join(FAILED)))
        return 1
    print("all worksheet tests passed")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        TEMP.cleanup()
