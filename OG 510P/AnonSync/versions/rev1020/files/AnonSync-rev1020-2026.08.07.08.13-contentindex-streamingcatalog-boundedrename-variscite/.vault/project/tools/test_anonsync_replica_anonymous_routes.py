#!/usr/bin/env python3
"""Process proof for AnonSync direct/Tor/I2P route ownership.

The fake SOCKS5 and SAM peers implement only the protocol surface needed to
prove that the shipped C++ executable carries its mutual-TLS file delivery over
the selected route. They never terminate TLS and therefore cannot forge the
application peer identity. The inbound SAM test also proves that STREAM FORWARD
uses SILENT=true and targets only the receiver's loopback TLS listener.
"""

from __future__ import annotations

import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import select
import signal
import socket
import subprocess
import tempfile
import threading
import time
from typing import Any, Callable, Sequence

from test_anonsync_replica_cli import (
    expect_fields,
    fail,
    generate_tls_fixture,
    reserve_port,
    run_failure,
    run_json,
    wait_until_listening,
)

VALID_ONION = (
    "pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd.onion"
)
TOR_TOKEN = "rev0908-process-route-isolation"
SAM_SESSION_ID = "anonsync-rev0908-process"
I2P_PEER = "peer-process-test.b32.i2p"
PERSISTED_DESTINATION = "persisted-private-destination-process-token"


def make_listener() -> socket.socket:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    listener.listen(8)
    listener.settimeout(20.0)
    return listener


def listener_port(listener: socket.socket) -> int:
    return int(listener.getsockname()[1])


def read_exact(peer: socket.socket, size: int, label: str) -> bytes:
    output = bytearray()
    while len(output) < size:
        chunk = peer.recv(size - len(output))
        if not chunk:
            fail(f"{label} peer closed after {len(output)} of {size} bytes")
        output.extend(chunk)
    return bytes(output)


def read_line(peer: socket.socket, label: str) -> str:
    output = bytearray()
    while len(output) < 16384:
        byte = read_exact(peer, 1, label)
        if byte == b"\n":
            return output.decode("ascii")
        if byte == b"\x00":
            fail(f"{label} contains NUL")
        output.extend(byte)
    fail(f"{label} line is oversized")


def relay_bidirectional(left: socket.socket, right: socket.socket, label: str) -> None:
    open_read = {left, right}
    while open_read:
        readable, _, exceptional = select.select(
            list(open_read), [], list(open_read), 20.0
        )
        if exceptional:
            fail(f"{label} observed an exceptional socket")
        if not readable:
            fail(f"{label} relay timed out")
        for source in readable:
            destination = right if source is left else left
            try:
                data = source.recv(65536)
            except ConnectionResetError:
                data = b""
            if data:
                try:
                    destination.sendall(data)
                except (BrokenPipeError, ConnectionResetError):
                    data = b""
                if data:
                    continue
            open_read.remove(source)
            try:
                destination.shutdown(socket.SHUT_WR)
            except OSError:
                pass


class CheckedThread:
    def __init__(self, function: Callable[[], None], label: str) -> None:
        self._error: BaseException | None = None
        self._label = label

        def entry() -> None:
            try:
                function()
            except BaseException as error:  # noqa: BLE001 - test boundary.
                self._error = error

        self._thread = threading.Thread(target=entry, name=label, daemon=True)
        self._thread.start()

    def raise_if_failed(self) -> None:
        if self._error is not None:
            raise self._error

    def join(self, timeout: float = 30.0) -> None:
        self._thread.join(timeout)
        if self._thread.is_alive():
            fail(f"{self._label} did not terminate")
        self.raise_if_failed()


def wait_for_process_event(
    event: threading.Event,
    process: subprocess.Popen[str],
    worker: CheckedThread,
    timeout: float,
    label: str,
) -> None:
    deadline = time.monotonic() + timeout
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0.0:
            fail(f"{label} was not established before its readiness deadline")
        if event.wait(min(0.05, remaining)):
            worker.raise_if_failed()
            return
        worker.raise_if_failed()
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1.0)
            fail(
                f"{label} process exited before readiness with status "
                f"{process.returncode}\nstdout:\n{stdout}\nstderr:\n{stderr}"
            )


