"""Pattern guard for real secret formats. Patterns are assembled to avoid self-matching."""
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parents[1]
GH_P = "gh" + "p_" + "|gh" + "o_"
AKIA = "AKIA[0-9A-Z]{16}"
SLACK = "xox[ bap]" + "-"
PATTERN = "(?i)(" + GH_P + "|" + AKIA + "|" + SLACK + ")"

bad: list[str] = []
for path in root.rglob("*"):
    if ".git/" in str(path) or "__pycache__" in str(path) or not path.is_file():
        continue
    if path.suffix == ".pyc":
        continue
    if path.name == "secrets_guard.py":
        continue
    try:
        text = path.read_text(errors="ignore")[:20000]
    except OSError:
        continue
    if re.search(PATTERN, text):
        bad.append(str(path.relative_to(root)))

print("secret pattern hit:", bad)
sys.exit(1 if bad else 0)
