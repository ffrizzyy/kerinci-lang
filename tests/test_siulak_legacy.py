"""Tests for the frozen Siulak 0.5 dialect.

The committed `dialects/siulak.json` must match the v0.5 tables in
`kerincilang.py` exactly, and `DialectVocabulary` must behave like
`LegacySiulak` for every word and message.

Run with: python3 tests/test_siulak_legacy.py
"""
import contextlib
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
from kerincilang import main, resolve_dialect, run_source  # noqa: E402
from dialects import loader  # noqa: E402

FAILED = []
IDS = kerincilang.CATALOG["ids"]
DIALECTS = os.path.join(ROOT, "dialects")
SIULAK_FILE = os.path.join(DIALECTS, "siulak.json")
SIULAK_MD = os.path.join(DIALECTS, "siulak.md")

EXPECTED_NAME = "Siulak (legacy 0.5)"
EXPECTED_NOTES = ("Frozen legacy vocabulary; do not edit. A completed Siulak "
                  "re-review is a separate revision.")
EXPECTED_ORTHOGRAPHY = ("Frozen Siulak v0.5 spelling. Comparison words use "
                        "underscores (lebih_daripado); lain kalu is two words; "
                        "type.bool remains the English placeholder boolean.")
EXPECTED_SOURCES = [
    "docs/02-vocabulary-worksheet.md",
    "kerincilang.py v0.5 LEGACY_WORDS and LEGACY_OPERATORS",
]
PLACEHOLDER_RE = re.compile(r"\{([a-z][a-z0-9_]*)\}")


def check(ok, label, detail=""):
    print("PASS" if ok else "FAIL", label, "" if ok else "-> " + str(detail))
    if not ok:
        FAILED.append(label)


def capture(fn, *args, **kwargs):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        result = fn(*args, **kwargs)
    return result, out.getvalue(), err.getvalue()


def read_data():
    with open(SIULAK_FILE, encoding="utf-8") as handle:
        return json.load(handle)


def expected_words():
    words = dict(kerincilang.LEGACY_WORDS)
    words.update({id: word for id, (word, _symbol)
                  in kerincilang.LEGACY_OPERATORS.items()})
    return words


def message_ids():
    return sorted(id for id in IDS if id.startswith("msg."))


# ---- 1. file and load -----------------------------------------------------
def test_file_and_load():
    check(os.path.isfile(SIULAK_FILE), "dialects/siulak.json exists", SIULAK_FILE)
    check(os.path.isfile(SIULAK_MD), "dialects/siulak.md exists", SIULAK_MD)

    raw = pathlib.Path(SIULAK_FILE).read_bytes()
    check(not raw.startswith(b"\xef\xbb\xbf"), "the file has no UTF-8 BOM", raw[:3])
    check(raw.endswith(b"\n"), "the file ends with a newline", raw[-1:])
    try:
        text = raw.decode("utf-8")
        data = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as err:
        check(False, "the file is UTF-8 JSON", err)
        return
    check(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
          == text, "the file is 2-space indented and sorted")

    dialect = loader.load_dialect("siulak", root=DIALECTS)
    check(dialect.report.problems == [], "load_dialect reports no problems",
          dialect.report.problems)
    check(dialect.code == "siulak", "the loaded code is siulak", dialect.code)
    check(dialect.name == EXPECTED_NAME, "the display name is exact", dialect.name)
    check(dialect.status == "draft", "the status is draft", dialect.status)
    check(dialect.core == "0.6", "core is 0.6", dialect.core)
    check(dialect.revision == 1, "revision is 1", dialect.revision)

    check(data.get("parent") is None, "parent is null", data.get("parent"))
    check(data.get("reviewer") is None, "reviewer is null", data.get("reviewer"))
    check(data.get("license") == "CC BY-SA 4.0", "the license is CC BY-SA 4.0",
          data.get("license"))
    check(data.get("maintainer") == "KerinciLang core",
          "the maintainer is KerinciLang core", data.get("maintainer"))
    check(data.get("sources") == EXPECTED_SOURCES, "the sources are exact",
          data.get("sources"))
    check(data.get("orthography") == EXPECTED_ORTHOGRAPHY,
          "the orthography note is exact", data.get("orthography"))
    check(data.get("notes") == EXPECTED_NOTES, "the notes are exact",
          data.get("notes"))


