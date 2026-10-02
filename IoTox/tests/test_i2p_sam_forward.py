#!/usr/bin/env python3
"""Process test for the strict persistent I2P SAM service forward."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path


PUBLIC_BYTES = bytes(range(256)) + bytes(range(128))
PRIVATE_BYTES = PUBLIC_BYTES + bytes(range(64))
PAYLOAD = b"raw-i2p-service-stream"
REPLY = b"tox-relay-accepted"


def i2p_base64(value: bytes) -> str:
    encoded = base64.b64encode(value).decode("ascii")
    return encoded.translate(str.maketrans("+/", "-~"))


PUBLIC = i2p_base64(PUBLIC_BYTES)
PRIVATE = i2p_base64(PRIVATE_BYTES)
DESTINATION = (
    base64.b32encode(hashlib.sha256(PUBLIC_BYTES).digest())
    .decode("ascii")
    .lower()
    .rstrip("=")
    + ".b32.i2p"
)


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise RuntimeError(detail)


def receive_exact(stream: socket.socket, size: int) -> bytes:
    output = bytearray()
    while len(output) < size:
        block = stream.recv(size - len(output))
        require(bool(block), "unexpected end of stream")
        output.extend(block)
    return bytes(output)


def receive_line(stream: socket.socket) -> str:
    output = bytearray()
    while True:
        byte = stream.recv(1)
        require(bool(byte), "mock SAM received a partial line")
        if byte == b"\n":
            return output.decode("ascii")
        output.extend(byte)


class TargetService:
    def __init__(self) -> None:
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen(8)
        self.listener.settimeout(0.2)
        self.endpoint = self.listener.getsockname()[:2]
        self.stopping = threading.Event()
        self.payloads: list[bytes] = []
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.serve, daemon=True)
        self.thread.start()

    def serve(self) -> None:
        while not self.stopping.is_set():
            try:
                connection, _source = self.listener.accept()
            except TimeoutError:
                continue
            except OSError:
                return
            with connection:
                payload = receive_exact(connection, len(PAYLOAD))
                with self.lock:
                    self.payloads.append(payload)
                connection.sendall(REPLY)

    def close(self) -> None:
        self.stopping.set()
        self.listener.close()
        self.thread.join(timeout=2.0)


class MockSam:
    def __init__(self, target: TargetService) -> None:
        self.target = target
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen(16)
        self.listener.settimeout(0.2)
        self.endpoint = self.listener.getsockname()[:2]
        self.stopping = threading.Event()
        self.lock = threading.Lock()
        self.sessions: dict[str, socket.socket] = {}
        self.forwards: dict[str, socket.socket] = {}
        self.transcript: list[str] = []
        self.destination_generations = 0
        self.forward_generations = 0
        self.forward_results: list[bytes] = []
        self.workers: list[threading.Thread] = []
        self.thread = threading.Thread(target=self.serve, daemon=True)
        self.thread.start()

    def serve(self) -> None:
        while not self.stopping.is_set():
            try:
                connection, _source = self.listener.accept()
            except TimeoutError:
                continue
            except OSError:
                return
            worker = threading.Thread(
                target=self.handle, args=(connection,), daemon=True
            )
            self.workers.append(worker)
            worker.start()

    def append(self, line: str) -> None:
        with self.lock:
            self.transcript.append(line)

    def simulate_forward(self) -> None:
        try:
            with socket.create_connection(self.target.endpoint, timeout=5.0) as stream:
                stream.sendall(PAYLOAD)
                result = receive_exact(stream, len(REPLY))
            with self.lock:
                self.forward_results.append(result)
        except (OSError, RuntimeError):
            pass

    def handle(self, connection: socket.socket) -> None:
        role = ""
        session_id = ""
        with connection:
            try:
                hello = receive_line(connection)
                self.append(hello)
                require(
                    hello == "HELLO VERSION MIN=3.1 MAX=3.1",
                    "SAM version request drifted",
                )
                connection.sendall(b"HELLO REPLY VERSION=3.1 RESULT=OK\n")
                command = receive_line(connection)
                self.append(command)
                if command == "DEST GENERATE SIGNATURE_TYPE=7":
                    with self.lock:
                        self.destination_generations += 1
                    connection.sendall(
                        f"DEST REPLY PUB={PUBLIC} PRIV={PRIVATE}\n".encode("ascii")
                    )
                    return
                session_match = re.fullmatch(
                    r"SESSION CREATE ID=(iotox_forward_[0-9a-f]{20}) "
                    + re.escape(
                        "STYLE=STREAM DESTINATION="
                        + PRIVATE
                        + " i2cp.leaseSetEncType=4 inbound.quantity=2 "
                        "outbound.quantity=2 i2p.streaming.profile=2"
                    ),
                    command,
                )
                if session_match:
                    role = "session"
                    session_id = session_match.group(1)
                    with self.lock:
                        require(session_id not in self.sessions, "duplicate session ID")
                        self.sessions[session_id] = connection
                    connection.sendall(
                        f"SESSION STATUS RESULT=OK DESTINATION={PRIVATE}\n".encode(
                            "ascii"
                        )
                    )
                else:
                    forward_match = re.fullmatch(
                        r"STREAM FORWARD ID=(iotox_forward_[0-9a-f]{20}) "
                        + re.escape(
                            f"PORT={self.target.endpoint[1]} "
                            "HOST=127.0.0.1 SILENT=true"
                        ),
                        command,
                    )
                    require(forward_match is not None, "SAM command drifted")
                    role = "forward"
                    session_id = forward_match.group(1)
                    with self.lock:
                        require(session_id in self.sessions, "forward lacks a session")
                        self.forwards[session_id] = connection
                        self.forward_generations += 1
                    connection.sendall(b"STREAM STATUS RESULT=OK\n")
                    threading.Thread(
                        target=self.simulate_forward, daemon=True
                    ).start()
                while not self.stopping.is_set():
                    if not connection.recv(1):
                        return
            except (ConnectionError, OSError, RuntimeError):
                pass
            finally:
                with self.lock:
                    if role == "session" and self.sessions.get(session_id) is connection:
                        del self.sessions[session_id]
                    if role == "forward" and self.forwards.get(session_id) is connection:
                        del self.forwards[session_id]

    def suspend(self) -> None:
        with self.lock:
            streams = [*self.sessions.values(), *self.forwards.values()]
        require(len(streams) == 2, "mock SAM lacks one complete forward generation")
        for stream in streams:
            try:
                stream.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            stream.close()

    def wait_forwards(self, count: int, timeout: float = 5.0) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with self.lock:
                if (
                    self.forward_generations >= count
                    and len(self.forward_results) >= count
                ):
                    return
            time.sleep(0.02)
        raise RuntimeError(f"timed out waiting for {count} SAM forwards")

    def close(self) -> None:
        self.stopping.set()
        with self.lock:
            streams = [*self.sessions.values(), *self.forwards.values()]
        for stream in streams:
            try:
                stream.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            stream.close()
        self.listener.close()
        self.thread.join(timeout=2.0)
        for worker in self.workers:
            worker.join(timeout=2.0)


def start_forward(
    script: Path,
    mock: MockSam,
    target: TargetService,
    key: Path,
    audit: Path,
) -> tuple[subprocess.Popen[str], str]:
    process = subprocess.Popen(
        [
            sys.executable,
            str(script),
            "--sam",
            f"{mock.endpoint[0]}:{mock.endpoint[1]}",
            "--target",
            f"{target.endpoint[0]}:{target.endpoint[1]}",
            "--destination-key",
            str(key),
            "--audit",
            str(audit),
            "--startup-timeout",
            "5",
            "--command-timeout",
            "5",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    require(process.stdout is not None, "forward stdout is absent")
    ready = process.stdout.readline().strip()
    require(ready == f"ready={DESTINATION}", f"forward not ready: {ready}")
    return process, ready


def stop_forward(process: subprocess.Popen[str]) -> tuple[str, str]:
    process.terminate()
    output, errors = process.communicate(timeout=5.0)
    require(process.returncode == 0, f"SAM forward failed: {errors}")
    return output, errors


def load_audit(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text("ascii").splitlines()]


def reject(script: Path, arguments: list[str], phrase: str) -> None:
    result = subprocess.run(
        [sys.executable, str(script), *arguments],
        text=True,
        capture_output=True,
        timeout=5.0,
        check=False,
    )
    require(
        result.returncode != 0 and phrase in result.stderr,
        f"invalid configuration was not rejected: {result.stderr}",
    )


def main() -> int:
    require(len(sys.argv) == 2, "expected I2P SAM forward script path")
    script = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix="iotox-i2p-sam-forward-") as raw_root:
        root = Path(raw_root)
        os.chmod(root, 0o700)
        target = TargetService()
        mock = MockSam(target)
        key = root / "service.destination"
        first_audit = root / "first.audit.jsonl"
        process, first_ready = start_forward(script, mock, target, key, first_audit)
        try:
            mock.wait_forwards(1)
            mock.suspend()
            require(process.stdout is not None, "forward stdout is absent")
            recovery = process.stdout.readline().strip()
            require(
                recovery == "recovered-generation=2",
                f"forward did not recover exactly: {recovery}",
            )
            mock.wait_forwards(2)
        finally:
            first_output, first_errors = stop_forward(process)
        require("generations=2 losses=1" in first_output, first_errors)
        require(stat.S_IMODE(key.stat().st_mode) == 0o600, "key mode drifted")
        key_contents = key.read_text("ascii")
        require(PRIVATE in key_contents and PUBLIC in key_contents, "key was not retained")

        second_audit = root / "second.audit.jsonl"
        second, second_ready = start_forward(
            script, mock, target, key, second_audit
        )
        try:
            mock.wait_forwards(3)
        finally:
            second_output, second_errors = stop_forward(second)
        require("generations=1 losses=0" in second_output, second_errors)
        require(first_ready == second_ready, "persistent Destination changed on restart")

        first_records = load_audit(first_audit)
        second_records = load_audit(second_audit)
        require(
            [record["outcome"] for record in first_records]
            == ["created", "ready", "lost", "ready"],
            f"first lifecycle drifted: {first_records}",
        )
        require(
            [record["outcome"] for record in second_records] == ["loaded", "ready"],
            f"second lifecycle drifted: {second_records}",
        )
        all_records = first_records + second_records
        commitments = {record["destination_sha256"] for record in all_records}
        require(
            len(commitments) == 1
            and all(DESTINATION not in json.dumps(record) for record in all_records)
            and all(PRIVATE not in json.dumps(record) for record in all_records),
            "content-free destination audit drifted",
        )
        with mock.lock:
            transcript = list(mock.transcript)
            generations = mock.destination_generations
            forward_results = list(mock.forward_results)
        require(generations == 1, "restart generated a second Destination")
        require(
            sum(line == "DEST GENERATE SIGNATURE_TYPE=7" for line in transcript) == 1
            and sum(line.startswith("SESSION CREATE ID=") for line in transcript) == 3
            and sum(line.startswith("STREAM FORWARD ID=") for line in transcript) == 3,
            "SAM lifecycle transcript coverage drifted",
        )
        require(
            forward_results == [REPLY, REPLY, REPLY],
            "mock I2P forward did not reach the exact raw service",
        )
        with target.lock:
            payloads = list(target.payloads)
        require(payloads == [PAYLOAD, PAYLOAD, PAYLOAD], "target bytes changed")

        common = [
            "--sam",
            f"{mock.endpoint[0]}:{mock.endpoint[1]}",
            "--target",
            f"{target.endpoint[0]}:{target.endpoint[1]}",
            "--destination-key",
            str(key),
            "--audit",
            str(second_audit),
            "--startup-timeout",
            "1",
            "--command-timeout",
            "1",
        ]
        reject(script, common, "File exists")
        reject(
            script,
            [
                "--sam",
                f"{mock.endpoint[0]}:{mock.endpoint[1]}",
                "--target",
                "192.0.2.1:33445",
                "--destination-key",
                str(key),
                "--audit",
                str(root / "invalid-target.audit"),
            ],
            "must be numeric loopback",
        )
        os.chmod(key, 0o644)
        reject(
            script,
            [
                "--sam",
                f"{mock.endpoint[0]}:{mock.endpoint[1]}",
                "--target",
                f"{target.endpoint[0]}:{target.endpoint[1]}",
                "--destination-key",
                str(key),
                "--audit",
                str(root / "weak-key.audit"),
            ],
            "mode must be 0600",
        )
        os.chmod(key, 0o600)
        reject(
            script,
            [
                "--sam",
                "127.0.0.1:9",
                "--target",
                f"{target.endpoint[0]}:{target.endpoint[1]}",
                "--destination-key",
                str(key),
                "--audit",
                str(root / "startup-timeout.audit"),
                "--startup-timeout",
                "1",
                "--command-timeout",
                "1",
            ],
            "did not become ready before startup timeout",
        )
        mock.close()
        target.close()
    print("strict persistent I2P SAM service forward passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
