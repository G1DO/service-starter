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

    def test_log_redacts_secret_values(self) -> None:
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            app.log(
                "login_attempt",
                username="alice",
                password="s3cr3t-value-9f8e",
                nested={"token": "tok-abc123-def456", "role": "admin"},
                tags=["a", "b"],
            )
        out = buf.getvalue()
        record = json.loads(out)
        self.assertNotIn("s3cr3t-value-9f8e", out)
        self.assertNotIn("tok-abc123-def456", out)
        self.assertEqual(record["password"], "***REDACTED***")
        self.assertEqual(record["nested"]["token"], "***REDACTED***")
        # Non-sensitive fields pass through untouched.
        self.assertEqual(record["username"], "alice")
        self.assertEqual(record["nested"]["role"], "admin")
        self.assertEqual(record["tags"], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
