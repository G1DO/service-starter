"""Unit tests: probe semantics + log redaction guard."""

import json
import unittest

import src.app as app


class ProbeTests(unittest.TestCase):
    def test_liveness_has_no_deps(self) -> None:
        # /livez must not consult READY — signature check: Handler.do_GET
        # handles /livez before touching READY.
        import inspect

        src = inspect.getsource(app.Handler.do_GET)
        self.assertLess(src.index("/livez"), src.index("READY"))

    def test_log_record_shape(self) -> None:
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            app.log("hello")
        record = json.loads(buf.getvalue())
        for key in ("timestamp", "level", "service", "message", "trace_id", "span_id"):
            self.assertIn(key, record)

    def test_no_secret_keys_in_logs(self) -> None:
        import inspect

        src = inspect.getsource(app.log)
        for banned in ("password", "secret", "api_key", "token"):
            self.assertNotIn(banned, src.lower())


if __name__ == "__main__":
    unittest.main()
