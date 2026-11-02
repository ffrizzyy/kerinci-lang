"""Tests for the dialect-templated tutorial build.

Run with: python3 tests/test_tutorial_dialects.py
"""
import contextlib
import io
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
import sinkron_tutorial  # noqa: E402
from kerincilang import LangError  # noqa: E402
from dialects.loader import load_dialect  # noqa: E402

FAILED = []
TOOL = os.path.join(ROOT, "tools", "sinkron_tutorial.py")
CODE_LANGS = ("krc", "krc-error")
FENCE_LANGS = ("krc", "krc-error", "krc-berkas")
BASE_SURFACES = ("contains", "list", "map", "wait", "error", "boolean")
HEADER = "# dialek: koto-payang"
LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(\s+\"[^\"]*\")?\)")


def check(ok, label, detail=""):
    print("PASS" if ok else "FAIL", label, "" if ok else "-> " + str(detail))
    if not ok:
        FAILED.append(label)


def read_text(path):
    with open(path, encoding="utf-8", newline="") as handle:
        return handle.read()


def read_bytes(path):
    return pathlib.Path(path).read_bytes()


def write_bytes(path, text):
    pathlib.Path(path).write_bytes(text.encode("utf-8"))


def tempdir():
    return tempfile.TemporaryDirectory(dir=os.path.dirname(ROOT))


def baseline_paths():
    return sinkron_tutorial.baseline_paths()


def tree_files(root):
    root = pathlib.Path(root)
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(root.rglob("*")) if p.is_file()}


def copy_baseline(repo):
    """Copy the canonical lessons and the files they link to into a temp repo."""
    repo = pathlib.Path(repo)
    tutorial = repo / "tutorial"
    tutorial.mkdir(parents=True, exist_ok=True)
    for path in sorted((pathlib.Path(ROOT) / "tutorial").glob("*.md")):
        shutil.copy2(path, tutorial / path.name)
    (tutorial / "id").mkdir()
    for path in sorted((pathlib.Path(ROOT) / "tutorial" / "id").glob("*.md")):
        shutil.copy2(path, tutorial / "id" / path.name)
    (tutorial / "kerinci").mkdir()
    shutil.copy2(pathlib.Path(ROOT) / "tutorial" / "kerinci" / "README.md",
                 tutorial / "kerinci" / "README.md")
    shutil.copy2(pathlib.Path(ROOT) / "CONTRIBUTING.md", repo / "CONTRIBUTING.md")
    return repo


def build_repo(base, name="repo"):
    repo = copy_baseline(pathlib.Path(base) / name)
    result = sinkron_tutorial.build("koto-payang", out_root=repo / "tutorial",
                                    source_root=repo / "tutorial")
    return repo, result


def capture_main(argv):
    old = sys.argv
    sys.argv = ["sinkron_tutorial.py"] + list(argv)
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = sinkron_tutorial.main()
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
    finally:
        sys.argv = old
    return code, out.getvalue(), err.getvalue()


def run_tool(args):
    return subprocess.run([sys.executable, TOOL] + list(args), cwd=ROOT,
                          capture_output=True, text=True, encoding="utf-8")


def generated_dir(axis):
    return pathlib.Path(ROOT) / "tutorial" / axis / "koto-payang"


def baseline_dir(axis):
    return (pathlib.Path(ROOT) / "tutorial" if axis == "en"
            else pathlib.Path(ROOT) / "tutorial" / "id")


def generated_files():
    return (sorted(generated_dir("en").glob("*.md"))
            + sorted(generated_dir("id").glob("*.md")))


# ---- 1. determinism -------------------------------------------------------
def test_determinism():
    with tempdir() as tmp:
        repo_a, _ = build_repo(tmp, "a")
        repo_b, _ = build_repo(tmp, "b")
        a, b = {}, {}
        for axis in ("en", "id"):
            a.update({axis + "/" + k: v for k, v in
                      tree_files(repo_a / "tutorial" / axis / "koto-payang").items()})
            b.update({axis + "/" + k: v for k, v in
                      tree_files(repo_b / "tutorial" / axis / "koto-payang").items()})
        check(bool(a) and a == b,
              "determinism: two builds are byte-identical",
              sorted(set(a) ^ set(b)) or "bytes differ")


