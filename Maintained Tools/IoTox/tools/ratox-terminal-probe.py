#!/usr/bin/env python3
"""Capture genuine Ratox local-input to local-render timing.

This construction tool speaks the frozen private terminal socket protocol. It
does not emulate the network or PTY service: INPUT crosses the live IoTox
controller, Tox, the remote PTY, and the live IoTox controller again. Each
returned byte is copied through a local pseudoterminal before render completion
is timestamped.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pty
import re
import secrets
import select
import socket
import struct
import subprocess
import sys
import termios
import tempfile
import time
import tty
from dataclasses import dataclass
from pathlib import Path


MAGIC = b"ITTS"
HEADER = struct.Struct(">4sBBBBQQHH4s")
CONTROL_MAGIC = b"ITLC"
CONTROL_HEADER = struct.Struct(">4sBBBBQHHI")
CONTROL_PROTOCOL_MAJOR = 1
CONTROL_PROTOCOL_MINOR = 56
CONTROL_KIND_REQUEST = 1
CONTROL_KIND_RESPONSE = 2
CONTROL_OPERATION_INTERACTIVE_EVIDENCE = 78
CONTROL_MAX_PACKET = 24 + 60 * 1024
CONTROL_EVIDENCE = struct.Struct(">QQ")
OPENED = struct.Struct(">16sQQQQ")
PACKET_OPEN = 1
PACKET_INPUT = 2
PACKET_CLOSE = 5
PACKET_OUTPUT_ACK = 6
PACKET_PING = 7
PACKET_OPENED = 32
PACKET_OUTPUT = 33
PACKET_EXIT = 35
PACKET_CLOSED = 37
PACKET_ERROR = 38
PACKET_PONG = 39
ERROR_UNAVAILABLE = 4
MAX_PACKET = 32 + 16 * 1024
SCHEMA = "iotox-ratox-terminal-probe-v1"
HEARTBEAT_SCHEMA = "iotox-ratox-heartbeat-probe-v1"
HEX_KEY = re.compile(r"[0-9A-Fa-f]{64}")


class ProbeError(RuntimeError):
    pass


@dataclass(frozen=True)
class Packet:
    kind: int
    stream: int
    sequence: int
    status: int
    payload: bytes


@dataclass(frozen=True)
class Traffic:
    executed: int
    total_wait_us: int


def monotonic_us() -> int:
    return time.monotonic_ns() // 1000


def encode(kind: int, stream: int, sequence: int = 0, payload: bytes = b"") -> bytes:
    if stream == 0 or len(payload) > 16 * 1024:
        raise ProbeError("invalid local terminal packet")
    return HEADER.pack(
        MAGIC, 1, 0, kind, 0, stream, sequence, 0, len(payload), b"\0" * 4
    ) + payload


def decode(data: bytes) -> Packet:
    if not 32 <= len(data) <= MAX_PACKET:
        raise ProbeError("local terminal packet has an invalid extent")
    magic, major, minor, kind, flags, stream, sequence, status, size, reserved = (
        HEADER.unpack(data[:32])
    )
    if (
        magic != MAGIC
        or major != 1
        or minor != 0
        or flags != 0
        or reserved != b"\0" * 4
        or len(data) != 32 + size
    ):
        raise ProbeError("local terminal packet is not canonical v1")
    return Packet(kind, stream, sequence, status, data[32:])


def receive(connection: socket.socket, stream: int, timeout: float) -> Packet:
    connection.settimeout(timeout)
    try:
        packet = decode(connection.recv(MAX_PACKET + 1))
    except TimeoutError as error:
        raise ProbeError("local terminal receive deadline elapsed") from error
    if packet.stream != stream:
        raise ProbeError("local terminal server changed the stream ID")
    if packet.kind == PACKET_ERROR:
        detail = packet.payload.decode("ascii", "replace")
        raise ProbeError(f"local terminal error {packet.status}: {detail}")
    return packet


def traffic(runtime: Path, request_id: int, timeout: float) -> Traffic:
    if request_id == 0 or request_id >= 1 << 64:
        raise ProbeError("local control request ID is out of range")
    request = CONTROL_HEADER.pack(
        CONTROL_MAGIC,
        CONTROL_PROTOCOL_MAJOR,
        CONTROL_PROTOCOL_MINOR,
        CONTROL_KIND_REQUEST,
        CONTROL_OPERATION_INTERACTIVE_EVIDENCE,
        request_id,
        0,
        0,
        0,
    )
    connection = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    connection.settimeout(timeout)
    try:
        connection.connect(str(runtime / "control.sock"))
        connection.sendall(request)
        response = connection.recv(CONTROL_MAX_PACKET + 1)
    except (OSError, TimeoutError) as error:
        raise ProbeError(f"live controller inspection failed: {error}") from error
    finally:
        connection.close()
    if not 24 <= len(response) <= CONTROL_MAX_PACKET:
        raise ProbeError("live controller inspection returned an invalid extent")
    (
        magic,
        major,
        minor,
        kind,
        operation,
        returned_id,
        status,
        reserved,
        payload_size,
    ) = CONTROL_HEADER.unpack(response[:24])
    if (
        magic != CONTROL_MAGIC
        or major != CONTROL_PROTOCOL_MAJOR
        or minor > CONTROL_PROTOCOL_MINOR
        or kind != CONTROL_KIND_RESPONSE
        or operation != CONTROL_OPERATION_INTERACTIVE_EVIDENCE
        or returned_id != request_id
        or reserved != 0
        or payload_size != len(response) - 24
    ):
        raise ProbeError("live transport evidence returned a noncanonical response")
    payload = response[24:]
    if status != 0:
        detail = payload.decode("ascii", "replace")
        raise ProbeError(
            f"live transport evidence failed with status {status}: {detail}"
        )
    if len(payload) != CONTROL_EVIDENCE.size:
        raise ProbeError("live transport evidence is not exactly 16 bytes")
    return Traffic(*CONTROL_EVIDENCE.unpack(payload))


def await_traffic(
    runtime: Path,
    expected: int,
    deadline: float,
    request_id: int,
) -> tuple[Traffic, int]:
    while time.monotonic() < deadline:
        observed = traffic(
            runtime,
            request_id,
            max(0.001, deadline - time.monotonic()),
        )
        request_id += 1
        if observed.executed == expected:
            return observed, request_id
        if observed.executed > expected:
            raise ProbeError("another interactive owner command contaminated the trial")
        time.sleep(0.001)
    raise ProbeError("interactive owner-command evidence deadline elapsed")


def render_copy(master: int, slave: int, payload: bytes, deadline: float) -> None:
    written = os.write(slave, payload)
    if written != len(payload):
        raise ProbeError("local render pseudoterminal accepted a partial write")
    rendered = bytearray()
    while len(rendered) < len(payload):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ProbeError("local render pseudoterminal deadline elapsed")
        readable, _, _ = select.select([master], [], [], remaining)
        if not readable:
            raise ProbeError("local render pseudoterminal deadline elapsed")
        rendered.extend(os.read(master, len(payload) - len(rendered)))
    if bytes(rendered) != payload:
        raise ProbeError("local render pseudoterminal changed terminal bytes")


def write_progress(path: Path, completed: int, maximum_round_trip_us: int) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        "\n".join(
            (
                "schema\tiotox-ratox-terminal-progress-v1",
                f"samples-completed\t{completed}",
                f"maximum-round-trip-us\t{maximum_round_trip_us}",
                "",
            )
        ),
        encoding="ascii",
    )
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)


def write_heartbeat(path: Path, peer_hex: str, rows: list[str]) -> None:
    rendered = "\n".join(
        (
            "peer-public-key-sha256\t"
            + hashlib.sha256(bytes.fromhex(peer_hex)).hexdigest(),
            f"samples\t{len(rows)}",
            f"schema\t{HEARTBEAT_SCHEMA}",
            *rows,
            "",
        )
    )
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(rendered, encoding="ascii")
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)


def circuit_churn_lifecycle(
    peer_hex: str,
    session: bytes,
    initial_observation: dict[str, str | int],
    incarnation: int,
    initial_generation: int,
    initial_input_sequence: int,
    initial_output_sequence: int,
    transitions: list[dict[str, object]],
    final_generation: int,
) -> dict[str, object]:
    return {
        "schema": "iotox-ratox-circuit-churn-probe-v2",
        "status": "passed",
        "peer_public_key_sha256": hashlib.sha256(
            bytes.fromhex(peer_hex)
        ).hexdigest(),
        "session_id_sha256": hashlib.sha256(session).hexdigest(),
        "initial": {
            **initial_observation,
            "incarnation": incarnation,
            "generation": initial_generation,
            "input_sequence": initial_input_sequence,
            "output_sequence": initial_output_sequence,
        },
        "transitions": transitions,
        "resume_count": sum(
            transition["outcome"] == "explicit-resume"
            for transition in transitions
        ),
        "final_generation": final_generation,
    }


def await_phase_release(directory: Path, ordinal: int, timeout: float) -> int:
    release = directory / f"ratox-release-after-{ordinal}"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            release.unlink()
            return monotonic_us()
        except FileNotFoundError:
            time.sleep(0.01)
    raise ProbeError(f"phase release after sample {ordinal} did not arrive")


def atomic_text(path: Path, value: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(value, encoding="ascii")
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)


def await_named_release(directory: Path, name: str, timeout: float) -> int:
    release = directory / name
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            release.unlink()
            return monotonic_us()
        except FileNotFoundError:
            time.sleep(0.01)
    raise ProbeError(f"route-loss release {name} did not arrive")


def publish_checkpoint(directory: Path, name: str, session: bytes) -> None:
    atomic_text(
        directory / name,
        "\n".join(
            (
                "schema\tiotox-ratox-route-loss-checkpoint-v1",
                f"phase\t{name}",
                "session-sha256\t" + hashlib.sha256(session).hexdigest(),
                "",
            )
        ),
    )


def key_values(output: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in output.splitlines():
        for field in line.split():
            if "=" not in field:
                continue
            key, value = field.split("=", 1)
            values.setdefault(key, value)
    return values


def iotox_observation(
    binary: str, runtime: Path, peer_hex: str, timeout: float
) -> dict[str, str | int]:
    def invoke(operation: str) -> str:
        try:
            completed = subprocess.run(
                [binary, "--runtime", str(runtime), operation, peer_hex],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
            )
        except (OSError, subprocess.SubprocessError) as error:
            raise ProbeError(f"iotox {operation} observation failed: {error}") from error
        return completed.stdout

    session_output = invoke("session")
    session = key_values(session_output)
    authority = key_values(invoke("authority-session"))
    try:
        peers = subprocess.run(
            [binary, "--runtime", str(runtime), "peers"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        ).stdout
    except (OSError, subprocess.SubprocessError) as error:
        raise ProbeError(f"iotox peers observation failed: {error}") from error
    peer = {}
    for line in peers.splitlines():
        candidate = key_values(line)
        if candidate.get("public-key", "").upper() == peer_hex.upper():
            peer = candidate
            break
    epoch = session.get("online-epoch", "0")
    if not epoch.isdecimal():
        raise ProbeError("session online epoch is not canonical decimal")
    return {
        "session_state": session.get("state", "absent"),
        "online_epoch": int(epoch),
        "connection": peer.get("connection", "absent"),
        "capability_observed": int("ratox-interactive-v1" in session_output),
        "claimant_proof_sent": int(authority.get("claimant-state") == "proof-sent"),
        "claimant_principal_present": int(
            re.fullmatch(r"[0-9A-Fa-f]{64}", authority.get("local-claimant-principal", ""))
            is not None
            and authority.get("local-claimant-principal") != "0" * 64
        ),
    }


def run_route_loss_probe(
    runtime: Path,
    peer_hex: str,
    output: Path,
    heartbeat_output: Path,
    lifecycle_output: Path,
    checkpoint_dir: Path,
    release_dir: Path,
    expected_connection: str,
    heartbeat_timeout: float,
    route_timeout: float,
    iotox_binary: str,
) -> None:
    if HEX_KEY.fullmatch(peer_hex) is None:
        raise ProbeError("peer must be exactly 64 hexadecimal characters")
    if expected_connection not in {"udp", "tcp"}:
        raise ProbeError("expected connection must be udp or tcp")
    if not 0.1 <= heartbeat_timeout <= 30.0:
        raise ProbeError("heartbeat timeout must be in 100..30000 ms")
    if not 1.0 <= route_timeout <= 600.0:
        raise ProbeError("route timeout must be in 1..600 seconds")

    stream = secrets.randbits(64) or 1
    peer = bytes.fromhex(peer_hex)
    connection = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    connection.settimeout(route_timeout)
    connection.connect(str(runtime / "terminal.sock"))
    connection.sendall(
        encode(
            PACKET_OPEN,
            stream,
            payload=peer + b"\0" * 16 + struct.pack(">HHB3x", 80, 24, 1),
        )
    )
    packet = receive(connection, stream, route_timeout)
    if packet.kind != PACKET_OPENED or len(packet.payload) != OPENED.size:
        raise ProbeError("route-loss OPEN did not return canonical OPENED")
    session, incarnation, generation, input_sequence, output_sequence = OPENED.unpack(
        packet.payload
    )
    initial_generation = generation
    if (
        not any(session)
        or incarnation == 0
        or generation == 0
        or input_sequence != 1
        or output_sequence != 1
    ):
        raise ProbeError("route-loss OPENED identity or initial byte position is invalid")

    terminal_rows: list[str] = []
    heartbeat_rows: list[str] = []
    master, slave = pty.openpty()
    tty.setraw(slave, termios.TCSANOW)

    def heartbeat(ordinal: int, active: socket.socket) -> None:
        started = monotonic_us()
        active.sendall(encode(PACKET_PING, stream))
        pong = receive(active, stream, route_timeout)
        finished = monotonic_us()
        if pong.kind != PACKET_PONG or pong.sequence != 0 or pong.status != 0 or pong.payload:
            raise ProbeError("route-loss heartbeat was not a canonical PONG")
        heartbeat_rows.append(
            f"sample\t{ordinal}\t{started}\t{finished}\t{session.hex()}"
        )

    def echo(ordinal: int, active: socket.socket, value: bytes) -> tuple[int, int]:
        nonlocal input_sequence, output_sequence
        started = monotonic_us()
        active.sendall(encode(PACKET_INPUT, stream, input_sequence, value))
        reply = receive(active, stream, route_timeout)
        returned = monotonic_us()
        if (
            reply.kind != PACKET_OUTPUT
            or reply.sequence != output_sequence
            or reply.payload != value
        ):
            raise ProbeError("route-loss PTY did not return the exact trial byte")
        render_copy(master, slave, reply.payload, time.monotonic() + route_timeout)
        rendered = monotonic_us()
        next_input = input_sequence + 1
        next_output = output_sequence + 1
        terminal_rows.append(
            "\t".join(
                (
                    "sample",
                    str(ordinal),
                    str(started),
                    str(returned),
                    str(rendered),
                    session.hex(),
                    str(input_sequence),
                    str(next_input),
                    str(output_sequence),
                    str(next_output),
                    "0",
                )
            )
        )
        active.sendall(encode(PACKET_OUTPUT_ACK, stream, next_output))
        input_sequence = next_input
        output_sequence = next_output
        return returned - started, rendered - returned

    try:
        time.sleep(0.25)
        initial = iotox_observation(
            iotox_binary, runtime, peer_hex, min(route_timeout, 10.0)
        )
        if (
            initial["session_state"] != "confirmed"
            or initial["connection"] != expected_connection
            or initial["online_epoch"] == 0
            or initial["capability_observed"] != 1
            or initial["claimant_proof_sent"] != 1
            or initial["claimant_principal_present"] != 1
        ):
            raise ProbeError("initial route-loss observation is not authenticated and ready")

        heartbeat(1, connection)
        baseline_terminal_us, baseline_render_us = echo(1, connection, b"A")
        publish_checkpoint(checkpoint_dir, "client.ratox-route-loss-attached", session)

        loss_release_us = await_named_release(
            release_dir, "ratox-route-loss-active", route_timeout
        )
        missed_heartbeat_started_us = monotonic_us()
        connection.sendall(encode(PACKET_PING, stream))
        connection.settimeout(heartbeat_timeout)
        try:
            unexpected = decode(connection.recv(MAX_PACKET + 1))
        except TimeoutError:
            unexpected = None
        if unexpected is not None:
            raise ProbeError("route-loss heartbeat unexpectedly received a terminal packet")
        missed_heartbeat_us = monotonic_us()
        heartbeat_loss = iotox_observation(
            iotox_binary, runtime, peer_hex, min(route_timeout, 10.0)
        )
        if (
            heartbeat_loss["session_state"] != "confirmed"
            or heartbeat_loss["connection"] != expected_connection
            or heartbeat_loss["online_epoch"] != initial["online_epoch"]
        ):
            raise ProbeError("heartbeat loss did not precede authoritative carrier loss")
        publish_checkpoint(
            checkpoint_dir, "client.ratox-route-loss-heartbeat-missed", session
        )

        connection.settimeout(route_timeout)
        try:
            lost = decode(connection.recv(MAX_PACKET + 1))
        except TimeoutError as error:
            raise ProbeError("authoritative route-loss terminal outcome timed out") from error
        route_lost_us = monotonic_us()
        if (
            lost.stream != stream
            or lost.kind != PACKET_ERROR
            or lost.status != ERROR_UNAVAILABLE
            or not lost.payload
        ):
            raise ProbeError("route loss did not produce exact unavailable terminal ERROR")
        connection.close()
        offline_deadline = time.monotonic() + 10.0
        offline: dict[str, str | int] = {}
        while time.monotonic() < offline_deadline:
            offline = iotox_observation(
                iotox_binary, runtime, peer_hex, min(route_timeout, 10.0)
            )
            if offline["session_state"] == "offline" and offline["connection"] == "offline":
                break
            time.sleep(0.05)
        if offline.get("session_state") != "offline" or offline.get("connection") != "offline":
            raise ProbeError("terminal route-loss outcome preceded no exact offline state")
        publish_checkpoint(checkpoint_dir, "client.ratox-route-loss-offline", session)

        recovery_release_us = await_named_release(
            release_dir, "ratox-route-loss-recover", route_timeout
        )
        ready_deadline = time.monotonic() + route_timeout
        recovered: dict[str, str | int] = {}
        while time.monotonic() < ready_deadline:
            recovered = iotox_observation(
                iotox_binary, runtime, peer_hex, min(route_timeout, 10.0)
            )
            if (
                recovered["session_state"] == "confirmed"
                and recovered["connection"] == expected_connection
                and recovered["online_epoch"] > initial["online_epoch"]
                and recovered["capability_observed"] == 1
                and recovered["claimant_proof_sent"] == 1
                and recovered["claimant_principal_present"] == 1
            ):
                break
            time.sleep(0.05)
        if not (
            recovered.get("session_state") == "confirmed"
            and recovered.get("connection") == expected_connection
            and isinstance(recovered.get("online_epoch"), int)
            and recovered["online_epoch"] > initial["online_epoch"]
            and recovered.get("capability_observed") == 1
            and recovered.get("claimant_proof_sent") == 1
            and recovered.get("claimant_principal_present") == 1
        ):
            raise ProbeError("route did not recover to an authenticated confirmed session")
        route_recovered_us = monotonic_us()

        connection = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        connection.settimeout(route_timeout)
        connection.connect(str(runtime / "terminal.sock"))
        connection.sendall(
            encode(
                PACKET_OPEN,
                stream,
                payload=peer + session + struct.pack(">HHB3x", 80, 24, 2),
            )
        )
        resumed = receive(connection, stream, route_timeout)
        resumed_us = monotonic_us()
        if resumed.kind != PACKET_OPENED or len(resumed.payload) != OPENED.size:
            raise ProbeError("route recovery did not return canonical resumed OPENED")
        (
            resumed_session,
            resumed_incarnation,
            resumed_generation,
            resumed_input,
            resumed_output,
        ) = OPENED.unpack(resumed.payload)
        if (
            resumed_session != session
            or resumed_incarnation != incarnation
            or resumed_generation != generation + 1
            or resumed_input != input_sequence
            or resumed_output != output_sequence
        ):
            raise ProbeError("Ratox resume changed identity or exact byte positions")

        heartbeat(2, connection)
        recovered_terminal_us, recovered_render_us = echo(2, connection, b"B")
        connection.sendall(encode(PACKET_CLOSE, stream))
        while True:
            terminal = receive(connection, stream, route_timeout)
            if terminal.kind in (PACKET_EXIT, PACKET_CLOSED):
                break
            raise ProbeError("route-loss terminal close returned an unexpected packet")

        peer_commitment = hashlib.sha256(peer).hexdigest()
        rendered_terminal = "\n".join(
            (
                f"peer-public-key-sha256\t{peer_commitment}",
                "samples\t2",
                f"schema\t{SCHEMA}",
                *terminal_rows,
                "",
            )
        )
        atomic_text(output, rendered_terminal)
        write_heartbeat(heartbeat_output, peer_hex, heartbeat_rows)
        lifecycle = {
            "schema": "iotox-ratox-route-loss-probe-v1",
            "status": "passed",
            "peer_public_key_sha256": peer_commitment,
            "session_id_sha256": hashlib.sha256(session).hexdigest(),
            "initial": {
                **initial,
                "incarnation": incarnation,
                "generation": generation,
                "input_sequence": 1,
                "output_sequence": 1,
                "heartbeat_us": int(heartbeat_rows[0].split("\t")[3])
                - int(heartbeat_rows[0].split("\t")[2]),
                "terminal_us": baseline_terminal_us,
                "render_us": baseline_render_us,
            },
            "loss": {
                "release_us": loss_release_us,
                "heartbeat_started_us": missed_heartbeat_started_us,
                "heartbeat_deadline_us": missed_heartbeat_us,
                "heartbeat_timeout_us": missed_heartbeat_us
                - missed_heartbeat_started_us,
                "carrier_at_heartbeat_timeout": heartbeat_loss["connection"],
                "session_state_at_heartbeat_timeout": heartbeat_loss["session_state"],
                "online_epoch_at_heartbeat_timeout": heartbeat_loss["online_epoch"],
                "controller_outcome_us": route_lost_us,
                "controller_outcome": "error-unavailable",
                "controller_error_detail_sha256": hashlib.sha256(lost.payload).hexdigest(),
                "offline": offline,
            },
            "recovery": {
                "release_us": recovery_release_us,
                "route_ready_us": route_recovered_us,
                "resume_opened_us": resumed_us,
                **recovered,
                "incarnation": resumed_incarnation,
                "generation": resumed_generation,
                "input_sequence": resumed_input,
                "output_sequence": resumed_output,
                "heartbeat_us": int(heartbeat_rows[1].split("\t")[3])
                - int(heartbeat_rows[1].split("\t")[2]),
                "terminal_us": recovered_terminal_us,
                "render_us": recovered_render_us,
            },
        }
        temporary = lifecycle_output.with_name(lifecycle_output.name + ".tmp")
        temporary.write_text(
            json.dumps(lifecycle, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.chmod(temporary, 0o600)
        os.replace(temporary, lifecycle_output)
    finally:
        os.close(master)
        os.close(slave)
        connection.close()


def run_probe(
    runtime: Path,
    peer_hex: str,
    samples: int,
    output: Path,
    timeout: float,
    progress: Path | None = None,
    heartbeat_output: Path | None = None,
    pause_after: frozenset[int] = frozenset(),
    release_dir: Path | None = None,
    sample_interval: float = 0.0,
    circuit_churn_output: Path | None = None,
    expected_connection: str | None = None,
    iotox_binary: str = "iotox",
    admission_output: Path | None = None,
    admission_origin_us: int | None = None,
) -> None:
    if HEX_KEY.fullmatch(peer_hex) is None:
        raise ProbeError("peer must be exactly 64 hexadecimal characters")
    if samples < 1 or samples > 100000:
        raise ProbeError("samples must be in 1..100000")
    if any(ordinal < 1 or ordinal >= samples for ordinal in pause_after):
        raise ProbeError("phase pauses must be in 1..samples-1")
    if pause_after and (progress is None or release_dir is None):
        raise ProbeError("phase pauses require progress and a release directory")
    if sample_interval < 0.0 or sample_interval > 60.0:
        raise ProbeError("sample interval must be in 0..60 seconds")
    if (admission_output is None) != (admission_origin_us is None):
        raise ProbeError(
            "admission output and its monotonic origin must be used together"
        )
    if admission_origin_us is not None and admission_origin_us <= 0:
        raise ProbeError("admission monotonic origin must be positive")
    if admission_output is not None and expected_connection not in {"udp", "tcp"}:
        raise ProbeError("admission evidence requires an expected connection")
    if circuit_churn_output is not None and (
        heartbeat_output is None
        or not pause_after
        or progress is None
        or release_dir is None
        or expected_connection not in {"udp", "tcp"}
    ):
        raise ProbeError(
            "circuit churn requires heartbeat/progress/pauses/releases and "
            "an expected connection"
        )
    probe_started_us = monotonic_us()
    connection = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    connection.settimeout(timeout)
    connection.connect(str(runtime / "terminal.sock"))
    socket_connected_us = monotonic_us()
    stream = secrets.randbits(64) or 1
    open_payload = (
        bytes.fromhex(peer_hex) + b"\0" * 16 + struct.pack(">HHB3x", 80, 24, 1)
    )
    open_sent_us = monotonic_us()
    connection.sendall(encode(PACKET_OPEN, stream, payload=open_payload))
    packet = receive(connection, stream, timeout)
    opened_us = monotonic_us()
    if packet.kind != PACKET_OPENED or len(packet.payload) != OPENED.size:
        raise ProbeError("local terminal server did not return canonical OPENED")
    session, incarnation, generation, input_sequence, output_sequence = OPENED.unpack(
        packet.payload
    )
    if (
        not any(session)
        or incarnation == 0
        or generation == 0
        or input_sequence == 0
        or output_sequence == 0
    ):
        raise ProbeError("local terminal OPENED carries zero identity or sequence")
    initial_generation = generation
    initial_input_sequence = input_sequence
    initial_output_sequence = output_sequence
    admission_observation = (
        iotox_observation(iotox_binary, runtime, peer_hex, min(timeout, 10.0))
        if admission_output is not None
        else {}
    )
    if admission_output is not None and not (
        admission_observation.get("session_state") == "confirmed"
        and admission_observation.get("connection") == expected_connection
        and isinstance(admission_observation.get("online_epoch"), int)
        and admission_observation["online_epoch"] > 0
        and admission_observation.get("capability_observed") == 1
        and admission_observation.get("claimant_proof_sent") == 1
        and admission_observation.get("claimant_principal_present") == 1
    ):
        raise ProbeError("fresh admission is not bound to authenticated route truth")

    master, slave = pty.openpty()
    tty.setraw(slave, termios.TCSANOW)
    rows: list[str] = []
    heartbeat_rows: list[str] = []
    churn_transitions: list[dict[str, object]] = []
    maximum_round_trip_us = 0
    try:
        # The fixed lab profile enters raw/no-echo mode before the first byte.
        time.sleep(0.25)
        connection.setblocking(False)
        try:
            unexpected = connection.recv(MAX_PACKET + 1)
        except BlockingIOError:
            unexpected = b""
        finally:
            connection.setblocking(True)
        if unexpected:
            raise ProbeError("terminal profile emitted bytes before the first trial")

        control_request_id = secrets.randbits(63) or 1
        baseline = traffic(runtime, control_request_id, timeout)
        control_request_id += 1
        initial_observation = (
            iotox_observation(iotox_binary, runtime, peer_hex, min(timeout, 10.0))
            if circuit_churn_output is not None
            else {}
        )
        if circuit_churn_output is not None and not (
            initial_observation.get("session_state") == "confirmed"
            and initial_observation.get("connection") == expected_connection
            and isinstance(initial_observation.get("online_epoch"), int)
            and initial_observation["online_epoch"] > 0
            and initial_observation.get("capability_observed") == 1
            and initial_observation.get("claimant_proof_sent") == 1
            and initial_observation.get("claimant_principal_present") == 1
        ):
            raise ProbeError("initial circuit-churn session is not authenticated and ready")
        online_epoch = int(initial_observation.get("online_epoch", 0))
        for ordinal in range(1, samples + 1):
            if heartbeat_output is not None:
                heartbeat_start_us = monotonic_us()
                connection.sendall(encode(PACKET_PING, stream))
                heartbeat = receive(connection, stream, timeout)
                heartbeat_pong_us = monotonic_us()
                if (
                    heartbeat.kind != PACKET_PONG
                    or heartbeat.sequence != 0
                    or heartbeat.status != 0
                    or heartbeat.payload
                ):
                    raise ProbeError("remote Ratox heartbeat was not a canonical PONG")
                heartbeat_rows.append(
                    "\t".join(
                        (
                            "sample",
                            str(ordinal),
                            str(heartbeat_start_us),
                            str(heartbeat_pong_us),
                            session.hex(),
                        )
                    )
                )
            value = bytes((0x41 + ((ordinal - 1) % 26),))
            controller_input_us = monotonic_us()
            connection.sendall(encode(PACKET_INPUT, stream, input_sequence, value))
            packet = receive(connection, stream, timeout)
            controller_output_us = monotonic_us()
            if (
                packet.kind != PACKET_OUTPUT
                or packet.sequence != output_sequence
                or packet.payload != value
            ):
                raise ProbeError("remote PTY did not return the exact trial byte")
            deadline = time.monotonic() + timeout
            render_copy(master, slave, packet.payload, deadline)
            controller_render_us = monotonic_us()
            after_input, control_request_id = await_traffic(
                runtime,
                baseline.executed + 1,
                deadline,
                control_request_id,
            )
            if after_input.total_wait_us < baseline.total_wait_us:
                raise ProbeError("interactive queue-wait total moved backwards")
            next_input = input_sequence + 1
            next_output = output_sequence + 1
            rows.append(
                "\t".join(
                    (
                        "sample",
                        str(ordinal),
                        str(controller_input_us),
                        str(controller_output_us),
                        str(controller_render_us),
                        session.hex(),
                        str(input_sequence),
                        str(next_input),
                        str(output_sequence),
                        str(next_output),
                        str(after_input.total_wait_us - baseline.total_wait_us),
                    )
                )
            )
            maximum_round_trip_us = max(
                maximum_round_trip_us, controller_output_us - controller_input_us
            )
            connection.sendall(encode(PACKET_OUTPUT_ACK, stream, next_output))
            baseline, control_request_id = await_traffic(
                runtime,
                after_input.executed + 1,
                time.monotonic() + timeout,
                control_request_id,
            )
            input_sequence = next_input
            output_sequence = next_output
            if progress is not None:
                write_progress(progress, ordinal, maximum_round_trip_us)
            if ordinal in pause_after:
                assert release_dir is not None
                release_us = await_phase_release(release_dir, ordinal, timeout)
                if circuit_churn_output is not None:
                    connection.settimeout(timeout)
                    connection.sendall(encode(PACKET_PING, stream))
                    observed = decode(connection.recv(MAX_PACKET + 1))
                    observed_us = monotonic_us()
                    if (
                        observed.stream == stream
                        and observed.kind == PACKET_PONG
                        and observed.sequence == 0
                        and observed.status == 0
                        and not observed.payload
                    ):
                        continuous = iotox_observation(
                            iotox_binary, runtime, peer_hex, min(timeout, 10.0)
                        )
                        if not (
                            continuous["session_state"] == "confirmed"
                            and continuous["connection"] == expected_connection
                            and continuous["online_epoch"] == online_epoch
                            and continuous["capability_observed"] == 1
                            and continuous["claimant_proof_sent"] == 1
                            and continuous["claimant_principal_present"] == 1
                        ):
                            raise ProbeError(
                                "circuit churn PONG did not preserve exact session truth"
                            )
                        churn_transitions.append(
                            {
                                "ordinal": ordinal,
                                "outcome": "attachment-continuous",
                                "release_us": release_us,
                                "observed_us": observed_us,
                                "controller_error_detail_sha256": "",
                                "previous_online_epoch": online_epoch,
                                "recovered_online_epoch": online_epoch,
                                "route_ready_us": observed_us,
                                "resume_opened_us": 0,
                                "generation_before": generation,
                                "generation_after": generation,
                                "input_sequence": input_sequence,
                                "output_sequence": output_sequence,
                                "connection": continuous["connection"],
                                "capability_observed": continuous[
                                    "capability_observed"
                                ],
                                "claimant_proof_sent": continuous[
                                    "claimant_proof_sent"
                                ],
                                "claimant_principal_present": continuous[
                                    "claimant_principal_present"
                                ],
                            }
                        )
                    elif (
                        observed.stream == stream
                        and observed.kind == PACKET_ERROR
                        and observed.status == ERROR_UNAVAILABLE
                        and observed.payload
                    ):
                        connection.close()
                        ready_deadline = time.monotonic() + timeout
                        recovered: dict[str, str | int] = {}
                        while time.monotonic() < ready_deadline:
                            recovered = iotox_observation(
                                iotox_binary, runtime, peer_hex, min(timeout, 10.0)
                            )
                            if (
                                recovered["session_state"] == "confirmed"
                                and recovered["connection"] == expected_connection
                                and recovered["online_epoch"] > online_epoch
                                and recovered["capability_observed"] == 1
                                and recovered["claimant_proof_sent"] == 1
                                and recovered["claimant_principal_present"] == 1
                            ):
                                break
                            time.sleep(0.05)
                        if not (
                            recovered.get("session_state") == "confirmed"
                            and recovered.get("connection") == expected_connection
                            and isinstance(recovered.get("online_epoch"), int)
                            and recovered["online_epoch"] > online_epoch
                            and recovered.get("capability_observed") == 1
                            and recovered.get("claimant_proof_sent") == 1
                            and recovered.get("claimant_principal_present") == 1
                        ):
                            raise ProbeError(
                                "circuit churn did not recover an authenticated higher epoch"
                            )
                        route_ready_us = monotonic_us()
                        resumed_connection = socket.socket(
                            socket.AF_UNIX, socket.SOCK_SEQPACKET
                        )
                        resumed_connection.settimeout(timeout)
                        resumed_connection.connect(str(runtime / "terminal.sock"))
                        resumed_connection.sendall(
                            encode(
                                PACKET_OPEN,
                                stream,
                                payload=(
                                    bytes.fromhex(peer_hex)
                                    + session
                                    + struct.pack(">HHB3x", 80, 24, 2)
                                ),
                            )
                        )
                        resumed = receive(resumed_connection, stream, timeout)
                        resume_opened_us = monotonic_us()
                        if (
                            resumed.kind != PACKET_OPENED
                            or len(resumed.payload) != OPENED.size
                        ):
                            raise ProbeError(
                                "circuit churn resume did not return canonical OPENED"
                            )
                        (
                            resumed_session,
                            resumed_incarnation,
                            resumed_generation,
                            resumed_input,
                            resumed_output,
                        ) = OPENED.unpack(resumed.payload)
                        if (
                            resumed_session != session
                            or resumed_incarnation != incarnation
                            or resumed_generation != generation + 1
                            or resumed_input != input_sequence
                            or resumed_output != output_sequence
                        ):
                            raise ProbeError(
                                "circuit churn resume changed session or exact byte positions"
                            )
                        churn_transitions.append(
                            {
                                "ordinal": ordinal,
                                "outcome": "explicit-resume",
                                "release_us": release_us,
                                "observed_us": observed_us,
                                "controller_error_detail_sha256": hashlib.sha256(
                                    observed.payload
                                ).hexdigest(),
                                "previous_online_epoch": online_epoch,
                                "recovered_online_epoch": recovered["online_epoch"],
                                "route_ready_us": route_ready_us,
                                "resume_opened_us": resume_opened_us,
                                "generation_before": generation,
                                "generation_after": resumed_generation,
                                "input_sequence": resumed_input,
                                "output_sequence": resumed_output,
                                "connection": recovered["connection"],
                                "capability_observed": recovered[
                                    "capability_observed"
                                ],
                                "claimant_proof_sent": recovered[
                                    "claimant_proof_sent"
                                ],
                                "claimant_principal_present": recovered[
                                    "claimant_principal_present"
                                ],
                            }
                        )
                        connection = resumed_connection
                        generation = resumed_generation
                        online_epoch = int(recovered["online_epoch"])
                    else:
                        raise ProbeError(
                            "circuit churn produced neither canonical PONG nor unavailable"
                        )
            if ordinal != samples and sample_interval > 0.0:
                time.sleep(sample_interval)

        connection.sendall(encode(PACKET_CLOSE, stream))
        # The production CLI treats either terminal result as completion. A
        # process EXIT_STATUS finalizes the remote session, so no later CLOSED
        # packet is required or implied.
        while True:
            packet = receive(connection, stream, timeout)
            if packet.kind in (PACKET_EXIT, PACKET_CLOSED):
                break
            raise ProbeError("terminal close returned an unexpected packet")
    finally:
        os.close(master)
        os.close(slave)
        connection.close()

    rendered = "\n".join(
        (
            "peer-public-key-sha256\t"
            + hashlib.sha256(bytes.fromhex(peer_hex)).hexdigest(),
            f"samples\t{samples}",
            f"sample-interval-ms\t{round(sample_interval * 1000)}",
            f"schema\t{SCHEMA}",
            *rows,
            "",
        )
    )
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(rendered, encoding="ascii")
    os.chmod(temporary, 0o600)
    os.replace(temporary, output)
    if admission_output is not None:
        assert admission_origin_us is not None
        capture_sha256 = hashlib.sha256(output.read_bytes()).hexdigest()
        admission = "\n".join(
            (
                "schema\tiotox-ratox-admission-evidence-v1",
                f"origin-us\t{admission_origin_us}",
                f"probe-start-us\t{probe_started_us}",
                f"socket-connected-us\t{socket_connected_us}",
                f"open-sent-us\t{open_sent_us}",
                f"opened-us\t{opened_us}",
                f"origin-to-open-sent-us\t{open_sent_us - admission_origin_us}",
                f"origin-to-opened-us\t{opened_us - admission_origin_us}",
                f"open-round-trip-us\t{opened_us - open_sent_us}",
                f"connection\t{admission_observation['connection']}",
                f"online-epoch\t{admission_observation['online_epoch']}",
                "capability-observed\t1",
                "claimant-proof-sent\t1",
                "claimant-principal-present\t1",
                "session-sha256\t" + hashlib.sha256(session).hexdigest(),
                f"incarnation\t{incarnation}",
                f"generation\t{initial_generation}",
                f"initial-input-sequence\t{initial_input_sequence}",
                f"initial-output-sequence\t{initial_output_sequence}",
                f"samples\t{samples}",
                f"capture-sha256\t{capture_sha256}",
                "",
            )
        )
        temporary = admission_output.with_name(admission_output.name + ".tmp")
        temporary.write_text(admission, encoding="ascii")
        os.chmod(temporary, 0o600)
        os.replace(temporary, admission_output)
    if heartbeat_output is not None:
        write_heartbeat(heartbeat_output, peer_hex, heartbeat_rows)
    if circuit_churn_output is not None:
        lifecycle = circuit_churn_lifecycle(
            peer_hex,
            session,
            initial_observation,
            incarnation,
            initial_generation,
            initial_input_sequence,
            initial_output_sequence,
            churn_transitions,
            generation,
        )
        temporary = circuit_churn_output.with_name(
            circuit_churn_output.name + ".tmp"
        )
        temporary.write_text(
            json.dumps(lifecycle, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.chmod(temporary, 0o600)
        os.replace(temporary, circuit_churn_output)


def self_test() -> None:
    stream = 7
    encoded = encode(PACKET_INPUT, stream, 9, b"Q")
    assert decode(encoded) == Packet(PACKET_INPUT, stream, 9, 0, b"Q")
    try:
        decode(encoded + b"x")
    except ProbeError:
        pass
    else:
        raise AssertionError("noncanonical extent was accepted")
    control = CONTROL_HEADER.pack(
        CONTROL_MAGIC,
        CONTROL_PROTOCOL_MAJOR,
        CONTROL_PROTOCOL_MINOR,
        CONTROL_KIND_REQUEST,
        CONTROL_OPERATION_INTERACTIVE_EVIDENCE,
        11,
        0,
        0,
        0,
    )
    assert len(control) == 24
    assert CONTROL_HEADER.unpack(control)[5] == 11
    assert Traffic(*CONTROL_EVIDENCE.unpack(CONTROL_EVIDENCE.pack(9, 17))) == (
        Traffic(9, 17)
    )
    source_header = (
        Path(__file__).resolve().parents[1]
        / "include/iotox/local/control_protocol.hpp"
    )
    if source_header.is_file():
        source = source_header.read_text(encoding="utf-8")
        expected_minor = re.search(
            r"kControlProtocolMinor\s*=\s*([0-9]+)U", source
        )
        assert expected_minor is not None
        assert int(expected_minor.group(1)) == CONTROL_PROTOCOL_MINOR
    master, slave = pty.openpty()
    try:
        tty.setraw(slave, termios.TCSANOW)
        render_copy(master, slave, b"probe", time.monotonic() + 1)
    finally:
        os.close(master)
        os.close(slave)
    with tempfile.TemporaryDirectory(prefix="iotox-ratox-heartbeat-test.") as root:
        heartbeat = Path(root) / "heartbeat.tsv"
        write_heartbeat(heartbeat, "AB" * 32, ["sample\t1\t10\t20\t" + "01" * 16])
        assert heartbeat.read_text(encoding="ascii").splitlines()[1:] == [
            "samples\t1",
            f"schema\t{HEARTBEAT_SCHEMA}",
            "sample\t1\t10\t20\t" + "01" * 16,
        ]
        checkpoint = Path(root) / "checkpoint"
        publish_checkpoint(Path(root), "checkpoint", bytes.fromhex("01" * 16))
        assert checkpoint.read_text(encoding="ascii").splitlines() == [
            "schema\tiotox-ratox-route-loss-checkpoint-v1",
            "phase\tcheckpoint",
            "session-sha256\t"
            + hashlib.sha256(bytes.fromhex("01" * 16)).hexdigest(),
        ]
        assert key_values("state=confirmed online-epoch=2\n") == {
            "state": "confirmed",
            "online-epoch": "2",
        }
        lifecycle = circuit_churn_lifecycle(
            "AB" * 32,
            bytes.fromhex("01" * 16),
            {
                "session_state": "confirmed",
                "connection": "tcp",
                "online_epoch": 7,
                "capability_observed": 1,
                "claimant_proof_sent": 1,
                "claimant_principal_present": 1,
            },
            11,
            1,
            1,
            1,
            [
                {"outcome": "attachment-continuous"},
                {"outcome": "explicit-resume"},
            ],
            2,
        )
        assert lifecycle["initial"] == {
            "session_state": "confirmed",
            "connection": "tcp",
            "online_epoch": 7,
            "capability_observed": 1,
            "claimant_proof_sent": 1,
            "claimant_principal_present": 1,
            "incarnation": 11,
            "generation": 1,
            "input_sequence": 1,
            "output_sequence": 1,
        }
        assert lifecycle["resume_count"] == 1
        assert lifecycle["final_generation"] == 2
    print("ratox-terminal probe self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--peer")
    parser.add_argument("--samples", type=int, default=40)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--progress", type=Path)
    parser.add_argument("--heartbeat-output", type=Path)
    parser.add_argument("--route-loss-output", type=Path)
    parser.add_argument("--circuit-churn-output", type=Path)
    parser.add_argument("--admission-output", type=Path)
    parser.add_argument("--admission-origin-us", type=int)
    parser.add_argument("--checkpoint-dir", type=Path)
    parser.add_argument("--expected-connection", choices=("udp", "tcp"))
    parser.add_argument("--heartbeat-timeout-ms", type=int, default=2000)
    parser.add_argument("--iotox-binary", default="iotox")
    parser.add_argument("--pause-after", action="append", type=int, default=[])
    parser.add_argument("--release-dir", type=Path)
    parser.add_argument("--sample-interval-ms", type=int, default=0)
    parser.add_argument("--timeout-ms", type=int, default=5000)
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
        return 0
    if arguments.runtime is None or arguments.peer is None or arguments.output is None:
        parser.error("--runtime, --peer, and --output are required")
    maximum_timeout_ms = 60000
    if (
        arguments.route_loss_output is not None
        or arguments.circuit_churn_output is not None
    ):
        maximum_timeout_ms = 600000
    elif arguments.pause_after:
        maximum_timeout_ms = 180000
    if arguments.timeout_ms < 1 or arguments.timeout_ms > maximum_timeout_ms:
        parser.error(f"--timeout-ms must be in 1..{maximum_timeout_ms}")
    if arguments.sample_interval_ms < 0 or arguments.sample_interval_ms > 60000:
        parser.error("--sample-interval-ms must be in 0..60000")
    try:
        output = arguments.output.resolve()
        progress = (
            arguments.progress.resolve()
            if arguments.progress is not None
            else None
        )
        heartbeat_output = (
            arguments.heartbeat_output.resolve()
            if arguments.heartbeat_output is not None
            else None
        )
        route_loss_output = (
            arguments.route_loss_output.resolve()
            if arguments.route_loss_output is not None
            else None
        )
        circuit_churn_output = (
            arguments.circuit_churn_output.resolve()
            if arguments.circuit_churn_output is not None
            else None
        )
        admission_output = (
            arguments.admission_output.resolve()
            if arguments.admission_output is not None
            else None
        )
        checkpoint_dir = (
            arguments.checkpoint_dir.resolve()
            if arguments.checkpoint_dir is not None
            else None
        )
        pause_after = frozenset(arguments.pause_after)
        if len(pause_after) != len(arguments.pause_after):
            raise ProbeError("phase pauses must be unique")
        release_dir = (
            arguments.release_dir.resolve()
            if arguments.release_dir is not None
            else None
        )
        if route_loss_output is not None and circuit_churn_output is not None:
            raise ProbeError("route-loss and circuit-churn modes are mutually exclusive")
        if route_loss_output is None and bool(pause_after) != (release_dir is not None):
            raise ProbeError("phase pauses and release directory must be used together")
        if (
            progress == output
            or (
                heartbeat_output is not None
                and heartbeat_output in {output, progress}
            )
            or (
                route_loss_output is not None
                and route_loss_output in {output, progress, heartbeat_output}
            )
            or (
                circuit_churn_output is not None
                and circuit_churn_output
                in {output, progress, heartbeat_output, route_loss_output}
            )
            or (
                admission_output is not None
                and admission_output
                in {
                    output,
                    progress,
                    heartbeat_output,
                    route_loss_output,
                    circuit_churn_output,
                }
            )
        ):
            raise ProbeError("probe output paths must be distinct")
        if route_loss_output is not None:
            if (
                heartbeat_output is None
                or checkpoint_dir is None
                or release_dir is None
                or arguments.expected_connection is None
                or progress is not None
                or pause_after
                or admission_output is not None
                or arguments.admission_origin_us is not None
            ):
                raise ProbeError(
                    "route-loss mode requires heartbeat output, checkpoint/release "
                    "directories, and expected connection without progress/phase pauses"
                )
            run_route_loss_probe(
                arguments.runtime.resolve(),
                arguments.peer,
                output,
                heartbeat_output,
                route_loss_output,
                checkpoint_dir,
                release_dir,
                arguments.expected_connection,
                arguments.heartbeat_timeout_ms / 1000,
                arguments.timeout_ms / 1000,
                arguments.iotox_binary,
            )
            return 0
        run_probe(
            arguments.runtime.resolve(),
            arguments.peer,
            arguments.samples,
            output,
            arguments.timeout_ms / 1000,
            progress,
            heartbeat_output,
            pause_after,
            release_dir,
            arguments.sample_interval_ms / 1000,
            circuit_churn_output,
            arguments.expected_connection,
            arguments.iotox_binary,
            admission_output,
            arguments.admission_origin_us,
        )
    except (OSError, ProbeError) as error:
        print(f"ratox-terminal probe: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
