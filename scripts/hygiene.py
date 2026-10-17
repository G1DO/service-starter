"""Hygiene: fails on ORG placeholders, TODO owners, echo stubs, CODEOWNERS/CI misalignment."""
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parents[1]
failures: list[str] = []

for path in root.rglob("*"):
    if ".git/" in str(path) or path.is_dir():
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
        failures.append(f"{path}: swallows failures via || true")

codeowners = (root / ".github" / "CODEOWNERS").read_text()
for must in ("/src/auth/", "/src/data/", "migrations/", "/openapi", "/.github/"):
    alt = must.strip("/")
    if must not in codeowners and alt not in codeowners:
        failures.append(f"CODEOWNERS: missing coverage for {must}")

ci = (root / ".github" / "workflows" / "ci.yml").read_text()
for needle in ("dorny/paths-filter", "needs: [changes", "contains(github.event.pull_request.labels"):
    if needle not in ci:
        failures.append(f"ci.yml: missing {needle}")

if failures:
    print("\n".join(failures))
    sys.exit(1)
print("hygiene: ok")