# ---- 2. the committed tree matches a fresh build -------------------------
def test_committed_tree():
    with tempdir() as tmp:
        repo, _ = build_repo(tmp)
        for axis in ("en", "id"):
            committed = generated_dir(axis)
            fresh = repo / "tutorial" / axis / "koto-payang"
            left, right = tree_files(committed), tree_files(fresh)
            differing = [name for name in sorted(set(left) & set(right))
                         if left[name] != right[name]]
            check(left and left == right,
                  "committed %s tree matches a fresh build" % axis,
                  {"only committed": sorted(set(left) - set(right)),
                   "only fresh": sorted(set(right) - set(left)),
                   "differing": differing[:5]})


# ---- 3. baseline untouched ------------------------------------------------
def test_baseline_untouched():
    problems = []
    for path in baseline_paths():
        text = read_text(path)
        if "Generated from the Siulak lesson" in text:
            problems.append("%s has a generated footer" % path.name)
        if "Dibuat dari pelajaran Siulak" in text:
            problems.append("%s has a generated footer" % path.name)
        if "> **Generated tutorial:**" in text:
            problems.append("%s has a generated banner" % path.name)
        if "> **Tutorial hasil bangun:**" in text:
            problems.append("%s has a generated banner" % path.name)
        for block in sinkron_tutorial.parse_blocks(text.split("\n")):
            if block["lang"] in FENCE_LANGS:
                first = block["code"].split("\n", 1)[0]
                if first.startswith("# dialek:"):
                    problems.append("%s:%d has a header"
                                    % (path.name, block["start"] + 1))
    check(not problems, "baseline files have no header, banner, or footer",
          problems[:5])

    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tests", "test_tutorial.py")],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    text = result.stdout + result.stderr
    check(result.returncode == 0
          and "550 blocks checked, 0 problems" in text,
          "tests/test_tutorial.py still checks exactly 550 baseline blocks",
          (result.returncode, text[-500:]))


# ---- 4. building Siulak reproduces the baseline blocks --------------------
def test_siulak_self_build():
    with tempdir() as tmp:
        repo = copy_baseline(pathlib.Path(tmp) / "repo")
        out = pathlib.Path(tmp) / "out"
        sinkron_tutorial.build("siulak", out_root=out,
                               source_root=repo / "tutorial")
        problems, checked = [], 0
        for axis in ("en", "id"):
            source_dir = repo / "tutorial" if axis == "en" else repo / "tutorial" / "id"
            for source in sorted(source_dir.glob("*.md")):
                if source.name in ("glossary.md", "glosarium.md"):
                    continue
                generated = out / axis / "siulak" / source.name
                old = sinkron_tutorial.parse_blocks(
                    read_text(source).split("\n"))
                new = sinkron_tutorial.parse_blocks(
                    read_text(generated).split("\n"))
                if len(old) != len(new):
                    problems.append("%s: block count %d != %d"
                                    % (source.name, len(old), len(new)))
                    continue
                for before, after in zip(old, new):
                    if (before["lang"], before["info"]) != (after["lang"], after["info"]):
                        problems.append("%s:%d: block kind or info changed"
                                        % (source.name, before["start"] + 1))
                        continue
                    if before["lang"] not in FENCE_LANGS:
                        continue
                    checked += 1
                    lines = after["code"].split("\n")
                    body = "\n".join(lines[1:]) if lines and lines[0] == "# dialek: siulak" else after["code"]
                    if body.replace("\r", "") != before["code"].replace("\r", ""):
                        problems.append("%s:%d: code changed"
                                        % (source.name, before["start"] + 1))
        check(not problems and checked > 0,
              "Siulak self-build keeps every block's kind, info, and code",
              {"checked": checked, "problems": problems[:5]})


# ---- 5. every generated block really runs --------------------------------
def test_generated_blocks_run():
    problems, total = [], 0
    for path in generated_files():
        with contextlib.redirect_stderr(io.StringIO()):
            found, count = sinkron_tutorial.process(path, write=False)
        problems += found
        total += count
    check(not problems and total == 550,
          "every generated block runs and every hasil matches",
          {"blocks": total, "problems": problems[:5]})


