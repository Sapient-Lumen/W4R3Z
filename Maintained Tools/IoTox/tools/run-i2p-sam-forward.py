#!/usr/bin/env python3
"""Expose one loopback TCP service through a strict persistent I2P SAM route.

This bounded construction process controls an existing local I2P router. It is
not a router, outproxy, production service manager, or anonymity proof.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import ipaddress
import json
import os
import secrets
import select
import signal
import socket
import stat
import sys
import time
from pathlib import Path


HELLO = b"HELLO VERSION MIN=3.1 MAX=3.1\n"
MAX_SAM_LINE_BYTES = 16384
MAX_KEY_FILE_BYTES = 32768
KEY_HEADER = "iotox-i2p-destination-key-v1"
SESSION_OPTIONS = (
    "STYLE=STREAM DESTINATION={private} "
    "i2cp.leaseSetEncType=4 inbound.quantity=2 outbound.quantity=2 "
    "i2p.streaming.profile=2"
)
I2P_BASE64 = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-~="
)


class SamForwardError(RuntimeError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise SamForwardError(detail)


def parse_endpoint(text: str) -> tuple[str, int]:
    host: str
    port_text: str
    if text.startswith("["):
        closing = text.find("]")
        if closing <= 1 or closing + 1 >= len(text) or text[closing + 1] != ":":
            raise argparse.ArgumentTypeError("endpoint must use [IPv6]:PORT")
        host = text[1:closing]
        port_text = text[closing + 2 :]
    else:
        if text.count(":") != 1:
            raise argparse.ArgumentTypeError(
                "endpoint must use IPv4:PORT or [IPv6]:PORT"
            )
        host, port_text = text.split(":", 1)
    try:
        address = ipaddress.ip_address(host)
        port = int(port_text, 10)
    except ValueError as error:
        raise argparse.ArgumentTypeError("endpoint must be numeric") from error
    if str(address) != host or not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("endpoint is noncanonical or has an invalid port")
    return host, port


def parse_loopback_endpoint(text: str) -> tuple[str, int]:
    endpoint = parse_endpoint(text)
    if not ipaddress.ip_address(endpoint[0]).is_loopback:
        raise argparse.ArgumentTypeError("endpoint must be numeric loopback")
    return endpoint


def bounded_seconds(text: str) -> float:
    try:
        value = float(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("timeout must be numeric") from error
    if not 1.0 <= value <= 900.0:
        raise argparse.ArgumentTypeError("timeout must be in 1..900 seconds")
    return value


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
            raise SamForwardError("SAM closed a partial control line")
        if byte == b"\n":
            break
        require(byte not in (b"\r", b"\0"), "SAM line is noncanonical")
        value.extend(byte)
    else:
        raise SamForwardError("SAM control line exceeds the bound")
    try:
        return value.decode("ascii")
    except UnicodeDecodeError as error:
        raise SamForwardError("SAM v3.1 line is not ASCII") from error


def parse_reply(line: str, command: str, subcommand: str) -> dict[str, str]:
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
    reply = parse_reply(receive_line(stream), "HELLO", "REPLY")
    require(
        reply.get("RESULT") == "OK" and reply.get("VERSION") == "3.1",
        "SAM did not negotiate exact version 3.1",
    )


def decode_i2p_base64(value: str, label: str) -> bytes:
    require(
        bool(value)
        and len(value) <= MAX_KEY_FILE_BYTES
        and all(character in I2P_BASE64 for character in value),
        f"{label} is not canonical I2P base64",
    )
    require(
        value.rstrip("=").find("=") == -1
        and len(value) - len(value.rstrip("=")) <= 2,
        f"{label} has invalid I2P base64 padding",
    )
    standard = value.translate(str.maketrans("-~", "+/"))
    try:
        decoded = base64.b64decode(standard, validate=True)
    except (ValueError, binascii.Error) as error:
        raise SamForwardError(f"{label} is not valid I2P base64") from error
    canonical = base64.b64encode(decoded).decode("ascii")
    canonical = canonical.translate(str.maketrans("+/", "-~"))
    require(canonical == value, f"{label} is noncanonical I2P base64")
    return decoded


def validate_key_pair(public: str, private: str) -> bytes:
    public_bytes = decode_i2p_base64(public, "public Destination")
    private_bytes = decode_i2p_base64(private, "private Destination")
    require(
        len(public_bytes) >= 384
        and len(private_bytes) > len(public_bytes)
        and private_bytes.startswith(public_bytes),
        "private Destination does not bind the public Destination",
    )
    return public_bytes


def destination_b32(public_bytes: bytes) -> str:
    encoded = base64.b32encode(hashlib.sha256(public_bytes).digest())
    return encoded.decode("ascii").lower().rstrip("=") + ".b32.i2p"


def key_text(public: str, private: str) -> bytes:
    return (
        f"{KEY_HEADER}\npublic={public}\nprivate={private}\n"
    ).encode("ascii")


def validate_key_descriptor(descriptor: int, path: Path) -> os.stat_result:
    status = os.fstat(descriptor)
    require(stat.S_ISREG(status.st_mode), "Destination key is not a regular file")
    require(status.st_uid == os.geteuid(), "Destination key is not owner-owned")
    require(stat.S_IMODE(status.st_mode) == 0o600, "Destination key mode must be 0600")
    require(status.st_nlink == 1, "Destination key must have exactly one link")
    require(status.st_size <= MAX_KEY_FILE_BYTES, "Destination key exceeds its bound")
    require(path.is_absolute(), "Destination key path must be absolute")
    return status


def parse_key_bytes(data: bytes) -> tuple[str, str, bytes]:
    require(len(data) <= MAX_KEY_FILE_BYTES, "Destination key exceeds its bound")
    try:
        text = data.decode("ascii")
    except UnicodeDecodeError as error:
        raise SamForwardError("Destination key is not ASCII") from error
    lines = text.splitlines(keepends=True)
    require(
        len(lines) == 3
        and all(line.endswith("\n") for line in lines)
        and lines[0] == KEY_HEADER + "\n"
        and lines[1].startswith("public=")
        and lines[2].startswith("private="),
        "Destination key has invalid canonical framing",
    )
    public = lines[1][len("public=") : -1]
    private = lines[2][len("private=") : -1]
    return public, private, validate_key_pair(public, private)


def read_key(path: Path) -> tuple[str, str, bytes]:
    flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        status = validate_key_descriptor(descriptor, path)
        data = bytearray()
        while len(data) <= MAX_KEY_FILE_BYTES:
            block = os.read(descriptor, min(8192, MAX_KEY_FILE_BYTES + 1 - len(data)))
            if not block:
                break
            data.extend(block)
        require(len(data) == status.st_size, "Destination key changed while reading")
        return parse_key_bytes(bytes(data))
    finally:
        os.close(descriptor)


def generate_key(
    sam_endpoint: tuple[str, int], timeout: float
) -> tuple[str, str, bytes]:
    stream = open_numeric(sam_endpoint, 10.0)
    try:
        negotiate(stream)
        stream.settimeout(timeout)
        stream.sendall(b"DEST GENERATE SIGNATURE_TYPE=7\n")
        reply = parse_reply(receive_line(stream), "DEST", "REPLY")
        require(
            set(reply) == {"PUB", "PRIV"},
            "SAM DEST GENERATE did not return exactly PUB and PRIV",
        )
        public = reply["PUB"]
        private = reply["PRIV"]
        return public, private, validate_key_pair(public, private)
    finally:
        stream.close()


def store_new_key(path: Path, public: str, private: str) -> bool:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    parent = path.parent.stat()
    require(stat.S_ISDIR(parent.st_mode), "Destination key parent is not a directory")
    require(parent.st_uid == os.geteuid(), "Destination key parent is not owner-owned")
    require(
        stat.S_IMODE(parent.st_mode) & 0o077 == 0,
        "Destination key parent must deny group and world access",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError:
        return False
    try:
        data = key_text(public, private)
        written = 0
        while written < len(data):
            written += os.write(descriptor, data[written:])
        os.fsync(descriptor)
        validate_key_descriptor(descriptor, path)
    finally:
        os.close(descriptor)
    directory = os.open(path.parent, os.O_RDONLY | os.O_CLOEXEC)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return True


def load_or_create_key(
    path: Path, sam_endpoint: tuple[str, int], timeout: float
) -> tuple[str, str, bytes, str]:
    try:
        public, private, public_bytes = read_key(path)
        return public, private, public_bytes, "loaded"
    except FileNotFoundError:
        public, private, public_bytes = generate_key(sam_endpoint, timeout)
        if store_new_key(path, public, private):
            return public, private, public_bytes, "created"
        public, private, public_bytes = read_key(path)
        return public, private, public_bytes, "loaded-after-race"


def create_session(
    sam_endpoint: tuple[str, int], session_id: str, private: str, timeout: float
) -> socket.socket:
    stream = open_numeric(sam_endpoint, 10.0)
    try:
        negotiate(stream)
        stream.settimeout(timeout)
        command = "SESSION CREATE ID={} {}\n".format(
            session_id, SESSION_OPTIONS.format(private=private)
        )
        stream.sendall(command.encode("ascii"))
        reply = parse_reply(receive_line(stream), "SESSION", "STATUS")
        require(
            reply.get("RESULT") == "OK"
            and reply.get("DESTINATION") == private,
            "SAM refused or substituted the persistent STREAM Destination",
        )
        stream.settimeout(None)
        return stream
    except Exception:
        stream.close()
        raise


def create_forward(
    sam_endpoint: tuple[str, int],
    session_id: str,
    target: tuple[str, int],
    timeout: float,
) -> socket.socket:
    stream = open_numeric(sam_endpoint, 10.0)
    try:
        negotiate(stream)
        stream.settimeout(timeout)
        host, port = target
        command = (
            f"STREAM FORWARD ID={session_id} PORT={port} "
            f"HOST={host} SILENT=true\n"
        )
        stream.sendall(command.encode("ascii"))
        reply = parse_reply(receive_line(stream), "STREAM", "STATUS")
        require(
            reply == {"RESULT": "OK"},
            "SAM refused the exact silent STREAM FORWARD",
        )
        stream.settimeout(None)
        return stream
    except Exception:
        stream.close()
        raise


class Audit:
    def __init__(self, path: Path, destination: str, key_outcome: str) -> None:
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        descriptor = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC,
            0o600,
        )
        self.output = os.fdopen(descriptor, "w", encoding="ascii")
        self.destination_commitment = hashlib.sha256(
            ("iotox-i2p-b32-v1\0" + destination).encode("ascii")
        ).hexdigest()
        self.append("destination-key", 0, key_outcome)

    def append(self, event: str, generation: int, outcome: str) -> None:
        record = {
            "destination_sha256": self.destination_commitment,
            "event": event,
            "generation": generation,
            "monotonic_ns": time.monotonic_ns(),
            "outcome": outcome,
        }
        self.output.write(
            json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
        )
        self.output.flush()
        os.fsync(self.output.fileno())

    def close(self) -> None:
        self.output.close()


def main() -> int:
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sam", required=True, type=parse_loopback_endpoint)
    parser.add_argument("--target", required=True, type=parse_loopback_endpoint)
    parser.add_argument("--destination-key", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--startup-timeout", type=bounded_seconds, default=180.0)
    parser.add_argument("--command-timeout", type=bounded_seconds, default=180.0)
    arguments = parser.parse_args()
    key_path = arguments.destination_key.absolute()
    audit_path = arguments.audit.absolute()
    if key_path == audit_path:
        parser.error("Destination key and audit paths must differ")

    public, private, public_bytes, key_outcome = load_or_create_key(
        key_path, arguments.sam, arguments.command_timeout
    )
    del public
    destination = destination_b32(public_bytes)
    audit = Audit(audit_path, destination, key_outcome)
    stopping = False
    generation = 0
    losses = 0
    ready_printed = False
    controls: list[socket.socket] = []

    def request_stop(_signum: int, _frame: object) -> None:
        nonlocal stopping
        stopping = True
        for stream in controls:
            try:
                stream.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    try:
        startup_deadline = time.monotonic() + arguments.startup_timeout
        while not stopping:
            session: socket.socket | None = None
            forward: socket.socket | None = None
            remaining = startup_deadline - time.monotonic()
            if not ready_printed and remaining <= 0:
                raise SamForwardError(
                    "SAM forward did not become ready before startup timeout"
                )
            try:
                session_id = "iotox_forward_" + secrets.token_hex(10)
                session = create_session(
                    arguments.sam,
                    session_id,
                    private,
                    min(arguments.command_timeout, max(1.0, remaining))
                    if not ready_printed
                    else arguments.command_timeout,
                )
                controls.append(session)
                forward = create_forward(
                    arguments.sam,
                    session_id,
                    arguments.target,
                    arguments.command_timeout,
                )
                controls.append(forward)
                generation += 1
                audit.append("sam-forward", generation, "ready")
                if not ready_printed:
                    print(f"ready={destination}", flush=True)
                    ready_printed = True
                else:
                    print(f"recovered-generation={generation}", flush=True)
                readable, _, _ = select.select([session, forward], [], [], None)
                if stopping:
                    break
                for stream in readable:
                    require(stream.recv(1) == b"", "SAM control emitted unexpected data")
                raise SamForwardError("SAM session or forward control closed")
            except (OSError, SamForwardError):
                if ready_printed and not stopping:
                    losses += 1
                    audit.append("sam-forward", generation, "lost")
            finally:
                for stream in (forward, session):
                    if stream is not None:
                        if stream in controls:
                            controls.remove(stream)
                        stream.close()
            if not stopping:
                time.sleep(0.1)
    finally:
        audit.close()
    print(f"generations={generation} losses={losses}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, SamForwardError) as error:
        print(f"I2P SAM forward failed: {error}", file=sys.stderr)
        raise SystemExit(1)
