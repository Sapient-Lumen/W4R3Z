#!/usr/bin/env python3
"""Strictly verify a content-free two-router I2P SAM smoke receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


SCHEMA = "iotox.i2p-sam-two-router-smoke.v1"
TARGET = "192.0.2.17:33445"
STREAM_COUNT = 4
PAYLOAD_BYTES = 65536
WARMUP_BYTES = 4096
MAX_RECEIPT_BYTES = 128 * 1024
SHA256 = re.compile(r"[0-9a-f]{64}")
COMMIT = re.compile(r"[0-9a-f]{40}")
TOP_KEYS = {
    "actual_i2p",
    "adapter_audit_records",
    "adapter_audit_sha256",
    "adapter_session_generation",
    "adapter_sha256",
    "client_router",
    "client_sam_endpoint_sha256",
    "client_start_span_ns",
    "client_streams",
    "contains_secrets",
    "discovery_denied_stream_count",
    "payload_bytes_per_stream",
    "payload_set_sha256",
    "payload_total_bytes",
    "remote_destination_count",
    "remote_destination_set_sha256",
    "router_binary_sha256",
    "router_process_count",
    "router_source_file_count",
    "router_source_tree_sha256",
    "router_version",
    "schema",
    "server_destination_sha256",
    "server_router",
    "server_sam_endpoint_sha256",
    "server_session_setup_ns",
    "server_streams",
    "source_commit",
    "status",
    "stream_count",
    "stream_latency_ns",
    "warmup",
    "warmup_server",
}
ROUTER_KEYS = {
    "command_line_sha256",
    "pid",
    "process_start_time",
    "public_tcp_remote_count",
    "public_tcp_remote_set_sha256",
    "sam_listener_owned",
}


class VerifyError(RuntimeError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise VerifyError(detail)


def is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def require_integer(value: object, minimum: int, maximum: int, label: str) -> int:
    require(is_integer(value) and minimum <= value <= maximum, f"invalid {label}")
    return int(value)


def require_sha(value: object, label: str) -> str:
    require(isinstance(value, str) and SHA256.fullmatch(value) is not None,
            f"invalid {label}")
    return value


def require_keys(value: object, keys: set[str], label: str) -> dict[str, object]:
    require(isinstance(value, dict) and set(value) == keys,
            f"{label} fields drifted")
    return value


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for key, value in pairs:
        if key in output:
            raise VerifyError(f"duplicate JSON member: {key}")
        output[key] = value
    return output


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
    paths = sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix())
    for path in paths:
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


def payload(index: int) -> bytes:
    seed = hashlib.sha256(f"iotox-i2p-smoke-{index}".encode("ascii")).digest()
    return (seed * ((PAYLOAD_BYTES + len(seed) - 1) // len(seed)))[:PAYLOAD_BYTES]


def warmup_payload() -> bytes:
    seed = hashlib.sha256(b"iotox-i2p-smoke-warmup").digest()
    return (seed * ((WARMUP_BYTES + len(seed) - 1) // len(seed)))[:WARMUP_BYTES]


def git_blob(root: Path, commit: str, path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=root,
        capture_output=True,
        timeout=10.0,
        check=False,
    )
    require(result.returncode == 0, f"source commit lacks {path}")
    return result.stdout


def verify_router(value: object, label: str) -> dict[str, object]:
    router = require_keys(value, ROUTER_KEYS, label)
    require_sha(router["command_line_sha256"], f"{label} command line")
    require_sha(router["public_tcp_remote_set_sha256"], f"{label} remote set")
    require_integer(router["pid"], 2, 2**31 - 1, f"{label} PID")
    require_integer(router["process_start_time"], 1, 2**63 - 1,
                    f"{label} process start")
    require_integer(router["public_tcp_remote_count"], 1, 65535,
                    f"{label} public remote count")
    require(router["sam_listener_owned"] is True,
            f"{label} did not own its SAM listener")
    return router


def verify_receipt(
    path: Path,
    router_binary: Path | None = None,
    router_source: Path | None = None,
) -> dict[str, object]:
    require(path.exists() and path.is_file() and not path.is_symlink(),
            "receipt must be a regular non-symlink file")
    raw = path.read_bytes()
    require(0 < len(raw) <= MAX_RECEIPT_BYTES, "receipt size is invalid")
    require(b".b32.i2p" not in raw.lower() and b"DESTINATION=" not in raw,
            "receipt disclosed a raw I2P Destination")
    try:
        receipt = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise VerifyError("receipt is not strict UTF-8 JSON") from error
    receipt = require_keys(receipt, TOP_KEYS, "receipt")
    require(receipt["schema"] == SCHEMA and receipt["status"] == "passed",
            "receipt schema or status drifted")
    require(receipt["contains_secrets"] is False and receipt["actual_i2p"] is True,
            "receipt secrecy or actual-I2P classification drifted")

    commit = receipt["source_commit"]
    require(isinstance(commit, str) and COMMIT.fullmatch(commit) is not None,
            "source commit is invalid")
    root = Path(__file__).resolve().parent.parent
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=root,
        timeout=10.0,
        check=False,
    )
    require(ancestor.returncode == 0, "source commit is not retained in current history")
    require(digest_bytes(git_blob(root, commit, "tools/run-i2p-sam-socks.py"))
            == require_sha(receipt["adapter_sha256"], "adapter digest"),
            "source-commit adapter digest differs")
    require(bool(git_blob(root, commit, "tools/run-i2p-sam-smoke.py")),
            "source-commit runner is empty")

    require_sha(receipt["router_binary_sha256"], "router binary digest")
    require_sha(receipt["router_source_tree_sha256"], "router source digest")
    require_integer(receipt["router_source_file_count"], 1, 1_000_000,
                    "router source file count")
    require(isinstance(receipt["router_version"], str)
            and receipt["router_version"].splitlines()[0]
            == "i2pd version 2.60.0 (0.9.69)",
            "router version drifted")
    if router_binary is not None:
        binary = router_binary.resolve()
        require(binary.is_file() and digest_file(binary)
                == receipt["router_binary_sha256"],
                "supplied router binary differs")
    if router_source is not None:
        source = router_source.resolve()
        require(source.is_dir(), "supplied router source tree is invalid")
        source_digest, source_count = digest_source_tree(source)
        require(source_digest == receipt["router_source_tree_sha256"]
                and source_count == receipt["router_source_file_count"],
                "supplied router source tree differs")

    require(receipt["router_process_count"] == 2,
            "router process count drifted")
    server_router = verify_router(receipt["server_router"], "server router")
    client_router = verify_router(receipt["client_router"], "client router")
    require(server_router["pid"] != client_router["pid"]
            and server_router["process_start_time"] != client_router["process_start_time"]
            and server_router["command_line_sha256"]
            != client_router["command_line_sha256"],
            "router process identities are not distinct")
    require_sha(receipt["server_sam_endpoint_sha256"], "server SAM endpoint")
    require_sha(receipt["client_sam_endpoint_sha256"], "client SAM endpoint")
    require(receipt["server_sam_endpoint_sha256"]
            != receipt["client_sam_endpoint_sha256"],
            "SAM endpoint commitments are not distinct")
    require_integer(receipt["server_session_setup_ns"], 1, 600_000_000_000,
                    "server session setup duration")

    destination_sha = require_sha(
        receipt["server_destination_sha256"], "server Destination commitment"
    )
    audit = receipt["adapter_audit_records"]
    require(isinstance(audit, list) and audit, "adapter audit is absent")
    require_keys(
        audit[0], {"event", "generation", "monotonic_ns", "outcome"},
        "adapter ready record",
    )
    require(audit[0]["event"] == "sam-session"
            and audit[0]["outcome"] == "ready"
            and audit[0]["generation"] == 1,
            "adapter ready record drifted")
    previous_time = require_integer(
        audit[0]["monotonic_ns"], 1, 2**63 - 1, "adapter ready time"
    )
    route_outcomes: list[str] = []
    for index, item in enumerate(audit[1:], 1):
        record = require_keys(
            item,
            {"destination_sha256", "event", "generation", "monotonic_ns",
             "outcome", "target"},
            f"adapter route record {index}",
        )
        require(record["event"] == "socks5-i2p-connect"
                and record["generation"] == 1
                and record["target"] == TARGET
                and record["destination_sha256"] == destination_sha
                and record["outcome"] in {"admitted", "denied-stream"},
                f"adapter route record {index} drifted")
        current_time = require_integer(
            record["monotonic_ns"], previous_time + 1, 2**63 - 1,
            f"adapter route time {index}",
        )
        previous_time = current_time
        route_outcomes.append(str(record["outcome"]))
    denied = require_integer(receipt["discovery_denied_stream_count"], 0, 1000,
                             "discovery denial count")
    require(route_outcomes == ["denied-stream"] * denied + ["admitted"] * 5,
            "adapter discovery/admission ordering drifted")
    audit_bytes = b"".join(
        (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode(
            "ascii"
        )
        for record in audit
    )
    require(digest_bytes(audit_bytes)
            == require_sha(receipt["adapter_audit_sha256"], "adapter audit digest"),
            "adapter audit byte commitment differs")
    require(receipt["adapter_session_generation"] == 1,
            "adapter session generation drifted")

    expected_payloads = [digest_bytes(payload(index)) for index in range(STREAM_COUNT)]
    expected_set = set(expected_payloads)
    require(receipt["stream_count"] == STREAM_COUNT
            and receipt["payload_bytes_per_stream"] == PAYLOAD_BYTES
            and receipt["payload_total_bytes"] == STREAM_COUNT * PAYLOAD_BYTES,
            "measured payload dimensions drifted")
    require(receipt["payload_set_sha256"]
            == set_commitment("iotox-i2p-smoke-payload-set-v1", expected_set),
            "measured payload-set commitment differs")

    clients = receipt["client_streams"]
    require(isinstance(clients, list) and len(clients) == STREAM_COUNT,
            "client stream count drifted")
    latencies = receipt["stream_latency_ns"]
    require(isinstance(latencies, list) and len(latencies) == STREAM_COUNT,
            "stream latency list drifted")
    offsets: list[int] = []
    for index, item in enumerate(clients):
        stream = require_keys(
            item, {"latency_ns", "payload_sha256", "start_offset_ns", "status"},
            f"client stream {index}",
        )
        latency = require_integer(stream["latency_ns"], 1, 600_000_000_000,
                                  f"client latency {index}")
        offset = require_integer(stream["start_offset_ns"], 0, 50_000_000,
                                 f"client start offset {index}")
        require(stream["status"] == "passed"
                and stream["payload_sha256"] == expected_payloads[index]
                and latencies[index] == latency,
                f"client stream {index} evidence drifted")
        offsets.append(offset)
    start_span = require_integer(receipt["client_start_span_ns"], 0, 50_000_000,
                                 "client start span")
    require(min(offsets) == 0 and max(offsets) == start_span,
            "client start-span evidence differs")

    servers = receipt["server_streams"]
    require(isinstance(servers, list) and len(servers) == STREAM_COUNT,
            "server stream count drifted")
    server_payloads: set[str] = set()
    remote_hashes: set[str] = set()
    for index, item in enumerate(servers):
        stream = require_keys(
            item, {"payload_sha256", "remote_destination_sha256", "status"},
            f"server stream {index}",
        )
        payload_sha = require_sha(stream["payload_sha256"],
                                  f"server payload {index}")
        remote_sha = require_sha(stream["remote_destination_sha256"],
                                 f"server remote {index}")
        require(stream["status"] == "passed", f"server stream {index} failed")
        server_payloads.add(payload_sha)
        remote_hashes.add(remote_sha)
    require(server_payloads == expected_set, "server payload set differs")
    require(receipt["remote_destination_count"] == len(remote_hashes) == 1,
            "remote Destination count drifted")
    require(receipt["remote_destination_set_sha256"]
            == set_commitment("iotox-i2p-smoke-remote-set-v1", remote_hashes),
            "remote Destination-set commitment differs")

    warmup = require_keys(
        receipt["warmup"],
        {"attempt_count", "latency_ns", "payload_bytes", "payload_sha256", "status"},
        "warm-up",
    )
    warm_sha = digest_bytes(warmup_payload())
    require(warmup["status"] == "passed"
            and warmup["payload_bytes"] == WARMUP_BYTES
            and warmup["payload_sha256"] == warm_sha
            and warmup["attempt_count"] == denied + 1,
            "warm-up evidence drifted")
    require_integer(warmup["latency_ns"], 1, 600_000_000_000,
                    "warm-up latency")
    warm_server = require_keys(
        receipt["warmup_server"],
        {"payload_sha256", "remote_destination_sha256", "status"},
        "warm-up server",
    )
    require(warm_server["status"] == "passed"
            and warm_server["payload_sha256"] == warm_sha
            and warm_server["remote_destination_sha256"] in remote_hashes,
            "warm-up server evidence drifted")
    return receipt


def self_test() -> None:
    expected = {digest_bytes(payload(index)) for index in range(STREAM_COUNT)}
    require(set_commitment("iotox-i2p-smoke-payload-set-v1", expected)
            == "a6c211d9797990b8a24bd4508379343e0eaf41d9bba0e77150bb9305d6d5f7d4",
            "payload commitment self-test drifted")
    require(digest_bytes(warmup_payload())
            == "973f689d2b83cc01991a007a5390106b14fda8ce6a608a35ce460b455a2538b5",
            "warm-up commitment self-test drifted")
    try:
        json.loads('{"a":1,"a":2}', object_pairs_hook=unique_object)
    except VerifyError:
        pass
    else:
        raise VerifyError("duplicate JSON self-test was admitted")
    with tempfile.TemporaryDirectory(prefix="iotox-i2p-source-self-test-") as raw:
        root = Path(raw)
        (root / "a").write_bytes(b"a")
        (root / "link").symlink_to("a")
        first = digest_source_tree(root)
        (root / "a").write_bytes(b"b")
        second = digest_source_tree(root)
        require(first != second and first[1] == second[1] == 2,
                "source-tree commitment self-test drifted")
    print("I2P SAM smoke verifier self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", nargs="?", type=Path)
    parser.add_argument("--router-binary", type=Path)
    parser.add_argument("--router-source", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        require(arguments.receipt is None
                and arguments.router_binary is None
                and arguments.router_source is None,
                "--self-test accepts no receipt or router inputs")
        self_test()
        return 0
    require(arguments.receipt is not None, "receipt path is required")
    receipt = verify_receipt(
        arguments.receipt, arguments.router_binary, arguments.router_source
    )
    print(
        "I2P SAM smoke receipt: PASS "
        f"streams={receipt['stream_count']} "
        f"bytes={receipt['payload_total_bytes']} "
        f"discovery_denials={receipt['discovery_denied_stream_count']} "
        f"source_commit={receipt['source_commit']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, VerifyError, subprocess.SubprocessError) as error:
        print(f"I2P SAM smoke verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
