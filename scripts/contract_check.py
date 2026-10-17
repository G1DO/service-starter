"""Contract gate: oasdiff breaking --fail-on ERR --err-ignore <baseline>.

N/A-absent while no versioned contract exists. Once spec files land, every
ERR-level breaking change fails the gate unless listed in the baseline, and
a baseline that matches nothing fails as stale (must-resolve).
"""
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC_SUFFIXES = {".yaml", ".yml", ".json"}
SPEC_DIRS = ("openapi", "docs/contracts")
BASELINE = ROOT / ".oasdiff.err-ignore"


def specs() -> list[pathlib.Path]:
    found = []
    for dirname in SPEC_DIRS:
        d = ROOT / dirname
        if d.is_dir():
            found.extend(p for p in sorted(d.rglob("*")) if p.suffix in SPEC_SUFFIXES)
    return found


def active_baseline_lines() -> list[str]:
    if not BASELINE.is_file():
        return []
    return [l.strip() for l in BASELINE.read_text().splitlines()
            if l.strip() and not l.strip().startswith("#")]


def pick_pair(found: list[pathlib.Path]) -> tuple[pathlib.Path, pathlib.Path]:
    names = {p.name.lower(): p for p in found}
    base = next((p for n, p in names.items() if "base" in n), None)
    rev = next((p for n, p in names.items() if "revision" in n or "rev" in n), None)
    if base is not None and rev is not None and base != rev:
        return base, rev
    if len(found) == 2:
        return found[0], found[1]
    if len(found) == 1:
        rel = found[0].relative_to(ROOT).as_posix()
        head = subprocess.run(["git", "show", f"HEAD:{rel}"],
                              capture_output=True, cwd=ROOT)
        if head.returncode != 0:
            print(f"contract: FAIL — {rel} is unversioned with no base to diff;"
                  " add an openapi/base.yaml + revision pair or commit it first")
            sys.exit(1)
        tmp = pathlib.Path("/tmp/opencode-contract-base.yaml")
        tmp.write_bytes(head.stdout)
        return tmp, found[0]
    print("contract: FAIL — ambiguous spec set (need a base+revision pair);"
          f" found: {', '.join(str(p.relative_to(ROOT)) for p in found)}")
    sys.exit(1)


def run_breaking(base: pathlib.Path, rev: pathlib.Path) -> subprocess.CompletedProcess:
    cmd = ["oasdiff", "breaking", "--fail-on", "ERR",
           "--err-ignore", str(BASELINE), str(base), str(rev)]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)


def main() -> int:
    found = specs()
    if not found:
        print("contract: N/A absent (no versioned contract; nothing to check)")
        return 0
    if shutil.which("oasdiff") is None:
        print("contract: FAIL — spec files present but oasdiff is not installed;"
              " cannot verify compatibility")
        return 1
    if not BASELINE.is_file():
        print(f"contract: FAIL — {BASELINE.name} baseline missing;"
              " create it (may be comments-only) so ignores stay explicit")
        return 1
    base, rev = pick_pair(found)
    ignored = run_breaking(base, rev)
    if ignored.returncode != 0:
        out = (ignored.stdout or "") + (ignored.stderr or "")

        def rel(p: pathlib.Path) -> str:
            try:
                return str(p.relative_to(ROOT))
            except ValueError:
                return str(p)

        print(f"contract: FAIL — breaking ERR {rel(base)} -> {rel(rev)} (--fail-on ERR):\n{out.strip()}")
        return 1
    active = active_baseline_lines()
    if active:
        raw = subprocess.run(["oasdiff", "breaking", "-f", "singleline",
                              str(base), str(rev)],
                             capture_output=True, text=True, cwd=ROOT)
        lines = [l for l in (raw.stdout or "").splitlines()
                 if re.match(r"^(error|warning)\b", l.strip())]
        if not lines:
            print(f"contract: FAIL — baseline {BASELINE.name} is stale"
                  f" ({len(active)} entr{'y' if len(active) == 1 else 'ies'}"
                  " match nothing); resolve by emptying it")
            return 1
        print(f"contract: ok (no unignored ERR;"
              f" {len(active)} baseline entr{'y' if len(active) == 1 else 'ies'}"
              " applied — resolve them)")
        return 0
    print(f"contract: ok (no breaking ERR"
          f" {base.name} -> {rev.name}; baseline empty)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
