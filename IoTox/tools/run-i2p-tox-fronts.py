#!/usr/bin/env python3
"""Supervise the bounded three-front Tox-over-I2P construction topology.

The process owns two local i2pd routers, three persistent server Destinations,
three exact-target TCP egress shims, and one strict SOCKS-to-SAM adapter.  It
prints one machine-readable ready record, stays resident, and writes a
content-free final receipt after a signal.  Public Tox node records are always
explicit inputs; this tool never discovers or substitutes infrastructure.
"""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
import re
import select
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path


SCHEMA = "iotox.i2p-tox-fronts.v1"
NODE_PATTERN = re.compile(r"([^:]+):([0-9]+):([0-9A-Fa-f]{64})")
MAX_ROUTER_FAULT_DENIALS = 384


class FrontError(RuntimeError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise FrontError(detail)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def tree_sha256(root: Path, domain: bytes) -> tuple[str, int]:
    digest = hashlib.sha256(domain + b"\0")
    count = 0
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        if path.is_symlink():
            target_text = os.readlink(path)
            require(
                not os.path.isabs(target_text) and path.resolve().is_relative_to(root),
                "router source tree contains an escaping symbolic link",
            )
            target = target_text.encode("utf-8")
            digest.update(len(relative).to_bytes(8, "big"))
            digest.update(relative)
            digest.update(b"L")
            digest.update(len(target).to_bytes(8, "big"))
            digest.update(target)
            count += 1
        elif path.is_file():
            content = path.read_bytes()
            digest.update(len(relative).to_bytes(8, "big"))
            digest.update(relative)
            digest.update(b"F")
            digest.update((path.stat().st_mode & 0o111 != 0).to_bytes(1, "big"))
            digest.update(len(content).to_bytes(8, "big"))
            digest.update(content)
            count += 1
        else:
            require(path.is_dir(), "router source tree contains a special entry")
    require(count > 0, "router source tree is empty")
    return digest.hexdigest(), count


def source_tree_sha256(root: Path) -> tuple[str, int]:
    return tree_sha256(root, b"iotox-i2pd-source-tree-v1")


def certificates_tree_sha256(root: Path) -> tuple[str, int]:
    return tree_sha256(root, b"iotox-i2pd-certificates-tree-v1")


def process_start_ticks(pid: int) -> int:
    record = Path(f"/proc/{pid}/stat").read_text(encoding="ascii")
    closing = record.rfind(")")
    require(closing > 0, f"cannot parse process stat for PID {pid}")
    fields = record[closing + 2 :].split()
    require(
        len(fields) > 19 and fields[19].isascii() and fields[19].isdecimal(),
        f"process start time is invalid for PID {pid}",
    )
    return int(fields[19])


def process_socket_inodes(pid: int) -> set[str]:
    output: set[str] = set()
    for descriptor in Path(f"/proc/{pid}/fd").iterdir():
        try:
            target = os.readlink(descriptor)
        except (FileNotFoundError, PermissionError):
            continue
        match = re.fullmatch(r"socket:\[([0-9]+)\]", target)
        if match is not None:
            output.add(match.group(1))
    require(output, f"router PID {pid} owns no sockets")
    return output


def decode_proc_address(value: str, version: int) -> str:
    raw = bytes.fromhex(value)
    if version == 4:
        return str(ipaddress.IPv4Address(raw[::-1]))
    require(len(raw) == 16, "Linux IPv6 socket address has the wrong size")
    reordered = b"".join(
        raw[offset : offset + 4][::-1] for offset in range(0, 16, 4)
    )
    return str(ipaddress.IPv6Address(reordered))


def router_tcp_inventory(
    role: str, process: subprocess.Popen[object], sam: tuple[str, int]
) -> dict[str, object]:
    require(process.poll() is None, f"{role} router exited before socket attribution")
    inodes = process_socket_inodes(process.pid)
    public_remotes: set[str] = set()
    sam_listener_owned = False
    for version, table in (
        (4, Path("/proc/net/tcp")),
        (6, Path("/proc/net/tcp6")),
    ):
        if not table.is_file():
            continue
        for line in table.read_text(encoding="ascii").splitlines()[1:]:
            fields = line.split()
            if len(fields) < 10 or fields[9] not in inodes:
                continue
            local_hex, local_port_hex = fields[1].split(":")
            remote_hex, remote_port_hex = fields[2].split(":")
            local_address = decode_proc_address(local_hex, version)
            remote_address = decode_proc_address(remote_hex, version)
            local_port = int(local_port_hex, 16)
            remote_port = int(remote_port_hex, 16)
            if (
                fields[3] == "0A"
                and local_address == sam[0]
                and local_port == sam[1]
            ):
                sam_listener_owned = True
            if (
                fields[3] == "01"
                and remote_port != 0
                and ipaddress.ip_address(remote_address).is_global
            ):
                public_remotes.add(f"{remote_address}:{remote_port}")
    require(sam_listener_owned, f"{role} router does not own its SAM listener")
    require(public_remotes, f"{role} router owns no established public TCP socket")
    digest = hashlib.sha256(b"iotox-i2pd-public-tcp-remotes-v1\0")
    for remote in sorted(public_remotes):
        encoded = remote.encode("ascii")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return {
        "role": role,
        "pid": process.pid,
        "process_start_ticks": process_start_ticks(process.pid),
        "sam_listener_owned": True,
        "public_tcp_remote_count": len(public_remotes),
        "public_tcp_remote_set_sha256": digest.hexdigest(),
        "contains_secrets": False,
    }


def wait_for_router_tcp_inventory(
    role: str,
    process: subprocess.Popen[object],
    sam: tuple[str, int],
    timeout: float,
) -> dict[str, object]:
    deadline = time.monotonic() + timeout
    last_error = "router socket attribution did not start"
    while time.monotonic() < deadline:
        try:
            return router_tcp_inventory(role, process, sam)
        except (FrontError, OSError, UnicodeError, ValueError) as error:
            last_error = str(error)
        time.sleep(0.2)
    raise FrontError(f"{role} router socket attribution timed out: {last_error}")


def endpoint(text: str, *, loopback: bool = False) -> tuple[str, int]:
    fields = text.rsplit(":", 1)
    if len(fields) != 2 or not fields[1].isascii() or not fields[1].isdecimal():
        raise argparse.ArgumentTypeError("endpoint must be numeric HOST:PORT")
    try:
        address = ipaddress.ip_address(fields[0])
    except ValueError as error:
        raise argparse.ArgumentTypeError("endpoint address must be numeric") from error
    port = int(fields[1])
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("endpoint port is out of range")
    if loopback and not address.is_loopback:
        raise argparse.ArgumentTypeError("endpoint must be loopback")
    return address.compressed, port


def parse_node(text: str) -> dict[str, object]:
    match = NODE_PATTERN.fullmatch(text)
    if match is None:
        raise argparse.ArgumentTypeError("node must be public IPv4:PORT:64_HEX_KEY")
    try:
        address = ipaddress.ip_address(match.group(1))
    except ValueError as error:
        raise argparse.ArgumentTypeError("node address must be numeric") from error
    port = int(match.group(2))
    if address.version != 4 or not address.is_global:
        raise argparse.ArgumentTypeError("node address must be public IPv4")
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("node port is out of range")
    key = match.group(3).upper()
    return {
        "address": address.compressed,
        "port": port,
        "public_key": key,
        "target": f"{address.compressed}:{port}",
        "record": f"{address.compressed}:{port}:{key}",
    }


def write_new(path: Path, value: dict[str, object]) -> None:
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        os.write(descriptor, payload)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def port_open(address: str, port: int) -> bool:
    try:
        with socket.create_connection((address, port), timeout=0.25):
            return True
    except OSError:
        return False


def wait_for(predicate, timeout: float, detail: str) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.1)
    raise FrontError(f"timeout waiting for {detail}")