# ---- 2. completeness ------------------------------------------------------
def test_completeness():
    data = read_data()
    words, messages = data.get("words", {}), data.get("messages", {})
    check(len(words) == 69, "there are 69 word IDs", len(words))
    check(len(messages) == 68, "there are 68 message IDs", len(messages))
    check(set(words) & set(messages) == set(), "words and messages are disjoint",
          sorted(set(words) & set(messages)))
    check(set(words) | set(messages) == set(IDS),
          "together they cover exactly the catalogue",
          sorted((set(words) | set(messages)) ^ set(IDS)))
    check(set(words) == {id for id in IDS if not id.startswith("msg.")},
          "the word IDs are exactly the non-message IDs",
          sorted(set(words) ^ {id for id in IDS if not id.startswith("msg.")}))
    check(set(messages) == set(message_ids()),
          "the message IDs are exactly the msg.* IDs",
          sorted(set(messages) ^ set(message_ids())))

    dialect = loader.load_dialect("siulak", root=DIALECTS)
    check(dialect.report.tiers() == {1: (32, 32), 2: (104, 104), 3: (1, 1)},
          "every tier is complete", dialect.report.tiers())
    check(dialect.report.fallbacks == [], "nothing falls back",
          dialect.report.fallbacks)
    check(dialect.report.missing() == [], "nothing is missing",
          dialect.report.missing())


# ---- 3. word mapping ------------------------------------------------------
def test_word_mapping():
    data = read_data()
    words = data.get("words", {})
    expected = expected_words()
    check(words == expected, "every word matches LEGACY_WORDS and LEGACY_OPERATORS",
          sorted(set(words.items()) ^ set(expected.items())))

    groups = {"kw": 26, "op": 6, "fn": 24, "type": 9, "mode": 3, "reserved": 1}
    for namespace, count in groups.items():
        found = [id for id in words if id.split(".", 1)[0] == namespace]
        check(len(found) == count, "the %s group has %d IDs" % (namespace, count),
              len(found))

    check(words.get("type.bool") == "boolean",
          "type.bool keeps the v0.5 placeholder boolean", words.get("type.bool"))
    check(words.get("reserved.error") == "kelihu",
          "the reserved word is kelihu", words.get("reserved.error"))
    check(words.get("kw.begin") == "mulai" and words.get("kw.end") == "habih",
          "kw.begin and kw.end are unchanged",
          (words.get("kw.begin"), words.get("kw.end")))


# ---- 4. message mapping ---------------------------------------------------
def test_message_mapping():
    data = read_data()
    messages = data.get("messages", {})
    check(len(messages) == 68, "there are 68 message templates", len(messages))

    mismatched, placeholder_gaps = [], []
    for id in message_ids():
        expected = IDS[id]["id_gloss"]
        if messages.get(id) != expected:
            mismatched.append(id)
        used = set(PLACEHOLDER_RE.findall(messages.get(id, "")))
        if used != set(IDS[id]["placeholders"]):
            placeholder_gaps.append((id, sorted(used),
                                     sorted(IDS[id]["placeholders"])))
    check(mismatched == [], "every message equals its id_gloss", mismatched)
    check(placeholder_gaps == [], "every placeholder set matches the catalogue",
          placeholder_gaps)


# ---- 5. vocabulary equivalence -------------------------------------------
def test_vocabulary_equivalence():
    dialect = loader.load_dialect("siulak", root=DIALECTS)
    file_vocab, legacy = dialect.vocab, kerincilang.LEGACY
    words = expected_words()

    check(file_vocab.code == legacy.code == "siulak", "both vocabularies say siulak",
          (file_vocab.code, legacy.code))
    check(file_vocab.surface() == legacy.surface(), "surface() agrees",
          (file_vocab.surface(), legacy.surface()))
    check(file_vocab.operators() == legacy.operators(), "operators() agrees",
          (file_vocab.operators(), legacy.operators()))
    check(file_vocab.reserved() == legacy.reserved(), "reserved() agrees",
          (file_vocab.reserved(), legacy.reserved()))

    word_gaps, mode_gaps = [], []
    for id, word in sorted(words.items()):
        if file_vocab.word(id) != legacy.word(id):
            word_gaps.append((id, file_vocab.word(id), legacy.word(id)))
        if file_vocab.mode_id(word) != legacy.mode_id(word):
            mode_gaps.append((word, file_vocab.mode_id(word), legacy.mode_id(word)))
    check(word_gaps == [], "word(id) agrees for all 69 IDs", word_gaps)
    check(mode_gaps == [], "mode_id(word) agrees for all 69 words", mode_gaps)

    names = sorted(file_vocab.surface())
    check(all(file_vocab.surface()[name] == legacy.surface()[name]
              for name in names), "surface entries agree one by one", names)

    message_gaps = []
    for id in message_ids():
        args = {name: "<%s>" % name for name in IDS[id]["placeholders"]}
        got = file_vocab.message(id, args)
        want = legacy.message(id, args)
        if got != want:
            message_gaps.append((id, got, want))
    check(message_gaps == [], "message(id, args) agrees for all 68 IDs",
          message_gaps)


