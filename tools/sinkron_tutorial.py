"""Checks, refreshes, or builds the tutorial code samples.

  python3 tools/sinkron_tutorial.py                   check the baseline (exit 1 on any problem)
  python3 tools/sinkron_tutorial.py --tulis           rewrite the baseline ```hasil blocks
  python3 tools/sinkron_tutorial.py --bangun KODE     build tutorial/{en,id}/KODE/
  python3 tools/sinkron_tutorial.py --semua-dialek    build every review/approved dialect

Block kinds, written as the language of a fenced block:
  krc                 a program. It must run without error.
  krc masukan=a|b     the same, with the lines a and b typed in for tanyo()
  krc-error           a program that must fail (the message goes in the hasil block)
  krc-berkas NAME     a helper file (not run); later blocks in the lesson can use it.
                      A helper ending in .krc is code and gets a dialect header; any
                      other helper is raw data and keeps its bytes unchanged.
  hasil               the expected output of the block just above it
Any other language (bash, text, ...) is copied byte for byte.
"""
import argparse
import contextlib
import io
import os
import pathlib
import re
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import kerincilang  # noqa: E402
from kerincilang import LangError  # noqa: E402

FENCE = re.compile(r"^```(\S+)\s*(.*)$")
SPAN = re.compile(r"(?<!`)`(?!`)([^`\n]+?)(?<!`)`(?!`)")
LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(\s+\"[^\"]*\")?\)")

CODE_PREFIXES = ("kw.", "op.", "fn.", "reserved.")
TYPE_PREFIXES = ("type.",)
INLINE_PREFIXES = ("kw.", "reserved.", "op.", "fn.", "type.")
ALLOWED_FALLBACKS = {"fn.contains", "type.bool"}

GLOSSARY_NAMES = {"en": "glossary.md", "id": "glosarium.md"}

FOOTER = {
    "en": ("\n---\n*Generated from the Siulak lesson. Code and inline code "
           "use {name}\n(status: {status}).*\n"),
    "id": ("\n---\n*Dibuat dari pelajaran Siulak. Kode dan kode sebaris "
           "memakai {name}\n(status: {status}).*\n"),
}
BANNER = {
    "en": ("> **Generated tutorial:** the code and inline code below use "
           "{name} (status: {status}). The prose is the English Siulak lesson."),
    "id": ("> **Tutorial hasil bangun:** kode dan kode sebaris di bawah "
           "memakai {name} (status: {status}). Teksnya berasal dari pelajaran "
           "bahasa Indonesia dialek Siulak."),
}
FALLBACK_HEADING = {
    "en": "## Base words used (review)",
    "id": "## Kata dasar yang dipakai (review)",
}
FALLBACK_NOTE = {
    "en": ("{name} does not own these words yet, so the generated examples use "
           "the neutral English base word. They will change when the dialect "
           "is approved.\n\n| ID | Word | Meaning |\n|---|---|---|"),
    "id": ("{name} belum memiliki kata untuk hal berikut, jadi contoh yang "
           "dibangun memakai kata dasar Inggris. Kata ini akan berubah setelah "
           "dialek disetujui.\n\n| ID | Kata | Arti |\n|---|---|---|"),
}


class BuildError(Exception):
    """A tutorial build that cannot be written."""


class LimitedInput(io.StringIO):
    """Typed-in lines. If a program keeps asking after they run out, stop it."""
    extra_reads = 0

    def readline(self, *args):
        line = super().readline(*args)
        if line == "":
            self.extra_reads += 1
            if self.extra_reads > 20:
                raise RuntimeError("the program keeps asking for input after the typed input ran out")
        return line


def baseline_paths(root=None):
    """The canonical English and Indonesian lesson files, never generated trees."""
    base = pathlib.Path(root) if root is not None else ROOT / "tutorial"
    return sorted(base.glob("*.md")) + sorted((base / "id").glob("*.md"))


