"""End-to-end — probe the real target, local or compose.

Why this script exists:
  CI cannot test without test code. This IS the e2e test:

  - E2E_BASE_URL set → probe that stack (compose).
  - Unset → start src.app locally on an ephemeral port and probe it.
  - /livez and /readyz must be 200, unknown route must be 404.
  - Anything else → FAIL with the probe error.
"""
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
