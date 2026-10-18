"""Integration: exercise the real HTTP probes against a live server subprocess (stdlib only)."""

import contextlib
import os
import pathlib
import socket
import subprocess
import sys
import time
import unittest
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _free_port() -> int:
    with contextlib.closing(socket.socket()) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _get(base: str, path: str, timeout: float = 2.0) -> int:
    with urllib.request.urlopen(base + path, timeout=timeout) as resp:  # noqa: S310 — test-only localhost probe
        return resp.status


def _get_code(base: str, path: str) -> int:
    try:
        return _get(base, path)
    except urllib.error.HTTPError as exc:
        return exc.code


@contextlib.contextmanager
def _run_local(timeout: float = 20.0):
    port = _free_port()
    env = {**os.environ, "PORT": str(port), "TRACE_ID": "e2e", "SPAN_ID": "e2e"}
    proc = subprocess.Popen(
        [sys.executable, "-m", "src.app"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        base = f"http://127.0.0.1:{port}"
        deadline = time.time() + timeout
        while time.time() < deadline:
            if proc.poll() is not None:
                raise AssertionError("service exited before answering probes")
            try:
                if _get_code(base, "/livez") == 200:
                    break
            except OSError:
                time.sleep(0.2)
        else:
            raise AssertionError("/livez did not answer 200 in time")
        yield base
    finally:
        proc.terminate()
        proc.wait(timeout=10)


class ProbeIntegrationTests(unittest.TestCase):
    def test_probes_end_to_end(self) -> None:
        with _run_local() as base:
            self.assertEqual(_get_code(base, "/livez"), 200)
            self.assertEqual(_get_code(base, "/readyz"), 200)
            self.assertEqual(_get_code(base, "/no-such-route"), 404)


if __name__ == "__main__":
    unittest.main()
