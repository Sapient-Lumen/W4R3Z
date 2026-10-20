#!/usr/bin/env python3
"""Process test for the strict SOCKS5-to-I2P SAM construction adapter."""

from __future__ import annotations

import json
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path


DESTINATION = "a" * 52 + ".b32.i2p"
TARGET = ("192.0.2.17", 33445)


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
    value = bytearray()
    while True:
        byte = stream.recv(1)
        require(bool(byte), "mock SAM received a partial line")
        if byte == b"\n":
            return value.decode("ascii")
        value.extend(byte)


class MockSam:
    def __init__(self) -> None:
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen(32)
        self.listener.settimeout(0.2)
        self.endpoint = self.listener.getsockname()[:2]
        self.lock = threading.Lock()
        self.stopping = threading.Event()
        self.allow_sessions = True
        self.control: socket.socket | None = None
        self.session_id: str | None = None
        self.transcript: list[str] = []
        self.workers: list[threading.Thread] = []
        self.server = threading.Thread(target=self.serve, daemon=True)
        self.server.start()

    def append(self, line: str) -> None:
        with self.lock:
            self.transcript.append(line)

    def serve(self) -> None:
        while not self.stopping.is_set():
            try:
                connection, _source = self.listener.accept()
            except TimeoutError:
                continue
            except OSError:
                if self.stopping.is_set():
                    return
                raise
            worker = threading.Thread(
                target=self.handle, args=(connection,), daemon=True
            )
            self.workers.append(worker)
            worker.start()

    def handle(self, connection: socket.socket) -> None:
        with connection:
            try:
                hello = receive_line(connection)
                self.append(hello)
                require(
                    hello == "HELLO VERSION MIN=3.1 MAX=3.1",
                    "adapter SAM version request drifted",
                )
                connection.sendall(b"HELLO REPLY VERSION=3.1 RESULT=OK\n")
                command = receive_line(connection)
                self.append(command)
                if command.startswith("SESSION CREATE "):
                    match = re.fullmatch(
                        r"SESSION CREATE ID=(iotox_[0-9a-f]{24}) "
                        r"STYLE=STREAM DESTINATION=TRANSIENT SIGNATURE_TYPE=7 "
                        r"i2cp\.leaseSetEncType=4 inbound\.quantity=2 "
                        r"outbound\.quantity=2 i2p\.streaming\.profile=2",
                        command,
                    )
                    require(match is not None, "SAM SESSION CREATE drifted")
                    with self.lock:
                        allowed = self.allow_sessions
                        if allowed:
                            self.control = connection
                            self.session_id = match.group(1)
                    if not allowed:
                        connection.sendall(b"SESSION STATUS RESULT=I2P_ERROR\n")
                        return
                    connection.sendall(
                        b"SESSION STATUS DESTINATION=private RESULT=OK\n"
                    )
                    while not self.stopping.is_set():
                        line = receive_line(connection)
                        self.append(line)
                elif command.startswith("STREAM CONNECT "):
                    match = re.fullmatch(
                        r"STREAM CONNECT ID=(iotox_[0-9a-f]{24}) "
                        + re.escape(f"DESTINATION={DESTINATION} SILENT=false"),
                        command,
                    )
                    require(match is not None, "SAM STREAM CONNECT drifted")
                    with self.lock:
                        ready = (
                            self.control is not None
                            and self.session_id == match.group(1)
                            and self.allow_sessions
                        )
                    if not ready:
                        connection.sendall(b"STREAM STATUS RESULT=INVALID_ID\n")
                        return
                    connection.sendall(b"STREAM STATUS RESULT=OK\n")
                    while data := connection.recv(65536):
                        connection.sendall(data)
                else:
                    raise RuntimeError("unexpected mock SAM command")
            except (ConnectionError, OSError, RuntimeError):
                pass
            finally:
                with self.lock:
                    if self.control is connection:
                        self.control = None

    def suspend(self) -> None:
        with self.lock:
            self.allow_sessions = False
            control = self.control
        require(control is not None, "mock SAM has no control session to suspend")
        try:
            control.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        control.close()

    def ping(self, payload: str) -> None:
        with self.lock:
            control = self.control
        require(control is not None, "mock SAM has no control session to ping")
        control.sendall(f"PING {payload}\n".encode("ascii"))

    def wait_transcript(self, line: str, timeout: float = 5.0) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with self.lock:
                if line in self.transcript:
                    return
            time.sleep(0.02)
        raise RuntimeError(f"timed out waiting for SAM transcript line: {line}")

    def resume(self) -> None:
        with self.lock:
            self.allow_sessions = True

    def close(self) -> None:
        self.stopping.set()
        with self.lock:
            control = self.control
        if control is not None:
            try:
                control.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            control.close()
        self.listener.close()
        self.server.join(timeout=2.0)
        for worker in self.workers:
            worker.join(timeout=2.0)