def terminate(processes: list[subprocess.Popen[object]]) -> None:
    for process in reversed(processes):
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline and any(
        process.poll() is None for process in processes
    ):
        time.sleep(0.1)
    for process in reversed(processes):
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        try:
            process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            pass


def read_ready(process: subprocess.Popen[str], timeout: float, prefix: str) -> str:
    require(process.stdout is not None, f"{prefix} stdout is unavailable")
    readable, _, _ = select.select([process.stdout], [], [], timeout)
    require(bool(readable), f"{prefix} did not report readiness")
    line = process.stdout.readline().strip()
    require(line.startswith("ready="), f"{prefix} readiness drifted: {line}")
    return line.removeprefix("ready=")


def router_command(
    binary: Path,
    source: Path,
    datadir: Path,
    sam: tuple[str, int],
    public_port: int,
) -> list[str]:
    return [
        str(binary),
        f"--datadir={datadir}",
        f"--certsdir={source / 'contrib/certificates'}",
        f"--pidfile={datadir / 'i2pd.pid'}",
        "--log=stdout",
        "--loglevel=info",
        f"--port={public_port}",
        "--ipv4",
        "--notransit",
        "--bandwidth=P",
        "--share=0",
        "--http.enabled=false",
        "--httpproxy.enabled=false",
        "--socksproxy.enabled=false",
        "--bob.enabled=false",
        "--i2cp.enabled=false",
        "--i2pcontrol.enabled=false",
        "--upnp.enabled=false",
        "--ntcp2.enabled=true",
        "--ssu2.enabled=false",
        "--addressbook.enabled=false",
        "--nettime.enabled=false",
        "--reseed.verify=true",
        "--sam.enabled=true",
        f"--sam.address={sam[0]}",
        f"--sam.port={sam[1]}",
        "--sam.singlethread=false",
    ]