# ---- 6. helper files get the target header, raw data does not ------------
def test_helper_files():
    problems, helpers = [], 0
    for path in generated_files():
        for block in sinkron_tutorial.parse_blocks(read_text(path).split("\n")):
            if block["lang"] != "krc-berkas":
                continue
            helpers += 1
            first = block["code"].split("\n", 1)[0]
            if block["info"].endswith(".krc"):
                if first != HEADER:
                    problems.append("%s: %s lacks the header"
                                    % (path.name, block["info"]))
            elif first.startswith("# dialek:"):
                problems.append("%s: raw data %s gained a header"
                                % (path.name, block["info"]))
    for axis, lesson in (("en", "13-project.md"), ("id", "13-proyek.md")):
        text = read_text(generated_dir(axis) / lesson)
        blocks = sinkron_tutorial.parse_blocks(text.split("\n"))
        names = {block["info"] for block in blocks
                 if block["lang"] == "krc-berkas"}
        if not {"buku_nilai.krc", "nilai.txt"} <= names:
            problems.append("%s: helper names changed: %s" % (lesson, names))
        if 'impor "buku_nilai"' not in text:
            problems.append("%s: the helper is not imported" % lesson)
    check(not problems and helpers >= 4,
          "helpers import successfully; .krc gets a header, raw data does not",
          {"helpers": helpers, "problems": problems[:5]})


# ---- 7. normalized equivalence with the Siulak baseline ------------------
NEUTRAL = None


def neutral_maps():
    global NEUTRAL
    if NEUTRAL is not None:
        return NEUTRAL
    ids = [id for id in kerincilang.CATALOG["ids"] if not id.startswith("msg.")]
    vocabs = [load_dialect("siulak").vocab, load_dialect("koto-payang").vocab]
    literals = []
    for vocab in vocabs:
        for id in ("kw.true", "kw.false", "kw.null"):
            literals.append((vocab.word(id), "<" + id + ">"))
        for id in ids:
            if id.startswith("type."):
                literals.append((vocab.word(id), "<" + id + ">"))
    literals.sort(key=lambda pair: -len(pair[0]))

    templates = []
    for vocab in vocabs:
        for id, entry in kerincilang.CATALOG["ids"].items():
            if not id.startswith("msg."):
                continue
            holes = {name: "\x00" for name in entry.get("placeholders", [])}
            try:
                text = vocab.message(id, holes)
            except (KeyError, IndexError, ValueError):
                continue
            parts = re.split("\x00", text)
            templates.append((re.compile(".+?".join(re.escape(p) for p in parts),
                                         re.S), "<" + id + ">"))
    templates.sort(key=lambda pair: -len(pair[0].pattern))

    code_words = {}
    for id in ids:
        if id.startswith(("kw.", "op.", "fn.", "reserved.")):
            for vocab in vocabs:
                code_words.setdefault(vocab.word(id), "<" + id + ">")
    NEUTRAL = (literals, templates, code_words)
    return NEUTRAL


def normalize(text):
    literals, templates, _code_words = neutral_maps()
    for pattern, replacement in templates:
        text = pattern.sub(replacement, text)
    for word, replacement in literals:
        text = re.sub(r"(?<!\w)" + re.escape(word) + r"(?!\w)", replacement, text)
    return text


def normalize_arg(value):
    _literals, _templates, code_words = neutral_maps()
    text = str(value)
    text = re.sub(r"[A-Za-z_][A-Za-z0-9_]*",
                  lambda m: code_words.get(m.group(0), m.group(0)), text)
    return normalize(text)


def error_signature(error):
    if error is None:
        return None
    if not isinstance(error, LangError):
        return ("harness", str(error))
    args = tuple(sorted((key, normalize_arg(value))
                        for key, value in (error.msg_args or {}).items()))
    return (error.msg_id, args)


def run_source(code, info, files):
    typed = ""
    match = re.search(r"masukan=(.*)$", info)
    if match:
        typed = "\n".join(match.group(1).split("|")) + "\n"
    code = code.replace("\r\n", "\n").replace("\r", "")
    with tempfile.TemporaryDirectory() as tmp:
        for name, content in files.items():
            content = content.replace("\r\n", "\n").replace("\r", "")
            pathlib.Path(tmp, name).write_text(content, encoding="utf-8")
        pathlib.Path(tmp, "program.krc").write_text(code + "\n", encoding="utf-8")
        old_cwd, old_stdin = os.getcwd(), sys.stdin
        os.chdir(tmp)
        sys.stdin = sinkron_tutorial.LimitedInput(typed)
        out, error = io.StringIO(), None
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                kerincilang.run_file("program.krc")
        except LangError as err:
            error = err
        except Exception as err:                    # a harness failure, not a language error
            error = err
        finally:
            kerincilang.close_all_files()
            os.chdir(old_cwd)
            sys.stdin = old_stdin
    return out.getvalue(), error


