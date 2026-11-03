"""Offline tests for the contributor guide, docs truth audit, grammar, and release gate.

Run with: python3 tests/test_docs_release.py

The wheel smoke is a separate network-dependent suite: tests/test_release.py.
"""
import csv
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import kerincilang  # noqa: E402
import make_highlight  # noqa: E402
import sinkron_tutorial  # noqa: E402

FAILED = []
TEMP = tempfile.TemporaryDirectory()
BASE = pathlib.Path(TEMP.name)

COLUMNS = ("id", "tier", "namespace", "en", "id_gloss", "answer", "notes",
           "status")
READER_FILES = (
    "README.md",
    "GETTING-STARTED.md",
    "CONTRIBUTING.md",
    "docs/01-vision-and-goals.md",
    "docs/02-vocabulary-worksheet.md",
    "docs/03-syntax-design.md",
    "docs/04-implementation.md",
    "docs/05-tooling-and-docs.md",
    "docs/06-community-and-preservation.md",
    "docs/07-roadmap.md",
    "vscode-extension/README.md",
)
STALE_STRINGS = (
    "Reference dialect: Siulak",
    "the reference dialect is **Siulak**",
    "edit the value in the `KEYWORDS` table",
    "Edit the right-hand side of `KEYWORDS`",
    'TYPE_NAMES["bool"]',
    "kerincilang-0.5.0",
    "uses Siulak Kerinci words",
)


def check(ok, label, detail=""):
    print("PASS" if ok else "FAIL", label, "" if ok else "-> " + str(detail))
    if not ok:
        FAILED.append(label)


def read(path):
    return pathlib.Path(path).read_text(encoding="utf-8")


def run(cwd, *args):
    return subprocess.run([sys.executable] + list(args), cwd=str(cwd),
                          capture_output=True, text=True)


def copy_runtime(destination):
    """A checkout-shaped copy with no generated build or test output."""
    destination = pathlib.Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("kerincilang.py", "make_highlight.py"):
        shutil.copy2(os.path.join(ROOT, name), destination / name)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    for folder in ("core", "dialects", "tools"):
        shutil.copytree(os.path.join(ROOT, folder), destination / folder,
                        ignore=ignore)
    return destination