def audit_summary(path: Path) -> dict[str, object]:
    require(path.is_file() and not path.is_symlink(), f"audit is absent: {path}")
    records = [json.loads(line) for line in path.read_text(encoding="ascii").splitlines()]
    require(all(isinstance(record, dict) for record in records), "audit record drifted")
    outcomes: dict[str, int] = {}
    for record in records:
        outcome = str(record.get("outcome", ""))
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
    return {
        "path": path.name,
        "sha256": sha256(path),
        "records": len(records),
        "outcomes": outcomes,
    }


def validate_adapter_audit(
    path: Path,
    destinations: list[str],
    fault_kind: str = "",
    fault_started_ns: int = 0,
    fault_recovered_ns: int = 0,
) -> None:
    require(
        fault_kind in {"", "client-router", "server-fronts"},
        "adapter validation fault kind is invalid",
    )
    expect_router_restart = fault_kind == "client-router"
    expect_server_front_restart = fault_kind == "server-fronts"
    expect_fault = bool(fault_kind)
    records = [json.loads(line) for line in path.read_text(encoding="ascii").splitlines()]
    commitments = {
        hashlib.sha256(("iotox-i2p-b32-v1\0" + value).encode("ascii")).hexdigest()
        for value in destinations
    }
    connection_records = [
        record for record in records if record.get("event") == "socks5-i2p-connect"
    ]
    admitted = [record for record in connection_records if record.get("outcome") == "admitted"]
    denied = [
        record for record in connection_records if record.get("outcome") != "admitted"
    ]
    session_records = [record for record in records if record.get("event") == "sam-session"]
    expected_session_outcomes = (
        ["ready", "lost", "ready"] if expect_router_restart else ["ready"]
    )
    allowed_denials = (
        {"denied-stream", "denied-sam-unavailable", "denied-stale-generation"}
        if expect_router_restart
        else {"denied-stream"}
        if expect_server_front_restart
        else {"denied-stream"}
    )
    require(
        [record.get("outcome") for record in session_records]
        == expected_session_outcomes
        and [record.get("generation") for record in session_records]
        == ([1, 1, 2] if expect_router_restart else [1]),
        "adapter session lifecycle drifted",
    )
    require(
        len(records) == len(connection_records) + len(session_records)
        and 6 <= len(admitted) <= 24
        and len(denied) <= (MAX_ROUTER_FAULT_DENIALS if expect_fault else 6)
        and len(admitted) + len(denied) == len(connection_records)
        and all(
            record.get("outcome") in {"admitted", *allowed_denials}
            and record.get("destination_sha256") in commitments
            for record in connection_records
        ),
        "adapter recorded an unbounded outcome or destination",
    )
    require(
        {record.get("destination_sha256") for record in admitted} == commitments,
        "adapter did not admit both three-front populations",
    )
    if expect_router_restart:
        generation_one = [
            record for record in admitted if record.get("generation") == 1
        ]
        generation_two = [
            record for record in admitted if record.get("generation") == 2
        ]
        require(
            {record.get("destination_sha256") for record in generation_one}
            == commitments,
            "adapter generation one did not admit every front",
        )
        # c-toxcore may stop retrying redundant bootstrap fronts after the
        # authenticated peer session returns.  Bilateral recovery is proved by
        # the joined guest receipts; this seam only requires both guest-side
        # streams to re-enter through a committed generation-two front.
        require(
            len(generation_two) >= 2
            and {
                record.get("destination_sha256") for record in generation_two
            }.issubset(commitments),
            "adapter generation two did not admit both recovering guests",
        )
    if expect_server_front_restart:
        require(
            fault_started_ns > 0 and fault_recovered_ns > fault_started_ns,
            "server-front fault interval is invalid",
        )
        pre_fault = [
            record
            for record in admitted
            if isinstance(record.get("monotonic_ns"), int)
            and record["monotonic_ns"] < fault_started_ns
        ]
        post_recovery = [
            record
            for record in admitted
            if isinstance(record.get("monotonic_ns"), int)
            and record["monotonic_ns"] > fault_recovered_ns
        ]
        require(
            {record.get("destination_sha256") for record in pre_fault}
            == commitments,
            "adapter did not admit every front before the server-front fault",
        )
        require(
            len(post_recovery) >= 2
            and {
                record.get("destination_sha256") for record in post_recovery
            }.issubset(commitments),
            "adapter did not admit both guests after server-front recovery",
        )


def audit_has_session(path: Path, outcome: str, generation: int) -> bool:
    if not path.is_file() or path.is_symlink():
        return False
    try:
        records = [
            json.loads(line) for line in path.read_text(encoding="ascii").splitlines()
        ]
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    return any(
        record.get("event") == "sam-session"
        and record.get("outcome") == outcome
        and record.get("generation") == generation
        for record in records
        if isinstance(record, dict)
    )


