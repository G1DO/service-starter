"""Hygiene: fails on ORG placeholders, TODO owners, echo stubs, CODEOWNERS/CI misalignment."""
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

ci = (root / ".github" / "workflows" / "ci.yml").read_text()
nightly = (root / ".github" / "workflows" / "nightly.yml").read_text()
for needle in ("task verify", "!cancelled()"):
    if needle not in ci:
        failures.append(f"ci.yml: missing {needle}")
for banned in ("dorny/paths-filter", "paths-filter", "needs: [changes", "needs: [test]", "needs.changes", "force-integration", "force-e2e", "force-contract", "contains(github.event.pull_request.labels", "test:int", "test:e2e", "test:contract"):
    if banned in ci:
        failures.append(f"ci.yml: forbidden {banned}")
if "task verify" not in nightly:
    failures.append("nightly.yml: missing task verify")
if nightly.count("run: task") != 1:
    failures.append("nightly.yml: must run task verify only")

if failures:
    print("\n".join(failures))
    sys.exit(1)
print("hygiene: ok")
