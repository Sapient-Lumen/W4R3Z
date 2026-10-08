#!/usr/bin/env python3
"""Two-process product proof for the production reconciliation endpoint.

Only shipped executables create or mutate AnonSync authority. The test builds two
combined deployments, publishes a nested local tree through the configured-folder
process, transfers evidence and payloads over mutual TLS, materializes missing
parent directories, repeats as a durable no-op, then authors a reverse-direction
edit and proves the same peer roles work symmetrically across fresh processes. A
fresh one-file share also proves a payload larger than the historical 64 MiB
complete-file/page ceiling continues by exact 4 MiB ranges across independent
client and server processes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import tempfile
import time
from typing import Any, NoReturn, Sequence


def fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def run_json(
    command: Sequence[str], *, label: str, timeout: float = 60.0
) -> dict[str, Any]:
    completed = subprocess.run(
        list(command), check=False, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, timeout=timeout,
    )
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        fail(
            f"{label} did not emit one JSON object: {error}\n"
            f"command: {' '.join(command)}\nstdout:\n{completed.stdout}"
            f"stderr:\n{completed.stderr}"
        )
    if not isinstance(value, dict):
        fail(f"{label} JSON is not an object")
    if completed.returncode != 0:
        fail(
            f"{label} failed with {completed.returncode}\n"
            f"command: {' '.join(command)}\nstdout:\n{completed.stdout}"
            f"stderr:\n{completed.stderr}"
        )
    if completed.stderr:
        fail(f"{label} wrote diagnostics on success: {completed.stderr}")
    return value


def expect(value: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    for key, wanted in expected.items():
        observed = value.get(key)
        if observed != wanted:
            fail(
                f"{label} field {key!r} was {observed!r}, expected "
                f"{wanted!r}: {json.dumps(value, sort_keys=True)}"
            )


def openssl(executable: str, arguments: Sequence[str]) -> None:
    completed = subprocess.run(
        [executable, *arguments], check=False, stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE, text=True, timeout=30.0,
    )
    if completed.returncode != 0:
        fail(
            f"openssl {' '.join(arguments)} failed with "
            f"{completed.returncode}: {completed.stderr}"
        )


def generate_tls_fixture(root: Path, executable: str) -> None:
    extension = root / "leaf.ext"
    extension.write_text(
        "basicConstraints=critical,CA:FALSE\n"
        "keyUsage=critical,digitalSignature\n"
        "extendedKeyUsage=serverAuth,clientAuth\n",
        encoding="ascii",
    )
    openssl(executable, [
        "genpkey", "-algorithm", "ED25519", "-out", str(root / "ca.key"),
    ])
    openssl(executable, [
        "req", "-new", "-x509", "-key", str(root / "ca.key"),
        "-out", str(root / "ca.pem"), "-subj", "/CN=AnonSync-Reconcile-CA",
        "-days", "1", "-addext", "basicConstraints=critical,CA:TRUE",
        "-addext", "keyUsage=critical,keyCertSign,cRLSign",
    ])
    for name in ("source", "receiver"):
        openssl(executable, [
            "genpkey", "-algorithm", "ED25519",
            "-out", str(root / f"{name}.key"),
        ])
        openssl(executable, [
            "req", "-new", "-key", str(root / f"{name}.key"),
            "-out", str(root / f"{name}.csr"),
            "-subj", f"/CN=AnonSync-Reconcile-{name}",
        ])
        openssl(executable, [
            "x509", "-req", "-in", str(root / f"{name}.csr"),
            "-CA", str(root / "ca.pem"), "-CAkey", str(root / "ca.key"),
            "-CAcreateserial", "-out", str(root / f"{name}.pem"),
            "-days", "1", "-extfile", str(extension),
        ])


def reserve_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def linux_port_is_listening(port: int) -> bool:
    encoded_port = f"{port:04X}"
    for filename in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            lines = Path(filename).read_text(encoding="ascii").splitlines()[1:]
        except OSError:
            continue
        for line in lines:
            fields = line.split()
            if len(fields) >= 4 and fields[3] == "0A":
                if fields[1].rsplit(":", 1)[-1].upper() == encoded_port:
                    return True
    return False


def wait_until_listening(process: subprocess.Popen[str], port: int) -> None:
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1.0)
            fail(
                f"server exited before listening with {process.returncode}\n"
                f"stdout:\n{stdout}\nstderr:\n{stderr}"
            )
        if linux_port_is_listening(port):
            return
        time.sleep(0.02)
    fail(f"server did not expose port {port}")


def finish_server(process: subprocess.Popen[str], label: str) -> dict[str, Any]:
    try:
        stdout, stderr = process.communicate(timeout=120.0)
    finally:
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
            try:
                process.communicate(timeout=2.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=2.0)
    if process.returncode != 0:
        fail(
            f"{label} failed with {process.returncode}\n"
            f"stdout:\n{stdout}\nstderr:\n{stderr}"
        )
    if stderr:
        fail(f"{label} wrote diagnostics on success: {stderr}")
    try:
        value = json.loads(stdout)
    except json.JSONDecodeError as error:
        fail(f"{label} did not emit JSON: {error}: {stdout}")
    if not isinstance(value, dict):
        fail(f"{label} JSON is not an object")
    return value


_PUBLICATION_TEMP_PREFIX = ".anonsync-publish-v1-"
_PUBLICATION_TEMP_SUFFIX = ".tmp"


def publication_temp_basename_is_exact(basename: str) -> bool:
    if not basename.startswith(_PUBLICATION_TEMP_PREFIX):
        return False
    if not basename.endswith(_PUBLICATION_TEMP_SUFFIX):
        return False
    body = basename[
        len(_PUBLICATION_TEMP_PREFIX) : -len(_PUBLICATION_TEMP_SUFFIX)
    ]
    if len(body) != 50 or body[16] != "-" or body[33] != "-":
        return False
    hex_digits = body[:16] + body[17:33] + body[34:]
    return all(byte in "0123456789abcdef" for byte in hex_digits)


def file_identity(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            size += len(block)
            digest.update(block)
    return size, digest.hexdigest()


def tree_snapshot(root: Path) -> dict[str, tuple[int, str]]:
    result: dict[str, tuple[int, str]] = {}
    for path in sorted(root.rglob("*")):
        if publication_temp_basename_is_exact(path.name):
            continue
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root).as_posix()
        result[relative] = file_identity(path)
    return result


def write_repeated_pattern(path: Path, size: int, pattern: bytes) -> None:
    if not pattern:
        fail("large-file pattern must not be empty")
    remaining = size
    with path.open("wb") as stream:
        while remaining:
            block_size = min(1024 * 1024, remaining)
            repetitions = (block_size + len(pattern) - 1) // len(pattern)
            block = (pattern * repetitions)[:block_size]
            stream.write(block)
            remaining -= block_size


def init_combined(
    replica: Path,
    root: Path,
    device: str,
    max_payload_bytes: int | None = None,
) -> tuple[Path, Path, Path]:
    root.mkdir(mode=0o700)
    database_root = root / "db"
    payload_root = root / "payload"
    files_root = root / "files"
    for directory in (database_root, payload_root, files_root):
        directory.mkdir(mode=0o700)
    manifest = database_root / "deployment.json"
    command = [
        str(replica), "init", "--manifest", str(manifest),
        "--replica-db", str(database_root / "replica.sqlite"),
        "--payload-root", str(payload_root),
        "--effect-db", str(database_root / "effect.sqlite"),
        "--files-root", str(files_root),
        "--membership-db", str(database_root / "membership.sqlite"),
        "--anchor-db", str(database_root / "anchor.sqlite"),
        "--folder", "reconciliation-process", "--local-device", device,
        "--local-epoch", "1",
    ]
    if max_payload_bytes is not None:
        command.extend(["--max-payload-bytes", str(max_payload_bytes)])
    run_json(command, label=f"{device} combined deployment init")
    return manifest, payload_root, files_root


def run_reconciliation_session(
    replica: Path,
    certificates: Path,
    serving_manifest: Path,
    pulling_manifest: Path,
    serving_device: str,
    pulling_device: str,
    serving_pin: str,
    sequence: str,
    max_round_trips: int = 8,
    payload_continuation: dict[str, Any] | None = None,
    page_continuation: dict[str, Any] | None = None,
    timeout_seconds: int = 5,
) -> tuple[dict[str, Any], dict[str, Any]]:
    port = reserve_port()
    server_command = [
        str(replica), "serve-one", "--manifest", str(serving_manifest),
        "--bind-address", "127.0.0.1", "--port", str(port),
        "--certificate", str(certificates / f"{serving_device}.pem"),
        "--private-key", str(certificates / f"{serving_device}.key"),
        "--ca-file", str(certificates / "ca.pem"),
        "--timeout-seconds", str(timeout_seconds), "--max-round-trips",
        str(max_round_trips),
    ]
    server = subprocess.Popen(
        server_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True,
    )
    try:
        wait_until_listening(server, port)
        client_command = [
            str(replica), "reconcile-pull", "--manifest", str(pulling_manifest),
            "--remote-device", serving_device, "--remote-epoch", "1",
            "--remote-spki", serving_pin, "--address", "127.0.0.1",
            "--port", str(port),
            "--certificate", str(certificates / f"{pulling_device}.pem"),
            "--private-key", str(certificates / f"{pulling_device}.key"),
            "--ca-file", str(certificates / "ca.pem"),
            "--timeout-seconds", str(timeout_seconds), "--max-round-trips",
            str(max_round_trips), "--max-source-resets",
            str(min(4, max_round_trips)),
        ]
        if payload_continuation is not None and page_continuation is not None:
            fail("payload and page continuations are mutually exclusive")
        if payload_continuation is not None:
            required = (
                "source_evidence_set_digest", "payload_operation_id",
                "payload_content_sha256", "payload_total_size_bytes",
                "payload_next_offset_bytes",
            )
            missing = [
                key for key in required if key not in payload_continuation
            ]
            if missing:
                fail(
                    "payload continuation is missing fields: "
                    + ", ".join(missing)
                )
            client_command.extend([
                "--source-evidence-set-digest",
                str(payload_continuation["source_evidence_set_digest"]),
                "--payload-operation-id",
                str(payload_continuation["payload_operation_id"]),
                "--payload-content-sha256",
                str(payload_continuation["payload_content_sha256"]),
                "--payload-total-size",
                str(payload_continuation["payload_total_size_bytes"]),
                "--payload-next-offset",
                str(payload_continuation["payload_next_offset_bytes"]),
            ])
        if page_continuation is not None:
            required = (
                "source_evidence_set_digest", "next_after_operation_id",
            )
            missing = [
                key for key in required if key not in page_continuation
            ]
            if missing:
                fail(
                    "page continuation is missing fields: "
                    + ", ".join(missing)
                )
            client_command.extend([
                "--source-evidence-set-digest",
                str(page_continuation["source_evidence_set_digest"]),
                "--after-operation-id",
                str(page_continuation["next_after_operation_id"]),
            ])
        client = run_json(
            client_command, label=f"reconciliation pull {sequence}",
            timeout=180.0,
        )
        source = finish_server(server, f"reconciliation source {sequence}")
        require_direct_source_frame(
            source, f"reconciliation source {sequence}"
        )
    finally:
        if server.poll() is None:
            server.kill()
            server.communicate(timeout=2.0)
    return client, source


def require_direct_source_frame(
    value: dict[str, object], label: str
) -> None:
    responses = value.get("reconciliation_responses_written")
    if value.get("reconciliation_response_direct_source_frames") != responses:
        fail(
            f"{label}: every response was not built through the direct "
            "generation-9 source-frame path"
        )
    if value.get(
        "reconciliation_response_direct_source_frame_payload_page_bytes_at_reservation"
    ) != 0:
        fail(
            f"{label}: an aggregate source payload page survived final-frame "
            "reservation"
        )
    staging = value.get(
        "reconciliation_response_direct_source_frame_maximum_staging_bytes"
    )
    if staging != 0:
        fail(f"{label}: direct source framing retained range-sized staging")
    descriptors = value.get(
        "reconciliation_response_direct_source_frame_maximum_open_descriptors"
    )
    if (
        not isinstance(descriptors, int)
        or isinstance(descriptors, bool)
        or descriptors < 0
        or descriptors > 128
    ):
        fail(f"{label}: direct source descriptor frontier is invalid")
    payload_bytes = value.get(
        "reconciliation_response_direct_source_frame_payload_bytes"
    )
    if (
        not isinstance(payload_bytes, int)
        or isinstance(payload_bytes, bool)
        or payload_bytes < 0
    ):
        fail(f"{label}: direct source payload-byte accounting is invalid")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replica", required=True, type=Path)
    parser.add_argument("--folder", required=True, type=Path)
    args = parser.parse_args()
    replica = args.replica.resolve(strict=True)
    folder = args.folder.resolve(strict=True)
    openssl_executable = shutil.which("openssl")
    if openssl_executable is None:
        fail("openssl executable is unavailable")

    with tempfile.TemporaryDirectory(prefix="anonsync-reconcile-process-") as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        certificates = root / "certificates"
        certificates.mkdir(mode=0o700)
        generate_tls_fixture(certificates, openssl_executable)

        source_manifest, _, source_files = init_combined(
            replica, root / "source", "source"
        )
        receiver_manifest, _, receiver_files = init_combined(
            replica, root / "receiver", "receiver"
        )
        run_json([
            str(folder), "init", "--manifest", str(source_manifest),
        ], label="source folder catalog init")
        run_json([
            str(folder), "init", "--manifest", str(receiver_manifest),
        ], label="receiver folder catalog init")

        source_pin = run_json([
            str(replica), "certificate-spki", "--certificate",
            str(certificates / "source.pem"),
        ], label="source certificate pin")["spki_sha256"]
        receiver_pin = run_json([
            str(replica), "certificate-spki", "--certificate",
            str(certificates / "receiver.pem"),
        ], label="receiver certificate pin")["spki_sha256"]
        run_json([
            str(replica), "membership-publish", "--manifest",
            str(source_manifest), "--policy-epoch", "1", "--peer",
            f"receiver:1:{receiver_pin}",
        ], label="source membership publication")
        run_json([
            str(replica), "membership-publish", "--manifest",
            str(receiver_manifest), "--policy-epoch", "1", "--peer",
            f"source:1:{source_pin}",
        ], label="receiver membership publication")

        batch = source_files / "batch"
        batch.mkdir(mode=0o700)
        for index in range(3):
            (batch / f"item-{index:03d}.txt").write_bytes(
                f"AnonSync production reconciliation payload {index:03d}\n".encode(
                    "ascii"
                )
            )
        source_tree = tree_snapshot(source_files)
        source_pass = run_json([
            str(folder), "run", "--manifest", str(source_manifest),
        ], label="source configured-folder publication")
        expect(source_pass, {
            "terminal_class": "completed", "regular_files": 3,
            "local_published": 3, "remote_applied": 0,
        }, "source configured-folder publication")

        first_pull, first_source = run_reconciliation_session(
            replica, certificates, source_manifest, receiver_manifest,
            "source", "receiver", source_pin, "source-to-receiver-1",
        )
        expect(first_pull, {
            "command": "reconcile-pull", "disposition": "pull_completed",
            "pull_disposition": "complete", "peer_authenticated": True,
            "peer_device_id": "source", "round_trips": 1,
            "pages_applied": 1, "inserted_quarantined": 0,
            "duplicate_operations": 0, "inserted_payloads": 3,
            "existing_payloads": 0, "has_more": False,
        }, "first reconciliation pull")
        if (
            first_pull.get("inserted_active", 0) +
            first_pull.get("inserted_pending", 0)
        ) != 3:
            fail("first reconciliation did not admit all three operations")
        expect(first_source, {
            "command": "serve-one", "peer_dispatch_enabled": True,
            "disposition": "application_served",
            "application_disposition": "reconciliation",
            "reconciliation_disposition": "complete",
            "reconciliation_requests_received": 1,
            "reconciliation_responses_written": 1,
            "reconciliation_pages_served": 1,
            "peer_device_id": "receiver", "stop_reason": "max_sessions_reached",
        }, "first reconciliation source")
        if first_pull.get("request_frame_bytes_written") != first_source.get(
            "reconciliation_request_frame_bytes_received"
        ):
            fail("first reconciliation peers disagree on request bytes")
        if first_pull.get("response_frame_bytes_received") != first_source.get(
            "reconciliation_response_frame_bytes_written"
        ):
            fail("first reconciliation peers disagree on response bytes")
        if first_source.get(
            "reconciliation_response_frame_owned_handoffs"
        ) != first_source.get("reconciliation_responses_written"):
            fail(
                "first reconciliation source did not transfer every final "
                "response frame into TLS ownership"
            )

        receiver_pass = run_json([
            str(folder), "run", "--manifest", str(receiver_manifest),
        ], label="receiver configured-folder apply")
        expect(receiver_pass, {
            "terminal_class": "completed", "local_published": 0,
            "remote_applied": 3, "skipped_conflicted_remote_paths": 0,
        }, "receiver configured-folder apply")
        if tree_snapshot(receiver_files) != source_tree:
            fail("receiver materialized tree differs from source tree")

        source_status = run_json([
            str(replica), "status", "--manifest", str(source_manifest),
        ], label="source status")
        receiver_status = run_json([
            str(replica), "status", "--manifest", str(receiver_manifest),
        ], label="receiver status after first pull")
        for field in (
            "replica_evidence_operations", "replica_active_operations",
            "replica_operation_set_digest", "replica_evidence_set_digest",
            "replica_visible_state_digest",
        ):
            if receiver_status.get(field) != source_status.get(field):
                fail(f"replicas disagree after first pull on {field}")

        first_receiver_cutpoint = {
            key: receiver_status.get(key) for key in (
                "replica_state_generation", "replica_cutpoint_digest",
                "replica_evidence_set_digest", "replica_visible_state_digest",
                "payload_entries", "payload_indexed_bytes",
                "payload_snapshot_digest",
            )
        }
        second_pull, second_source = run_reconciliation_session(
            replica, certificates, source_manifest, receiver_manifest,
            "source", "receiver", source_pin, "source-to-receiver-2",
        )
        expect(second_pull, {
            "pull_disposition": "complete", "round_trips": 1,
            "pages_applied": 1, "inserted_active": 0,
            "inserted_pending": 0, "inserted_quarantined": 0,
            "duplicate_operations": 3, "inserted_payloads": 0,
            "existing_payloads": 3, "has_more": False,
        }, "second reconciliation pull")
        expect(second_source, {
            "application_disposition": "reconciliation",
            "reconciliation_disposition": "complete",
            "reconciliation_requests_received": 1,
            "reconciliation_responses_written": 1,
        }, "second reconciliation source")

        second_receiver_status = run_json([
            str(replica), "status", "--manifest", str(receiver_manifest),
        ], label="receiver status after duplicate pull")
        second_receiver_cutpoint = {
            key: second_receiver_status.get(key) for key in first_receiver_cutpoint
        }
        if second_receiver_cutpoint != first_receiver_cutpoint:
            fail(
                "duplicate reconciliation changed receiver durable cutpoint: "
                f"before={first_receiver_cutpoint}, "
                f"after={second_receiver_cutpoint}"
            )
        receiver_no_op = run_json([
            str(folder), "run", "--manifest", str(receiver_manifest),
        ], label="receiver fresh-process no-op")
        expect(receiver_no_op, {
            "local_published": 0, "remote_applied": 0,
            "local_catalog_no_op": 3,
            "replica_cutpoint_before": receiver_pass["replica_cutpoint_after"],
            "replica_cutpoint_after": receiver_pass["replica_cutpoint_after"],
        }, "receiver fresh-process no-op")
        if tree_snapshot(receiver_files) != source_tree:
            fail("receiver no-op pass changed the materialized tree")

        reverse_path = receiver_files / "nested" / "from-receiver.txt"
        reverse_path.parent.mkdir(mode=0o700)
        reverse_path.write_bytes(b"reverse-direction AnonSync edit\n")
        receiver_publish = run_json([
            str(folder), "run", "--manifest", str(receiver_manifest),
        ], label="receiver reverse publication")
        expect(receiver_publish, {
            "terminal_class": "completed", "regular_files": 4,
            "local_published": 1, "remote_applied": 0,
            "local_catalog_no_op": 3,
        }, "receiver reverse publication")
        receiver_tree = tree_snapshot(receiver_files)

        reverse_pull, reverse_source = run_reconciliation_session(
            replica, certificates, receiver_manifest, source_manifest,
            "receiver", "source", receiver_pin, "receiver-to-source-1",
        )
        expect(reverse_pull, {
            "command": "reconcile-pull", "disposition": "pull_completed",
            "pull_disposition": "complete", "peer_authenticated": True,
            "peer_device_id": "receiver", "round_trips": 1,
            "pages_applied": 1, "inserted_quarantined": 0,
            "duplicate_operations": 3, "inserted_payloads": 1,
            "existing_payloads": 3, "has_more": False,
        }, "reverse reconciliation pull")
        if (
            reverse_pull.get("inserted_active", 0) +
            reverse_pull.get("inserted_pending", 0)
        ) != 1:
            fail("reverse reconciliation did not admit the receiver edit")
        expect(reverse_source, {
            "command": "serve-one", "peer_dispatch_enabled": True,
            "disposition": "application_served",
            "application_disposition": "reconciliation",
            "reconciliation_disposition": "complete",
            "reconciliation_requests_received": 1,
            "reconciliation_responses_written": 1,
            "reconciliation_pages_served": 1,
            "peer_device_id": "source", "stop_reason": "max_sessions_reached",
        }, "reverse reconciliation source")

        source_apply = run_json([
            str(folder), "run", "--manifest", str(source_manifest),
        ], label="source reverse remote apply")
        expect(source_apply, {
            "terminal_class": "completed", "local_published": 0,
            "remote_applied": 1, "local_catalog_no_op": 3,
            "skipped_conflicted_remote_paths": 0,
        }, "source reverse remote apply")
        if tree_snapshot(source_files) != receiver_tree:
            fail("source materialized tree differs after reverse reconciliation")

        source_after_reverse = run_json([
            str(replica), "status", "--manifest", str(source_manifest),
        ], label="source status after reverse pull")
        receiver_after_reverse = run_json([
            str(replica), "status", "--manifest", str(receiver_manifest),
        ], label="receiver status after reverse publication")
        for field in (
            "replica_evidence_operations", "replica_active_operations",
            "replica_operation_set_digest", "replica_evidence_set_digest",
            "replica_visible_state_digest",
        ):
            if source_after_reverse.get(field) != receiver_after_reverse.get(field):
                fail(f"replicas disagree after reverse pull on {field}")

        source_reverse_cutpoint = {
            key: source_after_reverse.get(key) for key in (
                "replica_state_generation", "replica_cutpoint_digest",
                "replica_evidence_set_digest", "replica_visible_state_digest",
                "payload_entries", "payload_indexed_bytes",
                "payload_snapshot_digest",
            )
        }
        reverse_repeat, reverse_repeat_source = run_reconciliation_session(
            replica, certificates, receiver_manifest, source_manifest,
            "receiver", "source", receiver_pin, "receiver-to-source-2",
        )
        expect(reverse_repeat, {
            "pull_disposition": "complete", "round_trips": 1,
            "pages_applied": 1, "inserted_active": 0,
            "inserted_pending": 0, "inserted_quarantined": 0,
            "duplicate_operations": 4, "inserted_payloads": 0,
            "existing_payloads": 4, "has_more": False,
        }, "reverse duplicate reconciliation pull")
        expect(reverse_repeat_source, {
            "application_disposition": "reconciliation",
            "reconciliation_disposition": "complete",
            "reconciliation_requests_received": 1,
            "reconciliation_responses_written": 1,
        }, "reverse duplicate reconciliation source")
        source_after_reverse_repeat = run_json([
            str(replica), "status", "--manifest", str(source_manifest),
        ], label="source status after reverse duplicate pull")
        if {
            key: source_after_reverse_repeat.get(key)
            for key in source_reverse_cutpoint
        } != source_reverse_cutpoint:
            fail("reverse duplicate reconciliation changed source durable state")

        # A fresh share removes operation-order ambiguity from the product-level
        # range proof. One generation-9 round trip stages sixteen exact 4 MiB
        # ranges: one complete 64 MiB page, but not the complete file. The next
        # fresh client and server receive only the explicit continuation tuple
        # printed by the first shipped CLI process and complete the tail beyond
        # the page ceiling.
        range_payload_ceiling = 80 * 1024 * 1024
        range_source_manifest, _, range_source_files = init_combined(
            replica, root / "range-source", "source", range_payload_ceiling
        )
        range_receiver_manifest, _, range_receiver_files = init_combined(
            replica, root / "range-receiver", "receiver",
            range_payload_ceiling,
        )
        run_json([
            str(folder), "init", "--manifest", str(range_source_manifest),
        ], label="range source folder catalog init")
        run_json([
            str(folder), "init", "--manifest", str(range_receiver_manifest),
        ], label="range receiver folder catalog init")
        run_json([
            str(replica), "membership-publish", "--manifest",
            str(range_source_manifest), "--policy-epoch", "1", "--peer",
            f"receiver:1:{receiver_pin}",
        ], label="range source membership publication")
        run_json([
            str(replica), "membership-publish", "--manifest",
            str(range_receiver_manifest), "--policy-epoch", "1", "--peer",
            f"source:1:{source_pin}",
        ], label="range receiver membership publication")

        first_session_bytes = 64 * 1024 * 1024
        range_size = first_session_bytes + 4096
        range_pattern = b"AnonSync exact ranged payload over fresh TLS processes\n"
        range_path = range_source_files / "large" / "resumable.bin"
        range_path.parent.mkdir(mode=0o700)
        write_repeated_pattern(range_path, range_size, range_pattern)
        range_source_tree = tree_snapshot(range_source_files)
        range_publish = run_json([
            str(folder), "run", "--manifest", str(range_source_manifest),
        ], label="range source configured-folder publication", timeout=90.0)
        expect(range_publish, {
            "terminal_class": "completed", "regular_files": 1,
            "local_published": 1, "remote_applied": 0,
        }, "range source configured-folder publication")

        first_range_pull, first_range_source = run_reconciliation_session(
            replica, certificates, range_source_manifest,
            range_receiver_manifest, "source", "receiver", source_pin,
            "ranged-source-to-receiver-1", max_round_trips=3,
            timeout_seconds=30,
        )
        expect(first_range_pull, {
            "command": "reconcile-pull", "disposition": "pull_completed",
            "pull_disposition": "round_trip_limit_reached",
            "peer_authenticated": True, "peer_device_id": "source",
            "round_trips": 3,
            "source_payload_preparing_responses": 2,
            "pages_applied": 0,
            "inserted_active": 0, "duplicate_operations": 0,
            "staged_payload_ranges": 16,
            "staged_payload_bytes": first_session_bytes,
            "payload_total_size_bytes": range_size,
            "payload_next_offset_bytes": first_session_bytes,
            "has_more": True,
        }, "first ranged reconciliation pull")
        for key in (
            "source_evidence_set_digest", "payload_operation_id",
            "payload_content_sha256",
        ):
            value = first_range_pull.get(key)
            if not isinstance(value, str) or len(value) != 64:
                fail(f"first ranged pull did not expose exact {key}")
        expect(first_range_source, {
            "application_disposition": "reconciliation",
            "reconciliation_disposition": "round_trip_limit_reached",
            "reconciliation_requests_received": 3,
            "reconciliation_responses_written": 3,
            "reconciliation_source_payload_preparing_responses": 2,
            "reconciliation_content_defined_manifest_projection_steps": 3,
            "reconciliation_content_defined_manifest_hashed_bytes":
                range_size,
            "reconciliation_ranged_payload_windows": 1,
            "reconciliation_ranged_payload_ranges": 16,
            "reconciliation_ranged_payload_bytes": first_session_bytes,
            "reconciliation_payload_total_size_bytes": range_size,
            "reconciliation_payload_next_offset_bytes": first_session_bytes,
        }, "first ranged reconciliation source")
        if (
            first_range_source.get("reconciliation_payload_operation_id") !=
                first_range_pull["payload_operation_id"] or
            first_range_source.get("reconciliation_payload_content_sha256") !=
                first_range_pull["payload_content_sha256"]
        ):
            fail("ranged reconciliation peers disagree on continuation identity")
        first_range_status = run_json([
            str(replica), "status", "--manifest", str(range_receiver_manifest),
        ], label="range receiver status after first durable range")
        expect(first_range_status, {
            "replica_evidence_operations": 0,
            "replica_active_operations": 0,
            "payload_entries": 0,
            "payload_transient_entries": 1,
            "payload_transient_bytes": first_session_bytes,
        }, "range receiver incomplete-payload crash frontier")

        final_range_pull, final_range_source = run_reconciliation_session(
            replica, certificates, range_source_manifest,
            range_receiver_manifest, "source", "receiver", source_pin,
            "ranged-source-to-receiver-2", max_round_trips=3,
            payload_continuation=first_range_pull, timeout_seconds=30,
        )
        expect(final_range_pull, {
            "command": "reconcile-pull", "disposition": "pull_completed",
            "pull_disposition": "complete",
            "round_trips": 2,
            "source_payload_preparing_responses": 0,
            "pages_applied": 2,
            "inserted_active": 1, "duplicate_operations": 0,
            "inserted_payloads": 1, "staged_payload_ranges": 1,
            "staged_payload_bytes": range_size - first_session_bytes,
            "terminal_verification_steps": 3,
            "terminal_verification_local_continuation_steps": 2,
            "terminal_verification_step_budget_exhaustions": 0,
            "has_more": False,
        }, "restart-warm final range and local verification completion")
        if (
            final_range_pull.get("source_evidence_set_digest") !=
                first_range_pull["source_evidence_set_digest"] or
            final_range_pull.get("next_after_operation_id") !=
                first_range_pull["payload_operation_id"]
        ):
            fail("final range did not advance to the exact operation cursor")
        for key in (
            "payload_operation_id", "payload_content_sha256",
            "payload_total_size_bytes", "payload_next_offset_bytes",
        ):
            if key in final_range_pull:
                fail(f"locally completed ranged pull retained field {key}")
        expect(final_range_source, {
            "application_disposition": "reconciliation",
            "reconciliation_disposition": "complete",
            "reconciliation_requests_received": 2,
            "reconciliation_responses_written": 2,
            "reconciliation_source_payload_preparing_responses": 0,
            "reconciliation_content_defined_manifest_projection_steps": 0,
            "reconciliation_content_defined_manifest_hashed_bytes": 0,
            "reconciliation_content_defined_manifest_reuses": 1,
            "reconciliation_content_defined_chunk_index_reuses": 1,
            "reconciliation_ranged_payload_ranges": 1,
            "reconciliation_ranged_payload_bytes":
                range_size - first_session_bytes,
            "reconciliation_has_more": False,
        }, "restart-warm final ranged source completion")

        completed_range_status = run_json([
            str(replica), "status", "--manifest",
            str(range_receiver_manifest),
        ], label="range receiver status after local verification pulse")
        expect(completed_range_status, {
            "replica_evidence_operations": 1,
            "replica_active_operations": 1,
            "payload_entries": 1,
            "payload_transient_entries": 0,
            "payload_transient_bytes": 0,
        }, "local verification pulse publication frontier")

        completed_range_pull, completed_range_source = (
            run_reconciliation_session(
                replica, certificates, range_source_manifest,
                range_receiver_manifest, "source", "receiver", source_pin,
                "ranged-source-to-receiver-exact-cursor",
                max_round_trips=1,
                page_continuation=final_range_pull,
                timeout_seconds=30,
            )
        )
        expect(completed_range_pull, {
            "command": "reconcile-pull", "disposition": "pull_completed",
            "pull_disposition": "complete", "round_trips": 1,
            "pages_applied": 1, "inserted_active": 0,
            "duplicate_operations": 0,
            "inserted_payloads": 0, "staged_payload_ranges": 0,
            "staged_payload_bytes": 0,
            "terminal_verification_steps": 0,
            "terminal_verification_local_continuation_steps": 0,
            "terminal_verification_step_budget_exhaustions": 0,
            "has_more": False,
        }, "payload-cold exact-cursor completion")
        for key in (
            "payload_operation_id", "payload_content_sha256",
            "payload_total_size_bytes", "payload_next_offset_bytes",
        ):
            if key in completed_range_pull:
                fail(f"exact-cursor completion retained field {key}")
        if (
            completed_range_pull.get("next_after_operation_id") !=
                final_range_pull["next_after_operation_id"]
        ):
            fail("exact-cursor completion changed the terminal page cursor")
        response_bytes = completed_range_pull.get("response_frame_bytes_received")
        if (
            not isinstance(response_bytes, int) or
            isinstance(response_bytes, bool) or
            response_bytes <= 0 or response_bytes > 1024
        ):
            fail("exact-cursor completion was not a bounded payload-cold frame")
        expect(completed_range_source, {
            "application_disposition": "reconciliation",
            "reconciliation_disposition": "complete",
            "reconciliation_requests_received": 1,
            "reconciliation_responses_written": 1,
            "reconciliation_ranged_payload_ranges": 0,
            "reconciliation_ranged_payload_bytes": 0,
        }, "payload-cold exact-cursor source completion")
        for key in (
            "reconciliation_payload_operation_id",
            "reconciliation_payload_content_sha256",
            "reconciliation_payload_total_size_bytes",
            "reconciliation_payload_next_offset_bytes",
        ):
            if key in completed_range_source:
                fail(f"exact-cursor source retained terminal field {key}")

        range_receiver_apply = run_json([
            str(folder), "run", "--manifest", str(range_receiver_manifest),
        ], label="range receiver configured-folder apply", timeout=90.0)
        expect(range_receiver_apply, {
            "terminal_class": "completed", "local_published": 0,
            "remote_applied": 1, "skipped_conflicted_remote_paths": 0,
        }, "range receiver configured-folder apply")
        if tree_snapshot(range_receiver_files) != range_source_tree:
            fail("ranged payload did not materialize exact whole-file bytes")
        range_receiver_no_op = run_json([
            str(folder), "run", "--manifest", str(range_receiver_manifest),
        ], label="range receiver fresh-process no-op", timeout=90.0)
        expect(range_receiver_no_op, {
            "local_published": 0, "remote_applied": 0,
            "local_catalog_no_op": 1,
        }, "range receiver fresh-process no-op")

        source_no_op = run_json([
            str(folder), "run", "--manifest", str(source_manifest),
        ], label="source final fresh-process no-op")
        receiver_final_no_op = run_json([
            str(folder), "run", "--manifest", str(receiver_manifest),
        ], label="receiver final fresh-process no-op")
        for value, label in (
            (source_no_op, "source final no-op"),
            (receiver_final_no_op, "receiver final no-op"),
        ):
            expect(value, {
                "local_published": 0, "remote_applied": 0,
                "local_catalog_no_op": 4,
            }, label)
        if (
            tree_snapshot(source_files) != receiver_tree or
            tree_snapshot(receiver_files) != receiver_tree
        ):
            fail("final no-op passes changed the converged peer trees")

    print("anonsync reconciliation process test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