def fake_tor_socks5(
    listener: socket.socket,
    target_port: int,
) -> CheckedThread:
    def serve() -> None:
        with closing(listener):
            peer, _ = listener.accept()
            with peer:
                peer.settimeout(20.0)
                if read_exact(peer, 3, "Tor method request") != b"\x05\x01\x02":
                    fail("Tor client did not require username/password method")
                peer.sendall(b"\x05\x02")

                version, user_bytes = read_exact(peer, 2, "Tor auth header")
                if version != 1:
                    fail("Tor auth subnegotiation version changed")
                username = read_exact(peer, user_bytes, "Tor auth username")
                password_bytes = read_exact(peer, 1, "Tor auth password length")[0]
                password = read_exact(peer, password_bytes, "Tor auth password")
                if username != b"<torS0X>0":
                    fail("Tor format-0 isolation username changed")
                if password.decode("ascii") != TOR_TOKEN:
                    fail("Tor isolation token changed")
                peer.sendall(b"\x01\x00")

                if read_exact(peer, 4, "Tor connect header") != b"\x05\x01\x00\x03":
                    fail("Tor client did not issue a domain-name CONNECT")
                name_bytes = read_exact(peer, 1, "Tor onion length")[0]
                onion = read_exact(peer, name_bytes, "Tor onion name").decode("ascii")
                service_port = int.from_bytes(
                    read_exact(peer, 2, "Tor service port"), "big"
                )
                if onion != VALID_ONION or service_port != 443:
                    fail("Tor SOCKS request changed the onion endpoint")

                with socket.create_connection(("127.0.0.1", target_port), 10.0) as target:
                    target.settimeout(None)
                    peer.settimeout(None)
                    peer.sendall(b"\x05\x00\x00\x01\x7f\x00\x00\x01\x00\x00")
                    relay_bidirectional(peer, target, "Tor TLS stream")

    return CheckedThread(serve, "fake Tor SOCKS5")


def expect_sam_hello(
    peer: socket.socket,
    label: str,
    selected_version: str = "3.1",
) -> None:
    if read_line(peer, label) != "HELLO VERSION MIN=3.1 MAX=3.2":
        fail(f"{label} did not advertise the supported SAM 3.1..3.2 range")
    if selected_version not in {"3.1", "3.2"}:
        fail(f"{label} selected unsupported SAM version {selected_version!r}")
    peer.sendall(
        f"HELLO REPLY RESULT=OK VERSION={selected_version}\n".encode("ascii")
    )


def runtime_sam_session_id(command: str, label: str) -> str:
    """Extract and validate the bridge-global runtime ID from a SAM command."""
    values = [token[3:] for token in command.split() if token.startswith("ID=")]
    if len(values) != 1:
        fail(f"{label} must contain exactly one SAM ID: {command}")
    value = values[0]
    prefix = SAM_SESSION_ID + "."
    suffix = value[len(prefix):] if value.startswith(prefix) else ""
    if (
        not value.startswith(prefix)
        or len(value) > 64
        or len(suffix) != 32
        or any(character not in "0123456789abcdef" for character in suffix)
    ):
        fail(f"{label} carried an invalid runtime SAM ID: {value!r}")
    return value