def parse_blocks(lines):
    blocks, i = [], 0
    while i < len(lines):
        m = FENCE.match(lines[i])
        if m:
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            blocks.append({"lang": m.group(1), "info": m.group(2).strip(),
                           "start": i, "end": j,
                           "code": "\n".join(lines[i + 1:j]),
                           "closed": j < len(lines)})
            i = j + 1
        else:
            i += 1
    return blocks


def ensure_header(code, code_name):
    """Put exactly one line-1 header on a code block."""
    lines = code.split("\n")
    if lines and kerincilang.HEADER_HINT_RE.match(lines[0]):
        if not kerincilang.HEADER_RE.match(lines[0]):
            raise BuildError("line 1 is a malformed dialect header")
        lines[0] = "# dialek: %s" % code_name
        return "\n".join(lines)
    return "# dialek: %s\n%s" % (code_name, code)


def run_block(code, info, files, quiet=False):
    typed = ""
    m = re.search(r"masukan=(.*)$", info)
    if m:
        typed = "\n".join(m.group(1).split("|")) + "\n"
    with tempfile.TemporaryDirectory() as tmp:
        for name, content in files.items():
            pathlib.Path(tmp, name).write_text(content, encoding="utf-8")
        pathlib.Path(tmp, "program.krc").write_text(code + "\n", encoding="utf-8")
        old_cwd, old_stdin = os.getcwd(), sys.stdin
        os.chdir(tmp)
        sys.stdin = LimitedInput(typed)
        out, error = io.StringIO(), None
        devnull = io.StringIO() if quiet else None
        try:
            if quiet:
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(devnull):
                    kerincilang.run_file("program.krc")
            else:
                with contextlib.redirect_stdout(out):
                    kerincilang.run_file("program.krc")
        except LangError as err:
            error = str(err)
        except RuntimeError as err:
            error = f"(test harness) {err}"
        finally:
            kerincilang.close_all_files()
            os.chdir(old_cwd)
            sys.stdin = old_stdin
    return out.getvalue(), error


def process(path, write):
    lines = path.read_text(encoding="utf-8").split("\n")
    blocks = parse_blocks(lines)
    files, problems, edits = {}, [], []
    for idx, b in enumerate(blocks):
        where = f"{path.name}:{b['start'] + 1}"
        if not b["closed"]:
            problems.append(f"{where}: the fence is not closed")
            continue
        if b["lang"] == "krc-berkas":
            if b["info"].endswith(".krc"):
                files[b["info"]] = b["code"] + "\n"
            else:
                files[b["info"]] = b["code"] + "\n"
            continue
        if b["lang"] not in ("krc", "krc-error"):
            continue
        out, error = run_block(b["code"], b["info"], files)
        if b["lang"] == "krc" and error:
            problems.append(f"{where}: unexpected error: {error}")
        if b["lang"] == "krc-error" and not error:
            problems.append(f"{where}: this program should fail but it succeeded")
        actual = (out + (f"Kesalahan: {error}\n" if error else "")).rstrip("\n")
        actual = re.sub(r"\(lebih dari \d+\)", "(lebih dari 400)", actual)   # depth limit differs by Python version
        nxt = blocks[idx + 1] if idx + 1 < len(blocks) else None
        paired = (nxt is not None and nxt["lang"] == "hasil"
                  and all(not l.strip() for l in lines[b["end"] + 1:nxt["start"]]))
        if paired and nxt["code"] != actual:
            problems.append(f"{where}: the printed output differs from the real output")
            edits.append((nxt["start"] + 1, nxt["end"], actual.split("\n") if actual else []))
        if not paired and b["lang"] == "krc-error":
            problems.append(f"{where}: a krc-error block must be followed by a hasil block")
    if write and edits:
        for start, end, new in sorted(edits, reverse=True):
            lines[start:end] = new
        path.write_text("\n".join(lines), encoding="utf-8")
    return problems, len(blocks)


