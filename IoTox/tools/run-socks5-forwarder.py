#!/usr/bin/env python3
"""Bounded numeric-only SOCKS5 forwarder for IoTox route qualification.

This is laboratory plumbing, not a privacy network. It proves that c-toxcore
uses the configured SOCKS5 boundary and gives packet-capture gates one small,
auditable forwarding process. It deliberately has no authentication, DNS,
UDP ASSOCIATE, BIND, wildcard target policy, or daemon mode.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import selectors
import signal
import socket
import socketserver
import threading
import time
from dataclasses import dataclass
from pathlib import Path


MAX_GREETING_METHODS = 32
MAX_CONNECTIONS = 256
BUFFER_BYTES = 64 * 1024


def parse_endpoint(text: str, *, allow_zero: bool = False) -> tuple[str, int]:
    if text.startswith("["):
        closing = text.find("]")
        if closing <= 1 or closing + 1 >= len(text) or text[closing + 1] != ":":
            raise argparse.ArgumentTypeError("endpoint must use [IPv6]:PORT")
        host = text[1:closing]
        port_text = text[closing + 2 :]
    else:
        if text.count(":") != 1:
            raise argparse.ArgumentTypeError("endpoint must use IPv4:PORT or [IPv6]:PORT")
        host, port_text = text.split(":", 1)
    try:
        address = ipaddress.ip_address(host)
    except ValueError as error:
        raise argparse.ArgumentTypeError("endpoint host must be numeric") from error
    if not port_text.isascii() or not port_text.isdecimal():
        raise argparse.ArgumentTypeError("endpoint port must be decimal")
    port = int(port_text, 10)
    minimum = 0 if allow_zero else 1
    if port < minimum or port > 65535:
        raise argparse.ArgumentTypeError(
            f"endpoint port must be in {minimum}..65535"
        )
    return str(address), port


def parse_listen_endpoint(text: str) -> tuple[str, int]:
    return parse_endpoint(text, allow_zero=True)


def receive_exact(stream: socket.socket, size: int) -> bytes:
    output = bytearray()
    while len(output) < size:
        chunk = stream.recv(size - len(output))
        if not chunk:
            raise ConnectionError("peer closed a partial SOCKS5 record")
        output.extend(chunk)
    return bytes(output)


def socks_reply(code: int, ipv6: bool = False) -> bytes:
    if ipv6:
        return bytes((5, code, 0, 4)) + bytes(16) + bytes(2)
    return bytes((5, code, 0, 1)) + bytes(4) + bytes(2)


@dataclass
class Counters:
    admitted: int = 0
    denied: int = 0
    active: int = 0
    peak_active: int = 0


class State:
    def __init__(self, allowed: set[tuple[str, int]], audit: Path | None) -> None:
        self.allowed = allowed
        self.audit = audit
        self.lock = threading.Lock()
        self.counters = Counters()

    def record(self, outcome: str, host: str, port: int) -> None:
        with self.lock:
            if outcome == "admitted":
                self.counters.admitted += 1
            else:
                self.counters.denied += 1
            if self.audit is not None:
                record = {
                    "event": "socks5-connect",
                    "monotonic_ns": time.monotonic_ns(),
                    "outcome": outcome,
                    "target": f"[{host}]:{port}" if ":" in host else f"{host}:{port}",
                }
                with self.audit.open("a", encoding="ascii") as output:
                    output.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")

    def enter(self) -> bool:
        with self.lock:
            if self.counters.active >= MAX_CONNECTIONS:
                return False
            self.counters.active += 1
            self.counters.peak_active = max(
                self.counters.peak_active, self.counters.active
            )
            return True

    def leave(self) -> None:
        with self.lock:
            self.counters.active -= 1


class Handler(socketserver.BaseRequestHandler):
    server: "Forwarder"

    def handle(self) -> None:
        if not self.server.state.enter():
            return
        try:
            self.request.settimeout(10.0)
            version, method_count = receive_exact(self.request, 2)
            if version != 5 or method_count == 0 or method_count > MAX_GREETING_METHODS:
                return
            methods = receive_exact(self.request, method_count)
            if 0 not in methods:
                self.request.sendall(b"\x05\xff")
                return
            self.request.sendall(b"\x05\x00")
            version, command, reserved, address_type = receive_exact(self.request, 4)
            if version != 5 or command != 1 or reserved != 0:
                self.request.sendall(socks_reply(7))
                return
            if address_type == 1:
                packed = receive_exact(self.request, 4)
                host = str(ipaddress.ip_address(packed))
            elif address_type == 4:
                packed = receive_exact(self.request, 16)
                host = str(ipaddress.ip_address(packed))
            else:
                # Refuse domain-name ATYP as a positive native-DNS containment
                # assertion, even if a future caller tries to use it.
                self.request.sendall(socks_reply(8))
                self.server.state.record("denied-address-type", "0.0.0.0", 0)
                return
            port = int.from_bytes(receive_exact(self.request, 2), "big")
            target = (host, port)
            if target not in self.server.state.allowed:
                self.request.sendall(socks_reply(2, address_type == 4))
                self.server.state.record("denied-target", host, port)
                return
            try:
                upstream = socket.create_connection(target, timeout=10.0)
            except OSError:
                self.request.sendall(socks_reply(5, address_type == 4))
                self.server.state.record("denied-connect", host, port)
                return
            with upstream:
                self.server.state.record("admitted", host, port)
                self.request.sendall(socks_reply(0, address_type == 4))
                self.request.settimeout(None)
                upstream.settimeout(None)
                relay(self.request, upstream)
        except (ConnectionError, OSError, ValueError):
            return
        finally:
            self.server.state.leave()


def relay(left: socket.socket, right: socket.socket) -> None:
    selector = selectors.DefaultSelector()
    selector.register(left, selectors.EVENT_READ, right)
    selector.register(right, selectors.EVENT_READ, left)
    try:
        while True:
            ready = selector.select(timeout=30.0)
            if not ready:
                continue
            for key, _ in ready:
                source = key.fileobj
                destination = key.data
                data = source.recv(BUFFER_BYTES)
                if not data:
                    return
                destination.sendall(data)
    finally:
        selector.close()


class Forwarder(socketserver.ThreadingMixIn, socketserver.TCPServer):
    # Route-fault qualification restarts the same explicit proxy endpoint.
    # The kernel may retain the previous accepted stream in TIME_WAIT; reuse
    # permits the intended same-address restart but cannot steal a live bind.
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address: tuple[str, int], state: State) -> None:
        family = socket.AF_INET6 if ":" in address[0] else socket.AF_INET
        self.address_family = family
        self.state = state
        super().__init__(address, Handler, bind_and_activate=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listen", required=True, type=parse_listen_endpoint)
    parser.add_argument(
        "--allow-target", required=True, action="append", type=parse_endpoint
    )
    parser.add_argument("--audit", type=Path)
    arguments = parser.parse_args()
    allowed = set(arguments.allow_target)
    if len(allowed) != len(arguments.allow_target):
        parser.error("duplicate --allow-target")
    if arguments.audit is not None:
        arguments.audit.parent.mkdir(parents=True, exist_ok=True)
        arguments.audit.write_text("", encoding="ascii")
    state = State(allowed, arguments.audit)
    with Forwarder(arguments.listen, state) as server:
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
