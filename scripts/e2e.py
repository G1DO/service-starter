"""End-to-end: probe the real target. Against compose set E2E_BASE_URL, else local."""
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from probe import check_probes, run_local


def main() -> int:
    base = os.environ.get("E2E_BASE_URL")
    try:
        if base:
            check_probes(base)
            print(f"e2e: ok (probes green against {base})")
        else:
            with run_local() as local_base:
                check_probes(local_base)
            print("e2e: ok (probes green against local server)")
        return 0
    except (AssertionError, OSError) as exc:
        print(f"e2e: FAIL — {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
