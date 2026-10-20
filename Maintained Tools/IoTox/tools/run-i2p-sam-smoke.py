#!/usr/bin/env python3
"""Run a bounded real-I2P stream smoke through two existing i2pd routers."""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import importlib.util
import ipaddress
import json
import os
import re
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path


ADAPTER_PATH = Path(__file__).with_name("run-i2p-sam-socks.py")
SPEC = importlib.util.spec_from_file_location("iotox_i2p_sam_socks", ADAPTER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load the I2P SAM SOCKS adapter")
ADAPTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ADAPTER
SPEC.loader.exec_module(ADAPTER)

SCHEMA = "iotox.i2p-sam-two-router-smoke.v1"
LOGICAL_TARGET = ("192.0.2.17", 33445)
STREAM_COUNT = 4
PAYLOAD_BYTES = 65536
WARMUP_BYTES = 4096
class SmokeError(RuntimeError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise SmokeError(detail)


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            value.update(block)
    return value.hexdigest()


def digest_source_tree(root: Path) -> tuple[str, int]:
    value = hashlib.sha256(b"iotox-i2pd-source-tree-v1\0")
    count = 0
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        if path.is_symlink():
            target_text = os.readlink(path)
            target = target_text.encode("utf-8")
            require(not os.path.isabs(target_text)
                    and path.resolve().is_relative_to(root),
                    "router source tree contains an escaping symbolic link")
            value.update(len(relative).to_bytes(8, "big"))
            value.update(relative)
            value.update(b"L")
            value.update(len(target).to_bytes(8, "big"))
            value.update(target)
            count += 1
            continue
        if path.is_dir():
            continue
        require(path.is_file(), "router source tree contains a non-regular entry")
        content = path.read_bytes()
        value.update(len(relative).to_bytes(8, "big"))
        value.update(relative)
        value.update(b"F")
        value.update((path.stat().st_mode & 0o111 != 0).to_bytes(1, "big"))
        value.update(len(content).to_bytes(8, "big"))
        value.update(content)
        count += 1
    require(count > 0, "router source tree is empty")
    return value.hexdigest(), count


def set_commitment(label: str, values: set[str]) -> str:
    require(bool(values), f"cannot commit empty {label} set")
    canonical = label.encode("ascii") + b"\0"
    canonical += "\n".join(sorted(values)).encode("ascii") + b"\n"
    return digest_bytes(canonical)


def decode_i2p_base64(value: str) -> bytes:
    require(
        bool(value)
        and all(
            character.isalnum() or character in "-~="
            for character in value
        ),
        "SAM returned a noncanonical I2P base64 Destination",
    )
    translated = value.replace("-", "+").replace("~", "/")
    translated += "=" * ((-len(translated)) % 4)
    try:
        decoded = base64.b64decode(translated, validate=True)
    except (ValueError, binascii.Error) as error:
        raise SmokeError("SAM returned invalid I2P base64") from error
    require(len(decoded) >= 387, "SAM public Destination is too short")
    return decoded


def destination_b32(public_destination: str) -> str:
    identity = hashlib.sha256(decode_i2p_base64(public_destination)).digest()
    label = base64.b32encode(identity).decode("ascii").rstrip("=").lower()
    require(len(label) == 52, "I2P Destination hash did not form traditional b32")
    return label + ".b32.i2p"


def receive_exact(stream: socket.socket, size: int) -> bytes:
    output = bytearray()
    while len(output) < size:
        block = stream.recv(size - len(output))
        require(bool(block), "stream closed before the exact record completed")
        output.extend(block)
    return bytes(output)


def create_server_session(
    endpoint: tuple[str, int], session_id: str, timeout: float
) -> tuple[socket.socket, str, int]:
    started = time.monotonic_ns()
    control = ADAPTER.open_numeric(endpoint, 10.0)
    try:
        ADAPTER.negotiate(control)
        control.settimeout(timeout)
        control.sendall(
            (
                f"SESSION CREATE ID={session_id} STYLE=STREAM "
                "DESTINATION=TRANSIENT SIGNATURE_TYPE=7 "
                "i2cp.leaseSetType=1 i2cp.leaseSetEncType=4 "
                "inbound.quantity=2 outbound.quantity=2\n"
            ).encode("ascii")
        )
        created = ADAPTER.parse_status(
            ADAPTER.receive_line(control), "SESSION", "STATUS"
        )
        require(
            created.get("RESULT") == "OK" and bool(created.get("DESTINATION")),
            "server router refused the transient SAM session",
        )
        control.sendall(b"NAMING LOOKUP NAME=ME\n")
        named = ADAPTER.parse_status(
            ADAPTER.receive_line(control), "NAMING", "REPLY"
        )
        require(
            named.get("RESULT") == "OK"
            and named.get("NAME") == "ME"
            and bool(named.get("VALUE")),
            "server router did not disclose its public session Destination",
        )
        return control, destination_b32(named["VALUE"]), time.monotonic_ns() - started
    except Exception:
        control.close()
        raise


def echo_accepted(
    stream: socket.socket,
    remote_destination: str,
    expected_payload_sha256: frozenset[str],
    expected_payload_bytes: int,
    result: dict[str, object],
) -> None:
    try:
        size = int.from_bytes(receive_exact(stream, 4), "big")
        require(size == expected_payload_bytes, "I2P stream payload length drifted")
        payload = receive_exact(stream, size)
        payload_sha256 = digest_bytes(payload)
        require(payload_sha256 in expected_payload_sha256,
                "I2P stream carried an unknown payload")
        stream.sendall(size.to_bytes(4, "big") + payload)
        result.update(
            {
                "remote_destination_sha256": digest_bytes(
                    ("iotox-i2p-remote-destination-v1\0" + remote_destination).encode(
                        "ascii"
                    )
                ),
                "payload_sha256": payload_sha256,
                "status": "passed",
            }
        )
    except Exception as error:  # noqa: BLE001 - return thread failure to caller
        result.update({"status": "failed", "error": str(error)})
    finally:
        stream.close()


def dispatch_accepts(
    endpoint: tuple[str, int],
    session_id: str,
    expected_payload_sha256: frozenset[str],
    expected_payload_bytes: int,
    timeout: float,
    ready: threading.Event,
    results: list[dict[str, object]],
    errors: list[str],
) -> None:
    workers: list[threading.Thread] = []
    try:
        for index in range(len(results)):
            stream = ADAPTER.open_numeric(endpoint, 10.0)
            try:
                ADAPTER.negotiate(stream)
                stream.settimeout(timeout)
                stream.sendall(
                    f"STREAM ACCEPT ID={session_id} SILENT=false\n".encode("ascii")
                )
                status = ADAPTER.parse_status(
                    ADAPTER.receive_line(stream), "STREAM", "STATUS"
                )
                require(status.get("RESULT") == "OK", "server SAM ACCEPT was refused")
                if index == 0:
                    ready.set()
                remote_destination = ADAPTER.receive_line(stream)
                require(bool(remote_destination),
                        "server SAM omitted the remote Destination")
            except Exception:
                stream.close()
                raise
            worker = threading.Thread(
                target=echo_accepted,
                args=(
                    stream,
                    remote_destination,
                    expected_payload_sha256,
                    expected_payload_bytes,
                    results[index],
                ),
            )
            workers.append(worker)
            worker.start()
        for worker in workers:
            worker.join(timeout + 30.0)
        require(all(not worker.is_alive() for worker in workers),
                "accepted I2P stream workers did not quiesce")
    except Exception as error:  # noqa: BLE001 - return thread failure to caller
        errors.append(str(error))
    finally:
        ready.set()


def open_socks_stream(
    proxy: tuple[str, int], target: tuple[str, int], timeout: float
) -> socket.socket:
    stream = ADAPTER.open_numeric(proxy, 10.0)
    try:
        stream.settimeout(timeout)
        stream.sendall(b"\x05\x01\x00")
        require(receive_exact(stream, 2) == b"\x05\x00", "SOCKS greeting failed")
        packed = socket.inet_pton(socket.AF_INET, target[0])
        stream.sendall(
            b"\x05\x01\x00\x01" + packed + target[1].to_bytes(2, "big")
        )
        reply = receive_exact(stream, 10)
        require(reply[:2] == b"\x05\x00", f"SOCKS I2P CONNECT failed: {reply[1]}")
        return stream
    except Exception:
        stream.close()
        raise


def payload(index: int) -> bytes:
    seed = hashlib.sha256(f"iotox-i2p-smoke-{index}".encode("ascii")).digest()
    return (seed * ((PAYLOAD_BYTES + len(seed) - 1) // len(seed)))[:PAYLOAD_BYTES]


def warmup_payload() -> bytes:
    seed = hashlib.sha256(b"iotox-i2p-smoke-warmup").digest()
    return (seed * ((WARMUP_BYTES + len(seed) - 1) // len(seed)))[:WARMUP_BYTES]


def run_warmup(
    proxy: tuple[str, int], timeout: float
) -> dict[str, object]:
    started = time.monotonic_ns()
    deadline = time.monotonic() + timeout
    attempts = 0
    value = warmup_payload()
    while True:
        attempts += 1
        remaining = deadline - time.monotonic()
        require(remaining > 1.0, "I2P route did not become reachable during warm-up")
        try:
            stream = open_socks_stream(
                proxy, LOGICAL_TARGET, min(65.0, remaining)
            )
        except SmokeError as error:
            require(str(error).startswith("SOCKS I2P CONNECT failed:"),
                    f"warm-up failed before I2P discovery: {error}")
            remaining = deadline - time.monotonic()
            require(remaining > 2.0, "I2P route did not become reachable during warm-up")
            time.sleep(min(2.0, remaining - 1.0))
            continue
        with stream:
            stream.sendall(len(value).to_bytes(4, "big") + value)
            size = int.from_bytes(receive_exact(stream, 4), "big")
            require(size == len(value), "warm-up echo length drifted")
            echoed = receive_exact(stream, size)
            require(echoed == value, "warm-up echo changed bytes")
        return {
            "attempt_count": attempts,
            "latency_ns": time.monotonic_ns() - started,
            "payload_bytes": len(value),
            "payload_sha256": digest_bytes(value),
            "status": "passed",
        }


def run_client(
    proxy: tuple[str, int],
    index: int,
    timeout: float,
    barrier: threading.Barrier,
    result: dict[str, object],
) -> None:
    value = payload(index)
    try:
        barrier.wait(timeout=10.0)
        started = time.monotonic_ns()
        with open_socks_stream(proxy, LOGICAL_TARGET, timeout) as stream:
            stream.sendall(len(value).to_bytes(4, "big") + value)
            size = int.from_bytes(receive_exact(stream, 4), "big")
            require(size == len(value), "echoed I2P payload length drifted")
            echoed = receive_exact(stream, size)
            require(echoed == value, "I2P echo changed bytes")
        result.update(
            {
                "_started_ns": started,
                "latency_ns": time.monotonic_ns() - started,
                "payload_sha256": digest_bytes(value),
                "status": "passed",
            }
        )
    except Exception as error:  # noqa: BLE001 - return thread failure to caller
        result.update({"status": "failed", "error": str(error)})


def process_start_time(pid: int) -> int:
    record = Path(f"/proc/{pid}/stat").read_text(encoding="ascii")
    closing = record.rfind(")")
    require(closing > 0, f"cannot parse process stat for PID {pid}")
    fields = record[closing + 2 :].split()
    require(len(fields) > 19 and fields[19].isdecimal(), "process start time is invalid")
    return int(fields[19])


def owned_socket_inodes(pid: int) -> set[str]:
    output: set[str] = set()
    for descriptor in Path(f"/proc/{pid}/fd").iterdir():
        try:
            target = os.readlink(descriptor)
        except OSError:
            continue
        match = re.fullmatch(r"socket:\[([0-9]+)\]", target)
        if match:
            output.add(match.group(1))
    require(bool(output), f"router PID {pid} owns no sockets")
    return output


def decode_ipv4(hexadecimal: str) -> str:
    return str(ipaddress.ip_address(bytes.fromhex(hexadecimal)[::-1]))


def tcp_inventory(pid: int, sam_port: int) -> dict[str, object]:
    owned = owned_socket_inodes(pid)
    public_remotes: set[str] = set()
    sam_listener = False
    for path in (Path("/proc/net/tcp"), Path("/proc/net/tcp6")):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="ascii").splitlines()[1:]:
            fields = line.split()
            if len(fields) < 10 or fields[9] not in owned:
                continue
            local_hex, local_port_hex = fields[1].split(":")
            remote_hex, remote_port_hex = fields[2].split(":")
            local_port = int(local_port_hex, 16)
            remote_port = int(remote_port_hex, 16)
            if len(local_hex) == 8:
                local_address = decode_ipv4(local_hex)
                remote_address = decode_ipv4(remote_hex)
            else:
                # Only exact loopback listener attribution needs an address;
                # public IPv6 remotes remain content-free commitments below.
                local_address = "ipv6"
                remote_address = "ipv6:" + remote_hex.lower()
            if fields[3] == "0A" and local_port == sam_port:
                sam_listener = local_address == "127.0.0.1"
            if remote_port != 0:
                try:
                    is_public = ipaddress.ip_address(remote_address).is_global
                except ValueError:
                    is_public = True
                if is_public:
                    public_remotes.add(f"{remote_address}:{remote_port}")
    require(sam_listener, f"router PID {pid} does not own its loopback SAM listener")
    require(public_remotes, f"router PID {pid} owns no public TCP connection")
    return {
        "public_tcp_remote_count": len(public_remotes),
        "public_tcp_remote_set_sha256": set_commitment(
            "iotox-i2pd-public-tcp-remotes-v1", public_remotes
        ),
        "sam_listener_owned": True,
    }


def router_record(
    pid: int, binary: Path, sam_endpoint: tuple[str, int]
) -> dict[str, object]:
    require(pid > 1 and Path(f"/proc/{pid}").is_dir(), "router PID is absent")
    executable = Path(f"/proc/{pid}/exe").resolve()
    require(executable == binary, f"router PID {pid} executable identity drifted")
    cmdline = Path(f"/proc/{pid}/cmdline").read_bytes()
    require(
        f"--sam.port={sam_endpoint[1]}".encode("ascii") in cmdline.split(b"\0")
        and b"--sam.address=127.0.0.1" in cmdline.split(b"\0"),
        f"router PID {pid} command line lacks exact SAM policy",
    )
    return {
        "pid": pid,
        "process_start_time": process_start_time(pid),
        "command_line_sha256": digest_bytes(cmdline),
        **tcp_inventory(pid, sam_endpoint[1]),
    }


def git_clean_commit() -> str:
    root = Path(__file__).resolve().parent.parent
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=10.0,
        check=True,
    )
    require(not status.stdout, "actual-I2P smoke requires a clean source tree")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=10.0,
        check=True,
    ).stdout.strip()
    require(re.fullmatch(r"[0-9a-f]{40}", commit) is not None, "git commit is invalid")
    return commit


def parse_pid(text: str) -> int:
    if not text.isascii() or not text.isdecimal() or int(text) <= 1:
        raise argparse.ArgumentTypeError("router PID must be greater than one")
    return int(text)


def self_test() -> None:
    raw = b"x" * 387
    encoded = base64.b64encode(raw).decode("ascii").replace("+", "-").replace("/", "~")
    expected = base64.b32encode(hashlib.sha256(raw).digest()).decode("ascii").rstrip("=").lower()
    require(destination_b32(encoded) == expected + ".b32.i2p", "b32 derivation drifted")
    require(len(payload(0)) == PAYLOAD_BYTES and payload(0) != payload(1),
            "payload generation drifted")
    require(len(warmup_payload()) == WARMUP_BYTES,
            "warm-up payload generation drifted")
    print("actual-I2P SAM smoke self-test: PASS")


def write_new(path: Path, rendered: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        data = rendered.encode("utf-8")
        with os.fdopen(descriptor, "wb", closefd=False) as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
    finally:
        os.close(descriptor)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-sam", type=ADAPTER.BASE.parse_endpoint)
    parser.add_argument("--client-sam", type=ADAPTER.BASE.parse_endpoint)
    parser.add_argument("--server-router-pid", type=parse_pid)
    parser.add_argument("--client-router-pid", type=parse_pid)
    parser.add_argument("--router-binary", type=Path)
    parser.add_argument("--router-source", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=ADAPTER.bounded_seconds, default=300.0)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        require(
            all(
                value is None
                for value in (
                    arguments.server_sam,
                    arguments.client_sam,
                    arguments.server_router_pid,
                    arguments.client_router_pid,
                    arguments.router_binary,
                    arguments.router_source,
                    arguments.output,
                )
            ),
            "--self-test accepts no live arguments",
        )
        self_test()
        return 0
    require(
        arguments.server_sam is not None
        and arguments.client_sam is not None
        and arguments.server_router_pid is not None
        and arguments.client_router_pid is not None
        and arguments.router_binary is not None
        and arguments.router_source is not None
        and arguments.output is not None,
        "all live actual-I2P arguments are required",
    )
    require(
        arguments.server_sam != arguments.client_sam
        and arguments.server_router_pid != arguments.client_router_pid,
        "actual-I2P smoke requires distinct router processes and SAM endpoints",
    )
    require(
        ipaddress.ip_address(arguments.server_sam[0]).is_loopback
        and ipaddress.ip_address(arguments.client_sam[0]).is_loopback,
        "SAM endpoints must be loopback",
    )
    binary = arguments.router_binary.resolve()
    require(binary.is_file() and not binary.is_symlink(), "router binary is invalid")
    router_source = arguments.router_source.resolve()
    require(router_source.is_dir() and not router_source.is_symlink(),
            "router source tree is invalid")
    router_source_sha256, router_source_file_count = digest_source_tree(router_source)
    source_commit = git_clean_commit()
    version = subprocess.run(
        [str(binary), "--version"],
        text=True,
        capture_output=True,
        timeout=10.0,
        check=True,
    ).stdout.strip()
    require(version.startswith("i2pd version "), "router version output is invalid")
    server_router = router_record(
        arguments.server_router_pid, binary, arguments.server_sam
    )
    client_router = router_record(
        arguments.client_router_pid, binary, arguments.client_sam
    )

    server_id = "iotox_server_" + os.urandom(12).hex()
    control, b32_destination, server_setup_ns = create_server_session(
        arguments.server_sam, server_id, arguments.timeout
    )
    adapter: subprocess.Popen[str] | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="iotox-actual-i2p-") as raw_root:
            root = Path(raw_root)
            audit = root / "adapter-audit.jsonl"
            adapter = subprocess.Popen(
                [
                    sys.executable,
                    str(ADAPTER_PATH),
                    "--listen", "127.0.0.1:0",
                    "--sam", f"{arguments.client_sam[0]}:{arguments.client_sam[1]}",
                    "--map",
                    f"{LOGICAL_TARGET[0]}:{LOGICAL_TARGET[1]}={b32_destination}",
                    "--audit", str(audit),
                    "--startup-timeout", str(arguments.timeout),
                    "--command-timeout", str(min(arguments.timeout, 60.0)),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            require(adapter.stdout is not None, "adapter stdout is absent")
            ready = adapter.stdout.readline().strip()
            require(ready.startswith("ready=127.0.0.1:"), f"adapter not ready: {ready}")
            proxy = ("127.0.0.1", int(ready.rsplit(":", 1)[1]))

            warm_server_results = [{}]
            warm_ready = threading.Event()
            warm_errors: list[str] = []
            warm_dispatcher = threading.Thread(
                target=dispatch_accepts,
                args=(
                    arguments.server_sam,
                    server_id,
                    frozenset({digest_bytes(warmup_payload())}),
                    WARMUP_BYTES,
                    arguments.timeout,
                    warm_ready,
                    warm_server_results,
                    warm_errors,
                ),
            )
            warm_dispatcher.start()
            require(warm_ready.wait(15.0), "warm-up SAM accept did not become ready")
            require(not warm_errors, f"warm-up SAM accept failed: {warm_errors}")
            warmup = run_warmup(proxy, arguments.timeout)
            warm_dispatcher.join(arguments.timeout + 30.0)
            require(not warm_dispatcher.is_alive() and not warm_errors,
                    f"warm-up SAM dispatch did not quiesce: {warm_errors}")
            require(warm_server_results[0].get("status") == "passed"
                    and warm_server_results[0].get("payload_sha256")
                    == warmup["payload_sha256"],
                    f"warm-up server evidence failed: {warm_server_results}")

            server_results = [{} for _ in range(STREAM_COUNT)]
            client_results = [{} for _ in range(STREAM_COUNT)]
            expected_payload_hashes = frozenset(
                digest_bytes(payload(index)) for index in range(STREAM_COUNT)
            )
            accept_ready = threading.Event()
            accept_errors: list[str] = []
            dispatcher = threading.Thread(
                target=dispatch_accepts,
                args=(
                    arguments.server_sam,
                    server_id,
                    expected_payload_hashes,
                    PAYLOAD_BYTES,
                    arguments.timeout,
                    accept_ready,
                    server_results,
                    accept_errors,
                ),
            )
            dispatcher.start()
            require(accept_ready.wait(15.0), "server SAM accept did not become ready")
            require(not accept_errors, f"server SAM accept failed: {accept_errors}")
            start_barrier = threading.Barrier(STREAM_COUNT + 1)
            clients = [
                threading.Thread(
                    target=run_client,
                    args=(
                        proxy,
                        index,
                        arguments.timeout,
                        start_barrier,
                        client_results[index],
                    ),
                )
                for index in range(STREAM_COUNT)
            ]
            for client in clients:
                client.start()
            start_barrier.wait(timeout=10.0)
            for client in clients:
                client.join(arguments.timeout + 30.0)
            dispatcher.join(arguments.timeout + 30.0)
            require(
                all(not thread.is_alive() for thread in clients)
                and not dispatcher.is_alive(),
                "actual-I2P stream threads did not quiesce",
            )
            require(not accept_errors, f"server SAM accept failed: {accept_errors}")
            require(
                all(result.get("status") == "passed" for result in client_results)
                and all(result.get("status") == "passed" for result in server_results),
                f"actual-I2P stream failed: clients={client_results} servers={server_results}",
            )
            started_values = [int(result.pop("_started_ns")) for result in client_results]
            start_floor = min(started_values)
            start_span_ns = max(started_values) - start_floor
            require(start_span_ns <= 50_000_000,
                    "actual-I2P client release exceeded 50 milliseconds")
            for result, started_ns in zip(client_results, started_values):
                result["start_offset_ns"] = started_ns - start_floor
            adapter.send_signal(signal.SIGTERM)
            adapter_output, adapter_errors = adapter.communicate(timeout=10.0)
            require(adapter.returncode == 0, f"adapter failed: {adapter_errors}")
            audit_bytes = audit.read_bytes()
            require(b32_destination.encode("ascii") not in audit_bytes,
                    "adapter audit disclosed the b32 Destination")
            audit_records = [
                json.loads(line)
                for line in audit_bytes.decode("ascii").splitlines()
            ]
            require(
                sum(record.get("outcome") == "ready" for record in audit_records) == 1
                and sum(record.get("outcome") == "admitted" for record in audit_records)
                == STREAM_COUNT + 1
                and all(
                    record.get("outcome") in {"ready", "admitted", "denied-stream"}
                    for record in audit_records
                ),
                "adapter audit counters drifted",
            )
            denied_streams = sum(
                record.get("outcome") == "denied-stream" for record in audit_records
            )
            require(
                f"admitted={STREAM_COUNT + 1} denied={denied_streams}" in adapter_output,
                "adapter summary counters drifted",
            )
            payload_hashes = {
                str(result["payload_sha256"]) for result in client_results
            }
            server_payload_hashes = {
                str(result["payload_sha256"]) for result in server_results
            }
            remote_hashes = {
                str(result["remote_destination_sha256"])
                for result in server_results
            }
            require(len(payload_hashes) == STREAM_COUNT,
                    "actual-I2P payload identities are not distinct")
            require(payload_hashes == server_payload_hashes == expected_payload_hashes,
                    "client and server payload identities differ")
            receipt = {
                "schema": SCHEMA,
                "status": "passed",
                "contains_secrets": False,
                "actual_i2p": True,
                "source_commit": source_commit,
                "router_version": version,
                "router_binary_sha256": digest_file(binary),
                "router_source_tree_sha256": router_source_sha256,
                "router_source_file_count": router_source_file_count,
                "router_process_count": 2,
                "server_router": server_router,
                "client_router": client_router,
                "server_sam_endpoint_sha256": digest_bytes(
                    f"{arguments.server_sam[0]}:{arguments.server_sam[1]}".encode("ascii")
                ),
                "client_sam_endpoint_sha256": digest_bytes(
                    f"{arguments.client_sam[0]}:{arguments.client_sam[1]}".encode("ascii")
                ),
                "server_session_setup_ns": server_setup_ns,
                "server_destination_sha256": digest_bytes(
                    ("iotox-i2p-b32-v1\0" + b32_destination).encode("ascii")
                ),
                "adapter_sha256": digest_file(ADAPTER_PATH),
                "adapter_audit_sha256": digest_bytes(audit_bytes),
                "adapter_audit_records": audit_records,
                "adapter_session_generation": 1,
                "warmup": warmup,
                "warmup_server": warm_server_results[0],
                "discovery_denied_stream_count": denied_streams,
                "stream_count": STREAM_COUNT,
                "payload_bytes_per_stream": PAYLOAD_BYTES,
                "payload_total_bytes": STREAM_COUNT * PAYLOAD_BYTES,
                "payload_set_sha256": set_commitment(
                    "iotox-i2p-smoke-payload-set-v1", payload_hashes
                ),
                "remote_destination_count": len(remote_hashes),
                "remote_destination_set_sha256": set_commitment(
                    "iotox-i2p-smoke-remote-set-v1", remote_hashes
                ),
                "stream_latency_ns": [
                    int(result["latency_ns"]) for result in client_results
                ],
                "client_start_span_ns": start_span_ns,
                "client_streams": client_results,
                "server_streams": server_results,
            }
            rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
            write_new(arguments.output, rendered)
            print(rendered, end="")
    finally:
        control.close()
        if adapter is not None and adapter.poll() is None:
            adapter.terminate()
            adapter.communicate(timeout=10.0)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, SmokeError, subprocess.SubprocessError) as error:
        print(f"actual-I2P SAM smoke failed: {error}", file=sys.stderr)
        raise SystemExit(1)