# ---- dialect builds -------------------------------------------------------
def _words(vocab):
    dialect = getattr(vocab, "dialect", None)
    if dialect is not None:
        return dict(dialect.words)
    return {id: vocab.word(id) for id in kerincilang.CATALOG["ids"]
            if not id.startswith("msg.")}


def _base_ids(vocab):
    dialect = getattr(vocab, "dialect", None)
    return set(dialect.base_ids) if dialect is not None else set()


def _owns(vocab, id):
    dialect = getattr(vocab, "dialect", None)
    if dialect is None or dialect.code == "base":
        return True
    return id not in dialect.base_ids


def _load(code):
    from dialects.loader import DialectError, load_dialect
    try:
        return load_dialect(code)
    except DialectError as err:
        raise BuildError("dialect %s: %s" % (code, err))


def _word_maps(words):
    maps = {}
    for id, word in words.items():
        maps.setdefault(word, []).append(id)
    return maps


def _ordered_candidates(ids, force_type):
    order = ("type.",) if force_type else INLINE_PREFIXES

    def rank(id):
        for index, prefix in enumerate(order):
            if id.startswith(prefix):
                return index
        return len(order)
    return sorted(ids, key=rank)


def _map_bare_word(word, source_maps, source_vocab, target_words,
                   target_vocab, force_type):
    for id in _ordered_candidates(source_maps.get(word, []), force_type):
        if not id.startswith(INLINE_PREFIXES):
            continue
        if _owns(target_vocab, id) or id in ALLOWED_FALLBACKS:
            return target_words[id], id
    return word, None


def _map_inline_span(text, source_maps, source_vocab, target_words,
                     target_vocab, force_type):
    stripped = text.strip()
    if not stripped:
        return text, set()
    expression = (len(stripped.split()) > 1
                  or any(c in stripped for c in "()[]{}.,=<>!+-*/%"))
    if expression and not force_type:
        new, used = kerincilang.rewrite_dialect_words(
            text, source_vocab, target_vocab)
        base = {id for id in used if id in _base_ids(target_vocab)}
        if base - ALLOWED_FALLBACKS:
            return text, set()
        return new, {id for id in used if id in ALLOWED_FALLBACKS}
    new, id = _map_bare_word(stripped, source_maps, source_vocab,
                             target_words, target_vocab, force_type)
    if new == stripped:
        return text, set()
    prefix = text[:len(text) - len(text.lstrip())]
    suffix = text[len(text.rstrip()):]
    used = {id} if id in ALLOWED_FALLBACKS else set()
    return prefix + new + suffix, used


def _map_spans(text, source_maps, source_vocab, target_words, target_vocab,
               fallbacks, force_type=False):
    def replace(match):
        content = match.group(1)
        new, used = _map_inline_span(content, source_maps, source_vocab,
                                     target_words, target_vocab, force_type)
        for id in used:
            fallbacks[id] = target_words[id]
        return "`" + new + "`"
    return SPAN.sub(replace, text)


def _kind_columns(header):
    cells = header.split("|")
    columns = set()
    for index, cell in enumerate(cells):
        if cell.strip() in ("Kind", "Jenis"):
            columns.add(index)
    return columns


def _map_prose_line(line, source_maps, source_vocab, target_words,
                    target_vocab, fallbacks, type_columns):
    if type_columns and line.startswith("|"):
        cells = line.split("|")
        for index, cell in enumerate(cells):
            cells[index] = _map_spans(cell, source_maps, source_vocab,
                                      target_words, target_vocab, fallbacks,
                                      force_type=index in type_columns)
        line = "|".join(cells)
    else:
        line = _map_spans(line, source_maps, source_vocab, target_words,
                          target_vocab, fallbacks)
    return line