def fake_outbound_sam(
    listener: socket.socket,
    target_port: int,
) -> CheckedThread:
    def serve() -> None:
        with closing(listener):
            control, _ = listener.accept()
            with control:
                control.settimeout(20.0)
                expect_sam_hello(control, "outbound SAM control HELLO")
                session = read_line(control, "outbound SAM SESSION CREATE")
                session_id = runtime_sam_session_id(
                    session, "outbound SAM SESSION CREATE"
                )
                required = (
                    "SESSION CREATE STYLE=STREAM",
                    "DESTINATION=TRANSIENT",
                    "SIGNATURE_TYPE=7",
                    "i2cp.leaseSetEncType=4",
                    "inbound.quantity=2",
                    "outbound.quantity=2",
                )
                if not all(token in session for token in required):
                    fail(f"outbound SAM session command is incomplete: {session}")
                control.sendall(
                    b"SESSION STATUS RESULT=OK DESTINATION=fake-outbound-private\n"
                )

                data, _ = listener.accept()
                with data:
                    data.settimeout(20.0)
                    expect_sam_hello(data, "outbound SAM stream HELLO")
                    connect = read_line(data, "outbound SAM STREAM CONNECT")
                    required_connect = (
                        "STREAM CONNECT",
                        f"ID={session_id}",
                        f"DESTINATION={I2P_PEER}",
                        "SILENT=false",
                    )
                    if not all(token in connect for token in required_connect):
                        fail(f"outbound SAM connect command changed: {connect}")
                    with socket.create_connection(
                        ("127.0.0.1", target_port), 10.0
                    ) as target:
                        target.settimeout(None)
                        data.settimeout(None)
                        data.sendall(b"STREAM STATUS RESULT=OK\n")
                        relay_bidirectional(data, target, "I2P outbound TLS stream")

    return CheckedThread(serve, "fake outbound SAM")


def fake_inbound_sam(
    listener: socket.socket,
    peer_listener: socket.socket,
    expected_forward_port: int,
    forward_ready: threading.Event,
) -> CheckedThread:
    def serve() -> None:
        with closing(listener), closing(peer_listener):
            control, _ = listener.accept()
            with control:
                control.settimeout(20.0)
                expect_sam_hello(control, "inbound SAM control HELLO")
                session = read_line(control, "inbound SAM SESSION CREATE")
                session_id = runtime_sam_session_id(
                    session, "inbound SAM SESSION CREATE"
                )
                required = (
                    "SESSION CREATE STYLE=STREAM",
                    f"DESTINATION={PERSISTED_DESTINATION}",
                    "i2cp.leaseSetEncType=4",
                    "inbound.quantity=2",
                    "outbound.quantity=2",
                )
                if not all(token in session for token in required):
                    fail(f"inbound SAM session command is incomplete: {session}")
                if "SIGNATURE_TYPE=" in session:
                    fail("inbound persistent SAM identity received SIGNATURE_TYPE")
                control.sendall(
                    b"SESSION STATUS RESULT=OK DESTINATION=fake-inbound-public\n"
                )

                forward, _ = listener.accept()
                with forward:
                    forward.settimeout(20.0)
                    expect_sam_hello(forward, "inbound SAM forward HELLO")
                    command = read_line(forward, "inbound SAM STREAM FORWARD")
                    required_forward = (
                        "STREAM FORWARD",
                        f"ID={session_id}",
                        "HOST=127.0.0.1",
                        f"PORT={expected_forward_port}",
                        "SILENT=true",
                    )
                    if not all(token in command for token in required_forward):
                        fail(f"inbound SAM forward command changed: {command}")
                    if "SILENT=false" in command:
                        fail("inbound SAM forwarding enabled destination injection")
                    forward.sendall(b"STREAM STATUS RESULT=OK\n")
                    forward_ready.set()

                    remote, _ = peer_listener.accept()
                    with remote, socket.create_connection(
                        ("127.0.0.1", expected_forward_port), 10.0
                    ) as target:
                        remote.settimeout(None)
                        target.settimeout(None)
                        relay_bidirectional(remote, target, "I2P inbound TLS stream")

    return CheckedThread(serve, "fake inbound SAM")


