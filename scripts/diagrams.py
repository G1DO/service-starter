"""Diagrams: validate workspace.dsl via structurizr validate; check docs are pointers (Lite EOL)."""
import os
import pathlib
import re
import shutil
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parents[1]
dsl = root / "docs" / "architecture" / "workspace.dsl"
if not dsl.exists():
    print("diagrams: no workspace.dsl — N/A absent")
    sys.exit(0)
text = dsl.read_text()
for needle in ("workspace", "model", "views", "container"):
    if needle not in text:
        print(f"diagrams: workspace.dsl missing {needle}")
        sys.exit(1)
depth = 0
for ch in text:
    if ch == "{":
        depth += 1
    elif ch == "}":
        depth -= 1
        if depth < 0:
            print("diagrams: workspace.dsl has unbalanced braces")
            sys.exit(1)
if depth != 0:
    print("diagrams: workspace.dsl has unbalanced braces")
    sys.exit(1)
dupes = [p for p in root.rglob("*.mmd") if ".git/" not in str(p) and "__pycache__" not in str(p)]
if dupes:
    print(f"diagrams: duplicate mermaid export present: {dupes[0]} (delete; DSL is source of truth)")
    sys.exit(1)
for md in (root / "docs" / "architecture").rglob("*.md"):
    body = md.read_text()
    if "workspace.dsl" not in body:
        print(f"diagrams: {md} does not point at workspace.dsl")
        sys.exit(1)
    if "structurizr validate -workspace" not in body:
        print(f"diagrams: {md} does not document structurizr validate")
        sys.exit(1)
    if re.search(r"```(mermaid|plantuml)", body):
        print(f"diagrams: {md} pastes a rendered copy — link path+version instead")
        sys.exit(1)
cli = shutil.which("structurizr") or shutil.which("structurizr.sh")
script = root / "structurizr.sh"
if cli is None and script.exists():
    cli = str(script)
if cli is not None:
    proc = subprocess.run(
        [cli, "validate", "-workspace", str(dsl)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        out = (proc.stdout or "") + (proc.stderr or "")
        print(f"diagrams: structurizr validate failed\n{out.strip()}")
        sys.exit(1)
    print("diagrams: ok (pointers valid; structurizr validate passed)")
else:
    if os.environ.get("CI") == "true":
        print("diagrams: FAIL — structurizr CLI missing in CI; STRUCTURAL-ONLY not allowed")
        sys.exit(1)
    print("diagrams: ok STRUCTURAL-ONLY (pointers valid; structural validation passed, structurizr CLI not installed)")
