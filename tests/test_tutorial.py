"""Runs every code sample in tutorial/ and checks the glossary covers the whole language.

    python3 tests/test_tutorial.py
"""
import os
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, ROOT)

import sinkron_tutorial  # noqa: E402

failed = 0

# 1. every ```krc sample runs and prints exactly what the lesson says
problems = []
total = 0
for path in sinkron_tutorial.baseline_paths():
    found, n = sinkron_tutorial.process(path, write=False)
    problems += found
    total += n
for p in problems:
    print("FAIL tutorial:", p)
print("PASS" if not problems else "FAIL", f"tutorial: {total} blocks checked, {len(problems)} problems")
failed += bool(problems)

# 2. the glossary covers every keyword, comparison word, and built-in function
result = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "buat_glosarium.py")],
                        capture_output=True, text=True)
ok = result.returncode == 0
print("PASS" if ok else "FAIL", "glossary covers the whole language", "" if ok else result.stdout + result.stderr)
failed += not ok

# 3. every lesson is linked from its tutorial index (English and Indonesian)
for folder in ("tutorial", os.path.join("tutorial", "id")):
    if not os.path.isdir(os.path.join(ROOT, folder)):      # the Indonesian copy is optional
        continue
    index = open(os.path.join(ROOT, folder, "README.md"), encoding="utf-8").read()
    lessons = [f for f in sorted(os.listdir(os.path.join(ROOT, folder))) if f[:2].isdigit() and f.endswith(".md")]
    missing = [f for f in lessons if f not in index]
    ok = len(lessons) == 14 and not missing
    print("PASS" if ok else "FAIL", f"{folder}/README.md links all {len(lessons)} lessons", missing or "")
    failed += not ok

print("\nALL PASSED" if not failed else f"\nFAILED: {failed}")
sys.exit(1 if failed else 0)