def consume_control(path: Path, expected: str) -> None:
    require(path.is_file() and not path.is_symlink(), f"invalid control path: {path.name}")
    require(path.stat().st_uid == os.getuid(), f"unowned control path: {path.name}")
    require(path.read_text(encoding="ascii") == expected, f"invalid control: {path.name}")
    path.unlink()


def run(arguments: argparse.Namespace) -> int:
    root = arguments.work_root.resolve()
    require(root.is_dir() and not root.is_symlink(), "work root must be an existing directory")
    require(root.stat().st_uid == os.getuid(), "work root must be owned by this user")
    os.chmod(root, 0o700)
    binary = arguments.router_binary.resolve()
    source = arguments.router_source.resolve()
    socat = arguments.socat.resolve()
    require(binary.is_file() and not binary.is_symlink(), "router binary is invalid")
    require(source.is_dir() and not source.is_symlink(), "router source is invalid")
    require(socat.is_file() and not socat.is_symlink(), "socat binary is invalid")
    nodes = arguments.node
    require(len(nodes) == 3, "the construction topology requires exactly three nodes")
    require(len({str(node["record"]) for node in nodes}) == 3, "node records must be distinct")
    require(len({str(node["public_key"]) for node in nodes}) == 3, "node keys must be distinct")
    require(arguments.server_sam != arguments.client_sam, "router SAM endpoints must differ")
    require(arguments.server_port != arguments.client_port, "router public ports must differ")

    source_digest, source_files = source_tree_sha256(source)
    certificates = source / "contrib/certificates"
    require(
        certificates.is_dir() and not certificates.is_symlink(),
        "router certificate bundle is absent",
    )
    certificate_digest, certificate_files = certificates_tree_sha256(certificates)
    require(
        certificate_files >= 2
        and (certificates / "family").is_dir()
        and (certificates / "reseed").is_dir(),
        "router certificate bundle is incomplete",
    )
    version = subprocess.run(
        [str(binary), "--version"],
        check=True,
        text=True,
        capture_output=True,
        timeout=10.0,
    ).stdout.strip()
    require(version.startswith("i2pd version "), "router version output drifted")

    processes: list[subprocess.Popen[object]] = []
    logs: list[object] = []
    stopping = False

    def request_stop(_signum: int, _frame: object) -> None:
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    started_ns = time.monotonic_ns()
    destinations: list[str] = []
    router_restart_count = 0
    server_front_restart_count = 0
    fault_summary: dict[str, object] = {}
    server_front_fault: dict[str, object] = {}
    recovered_client_socket_attribution: dict[str, object] = {}
    restarted_forward_audits: list[Path] = []
    try:
        routers: list[subprocess.Popen[object]] = []
        router_logs: dict[str, object] = {}
        for label, sam, public_port in (
            ("server", arguments.server_sam, arguments.server_port),
            ("client", arguments.client_sam, arguments.client_port),
        ):
            datadir = root / f"{label}-router"
            datadir.mkdir(mode=0o700)
            log = (root / f"{label}-router.log").open("wb")
            logs.append(log)
            router_logs[label] = log
            process = subprocess.Popen(
                router_command(binary, source, datadir, sam, public_port),
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            processes.append(process)
            routers.append(process)
        for label, process, sam in zip(
            ("server", "client"), routers, (arguments.server_sam, arguments.client_sam)
        ):
            wait_for(
                lambda process=process, sam=sam: process.poll() is not None
                or port_open(*sam),
                arguments.startup_timeout,
                f"{label} router SAM listener",
            )
            require(process.poll() is None and port_open(*sam), f"{label} router exited")

        forward_processes: list[subprocess.Popen[str]] = []
        for index, node in enumerate(nodes, start=1):
            egress_port = arguments.egress_port_base + index - 1
            egress_log = (root / f"egress-{index}.log").open("wb")
            logs.append(egress_log)
            egress = subprocess.Popen(
                [
                    str(socat),
                    f"TCP4-LISTEN:{egress_port},bind=127.0.0.1,reuseaddr,fork",
                    f"TCP4:{node['address']}:{node['port']}",
                ],
                stdout=egress_log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            processes.append(egress)
            wait_for(
                lambda process=egress, port=egress_port: process.poll() is not None
                or port_open("127.0.0.1", port),
                10.0,
                f"egress shim {index}",
            )
            require(egress.poll() is None, f"egress shim {index} exited")
            forward_stderr = (root / f"forward-{index}.stderr").open(
                "w", encoding="utf-8"
            )
            logs.append(forward_stderr)
            forward = subprocess.Popen(
                [
                    sys.executable,
                    str(Path(__file__).with_name("run-i2p-sam-forward.py")),
                    "--sam",
                    f"{arguments.server_sam[0]}:{arguments.server_sam[1]}",
                    "--target",
                    f"127.0.0.1:{egress_port}",
                    "--destination-key",
                    str(root / f"service-{index}.destination"),
                    "--audit",
                    str(root / f"forward-{index}.audit.jsonl"),
                    "--startup-timeout",
                    str(arguments.startup_timeout),
                    "--command-timeout",
                    str(arguments.command_timeout),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=forward_stderr,
                start_new_session=True,
            )
            processes.append(forward)
            forward_processes.append(forward)
            destination = read_ready(forward, arguments.startup_timeout, f"service front {index}")
            require(
                re.fullmatch(r"[a-z2-7]{52}\.b32\.i2p", destination) is not None,
                "service Destination is noncanonical",
            )
            destinations.append(destination)

        adapter_stderr = (root / "adapter.stderr").open("w", encoding="utf-8")
        logs.append(adapter_stderr)
        adapter = subprocess.Popen(
            [
                sys.executable,
                str(Path(__file__).with_name("run-i2p-sam-socks.py")),
                "--listen",
                f"{arguments.listen[0]}:{arguments.listen[1]}",
                "--sam",
                f"{arguments.client_sam[0]}:{arguments.client_sam[1]}",
                *sum(
                    (
                        ["--map", f"{node['target']}={destination}"]
                        for node, destination in zip(nodes, destinations)
                    ),
                    [],
                ),
                "--audit",
                str(root / "adapter.audit.jsonl"),
                "--startup-timeout",
                str(arguments.startup_timeout),
                "--command-timeout",
                str(arguments.command_timeout),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=adapter_stderr,
            start_new_session=True,
        )
        processes.append(adapter)
        ready_endpoint = read_ready(adapter, arguments.startup_timeout, "client adapter")
        require(
            ready_endpoint == f"{arguments.listen[0]}:{arguments.listen[1]}",
            "adapter bound an unexpected endpoint",
        )

        initial_socket_attribution = [
            wait_for_router_tcp_inventory(label, process, sam, arguments.startup_timeout)
            for label, process, sam in zip(
                ("server", "client"),
                routers,
                (arguments.server_sam, arguments.client_sam),
            )
        ]

        ready = {
            "schema": SCHEMA,
            "status": "ready",
            "proxy_endpoint": ready_endpoint,
            "nodes": [str(node["record"]) for node in nodes],
            "destination_commitments": [
                hashlib.sha256(("iotox-i2p-b32-v1\0" + value).encode("ascii")).hexdigest()
                for value in destinations
            ],
            "router_binary": str(binary),
            "router_binary_sha256": sha256(binary),
            "router_source": str(source),
            "router_source_tree_sha256": source_digest,
            "router_source_file_count": source_files,
            "router_certificates_relative_path": "contrib/certificates",
            "router_certificates_tree_sha256": certificate_digest,
            "router_certificates_file_count": certificate_files,
            "router_reseed_signature_verification": True,
            "router_socket_attribution": {
                "initial": initial_socket_attribution,
                "recovered_client": None,
            },
            "router_version": version,
            "router_processes": [
                {"role": label, "pid": process.pid, "sam_port": sam[1]}
                for label, process, sam in zip(
                    ("server", "client"),
                    routers,
                    (arguments.server_sam, arguments.client_sam),
                )
            ],
            "front_count": 3,
            "contains_secrets": False,
        }
        write_new(root / "topology-ready.json", ready)
        print("ready=" + json.dumps(ready, sort_keys=True, separators=(",", ":")), flush=True)
        fault_request = root / "fault-client-router"
        recover_request = root / "recover-client-router"
        front_fault_request = root / "fault-server-fronts"
        front_recover_request = root / "recover-server-fronts"
        fault_state = "idle"
        fault_kind = ""
        fault_started_ns = 0
        fault_recovered_ns = 0
        old_client_pid = 0
        old_front_pids: list[int] = []
        while not stopping:
            failed = [process.pid for process in processes if process.poll() is not None]
            require(not failed, f"topology child exited early: {failed}")
            if fault_state == "idle" and fault_request.exists():
                consume_control(fault_request, "fault-client-router=1\n")
                require(
                    port_open(*arguments.listen),
                    "guest-facing adapter listener was absent before the router fault",
                )
                old_client = routers[1]
                old_client_pid = old_client.pid
                processes.remove(old_client)
                terminate([old_client])
                wait_for(
                    lambda: not port_open(*arguments.client_sam),
                    15.0,
                    "client router SAM listener to close",
                )
                wait_for(
                    lambda: audit_has_session(
                        root / "adapter.audit.jsonl", "lost", 1
                    ),
                    30.0,
                    "adapter to record generation-one SAM loss",
                )
                listener_reachable = port_open(*arguments.listen)
                require(
                    listener_reachable,
                    "guest-facing adapter listener did not survive SAM loss",
                )
                fault_started_ns = time.monotonic_ns()
                write_new(
                    root / "fault-active.json",
                    {
                        "schema": SCHEMA,
                        "status": "fault-active",
                        "kind": "client-router-process-restart",
                        "old_client_router_pid": old_client_pid,
                        "adapter_listener_reachable": listener_reachable,
                        "client_sam_listener_reachable": port_open(
                            *arguments.client_sam
                        ),
                        "adapter_generation_one_lost": True,
                        "contains_secrets": False,
                    },
                )
                fault_state = "active"
                fault_kind = "client-router"
            elif fault_state == "idle" and front_fault_request.exists():
                consume_control(front_fault_request, "fault-server-fronts=1\n")
                require(
                    port_open(*arguments.listen)
                    and port_open(*arguments.server_sam)
                    and port_open(*arguments.client_sam),
                    "I2P listeners were absent before the server-front fault",
                )
                old_front_pids = [process.pid for process in forward_processes]
                for process in forward_processes:
                    processes.remove(process)
                terminate(list(forward_processes))
                require(
                    all(process.poll() is not None for process in forward_processes),
                    "a server front survived the fault",
                )
                listener_reachable = port_open(*arguments.listen)
                server_sam_reachable = port_open(*arguments.server_sam)
                client_sam_reachable = port_open(*arguments.client_sam)
                require(
                    listener_reachable
                    and server_sam_reachable
                    and client_sam_reachable
                    and all(router.poll() is None for router in routers),
                    "router or bridge availability changed during the server-front fault",
                )
                fault_started_ns = time.monotonic_ns()
                write_new(
                    root / "front-fault-active.json",
                    {
                        "schema": SCHEMA,
                        "status": "fault-active",
                        "kind": "server-front-process-restart",
                        "old_server_front_pids": old_front_pids,
                        "adapter_listener_reachable": listener_reachable,
                        "server_sam_listener_reachable": server_sam_reachable,
                        "client_sam_listener_reachable": client_sam_reachable,
                        "routers_preserved": True,
                        "contains_secrets": False,
                    },
                )
                fault_state = "active"
                fault_kind = "server-fronts"
            elif (
                fault_state == "active"
                and fault_kind == "client-router"
                and recover_request.exists()
            ):
                consume_control(recover_request, "recover-client-router=1\n")
                replacement = subprocess.Popen(
                    router_command(
                        binary,
                        source,
                        root / "client-router",
                        arguments.client_sam,
                        arguments.client_port,
                    ),
                    stdout=router_logs["client"],
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                processes.append(replacement)
                routers[1] = replacement
                wait_for(
                    lambda: replacement.poll() is not None
                    or port_open(*arguments.client_sam),
                    arguments.startup_timeout,
                    "replacement client router SAM listener",
                )
                require(
                    replacement.poll() is None and port_open(*arguments.client_sam),
                    "replacement client router exited",
                )
                wait_for(
                    lambda: audit_has_session(
                        root / "adapter.audit.jsonl", "ready", 2
                    ),
                    arguments.startup_timeout,
                    "adapter generation-two SAM recovery",
                )
                require(
                    port_open(*arguments.listen),
                    "guest-facing adapter listener disappeared during recovery",
                )
                recovered_client_socket_attribution = wait_for_router_tcp_inventory(
                    "client",
                    replacement,
                    arguments.client_sam,
                    arguments.startup_timeout,
                )
                router_restart_count = 1
                fault_summary = {
                    "kind": "client-router-process-restart",
                    "old_client_router_pid": old_client_pid,
                    "new_client_router_pid": replacement.pid,
                    "process_replaced": replacement.pid != old_client_pid,
                    "router_datadir_preserved": True,
                    "adapter_listener_reachable_while_sam_down": True,
                    "client_sam_listener_absent_during_fault": True,
                    "adapter_generation_one_lost": True,
                    "adapter_generation_two_ready": True,
                    "fault_hold_ns": time.monotonic_ns() - fault_started_ns,
                    "contains_secrets": False,
                }
                write_new(
                    root / "fault-recovered.json",
                    {"schema": SCHEMA, "status": "fault-recovered", **fault_summary},
                )
                fault_recovered_ns = time.monotonic_ns()
                fault_state = "recovered"
            elif (
                fault_state == "active"
                and fault_kind == "server-fronts"
                and front_recover_request.exists()
            ):
                consume_control(front_recover_request, "recover-server-fronts=1\n")
                new_front_pids: list[int] = []
                replacements: list[subprocess.Popen[str]] = []
                for index in range(1, 4):
                    forward_stderr = (root / f"forward-restart-{index}.stderr").open(
                        "w", encoding="utf-8"
                    )
                    logs.append(forward_stderr)
                    audit_path = root / f"forward-restart-{index}.audit.jsonl"
                    replacement = subprocess.Popen(
                        [
                            sys.executable,
                            str(Path(__file__).with_name("run-i2p-sam-forward.py")),
                            "--sam",
                            f"{arguments.server_sam[0]}:{arguments.server_sam[1]}",
                            "--target",
                            f"127.0.0.1:{arguments.egress_port_base + index - 1}",
                            "--destination-key",
                            str(root / f"service-{index}.destination"),
                            "--audit",
                            str(audit_path),
                            "--startup-timeout",
                            str(arguments.startup_timeout),
                            "--command-timeout",
                            str(arguments.command_timeout),
                        ],
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=forward_stderr,
                        start_new_session=True,
                    )
                    processes.append(replacement)
                    replacements.append(replacement)
                    returned_destination = read_ready(
                        replacement,
                        arguments.startup_timeout,
                        f"replacement service front {index}",
                    )
                    require(
                        returned_destination == destinations[index - 1],
                        f"service front {index} Destination changed on restart",
                    )
                    require(
                        replacement.pid not in old_front_pids
                        and replacement.pid not in new_front_pids,
                        "server-front replacement PID was reused",
                    )
                    new_front_pids.append(replacement.pid)
                    restarted_forward_audits.append(audit_path)
                forward_processes = replacements
                fault_recovered_ns = time.monotonic_ns()
                server_front_restart_count = 1
                server_front_fault = {
                    "kind": "server-front-process-restart",
                    "old_server_front_pids": old_front_pids,
                    "new_server_front_pids": new_front_pids,
                    "processes_replaced": all(
                        new not in old_front_pids for new in new_front_pids
                    ),
                    "destination_keys_preserved": True,
                    "adapter_listener_preserved": port_open(*arguments.listen),
                    "server_sam_listener_preserved": port_open(*arguments.server_sam),
                    "client_sam_listener_preserved": port_open(*arguments.client_sam),
                    "routers_preserved": all(router.poll() is None for router in routers),
                    "fault_started_ns": fault_started_ns,
                    "fault_recovered_ns": fault_recovered_ns,
                    "fault_hold_ns": fault_recovered_ns - fault_started_ns,
                    "contains_secrets": False,
                }
                require(
                    server_front_fault["processes_replaced"] is True
                    and server_front_fault["adapter_listener_preserved"] is True
                    and server_front_fault["server_sam_listener_preserved"] is True
                    and server_front_fault["client_sam_listener_preserved"] is True
                    and server_front_fault["routers_preserved"] is True,
                    "server-front recovery did not preserve the surrounding topology",
                )
                write_new(
                    root / "front-fault-recovered.json",
                    {
                        "schema": SCHEMA,
                        "status": "fault-recovered",
                        **server_front_fault,
                    },
                )
                fault_state = "recovered"
            time.sleep(0.2)
        require(fault_state != "active", "I2P topology fault was not recovered")
    finally:
        terminate(processes)
        for log in logs:
            try:
                log.close()
            except OSError:
                pass

    validate_adapter_audit(
        root / "adapter.audit.jsonl",
        destinations,
        fault_kind,
        fault_started_ns,
        fault_recovered_ns,
    )
    audits = [audit_summary(root / "adapter.audit.jsonl")]
    audits.extend(audit_summary(root / f"forward-{index}.audit.jsonl") for index in range(1, 4))
    audits.extend(audit_summary(path) for path in restarted_forward_audits)
    final = {
        "schema": SCHEMA,
        "status": "passed",
        "runtime_ns": time.monotonic_ns() - started_ns,
        "front_count": 3,
        "proxy_endpoint": f"{arguments.listen[0]}:{arguments.listen[1]}",
        "node_records_sha256": hashlib.sha256(
            ("\n".join(str(node["record"]) for node in nodes) + "\n").encode("ascii")
        ).hexdigest(),
        "destination_commitments": [
            hashlib.sha256(("iotox-i2p-b32-v1\0" + value).encode("ascii")).hexdigest()
            for value in destinations
        ],
        "router_binary_sha256": sha256(binary),
        "router_source_tree_sha256": source_digest,
        "router_source_file_count": source_files,
        "router_certificates_relative_path": "contrib/certificates",
        "router_certificates_tree_sha256": certificate_digest,
        "router_certificates_file_count": certificate_files,
        "router_reseed_signature_verification": True,
        "router_socket_attribution": {
            "initial": initial_socket_attribution,
            "recovered_client": (
                recovered_client_socket_attribution
                if router_restart_count == 1
                else None
            ),
        },
        "router_version": version,
        "client_router_restart_count": router_restart_count,
        "client_router_fault": fault_summary,
        "server_front_restart_count": server_front_restart_count,
        "server_front_fault": server_front_fault,
        "audits": audits,
        "contains_secrets": False,
    }
    write_new(root / "topology-final.json", final)
    print("final=" + json.dumps(final, sort_keys=True, separators=(",", ":")), flush=True)
    return 0


def self_test() -> None:
    first = parse_node(
        "205.185.115.131:53:3091C6BEB2A993F1C6300C16549FABA67098FF3D62C6D253828B531470B53D68"
    )
    require(first["target"] == "205.185.115.131:53", "node target drifted")
    require(endpoint("127.0.0.1:7656", loopback=True) == ("127.0.0.1", 7656), "endpoint drifted")
    for bad in (
        "192.0.2.1:53:" + "11" * 32,
        "205.185.115.131:0:" + "11" * 32,
        "205.185.115.131:53:11",
    ):
        try:
            parse_node(bad)
        except argparse.ArgumentTypeError:
            continue
        raise FrontError(f"accepted invalid node: {bad}")
    destinations = [character * 52 + ".b32.i2p" for character in "abc"]
    commitments = [
        hashlib.sha256(("iotox-i2p-b32-v1\0" + value).encode("ascii")).hexdigest()
        for value in destinations
    ]
    with tempfile.TemporaryDirectory(prefix="iotox-i2p-front-test.") as directory:
        audit = Path(directory) / "adapter.audit.jsonl"

        def connection_records(generation: int) -> list[dict[str, object]]:
            return [
                {
                    "event": "socks5-i2p-connect",
                    "generation": generation,
                    "outcome": "admitted",
                    "destination_sha256": commitment,
                }
                for commitment in commitments
            ]

        baseline = [
            {"event": "sam-session", "generation": 1, "outcome": "ready"},
            *connection_records(1),
            *connection_records(1),
        ]
        audit.write_text(
            "".join(json.dumps(record) + "\n" for record in baseline),
            encoding="ascii",
        )
        validate_adapter_audit(audit, destinations)
        restart = [
            {"event": "sam-session", "generation": 1, "outcome": "ready"},
            *connection_records(1),
            *connection_records(1),
            {
                "event": "sam-session",
                "generation": 1,
                "outcome": "lost",
            },
            *[
                {
                    "event": "socks5-i2p-connect",
                    "generation": 0,
                    "outcome": "denied-sam-unavailable",
                    "destination_sha256": commitments[index % 3],
                }
                for index in range(81)
            ],
            {"event": "sam-session", "generation": 2, "outcome": "ready"},
            *connection_records(2)[:2],
            *connection_records(2)[:2],
        ]
        audit.write_text(
            "".join(json.dumps(record) + "\n" for record in restart),
            encoding="ascii",
        )
        validate_adapter_audit(audit, destinations, "client-router")
        server_front_restart = [
            {"event": "sam-session", "generation": 1, "outcome": "ready"},
            *[
                {**record, "monotonic_ns": 50}
                for record in connection_records(1)
            ],
            *[
                {
                    "event": "socks5-i2p-connect",
                    "generation": 1,
                    "outcome": "denied-stream",
                    "destination_sha256": commitments[index % 3],
                    "monotonic_ns": 150,
                }
                for index in range(8)
            ],
            *[
                {**record, "monotonic_ns": 250}
                for record in connection_records(1)[:2]
            ],
            *[
                {**record, "monotonic_ns": 300}
                for record in connection_records(1)[:2]
            ],
        ]
        audit.write_text(
            "".join(json.dumps(record) + "\n" for record in server_front_restart),
            encoding="ascii",
        )
        validate_adapter_audit(
            audit, destinations, "server-fronts", 100, 200
        )
    print("I2P Tox fronts self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path)
    parser.add_argument("--router-binary", type=Path)
    parser.add_argument("--router-source", type=Path)
    parser.add_argument("--socat", type=Path)
    parser.add_argument("--listen", type=endpoint)
    parser.add_argument("--server-sam", type=lambda value: endpoint(value, loopback=True))
    parser.add_argument("--client-sam", type=lambda value: endpoint(value, loopback=True))
    parser.add_argument("--server-port", type=int, default=31211)
    parser.add_argument("--client-port", type=int, default=31212)
    parser.add_argument("--egress-port-base", type=int, default=39401)
    parser.add_argument("--node", type=parse_node, action="append", default=[])
    parser.add_argument("--startup-timeout", type=float, default=300.0)
    parser.add_argument("--command-timeout", type=float, default=180.0)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
        return 0
    required = (
        arguments.work_root,
        arguments.router_binary,
        arguments.router_source,
        arguments.socat,
        arguments.listen,
        arguments.server_sam,
        arguments.client_sam,
    )
    require(all(value is not None for value in required), "all live topology paths/endpoints are required")
    require(1 <= arguments.server_port <= 65535, "server port is out of range")
    require(1 <= arguments.client_port <= 65535, "client port is out of range")
    require(1 <= arguments.egress_port_base <= 65533, "egress port base is out of range")
    require(30.0 <= arguments.startup_timeout <= 900.0, "startup timeout is out of range")
    require(10.0 <= arguments.command_timeout <= 600.0, "command timeout is out of range")
    return run(arguments)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FrontError, OSError, subprocess.SubprocessError) as error:
        print(f"I2P Tox fronts failed: {error}", file=sys.stderr)
        raise SystemExit(1)
