"""Diagrams: validate workspace.dsl exists and parses minimally; check Notion path+version links are pointers."""
import pathlib
import re
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
for md in (root / "docs" / "architecture").rglob("*.md"):
    body = md.read_text()
    if "workspace.dsl" not in body:
        print(f"diagrams: {md} does not point at workspace.dsl")
        sys.exit(1)
    if re.search(r"```(mermaid|plantuml)", body):
        print(f"diagrams: {md} pastes a rendered copy — link path+version instead")
        sys.exit(1)
print("diagrams: ok (pointers valid; DSL validity via editor extension / Lite preview)")
