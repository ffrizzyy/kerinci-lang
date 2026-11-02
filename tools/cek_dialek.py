"""Checks dialect files. This is the CI gate for `dialects/`.

    python3 tools/cek_dialek.py --semua
    python3 tools/cek_dialek.py --kode koto-payang
    python3 tools/cek_dialek.py --kode koto-payang --ketat

Exit codes:
    0  every requested dialect is valid
    1  a validation error (schema, clash, identifier, path, JSON)
    2  strict mode: an approved dialect falls back to the base, or `core` is newer

The checker never imports or executes a dialect; it only reads JSON.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dialects import loader  # noqa: E402

HELP = """Usage:
  python3 tools/cek_dialek.py --semua
  python3 tools/cek_dialek.py --kode CODE [--ketat]

  --semua        check every file in dialects/
  --kode CODE    check one dialect (repeatable)
  --ketat        strict: fail an approved dialect that falls back to the base

Exit: 0 ok, 1 validation error, 2 strict failure."""


def _summary(dialect):
    tiers = dialect.report.tiers()
    return "%s: tier 1 %d/%d, tier 2 %d/%d, tier 3 %d/%d" % (
        dialect.code,
        tiers[1][0], tiers[1][1],
        tiers[2][0], tiers[2][1],
        tiers[3][0], tiers[3][1])


def _strict_gaps(dialect):
    """Tier 1 IDs an approved dialect still takes from the base."""
    if dialect.status != "approved":
        return []
    return [id for id, source in dialect.report.fallbacks
            if source == "base" and loader.IDS[id]["tier"] == 1]


def main(argv=None, root=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    codes, strict = [], False
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg in ("-h", "--help"):
            print(HELP)
            return 0
        if arg == "--semua":
            pass
        elif arg == "--ketat":
            strict = True
        elif arg == "--kode":
            index += 1
            if index >= len(argv):
                print("cek_dialek: --kode needs a value", file=sys.stderr)
                return 1
            codes.append(argv[index])
        elif arg.startswith("--kode="):
            codes.append(arg.split("=", 1)[1])
        else:
            print("cek_dialek: unknown argument %r\n\n%s" % (arg, HELP),
                  file=sys.stderr)
            return 1
        index += 1

    targets = codes or loader.available_dialects(root)
    had_error = had_strict = False
    for code in targets:
        try:
            dialect = loader.load_dialect(code, root=root)
        except loader.DialectError as err:
            for problem in err.problems:
                print("%s: %s" % (code, problem))
            had_error = True
            continue
        for problem in dialect.report.problems:
            print("%s: %s" % (code, problem))
            if problem.code == "newer-core" and strict:
                had_strict = True
        print(_summary(dialect))
        gaps = _strict_gaps(dialect)
        if gaps:
            if strict:
                print("%s: strict: %d tier-1 word%s still come from the base: %s"
                      % (code, len(gaps), "" if len(gaps) == 1 else "s",
                         ", ".join(gaps)))
                had_strict = True
            else:
                print("%s: note: %d tier-1 word%s still come from the base"
                      % (code, len(gaps), "" if len(gaps) == 1 else "s"))

    if had_error:
        return 1
    if had_strict:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