def write_answers(csv_path):
    with open(csv_path, encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    answers = {}
    for row in rows:
        if row["tier"] == "1":
            answer = "kata_" + row["id"].replace(".", "_")
            row["answer"] = answer
            row["notes"] = "synthetic walkthrough answer"
            row["status"] = "reviewed"
            answers[row["id"]] = answer
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows([{column: row.get(column, "") for column in COLUMNS}
                      for row in rows])
    pathlib.Path(csv_path).write_bytes(out.getvalue().encode("utf-8"))
    return answers


def set_review(json_path):
    data = json.loads(read(json_path))
    data["status"] = "review"
    data["sources"] = ["synthetic walkthrough source"]
    data["maintainer"] = "walkthrough"
    pathlib.Path(json_path).write_bytes(
        (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        .encode("utf-8"))


def test_guide_walkthrough():
    work = copy_runtime(BASE / "walkthrough")
    code = "dialek-baru"

    result = run(work, "tools/lembar_kerja.py", "buat", "--kode", code)
    check(result.returncode == 0,
          "guide: buat creates the worksheet", result.stdout + result.stderr)
    csv_path = work / "dialects" / "src" / (code + ".csv")
    check(csv_path.is_file(), "guide: worksheet exists at the documented path")

    result = run(work, "tools/lembar_kerja.py", "rangka", "--kode", code,
                 "--nama", "Dialek Baru")
    check(result.returncode == 0,
          "guide: rangka writes the JSON skeleton and notes",
          result.stdout + result.stderr)
    json_path = work / "dialects" / (code + ".json")
    md_path = work / "dialects" / (code + ".md")
    check(json_path.is_file() and md_path.is_file(),
          "guide: both rangka files exist")
    skeleton = json.loads(read(json_path))
    check(skeleton.get("status") == "draft" and skeleton.get("words") == {},
          "guide: rangka skeleton is an empty draft")
    check(skeleton.get("core") == kerincilang.CORE_VERSION,
          "guide: rangka uses the catalogue core version",
          skeleton.get("core"))

    answers = write_answers(csv_path)
    set_review(json_path)

    result = run(work, "tools/lembar_kerja.py", "periksa", "--kode", code,
                 "--siap")
    check(result.returncode == 0,
          "guide: periksa --siap passes for review", result.stdout + result.stderr)

    result = run(work, "tools/lembar_kerja.py", "laporan", "--kode", code)
    check(result.returncode == 0 and "ready for review: yes" in result.stdout,
          "guide: laporan reports review-ready", result.stdout + result.stderr)

    result = run(work, "tools/lembar_kerja.py", "json", "--kode", code)
    check(result.returncode == 0,
          "guide: json merges the accepted rows", result.stdout + result.stderr)
    merged = json.loads(read(json_path))
    check(len(merged.get("words", {})) == 32 and merged.get("messages") == {},
          "guide: json wrote 32 words and no messages",
          (len(merged.get("words", {})), merged.get("messages")))

    result = run(work, "tools/cek_dialek.py", "--kode", code)
    check(result.returncode == 0,
          "guide: cek_dialek accepts the review dialect",
          result.stdout + result.stderr)
    result = run(work, "tools/cek_dialek.py", "--kode", code, "--ketat")
    check(result.returncode == 0,
          "guide: cek_dialek --ketat accepts a review dialect",
          result.stdout + result.stderr)

    program = work / "halo.krc"
    program.write_bytes(("# dialek: %s\n%s \"halo\"\n"
                         % (code, answers["kw.print"])).encode("utf-8"))
    result = run(work, "kerincilang.py", "halo.krc")
    check(result.returncode == 0 and result.stdout == "halo\n",
          "guide: a headered program runs in the new dialect",
          (result.returncode, result.stdout, result.stderr))


def test_guide_references():
    guide = read(os.path.join(ROOT, "docs", "09-adding-a-dialect.md"))
    for command in ("rangka", "periksa", "laporan", "json", "cek_dialek",
                    "sinkron_tutorial.py --bangun", "make_highlight.py",
                    "build.py"):
        check(command in guide, "guide names %s" % command)

    for script in re.findall(r"python3 ((?:tools/[a-z_]+|make_highlight|build)\.py)",
                             guide):
        check(os.path.isfile(os.path.join(ROOT, script)),
              "guide command exists: %s" % script)

    paths = set(re.findall(r"`([^`\n]+)`", guide))
    for token in sorted(paths):
        if any(char in token for char in "<>{}*"):
            continue
        if token.startswith(("http://", "https://")) or " " in token:
            continue
        if not (token.endswith((".md", ".py", ".json", ".csv", ".txt"))
                or token.endswith("/")):
            continue
        # A markdown link in docs/09 is relative to the guide's own folder;
        # a code path such as `dialects/...` is relative to the repo root.
        candidates = (os.path.join(ROOT, token.rstrip("/")),
                      os.path.join(ROOT, "docs", token.rstrip("/")))
        exists = any((os.path.isdir(target) if token.endswith("/")
                      else os.path.isfile(target)) for target in candidates)
        check(exists, "guide path exists: %s" % token)


def test_docs_index_and_links():
    index = read(os.path.join(ROOT, "docs", "README.md"))
    check("08-multi-dialect-plan-review.md" in index,
          "docs index lists document 08")
    check("09-adding-a-dialect.md" in index, "docs index lists document 09")
    check("RELEASING.md" in index, "docs index links the release checklist")

    contributing = read(os.path.join(ROOT, "CONTRIBUTING.md"))
    check("docs/09-adding-a-dialect.md" in contributing,
          "CONTRIBUTING links the dialect guide")
    check("RELEASING.md" in contributing,
          "CONTRIBUTING links the release checklist")

    guide = read(os.path.join(ROOT, "docs", "09-adding-a-dialect.md"))
    for target in ("../RELEASING.md", "../dialects/koto-payang.md",
                   "../dialects/src/koto-payang.csv"):
        check(target in guide, "guide links %s" % target)


def test_stale_strings():
    for name in READER_FILES:
        text = read(os.path.join(ROOT, name))
        for stale in STALE_STRINGS:
            check(stale not in text, "%s has no stale string %r" % (name, stale))


def test_versions():
    version = "0.6.0"
    check(kerincilang.__version__ == version,
          "kerincilang.__version__ is 0.6.0", kerincilang.__version__)
    pyproject = read(os.path.join(ROOT, "pyproject.toml"))
    check(re.search(r'^version = "0\.6\.0"$', pyproject, re.M) is not None,
          "pyproject version is 0.6.0")
    extension = json.loads(read(os.path.join(ROOT, "vscode-extension",
                                             "package.json")))
    check(extension.get("version") == version,
          "VS Code extension version is 0.6.0", extension.get("version"))
    readme = read(os.path.join(ROOT, "README.md"))
    check("Version **0.6.0**" in readme, "README says Version 0.6.0")
    getting = read(os.path.join(ROOT, "GETTING-STARTED.md"))
    for text in ("KerinciLang 0.6.0", "kerincilang-0.6.0",
                 "kerincilang.kerincilang-0.6.0", "v0.6.0"):
        check(text in getting, "GETTING-STARTED mentions %s" % text)
    changelog = read(os.path.join(ROOT, "CHANGELOG.md"))
    check("## 0.6.0 (2026-11-02)" in changelog, "CHANGELOG has the 0.6.0 heading")
    check("v0.6.0" in read(os.path.join(ROOT, "RELEASING.md")),
          "RELEASING names v0.6.0")
    check("v0.6.0" in read(os.path.join(ROOT, "docs", "07-roadmap.md")),
          "roadmap names v0.6.0")

    for name in READER_FILES:
        check("0.5.0" not in read(os.path.join(ROOT, name)),
              "%s does not say 0.5.0" % name)


def test_release_notes():
    changelog = read(os.path.join(ROOT, "CHANGELOG.md"))
    check("| Siulak | `siulak` | `draft` (frozen v0.5) | 32/32 | 104/104 | 1/1 |"
          in changelog, "changelog table has Siulak counts")
    check("| Koto Payang | `koto-payang` | `review` | 32/32 | 57/104 | 0/1 |"
          in changelog, "changelog table has Koto Payang counts")
    check("Not in this release" in changelog,
          "changelog has a 'Not in this release' section")
    for name in ("Semurup", "Sungai Liuk", "Rawang"):
        check(name in changelog, "changelog names excluded dialect %s" % name)
    flat = " ".join(changelog.lower().split())
    check("no speaker-approved" in flat,
          "changelog says the excluded dialects have no approved file")


def test_grammar_freshness_and_coverage():
    committed = pathlib.Path(ROOT, "vscode-extension", "syntaxes",
                             "krc.tmLanguage.json").read_bytes()
    check(make_highlight.render().encode("utf-8") == committed,
          "committed grammar matches a fresh generation byte for byte")

    text = committed.decode("utf-8")
    grammar = json.loads(text)
    names = {pattern.get("name") for pattern in grammar.get("patterns", [])}
    for name in ("comment.line.number-sign.krc",
                 "string.quoted.double.krc",
                 "constant.numeric.krc",
                 "keyword.control.krc",
                 "keyword.operator.word.krc",
                 "support.function.builtin.krc"):
        check(name in names, "grammar has the %s rule" % name)
    check("error" not in text, "grammar does not highlight the reserved error word")
    check("boolean" not in text,
          "grammar does not highlight the type-only boolean word")

    from dialects.loader import available_dialects, load_dialect
    for code in available_dialects():
        dialect = load_dialect(code)
        missing = []
        for ident, word in sorted(dialect.words.items()):
            if ident.split(".", 1)[0] not in ("kw", "op", "fn"):
                continue
            if re.search(r"(?<![a-z0-9_])" + re.escape(word) + r"(?![a-z0-9_])",
                         text) is None:
                missing.append((ident, word))
        check(not missing, "grammar highlights every kw/op/fn word for %s" % code,
              missing)
    check("contains" in text and "wait" in text,
          "grammar includes Koto Payang's base fallback built-ins")
    check("nytak" in text and "nyetak" in text,
          "grammar is a union, not a Siulak-only list")


def test_extension_metadata():
    extension = json.loads(read(os.path.join(ROOT, "vscode-extension",
                                             "package.json")))
    description = extension.get("description", "")
    check("Siulak" in description and "Koto Payang" in description,
          "extension description names both dialects", description)
    readme = read(os.path.join(ROOT, "vscode-extension", "README.md"))
    check("union" in readme.lower(), "extension README explains the union rule")
    check("picker" in readme.lower(),
          "extension README explains the missing per-dialect picker")
    check("0.6.0" in readme, "extension README names the 0.6.0 install path")


def test_packaging_configuration():
    pyproject = read(os.path.join(ROOT, "pyproject.toml"))
    check('packages = ["core", "dialects"]' in pyproject,
          "pyproject declares the core and dialects packages")
    check('core = ["*.json"]' in pyproject, "pyproject ships core JSON")
    check('dialects = ["*.json", "*.md"]' in pyproject,
          "pyproject ships dialect JSON and notes")
    check("multi-dialect" in pyproject,
          "pyproject description is multi-dialect")
    check("csv" not in pyproject.lower(), "pyproject does not ship worksheets")

    for path in pathlib.Path(ROOT, "core").glob("*.json"):
        check(path.is_file(), "core data file exists: %s" % path.name)
    for path in pathlib.Path(ROOT, "dialects").glob("*.json"):
        check(path.is_file(), "dialect JSON exists: %s" % path.name)
    for path in pathlib.Path(ROOT, "dialects").glob("*.md"):
        check(path.is_file(), "dialect notes exist: %s" % path.name)


def test_releasing_document():
    text = read(os.path.join(ROOT, "RELEASING.md"))
    for needle in ("0.6.0", "build.py", "cek_dialek.py --semua",
                   "test_release.py", "pip wheel", "git tag"):
        check(needle in text, "RELEASING names %s" % needle)
    check("Semurup" in text and "Sungai Liuk" in text and "Rawang" in text,
          "RELEASING records the excluded dialects")


def test_no_collateral_change():
    total = 0
    problems = []
    for path in sinkron_tutorial.baseline_paths():
        found, count = sinkron_tutorial.process(path, write=False)
        problems += found
        total += count
    check(not problems, "baseline tutorial still has no problems", problems[:3])
    check(total == 550, "baseline tutorial still has 550 blocks", total)

    tutorial_test = read(os.path.join(ROOT, "tests", "test_tutorial.py"))
    check("baseline_paths" in tutorial_test,
          "test_tutorial.py still uses baseline_paths()")
    check("koto-payang" not in tutorial_test,
          "test_tutorial.py does not scan generated dialect trees")

    data = json.loads(read(os.path.join(ROOT, "dialects",
                                       "koto-payang.json")))
    check(data.get("status") == "review", "Koto Payang is still review",
          data.get("status"))
    check(kerincilang.__version__ == "0.6.0" and "0.5.0" not in read(
        os.path.join(ROOT, "README.md")), "no 0.5.0 regression in the README")


def main():
    tests = [
        test_guide_walkthrough,
        test_guide_references,
        test_docs_index_and_links,
        test_stale_strings,
        test_versions,
        test_release_notes,
        test_grammar_freshness_and_coverage,
        test_extension_metadata,
        test_packaging_configuration,
        test_releasing_document,
        test_no_collateral_change,
    ]
    for test in tests:
        test()
    print()
    if FAILED:
        print("%d FAILED: %s" % (len(FAILED), ", ".join(FAILED)))
        return 1
    print("all docs-release tests passed")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        TEMP.cleanup()
