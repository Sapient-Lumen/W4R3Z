import json
import socket
import struct
import time
from pathlib import Path

import pytest

from vhk.system.osc import OscdConfig, encode_osc_message, iter_osc_packets, make_oscd_server


def _bundle(elem: bytes) -> bytes:
    # Minimal OSC bundle: '#bundle\0' + timetag(8 bytes) + [size + element]
    timetag = b"\x00" * 8
    return b"#bundle\x00" + timetag + struct.pack(">i", len(elem)) + elem


def test_iter_osc_packets_bundle_roundtrip():
    msg = encode_osc_message("/hello", [1, "x", True])
    pkt = _bundle(msg)

    out = list(iter_osc_packets(pkt))
    assert out == [("/hello", [1, "x", True])]


def test_oscd_emit_and_dispatch(tmp_path: Path):
    bus = tmp_path / "bus.sock"
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    s.bind(str(bus))
    s.settimeout(2.0)

    cfg = OscdConfig(host="127.0.0.1", port=0, bus_socket=str(bus), dispatch_event="hotkey")
    srv = make_oscd_server(cfg)

    try:
        host, port = srv.address

        th = __import__("threading").Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        th.start()
        time.sleep(0.05)

        u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # /vhk/emit
        pkt = encode_osc_message("/vhk/emit", ["ping", "{\"n\": 1}"])
        u.sendto(pkt, (host, port))

        raw = s.recv(65535)
        obj = json.loads(raw.decode("utf-8"))
        assert obj["name"] == "ping"
        assert obj["data"] == {"n": 1}

        # /vhk/dispatch/<macro>
        pkt = encode_osc_message("/vhk/dispatch/hello", ["{\"x\": 1}"])
        u.sendto(pkt, (host, port))

        raw = s.recv(65535)
        obj = json.loads(raw.decode("utf-8"))
        assert obj["name"] == "hotkey"
        assert obj["data"]["macro"] == "hello"
        assert obj["data"]["vars"] == {"x": 1}
        assert obj["data"]["source"] == "osc"

    finally:
        try:
            srv.shutdown()
        except Exception:
            pass
        try:
            srv.server_close()
        except Exception:
            pass
        s.close()


def test_oscd_token_gating(tmp_path: Path):
    bus = tmp_path / "bus.sock"
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    s.bind(str(bus))
    s.settimeout(0.25)

    cfg = OscdConfig(host="127.0.0.1", port=0, bus_socket=str(bus), token="sekret")
    srv = make_oscd_server(cfg)

    try:
        host, port = srv.address
        th = __import__("threading").Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        th.start()
        time.sleep(0.05)

        u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Missing token -> ignored
        pkt = encode_osc_message("/vhk/emit", ["ping", "{\"n\": 1}"])
        u.sendto(pkt, (host, port))
        with pytest.raises(socket.timeout):
            s.recv(65535)

        # Token as first arg -> accepted
        pkt = encode_osc_message("/vhk/emit", ["sekret", "ping", "{\"n\": 2}"])
        u.sendto(pkt, (host, port))
        raw = s.recv(65535)
        obj = json.loads(raw.decode("utf-8"))
        assert obj["name"] == "ping"
        assert obj["data"] == {"n": 2}

    finally:
        try:
            srv.shutdown()
        except Exception:
            pass
        try:
            srv.server_close()
        except Exception:
            pass
        s.close()
