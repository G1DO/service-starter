"""Minimal service: liveness/readiness with correct probe semantics + structured JSON logs."""

import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

SERVICE = "service-starter"

REDACTED = "***REDACTED***"
REDACT_KEYS = frozenset({
    "password", "passwd", "secret", "client_secret", "token",
    "access_token", "refresh_token", "api_key", "apikey",
    "authorization", "cookie", "set-cookie",
})


def _redact(value: object, key: object = None) -> object:
    if isinstance(key, str) and key.lower() in REDACT_KEYS:
        return REDACTED
    if isinstance(value, dict):
        return {k: _redact(v, k) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact(v) for v in value]
    return value


def log(event: str, **fields: object) -> None:
    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "level": "info",
        "service": SERVICE,
        "message": event,
        "trace_id": os.environ.get("TRACE_ID", "none"),
        "span_id": os.environ.get("SPAN_ID", "none"),
    }
    record.update({k: _redact(v, k) for k, v in fields.items()})
    sys.stdout.write(json.dumps(record) + "\n")


READY = {"db": True}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes = b"ok") -> None:
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/livez":
            # Liveness: cheap, no dependency checks.
            self._send(200)
        elif self.path == "/readyz":
            # Readiness: includes dependency checks.
            if all(READY.values()):
                self._send(200)
            else:
                self._send(503, b"not ready")
        else:
            self._send(404, b"not found")

    def log_message(self, fmt: str, *args: object) -> None:
        log("http_request", path=self.path, status=fmt % args)


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    log("startup", port=port)
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
