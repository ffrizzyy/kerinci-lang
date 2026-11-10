"""Tests for the Koto Payang review-state dialect.

The committed CSV and JSON must match the approved mapping, the review gate
must pass, and a Koto Payang program must run with its own words and messages.

Run with: python3 tests/test_koto_payang.py
"""
import collections
import contextlib
import csv
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import kerincilang  # noqa: E402
from kerincilang import main, run_source  # noqa: E402
from dialects import loader  # noqa: E402

FAILED = []
IDS = kerincilang.CATALOG["ids"]
DIALECTS = os.path.join(ROOT, "dialects")
CSV_PATH = os.path.join(DIALECTS, "src", "koto-payang.csv")
JSON_PATH = os.path.join(DIALECTS, "koto-payang.json")
MD_PATH = os.path.join(DIALECTS, "koto-payang.md")

HEADER = ["id", "tier", "namespace", "en", "id_gloss", "answer", "notes",
          "status"]
PLACEHOLDER_RE = re.compile(r"\{([a-z][a-z0-9_]*)\}")

EXPECTED_WORDS = {
    # Tier 1
    "kw.var": "netakka_variabel",
    "kw.const": "netakka_konstanta",
    "kw.func": "jeloehka",
    "kw.return": "baluikka",
    "kw.if": "kalu",
    "kw.else": "nga_laen",
    "kw.while": "selamu",
    "kw.for": "ndik",
    "kw.in": "daling",
    "kw.switch": "cocokka",
    "kw.import": "impor",
    "kw.try": "cubea",
    "kw.catch": "kecuali",
    "kw.raise": "timbaoka",
    "kw.break": "slese",
    "kw.continue": "lanjutka",
    "kw.print": "nytak",
    "kw.input": "masukka",
    "kw.true": "betiu",
    "kw.false": "salah",
    "kw.null": "kusao",
    "kw.and": "nga",
    "kw.or": "atau",
    "kw.not": "iduak",
    "kw.begin": "mulai",
    "kw.end": "selesai",
    "op.eq": "samu_dinga",
    "op.ne": "iduak_samu_dinga",
    "op.gt": "lebih_geduang_dari",
    "op.lt": "lebih_nik_dari",
    "op.ge": "lebih_geduang_atau_samu_dinga",
    "op.le": "lebih_nik_atau_samu_dinga",
    # Tier 2 functions
    "fn.add": "tambah",
    "fn.sub": "kura",
    "fn.mul": "kali",
    "fn.div": "bagi",
    "fn.length": "panja",
    "fn.range": "rentang",
    "fn.sort": "terurut",
    "fn.reverse": "tebaluik",
    "fn.int": "bilangan_buluak",
    "fn.float": "desimal",
    "fn.text": "tulisan",
    "fn.append": "tambahka",
    "fn.split": "pecah",
    "fn.join": "basatau",
    "fn.open": "bukuak",
    "fn.read": "bacea",
    "fn.write": "tulaih",
    "fn.close": "tutamp",
    "fn.delete": "ngapih_berkas",
    "fn.type": "tipe",
    # Tier 2 types
    "type.int": "bilangan_buluak",
    "type.float": "bilangan_bakoma",
    "type.str": "tulisan",
    "type.list": "daftar",
    "type.map": "kamus",
    "type.func": "pungsi",
    "type.file": "berkas",
    "type.null": "kusao",
    # Tier 2 modes
    "mode.read": "bacea",
    "mode.write": "tulaih",
    "mode.append": "tambah",
}

