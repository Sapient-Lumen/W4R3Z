#!/usr/bin/env python3
"""Qualify source-linked Tox/Tor through an operator-owned Tor daemon.

This is an opt-in public-network gate.  The operator supplies current numeric
Tox TCP relay records; the tool never downloads or silently substitutes a node
catalog.  It binds the exact source, product and Tor binaries, normalized Tor
configuration, Tor control-plane stream/circuit evidence, Linux process socket
ownership, proxy-loss behavior, a held outage, and same-endpoint recovery.

The result is route-containment evidence for one host, Tor build, public relay
set, and time sample.  It is not an anonymity proof or a reliability SLA.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import ipaddress
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Callable, Sequence


ROOT = Path(__file__).resolve().parents[1]
HEX_KEY = re.compile(r"^[0-9A-Fa-f]{64}$")
ROUTE_HEALTH_KEYS = {
    "application", "application-error", "application-rtt-us",
    "carrier-connection", "local-boundary", "local-boundary-rtt-us",
    "network", "semantics", "upstream",
}
ROUTE_HEALTH_SEMANTICS = (
    "auxiliary-only-no-carrier-or-session-epoch-mutation"
)
ROUTE_TARGET_KEYS = {
    "carrier-connection", "network", "probe-stage", "semantics",
    "socks-reply-code", "target-health", "target-rtt-us", "target-source",
}
ROUTE_TARGET_SEMANTICS = (
    "auxiliary-only-explicit-numeric-relay-no-carrier-or-session-epoch-mutation"
)
APPLICATION_CIRCUIT_PURPOSES = {"GENERAL", "CONFLUX_LINKED"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def wait_for(probe: Callable[[], bool], timeout: float, label: str) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if probe():
            return
        time.sleep(0.1)
    raise RuntimeError(f"timed out waiting for {label}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def clean_source_revision() -> str:
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, text=True,
        capture_output=True, timeout=10
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, check=True, text=True,
        capture_output=True, timeout=10
    ).stdout
    require(not status, "operator Tor qualification requires an exact clean Git tree")
    require(re.fullmatch(r"[0-9a-f]{40}", revision) is not None,
            "source commit is not canonical SHA-1 text")
    return revision


def realize_iotox() -> Path:
    completed = subprocess.run(
        [
            "nix", "build", "--no-link", "--print-out-paths",
            f"git+file:{ROOT}#iotoxSourceLinked",
        ],
        check=True, text=True, capture_output=True, timeout=600,
    )
    binaries = [
        Path(line) / "bin/iotox"
        for line in completed.stdout.splitlines()
        if line and (Path(line) / "bin/iotox").is_file()
    ]
    require(len(binaries) == 1, "source-linked IoTox realization was ambiguous")
    return binaries[0]


def parse_node(value: str) -> dict[str, object]:
    try:
        host, port_text, public_key = value.rsplit(":", 2)
        address = ipaddress.ip_address(host.strip("[]"))
        port = int(port_text)
    except (ValueError, TypeError) as error:
        raise argparse.ArgumentTypeError(
            "node must be a public numeric IP:PORT:64_HEX_PUBLIC_KEY record"
        ) from error
    if not address.is_global:
        raise argparse.ArgumentTypeError("operator Tor node address must be globally routable")
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("operator Tor node port is outside 1..65535")
    if HEX_KEY.fullmatch(public_key) is None:
        raise argparse.ArgumentTypeError("operator Tor node key must contain exactly 64 hex digits")
    return {
        "address": address.compressed,
        "port": port,
        "public_key": public_key.upper(),
    }


def node_endpoint(node: dict[str, object]) -> str:
    address = ipaddress.ip_address(str(node["address"]))
    host = f"[{address.compressed}]" if address.version == 6 else address.compressed
    return f"{host}:{int(node['port'])}"


def node_record(node: dict[str, object]) -> str:
    return f"{node_endpoint(node)}:{node['public_key']}"


def private_process_root() -> Path:
    base = ROOT / ".sandwurm" / "operator-tor"
    base.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="run.", dir=base)).resolve()
    root.chmod(0o700)
    return root


def free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def tor_configuration(root: Path, socks_port: int) -> tuple[list[str], list[str]]:
    rendered = [
        "AvoidDiskWrites 1",
        "ClientOnly 1",
        "ClientUseIPv6 0",
        "CookieAuthentication 1",
        f"CookieAuthFile {root / 'control.authcookie'}",
        f"ControlSocket {root / 'control.sock'}",
        f"DataDirectory {root / 'tor-data'}",
        # IoTox accepts only operator-supplied numeric relay records and never
        # resolves them. SafeSocks=1 rejects exactly those SOCKS ATYP records
        # because Tor cannot tell they were not produced by local DNS.
        "SafeSocks 0",
        "SocksPolicy accept 127.0.0.1",
        "SocksPolicy reject *",
        f"SocksPort 127.0.0.1:{socks_port}",
    ]
    normalized = [line.replace(str(root), "<RUN_ROOT>") for line in rendered]
    return rendered, normalized


def terminate(process: subprocess.Popen[object] | None) -> None:
    if process is None:
        return
    if process.poll() is None:
        process.terminate()
    try:
        process.wait(timeout=20)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def tail(path: Path, limit: int = 4096) -> str:
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return ""
    return data[-limit:].decode("utf-8", errors="replace")


def process_alive(process: subprocess.Popen[object], log: Path, label: str) -> bool:
    status = process.poll()
    if status is not None:
        raise RuntimeError(f"{label} exited with {status}: {tail(log)}")
    return True


def tcp_connectable(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.2):
            return True
    except OSError:
        return False


def start_tor(
    tor_binary: Path,
    torrc: Path,
    root: Path,
    socks_port: int,
    log_path: Path,
    timeout: float,
) -> tuple[subprocess.Popen[object], object]:
    control_socket = root / "control.sock"
    if control_socket.exists() or control_socket.is_symlink():
        require(control_socket.is_socket(), "refusing to replace a non-socket Tor control path")
        control_socket.unlink()
    log = log_path.open("wb")
    process = subprocess.Popen(
        [
            str(tor_binary), "--defaults-torrc", "/dev/null", "-f", str(torrc),
        ],
        cwd=root, stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
    )

    def ready() -> bool:
        process_alive(process, log_path, "Tor")
        return (
            "Bootstrapped 100% (done): Done" in tail(log_path, 16384)
            and control_socket.is_socket()
            and (root / "control.authcookie").is_file()
            and tcp_connectable(socks_port)
        )

    try:
        wait_for(ready, timeout, "Tor bootstrap and local SOCKS/control readiness")
    except Exception:
        terminate(process)
        log.close()
        raise
    return process, log


def tor_getinfo(root: Path, key: str) -> str:
    cookie = (root / "control.authcookie").read_bytes()
    require(len(cookie) == 32, "Tor control cookie is not 32 bytes")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as control:
        control.settimeout(5)
        control.connect(str(root / "control.sock"))
        stream = control.makefile("rwb", buffering=0)
        stream.write(f"AUTHENTICATE {cookie.hex()}\r\n".encode("ascii"))
        authenticated = stream.readline().decode("ascii", errors="strict").rstrip("\r\n")
        require(authenticated == "250 OK", f"Tor control authentication failed: {authenticated}")
        stream.write(f"GETINFO {key}\r\n".encode("ascii"))
        first = stream.readline().decode("ascii", errors="strict").rstrip("\r\n")
        require(first.startswith((f"250-{key}=", f"250+{key}=")),
                f"unexpected Tor GETINFO {key} response: {first}")
        if first.startswith(f"250-{key}="):
            value = first.split("=", 1)[1]
            require(stream.readline().decode("ascii").rstrip("\r\n") == "250 OK",
                    f"Tor GETINFO {key} omitted final success")
            return value
        lines: list[str] = []
        while True:
            line = stream.readline().decode("ascii", errors="strict").rstrip("\r\n")
            require(line != "", f"Tor GETINFO {key} ended early")
            if line == ".":
                break
            lines.append(line[1:] if line.startswith("..") else line)
        require(stream.readline().decode("ascii").rstrip("\r\n") == "250 OK",
                f"Tor GETINFO {key} omitted final success")
        return "\n".join(lines)


def select_circuit_evidence(
    streams: Sequence[str],
    circuits: Sequence[str],
    allowed_targets: set[str],
    phase: str,
) -> dict[str, object]:
    circuit_by_id = {line.split()[0]: line for line in circuits if len(line.split()) >= 3}
    for line in streams:
        fields = line.split()
        if len(fields) < 4 or fields[1] != "SUCCEEDED" or fields[3] not in allowed_targets:
            continue
        circuit_id = fields[2]
        circuit = circuit_by_id.get(circuit_id, "")
        circuit_fields = circuit.split()
        if len(circuit_fields) < 3 or circuit_fields[1] != "BUILT":
            continue
        purpose_fields = [
            field.split("=", 1)[1] for field in circuit_fields[3:]
            if field.startswith("PURPOSE=")
        ]
        if (len(purpose_fields) != 1
                or purpose_fields[0] not in APPLICATION_CIRCUIT_PURPOSES):
            continue
        path = circuit_fields[2]
        hop_count = len(path.split(","))
        require(hop_count >= 3, "public SOCKS stream is not attached to a three-hop Tor circuit")
        return {
            "bootstrap_progress": 100,
            "circuit_hop_count": hop_count,
            "circuit_path_sha256": hashlib.sha256(path.encode("ascii")).hexdigest(),
            "circuit_purpose": purpose_fields[0],
            "phase": phase,
            "stream_target": fields[3],
        }
    raise RuntimeError(
        "Tor control plane has no successful public relay stream on a built application circuit"
    )


def circuit_evidence(root: Path, allowed_targets: set[str], phase: str) -> dict[str, object]:
    bootstrap = tor_getinfo(root, "status/bootstrap-phase")
    require("PROGRESS=100" in bootstrap and "TAG=done" in bootstrap,
            "Tor control plane does not report a completed bootstrap")
    streams = tor_getinfo(root, "stream-status")
    circuits = tor_getinfo(root, "circuit-status")
    # Failure roots are private and retained. These exact control projections
    # let a parser mismatch be diagnosed without weakening the live assertion;
    # a successful default run removes the complete private root.
    (root / f"tor-control-{phase}-stream-status.txt").write_text(
        streams + "\n", encoding="ascii"
    )
    (root / f"tor-control-{phase}-circuit-status.txt").write_text(
        circuits + "\n", encoding="ascii"
    )
    return select_circuit_evidence(
        streams.splitlines(),
        circuits.splitlines(),
        allowed_targets,
        phase,
    )


def process_socket_inodes(pid: int) -> set[str]:
    output: set[str] = set()
    try:
        descriptors = list((Path("/proc") / str(pid) / "fd").iterdir())
    except FileNotFoundError:
        return output
    for descriptor in descriptors:
        try:
            target = os.readlink(descriptor)
        except (FileNotFoundError, PermissionError):
            continue
        if target.startswith("socket:[") and target.endswith("]"):
            output.add(target[8:-1])
    return output


def decode_proc_address(value: str, version: int) -> str:
    raw = bytes.fromhex(value)
    if version == 4:
        return str(ipaddress.IPv4Address(raw[::-1]))
    require(len(raw) == 16, "Linux IPv6 socket address has the wrong size")
    reordered = b"".join(raw[offset:offset + 4][::-1] for offset in range(0, 16, 4))
    return str(ipaddress.IPv6Address(reordered))


def process_inet_sockets(pid: int, protocol: str) -> list[dict[str, object]]:
    inodes = process_socket_inodes(pid)
    records: list[dict[str, object]] = []
    for version, table in ((4, Path(f"/proc/net/{protocol}")),
                           (6, Path(f"/proc/net/{protocol}6"))):
        for line in table.read_text(encoding="ascii").splitlines()[1:]:
            fields = line.split()
            if len(fields) < 10 or fields[9] not in inodes:
                continue
            local_hex, local_port_hex = fields[1].rsplit(":", 1)
            remote_hex, remote_port_hex = fields[2].rsplit(":", 1)
            records.append({
                "local_address": decode_proc_address(local_hex, version),
                "local_port": int(local_port_hex, 16),
                "remote_address": decode_proc_address(remote_hex, version),
                "remote_port": int(remote_port_hex, 16),
                "state": fields[3],
            })
    return records


def agent_socket_evidence(pid: int, socks_port: int, phase: str, require_live: bool) -> dict[str, object]:
    tcp = process_inet_sockets(pid, "tcp")
    udp = process_inet_sockets(pid, "udp")
    remotes = sorted({
        f"{record['remote_address']}:{record['remote_port']}"
        for record in tcp if int(record["remote_port"]) != 0
    })
    expected = f"127.0.0.1:{socks_port}"
    require(set(remotes) <= {expected},
            f"IoTox opened a TCP route outside Tor SOCKS: {remotes}")
    if require_live:
        require(expected in remotes, "IoTox has no TCP stream to the Tor SOCKS endpoint")
    require(not udp, "IoTox Tox/Tor process opened a native UDP socket")
    return {
        "phase": phase,
        "tcp_remote_endpoints": remotes,
        "udp_socket_count": 0,
    }


def tor_public_socket_evidence(pid: int) -> dict[str, object]:
    public = sorted({
        f"{record['remote_address']}:{record['remote_port']}"
        for record in process_inet_sockets(pid, "tcp")
        if int(record["remote_port"]) != 0
        and ipaddress.ip_address(str(record["remote_address"])).is_global
    })
    require(public, "Tor has no process-owned public TCP connection")
    return {
        "public_tcp_remote_count": len(public),
        "public_tcp_remote_set_sha256": canonical_sha256(public),
    }


def read_state(path: Path, expected: str) -> bool:
    try:
        return path.read_text(encoding="utf-8") == expected + "\n"
    except FileNotFoundError:
        return False


def parse_route_health(text: str, phase: str) -> dict[str, object]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        require("=" in line, "route-health output contains a non-field line")
        key, value = line.split("=", 1)
        require(key not in fields, f"route-health duplicated field {key}")
        fields[key] = value
    require(set(fields) == ROUTE_HEALTH_KEYS,
            f"route-health schema drifted: {sorted(fields)}")
    require(fields["network"] == "Tox/Tor", "route-health route drifted")
    require(fields["carrier-connection"] in {"offline", "tcp"},
            "route-health carrier is not strict routed TCP/offline")
    require(fields["local-boundary"] in {
        "reachable", "refused", "timed-out", "unreachable", "failed",
    }, "route-health local boundary is invalid")
    require(fields["local-boundary-rtt-us"].isdigit(),
            "routed route-health omitted its local-boundary duration")
    require(fields["upstream"] in {
        "carrier-reported-online", "blocked-by-local-boundary", "unresolved",
    }, "route-health upstream classification is invalid")
    require(fields["application"] == "not-sampled"
            and fields["application-rtt-us"] == "not-sampled"
            and fields["application-error"] == "none",
            "carrier-only route-health unexpectedly sampled application content")
    require(fields["semantics"] == ROUTE_HEALTH_SEMANTICS,
            "route-health mutation disclaimer drifted")
    return {
        "application": fields["application"],
        "application_error": fields["application-error"],
        "application_rtt_us": None,
        "carrier_connection": fields["carrier-connection"],
        "local_boundary": fields["local-boundary"],
        "local_boundary_rtt_us": int(fields["local-boundary-rtt-us"]),
        "phase": phase,
        "semantics": fields["semantics"],
        "upstream": fields["upstream"],
    }


def sample_route_health(
    iotox_binary: Path, runtime: Path, phase: str,
) -> dict[str, object]:
    completed = subprocess.run(
        [
            str(iotox_binary), "--runtime", str(runtime),
            "--timeout-ms", "2000", "route-health",
        ],
        check=True, text=True, capture_output=True, timeout=5,
    )
    require(not completed.stderr, "route-health wrote unexpected diagnostics")
    return parse_route_health(completed.stdout, phase)


def parse_route_target_health(text: str, phase: str) -> dict[str, object]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        require("=" in line, "route-target-health output contains a non-field line")
        key, value = line.split("=", 1)
        require(key not in fields, f"route-target-health duplicated field {key}")
        fields[key] = value
    require(set(fields) == ROUTE_TARGET_KEYS,
            f"route-target-health schema drifted: {sorted(fields)}")
    require(fields["network"] == "Tox/Tor", "route-target-health route drifted")
    require(fields["carrier-connection"] in {"offline", "tcp"},
            "route-target-health carrier is not strict routed TCP/offline")
    require(fields["target-source"] == "configured-tcp-relay-0",
            "route-target-health source is not the first configured relay")
    require(fields["probe-stage"] in {
        "proxy-connect", "method-negotiation", "target-connect", "complete",
    }, "route-target-health stage is invalid")
    require(fields["target-health"] in {
        "reachable", "refused", "denied", "timed-out", "unreachable", "failed",
    }, "route-target-health result is invalid")
    require(fields["target-rtt-us"].isdigit(),
            "route-target-health RTT is not canonical decimal")
    reply: int | None = None
    if fields["socks-reply-code"] != "none":
        require(fields["socks-reply-code"].isdigit(),
                "route-target-health reply is not canonical decimal")
        reply = int(fields["socks-reply-code"])
        require(0 <= reply <= 255, "route-target-health reply is outside one byte")
    require(fields["semantics"] == ROUTE_TARGET_SEMANTICS,
            "route-target-health mutation disclaimer drifted")
    return {
        "carrier_connection": fields["carrier-connection"],
        "network": fields["network"],
        "phase": phase,
        "probe_stage": fields["probe-stage"],
        "semantics": fields["semantics"],
        "socks_reply_code": reply,
        "target_health": fields["target-health"],
        "target_rtt_us": int(fields["target-rtt-us"]),
        "target_source": fields["target-source"],
    }


def sample_route_target_health(
    iotox_binary: Path, runtime: Path, phase: str,
) -> dict[str, object]:
    completed = subprocess.run(
        [
            str(iotox_binary), "--runtime", str(runtime),
            "--timeout-ms", "5000", "route-target-health",
        ],
        check=True, text=True, capture_output=True, timeout=8,
    )
    require(not completed.stderr, "route-target-health wrote unexpected diagnostics")
    return parse_route_target_health(completed.stdout, phase)


def target_probe_circuit_evidence(
    root: Path,
    iotox_binary: Path,
    runtime: Path,
    agent_pid: int,
    socks_port: int,
    target: str,
    phase: str,
) -> tuple[dict[str, object], dict[str, object]]:
    existing_source_ports = {
        int(record["local_port"])
        for record in process_inet_sockets(agent_pid, "tcp")
        if record["remote_address"] == "127.0.0.1"
        and int(record["remote_port"]) == socks_port
    }
    cookie = (root / "control.authcookie").read_bytes()
    require(len(cookie) == 32, "Tor control cookie is not 32 bytes")
    new_stream_sources: dict[str, int] = {}
    selected_streams: list[tuple[str, str, int]] = []
    event_lines: list[str] = []
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as control:
        control.settimeout(10)
        control.connect(str(root / "control.sock"))
        stream = control.makefile("rwb", buffering=0)
        stream.write(f"AUTHENTICATE {cookie.hex()}\r\n".encode("ascii"))
        require(
            stream.readline().decode("ascii", errors="strict").rstrip("\r\n") ==
                "250 OK",
            "Tor control authentication failed for target probe",
        )
        stream.write(b"USEFEATURE EXTENDED_EVENTS\r\n")
        require(
            stream.readline().decode("ascii", errors="strict").rstrip("\r\n") ==
                "250 OK",
            "Tor refused extended STREAM evidence for target probe",
        )
        stream.write(b"SETEVENTS STREAM\r\n")
        require(
            stream.readline().decode("ascii", errors="strict").rstrip("\r\n") ==
                "250 OK",
            "Tor refused STREAM events for target probe",
        )

        observation = sample_route_target_health(iotox_binary, runtime, phase)
        require(
            observation["carrier_connection"] == "tcp"
            and observation["probe_stage"] == "complete"
            and observation["target_health"] == "reachable"
            and observation["socks_reply_code"] == 0,
            f"{phase} configured-target observation did not succeed",
        )
        event_deadline = time.monotonic() + 1.0
        while time.monotonic() < event_deadline:
            control.settimeout(max(0.1, event_deadline - time.monotonic()))
            try:
                line = stream.readline().decode(
                    "ascii", errors="strict").rstrip("\r\n")
            except (TimeoutError, OSError):
                break
            if not line:
                break
            event_lines.append(line)
            fields = line.split()
            if (len(fields) < 6 or fields[0] != "650" or
                fields[1] != "STREAM" or fields[5] != target):
                continue
            if fields[3] == "NEW":
                source_fields = [
                    field for field in fields[6:]
                    if field.startswith("SOURCE_ADDR=")
                ]
                if len(source_fields) != 1:
                    continue
                source_endpoint = source_fields[0].split("=", 1)[1]
                try:
                    source_host, source_port_text = source_endpoint.rsplit(":", 1)
                    source_port = int(source_port_text)
                except ValueError:
                    continue
                if (source_host == "127.0.0.1" and
                    source_port not in existing_source_ports):
                    new_stream_sources[fields[2]] = source_port
            elif fields[3] == "SUCCEEDED" and fields[2] in new_stream_sources:
                selected_streams.append(
                    (fields[2], fields[4], new_stream_sources[fields[2]]))

    (root / f"tor-control-{phase}-route-target-events.txt").write_text(
        "\n".join(event_lines) + "\n", encoding="ascii"
    )

    require(
        len(selected_streams) == 1,
        "authenticated Tor control did not see exactly one new successful configured-target stream",
    )
    stream_id, circuit_id, _ = selected_streams[0]
    circuits = tor_getinfo(root, "circuit-status").splitlines()
    (root / f"tor-control-{phase}-route-target-circuit-status.txt").write_text(
        "\n".join(circuits) + "\n", encoding="ascii"
    )
    circuit = next(
        (line for line in circuits if line.split()[:1] == [circuit_id]), "")
    circuit_fields = circuit.split()
    require(len(circuit_fields) >= 3 and circuit_fields[1] == "BUILT",
            "configured-target stream circuit is not built")
    purpose_fields = [
        field.split("=", 1)[1] for field in circuit_fields[3:]
        if field.startswith("PURPOSE=")
    ]
    require(len(purpose_fields) == 1
            and purpose_fields[0] in APPLICATION_CIRCUIT_PURPOSES,
            "configured-target stream circuit is not a public application circuit")
    path = circuit_fields[2]
    hop_count = len(path.split(","))
    require(hop_count >= 3,
            "configured-target stream circuit has fewer than three hops")
    return observation, {
        "circuit_hop_count": hop_count,
        "circuit_path_sha256": hashlib.sha256(path.encode("ascii")).hexdigest(),
        "circuit_purpose": purpose_fields[0],
        "control_authenticated": True,
        "phase": phase,
        "source_port_was_new": True,
        "stream_id_sha256": hashlib.sha256(stream_id.encode("ascii")).hexdigest(),
        "stream_target": target,
        "target_source": "configured-tcp-relay-0",
    }


def self_test() -> int:
    node = parse_node("8.8.8.8:443:" + "ab" * 32)
    require(node_record(node) == "8.8.8.8:443:" + "AB" * 32, "node normalization drifted")
    require(decode_proc_address("0100007F", 4) == "127.0.0.1", "IPv4 /proc decode failed")
    require(
        decode_proc_address("00000000000000000000000001000000", 6) == "::1",
        "IPv6 /proc decode failed",
    )
    rendered, normalized = tor_configuration(Path("/private/run"), 39060)
    require(len(rendered) == len(normalized) == 11, "Tor configuration field count drifted")
    require(all("/private/run" not in line for line in normalized),
            "normalized Tor configuration retained the private run root")
    require("SafeSocks 0" in normalized, "numeric-relay Tor policy drifted")
    evidence = select_circuit_evidence(
        ["19 SUCCEEDED 7 8.8.8.8:443 SOURCE_ADDR=127.0.0.1:40000"],
        [
            "7 BUILT $" + "11" * 20 + "~a,$" + "22" * 20
            + "~b,$" + "33" * 20 + "~c PURPOSE=GENERAL TIME_CREATED=now"
        ],
        {"8.8.8.8:443"},
        "self-test",
    )
    require(evidence["circuit_hop_count"] == 3, "Tor circuit parsing drifted")
    require(evidence["circuit_purpose"] == "GENERAL", "Tor circuit purpose parsing drifted")
    conflux_evidence = select_circuit_evidence(
        ["20 SUCCEEDED 8 8.8.8.8:443"],
        [
            "8 BUILT $" + "44" * 20 + "~d,$" + "55" * 20
            + "~e,$" + "66" * 20 + "~f PURPOSE=CONFLUX_LINKED TIME_CREATED=now"
        ],
        {"8.8.8.8:443"},
        "self-test-conflux",
    )
    require(conflux_evidence["circuit_purpose"] == "CONFLUX_LINKED",
            "Tor Conflux circuit purpose parsing drifted")
    health = parse_route_health(
        "network=Tox/Tor\n"
        "carrier-connection=tcp\n"
        "local-boundary=reachable\n"
        "local-boundary-rtt-us=123\n"
        "upstream=carrier-reported-online\n"
        "application=not-sampled\n"
        "application-rtt-us=not-sampled\n"
        "application-error=none\n"
        f"semantics={ROUTE_HEALTH_SEMANTICS}\n",
        "self-test",
    )
    require(health["local_boundary_rtt_us"] == 123,
            "route-health parsing drifted")
    target_health = parse_route_target_health(
        "network=Tox/Tor\n"
        "carrier-connection=tcp\n"
        "target-source=configured-tcp-relay-0\n"
        "probe-stage=complete\n"
        "target-health=reachable\n"
        "target-rtt-us=456\n"
        "socks-reply-code=0\n"
        f"semantics={ROUTE_TARGET_SEMANTICS}\n",
        "self-test",
    )
    require(target_health["target_rtt_us"] == 456,
            "route-target-health parsing drifted")
    print("iotox operator Tor smoke self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", action="append", type=parse_node,
                        help="public numeric IP:PORT:64_HEX_KEY; repeatable")
    parser.add_argument("--tor-bin", type=Path, default=Path(shutil.which("tor") or ""))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--keep", action="store_true")
    parser.add_argument("--tor-bootstrap-timeout", type=float, default=240)
    parser.add_argument("--online-timeout", type=float, default=360)
    parser.add_argument("--offline-timeout", type=float, default=180)
    parser.add_argument("--recovery-timeout", type=float, default=360)
    parser.add_argument("--outage-hold-seconds", type=float, default=30)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        return self_test()

    require(sys.platform.startswith("linux"), "route socket proof requires Linux /proc")
    require(arguments.node, "at least one explicit current public Tox TCP node is required")
    require(arguments.outage_hold_seconds >= 10,
            "qualification outage hold must be at least 10 seconds")
    nodes = list(arguments.node)
    require(len({node_record(node) for node in nodes}) == len(nodes),
            "duplicate public Tox node records are not allowed")
    tor_binary = arguments.tor_bin.expanduser().resolve()
    require(tor_binary.is_file() and os.access(tor_binary, os.X_OK),
            "--tor-bin does not resolve to an executable")

    source_commit = clean_source_revision()
    iotox_binary = realize_iotox()
    root = private_process_root()
    socks_port = free_loopback_port()
    rendered_config, normalized_config = tor_configuration(root, socks_port)
    torrc = root / "torrc"
    torrc.write_text("\n".join(rendered_config) + "\n", encoding="ascii")
    subprocess.run(
        [str(tor_binary), "--verify-config", "--defaults-torrc", "/dev/null", "-f", str(torrc)],
        cwd=root, check=True, text=True, capture_output=True, timeout=30,
    )

    tor: subprocess.Popen[object] | None = None
    agent: subprocess.Popen[object] | None = None
    tor_logs: list[object] = []
    agent_log = None
    succeeded = False
    gate_started = time.monotonic()
    try:
        tor, first_tor_log = start_tor(
            tor_binary, torrc, root, socks_port, root / "tor-first.log",
            arguments.tor_bootstrap_timeout,
        )
        tor_logs.append(first_tor_log)
        runtime = root / "runtime"
        state = root / "state" / "device.toxsave"
        agent_log = (root / "iotox.log").open("wb")
        run_ms = int((
            arguments.online_timeout + arguments.offline_timeout
            + arguments.outage_hold_seconds + arguments.recovery_timeout + 180
        ) * 1000)
        command = [
            str(iotox_binary), "run",
            "--state", str(state),
            "--runtime", str(runtime),
            "--network", "tox/tor",
            "--socks5-proxy", f"127.0.0.1:{socks_port}",
            "--bootstrap-retry-ms", "1000",
            "--run-ms", str(run_ms),
        ]
        for node in nodes:
            command.extend(("--bootstrap", node_record(node)))
            command.extend(("--tcp-relay", node_record(node)))
        agent = subprocess.Popen(
            command, cwd=root, stdout=agent_log, stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        connection = runtime / "self" / "connection"
        network = runtime / "self" / "network"

        def agent_state(expected: str) -> bool:
            process_alive(agent, root / "iotox.log", "source-linked IoTox")
            return read_state(connection, expected)

        agent_started = time.monotonic()
        wait_for(lambda: agent_state("tcp"), arguments.online_timeout,
                 "source-linked Tox/Tor TCP through public Tor")
        initial_online_ms = int((time.monotonic() - agent_started) * 1000)
        require(read_state(network, "Tox/Tor"), "runtime route projection drifted")
        socket_observations = [agent_socket_evidence(agent.pid, socks_port, "initial", True)]
        first_target = node_endpoint(nodes[0])
        initial_target, initial_target_circuit = target_probe_circuit_evidence(
            root, iotox_binary, runtime, agent.pid, socks_port,
            first_target, "initial",
        )
        route_target_observations = [initial_target]
        route_target_circuit_observations = [initial_target_circuit]
        initial_circuit = circuit_evidence(
            root, {node_endpoint(node) for node in nodes}, "initial"
        )
        initial_circuit.update(tor_public_socket_evidence(tor.pid))
        route_health_observations = [
            sample_route_health(iotox_binary, runtime, "initial")
        ]
        require(
            route_health_observations[-1]["carrier_connection"] == "tcp"
            and route_health_observations[-1]["local_boundary"] == "reachable"
            and route_health_observations[-1]["upstream"] == "carrier-reported-online",
            "initial auxiliary route-health observation is incoherent",
        )

        loss_started = time.monotonic()
        terminate(tor)
        tor = None
        route_health_observations.append(
            sample_route_health(iotox_binary, runtime, "post-tor-exit")
        )
        route_target_observations.append(
            sample_route_target_health(
                iotox_binary, runtime, "post-tor-exit")
        )
        local_loss_ms = int((time.monotonic() - loss_started) * 1000)
        require(
            route_health_observations[-1]["carrier_connection"] == "tcp"
            and route_health_observations[-1]["local_boundary"] == "refused"
            and route_health_observations[-1]["upstream"] == "carrier-reported-online",
            "local route loss did not remain separate from authoritative carrier truth",
        )
        require(
            route_target_observations[-1]["carrier_connection"] == "tcp"
            and route_target_observations[-1]["probe_stage"] == "proxy-connect"
            and route_target_observations[-1]["target_health"] in {
                "refused", "unreachable", "failed",
            }
            and route_target_observations[-1]["socks_reply_code"] is None,
            "configured-target proxy loss did not remain separate from carrier truth",
        )
        require(local_loss_ms <= 5000,
                "local route-loss observation exceeded its five-second gate")
        wait_for(lambda: agent_state("offline"), arguments.offline_timeout,
                 "authoritative offline state after Tor death")
        loss_to_offline_ms = int((time.monotonic() - loss_started) * 1000)
        route_health_observations.append(
            sample_route_health(iotox_binary, runtime, "authoritative-offline")
        )
        require(
            route_health_observations[-1]["carrier_connection"] == "offline"
            and route_health_observations[-1]["local_boundary"] == "refused"
            and route_health_observations[-1]["upstream"] == "blocked-by-local-boundary",
            "offline auxiliary route-health observation is incoherent",
        )
        outage_samples: list[dict[str, object]] = []
        hold_started = time.monotonic()
        while time.monotonic() - hold_started < arguments.outage_hold_seconds:
            process_alive(agent, root / "iotox.log", "source-linked IoTox")
            require(read_state(connection, "offline"),
                    "IoTox left offline state while Tor remained absent")
            outage_samples.append(
                agent_socket_evidence(agent.pid, socks_port, "outage", False)
            )
            time.sleep(1)
        outage_hold_ms = int((time.monotonic() - hold_started) * 1000)
        socket_observations.append(
            agent_socket_evidence(agent.pid, socks_port, "outage-final", False)
        )

        tor, second_tor_log = start_tor(
            tor_binary, torrc, root, socks_port, root / "tor-restarted.log",
            arguments.tor_bootstrap_timeout,
        )
        tor_logs.append(second_tor_log)
        restart_ready = time.monotonic()
        wait_for(lambda: agent_state("tcp"), arguments.recovery_timeout,
                 "source-linked Tox/Tor recovery through restarted Tor")
        restart_to_online_ms = int((time.monotonic() - restart_ready) * 1000)
        require(read_state(network, "Tox/Tor"), "recovered runtime route projection drifted")
        socket_observations.append(
            agent_socket_evidence(agent.pid, socks_port, "recovered", True)
        )
        recovered_target, recovered_target_circuit = target_probe_circuit_evidence(
            root, iotox_binary, runtime, agent.pid, socks_port,
            first_target, "recovered",
        )
        route_target_observations.append(recovered_target)
        route_target_circuit_observations.append(recovered_target_circuit)
        recovered_circuit = circuit_evidence(
            root, {node_endpoint(node) for node in nodes}, "recovered"
        )
        recovered_circuit.update(tor_public_socket_evidence(tor.pid))
        route_health_observations.append(
            sample_route_health(iotox_binary, runtime, "recovered")
        )
        require(
            route_health_observations[-1]["carrier_connection"] == "tcp"
            and route_health_observations[-1]["local_boundary"] == "reachable"
            and route_health_observations[-1]["upstream"] == "carrier-reported-online",
            "recovered auxiliary route-health observation is incoherent",
        )

        iotox_version = subprocess.run(
            [str(iotox_binary), "--version"], check=True, text=True,
            capture_output=True, timeout=10,
        ).stdout.strip()
        tor_version = subprocess.run(
            [str(tor_binary), "--version"], check=True, text=True,
            capture_output=True, timeout=10,
        ).stdout.strip()
        receipt = {
            "agent_socket_observations": socket_observations,
            "carrier": "tcp",
            "circuit_observations": [initial_circuit, recovered_circuit],
            "direct_relay_socket_observed": False,
            "dns_policy": "iotox-native-dns-disabled;numeric-relays-only;tor-directory-network-owned-by-tor",
            "fixture": "operator-owned-tor-public-numeric-relay",
            "initial_online_ms": initial_online_ms,
            "iotox_sha256": sha256(iotox_binary),
            "iotox_version": iotox_version,
            "native_udp_socket_observed": False,
            "network": "Tox/Tor",
            "node_records": nodes,
            "nonclaims": [
                "anonymity-proof",
                "censorship-resistance-proof",
                "multi-exit-or-multi-network-reliability",
                "public-relay-sla",
                "representative-deployment-qualification",
                "automatic-route-or-terminal-recovery-policy",
            ],
            "operator_tor_smoke_sha256": sha256(Path(__file__).resolve()),
            "outage_agent_socket_sample_count": len(outage_samples),
            "outage_agent_socket_samples_sha256": canonical_sha256(outage_samples),
            "outage_hold_ms": outage_hold_ms,
            "proxy_loss_to_offline_ms": loss_to_offline_ms,
            "proxy_loss_to_local_boundary_ms": local_loss_ms,
            "proxy_restart_count": 1,
            "proxy_restart_to_online_ms": restart_to_online_ms,
            "recovery_observed": True,
            "route_health_observations": route_health_observations,
            "route_target_circuit_observations":
                route_target_circuit_observations,
            "route_target_observations": route_target_observations,
            "scope": "operator-tor-public-relay-single-host-single-sample-not-anonymity-proof",
            "socks_endpoint": f"127.0.0.1:{socks_port}",
            "source_commit": source_commit,
            "source_tree_clean": True,
            "tor_binary_path": str(tor_binary),
            "tor_configuration": normalized_config,
            "tor_configuration_sha256": canonical_sha256(normalized_config),
            "tor_invocation": [
                "--defaults-torrc", "/dev/null", "-f", "<RUN_ROOT>/torrc",
            ],
            "tor_sha256": sha256(tor_binary),
            "tor_version": tor_version,
            "total_gate_ms": int((time.monotonic() - gate_started) * 1000),
            "utc_completed": datetime.datetime.now(datetime.timezone.utc).isoformat(),
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
        terminate(tor)
        if agent_log is not None:
            agent_log.close()
        for log in tor_logs:
            log.close()
        if succeeded and not arguments.keep:
            shutil.rmtree(root)
        else:
            print(f"retained-operator-tor-smoke={root}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
