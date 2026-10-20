#!/usr/bin/env python3
"""Process test for the bounded numeric-only SOCKS5 laboratory boundary."""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import threading
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def receive_exact(stream: socket.socket, size: int) -> bytes:
    output = bytearray()
    while len(output) < size:
        chunk = stream.recv(size - len(output))
        require(bool(chunk), "unexpected end of SOCKS5 process stream")
        output.extend(chunk)
    return bytes(output)


def serve_echo(listener: socket.socket, stopped: threading.Event) -> None:
    listener.settimeout(0.2)
    while not stopped.is_set():
        try:
            client, _ = listener.accept()
        except TimeoutError:
            continue
        with client:
            while True:
                data = client.recv(4096)
                if not data:
                    break
                client.sendall(data)


def open_socks(proxy: tuple[str, int]) -> socket.socket:
    client = socket.create_connection(proxy, timeout=5)
    client.sendall(b"\x05\x01\x00")
    require(receive_exact(client, 2) == b"\x05\x00", "SOCKS5 greeting failed")
    return client


def main() -> int:
    require(len(sys.argv) == 2, "expected the forwarder script path")
    forwarder = Path(sys.argv[1]).resolve()
    require(forwarder.is_file(), "forwarder script is absent")
    with tempfile.TemporaryDirectory(prefix="iotox-socks5-test-") as raw_root:
        root = Path(raw_root)
        audit = root / "audit.jsonl"
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", 0))
        listener.listen(4)
        echo_port = listener.getsockname()[1]
        stopped = threading.Event()
        echo = threading.Thread(
            target=serve_echo, args=(listener, stopped), daemon=True
        )
        echo.start()
        process = subprocess.Popen(
            [
                sys.executable,
                str(forwarder),
                "--listen",
                "127.0.0.1:0",
                "--allow-target",
                f"127.0.0.1:{echo_port}",
                "--audit",
                str(audit),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            require(process.stdout is not None, "forwarder stdout is absent")
            ready = process.stdout.readline().strip()
            require(ready.startswith("ready=127.0.0.1:"), "forwarder did not become ready")
            proxy = ("127.0.0.1", int(ready.rsplit(":", 1)[1]))

            with open_socks(proxy) as admitted:
                admitted.sendall(
                    b"\x05\x01\x00\x01\x7f\x00\x00\x01" +
                    echo_port.to_bytes(2, "big")
                )
                require(receive_exact(admitted, 10)[:2] == b"\x05\x00",
                        "allowed numeric target was refused")
                admitted.sendall(b"iotox-route")
                require(receive_exact(admitted, 11) == b"iotox-route",
                        "forwarded stream was not byte exact")

            with open_socks(proxy) as denied:
                denied.sendall(
                    b"\x05\x01\x00\x01\xc0\x00\x02\x01\x01\xbb"
                )
                require(receive_exact(denied, 10)[:2] == b"\x05\x02",
                        "unallowlisted numeric target was not refused")

            with open_socks(proxy) as domain:
                domain.sendall(b"\x05\x01\x00\x03\x07invalid\x01\xbb")
                require(receive_exact(domain, 10)[:2] == b"\x05\x08",
                        "domain-name address type was not refused")
        finally:
            process.terminate()
            output, errors = process.communicate(timeout=5)
            stopped.set()
            echo.join(timeout=2)
            listener.close()
        require(process.returncode == 0, f"forwarder failed: {errors}")
        require("admitted=1 denied=2" in output, "forwarder counters drifted")
        records = [json.loads(line) for line in audit.read_text(encoding="ascii").splitlines()]
        require([record["outcome"] for record in records] ==
                ["admitted", "denied-target", "denied-address-type"],
                "forwarder audit outcomes drifted")
    print("strict numeric SOCKS5 forwarder passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
