"""Dependency audit for a stdlib-only skeleton: fail on unpinned third-party imports.

If a manifest with dependencies ever lands, this script defers to pip audit
when installed and fails honestly when it cannot verify.
"""
import ast
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCAN_DIRS = ("src", "scripts", "tests", "migrations")


def local_top_levels() -> set[str]:
    names = {"src", "scripts", "tests", "migrations"}
    for dirname in SCAN_DIRS:
        d = ROOT / dirname
        if d.is_dir():
            names.update(p.stem for p in d.glob("*.py"))
    return names


def third_party_imports() -> set[str]:
    found: set[str] = set()
    stdlib = sys.stdlib_module_names
    local = local_top_levels()
    for dirname in SCAN_DIRS:
        d = ROOT / dirname
        if not d.is_dir():
            continue
        for path in sorted(d.rglob("*.py")):
            try:
                tree = ast.parse(path.read_text())
            except (OSError, SyntaxError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        found.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.level == 0 and node.module:
                        found.add(node.module.split(".")[0])
    return {m for m in found if m not in stdlib and m not in local}


def main() -> int:
    third_party = third_party_imports()
    if not third_party:
        print("audit: ok (stdlib-only, no third-party imports)")
        return 0
    manifests = list(ROOT.glob("requirements*.txt")) + list(ROOT.glob("pyproject.toml"))
    if not manifests:
        print(f"audit: FAIL — third-party imports {sorted(third_party)} with no manifest;"
              " pin them or remove them")
        return 1
    if shutil.which("pip-audit") is None:
        print(f"audit: FAIL — manifests exist but pip-audit is not installed;"
              f" cannot verify {sorted(third_party)}")
        return 1
    proc = subprocess.run(["pip-audit"], cwd=ROOT)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