EXPECTED_MESSAGES = {
    "msg.import.in_module": "daling modul '{name}': {message}",
    "msg.name.undefined": "namu lao dijeloehka: {name}",
    "msg.name.undeclared": "namu lao ditetakka: {name} (maki '{var_word}' duliu)",
    "msg.name.constant": "'{name}' adalah konstanta ('{const_word}') nga dak bisa diubuah",
    "msg.value.div_zero": "Pembagian dinga nol",
    "msg.value.operator": "Operator '{op}' nyendak dipake kik {left} nga {right}",
    "msg.value.convert": "Nynendak ngubuoah {value} jadi {target}",
    "msg.value.index_range": "Indeks kik luwua jangkauan: {index} (panja {length})",
    "msg.value.index_type": "Indeks harus bilangan buluak",
    "msg.value.key_missing": "sidiak besuao kuncai: {key}",
    "msg.value.key_type": "Kuncai peta harus tulisan atau bilangan buluak",
    "msg.value.text_immutable": "Tulisan nyendak diubuah per huruf",
    "msg.call.arity": "Pungsi butuh {arity} argumen, dibaguih {count}",
    "msg.call.not_function": "Nga diimbua iduak pungsi",
    "msg.call.depth": "Panggilan pungsi daling nia (lebih dari {max})",
    "msg.file.not_found": "Sidiak besuao berkas: {path}",
    "msg.file.closed": "Berkas lah ditutamp {path}",
    "msg.file.wrong_mode": ("Berkas inih dibukuak ndik '{mode}', dak buluih "
                            "dipake oleh '{fn}'"),
    "msg.syntax.bad_char": "Baris {line}: karakter nga sidiak dikenal {text}",
    "msg.syntax.unexpected": "Baris {line}: dak nyengkao {text}",
    "msg.syntax.expected": "Baris {line}: diharaok {what}, basuao {text}",
    "msg.func.return_outside": "Baris {line}: '{word}' hanya buluih daling pungsi",
    "msg.loop.break_outside": "Baris {line}: '{word}' hanya buluih daling pangulangan",
    "msg.syntax.try_requires_catch": ("Baris {line}: blok '{try_word}' harus "
                                      "dinga '{catch_word}' nga blok penanganan"),
    "msg.import.circular": "Impor melingkar: {name}",
    "msg.syntax.escape": r"Baris {line}: urutan escape nga sidiak dikenal: \{c}",
}

TODO_WORDS = {
    "fn.list": "daftar",
    "fn.map": "peta",
    "fn.contains": "meriksu",
    "fn.wait": "nunggu",
    "type.bool": "betiu_salah",
    "reserved.error": "kesalahan",
}

