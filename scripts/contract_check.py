"""Contract gate: N/A-absent while no versioned contract exists.

Fails loudly the moment spec files land without wired compatibility checks
(oasdiff breaking + response validation), so the Changes-a-versioned-contract
trigger cannot be silently skipped.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC_SUFFIXES = {".yaml", ".yml", ".json"}
SPEC_DIRS = ("openapi", "docs/contracts")


def main() -> int:
    specs = []
    for dirname in SPEC_DIRS:
        d = ROOT / dirname
        if d.is_dir():
            specs.extend(p for p in d.rglob("*") if p.suffix in SPEC_SUFFIXES)
    if not specs:
        print("contract: N/A absent (no versioned contract; nothing to check)")
        return 0
    print("contract: FAIL — spec files present but no compatibility check wired"
          f" ({', '.join(str(p.relative_to(ROOT)) for p in specs)});"
          " wire oasdiff breaking + response validation first")
    return 1


if __name__ == "__main__":
    sys.exit(main())
