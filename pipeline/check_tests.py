import py_compile
import re
import subprocess
import sys
from pathlib import Path

errors = []
files = sorted(Path("tests/api").glob("test_*.py"))

for f in files:
    code = f.read_text(encoding="utf-8")
    try:
        py_compile.compile(str(f), doraise=True)
    except py_compile.PyCompileError as e:
        errors.append(f"{f.name} : ne compile pas ({e.msg[:80]})")
    if not re.search(r'@pytest\.mark\.tc\("TC-[\w-]+"\)', code):
        errors.append(f"{f.name} : marqueur tc manquant")
    if "time.sleep" in code:
        errors.append(f"{f.name} : time.sleep interdit")
    if re.search(r"https?://(?!localhost)", code):
        errors.append(f"{f.name} : appel externe")
    if re.search(r"status_code\s*(==\s*5\d\d|in\s*\([^)]*5\d\d)", code):
        errors.append(f"{f.name} : assert un code 5xx (aligné sur un défaut ?)")

if files:
    r = subprocess.run([sys.executable, "-m", "ruff", "check", "tests/api"])
    if r.returncode:
        errors.append("ruff a signalé des erreurs")

print(f"{len(files)} fichiers vérifiés")
if errors:
    print("\n".join(errors))
    sys.exit(1)
print("OK")