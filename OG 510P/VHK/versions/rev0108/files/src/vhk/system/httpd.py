from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .event_bus import emit_bus_event


@dataclass
class HttpdConfig:
    """Configuration for the local HTTP control server."""

    host: str = "127.0.0.1"
    port: int = 39999
    token: str | None = None
    bus_socket: str = ""
    dispatch_event: str = "hotkey"


def _json_response(handler: BaseHTTPRequestHandler, code: int, payload: Any) -> None:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


class VhkHttpServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, addr: tuple[str, int], handler: type[BaseHTTPRequestHandler], cfg: HttpdConfig):
        super().__init__(addr, handler)
        self.cfg = cfg


class VhkHttpHandler(BaseHTTPRequestHandler):
    server: VhkHttpServer  # type: ignore[assignment]

    server_version = "VHKHttpd/0.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        # Avoid noisy stdout in tests/automation.
        return

    def _auth_ok(self) -> bool:
        tok = (self.server.cfg.token or "").strip()
        if not tok:
            return True

        hdr = (self.headers.get("Authorization") or "").strip()
        if hdr.lower().startswith("bearer "):
            got = hdr.split(" ", 1)[1].strip()
            return got == tok

        got2 = (self.headers.get("X-VHK-Token") or "").strip()
        return got2 == tok

    def _read_body(self) -> bytes:
        try:
            n = int(self.headers.get("Content-Length") or "0")
        except Exception:
            n = 0
        return self.rfile.read(n) if n > 0 else b""

    def _parse_body(self) -> tuple[Any | None, str]:
        raw = self._read_body()
        if not raw:
            return None, ""
        txt = raw.decode("utf-8", errors="replace")
        try:
            return json.loads(txt), txt
        except Exception:
            return None, txt

    def do_GET(self) -> None:
        if not self._auth_ok():
            _json_response(self, HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "unauthorized"})
            return

        if self.path.rstrip("/") == "/health":
            _json_response(self, HTTPStatus.OK, {"ok": True})
            return

        _json_response(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:
        if not self._auth_ok():
            _json_response(self, HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "unauthorized"})
            return

        obj, txt = self._parse_body()
        path = self.path

        if path.rstrip("/") == "/emit":
            if not isinstance(obj, dict):
                _json_response(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "expected_json_object"})
                return
            ev = str(obj.get("event") or "").strip()
            if not ev:
                _json_response(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_event"})
                return
            emit_bus_event(self.server.cfg.bus_socket, ev, obj.get("data"))
            _json_response(self, HTTPStatus.OK, {"ok": True, "event": ev})
            return

        if path.startswith("/bus/"):
            ev = path.split("/bus/", 1)[1].strip("/")
            if not ev:
                _json_response(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_event"})
                return
            data: Any = obj if obj is not None else txt
            emit_bus_event(self.server.cfg.bus_socket, ev, data)
            _json_response(self, HTTPStatus.OK, {"ok": True, "event": ev})
            return

        if path.startswith("/dispatch/"):
            macro = path.split("/dispatch/", 1)[1].strip("/")
            if not macro:
                _json_response(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_macro"})
                return

            payload: dict[str, Any] = {"macro": macro}
            if isinstance(obj, dict):
                for k in ("vars", "binding", "keys", "require_window"):
                    if k in obj:
                        payload[k] = obj[k]
            elif txt:
                payload["binding"] = txt

            emit_bus_event(self.server.cfg.bus_socket, self.server.cfg.dispatch_event, payload)
            _json_response(self, HTTPStatus.OK, {"ok": True, "event": self.server.cfg.dispatch_event, "macro": macro})
            return

        _json_response(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})


def make_http_server(cfg: HttpdConfig) -> VhkHttpServer:
    return VhkHttpServer((cfg.host, int(cfg.port)), VhkHttpHandler, cfg)


def serve_httpd(cfg: HttpdConfig, *, stop_event: threading.Event | None = None) -> None:
    """Run the local HTTP control server."""

    srv = make_http_server(cfg)

    if stop_event is None:
        srv.serve_forever(poll_interval=0.25)
        return

    # Serve in small steps so we can stop quickly.
    while not stop_event.is_set():
        srv.handle_request()

    try:
        srv.server_close()
    except Exception:
        pass
