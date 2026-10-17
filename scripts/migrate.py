"""Migration gate: N/A-absent while no migration files exist.

Fails loudly the moment migration files land without a wired runner,
so the Schema-compat trigger cannot be silently skipped.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MIGRATION_SUFFIXES = {".sql", ".py"}
IGNORE = {"__init__.py", "README.md"}


def main() -> int:
    d = ROOT / "migrations"
    files = [p for p in d.glob("*") if p.suffix in MIGRATION_SUFFIXES and p.name not in IGNORE] \
        if d.is_dir() else []
    if not files:
        print("migrate: N/A absent (no migration files; nothing to apply)")
        return 0
    print("migrate: FAIL — migration files present but no runner wired"
          f" ({', '.join(p.name for p in files)}); wire expand-contract runner first")
    return 1


if __name__ == "__main__":
    sys.exit(main())
