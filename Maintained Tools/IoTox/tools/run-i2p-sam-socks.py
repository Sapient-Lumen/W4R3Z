#!/usr/bin/env python3
"""Strict numeric SOCKS5-to-I2P SAM v3.1 construction adapter.

This bounded laboratory process is not an I2P router and proves no anonymity.
It maps exact numeric Tox bootstrap/relay records to exact traditional
52-character b32 I2P destinations, creates one long-lived transient SAM STREAM
session, and fails closed whenever that session is unavailable.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import ipaddress
import json
import secrets
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

MAX_SAM_LINE_BYTES = 8192
B32_ALPHABET = frozenset("abcdefghijklmnopqrstuvwxyz234567")
HELLO = b"HELLO VERSION MIN=3.1 MAX=3.1\n"
SESSION_OPTIONS = (
    "STYLE=STREAM DESTINATION=TRANSIENT SIGNATURE_TYPE=7 "
    "i2cp.leaseSetEncType=4 inbound.quantity=2 outbound.quantity=2 "
    "i2p.streaming.profile=2"
)


class SamError(RuntimeError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise SamError(detail)


def parse_b32_destination(text: str) -> str:
    suffix = ".b32.i2p"
    require(
        text.endswith(suffix)
        and len(text) == 52 + len(suffix)
        and all(character in B32_ALPHABET for character in text[:52]),
        "I2P destination must be a canonical lowercase 52-character b32.i2p name",
    )
    return text


def parse_mapping(text: str) -> tuple[tuple[str, int], str]:
    target_text, separator, destination_text = text.rpartition("=")
    if separator != "=" or not target_text or not destination_text:
        raise argparse.ArgumentTypeError(
            "mapping must use NUMERIC_IP:PORT=52_CHARACTERS.b32.i2p"
        )
    try:
        target = BASE.parse_endpoint(target_text)
        destination = parse_b32_destination(destination_text)
    except (argparse.ArgumentTypeError, SamError) as error:
        raise argparse.ArgumentTypeError(str(error)) from error
    return target, destination


def open_numeric(endpoint: tuple[str, int], timeout: float) -> socket.socket:
    family = socket.AF_INET6 if ":" in endpoint[0] else socket.AF_INET
    stream = socket.socket(family, socket.SOCK_STREAM)
    stream.settimeout(timeout)
    try:
        stream.connect(endpoint)
    except Exception:
        stream.close()
        raise
    return stream


def receive_line(stream: socket.socket) -> str:
    value = bytearray()
    while len(value) <= MAX_SAM_LINE_BYTES:
        byte = stream.recv(1)
        if not byte:
            raise SamError("SAM closed a partial control line")
        if byte == b"\n":
            break
        require(byte != b"\r" and byte != b"\0", "SAM line is noncanonical")
        value.extend(byte)
    else:
        raise SamError("SAM control line exceeds the bound")
    try:
        return value.decode("ascii")
    except UnicodeDecodeError as error:
        raise SamError("SAM v3.1 line is not ASCII") from error


def parse_status(line: str, command: str, subcommand: str) -> dict[str, str]:
    fields = line.split(" ")
    require(
        len(fields) >= 3
        and fields[0] == command
        and fields[1] == subcommand
        and all(fields),
        f"SAM returned an invalid {command} {subcommand} line",
    )
    values: dict[str, str] = {}
    for field in fields[2:]:
        key, separator, value = field.partition("=")
        require(
            separator == "=" and key and value and key not in values,
            f"SAM returned an invalid {command} {subcommand} field",
        )
        values[key] = value
    return values


def negotiate(stream: socket.socket) -> None:
    stream.sendall(HELLO)
    reply = parse_status(receive_line(stream), "HELLO", "REPLY")
    require(
        reply.get("RESULT") == "OK" and reply.get("VERSION") == "3.1",
        "SAM did not negotiate exact version 3.1",
    )


def create_session(
    endpoint: tuple[str, int], session_id: str, command_timeout: float
) -> socket.socket:
    stream = open_numeric(endpoint, 10.0)
    try:
        negotiate(stream)
        stream.settimeout(command_timeout)
        stream.sendall(
            f"SESSION CREATE ID={session_id} {SESSION_OPTIONS}\n".encode("ascii")
        )
        reply = parse_status(receive_line(stream), "SESSION", "STATUS")
        require(
            reply.get("RESULT") == "OK" and bool(reply.get("DESTINATION")),
            "SAM refused the transient STREAM session",
        )
        stream.settimeout(0.5)
        return stream
    except Exception:
        stream.close()
        raise


def connect_stream(
    endpoint: tuple[str, int],
    session_id: str,
    destination: str,
    command_timeout: float,
) -> socket.socket:
    stream = open_numeric(endpoint, 10.0)
    try:
        negotiate(stream)
        stream.settimeout(command_timeout)
        stream.sendall(
            (
                f"STREAM CONNECT ID={session_id} DESTINATION={destination} "
                "SILENT=false\n"
            ).encode("ascii")
        )
        reply = parse_status(receive_line(stream), "STREAM", "STATUS")
        require(reply.get("RESULT") == "OK", "SAM refused the I2P stream")
        return stream
    except Exception:
        stream.close()
        raise


def relay(left: socket.socket, right: socket.socket) -> None:
    selector = selectors.DefaultSelector()
    selector.register(left, selectors.EVENT_READ, right)
    selector.register(right, selectors.EVENT_READ, left)
    try:
        while True:
            for key, _events in selector.select(timeout=30.0):
                source = key.fileobj
                destination = key.data
                data = source.recv(BASE.BUFFER_BYTES)
                if not data:
                    return
                destination.sendall(data)
    finally:
        selector.close()


class State(BASE.State):
    def __init__(
        self,
        mappings: dict[tuple[str, int], str],
        audit: Path,
        sam_endpoint: tuple[str, int],
        command_timeout: float,
    ) -> None:
        super().__init__(set(mappings), audit)
        self.mappings = mappings
        self.sam_endpoint = sam_endpoint
        self.command_timeout = command_timeout
        self.session_id = "iotox_" + secrets.token_hex(12)
        self.generation = 0
        self.session_ready = False
        self.control: socket.socket | None = None
        self.stopping = threading.Event()
        self.condition = threading.Condition(self.lock)
        self.losses = 0

    def _append_locked(self, record: dict[str, object]) -> None:
        with self.audit.open("a", encoding="ascii") as output:
            output.write(
                json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
            )

    def session_started(self, control: socket.socket) -> None:
        with self.condition:
            if self.stopping.is_set():
                control.close()
                return
            self.control = control
            self.generation += 1
            self.session_ready = True
            self._append_locked(
                {
                    "event": "sam-session",
                    "generation": self.generation,
                    "monotonic_ns": time.monotonic_ns(),
                    "outcome": "ready",
                }
            )
            self.condition.notify_all()

    def session_ended(self, control: socket.socket) -> None:
        with self.condition:
            if self.control is not control:
                return
            generation = self.generation
            self.control = None
            if self.session_ready:
                self.session_ready = False
                if not self.stopping.is_set():
                    self.losses += 1
                    self._append_locked(
                        {
                            "event": "sam-session",
                            "generation": generation,
                            "monotonic_ns": time.monotonic_ns(),
                            "outcome": "lost",
                        }
                    )
            self.condition.notify_all()

    def wait_ready(self, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        with self.condition:
            while not self.session_ready and not self.stopping.is_set():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                self.condition.wait(remaining)
            return self.session_ready

    def current_session(self) -> tuple[str, int] | None:
        with self.lock:
            if not self.session_ready:
                return None
            return self.session_id, self.generation

    def generation_ready(self, generation: int) -> bool:
        with self.lock:
            return self.session_ready and self.generation == generation

    def record_route(
        self,
        outcome: str,
        target: tuple[str, int],
        destination: str,
        generation: int,
        setup_us: int,
    ) -> None:
        host, port = target
        with self.lock:
            if outcome == "admitted":
                self.counters.admitted += 1
            else:
                self.counters.denied += 1
            self._append_locked(
                {
                    "destination_sha256": hashlib.sha256(
                        ("iotox-i2p-b32-v1\0" + destination).encode("ascii")
                    ).hexdigest(),
                    "event": "socks5-i2p-connect",
                    "generation": generation,
                    "monotonic_ns": time.monotonic_ns(),
                    "outcome": outcome,
                    "setup_us": setup_us,
                    "target": f"[{host}]:{port}" if ":" in host else f"{host}:{port}",
                }
            )

    def close(self) -> None:
        self.stopping.set()
        with self.condition:
            control = self.control
            self.condition.notify_all()
        if control is not None:
            try:
                control.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            control.close()


def supervise_session(state: State) -> None:
    while not state.stopping.is_set():
        control: socket.socket | None = None
        try:
            control = create_session(
                state.sam_endpoint, state.session_id, state.command_timeout
            )
            state.session_started(control)
            while not state.stopping.is_set():
                try:
                    line = receive_line(control)
                except TimeoutError:
                    continue
                if line == "PING" or line.startswith("PING "):
                    control.sendall(("PONG" + line[4:] + "\n").encode("ascii"))
                elif line == "PONG" or line.startswith("PONG "):
                    continue
                else:
                    raise SamError("SAM session emitted an unexpected control line")
        except (OSError, SamError):
            pass
        finally:
            if control is not None:
                state.session_ended(control)
                control.close()
        state.stopping.wait(0.1)


class Handler(BASE.Handler):
    server: "Adapter"

    def handle(self) -> None:
        started_ns = time.monotonic_ns()
        def setup_us() -> int:
            return max(0, (time.monotonic_ns() - started_ns) // 1000)

        if not self.server.state.enter():
            return
        target = ("0.0.0.0", 0)
        destination = "a" * 52 + ".b32.i2p"
        generation = 0
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
                host = str(ipaddress.ip_address(BASE.receive_exact(self.request, 4)))
            elif address_type == 4:
                host = str(ipaddress.ip_address(BASE.receive_exact(self.request, 16)))
            else:
                self.server.state.record_route(
                    "denied-address-type", target, destination, generation,
                    setup_us(),
                )
                self.request.sendall(BASE.socks_reply(8))
                return
            port = int.from_bytes(BASE.receive_exact(self.request, 2), "big")
            target = (host, port)
            mapped = self.server.state.mappings.get(target)
            if mapped is None:
                self.server.state.record_route(
                    "denied-target", target, destination, generation,
                    setup_us(),
                )
                self.request.sendall(BASE.socks_reply(2, address_type == 4))
                return
            destination = mapped
            session = self.server.state.current_session()
            if session is None:
                self.server.state.record_route(
                    "denied-sam-unavailable", target, destination, generation,
                    setup_us(),
                )
                self.request.sendall(BASE.socks_reply(1, address_type == 4))
                return
            session_id, generation = session
            try:
                upstream = connect_stream(
                    self.server.state.sam_endpoint,
                    session_id,
                    destination,
                    self.server.state.command_timeout,
                )
            except (OSError, SamError):
                self.server.state.record_route(
                    "denied-stream", target, destination, generation,
                    setup_us(),
                )
                self.request.sendall(BASE.socks_reply(5, address_type == 4))
                return
            with upstream:
                if not self.server.state.generation_ready(generation):
                    self.server.state.record_route(
                        "denied-stale-generation", target, destination, generation,
                        setup_us(),
                    )
                    self.request.sendall(BASE.socks_reply(1, address_type == 4))
                    return
                self.server.state.record_route(
                    "admitted", target, destination, generation,
                    setup_us(),
                )
                self.request.sendall(BASE.socks_reply(0, address_type == 4))
                self.request.settimeout(None)
                upstream.settimeout(None)
                relay(self.request, upstream)
        except (ConnectionError, OSError, SamError, ValueError):
            return
        finally:
            self.server.state.leave()


class Adapter(BASE.Forwarder):
    def __init__(self, address: tuple[str, int], state: State) -> None:
        family = socket.AF_INET6 if ":" in address[0] else socket.AF_INET
        self.address_family = family
        self.state = state
        BASE.socketserver.TCPServer.__init__(
            self, address, Handler, bind_and_activate=True
        )


def bounded_seconds(text: str) -> float:
    try:
        value = float(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("timeout must be numeric") from error
    if not 1.0 <= value <= 900.0:
        raise argparse.ArgumentTypeError("timeout must be in 1..900 seconds")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listen", required=True, type=BASE.parse_listen_endpoint)
    parser.add_argument("--sam", required=True, type=BASE.parse_endpoint)
    parser.add_argument("--map", required=True, action="append", type=parse_mapping)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--startup-timeout", type=bounded_seconds, default=180.0)
    parser.add_argument("--command-timeout", type=bounded_seconds, default=180.0)
    arguments = parser.parse_args()
    sam_address = ipaddress.ip_address(arguments.sam[0])
    if not sam_address.is_loopback:
        parser.error("the unauthenticated SAM v3.1 endpoint must be numeric loopback")
    mappings = dict(arguments.map)
    if len(mappings) != len(arguments.map):
        parser.error("duplicate --map target")
    arguments.audit.parent.mkdir(parents=True, exist_ok=True)
    arguments.audit.write_text("", encoding="ascii")
    state = State(
        mappings, arguments.audit, arguments.sam, arguments.command_timeout
    )
    supervisor = threading.Thread(
        target=supervise_session, args=(state,), daemon=True
    )
    supervisor.start()
    if not state.wait_ready(arguments.startup_timeout):
        state.close()
        supervisor.join(timeout=2.0)
        parser.error("SAM STREAM session did not become ready before startup timeout")
    with Adapter(arguments.listen, state) as server:
        def request_stop(_signum: int, _frame: object) -> None:
            threading.Thread(target=server.shutdown, daemon=True).start()

        signal.signal(signal.SIGINT, request_stop)
        signal.signal(signal.SIGTERM, request_stop)
        host, port = server.server_address[:2]
        print(f"ready={host}:{port}", flush=True)
        server.serve_forever(poll_interval=0.1)
    state.close()
    supervisor.join(timeout=2.0)
    with state.lock:
        print(
            "admitted={} denied={} peak-active={} sessions={} losses={}".format(
                state.counters.admitted,
                state.counters.denied,
                state.counters.peak_active,
                state.generation,
                state.losses,
            ),
            flush=True,
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SamError as error:
        print(f"I2P SAM adapter failed: {error}", file=sys.stderr)
        raise SystemExit(1)
