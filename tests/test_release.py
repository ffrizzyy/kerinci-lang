"""Wheel smoke test: build, inspect, install, and run both dialects.

Run with: python3 tests/test_release.py

This suite needs pip and its isolated build (the network on a clean runner), so
`build.py` does not run it. CI runs it on Python 3.12 and `RELEASING.md` names
it as a release step. The offline docs/release gate is
`tests/test_docs_release.py`.
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

FAILED = []
TEMP = tempfile.TemporaryDirectory()
BASE = pathlib.Path(TEMP.name)

EXCLUDED = (".git", "build", "dist", "__pycache__")
EXCLUDED_SUFFIXES = (".pyc", ".egg-info")
EXPECTED_MEMBERS = (
    "core/ids.json",
    "dialects/siulak.json",
    "dialects/siulak.md",
    "dialects/koto-payang.json",
    "dialects/koto-payang.md",
)


def check(ok, label, detail=""):
    print("PASS" if ok else "FAIL", label, "" if ok else "-> " + str(detail))
    if not ok:
        FAILED.append(label)


def run(cwd, *args, **kwargs):
    env = dict(os.environ)
    env.update(kwargs.pop("env", {}))
    return subprocess.run([sys.executable] + list(args), cwd=str(cwd),
                          capture_output=True, text=True, env=env, **kwargs)


def copy_checkout(destination):
    """A clean checkout copy: no VCS, build output, or bytecode."""
    def ignore(folder, names):
        skipped = []
        for name in names:
            if name in EXCLUDED or name.endswith(EXCLUDED_SUFFIXES):
                skipped.append(name)
        return skipped

    shutil.copytree(ROOT, destination, ignore=ignore)
    return destination


def build_wheel(work):
    wheels = work / "wheels"
    wheels.mkdir()
    result = run(work, "-m", "pip", "wheel", ".", "--no-deps", "-w", str(wheels))
    if result.returncode != 0:
        check(False, "pip wheel builds the package",
              (result.stdout + result.stderr)[-3000:])
        return None
    check(True, "pip wheel builds the package")
    found = sorted(wheels.glob("kerincilang-*.whl"))
    check(len(found) == 1, "the build produced exactly one wheel", found)
    return found[0] if found else None


def inspect_wheel(wheel):
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        for member in EXPECTED_MEMBERS:
            check(member in names, "wheel contains %s" % member)
        check(any(name.endswith("kerincilang.py") for name in names),
              "wheel contains the interpreter module")

        csv = [name for name in names
               if name.startswith("dialects/src/") and name.endswith(".csv")]
        check(not csv, "wheel contains no dialect worksheets", csv)
        bytecode = [name for name in names
                    if "__pycache__" in name or name.endswith(".pyc")]
        check(not bytecode, "wheel contains no bytecode", bytecode)
        check(not any(name.endswith(".py") and name.count("/") > 1
                      for name in names),
              "wheel contains no per-dialect Python modules")


def install_wheel(wheel, target):
    result = run(BASE, "-m", "pip", "install", "--no-deps", "--target",
                 str(target), str(wheel))
    check(result.returncode == 0, "pip install --target succeeds",
          (result.stdout + result.stderr)[-3000:])
    check((target / "kerincilang.py").is_file(),
          "the installed target contains the interpreter")
    check((target / "core" / "ids.json").is_file(),
          "the installed target contains core/ids.json")
    check((target / "dialects" / "koto-payang.json").is_file(),
          "the installed target contains the Koto Payang data")


def run_installed(target, work):
    """Run both dialects from a cwd outside the checkout."""
    outside = BASE / "outside"
    outside.mkdir()
    env = {"PYTHONPATH": str(target)}

    siulak = outside / "siulak.krc"
    siulak.write_bytes(b'# dialek: siulak\nnyetak "siulak"\n')
    koto = outside / "koto-payang.krc"
    koto.write_bytes(b'# dialek: koto-payang\nnytak "koto-payang"\n')

    result = run(outside, "-c",
                 "import sys, kerincilang; "
                 "sys.exit(kerincilang.main([sys.argv[1]]))",
                 str(siulak), env=env)
    check(result.returncode == 0 and result.stdout == "siulak\n",
          "the installed Siulak program prints its output",
          (result.returncode, result.stdout, result.stderr))

    result = run(outside, "-c",
                 "import sys, kerincilang; "
                 "sys.exit(kerincilang.main([sys.argv[1]]))",
                 str(koto), env=env)
    check(result.returncode == 0 and result.stdout == "koto-payang\n",
          "the installed Koto Payang program prints its output",
          (result.returncode, result.stdout, result.stderr))

    result = run(outside, "-c",
                 "from dialects.loader import available_dialects; "
                 "print(','.join(sorted(available_dialects())))", env=env)
    codes = sorted(result.stdout.strip().split(","))
    check(result.returncode == 0 and codes == ["koto-payang", "siulak"],
          "the installed package finds both dialects", codes)

    result = run(outside, "-c",
                 "import kerincilang; print(kerincilang.__version__)", env=env)
    check(result.returncode == 0 and result.stdout.strip() == "0.6.0",
          "the installed package reports version 0.6.0",
          (result.returncode, result.stdout, result.stderr))


def main():
    work = copy_checkout(BASE / "checkout")
    check(not (work / ".git").exists(), "the clean copy has no .git")
    check(not (work / "build").exists(), "the clean copy has no build directory")
    check(not (work / "dist").exists(), "the clean copy has no dist directory")
    check(not any((work / "core").glob("__pycache__")),
          "the clean copy has no bytecode in core")

    wheel = build_wheel(work)
    if wheel is not None:
        inspect_wheel(wheel)
        target = BASE / "target"
        install_wheel(wheel, target)
        run_installed(target, work)

    print()
    if FAILED:
        print("%d FAILED: %s" % (len(FAILED), ", ".join(FAILED)))
        return 1
    print("all wheel smoke tests passed")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        TEMP.cleanup()
