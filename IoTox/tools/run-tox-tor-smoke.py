#!/usr/bin/env python3
"""Qualify source-linked Tox/Tor SOCKS policy on local loopback.

The gate proves real c-toxcore TCP self-connectivity through the strict SOCKS5
boundary, absence of an IoTox UDP socket or direct relay connection, explicit
offline observation when that boundary dies, and same-endpoint recovery. The
forwarder is laboratory plumbing, not Tor; this gate makes no anonymity or
public-overlay claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
FORWARDER = ROOT / "tools" / "run-socks5-forwarder.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def wait_for(probe: Callable[[], bool], timeout: float, label: str) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if probe():
            return
        time.sleep(0.05)
    raise RuntimeError(f"timed out waiting for {label}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def realize() -> tuple[Path, Path]:
    completed = subprocess.run(
        [
            "nix",
            "build",
            "--no-link",
            "--print-out-paths",
            f"git+file:{ROOT}#toxBootstrap",
            f"git+file:{ROOT}#iotoxSourceLinked",
        ],
        check=True,
        text=True,
        capture_output=True,
        timeout=600,
    )
    paths = [Path(line) for line in completed.stdout.splitlines() if line]
    bootstrap = [path / "bin/DHT_bootstrap" for path in paths
                 if (path / "bin/DHT_bootstrap").is_file()]
    iotox = [path / "bin/iotox" for path in paths
             if (path / "bin/iotox").is_file()]
    require(len(bootstrap) == 1, "bootstrap fixture realization was ambiguous")
    require(len(iotox) == 1, "source-linked IoTox realization was ambiguous")
    return bootstrap[0], iotox[0]


def clean_source_revision() -> str:
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, text=True,
        capture_output=True, timeout=10
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, check=True, text=True,
        capture_output=True, timeout=10
    ).stdout
    require(not status, "Tox/Tor qualification requires an exact clean Git tree")
    require(len(revision) == 40, "source commit is not canonical SHA-1 text")
    return revision


def private_process_root() -> Path:
    base = ROOT / ".sandwurm" / "tor-smoke"
    base.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="run.", dir=base)).resolve()
    root.chmod(0o700)
    return root


def terminate(process: subprocess.Popen[str] | None) -> tuple[str, str]:
    if process is None:
        return "", ""
    if process.poll() is None:
        process.terminate()
    try:
        return process.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        return process.communicate(timeout=5)


def start_forwarder(root: Path, port: int, audit_name: str) -> tuple[subprocess.Popen[str], int, Path]:
    audit = root / audit_name
    process = subprocess.Popen(
        [
            sys.executable,
            str(FORWARDER),
            "--listen",
            f"127.0.0.1:{port}",
            "--allow-target",
            "127.0.0.1:33445",
            "--audit",
            str(audit),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    require(process.stdout is not None, "SOCKS5 forwarder stdout is absent")
    ready = process.stdout.readline().strip()
    if not ready.startswith("ready=127.0.0.1:"):
        _output, errors = terminate(process)
        raise RuntimeError(f"SOCKS5 forwarder failed before readiness: {ready} {errors}")
    actual_port = int(ready.rsplit(":", 1)[1])
    require(port == 0 or actual_port == port, "SOCKS5 endpoint changed across restart")
    return process, actual_port, audit


def process_socket_inodes(pid: int) -> set[str]:
    output: set[str] = set()
    for descriptor in (Path("/proc") / str(pid) / "fd").iterdir():
        try:
            target = os.readlink(descriptor)
        except FileNotFoundError:
            continue
        if target.startswith("socket:[") and target.endswith("]"):
            output.add(target[8:-1])
    return output


def process_inet_sockets(pid: int, protocol: str) -> list[tuple[int, int]]:
    inodes = process_socket_inodes(pid)
    records: list[tuple[int, int]] = []
    for table in (Path(f"/proc/net/{protocol}"), Path(f"/proc/net/{protocol}6")):
        for line in table.read_text(encoding="ascii").splitlines()[1:]:
            fields = line.split()
            if len(fields) < 10 or fields[9] not in inodes:
                continue
            local_port = int(fields[1].rsplit(":", 1)[1], 16)
            remote_port = int(fields[2].rsplit(":", 1)[1], 16)
            records.append((local_port, remote_port))
    return records


def assert_route_sockets(pid: int, proxy_port: int, require_live: bool) -> None:
    tcp = process_inet_sockets(pid, "tcp")
    remote_ports = {remote for _local, remote in tcp if remote != 0}
    if require_live:
        require(proxy_port in remote_ports,
                "source-linked IoTox has no TCP stream to the SOCKS5 boundary")
    require(remote_ports <= {proxy_port},
            f"source-linked IoTox opened a TCP route outside SOCKS5: {sorted(remote_ports)}")
    require(not process_inet_sockets(pid, "udp"),
            "source-linked Tox/Tor opened a native UDP socket")


def read_state(path: Path, expected: str) -> bool:
    try:
        return path.read_text(encoding="utf-8") == expected + "\n"
    except FileNotFoundError:
        return False


def admitted_records(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="ascii").splitlines()
        if line
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--keep", action="store_true")
    arguments = parser.parse_args()
    require(sys.platform.startswith("linux"), "route socket proof requires Linux /proc")
    source_commit = clean_source_revision()
    bootstrap_binary, iotox_binary = realize()
    root = private_process_root()
    bootstrap: subprocess.Popen[str] | None = None
    proxy: subprocess.Popen[str] | None = None
    agent: subprocess.Popen[str] | None = None
    bootstrap_log = None
    succeeded = False
    gate_started = time.monotonic()
    try:
        bootstrap_log = (root / "bootstrap.log").open("w", encoding="utf-8")
        bootstrap = subprocess.Popen(
            [str(bootstrap_binary), "--ipv4"],
            cwd=root,
            text=True,
            stdout=bootstrap_log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        public_id = root / "PUBLIC_ID.txt"
        wait_for(lambda: public_id.is_file() and public_id.stat().st_size == 64,
                 15, "bootstrap public identity")
        bootstrap_key = public_id.read_text(encoding="ascii")
        require(len(bootstrap_key) == 64 and bootstrap_key.isalnum(),
                "bootstrap public identity is malformed")
        wait_for(
            lambda: bootstrap.poll() is None and _tcp_connectable(33445),
            15,
            "bootstrap TCP relay",
        )

        proxy, proxy_port, first_audit = start_forwarder(root, 0, "socks-first.jsonl")
        runtime = root / "run"
        state = root / "state" / "device.toxsave"
        endpoint = f"127.0.0.1:33445:{bootstrap_key}"
        agent_started = time.monotonic()
        agent = subprocess.Popen(
            [
                str(iotox_binary),
                "run",
                "--state",
                str(state),
                "--runtime",
                str(runtime),
                "--network",
                "tox/tor",
                "--socks5-proxy",
                f"127.0.0.1:{proxy_port}",
                "--bootstrap",
                endpoint,
                "--tcp-relay",
                endpoint,
                "--bootstrap-retry-ms",
                "1000",
                "--run-ms",
                "180000",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        connection = runtime / "self" / "connection"
        network = runtime / "self" / "network"
        wait_for(lambda: agent.poll() is None and read_state(connection, "tcp"),
                 60, "source-linked Tox/Tor TCP self-connection")
        initial_online_ms = int((time.monotonic() - agent_started) * 1000)
        require(read_state(network, "Tox/Tor"), "runtime route projection drifted")
        assert_route_sockets(agent.pid, proxy_port, True)
        first_records = admitted_records(first_audit)
        require(any(record.get("outcome") == "admitted" and
                    record.get("target") == "127.0.0.1:33445"
                    for record in first_records),
                "SOCKS5 boundary did not admit the exact relay")

        proxy_loss_started = time.monotonic()
        terminate(proxy)
        proxy = None
        assert_route_sockets(agent.pid, proxy_port, False)
        wait_for(lambda: agent.poll() is None and read_state(connection, "offline"),
                 120, "offline state after SOCKS5 loss")
        proxy_loss_to_offline_ms = int(
            (time.monotonic() - proxy_loss_started) * 1000
        )
        assert_route_sockets(agent.pid, proxy_port, False)

        proxy, restarted_port, second_audit = start_forwarder(
            root, proxy_port, "socks-restarted.jsonl"
        )
        require(restarted_port == proxy_port, "SOCKS5 restart endpoint drifted")
        proxy_restart_ready = time.monotonic()
        wait_for(lambda: agent.poll() is None and read_state(connection, "tcp"),
                 120, "Tox/Tor recovery through the same SOCKS5 endpoint")
        proxy_restart_to_online_ms = int(
            (time.monotonic() - proxy_restart_ready) * 1000
        )
        assert_route_sockets(agent.pid, proxy_port, True)
        second_records = admitted_records(second_audit)
        require(any(record.get("outcome") == "admitted" and
                    record.get("target") == "127.0.0.1:33445"
                    for record in second_records),
                "restarted SOCKS5 boundary did not carry recovery")

        version = subprocess.run(
            [str(iotox_binary), "--version"], check=True, text=True,
            capture_output=True, timeout=10
        ).stdout.strip()
        receipt = {
            "bootstrap_sha256": sha256(bootstrap_binary),
            "carrier": "tcp",
            "direct_relay_socket_observed": False,
            "dns_policy": "disabled-numeric-only",
            "fixture": "numeric-only-socks5-loopback",
            "iotox_sha256": sha256(iotox_binary),
            "iotox_version": version,
            "initial_online_ms": initial_online_ms,
            "network": "Tox/Tor",
            "native_udp_socket_observed": False,
            "proxy_first_admitted": sum(
                record.get("outcome") == "admitted" for record in first_records
            ),
            "proxy_first_denied": sum(
                record.get("outcome") != "admitted" for record in first_records
            ),
            "proxy_loss_to_offline_ms": proxy_loss_to_offline_ms,
            "proxy_restart_count": 1,
            "proxy_restart_admitted": sum(
                record.get("outcome") == "admitted" for record in second_records
            ),
            "proxy_restart_denied": sum(
                record.get("outcome") != "admitted" for record in second_records
            ),
            "proxy_restart_to_online_ms": proxy_restart_to_online_ms,
            "recovery_observed": True,
            "scope": "source-linked-local-construction-not-actual-tor",
            "socks5_forwarder_sha256": sha256(FORWARDER),
            "source_commit": source_commit,
            "source_tree_clean": True,
            "total_gate_ms": int((time.monotonic() - gate_started) * 1000),
            "tox_tor_smoke_sha256": sha256(Path(__file__).resolve()),
        }
        encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n"
        if arguments.output is not None:
            arguments.output.parent.mkdir(parents=True, exist_ok=True)
            arguments.output.write_text(encoded, encoding="ascii")
        print(encoded, end="")
        succeeded = True
        return 0
    finally:
        terminate(agent)
        terminate(proxy)
        terminate(bootstrap)
        if bootstrap_log is not None:
            bootstrap_log.close()
        if succeeded and not arguments.keep:
            shutil.rmtree(root)
        else:
            print(f"retained-route-smoke={root}", file=sys.stderr)


def _tcp_connectable(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.2):
            return True
    except OSError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
