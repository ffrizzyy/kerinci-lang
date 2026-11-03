"""Builds a single-file KerinciLang program: dist/krc.pyz

    python3 build.py

Every offline suite in `tests/test_*.py` runs first; `tests/test_release.py`
is the network-dependent wheel smoke and runs separately (CI and
`RELEASING.md`). The result runs on any computer with Python 3.9+:
`python3 krc.pyz contoh.krc`. On macOS/Linux you can also `chmod +x krc.pyz`
and run `./krc.pyz contoh.krc`.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipapp

root = pathlib.Path(__file__).parent
dist = root / "dist"

print("1/3 Running offline suites...")
suites = [path for path in sorted((root / "tests").glob("test_*.py"))
          if path.name != "test_release.py"]
if not suites:
    sys.exit("No test suites found. Build cancelled.")
for suite in suites:
    print(f"  {suite.stem} ...", end=" ", flush=True)
    result = subprocess.run([sys.executable, str(suite)], cwd=str(root),
                            capture_output=True, text=True)
    if result.returncode != 0:
        print("FAILED")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(f"Tests failed ({suite.name}). Build cancelled.")
    print("ok")
print("  wheel smoke: python3 tests/test_release.py (runs separately)")

print("2/3 Building krc.pyz...")
dist.mkdir(exist_ok=True)


def _skip_bytecode(directory, names):
    return [name for name in names
            if name == "__pycache__" or name.endswith(".pyc")]


with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    shutil.copy(root / "kerincilang.py", tmp / "kerincilang.py")
    # the neutral catalogue and the dialect data must travel with the program
    shutil.copytree(root / "core", tmp / "core", ignore=_skip_bytecode)
    shutil.copytree(root / "dialects", tmp / "dialects", ignore=_skip_bytecode)
    (tmp / "__main__.py").write_text(
        "import sys\nfrom kerincilang import main\nsys.exit(main())\n", encoding="utf-8")
    zipapp.create_archive(tmp, dist / "krc.pyz", interpreter="/usr/bin/env python3")
(dist / "krc.pyz").chmod(0o755)

print("3/3 Copying the examples...")
for example in (root / "examples").glob("*.krc"):
    shutil.copy(example, dist / example.name)

print(f"Done: {dist / 'krc.pyz'}  ({(dist / 'krc.pyz').stat().st_size} bytes)")