def test_normalized_equivalence():
    problems, checked = [], 0
    for axis in ("en", "id"):
        for source in sorted(baseline_dir(axis).glob("*.md")):
            if source.name in ("glossary.md", "glosarium.md"):
                continue
            generated = generated_dir(axis) / source.name
            old = sinkron_tutorial.parse_blocks(read_text(source).split("\n"))
            new = sinkron_tutorial.parse_blocks(read_text(generated).split("\n"))
            if len(old) != len(new):
                problems.append("%s: block count changed" % source.name)
                continue
            old_files, new_files = {}, {}
            for before, after in zip(old, new):
                if before["lang"] == "krc-berkas":
                    old_files[before["info"]] = before["code"] + "\n"
                    new_files[after["info"]] = after["code"] + "\n"
                    continue
                if before["lang"] not in CODE_LANGS:
                    continue
                checked += 1
                old_out, old_err = run_source("# dialek: siulak\n" + before["code"],
                                              before["info"], dict(old_files))
                new_out, new_err = run_source(after["code"], after["info"],
                                              dict(new_files))
                if (normalize(old_out) != normalize(new_out)
                        or error_signature(old_err) != error_signature(new_err)):
                    problems.append(
                        "%s:%d: output or error identity changed"
                        % (source.name, before["start"] + 1))
    check(not problems and checked == 268,
          "normalized output and error identity match the baseline",
          {"blocks": checked, "problems": problems[:5]})


# ---- 8. fallbacks are honest and limited ---------------------------------
def test_fallbacks():
    with tempdir() as tmp:
        _repo, result = build_repo(tmp)
        fallbacks = result["fallbacks"]
        check(set(fallbacks) == {"fn.contains", "type.bool"},
              "the build reports exactly the two expected fallbacks",
              sorted(fallbacks))

        for axis in ("en", "id"):
            index = read_text(generated_dir(axis) / "README.md")
            missing = [name for name in ("fn.contains", "contains",
                                         "type.bool", "boolean") if name not in index]
            check(not missing,
                  "the %s index lists the fallback IDs and words" % axis,
                  missing)

        found_code, found_output = set(), set()
        for path in generated_files():
            for block in sinkron_tutorial.parse_blocks(read_text(path).split("\n")):
                if block["lang"] in FENCE_LANGS:
                    for word in BASE_SURFACES:
                        if re.search(r"(?<![A-Za-z0-9_])" + word
                                     + r"(?![A-Za-z0-9_])", block["code"]):
                            found_code.add(word)
                elif block["lang"] == "hasil":
                    for word in BASE_SURFACES:
                        if re.search(r"(?<![A-Za-z0-9_])" + word
                                     + r"(?![A-Za-z0-9_])", block["code"]):
                            found_output.add(word)
        check(found_code == {"contains"},
              "only the allowed base word appears in generated code",
              sorted(found_code))
        check("boolean" in found_output,
              "the allowed type fallback appears in generated output",
              sorted(found_output))

        out = pathlib.Path(tmp) / "warn"
        code, _stdout, stderr = capture_main(
            ["--bangun", "koto-payang", "--keluaran", str(out)])
        warnings = [line for line in stderr.splitlines()
                    if line.startswith("warning:")]
        check(code == 0 and len(warnings) == 2
              and any("fn.contains" in line for line in warnings)
              and any("type.bool" in line for line in warnings),
              "stderr warns once for each fallback ID",
              (code, warnings))


# ---- 9. every generated code fence is headered ---------------------------
def test_headers():
    problems, headered = [], 0
    for path in generated_files():
        for block in sinkron_tutorial.parse_blocks(read_text(path).split("\n")):
            if block["lang"] not in FENCE_LANGS:
                continue
            first = block["code"].split("\n", 1)[0] if block["code"] else ""
            if block["lang"] == "krc-berkas" and not block["info"].endswith(".krc"):
                continue
            headered += 1
            if first != HEADER:
                problems.append("%s:%d: %s"
                                % (path.name, block["start"] + 1, first[:40]))
    for path in baseline_paths():
        for block in sinkron_tutorial.parse_blocks(read_text(path).split("\n")):
            if block["lang"] in FENCE_LANGS:
                first = block["code"].split("\n", 1)[0]
                if first.startswith("# dialek:"):
                    problems.append("%s:%d: baseline gained a header"
                                    % (path.name, block["start"] + 1))
    check(not problems and headered > 0,
          "every generated code fence carries exactly one dialect header",
          {"headered": headered, "problems": problems[:5]})