def start_adapter(
    script: Path, sam: tuple[str, int], audit: Path
) -> tuple[subprocess.Popen[str], tuple[str, int]]:
    process = subprocess.Popen(
        [
            sys.executable,
            str(script),
            "--listen",
            "127.0.0.1:0",
            "--sam",
            f"{sam[0]}:{sam[1]}",
            "--map",
            f"{TARGET[0]}:{TARGET[1]}={DESTINATION}",
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
    require(process.stdout is not None, "adapter stdout is absent")
    ready = process.stdout.readline().strip()
    require(ready.startswith("ready=127.0.0.1:"), f"adapter not ready: {ready}")
    return process, ("127.0.0.1", int(ready.rsplit(":", 1)[1]))


def socks_connect(
    proxy: tuple[str, int], target: tuple[str, int]
) -> tuple[socket.socket, int]:
    stream = socket.create_connection(proxy, timeout=5.0)
    stream.sendall(b"\x05\x01\x00")
    require(receive_exact(stream, 2) == b"\x05\x00", "SOCKS greeting failed")
    packed = socket.inet_pton(socket.AF_INET, target[0])
    stream.sendall(b"\x05\x01\x00\x01" + packed + target[1].to_bytes(2, "big"))
    reply = receive_exact(stream, 10)
    require(reply[0] == 5, "SOCKS reply version drifted")
    return stream, reply[1]


def domain_connect(proxy: tuple[str, int]) -> int:
    with socket.create_connection(proxy, timeout=5.0) as stream:
        stream.sendall(b"\x05\x01\x00")
        require(receive_exact(stream, 2) == b"\x05\x00", "SOCKS greeting failed")
        stream.sendall(b"\x05\x01\x00\x03\x07bad.i2p\x00\x50")
        return receive_exact(stream, 10)[1]


def load_audit(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="ascii").splitlines()
    ]


def wait_for(
    path: Path, predicate: object, timeout: float = 5.0
) -> list[dict[str, object]]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        records = load_audit(path)
        if predicate(records):
            return records
        time.sleep(0.02)
    raise RuntimeError("timed out waiting for adapter audit transition")


def reject_configuration(script: Path, arguments: list[str], phrase: str) -> None:
    result = subprocess.run(
        [sys.executable, str(script), *arguments],
        text=True,
        capture_output=True,
        timeout=5.0,
        check=False,
    )
    require(result.returncode != 0 and phrase in result.stderr,
            f"invalid adapter configuration was not rejected: {result.stderr}")


def main() -> int:
    require(len(sys.argv) == 2, "expected I2P SAM adapter script path")
    script = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix="iotox-i2p-sam-socks-") as raw_root:
        root = Path(raw_root)
        mock = MockSam()
        audit = root / "audit.jsonl"
        process, proxy = start_adapter(script, mock.endpoint, audit)
        try:
            stream, code = socks_connect(proxy, TARGET)
            require(code == 0, "mapped I2P stream was refused")
            with stream:
                stream.sendall(b"iotox-i2p")
                require(receive_exact(stream, 9) == b"iotox-i2p",
                        "I2P stream relay changed bytes")

            mock.ping("science")
            mock.wait_transcript("PONG science")

            failures: list[str] = []
            failure_lock = threading.Lock()

            def concurrent_stream(index: int) -> None:
                try:
                    member, member_code = socks_connect(proxy, TARGET)
                    require(member_code == 0, "concurrent I2P stream was refused")
                    payload = f"member-{index:02d}".encode("ascii")
                    with member:
                        member.sendall(payload)
                        require(receive_exact(member, len(payload)) == payload,
                                "concurrent I2P stream changed bytes")
                except Exception as error:  # noqa: BLE001 - collect thread failures
                    with failure_lock:
                        failures.append(str(error))

            members = [
                threading.Thread(target=concurrent_stream, args=(index,))
                for index in range(8)
            ]
            for member in members:
                member.start()
            for member in members:
                member.join(timeout=10.0)
            require(
                all(not member.is_alive() for member in members) and not failures,
                f"concurrent I2P streams failed: {failures}",
            )

            denied, code = socks_connect(proxy, ("192.0.2.18", TARGET[1]))
            denied.close()
            require(code == 2, "unmapped numeric target was admitted")
            require(domain_connect(proxy) == 8, "SOCKS domain target was admitted")

            mock.suspend()
            wait_for(
                audit,
                lambda records: any(
                    record.get("event") == "sam-session"
                    and record.get("outcome") == "lost"
                    for record in records
                ),
            )
            unavailable, code = socks_connect(proxy, TARGET)
            unavailable.close()
            require(code != 0, "SOCKS admitted a target without a SAM session")
            mock.resume()
            records = wait_for(
                audit,
                lambda values: sum(
                    record.get("event") == "sam-session"
                    and record.get("outcome") == "ready"
                    for record in values
                ) >= 2,
            )
            recovered, code = socks_connect(proxy, TARGET)
            require(code == 0, "mapped I2P stream did not recover")
            with recovered:
                recovered.sendall(b"recovered")
                require(receive_exact(recovered, 9) == b"recovered",
                        "recovered I2P stream changed bytes")
            records = wait_for(
                audit,
                lambda values: sum(
                    record.get("outcome") == "admitted" for record in values
                ) >= 2,
            )
        finally:
            process.terminate()
            output, errors = process.communicate(timeout=5.0)
            mock.close()
        require(process.returncode == 0, f"adapter failed: {errors}")
        require(
            "admitted=10 denied=3" in output
            and "sessions=2 losses=1" in output,
            f"adapter counters drifted: {output}",
        )
        outcomes = [record["outcome"] for record in records]
        require(
            outcomes == [
                "ready",
                *(["admitted"] * 9),
                "denied-target",
                "denied-address-type",
                "lost",
                "denied-sam-unavailable",
                "ready",
                "admitted",
            ],
            f"adapter audit ordering drifted: {outcomes}",
        )
        route_records = [
            record for record in records
            if record["event"] == "socks5-i2p-connect"
        ]
        require(
            all(
                re.fullmatch(r"[0-9a-f]{64}", str(record["destination_sha256"]))
                for record in route_records
            )
            and all(
                isinstance(record.get("setup_us"), int)
                and int(record["setup_us"]) >= 0
                for record in route_records
            )
            and all(DESTINATION not in json.dumps(record) for record in route_records),
            "adapter audit disclosed or failed to commit the I2P destination",
        )
        with mock.lock:
            transcript = list(mock.transcript)
        require(
            transcript.count("HELLO VERSION MIN=3.1 MAX=3.1") >= 12
            and transcript.count("PONG science") == 1,
            "SAM handshake coverage is incomplete",
        )
        session_ids = {
            match.group(1)
            for line in transcript
            if (match := re.match(r"SESSION CREATE ID=(iotox_[0-9a-f]{24}) ", line))
        }
        require(len(session_ids) == 1, "SAM session ID changed across recovery")

        common = [
            "--listen", "127.0.0.1:0",
            "--sam", f"{mock.endpoint[0]}:{mock.endpoint[1]}",
            "--audit", str(root / "invalid.jsonl"),
        ]
        reject_configuration(
            script,
            [*common, "--map", f"{TARGET[0]}:{TARGET[1]}={DESTINATION.upper()}"],
            "canonical lowercase",
        )
        reject_configuration(
            script,
            [
                "--listen", "127.0.0.1:0",
                "--sam", "192.0.2.1:7656",
                "--map", f"{TARGET[0]}:{TARGET[1]}={DESTINATION}",
                "--audit", str(root / "nonloopback.jsonl"),
            ],
            "must be numeric loopback",
        )
    print("strict I2P SAM SOCKS adapter passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
