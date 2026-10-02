#!/usr/bin/env python3
"""Whole-binary SOCKS5 configured-target observation gate."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def serve_target(listener: socket.socket, stopped: threading.Event) -> None:
    listener.settimeout(0.1)
    while not stopped.is_set():
        try:
            stream, _ = listener.accept()
        except TimeoutError:
            continue
        except OSError:
            return
        with stream:
            stream.settimeout(0.1)
            while not stopped.is_set():
                try:
                    if not stream.recv(1024):
                        break
                except TimeoutError:
                    continue


def wait_for_socket(path: Path, process: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        if path.exists():
            return
        require(process.poll() is None, "IoTox exited before publishing control.sock")
        time.sleep(0.01)
    raise RuntimeError("IoTox did not publish control.sock")


def run_control(iotox: Path, runtime: Path, command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(iotox), "--runtime", str(runtime), "--timeout-ms", "2000", command],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=5,
        check=False,
    )


def main() -> int:
    require(len(sys.argv) == 4, "expected IOTOX MOCK_TOXCORE FORWARDER")
    iotox = Path(sys.argv[1]).resolve()
    mock_toxcore = Path(sys.argv[2]).resolve()
    forwarder = Path(sys.argv[3]).resolve()
    require(iotox.is_file() and mock_toxcore.is_file() and forwarder.is_file(),
            "route-target fixture input is absent")

    with tempfile.TemporaryDirectory(prefix="iotox-route-target-") as raw_root:
        root = Path(raw_root)
        runtime = root / "run"
        state = root / "state" / "device.toxsave"
        state.parent.mkdir(mode=0o700)
        audit = root / "proxy-audit.jsonl"

        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", 0))
        listener.listen(4)
        target_port = listener.getsockname()[1]
        target_stopped = threading.Event()
        target_thread = threading.Thread(
            target=serve_target, args=(listener, target_stopped), daemon=True)
        target_thread.start()

        proxy = subprocess.Popen(
            [
                sys.executable,
                str(forwarder),
                "--listen", "127.0.0.1:0",
                "--allow-target", f"127.0.0.1:{target_port}",
                "--audit", str(audit),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        require(proxy.stdout is not None, "SOCKS5 forwarder stdout is absent")
        ready = proxy.stdout.readline().strip()
        require(ready.startswith("ready=127.0.0.1:"),
                "SOCKS5 forwarder did not become ready")
        proxy_port = int(ready.rsplit(":", 1)[1])

        key_a = "11" * 32
        key_b = "22" * 32
        agent = subprocess.Popen(
            [
                str(iotox), "run",
                "--library", str(mock_toxcore),
                "--state", str(state),
                "--runtime", str(runtime),
                "--network", "tox/tor",
                "--socks5-proxy", f"127.0.0.1:{proxy_port}",
                "--bootstrap", f"127.0.0.1:{target_port}:{key_a}",
                "--tcp-relay", f"127.0.0.1:{target_port}:{key_b}",
                "--no-default-bootstrap",
                "--no-default-relays",
                "--run-ms", "30000",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=os.environ.copy(),
        )
        try:
            wait_for_socket(runtime / "control.sock", agent)

            carrier_deadline = time.monotonic() + 5.0
            carrier = run_control(iotox, runtime, "route-health")
            while (
                (carrier.returncode != 0 or
                 "carrier-connection=tcp\n" not in carrier.stdout) and
                time.monotonic() < carrier_deadline
            ):
                time.sleep(0.01)
                carrier = run_control(iotox, runtime, "route-health")
            require(
                carrier.returncode == 0 and
                "carrier-connection=tcp\n" in carrier.stdout,
                f"mock carrier did not become ready:\n{carrier.stdout}",
            )

            reached = run_control(iotox, runtime, "route-target-health")
            require(
                reached.returncode == 0 and
                "network=Tox/Tor\n" in reached.stdout and
                "carrier-connection=tcp\n" in reached.stdout and
                "target-source=configured-tcp-relay-0\n" in reached.stdout and
                "probe-stage=complete\n" in reached.stdout and
                "target-health=reachable\n" in reached.stdout and
                "socks-reply-code=0\n" in reached.stdout,
                f"configured target did not become reachable:\n{reached.stdout}",
            )

            target_stopped.set()
            listener.close()
            target_thread.join(timeout=2)
            require(not target_thread.is_alive(), "configured target did not stop")

            refused = run_control(iotox, runtime, "route-target-health")
            require(
                refused.returncode == 0 and
                "carrier-connection=tcp\n" in refused.stdout and
                "probe-stage=target-connect\n" in refused.stdout and
                "target-health=refused\n" in refused.stdout and
                "socks-reply-code=5\n" in refused.stdout,
                f"configured target refusal was not separated:\n{refused.stdout}",
            )

            proxy.terminate()
            proxy_output, proxy_errors = proxy.communicate(timeout=5)
            require(proxy.returncode == 0, f"SOCKS5 forwarder failed: {proxy_errors}")
            require("admitted=1 denied=1" in proxy_output,
                    f"SOCKS5 target audit counters drifted: {proxy_output}")

            boundary = run_control(iotox, runtime, "route-target-health")
            require(
                boundary.returncode == 0 and
                "carrier-connection=tcp\n" in boundary.stdout and
                "probe-stage=proxy-connect\n" in boundary.stdout and
                "target-health=refused\n" in boundary.stdout and
                "socks-reply-code=none\n" in boundary.stdout,
                f"local proxy refusal was not kept separate from carrier truth:\n{boundary.stdout}",
            )

            records = [
                json.loads(line)
                for line in audit.read_text(encoding="ascii").splitlines()
            ]
            require(
                [record["outcome"] for record in records] ==
                    ["admitted", "denied-connect"],
                f"probe did not use only the allowlisted configured target: {records}",
            )
            stopped = run_control(iotox, runtime, "stop")
            require(stopped.returncode == 0, f"unable to stop IoTox: {stopped.stdout}")
            agent.wait(timeout=5)
            require(agent.returncode == 0, "IoTox route-target fixture did not stop cleanly")
        finally:
            target_stopped.set()
            listener.close()
            target_thread.join(timeout=1)
            if proxy.poll() is None:
                proxy.terminate()
                proxy.communicate(timeout=5)
            if agent.poll() is None:
                agent.terminate()
                agent.communicate(timeout=5)

    print("iotox route target process: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"FAIL route target process: {error}", file=sys.stderr)
        raise SystemExit(1)
