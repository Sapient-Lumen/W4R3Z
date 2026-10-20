#!/usr/bin/env python3
"""Process test for the bounded adversarial SOCKS5 interposer."""

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
        require(bool(chunk), "unexpected end of interposer stream")
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
            while data := client.recv(4096):
                client.sendall(data)


def start_process(arguments: list[str]) -> tuple[subprocess.Popen[str], tuple[str, int]]:
    process = subprocess.Popen(
        arguments,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    require(process.stdout is not None, "process stdout is absent")
    ready = process.stdout.readline().strip()
    require(ready.startswith("ready=127.0.0.1:"), f"process not ready: {ready}")
    return process, ("127.0.0.1", int(ready.rsplit(":", 1)[1]))


def open_target(proxy: tuple[str, int], port: int) -> socket.socket:
    stream = socket.create_connection(proxy, timeout=5)
    stream.sendall(b"\x05\x01\x00")
    require(receive_exact(stream, 2) == b"\x05\x00", "greeting failed")
    stream.sendall(b"\x05\x01\x00\x01\x7f\x00\x00\x01" + port.to_bytes(2, "big"))
    require(receive_exact(stream, 10)[:2] == b"\x05\x00", "CONNECT failed")
    return stream


def stop_process(process: subprocess.Popen[str]) -> tuple[str, str]:
    process.terminate()
    return process.communicate(timeout=5)


def main() -> int:
    require(len(sys.argv) == 3, "expected forwarder and adversary script paths")
    forwarder = Path(sys.argv[1]).resolve()
    adversary = Path(sys.argv[2]).resolve()
    with tempfile.TemporaryDirectory(prefix="iotox-socks5-adversary-") as raw_root:
        root = Path(raw_root)
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", 0))
        listener.listen(4)
        echo_port = listener.getsockname()[1]
        stopped = threading.Event()
        echo = threading.Thread(target=serve_echo, args=(listener, stopped), daemon=True)
        echo.start()
        upstream, upstream_endpoint = start_process(
            [
                sys.executable,
                str(forwarder),
                "--listen",
                "127.0.0.1:0",
                "--allow-target",
                f"127.0.0.1:{echo_port}",
                "--audit",
                str(root / "upstream.jsonl"),
            ]
        )
        hold = root / "hold"
        outer, outer_endpoint = start_process(
            [
                sys.executable,
                str(adversary),
                "--listen",
                "127.0.0.1:0",
                "--allow-target",
                f"127.0.0.1:{echo_port}",
                "--upstream-socks",
                f"{upstream_endpoint[0]}:{upstream_endpoint[1]}",
                "--hold-file",
                str(hold),
                "--audit",
                str(root / "outer.jsonl"),
            ]
        )
        try:
            with open_target(outer_endpoint, echo_port) as stream:
                stream.sendall(b"before")
                require(receive_exact(stream, 6) == b"before", "initial relay failed")
                hold.touch(mode=0o600)
                stream.sendall(b"held")
                stream.settimeout(0.25)
                try:
                    stream.recv(4)
                except TimeoutError:
                    pass
                else:
                    raise RuntimeError("hold file did not stop established relay bytes")
                with socket.create_connection(outer_endpoint, timeout=1):
                    pass
                hold.unlink()
                stream.settimeout(5)
                require(receive_exact(stream, 4) == b"held", "relay did not resume exactly")
        finally:
            outer_output, outer_errors = stop_process(outer)
            upstream_output, upstream_errors = stop_process(upstream)
            stopped.set()
            echo.join(timeout=2)
            listener.close()
        require(outer.returncode == 0, f"interposer failed: {outer_errors}")
        require(upstream.returncode == 0, f"upstream failed: {upstream_errors}")
        require("admitted=1 denied=0" in outer_output, "interposer counters drifted")
        require("admitted=1 denied=0" in upstream_output, "upstream counters drifted")
        records = [
            json.loads(line)
            for line in (root / "outer.jsonl").read_text(encoding="ascii").splitlines()
        ]
        require([record["outcome"] for record in records] ==
                ["admitted", "admitted-chain", "held"],
                "interposer audit ordering drifted")
        chain = records[1]
        require(chain["target"] == f"127.0.0.1:{echo_port}",
                "interposer target attribution drifted")
        require(chain["client_source"].startswith("127.0.0.1:"),
                "interposer client-source attribution drifted")
        require(chain["upstream_source"].startswith("127.0.0.1:"),
                "interposer upstream-source attribution drifted")
        require(chain["upstream_destination"] ==
                f"{upstream_endpoint[0]}:{upstream_endpoint[1]}",
                "interposer upstream destination drifted")
    print("adversarial SOCKS5 interposer passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