def _link_target(source_path, dest_path, target, generated_map, planned):
    if target.startswith("#") or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
        return target
    path, sep, fragment = target.partition("#")
    if not path:
        return target
    source_target = (source_path.parent / path).resolve()
    chosen = generated_map.get(source_target, source_target)
    if chosen == source_target:
        if not chosen.exists():
            raise BuildError("%s: link target does not exist: %s"
                             % (source_path.name, target))
    elif chosen not in planned:
        raise BuildError("%s: link target is not part of this build: %s"
                         % (source_path.name, target))
    try:
        relative = os.path.relpath(chosen, dest_path.parent).replace(os.sep, "/")
    except ValueError:
        raise BuildError("%s: cannot make a relative link from %s to %s; "
                         "put the output on the same drive as the tutorial"
                         % (source_path.name, dest_path.parent, chosen))
    return relative + ("#" + fragment if sep else "")


def _rewrite_links(text, source_path, dest_path, generated_map, planned):
    def replace(match):
        new = _link_target(source_path, dest_path, match.group(2),
                           generated_map, planned)
        return "[%s](%s%s)" % (match.group(1), new, match.group(3) or "")
    return LINK.sub(replace, text)


def _map_code(code, source_vocab, target_vocab, source_maps, target_words,
              path, line, fallbacks):
    new, used = kerincilang.rewrite_dialect_words(code, source_vocab,
                                                   target_vocab)
    for id in sorted(used):
        if id in _base_ids(target_vocab):
            fallbacks[id] = target_words[id]
        word = target_words.get(id)
        if word is not None and not re.match(r"^[^\W\d]\w*$", word, re.UNICODE):
            raise BuildError("%s:%d: target word %r for %s is not an identifier"
                             % (path, line, word, id))
    try:
        names = kerincilang.dialect_declared_names(code, source_vocab)
    except LangError:
        names = set()                     # a deliberately malformed krc-error demo
    source_guarded = {word for id, word in _words(source_vocab).items()
                      if id.startswith(CODE_PREFIXES)}
    target_guarded = {word for id, word in target_words.items()
                      if id.startswith(CODE_PREFIXES)}
    for name in sorted(names):
        if name in target_guarded and name not in source_guarded:
            raise BuildError("%s:%d: user name %r collides with a %s word"
                             % (path, line, name, target_vocab.code))
    return new


def _collect_output_fallbacks(actual, target_vocab, target_words, fallbacks):
    for id in sorted(_base_ids(target_vocab)):
        if not id.startswith(TYPE_PREFIXES):
            continue
        word = target_words[id]
        if re.search(r"(?<!\w)%s(?!\w)" % re.escape(word), actual):
            fallbacks[id] = word


