"""Builds a single-file KerinciLang program: dist/krc.pyz

    python3 build.py

The result runs on any computer with Python 3.9+:  python3 krc.pyz contoh.krc
On macOS/Linux you can also `chmod +x krc.pyz` and run  ./krc.pyz contoh.krc
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipapp

root = pathlib.Path(__file__).parent
dist = root / "dist"

print("1/3 Running tests...")
for test in ("test_kerincilang.py", "test_tutorial.py"):
    if subprocess.run([sys.executable, str(root / "tests" / test)],
                      stdout=subprocess.DEVNULL).returncode != 0:
        sys.exit(f"Tests failed ({test}). Build cancelled.")

print("2/3 Building krc.pyz...")
dist.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    shutil.copy(root / "kerincilang.py", tmp / "kerincilang.py")
    # the neutral catalogue and the dialect data must travel with the program
    shutil.copytree(root / "core", tmp / "core")
    shutil.copytree(root / "dialects", tmp / "dialects")
    (tmp / "__main__.py").write_text(
        "import sys\nfrom kerincilang import main\nsys.exit(main())\n", encoding="utf-8")
    zipapp.create_archive(tmp, dist / "krc.pyz", interpreter="/usr/bin/env python3")
(dist / "krc.pyz").chmod(0o755)

print("3/3 Copying the examples...")
for example in (root / "examples").glob("*.krc"):
    shutil.copy(example, dist / example.name)

print(f"Done: {dist / 'krc.pyz'}  ({(dist / 'krc.pyz').stat().st_size} bytes)")
