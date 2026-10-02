#!/usr/bin/env python3
"""Bounded numeric SOCKS5-over-SOCKS interposer for adversarial route tests.

This laboratory process is not a privacy network. It accepts only allowlisted
numeric CONNECT requests, forwards them through one numeric upstream SOCKS5
endpoint, and can hold established relay bytes while keeping both TCP sides
open. The host-owned hold file is a test fault, never production policy.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import selectors
import signal
import socket
import sys
import threading
import time
from pathlib import Path


FORWARDER_PATH = Path(__file__).with_name("run-socks5-forwarder.py")
SPEC = importlib.util.spec_from_file_location("iotox_socks5_forwarder", FORWARDER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load the frozen SOCKS5 forwarder")
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)


def consume_reply(stream: socket.socket) -> int:
    version, code, reserved, address_type = BASE.receive_exact(stream, 4)
    if version != 5 or reserved != 0:
        raise ConnectionError("upstream returned an invalid SOCKS5 reply")
    if address_type == 1:
        BASE.receive_exact(stream, 4)
    elif address_type == 4:
        BASE.receive_exact(stream, 16)
    elif address_type == 3:
        length = BASE.receive_exact(stream, 1)[0]
        BASE.receive_exact(stream, length)
    else:
        raise ConnectionError("upstream returned an invalid address type")
    BASE.receive_exact(stream, 2)
    return code


def connect_upstream(
    endpoint: tuple[str, int], target: tuple[str, int]
) -> socket.socket:
    stream = socket.create_connection(endpoint, timeout=10.0)
    try:
        stream.sendall(b"\x05\x01\x00")
        if BASE.receive_exact(stream, 2) != b"\x05\x00":
            raise ConnectionError("upstream rejected no-authentication SOCKS5")
        address = socket.inet_pton(
            socket.AF_INET6 if ":" in target[0] else socket.AF_INET,
            target[0],
        )
        address_type = 4 if ":" in target[0] else 1
        stream.sendall(
            bytes((5, 1, 0, address_type))
            + address
            + target[1].to_bytes(2, "big")
        )
        if consume_reply(stream) != 0:
            raise ConnectionError("upstream refused the numeric target")
        return stream
    except Exception:
        stream.close()
        raise


class State(BASE.State):
    def __init__(
        self,
        allowed: set[tuple[str, int]],
        audit: Path | None,
        upstream: tuple[str, int],
        hold_file: Path,
    ) -> None:
        super().__init__(allowed, audit)
        self.upstream = upstream
        self.hold_file = hold_file

    def held(self) -> bool:
        return self.hold_file.is_file()

    def record_hold(self) -> None:
        if self.audit is None:
            return
        record = {
            "event": "relay-hold",
            "monotonic_ns": time.monotonic_ns(),
            "outcome": "held",
        }
        with self.lock:
            with self.audit.open("a", encoding="ascii") as output:
                output.write(
                    json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
                )

    def record_chain(
        self,
        target: tuple[str, int],
        client_source: tuple[object, ...],
        upstream: socket.socket,
    ) -> None:
        if self.audit is None:
            return

        def endpoint(value: tuple[object, ...]) -> str:
            host = str(value[0])
            port = int(value[1])
            return f"[{host}]:{port}" if ":" in host else f"{host}:{port}"

        record = {
            "client_source": endpoint(client_source),
            "event": "socks5-chain",
            "monotonic_ns": time.monotonic_ns(),
            "outcome": "admitted-chain",
            "target": endpoint(target),
            "upstream_destination": endpoint(upstream.getpeername()),
            "upstream_source": endpoint(upstream.getsockname()),
        }
        with self.lock:
            with self.audit.open("a", encoding="ascii") as output:
                output.write(
                    json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
                )


def relay(left: socket.socket, right: socket.socket, state: State) -> None:
    selector = selectors.DefaultSelector()
    selector.register(left, selectors.EVENT_READ, right)
    selector.register(right, selectors.EVENT_READ, left)
    hold_recorded = False
    try:
        while True:
            if state.held():
                if not hold_recorded:
                    state.record_hold()
                    hold_recorded = True
                time.sleep(0.01)
                continue
            hold_recorded = False
            ready = selector.select(timeout=0.1)
            for key, _ in ready:
                if state.held():
                    break
                source = key.fileobj
                destination = key.data
                data = source.recv(BASE.BUFFER_BYTES)
                if not data:
                    return
                destination.sendall(data)
    finally:
        selector.close()


class Handler(BASE.Handler):
    server: "Interposer"

    def handle(self) -> None:
        if not self.server.state.enter():
            return
        try:
            self.request.settimeout(10.0)
            version, method_count = BASE.receive_exact(self.request, 2)
            if version != 5 or method_count == 0 or method_count > BASE.MAX_GREETING_METHODS:
                return
            methods = BASE.receive_exact(self.request, method_count)
            if 0 not in methods:
                self.request.sendall(b"\x05\xff")
                return
            self.request.sendall(b"\x05\x00")
            version, command, reserved, address_type = BASE.receive_exact(self.request, 4)
            if version != 5 or command != 1 or reserved != 0:
                self.request.sendall(BASE.socks_reply(7))
                return
            if address_type == 1:
                host = socket.inet_ntop(socket.AF_INET, BASE.receive_exact(self.request, 4))
            elif address_type == 4:
                host = socket.inet_ntop(socket.AF_INET6, BASE.receive_exact(self.request, 16))
            else:
                self.request.sendall(BASE.socks_reply(8))
                self.server.state.record("denied-address-type", "0.0.0.0", 0)
                return
            port = int.from_bytes(BASE.receive_exact(self.request, 2), "big")
            target = (host, port)
            if target not in self.server.state.allowed:
                self.request.sendall(BASE.socks_reply(2, address_type == 4))
                self.server.state.record("denied-target", host, port)
                return
            try:
                upstream = connect_upstream(self.server.state.upstream, target)
            except (ConnectionError, OSError):
                self.request.sendall(BASE.socks_reply(5, address_type == 4))
                self.server.state.record("denied-upstream", host, port)
                return
            with upstream:
                self.server.state.record("admitted", host, port)
                self.server.state.record_chain(target, self.client_address, upstream)
                self.request.sendall(BASE.socks_reply(0, address_type == 4))
                self.request.settimeout(None)
                upstream.settimeout(None)
                relay(self.request, upstream, self.server.state)
        except (ConnectionError, OSError, ValueError):
            return
        finally:
            self.server.state.leave()


class Interposer(BASE.Forwarder):
    def __init__(self, address: tuple[str, int], state: State) -> None:
        family = socket.AF_INET6 if ":" in address[0] else socket.AF_INET
        self.address_family = family
        self.state = state
        BASE.socketserver.TCPServer.__init__(self, address, Handler, bind_and_activate=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listen", required=True, type=BASE.parse_listen_endpoint)
    parser.add_argument("--allow-target", required=True, action="append", type=BASE.parse_endpoint)
    parser.add_argument("--upstream-socks", required=True, type=BASE.parse_endpoint)
    parser.add_argument("--hold-file", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    arguments = parser.parse_args()
    allowed = set(arguments.allow_target)
    if len(allowed) != len(arguments.allow_target):
        parser.error("duplicate --allow-target")
    arguments.audit.parent.mkdir(parents=True, exist_ok=True)
    arguments.audit.write_text("", encoding="ascii")
    if arguments.hold_file.exists():
        parser.error("hold file must be absent at startup")
    state = State(allowed, arguments.audit, arguments.upstream_socks, arguments.hold_file)
    with Interposer(arguments.listen, state) as server:
        stop = threading.Event()

        def request_stop(_signum: int, _frame: object) -> None:
            stop.set()
            threading.Thread(target=server.shutdown, daemon=True).start()

        signal.signal(signal.SIGINT, request_stop)
        signal.signal(signal.SIGTERM, request_stop)
        host, port = server.server_address[:2]
        print(f"ready={host}:{port}", flush=True)
        server.serve_forever(poll_interval=0.1)
        stop.set()
    with state.lock:
        print(
            "admitted={} denied={} peak-active={}".format(
                state.counters.admitted,
                state.counters.denied,
                state.counters.peak_active,
            ),
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