def start_receiver(
    replica: Path,
    manifest: Path,
    certificates: Path,
    port: int,
    route_arguments: Sequence[str],
    timeout_seconds: int,
) -> subprocess.Popen[str]:
    process = subprocess.Popen(
        [
            str(replica), "serve-one", "--manifest", str(manifest),
            "--bind-address", "127.0.0.1", "--port", str(port),
            "--certificate", str(certificates / "receiver.pem"),
            "--private-key", str(certificates / "receiver.key"),
            "--ca-file", str(certificates / "ca.pem"),
            "--timeout-seconds", str(timeout_seconds),
            *route_arguments,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    wait_until_listening(process, port)
    return process


def collect_receiver(process: subprocess.Popen[str], label: str) -> dict[str, Any]:
    stdout, stderr = process.communicate(timeout=30.0)
    if process.returncode != 0:
        fail(
            f"{label} failed with status {process.returncode}\n"
            f"stdout:\n{stdout}\nstderr:\n{stderr}"
        )
    if stderr:
        fail(f"{label} wrote diagnostics on success: {stderr}")
    try:
        value = json.loads(stdout)
    except json.JSONDecodeError as error:
        fail(f"{label} did not emit JSON: {error}: {stdout}")
    if not isinstance(value, dict):
        fail(f"{label} JSON is not an object")
    return value


def terminate_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.send_signal(signal.SIGTERM)
    try:
        process.communicate(timeout=2.0)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate(timeout=2.0)


def enqueue(
    replica: Path,
    manifest: Path,
    source_root: Path,
    name: str,
    payload: bytes,
) -> dict[str, Any]:
    source = source_root / name
    source.write_bytes(payload)
    return run_json([
        str(replica), "enqueue-file", "--manifest", str(manifest),
        "--destination-device", "receiver",
        "--canonical-path", f"routes/{name}",
        "--source-file", str(source),
    ])


def send_base(
    replica: Path,
    sender_manifest: Path,
    certificates: Path,
    receiver_pin: str,
) -> list[str]:
    return [
        str(replica), "send-one", "--manifest", str(sender_manifest),
        "--remote-device", "receiver", "--remote-epoch", "1",
        "--remote-spki", receiver_pin,
        "--certificate", str(certificates / "sender.pem"),
        "--private-key", str(certificates / "sender.key"),
        "--ca-file", str(certificates / "ca.pem"),
        "--operator-clock-authority-id", "anonymous-routes-process-test",
        "--operator-clock-uncertainty-ns", "1000000",
    ]


def assert_delivery(
    client: dict[str, Any],
    server: dict[str, Any],
    operation_id: str,
    sender_pin: str,
    receiver_pin: str,
    client_transport: str,
    server_transport: str,
    label: str,
) -> None:
    expect_fields(client, {
        "command": "send-one",
        "transport": client_transport,
        "route_disposition": "connected",
        "route_terminal_stage": "complete",
        "route_negotiated": True,
        "disposition": "receipt_applied",
        "peer_authenticated": True,
        "receipt_apply_result": "effect_settled",
        "operation_id": operation_id,
        "peer_spki_sha256": receiver_pin,
    }, f"{label} sender")
    expect_fields(server, {
        "command": "serve-one",
        "transport": server_transport,
        "disposition": "receipt_sent",
        "handshake_complete": True,
        "peer_device_id": "sender",
        "peer_epoch": 1,
        "peer_spki_sha256": sender_pin,
        "receipt_disposition": "published",
        "operation_id": operation_id,
    }, f"{label} receiver")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replica", required=True, type=Path)
    arguments = parser.parse_args()
    replica = arguments.replica.resolve(strict=True)

    with tempfile.TemporaryDirectory(prefix="anonsync-anonymous-routes-") as temp:
        root = Path(temp)
        certificates = root / "certificates"
        certificates.mkdir(mode=0o700)
        generate_tls_fixture(certificates, "openssl")

        private_destination = root / "receiver-i2p-private-destination"
        private_destination.write_text(PERSISTED_DESTINATION, encoding="ascii")
        os.chmod(private_destination, 0o600)

        # Route grammar is resolved before manifest/store/TLS authority.
        run_failure([
            str(replica), "send-one", "--transport", "tor",
            "--tor-socks-address", "192.0.2.1",
            "--onion-address", VALID_ONION, "--onion-port", "443",
        ], stderr_contains="Tor SOCKS proxy must be loopback")
        run_failure([
            str(replica), "send-one", "--transport", "i2p",
            "--i2p-sam-address", "192.0.2.1",
            "--i2p-destination", I2P_PEER,
        ], stderr_contains="SAM bridge must be loopback")
        run_failure([
            str(replica), "send-one", "--transport", "i2p",
            "--i2p-destination", I2P_PEER, "--timeout-seconds", "179",
        ], stderr_contains=(
            "--timeout-seconds must be at least 180 for --transport i2p"
        ))
        run_failure([
            str(replica), "serve-one", "--bind-address", "192.0.2.1",
            "--port", "4433", "--transport", "tor",
            "--onion-address", VALID_ONION, "--onion-port", "443",
        ], stderr_contains="requires a loopback --bind-address")
        run_failure([
            str(replica), "serve-one", "--bind-address", "127.0.0.1",
            "--port", "4433", "--transport", "i2p",
        ], stderr_contains="requires --i2p-private-destination-file")
        run_failure([
            str(replica), "serve-one", "--bind-address", "127.0.0.1",
            "--port", "4433", "--transport", "i2p",
            "--i2p-sam-address", "192.0.2.1",
            "--i2p-private-destination-file", str(private_destination),
        ], stderr_contains="SAM bridge must be loopback")
        run_failure([
            str(replica), "serve-one", "--bind-address", "127.0.0.1",
            "--port", "4433", "--transport", "i2p",
            "--i2p-private-destination-file", str(private_destination),
            "--timeout-seconds", "179",
        ], stderr_contains=(
            "--timeout-seconds must be at least 180 for --transport i2p"
        ))
        for command in ("send-batch", "serve-batch"):
            route = (
                ["--i2p-destination", I2P_PEER]
                if command == "send-batch"
                else [
                    "--bind-address", "127.0.0.1", "--port", "4433",
                    "--i2p-private-destination-file", str(private_destination),
                ]
            )
            run_failure([
                str(replica), command, "--max-sessions", "1",
                "--max-runtime-seconds", "179", "--transport", "i2p",
                "--timeout-seconds", "180", *route,
            ], stderr_contains=(
                "--max-runtime-seconds must be at least --timeout-seconds"
            ))

        database_root = root / "databases"
        database_root.mkdir(mode=0o700)
        payload_root = root / "sender-payloads"
        payload_root.mkdir(mode=0o700)
        files_root = root / "receiver-files"
        files_root.mkdir(mode=0o700)
        source_root = root / "sources"
        source_root.mkdir(mode=0o700)

        sender_manifest = database_root / "sender.json"
        receiver_manifest = database_root / "receiver.json"
        run_json([
            str(replica), "init", "--manifest", str(sender_manifest),
            "--replica-db", str(database_root / "sender.sqlite"),
            "--payload-root", str(payload_root),
            "--folder", "anonymous-routes", "--local-device", "sender",
            "--local-epoch", "1",
        ])
        run_json([
            str(replica), "init", "--manifest", str(receiver_manifest),
            "--replica-db", str(database_root / "receiver.sqlite"),
            "--effect-db", str(database_root / "effects.sqlite"),
            "--files-root", str(files_root),
            "--membership-db", str(database_root / "membership.sqlite"),
            "--anchor-db", str(database_root / "membership-anchor.sqlite"),
            "--folder", "anonymous-routes", "--local-device", "receiver",
            "--local-epoch", "1",
        ])
        (files_root / "routes").mkdir(mode=0o700)
        sender_pin = run_json([
            str(replica), "certificate-spki", "--certificate",
            str(certificates / "sender.pem"),
        ])["spki_sha256"]
        receiver_pin = run_json([
            str(replica), "certificate-spki", "--certificate",
            str(certificates / "receiver.pem"),
        ])["spki_sha256"]
        run_json([
            str(replica), "membership-publish", "--manifest",
            str(receiver_manifest), "--policy-epoch", "1", "--peer",
            f"sender:1:{sender_pin}",
        ])
        clock = run_json([
            str(replica), "clock-observe", "--manifest", str(sender_manifest),
            "--operator-clock-authority-id", "anonymous-routes-process-test",
            "--operator-clock-uncertainty-ns", "1000000",
        ])
        expect_fields(clock, {
            "command": "clock-observe", "clock_profile": "operator-trusted",
            "outcome": "accepted", "clock_health": "healthy",
        }, "anonymous-route sender clock")
        base = send_base(
            replica, sender_manifest, certificates, str(receiver_pin)
        )

        # Outbound Tor: SOCKS sees the onion name and isolation token, but the
        # proxy only relays an end-to-end mutually authenticated TLS stream.
        tor_payload = b"AnonSync route proof: outbound Tor\n"
        tor_enqueue = enqueue(
            replica, sender_manifest, source_root, "tor-outbound.bin", tor_payload
        )
        receiver_port = reserve_port()
        receiver = start_receiver(
            replica, receiver_manifest, certificates, receiver_port, [], 10
        )
        socks_listener = make_listener()
        socks_port = listener_port(socks_listener)
        proxy = fake_tor_socks5(socks_listener, receiver_port)
        try:
            client = run_json([
                *base, "--transport", "tor", "--onion-address", VALID_ONION,
                "--onion-port", "443", "--tor-socks-address", "127.0.0.1",
                "--tor-socks-port", str(socks_port),
                "--tor-isolation-token", TOR_TOKEN,
                "--timeout-seconds", "10",
            ], timeout=30.0)
            server = collect_receiver(receiver, "Tor outbound receiver")
        except BaseException as client_error:  # noqa: BLE001 - test boundary.
            try:
                collect_receiver(receiver, "Tor outbound receiver after client failure")
            except BaseException as server_error:  # noqa: BLE001
                proxy.join()
                fail(f"{client_error}; receiver diagnostic: {server_error}")
            proxy.join()
            raise
        finally:
            terminate_process(receiver)
        proxy.join()
        assert_delivery(
            client, server, tor_enqueue["operation_id"], str(sender_pin),
            str(receiver_pin), "tor_socks5", "direct_tcp", "Tor outbound"
        )
        if client.get("route_control_session_created") is not False:
            fail("Tor outbound route invented a retained control session")
        if (files_root / "routes" / "tor-outbound.bin").read_bytes() != tor_payload:
            fail("Tor outbound delivery changed payload bytes")

        # Outbound I2P: one retained control session creates one STREAM CONNECT
        # data socket carrying the same TLS/application protocol.
        i2p_payload = b"AnonSync route proof: outbound I2P\n"
        i2p_enqueue = enqueue(
            replica, sender_manifest, source_root, "i2p-outbound.bin", i2p_payload
        )
        receiver_port = reserve_port()
        receiver = start_receiver(
            replica, receiver_manifest, certificates, receiver_port, [], 10
        )
        sam_listener = make_listener()
        sam_port = listener_port(sam_listener)
        bridge = fake_outbound_sam(sam_listener, receiver_port)
        try:
            client = run_json([
                *base, "--transport", "i2p", "--i2p-destination", I2P_PEER,
                "--i2p-sam-address", "127.0.0.1", "--i2p-sam-port",
                str(sam_port), "--i2p-session-id", SAM_SESSION_ID,
                "--timeout-seconds", "180",
            ], timeout=30.0)
            server = collect_receiver(receiver, "I2P outbound receiver")
        finally:
            terminate_process(receiver)
        bridge.join()
        assert_delivery(
            client, server, i2p_enqueue["operation_id"], str(sender_pin),
            str(receiver_pin), "i2p_sam", "direct_tcp", "I2P outbound"
        )
        expect_fields(client, {
            "route_control_session_created": True,
            "route_control_session_reused": False,
            "route_numeric_connect_attempts": 2,
            "route_sam_result": "ok",
        }, "I2P outbound route evidence")
        if (files_root / "routes" / "i2p-outbound.bin").read_bytes() != i2p_payload:
            fail("I2P outbound delivery changed payload bytes")

        # Tor inbound profile: C++ validates the onion identity and forces the
        # actual TLS listener onto loopback. Tor daemon publication remains an
        # explicit deployment concern, so this test enters via the loopback target.
        tor_inbound_payload = b"AnonSync route proof: inbound Tor profile\n"
        tor_inbound_enqueue = enqueue(
            replica, sender_manifest, source_root, "tor-inbound.bin",
            tor_inbound_payload,
        )
        receiver_port = reserve_port()
        receiver = start_receiver(
            replica, receiver_manifest, certificates, receiver_port,
            [
                "--transport", "tor", "--onion-address", VALID_ONION,
                "--onion-port", "443",
            ],
            10,
        )
        try:
            client = run_json([
                *base, "--transport", "direct", "--address", "127.0.0.1",
                "--port", str(receiver_port), "--timeout-seconds", "10",
            ])
            server = collect_receiver(receiver, "Tor inbound-profile receiver")
        finally:
            terminate_process(receiver)
        assert_delivery(
            client, server, tor_inbound_enqueue["operation_id"], str(sender_pin),
            str(receiver_pin), "direct_tcp", "tor_onion_service",
            "Tor inbound profile",
        )
        if (files_root / "routes" / "tor-inbound.bin").read_bytes() != tor_inbound_payload:
            fail("Tor inbound-profile delivery changed payload bytes")

        # Native inbound I2P: receiver itself owns SAM SESSION CREATE and
        # STREAM FORWARD. The fake bridge opens the SILENT loopback child only
        # after a remote peer reaches its modeled I2P-facing listener.
        i2p_inbound_payload = b"AnonSync route proof: native inbound I2P\n"
        i2p_inbound_enqueue = enqueue(
            replica, sender_manifest, source_root, "i2p-inbound.bin",
            i2p_inbound_payload,
        )
        receiver_port = reserve_port()
        sam_listener = make_listener()
        sam_port = listener_port(sam_listener)
        peer_listener = make_listener()
        peer_port = listener_port(peer_listener)
        forward_ready = threading.Event()
        bridge = fake_inbound_sam(
            sam_listener, peer_listener, receiver_port, forward_ready
        )
        receiver = start_receiver(
            replica, receiver_manifest, certificates, receiver_port,
            [
                "--transport", "i2p", "--i2p-sam-address", "127.0.0.1",
                "--i2p-sam-port", str(sam_port), "--i2p-session-id",
                SAM_SESSION_ID, "--i2p-private-destination-file",
                str(private_destination),
            ],
            180,
        )
        try:
            # The complete registry deliberately runs this process proof beside
            # CPU-heavy SQLite and graph tests. Use the test's existing 90-second
            # outer budget rather than a brittle 10-second scheduling guess,
            # while still surfacing an exited receiver or failed fake SAM worker
            # immediately.
            wait_for_process_event(
                forward_ready, receiver, bridge, 30.0,
                "native inbound I2P STREAM FORWARD",
            )
        except BaseException:
            terminate_process(receiver)
            raise
        try:
            client = run_json([
                *base, "--transport", "direct", "--address", "127.0.0.1",
                "--port", str(peer_port), "--timeout-seconds", "10",
            ], timeout=30.0)
            server = collect_receiver(receiver, "native inbound I2P receiver")
        finally:
            terminate_process(receiver)
        bridge.join()
        assert_delivery(
            client, server, i2p_inbound_enqueue["operation_id"], str(sender_pin),
            str(receiver_pin), "direct_tcp", "i2p_sam_forward",
            "native inbound I2P",
        )
        expect_fields(server, {
            "i2p_forward_route_disposition": "connected",
            "i2p_forward_route_terminal_stage": "complete",
            "i2p_forward_route_negotiated": True,
            "i2p_forward_control_session_created": True,
            "i2p_forward_socket_created": True,
            "i2p_forward_socket_policy_verified": True,
            "i2p_forward_numeric_connect_attempts": 2,
            "i2p_forward_sam_result": "ok",
        }, "native inbound I2P publication evidence")
        if (files_root / "routes" / "i2p-inbound.bin").read_bytes() != i2p_inbound_payload:
            fail("native inbound I2P delivery changed payload bytes")

    print("anonsync_replica anonymous route process checks passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 - one diagnostic boundary.
        print(
            f"anonsync_replica anonymous route process checks failed: {error}",
            file=os.sys.stderr,
        )
        raise SystemExit(1)
