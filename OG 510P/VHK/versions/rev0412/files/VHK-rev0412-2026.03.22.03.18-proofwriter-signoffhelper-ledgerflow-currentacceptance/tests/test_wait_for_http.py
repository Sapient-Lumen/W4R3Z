from __future__ import annotations

import json
import threading
import time
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))
    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def _serve():
    state = {"flaky": 0, "json": 0}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            parts = urlsplit(self.path)
            if parts.path == "/flaky":
                state["flaky"] += 1
                if state["flaky"] == 1:
                    data = b"not yet"
                    self.send_response(503)
                    # Use an integer Retry-After to exercise parsing.
                    self.send_header("Retry-After", "1")
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                data = b"ready"
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

            if parts.path == "/json":
                state["json"] += 1
                payload = {"ready": state["json"] >= 2}
                data = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

            if parts.path == "/file":
                data = b"hello-download"
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"not found")

        def log_message(self, format, *args):  # noqa: A003
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_wait_for_http_respects_retry_after_and_condition(tmp_path: Path):
    server, thread = _serve()
    base = f"http://127.0.0.1:{server.server_port}"
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForHttp",
                        "method": "GET",
                        "url": base + "/flaky",
                        "timeout_ms": 4000,
                        "poll_ms": 10,
                        "max_poll_ms": 50,
                        "jitter_ms": 0,
                        "text_contains": "ready",
                        "respect_retry_after": True,
                        "out_attempts": "attempts",
                        "out_elapsed_ms": "elapsed_ms",
                    }
                ],
            }
        },
    )
    try:
        res = Runner(load_project(proj)).run("m")
    finally:
        server.shutdown()
        thread.join(timeout=1)

    assert res.ok
    assert res.vars["http_status"] == 200
    assert res.vars["attempts"] >= 2
    # Retry-After=1 should force at least ~1s between the first and second attempt.
    assert int(res.vars["elapsed_ms"]) >= 800


def test_wait_for_http_json_condition(tmp_path: Path):
    server, thread = _serve()
    base = f"http://127.0.0.1:{server.server_port}"
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForHttp",
                        "method": "GET",
                        "url": base + "/json",
                        "timeout_ms": 2000,
                        "poll_ms": 10,
                        "max_poll_ms": 50,
                        "jitter_ms": 0,
                        # condition uses http_json to ensure JSON parsing happens during wait
                        "condition": "http_json['ready'] == true",
                        "out_json": "resp_json",
                    }
                ],
            }
        },
    )
    try:
        res = Runner(load_project(proj)).run("m")
    finally:
        server.shutdown()
        thread.join(timeout=1)

    assert res.ok
    assert res.vars["http_status"] == 200
    assert res.vars["resp_json"]["ready"] is True


def test_download_file_atomic_and_sha256(tmp_path: Path):
    server, thread = _serve()
    base = f"http://127.0.0.1:{server.server_port}"
    sha = hashlib.sha256(b"hello-download").hexdigest()

    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml", "bad": "macros/bad.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "DownloadFile",
                        "url": base + "/file",
                        "path": "out.bin",
                        "atomic": True,
                        "tmp_suffix": ".tmp",
                        "sha256": sha,
                        "out_path": "p",
                    }
                ],
            },
            "bad": {
                "name": "bad",
                "steps": [
                    {
                        "type": "DownloadFile",
                        "url": base + "/file",
                        "path": "out_bad.bin",
                        "atomic": True,
                        "sha256": "00" * 32,
                    }
                ],
            },
        },
    )
    try:
        runner = Runner(load_project(proj))
        res = runner.run("m")
        bad = runner.run("bad")
    finally:
        server.shutdown()
        thread.join(timeout=1)

    assert res.ok
    out = Path(res.vars["p"])
    assert out.read_bytes() == b"hello-download"
    assert not out.with_name(out.name + ".tmp").exists()

    assert not bad.ok
    assert "SHA256 mismatch" in (bad.error or "")