TODO_MESSAGES = {
    "msg.call.builtin_arity": "Pungsi {fn} butuh {arity} argumen, dibaguih {count}",
    "msg.call.depth_short": "Panggilan pungsi daling nia",
    "msg.dialect.header": "Baris {line}: header dialek dak valid: {text}",
    "msg.dialect.invalid": "Dialek {code} dak valid: {detail}",
    "msg.dialect.unknown": "Dialek nga sidiak dikenal: {code}",
    "msg.file.handle_required": "'{fn}' butuh berkas dibukuak dinga {open_fn}",
    "msg.file.io": "Kesalahan berkas {path}: {reason}",
    "msg.file.is_dir": "Inih folder, iduak berkas: {path}",
    "msg.file.mode_invalid": ("Mode harus \"{read}\", \"{write}\", atau "
                              "\"{append}\", iduak {value}"),
    "msg.file.not_utf8": "Berkas inih iduak tulisan UTF-8: {path}",
    "msg.file.path_type": "'{fn}' butuh namu berkas jadi tulisan",
    "msg.file.permission": "Sidiak ado izin ndik berkas: {path}",
    "msg.fn.contains_kind": "'{fn}' hanya ndik daftar, peta, nga tulisan",
    "msg.fn.contains_type": "Ndik meriksu daling tulisan, item harus tulisan",
    "msg.fn.join_arity": "Pungsi {fn} butuh 1 atau 2 argumen, dibaguih {count}",
    "msg.fn.length_kind": "'{fn}' hanya ndik daftar, peta, nga tulisan",
    "msg.fn.list_only": "'{fn}' hanya ndik daftar",
    "msg.fn.open_arity": "Pungsi {fn} butuh 1 atau 2 argumen, dibaguih {count}",
    "msg.fn.range_args": "Argumen {fn} harus bilangan buluak",
    "msg.fn.range_arity": "Pungsi {fn} butuh 1, 2, atau 3 argumen, dibaguih {count}",
    "msg.fn.range_step": "Langkah {fn} iduak buluih 0",
    "msg.fn.range_too_big": "Rentang lebih geduang (maksimum {max})",
    "msg.fn.reverse_kind": "'{fn}' hanya ndik daftar nga tulisan",
    "msg.fn.sort_type": ("Daftar iduak bisa diurutkan: ado nilai nga dak bisa "
                         "dibandingkan"),
    "msg.fn.split_arity": "Pungsi {fn} butuh 1 atau 2 argumen, dibaguih {count}",
    "msg.fn.split_kind": "'{fn}' hanya ndik tulisan",
    "msg.fn.wait_number": "'{fn}' butuh bilangan waktiu",
    "msg.fn.wait_range": "Waktiu nunggu {fn} harus antara 0 nga {max}",
    "msg.import.not_found": "Sidiak besuao berkas: {name}",
    "msg.import.not_text": "'{kw}' butuh namu berkas jadi tulisan",
    "msg.loop.not_iterable": "Nilai inih iduak bisa diulang dinga '{for_word}'",
    "msg.loop.use_range": ("Ndik ngulang beberapa kali, maki {range_fn}(n): "
                           "{for_word} i {in_word} {range_fn}(5)"),
    "msg.name.already_const": "'{name}' lah ditetakka jadi konstanta",
    "msg.runtime.too_deep": "Daling nia",
    "msg.runtime.unknown_expr": "Ekspresi nga sidiak dikenal: {op}",
    "msg.syntax.assign_target": ("Baris {line}: sisi kiri '=' harus namu atau "
                                 "elemen daftar"),
    "msg.syntax.expected_after_name": ("Baris {line}: diharaok '{word}' kik namu, "
                                       "basuao {text}"),
    "msg.syntax.reserved": ("Baris {line}: '{text}' adalah kata cadangan ndik "
                            "fitur mase depang"),
    "msg.value.index_kind": "Hanya daftar, peta, nga tulisan nga bisa diindeks",
    "msg.value.map_pair": "Tiap pasangan peta harus daftar [kuncai, nilai]",
    "msg.value.neg_type": "Tanda minus hanya ndik bilangan, iduak {value}",
    "msg.value.separator": "Pemisah harus tulisan",
}

EXPECTED_FALLBACKS = set()

EXPECTED_TIERS = {1: (32, 32), 2: (104, 104), 3: (1, 1)}


def check(ok, label, detail=""):
    print("PASS" if ok else "FAIL", label, "" if ok else "-> " + str(detail))
    if not ok:
        FAILED.append(label)


def capture(fn, *args, **kwargs):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        result = fn(*args, **kwargs)
    return result, out.getvalue(), err.getvalue()


