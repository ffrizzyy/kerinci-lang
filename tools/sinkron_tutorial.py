"""Checks (or refreshes) the code samples in tutorial/*.md.

  python3 tools/sinkron_tutorial.py            check every sample (exit 1 on any problem)
  python3 tools/sinkron_tutorial.py --tulis    rewrite the ```hasil blocks with real output

Block kinds, written as the language of a fenced block:
  krc                 a program. It must run without error.
  krc masukan=a|b     the same, with the lines a and b typed in for tanyo()
  krc-error           a program that must fail (the message goes in the hasil block)
  krc-berkas NAME     a helper file (not run); later blocks in the lesson can use it
  hasil               the expected output of the block just above it
Any other language (bash, text, ...) is ignored.
"""
import argparse
import contextlib
import io
import os
import pathlib
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import kerincilang  # noqa: E402
from kerincilang import LangError  # noqa: E402

FENCE = re.compile(r"^```(\S+)\s*(.*)$")


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


def parse_blocks(lines):
    blocks, i = [], 0
    while i < len(lines):
        m = FENCE.match(lines[i])
        if m:
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            blocks.append({"lang": m.group(1), "info": m.group(2).strip(),
                           "start": i, "end": j, "code": "\n".join(lines[i + 1:j])})
            i = j + 1
        else:
            i += 1
    return blocks


def run_block(code, info, files):
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
        try:
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
        if b["lang"] == "krc-berkas":
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tulis", action="store_true", help="rewrite hasil blocks")
    args = parser.parse_args()
    all_problems, total = [], 0
    for path in sorted((ROOT / "tutorial").rglob("*.md")):
        problems, n = process(path, args.tulis)
        total += n
        all_problems += problems
    if args.tulis:
        remaining = []
        for path in sorted((ROOT / "tutorial").rglob("*.md")):
            remaining += process(path, False)[0]
        all_problems = remaining
    for p in all_problems:
        print("PROBLEM", p)
    print(f"{total} code blocks checked in tutorial/, {len(all_problems)} problems")
    return 1 if all_problems else 0


if __name__ == "__main__":
    sys.exit(main())
