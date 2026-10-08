import json
import socket
import threading
import urllib.request
from pathlib import Path

import pytest

from vhk.system.httpd import HttpdConfig, make_http_server


def _start_server(cfg: HttpdConfig):
    srv = make_http_server(cfg)
    th = threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    th.start()
    host, port = srv.server_address
    return srv, th, f"http://{host}:{port}"


def _post(url: str, path: str, body: bytes, headers: dict[str, str] | None = None):
    req = urllib.request.Request(url + path, data=body, method="POST")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    return urllib.request.urlopen(req, timeout=2.0)


def test_httpd_emit(tmp_path: Path):
    bus = tmp_path / "bus.sock"
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    s.bind(str(bus))
    s.settimeout(2.0)

    srv, th, base = _start_server(HttpdConfig(host="127.0.0.1", port=0, bus_socket=str(bus)))

    try:
        payload = json.dumps({"event": "ping", "data": {"n": 1}}).encode("utf-8")
        with _post(base, "/emit", payload, {"Content-Type": "application/json"}) as resp:
            assert resp.status == 200

        raw = s.recv(65535)
        obj = json.loads(raw.decode("utf-8"))
        assert obj["name"] == "ping"
        assert obj["data"] == {"n": 1}
    finally:
        srv.shutdown()
        srv.server_close()
        s.close()


def test_httpd_dispatch(tmp_path: Path):
    bus = tmp_path / "bus.sock"
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    s.bind(str(bus))
    s.settimeout(2.0)

    srv, th, base = _start_server(HttpdConfig(host="127.0.0.1", port=0, bus_socket=str(bus), dispatch_event="hotkey"))

    try:
        payload = json.dumps({"vars": {"x": 1}, "binding": "deck.1"}).encode("utf-8")
        with _post(base, "/dispatch/hello", payload, {"Content-Type": "application/json"}) as resp:
            assert resp.status == 200

        raw = s.recv(65535)
        obj = json.loads(raw.decode("utf-8"))
        assert obj["name"] == "hotkey"
        assert obj["data"]["macro"] == "hello"
        assert obj["data"]["vars"] == {"x": 1}
        assert obj["data"]["binding"] == "deck.1"
    finally:
        srv.shutdown()
        srv.server_close()
        s.close()


def test_httpd_token_auth(tmp_path: Path):
    bus = tmp_path / "bus.sock"
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    s.bind(str(bus))
    s.settimeout(2.0)

    srv, th, base = _start_server(HttpdConfig(host="127.0.0.1", port=0, bus_socket=str(bus), token="sekret"))

    try:
        payload = json.dumps({"event": "ping"}).encode("utf-8")

        # Without token -> 401
        with pytest.raises(Exception):
            _post(base, "/emit", payload, {"Content-Type": "application/json"})

        # With token -> ok
        with _post(
            base,
            "/emit",
            payload,
            {"Content-Type": "application/json", "Authorization": "Bearer sekret"},
        ) as resp:
            assert resp.status == 200

        raw = s.recv(65535)
        obj = json.loads(raw.decode("utf-8"))
        assert obj["name"] == "ping"
    finally:
        srv.shutdown()
        srv.server_close()
        s.close()