# ---- 10. links, index, and glossary stubs --------------------------------
def anchors(text):
    found, fenced = set(), False
    for line in text.split("\n"):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            slug = match.group(2).strip().lower()
            slug = re.sub(r"[^\w\s-]", "", slug)
            slug = re.sub(r"\s+", "-", slug)
            found.add(slug)
    return found


def test_links_and_index():
    problems = []
    for path in generated_files() + [generated_dir("en") / "glossary.md",
                                     generated_dir("id") / "glosarium.md"]:
        text = read_text(path)
        for match in LINK.finditer(text):
            target = match.group(2)
            if target.startswith("#") or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
                continue
            name, _sep, fragment = target.partition("#")
            resolved = (path.parent / name).resolve()
            if not resolved.exists():
                problems.append("%s: dead link %s" % (path.name, target))
            elif fragment:
                if fragment not in anchors(read_text(resolved)):
                    problems.append("%s: dead fragment %s" % (path.name, target))

    for axis, lesson_names in (
            ("en", [p.name for p in sorted(baseline_dir("en").glob("*.md"))
                    if p.name.startswith(tuple("0123456789"))]),
            ("id", [p.name for p in sorted(baseline_dir("id").glob("*.md"))
                    if p.name.startswith(tuple("0123456789"))])):
        index = read_text(generated_dir(axis) / "README.md")
        missing = [name for name in lesson_names if "(" + name + ")" not in index]
        if missing:
            problems.append("%s README misses %s" % (axis, missing))

    en_readme = read_text(generated_dir("en") / "README.md")
    id_readme = read_text(generated_dir("id") / "README.md")
    if "](../../id/koto-payang/README.md)" not in en_readme:
        problems.append("the English index does not link the Indonesian tree")
    if "](../../en/koto-payang/README.md)" not in id_readme:
        problems.append("the Indonesian index does not link the English tree")

    en_stub = read_text(generated_dir("en") / "glossary.md")
    id_stub = read_text(generated_dir("id") / "glosarium.md")
    if "## Error messages" not in en_stub:
        problems.append("the English glossary stub has no error-messages anchor")
    if "## Kesalahan" not in id_stub:
        problems.append("the Indonesian glossary stub has no kesalahan anchor")
    if "](../../glossary.md#error-messages)" not in en_stub:
        problems.append("the English glossary stub does not link the Siulak glossary")
    if "](../../id/glosarium.md)" not in id_stub:
        problems.append("the Indonesian glossary stub does not link the Siulak glossary")

    check(not problems, "every link, index lesson, and glossary stub resolves",
          problems[:8])


# ---- 11. prose fidelity ---------------------------------------------------
def prose(path, generated):
    lines = read_text(path).replace("\r\n", "\n").replace("\r", "\n").split("\n")
    blocks = sinkron_tutorial.parse_blocks(lines)
    kept, position = [], 0
    for block in blocks:
        kept.extend(lines[position:block["start"]])
        position = block["end"] + 1
    kept.extend(lines[position:])

    if generated:
        kept = [line for line in kept
                if not line.startswith("> **Generated tutorial:**")
                and not line.startswith("> **Tutorial hasil bangun:**")]
        for index, line in enumerate(kept):
            if line in ("## Base words used (review)",
                        "## Kata dasar yang dipakai (review)"):
                kept = kept[:index]
                break
        for index in range(len(kept) - 1, -1, -1):
            if (kept[index] == "---" and index + 1 < len(kept)
                    and (kept[index + 1].startswith("*Generated from")
                         or kept[index + 1].startswith("*Dibuat dari"))):
                kept = kept[:index]
                break

    result = []
    for line in kept:
        line = re.sub(r"\]\([^)]*\)", "]()", line)
        line = re.sub(r"`[^`\n]*`", "<code>", line)
        line = line.replace("Koto Payang", "Siulak")
        if line == "" and result and result[-1] == "":
            continue
        result.append(line)
    while result and result[0] == "":
        result.pop(0)
    while result and result[-1] == "":
        result.pop()
    return result


