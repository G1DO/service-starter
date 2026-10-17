"""Integration: exercise the real HTTP probes against a live server subprocess."""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))

from probe import check_probes, run_local


class ProbeIntegrationTests(unittest.TestCase):
    def test_probes_end_to_end(self) -> None:
        with run_local() as base:
            check_probes(base)


if __name__ == "__main__":
    unittest.main()