def _render_blocks(src, code_name, source_vocab, target_vocab, source_maps,
                   target_words, generated_map, planned, fallbacks):
    lines = src.read_text(encoding="utf-8").split("\n")
    blocks = parse_blocks(lines)
    for b in blocks:
        if not b["closed"]:
            raise BuildError("%s:%d: the fence is not closed"
                             % (src.name, b["start"] + 1))

    files = {}
    rendered = {}
    runnable = 0
    for idx, b in enumerate(blocks):
        where = b["start"] + 1
        if b["lang"] == "krc-berkas":
            name = b["info"]
            if name.endswith(".krc"):
                mapped = _map_code(b["code"], source_vocab, target_vocab,
                                   source_maps, target_words, src.name, where,
                                   fallbacks)
                content = ensure_header(mapped, code_name)
            else:
                content = b["code"]
            files[name] = content + "\n"
            rendered[idx] = {"kind": "helper", "code": content}
            continue
        if b["lang"] not in ("krc", "krc-error"):
            continue
        runnable += 1
        mapped = _map_code(b["code"], source_vocab, target_vocab, source_maps,
                           target_words, src.name, where, fallbacks)
        content = ensure_header(mapped, code_name)
        out, error = run_block(content, b["info"], files, quiet=True)
        if b["lang"] == "krc" and error:
            raise BuildError("%s:%d: unexpected error: %s"
                             % (src.name, where, error))
        if b["lang"] == "krc-error" and not error:
            raise BuildError("%s:%d: this program should fail but it succeeded"
                             % (src.name, where))
        actual = (out + (f"Kesalahan: {error}\n" if error else "")).rstrip("\n")
        actual = re.sub(r"\(lebih dari \d+\)", "(lebih dari 400)", actual)
        _collect_output_fallbacks(actual, target_vocab, target_words, fallbacks)
        nxt = blocks[idx + 1] if idx + 1 < len(blocks) else None
        paired = (nxt is not None and nxt["lang"] == "hasil"
                  and all(not l.strip() for l in lines[b["end"] + 1:nxt["start"]]))
        if not paired:
            raise BuildError("%s:%d: a %s block must be followed by a hasil block"
                             % (src.name, where, b["lang"]))
        rendered[idx] = {"kind": "run", "code": content, "actual": actual,
                         "hasil": idx + 1}

    out_lines, pos = [], 0
    for idx, b in enumerate(blocks):
        out_lines.extend(lines[pos:b["start"]])
        entry = rendered.get(idx)
        if entry is not None:
            if entry["kind"] == "helper":
                out_lines.append(lines[b["start"]])
                out_lines.extend(entry["code"].split("\n"))
                out_lines.append("```")
            else:
                out_lines.append(lines[b["start"]])
                out_lines.extend(entry["code"].split("\n"))
                out_lines.append("```")
                hasil = blocks[entry["hasil"]]
                out_lines.extend(lines[b["end"] + 1:hasil["start"]])
                out_lines.append(lines[hasil["start"]])
                out_lines.extend(entry["actual"].split("\n") if entry["actual"] else [])
                out_lines.append("```")
                pos = hasil["end"] + 1
                continue
        elif b["lang"] == "hasil" and idx > 0 and blocks[idx - 1].get("lang") in ("krc", "krc-error"):
            # already emitted by the block above
            pass
        else:
            out_lines.extend(lines[b["start"]:b["end"] + 1])
        pos = b["end"] + 1
    out_lines.extend(lines[pos:])
    return out_lines, runnable


def _transform_prose(lines, src, dest, source_maps, source_vocab, target_words,
                     target_vocab, fallbacks, generated_map, planned, name):
    result, type_columns = [], None
    for line in lines:
        if line.startswith("|"):
            if type_columns is None:
                type_columns = _kind_columns(line)
            line = _map_prose_line(line, source_maps, source_vocab, target_words,
                                   target_vocab, fallbacks, type_columns)
        else:
            type_columns = None
            line = _map_spans(line, source_maps, source_vocab, target_words,
                              target_vocab, fallbacks)
        line = _rewrite_links(line, src, dest, generated_map, planned)
        line = re.sub(r"\bSiulak\b", name, line)
        result.append(line)
    return result


def _render_file(src, dest, source_vocab, target_vocab, source_maps,
                 target_words, generated_map, planned, fallbacks, code_name,
                 name):
    block_lines, runnable = _render_blocks(
        src, code_name, source_vocab, target_vocab, source_maps, target_words,
        generated_map, planned, fallbacks)

    # Transform only the prose outside fenced blocks.
    lines = block_lines
    blocks = parse_blocks(lines)
    out, pos = [], 0
    for b in blocks:
        out.extend(_transform_prose(lines[pos:b["start"]], src, dest,
                                    source_maps, source_vocab, target_words,
                                    target_vocab, fallbacks, generated_map,
                                    planned, name))
        out.extend(lines[b["start"]:b["end"] + 1])
        pos = b["end"] + 1
    out.extend(_transform_prose(lines[pos:], src, dest, source_maps,
                                source_vocab, target_words, target_vocab,
                                fallbacks, generated_map, planned, name))
    return "\n".join(out), runnable


