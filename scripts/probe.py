"""Probe helpers — shared by e2e and integration (stdlib only).

Why this file exists:
  Both `scripts/e2e.py` and `tests/integration/test_smoke.py` need the
  same three checks against a live base URL. This holds them once:

  - free_port() → an ephemeral 127.0.0.1 port for local runs.
  - get() → GET base+path, returning HTTPError codes instead of raising.
  - check_probes() → /livez 200, /readyz 200, unknown route 404.
  - run_local() → start `src.app` as a subprocess, wait for /livez,
    yield the base URL, then terminate.
"""
import contextlib
import os
import pathlib
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]


def free_port() -> int:
    with contextlib.closing(socket.socket()) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def get(base: str, path: str, timeout: float = 2.0) -> int:
    try:
        # Test-only probe helper; base is a localhost ephemeral URL or an explicit E2E target, never attacker-controlled.
        with urllib.request.urlopen(base + path, timeout=timeout) as resp:  # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code


def check_probes(base: str) -> None:
    live = get(base, "/livez")
    if live != 200:
        raise AssertionError(f"/livez returned {live}, want 200")
    ready = get(base, "/readyz")
    if ready != 200:
        raise AssertionError(f"/readyz returned {ready}, want 200")
    missing = get(base, "/no-such-route")
    if missing != 404:
        raise AssertionError(f"unknown route returned {missing}, want 404")


@contextlib.contextmanager
def run_local(timeout: float = 20.0):
    """Start the service as a subprocess on an ephemeral port; yield its base URL."""
    port = free_port()
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
                if get(base, "/livez", timeout=1.0) == 200:
                    break
            except OSError:
                time.sleep(0.2)
        else:
            raise AssertionError("/livez did not answer 200 in time")
        yield base
    finally:
        proc.terminate()
        proc.wait(timeout=10)
