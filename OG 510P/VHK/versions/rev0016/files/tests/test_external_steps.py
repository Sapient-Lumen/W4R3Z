from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)
    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))
    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        parts = urlsplit(self.path)
        if parts.path == "/api":
            payload = {"ok": True, "q": parse_qs(parts.query).get("q", [""])[0]}
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


def _serve():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_http_request_and_download_file(tmp_path: Path):
    server, thread = _serve()
    base = f"http://127.0.0.1:{server.server_port}"
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {"type": "SetVar", "name": "q", "value": "ada"},
                    {
                        "type": "HttpRequest",
                        "method": "GET",
                        "url": base + "/api",
                        "params": {"q": "${q}"},
                        "out_json": "resp_json",
                    },
                    {
                        "type": "HttpRequest",
                        "method": "GET",
                        "url": base + "/missing",
                        "allow_error_status": True,
                        "out_text": "missing_text",
                        "out_status": "missing_status",
                    },
                    {"type": "DownloadFile", "url": base + "/file", "path": "data/out.bin"},
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
    assert res.vars["resp_json"]["q"] == "ada"
    assert res.vars["missing_status"] == 404
    assert "not found" in res.vars["missing_text"]
    out = Path(res.vars["download_path"])
    assert out.read_bytes() == b"hello-download"
    assert res.vars["download_bytes"] == len(b"hello-download")


def test_open_url_compose_email_paste_and_wait_for_new_file(tmp_path: Path, monkeypatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {"type": "OpenUrl", "url": "https://example.com/?q=${name}"},
                    {
                        "type": "ComposeEmail",
                        "to": ["a@example.com", "b@example.com"],
                        "cc": "c@example.com",
                        "subject": "Hello ${name}",
                        "body": "Body ${name}",
                    },
                    {"type": "PasteClipboard", "selection": "primary"},
                    {"type": "WaitForNewFile", "directory": "data", "pattern": "*.txt", "timeout_ms": 500, "poll_ms": 10, "max_poll_ms": 20, "jitter_ms": 0},
                ],
            }
        },
    )

    import vhk.core.runner as runner_mod

    calls = []
    monkeypatch.setattr(runner_mod.openers_mod, "open_target", lambda target: calls.append(("open", target)))
    monkeypatch.setattr(runner_mod.openers_mod, "compose_email", lambda *args, **kwargs: calls.append(("email", args, kwargs)))
    monkeypatch.setattr(runner_mod.input_mod, "paste", lambda **kwargs: calls.append(("paste", kwargs)))

    data_dir = proj / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    def create_file():
        time.sleep(0.03)
        (data_dir / "new.txt").write_text("hello")

    t = threading.Thread(target=create_file, daemon=True)
    t.start()
    res = Runner(load_project(proj)).run("m", initial_vars={"name": "Ada"})
    t.join(timeout=1)

    assert res.ok
    assert calls[0] == ("open", "https://example.com/?q=Ada")
    assert calls[1][0] == "email"
    assert calls[1][1][0] == ["a@example.com", "b@example.com"]
    assert calls[1][2]["subject"] == "Hello Ada"
    assert calls[2] == ("paste", {"selection": "primary", "clearmodifiers": False})
    assert Path(res.vars["new_file_path"]).name == "new.txt"
    assert res.vars["new_file_name"] == "new.txt"
    assert res.vars["new_file_size"] == 5