def _glossary_stub(axis, code_name, name, status):
    if axis == "en":
        return ("# Glossary\n\n"
                "This tutorial is generated for %s (status: %s). The full glossary\n"
                "is still the Siulak one: [glossary](../../glossary.md). A %s glossary\n"
                "follows when the dialect is approved.\n"
                "\n"
                "## Error messages\n"
                "\n"
                "The error messages are explained in the [Siulak glossary's error\n"
                "messages section](../../glossary.md#error-messages). They will be\n"
                "listed here when the dialect is approved.\n" % (name, status, name))
    return ("# Glosarium\n\n"
            "Tutorial ini dibuat untuk %s (status: %s). Glosarium lengkapnya\n"
            "masih glosarium Siulak: [glosarium](../../id/glosarium.md). "
            "Glosarium %s\nmenyusul setelah dialek ini disetujui.\n"
            "\n"
            "## Kesalahan\n"
            "\n"
            "Pesan kesalahan mengikuti glosarium Siulak: [glosarium\n"
            "Indonesia](../../id/glosarium.md). Daftar lengkapnya akan ditulis di\n"
            "sini setelah dialek ini disetujui.\n"
            % (name, status, name))


def _insert_banner(text, axis, name, status):
    lines = text.split("\n")
    banner = BANNER[axis].format(name=name, status=status)
    for i, line in enumerate(lines):
        if line.startswith("# "):
            if i + 1 < len(lines) and not lines[i + 1].strip():
                lines[i + 2:i + 2] = [banner, ""]
            else:
                lines[i + 1:i + 1] = ["", banner, ""]
            break
    return "\n".join(lines)


def _fallback_section(axis, name, fallbacks, target_words):
    if not fallbacks:
        return ""
    heading = FALLBACK_HEADING[axis]
    note = FALLBACK_NOTE[axis].format(name=name)
    rows = []
    for id in sorted(fallbacks):
        entry = kerincilang.CATALOG["ids"][id]
        rows.append("| `%s` | `%s` | %s |"
                    % (id, fallbacks[id], entry.get("description", "")))
    return "\n" + heading + "\n\n" + note + "\n" + "\n".join(rows) + "\n"


def _write_tree(dest_root, contents):
    dest_root = pathlib.Path(dest_root)
    parent = dest_root.parent
    parent.mkdir(parents=True, exist_ok=True)
    temporary = pathlib.Path(tempfile.mkdtemp(prefix=".krc-tutorial-", dir=parent))
    try:
        for dest, text in contents.items():
            target = temporary / dest.relative_to(dest_root)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(text.encode("utf-8"))
        if dest_root.exists():
            shutil.rmtree(dest_root)
        os.replace(temporary, dest_root)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def build(code, prose="semua", out_root=None, source_root=None):
    """Build one dialect's tutorial trees and return a summary.

    `source_root` and `out_root` are for tests and never change the default
    committed layout (`tutorial/`).
    """
    source_root = pathlib.Path(source_root) if source_root is not None else ROOT / "tutorial"
    out_root = pathlib.Path(out_root) if out_root is not None else ROOT / "tutorial"
    source_dialect = _load("siulak")
    target_dialect = _load(code)
    source_vocab = source_dialect.vocab
    target_vocab = target_dialect.vocab
    source_words = _words(source_vocab)
    target_words = _words(target_vocab)
    source_maps = _word_maps(source_words)
    name, status = target_dialect.name, target_dialect.status

    axes = ("en", "id") if prose == "semua" else (prose,)
    baseline = {
        "en": sorted(source_root.glob("*.md")),
        "id": sorted((source_root / "id").glob("*.md")),
    }
    for axis in axes:
        if not baseline[axis]:
            raise BuildError("no %s lessons under %s" % (axis, source_root))

    generated_map, planned = {}, set()
    for axis in axes:
        for src in baseline[axis]:
            dest = (out_root / axis / code / src.name).resolve()
            generated_map[src.resolve()] = dest
            planned.add(dest)

    fallbacks = {}
    contents = {}
    blocks = 0
    indexes = {}
    for axis in axes:
        for src in baseline[axis]:
            dest = out_root / axis / code / src.name
            if src.name == GLOSSARY_NAMES[axis]:
                contents[dest] = _glossary_stub(axis, code, name, status)
                continue
            text, runnable = _render_file(
                src, dest, source_vocab, target_vocab, source_maps,
                target_words, generated_map, planned, fallbacks, code, name)
            blocks += runnable
            if src.name == "README.md":
                indexes[axis] = (dest, text)
            else:
                contents[dest] = text + FOOTER[axis].format(name=name, status=status)

    for axis, (index_dest, index_text) in indexes.items():
        text = _insert_banner(index_text, axis, name, status)
        text += _fallback_section(axis, name, fallbacks, target_words)
        text += FOOTER[axis].format(name=name, status=status)
        contents[index_dest] = text

    for axis in axes:
        root = out_root / axis / code
        tree = {dest: text for dest, text in contents.items()
                if root in dest.parents}
        _write_tree(root, tree)

    return {"code": code, "axes": axes, "files": len(contents), "blocks": blocks,
            "fallbacks": fallbacks}