def read_json():
    with open(JSON_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def read_csv():
    with open(CSV_PATH, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def catalogue_order():
    return sorted(IDS, key=lambda ident: (IDS[ident]["tier"], ident))


# ---- 1. artifacts and load ------------------------------------------------
def test_artifacts_and_load():
    for path in (CSV_PATH, JSON_PATH, MD_PATH):
        check(os.path.isfile(path), "artifact exists: %s" % os.path.basename(path),
              path)

    raw = pathlib.Path(JSON_PATH).read_bytes()
    check(not raw.startswith(b"\xef\xbb\xbf"), "the JSON has no BOM", raw[:3])
    check(raw.endswith(b"\n"), "the JSON ends with a newline", raw[-1:])
    text = raw.decode("utf-8")
    data = json.loads(text)
    check(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
          == text, "the JSON is 2-space indented and sorted")

    dialect = loader.load_dialect("koto-payang", root=DIALECTS)
    check(dialect.report.problems == [], "load_dialect reports no problems",
          dialect.report.problems)
    check(dialect.code == "koto-payang", "the code is koto-payang", dialect.code)


# ---- 2. metadata ----------------------------------------------------------
def test_metadata():
    dialect = loader.load_dialect("koto-payang", root=DIALECTS)
    data = dialect.data
    check(dialect.name == "Koto Payang", "the display name is Koto Payang",
          dialect.name)
    check(dialect.status == "approved", "the status is approved", dialect.status)
    check(dialect.core == "0.6", "core is 0.6", dialect.core)
    check(dialect.revision == 2, "revision is 2", dialect.revision)
    check(data.get("parent") is None, "parent is null", data.get("parent"))
    check(data.get("reviewer") == "Rizka Hanifa Khairany",
          "the reviewer is Rizka Hanifa Khairany", data.get("reviewer"))
    check(data.get("license") == "CC BY-SA 4.0", "the license is CC BY-SA 4.0",
          data.get("license"))
    check(data.get("maintainer") == "KerinciLang core",
          "the maintainer is KerinciLang core", data.get("maintainer"))
    check(data.get("sources") == [
        "Translation Worksheet (Koto Payang), 2026",
        "docs/08-multi-dialect-plan-review.md",
        "dialects/src/koto-payang.csv",
    ], "the sources are exact", data.get("sources"))
    check(data.get("orthography") == (
        "Koto Payang spelling: final -u (kalu, selamu, daling); nga for and; "
        "multi-word concepts use underscores (lebih_nik_dari)."),
        "the orthography note is exact", data.get("orthography"))
    check(data.get("notes") == (
        "Tier 1 and Tier 2 complete: all 137 IDs reviewed by the speaker; "
        "no English fallback."),
        "the notes are exact", data.get("notes"))
    check(len(data.get("words", {})) == 69, "the JSON has 69 words",
          len(data.get("words", {})))
    check(len(data.get("messages", {})) == 68, "the JSON has 68 messages",
          len(data.get("messages", {})))


# ---- 3. completeness ------------------------------------------------------
def test_completeness():
    dialect = loader.load_dialect("koto-payang", root=DIALECTS)
    data = dialect.data
    check(dialect.report.tiers() == EXPECTED_TIERS, "the tiers are exact",
          dialect.report.tiers())
    check(dialect.report.fallbacks == [],
          "there are no base fallbacks", dialect.report.fallbacks)
    check(dialect.base_ids == set(),
          "the base IDs are empty", dialect.base_ids)
    check(dialect.report.missing() == [],
          "missing() is empty", dialect.report.missing())
    words = EXPECTED_WORDS | TODO_WORDS
    messages = EXPECTED_MESSAGES | TODO_MESSAGES
    check(set(data["words"]) == set(words),
          "the owned words are exactly the 69 mapped IDs",
          sorted(set(data["words"]) ^ set(words)))
    check(set(data["messages"]) == set(messages),
          "the owned messages are exactly the 68 mapped IDs",
          sorted(set(data["messages"]) ^ set(messages)))
    check(not set(data["words"]) & set(data["messages"]),
          "words and messages are disjoint")
    check(all(IDS[ident]["tier"] == 1 for ident in data["words"]
              if ident.startswith(("kw.", "op."))),
          "all 32 Tier 1 IDs are owned",
          [ident for ident in IDS if IDS[ident]["tier"] == 1
           and ident not in data["words"]])


# ---- 4. word mapping ------------------------------------------------------
def test_word_mapping():
    data = read_json()
    words = dict(EXPECTED_WORDS, **TODO_WORDS)
    check(data["words"] == words, "every word equals the approved map",
          sorted(set(data["words"].items()) ^ set(words.items())))
    check(len(words) == 69, "the expected map has 69 words", len(words))
    for ident, word in sorted(TODO_WORDS.items()):
        check(data["words"].get(ident) == word, "%s is owned" % ident,
              data["words"].get(ident))
    check(data["words"].get("kw.begin") == "mulai"
          and data["words"].get("kw.end") == "selesai",
          "the block aliases are mulai and selesai",
          (data["words"].get("kw.begin"), data["words"].get("kw.end")))


# ---- 5. message mapping ---------------------------------------------------
def test_message_mapping():
    data = read_json()
    messages = dict(EXPECTED_MESSAGES, **TODO_MESSAGES)
    check(data["messages"] == messages,
          "every message equals the approved map",
          sorted(set(data["messages"].items()) ^ set(messages.items())))
    check(len(messages) == 68, "the expected map has 68 messages",
          len(messages))
    gaps = []
    for ident, template in data["messages"].items():
        used = set(PLACEHOLDER_RE.findall(template))
        if used != set(IDS[ident]["placeholders"]):
            gaps.append((ident, sorted(used), sorted(IDS[ident]["placeholders"])))
    check(gaps == [], "every placeholder set matches the catalogue", gaps)
    for ident, template in sorted(TODO_MESSAGES.items()):
        check(data["messages"].get(ident) == template, "%s is owned" % ident,
              data["messages"].get(ident))


# ---- 6. CSV contract ------------------------------------------------------
def test_csv():
    raw = pathlib.Path(CSV_PATH).read_bytes()
    check(not raw.startswith(b"\xef\xbb\xbf"), "the CSV has no BOM", raw[:3])
    check(b"\r\n" not in raw, "the CSV uses LF, not CRLF", raw[:40])
    check(raw.endswith(b"\n"), "the CSV ends with a newline", raw[-1:])

    rows = read_csv()
    check(list(rows[0].keys()) == HEADER, "the CSV header is exact",
          list(rows[0].keys()))
    check(len(rows) == 137, "the CSV has 137 rows", len(rows))
    check([row["id"] for row in rows] == catalogue_order(),
          "the rows follow the catalogue order")
    check(all(row["tier"] == str(IDS[row["id"]]["tier"])
              and row["namespace"] == IDS[row["id"]]["namespace"]
              and row["en"] == IDS[row["id"]]["en"]
              and row["id_gloss"] == IDS[row["id"]]["id_gloss"]
              for row in rows),
          "the first five columns mirror core/ids.json")

    counts = collections.Counter((row["tier"], row["status"]) for row in rows)
    check(counts == {("1", "reviewed"): 32, ("2", "reviewed"): 104,
                     ("3", "reviewed"): 1},
          "the status counts are 137 reviewed", counts)
    check(all(row["status"] == "reviewed" for row in rows),
          "every row is reviewed")

    bad_words = []
    for row in rows:
        if row["namespace"] == "msg" or not row["answer"]:
            continue
        answer = row["answer"]
        if (not re.fullmatch(r"[a-z][a-z0-9_]*", answer)
                or answer != answer.strip() or "/" in answer or "," in answer
                or " " in answer or answer.endswith("()")):
            bad_words.append((row["id"], answer))
    check(bad_words == [], "every word answer is a normalized identifier",
          bad_words)

    missing_notes = [row["id"] for row in rows
                     if row["status"] == "todo" and not row["notes"].strip()]
    check(missing_notes == [], "every todo row keeps a note", missing_notes)

    tool = os.path.join(ROOT, "tools", "lembar_kerja.py")
    result = subprocess.run(
        [sys.executable, tool, "periksa", "--kode", "koto-payang", "--siap"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    check(result.returncode == 0, "periksa --siap passes the review gate",
          (result.returncode, result.stdout, result.stderr))
    result = subprocess.run(
        [sys.executable, tool, "laporan", "--kode", "koto-payang"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    check("ready for review: yes" in result.stdout,
          "the report says ready for review", result.stdout)
    check("ready for approved: yes" in result.stdout,
          "the report says ready for approved", result.stdout)


# ---- 7. selection and fallback -------------------------------------------
BODY = """netakka_variabel x = 6
nytak x * 7
kalu x lebih_geduang_dari 5 { nytak "geduang" } nga_laen { nytak "nik" }
cubea { nytak 1 / 0 } kecuali e { nytak e }
ndik i daling [1, 2] { nytak i }
"""
EXPECTED_OUTPUT = "42\ngeduang\nPembagian dinga nol\n1\n2\n"


def test_selection_and_fallback():
    env, out, err = capture(run_source, "# dialek: koto-payang\n" + BODY,
                            dialect_root=DIALECTS)
    check(out == EXPECTED_OUTPUT, "a header runs the Koto Payang program",
          repr(out))
    check(err == "", "a clean Koto Payang run prints no warning", repr(err))
    check(type(env.vocab) is loader.DialectVocabulary,
          "the header uses the file, not a built-in vocabulary",
          type(env.vocab).__name__)
    check(env.vocab.code == "koto-payang", "the run is Koto Payang",
          env.vocab.code)

    with tempfile.TemporaryDirectory() as tmp:
        program = pathlib.Path(tmp) / "prog.krc"
        program.write_text(BODY, encoding="utf-8")
        code, out, err = capture(main, ["--dialek", "koto-payang", str(program)],
                                 dialect_root=DIALECTS)
        check(code == 0 and out == EXPECTED_OUTPUT,
              "--dialek koto-payang runs a headerless file", (code, out, err))
        check(err == "", "--dialek koto-payang is quiet", repr(err))

        code, out, err = capture(
            main, ["--ketat", "--dialek", "koto-payang", "-c", BODY],
            dialect_root=DIALECTS)
        check(code == 0 and out == EXPECTED_OUTPUT,
              "--ketat passes a complete Tier 1", (code, out, err))

    _, out, err = capture(run_source, "# dialek: koto-payang\nnytak tipe(betiu)\n",
                          dialect_root=DIALECTS)
    check(out == "betiu_salah\n", "type.bool is the dialect word", repr(out))
    check(err == "", "the complete dialect warns about no fallback", repr(err))

    code, out, err = capture(
        main, ["--ketat", "--dialek", "koto-payang", "-c", "nytak tipe(betiu)"],
        dialect_root=DIALECTS)
    check(code == 0 and out == "betiu_salah\n",
          "strict mode runs the dialect word", (code, out, err))
    check(err == "", "strict mode is quiet", repr(err))


# ---- 8. gate --------------------------------------------------------------
def run_checker(*args):
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "cek_dialek.py")] + list(args),
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return result.returncode, result.stdout, result.stderr


def test_gate():
    summary = "koto-payang: tier 1 32/32, tier 2 104/104, tier 3 1/1"
    code, out, err = run_checker("--kode", "koto-payang")
    check(code == 0, "cek_dialek --kode koto-payang exits 0", (code, out, err))
    check(summary in out, "the summary is exact", repr(out))

    code, out, err = run_checker("--kode", "koto-payang", "--ketat")
    check(code == 0, "cek_dialek --kode koto-payang --ketat exits 0",
          (code, out, err))
    check(summary in out, "strict still reports the exact summary", repr(out))

    code, out, err = run_checker("--semua")
    check(code == 0, "cek_dialek --semua exits 0", (code, out, err))
    check("koto-payang:" in out and "siulak:" in out,
          "--semua includes both committed dialects", repr(out))


def main_test():
    test_artifacts_and_load()
    test_metadata()
    test_completeness()
    test_word_mapping()
    test_message_mapping()
    test_csv()
    test_selection_and_fallback()
    test_gate()
    print("\nFAILED:" if FAILED else "\nALL PASSED", len(FAILED) or "")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main_test())