def test_prose_fidelity():
    problems = []
    for axis in ("en", "id"):
        for source in sorted(baseline_dir(axis).glob("*.md")):
            if source.name in ("glossary.md", "glosarium.md"):
                continue
            generated = generated_dir(axis) / source.name
            before, after = prose(source, False), prose(generated, True)
            if before != after:
                for index, (left, right) in enumerate(zip(before, after)):
                    if left != right:
                        problems.append("%s:%d: %r != %r"
                                        % (source.name, index + 1, left, right))
                        break
                else:
                    problems.append("%s: prose length changed" % source.name)
    check(not problems, "generated prose equals the baseline prose",
          problems[:8])


# ---- 12. usage errors and --semua-dialek ---------------------------------
def test_usage_errors():
    problems = []
    with tempdir() as tmp:
        for label, args in (
                ("unknown dialect", ["--bangun", "nope", "--keluaran", str(tmp)]),
                ("--tulis with a build", ["--tulis", "--bangun", "koto-payang"]),
                ("--prosa without a build", ["--prosa", "en"]),
                ("--bangun without a value", ["--bangun"])):
            result = run_tool(args)
            if result.returncode != 2:
                problems.append("%s: exit %s" % (label, result.returncode))
            if (pathlib.Path(tmp) / "en").exists() or (pathlib.Path(tmp) / "id").exists():
                problems.append("%s: wrote output" % label)
                shutil.rmtree(pathlib.Path(tmp) / "en", ignore_errors=True)
                shutil.rmtree(pathlib.Path(tmp) / "id", ignore_errors=True)

        all_out = pathlib.Path(tmp) / "all"
        result = run_tool(["--semua-dialek", "--keluaran", str(all_out)])
        if result.returncode != 0:
            problems.append("--semua-dialek: exit %s (%s)"
                            % (result.returncode, result.stderr[-300:]))
        for axis in ("en", "id"):
            found = sorted(p.name for p in (all_out / axis).iterdir()
                           if p.is_dir()) if (all_out / axis).exists() else []
            if found != ["koto-payang"]:
                problems.append("--semua-dialek %s built %s" % (axis, found))
    check(not problems, "bad usage exits 2 and --semua-dialek builds only Koto Payang",
          problems[:8])


# ---- 13. a failed build leaves the destination alone ---------------------
def make_full_repo(base):
    repo = pathlib.Path(base) / "repo"
    repo.mkdir()
    shutil.copy2(os.path.join(ROOT, "kerincilang.py"), repo / "kerincilang.py")
    shutil.copytree(os.path.join(ROOT, "core"), repo / "core",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(os.path.join(ROOT, "dialects"), repo / "dialects",
                    ignore=shutil.ignore_patterns("__pycache__"))
    (repo / "tools").mkdir()
    shutil.copy2(TOOL, repo / "tools" / "sinkron_tutorial.py")
    copy_baseline(repo)
    return repo


def test_failed_build_is_transactional():
    with tempdir() as tmp:
        repo = make_full_repo(tmp)
        lesson = repo / "tutorial" / "01-hello-world.md"
        lines = read_text(lesson).split("\n")
        blocks = sinkron_tutorial.parse_blocks(lines)
        block = next(block for block in blocks if block["lang"] == "krc")
        lines[block["start"] + 1:block["end"]] = ['ngangkat "boom"']
        write_bytes(lesson, "\n".join(lines))

        out = pathlib.Path(tmp) / "out"
        keep = out / "en" / "koto-payang" / "keep.txt"
        keep.parent.mkdir(parents=True)
        keep.write_bytes(b"keep\n")

        result = subprocess.run(
            [sys.executable, str(repo / "tools" / "sinkron_tutorial.py"),
             "--bangun", "koto-payang", "--keluaran", str(out)],
            cwd=str(repo), capture_output=True, text=True, encoding="utf-8")
        check(result.returncode == 1
              and keep.exists() and read_bytes(keep) == b"keep\n"
              and tree_files(out) == {"en/koto-payang/keep.txt": b"keep\n"},
              "a broken lesson exits 1 and leaves the destination unchanged",
              (result.returncode, tree_files(out), result.stderr[-300:]))


def main_test():
    test_determinism()
    test_committed_tree()
    test_baseline_untouched()
    test_siulak_self_build()
    test_generated_blocks_run()
    test_helper_files()
    test_normalized_equivalence()
    test_fallbacks()
    test_headers()
    test_links_and_index()
    test_prose_fidelity()
    test_usage_errors()
    test_failed_build_is_transactional()
    print("\nFAILED:" if FAILED else "\nALL PASSED", len(FAILED) or "")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main_test())