def _build_targets(args, parser):
    if args.bangun and args.semua_dialek:
        parser.error("--bangun and --semua-dialek cannot be combined")
    if args.tulis and (args.bangun or args.semua_dialek):
        parser.error("--tulis cannot be combined with a build")
    if (args.prosa or args.keluaran) and not (args.bangun or args.semua_dialek):
        parser.error("--prosa and --keluaran require --bangun or --semua-dialek")
    if not (args.bangun or args.semua_dialek):
        return None
    prose = args.prosa or "semua"
    if args.bangun:
        return [args.bangun], prose
    from dialects.loader import available_dialects
    codes = []
    for code in available_dialects():
        if code in ("siulak", "base"):
            continue
        dialect = _load(code)
        if dialect.status in ("review", "approved"):
            codes.append(code)
    return codes, prose


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tulis", action="store_true", help="rewrite baseline hasil blocks")
    parser.add_argument("--bangun", metavar="KODE", help="build one dialect tutorial tree")
    parser.add_argument("--semua-dialek", action="store_true",
                        help="build every review or approved dialect")
    parser.add_argument("--prosa", choices=("en", "id", "semua"),
                        help="prose tree to build (default: semua)")
    parser.add_argument("--keluaran", metavar="DIR", help="output root (default: tutorial/)")
    args = parser.parse_args()

    try:
        targets = _build_targets(args, parser)
    except BuildError as err:
        print("sinkron_tutorial: error: %s" % err, file=sys.stderr)
        return 2

    if targets is None:
        all_problems, total = [], 0
        for path in baseline_paths():
            problems, n = process(path, args.tulis)
            total += n
            all_problems += problems
        if args.tulis:
            remaining = []
            for path in baseline_paths():
                remaining += process(path, False)[0]
            all_problems = remaining
        for p in all_problems:
            print("PROBLEM", p)
        print(f"{total} code blocks checked in tutorial/, {len(all_problems)} problems")
        return 1 if all_problems else 0

    codes, prose = targets
    out_root = pathlib.Path(args.keluaran) if args.keluaran else ROOT / "tutorial"
    try:
        # Validate every target before writing anything.
        for code in codes:
            _load(code)
    except BuildError as err:
        print("sinkron_tutorial: error: %s" % err, file=sys.stderr)
        return 2

    results = []
    for code in codes:
        try:
            results.append(build(code, prose=prose, out_root=out_root))
        except BuildError as err:
            print("sinkron_tutorial: error: %s" % err, file=sys.stderr)
            return 1
        except Exception as err:                   # a block or link failure
            print("sinkron_tutorial: error: %s" % err, file=sys.stderr)
            return 1

    for result in results:
        for id in sorted(result["fallbacks"]):
            word = result["fallbacks"][id]
            print("warning: dialect %s: %s falls back to the base word %r"
                  % (result["code"], id, word), file=sys.stderr)
        print("built %s: %s; %d files; %d blocks; %d base fallback(s)"
              % (result["code"], ", ".join(result["axes"]), result["files"],
                 result["blocks"], len(result["fallbacks"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
