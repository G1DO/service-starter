"""Hygiene: fails on placeholders, echo stubs, and CODEOWNERS gaps.

CI/workflow alignment is enforced by branch protection (required `gate`
check, strict) plus the gate job's needs check in ci.yml — not by text lint.
"""
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parents[1]
failures: list[str] = []

for path in root.rglob("*"):
    if ".git/" in str(path) or "__pycache__" in str(path) or path.is_dir():
        continue
    if path.suffix == ".pyc":
        continue
    if path.name == "hygiene.py":
        continue
    try:
        text = path.read_text(errors="ignore")
    except OSError:
        continue
    if "@" + "ORG/" in text:
        failures.append(f"{path}: contains placeholder")
    if re.search(r"echo\s+place" + r"holder", text):
        failures.append(f"{path}: contains echo stub")
    if "TODO" + " CI" in text:
        failures.append(f"{path}: contains stub marker")
    if re.search(r"\|\|\s*true", text):
        failures.append(f"{path}: swallows failures via {'||'} true")
    if re.search("python3?\\s+-c\\s+[\"']print\\s*\\(", text):
        failures.append(f"{path}: contains inline print stub (move real logic into scripts/)")
    if re.search("assertTrue\\s*\\(\\s*True\\s*\\)", text):
        failures.append(f"{path}: contains placeholder assertion")

codeowners = (root / ".github" / "CODEOWNERS").read_text()
for must in ("/src/auth/", "/src/data/", "migrations/", "/openapi", "/.github/"):
    alt = must.strip("/")
    if must not in codeowners and alt not in codeowners:
        failures.append(f"CODEOWNERS: missing coverage for {must}")
if not re.search(r"(?m)^\*\s+@\S+", codeowners):
    failures.append("CODEOWNERS: missing fallback `*` owner")

if failures:
    print("\n".join(failures))
    sys.exit(1)
print("hygiene: ok")
