"""SAST guard: stdlib-only static analysis. Fails on dangerous patterns.

Runs everywhere with zero dependencies. Complements (does not replace)
CodeQL default setup, which covers PRs server-side, and Semgrep where installed.
"""
import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCAN_DIRS = ("src", "scripts", "tests", "migrations")

# (rule id, matcher description) — kept tight to avoid false positives.
DANGEROUS_CALLS = {"eval", "exec"}
DANGEROUS_ATTRS = {
    ("os", "system"),
    ("os", "popen"),
    ("pickle", "load"),
    ("pickle", "loads"),
    ("marshal", "load"),
    ("marshal", "loads"),
    ("yaml", "load"),
}


def check_file(path: pathlib.Path) -> list[str]:
    findings: list[str] = []
    try:
        tree = ast.parse(path.read_text(), filename=str(path))
    except (OSError, SyntaxError) as exc:
        return [f"{path}: cannot parse ({exc})"]
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id in DANGEROUS_CALLS:
            findings.append(f"{path}:{node.lineno}: rule no-dynamic-exec ({func.id})")
        elif isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            if (func.value.id, func.attr) in DANGEROUS_ATTRS:
                findings.append(
                    f"{path}:{node.lineno}: rule no-unsafe-deser-or-shell"
                    f" ({func.value.id}.{func.attr})"
                )
            if func.value.id == "subprocess":
                for kw in node.keywords:
                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) \
                            and kw.value.value is True:
                        findings.append(f"{path}:{node.lineno}: rule no-shell-true")
    return findings


def main() -> int:
    findings: list[str] = []
    for dirname in SCAN_DIRS:
        d = ROOT / dirname
        if not d.is_dir():
            continue
        for path in sorted(d.rglob("*.py")):
            if path.name == "sast_guard.py":
                continue
            findings.extend(check_file(path))
    if findings:
        print("sast_guard: findings (fix or justify in the PR):")
        print("\n".join(findings))
        return 1
    print("sast_guard: ok (no eval/exec/os.system/pickle/yaml.load/shell=True)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