# ---- 6. selection ---------------------------------------------------------
BODY = """barang x = 6
nyetak x * 7
nyetak "kato"
kalu x lebih_daripado 5 { nyetak "gedang" } lain { nyetak "ketek" }
cubo { nyetak 1 / 0 } tangkap e { nyetak e }
untuk i alem [1, 2] { nyetak i }
"""
EXPECTED_OUTPUT = "42\nkato\ngedang\nPembagian dengan nol\n1\n2\n"


def test_selection():
    _, legacy_out, _ = capture(run_source, BODY)

    env, out, err = capture(run_source, "# dialek: siulak\n" + BODY,
                            dialect_root=DIALECTS)
    check(out == EXPECTED_OUTPUT, "a header runs the v0.5 program", repr(out))
    check(err == "", "a header run prints no fallback warning", repr(err))
    check(type(env.vocab) is loader.DialectVocabulary,
          "the header uses the file, not LegacySiulak", type(env.vocab).__name__)
    check(env.vocab.code == "siulak", "the header run is Siulak", env.vocab.code)
    check(out == legacy_out, "header output equals the LEGACY output",
          (out, legacy_out))

    with tempfile.TemporaryDirectory() as tmp:
        program = pathlib.Path(tmp) / "prog.krc"
        program.write_text(BODY, encoding="utf-8")
        code, out, err = capture(main, ["--dialek", "siulak", str(program)],
                                 dialect_root=DIALECTS)
        check(code == 0, "--dialek siulak exits 0", (code, err))
        check(out == EXPECTED_OUTPUT, "--dialek siulak runs the v0.5 program",
              repr(out))
        check(err == "", "--dialek siulak prints no fallback warning", repr(err))

        code, out, err = capture(main, ["--dialek", "siulak", "-c", BODY],
                                 dialect_root=DIALECTS)
        check(code == 0 and out == EXPECTED_OUTPUT,
              "--dialek siulak applies to -c", (code, out, err))
        check(err == "", "-c prints no fallback warning", repr(err))


def test_missing_file_falls_back():
    with tempfile.TemporaryDirectory() as tmp:
        context = kerincilang.RunContext(dialect_root=tmp)
        vocab = resolve_dialect("siulak", context)
        check(vocab is kerincilang.LEGACY,
              "a missing siulak.json still resolves to LEGACY", vocab)


# ---- 7. gate --------------------------------------------------------------
def run_checker(*args):
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "cek_dialek.py")] + list(args),
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return result.returncode, result.stdout, result.stderr


def test_gate():
    summary = "siulak: tier 1 32/32, tier 2 104/104, tier 3 1/1"
    code, out, err = run_checker("--kode", "siulak")
    check(code == 0, "cek_dialek --kode siulak exits 0", (code, out, err))
    check(summary in out, "the summary reports complete tiers", repr(out))

    code, out, err = run_checker("--kode", "siulak", "--ketat")
    check(code == 0, "cek_dialek --kode siulak --ketat exits 0",
          (code, out, err))
    check(summary in out, "strict still reports complete tiers", repr(out))

    code, out, err = run_checker("--semua")
    check(code == 0, "cek_dialek --semua exits 0", (code, out, err))
    check("siulak:" in out, "--semua includes siulak", repr(out))


def main_test():
    test_file_and_load()
    test_completeness()
    test_word_mapping()
    test_message_mapping()
    test_vocabulary_equivalence()
    test_selection()
    test_missing_file_falls_back()
    test_gate()
    print("\nFAILED:" if FAILED else "\nALL PASSED", len(FAILED) or "")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main_test())
