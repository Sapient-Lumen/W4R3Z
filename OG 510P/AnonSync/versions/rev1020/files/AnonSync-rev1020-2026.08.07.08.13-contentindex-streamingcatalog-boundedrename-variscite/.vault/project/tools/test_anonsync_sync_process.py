#!/usr/bin/env python3
"""Exercise the product sync-once composition across two real peer processes.

The test bootstraps two configured folders and mutual-TLS identities, authors a
nested tree through sync-once's local pass, pulls it on the other peer, and
forces remote materialization through a one-file aggregate frontier. The first
cycle commits one deterministic remote prefix; the second finishes the remote
suffix but still has an authenticated local-scan suffix; and the third settles
through scan-only durable progress. The test then proves a duplicate invocation
is a durable no-op and converges a reverse-direction nested edit. The server
remains the existing peer-dispatch command so this test detects accidental
creation of a second wire protocol or folder engine.
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


def unique_json_object_pairs(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, member in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON object key {key!r}")
        value[key] = member
    return value


def run_json(
    command: Sequence[str], *, label: str, timeout: float = 60.0
) -> dict[str, Any]:
    completed = subprocess.run(
        list(command), check=False, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, timeout=timeout,
    )
    try:
        value = json.loads(
            completed.stdout, object_pairs_hook=unique_json_object_pairs
        )
    except (json.JSONDecodeError, ValueError) as error:
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


def require_object(
    value: dict[str, Any], key: str, label: str
) -> dict[str, Any]:
    observed = value.get(key)
    if not isinstance(observed, dict):
        fail(
            f"{label} field {key!r} is not an object: "
            f"{json.dumps(value, sort_keys=True)}"
        )
    return observed


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
        "-out", str(root / "ca.pem"), "-subj", "/CN=AnonSync-Sync-CA",
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
            "-subj", f"/CN=AnonSync-Sync-{name}",
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
        stdout, stderr = process.communicate(timeout=30.0)
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
        result[path.relative_to(root).as_posix()] = file_identity(path)
    return result


def init_combined(
    replica: Path,
    root: Path,
    device: str,
    max_payload_bytes: int | None = None,
) -> tuple[Path, Path]:
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
    return manifest, files_root


def run_sync_once_session(
    replica: Path,
    sync: Path,
    certificates: Path,
    serving_manifest: Path,
    syncing_manifest: Path,
    serving_device: str,
    syncing_device: str,
    serving_pin: str,
    sequence: str,
    syncing_extra_arguments: Sequence[str] = (),
) -> tuple[dict[str, Any], dict[str, Any]]:
    port = reserve_port()
    server = subprocess.Popen([
        str(replica), "serve-one", "--manifest", str(serving_manifest),
        "--bind-address", "127.0.0.1", "--port", str(port),
        "--certificate", str(certificates / f"{serving_device}.pem"),
        "--private-key", str(certificates / f"{serving_device}.key"),
        "--ca-file", str(certificates / "ca.pem"),
        "--timeout-seconds", "5", "--max-round-trips", "8",
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        wait_until_listening(server, port)
        client = run_json([
            str(sync), "once", "--manifest", str(syncing_manifest),
            "--remote-device", serving_device, "--remote-epoch", "1",
            "--remote-spki", serving_pin, "--address", "127.0.0.1",
            "--port", str(port),
            "--certificate", str(certificates / f"{syncing_device}.pem"),
            "--private-key", str(certificates / f"{syncing_device}.key"),
            "--ca-file", str(certificates / "ca.pem"),
            "--timeout-seconds", "5", "--max-runtime-seconds", "30",
            "--max-round-trips", "8",
            *syncing_extra_arguments,
        ], label=f"sync once {sequence}")
        source = finish_server(server, f"sync source {sequence}")
    finally:
        if server.poll() is None:
            server.kill()
            server.communicate(timeout=2.0)
    return client, source


def expect_sync_top(
    value: dict[str, Any], disposition: str, local: str, remote: str,
    label: str, *, settled: bool = True,
) -> None:
    expect(value, {
        "command": "once", "terminal_class": "completed",
        "disposition": disposition, "bounded_progress": True,
        "durable_progress": disposition != "complete_no_op",
        "settled": settled, "local_device_id": local,
        "remote_device_id": remote, "transport": "direct_tcp",
        "pull_attempted": True, "remote_apply_attempted": True,
    }, label)
    reconciliation = require_object(value, "reconciliation", label)
    expect(reconciliation, {
        "client_disposition": "pull_completed", "connected": True,
        "handshake_complete": True, "peer_authenticated": True,
        "peer_device_id": remote, "peer_epoch": 1,
        "transport": "direct_tcp",
    }, f"{label} reconciliation")


def expect_server(
    value: dict[str, Any], peer: str, label: str
) -> None:
    expect(value, {
        "command": "serve-one", "peer_dispatch_enabled": True,
        "disposition": "application_served",
        "application_disposition": "reconciliation",
        "reconciliation_disposition": "complete",
        "reconciliation_requests_received": 1,
        "reconciliation_responses_written": 1,
        "reconciliation_pages_served": 1,
        "peer_device_id": peer, "stop_reason": "max_sessions_reached",
    }, label)
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
    if value.get(
        "reconciliation_response_direct_source_frame_maximum_staging_bytes"
    ) != 0:
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


def status_cutpoint(status: dict[str, Any]) -> dict[str, Any]:
    return {
        key: status.get(key) for key in (
            "replica_state_generation", "replica_cutpoint_digest",
            "replica_evidence_set_digest", "replica_visible_state_digest",
            "payload_entries", "payload_indexed_bytes",
            "payload_snapshot_digest",
        )
    }


def require_replica_equivalence(
    left: dict[str, Any], right: dict[str, Any], label: str
) -> None:
    for field in (
        "replica_evidence_operations", "replica_active_operations",
        "replica_operation_set_digest", "replica_evidence_set_digest",
        "replica_visible_state_digest",
    ):
        if left.get(field) != right.get(field):
            fail(f"{label}: replicas disagree on {field}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replica", required=True, type=Path)
    parser.add_argument("--folder", required=True, type=Path)
    parser.add_argument("--sync", required=True, type=Path)
    args = parser.parse_args()
    replica = args.replica.resolve(strict=True)
    folder = args.folder.resolve(strict=True)
    sync = args.sync.resolve(strict=True)
    openssl_executable = shutil.which("openssl")
    if openssl_executable is None:
        fail("openssl executable is unavailable")

    with tempfile.TemporaryDirectory(prefix="anonsync-sync-once-process-") as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        certificates = root / "certificates"
        certificates.mkdir(mode=0o700)
        generate_tls_fixture(certificates, openssl_executable)

        # Every ordinary sync-once cycle runs under an extent above the old
        # 64 MiB protocol/page and 256 MiB aggregate-pass couplings. The
        # files remain small so this isolates composition rather than
        # duplicating the large transfer proof.
        configured_extent = 320 * 1024 * 1024
        source_manifest, source_files = init_combined(
            replica, root / "source", "source", configured_extent
        )
        receiver_manifest, receiver_files = init_combined(
            replica, root / "receiver", "receiver", configured_extent
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
                f"AnonSync production sync-once payload {index:03d}\n".encode(
                    "ascii"
                )
            )
        source_tree = tree_snapshot(source_files)

        source_publish, empty_receiver_server = run_sync_once_session(
            replica, sync, certificates, receiver_manifest, source_manifest,
            "receiver", "source", receiver_pin, "source-local-publication",
        )
        expect_sync_top(
            source_publish, "complete_changed", "source", "receiver",
            "source local publication sync",
        )
        expect(require_object(
            source_publish, "local_pass", "source local publication sync"
        ), {
            "regular_files": 3, "local_published": 3,
            "remote_applied": 0,
        }, "source local publication pass")
        empty_pull = require_object(require_object(
            source_publish, "reconciliation", "source local publication sync"
        ), "pull", "source local publication reconciliation")
        expect(empty_pull, {
            "disposition": "complete", "round_trips": 1,
            "pages_applied": 1, "source_evidence_count": 0,
            "inserted_active": 0, "inserted_pending": 0,
            "duplicate_operations": 0, "inserted_payloads": 0,
            "existing_payloads": 0, "has_more": False,
        }, "empty receiver pull")
        expect(require_object(
            source_publish, "remote_apply_pass",
            "source local publication sync"
        ), {
            "used_idle_fast_path": True,
            "local_catalog_no_op": 3, "remote_applied": 0,
        }, "source publication post-pull pass")
        expect_server(
            empty_receiver_server, "source", "empty receiver server"
        )

        one_file_frontier = (
            "--maximum-file-bytes", "42",
            "--maximum-total-file-bytes", "42",
        )
        first_receiver, first_source = run_sync_once_session(
            replica, sync, certificates, source_manifest, receiver_manifest,
            "source", "receiver", source_pin, "source-to-receiver-1",
            one_file_frontier,
        )
        expect_sync_top(
            first_receiver, "complete_with_unresolved_paths", "receiver",
            "source", "first receiver bounded sync", settled=False,
        )
        expect(require_object(
            first_receiver, "local_pass", "first receiver bounded sync"
        ), {
            "used_idle_fast_path": True,
            "regular_files": 0, "local_published": 0,
            "remote_applied": 0,
        }, "first receiver bounded local pass")
        first_reconciliation = require_object(
            first_receiver, "reconciliation", "first receiver bounded sync"
        )
        first_pull = require_object(
            first_reconciliation, "pull", "first receiver reconciliation"
        )
        expect(first_pull, {
            "disposition": "complete", "round_trips": 1,
            "pages_applied": 1, "inserted_quarantined": 0,
            "duplicate_operations": 0, "inserted_payloads": 3,
            "existing_payloads": 0, "has_more": False,
        }, "first receiver pull")
        if first_pull.get("inserted_active", 0) + first_pull.get(
            "inserted_pending", 0
        ) != 3:
            fail("first receiver pull did not admit all three operations")
        expect(require_object(
            first_receiver, "remote_apply_pass", "first receiver bounded sync"
        ), {
            "local_published": 0, "remote_applied": 1,
            "remote_apply_operations": 1,
            "remote_payload_snapshot_observations": 0,
            "remote_payload_snapshot_entries": 0,
            "remote_targeted_payload_accesses": 1,
            "remote_targeted_payload_probes": 2,
            "remote_targeted_payload_selections": 1,
            "remote_targeted_payload_selected_bytes": 42,
            "deferred_remote_payload_candidates": 0,
            "remote_apply_revalidated_catalog_predecessors": 0,
            "remote_apply_started_after_path": "",
            "remote_apply_resume_after_path": "batch/item-000.txt",
            "remote_apply_wrapped_projection": False,
            "remote_inspected_paths": 2,
            "remote_acknowledged_paths": 1,
            "remote_inspection_sweep_started_after_path": "",
            "remote_inspection_sweep_seen_path_count": 1,
            "completed_remote_inspection_sweep": False,
            "remote_inspection_sweep_had_unresolved_paths": False,
            "deferred_remote_inspection_paths": 2,
            "deferred_remote_apply_candidates": 1,
            "remote_apply_stop_reason": "aggregate_file_byte_frontier",
            "exact_remote_file_bytes": 42,
            "skipped_conflicted_remote_paths": 0,
            "skipped_tombstone_remote_paths": 0,
        }, "first receiver bounded remote apply")
        for phase in ("before", "after_local_pass", "after_pull"):
            if require_object(
                first_receiver, phase, "first receiver bounded sync"
            ).get("remote_apply_resume_after_path") != "":
                fail(
                    "first receiver cursor advanced before the remote apply "
                    f"stage: {phase}"
                )
        if require_object(
            first_receiver, "after", "first receiver bounded sync"
        ).get("remote_apply_resume_after_path") != "batch/item-000.txt":
            fail("sync-once cutpoint did not expose remote cursor advancement")
        expect_server(first_source, "receiver", "first source server")
        if first_pull.get("request_frame_bytes_written") != first_source.get(
            "reconciliation_request_frame_bytes_received"
        ):
            fail("first sync peers disagree on request bytes")
        if first_pull.get("response_frame_bytes_received") != first_source.get(
            "reconciliation_response_frame_bytes_written"
        ):
            fail("first sync peers disagree on response bytes")
        if first_source.get(
            "reconciliation_response_frame_owned_handoffs"
        ) != first_source.get("reconciliation_responses_written"):
            fail(
                "first sync source did not transfer every final response "
                "frame into TLS ownership"
            )
        first_receiver_tree = tree_snapshot(receiver_files)
        if list(first_receiver_tree) != ["batch/item-000.txt"]:
            fail(
                "first bounded receiver sync did not materialize exactly the "
                f"deterministic first path: {first_receiver_tree}"
            )

        completing_receiver, completing_source = run_sync_once_session(
            replica, sync, certificates, source_manifest, receiver_manifest,
            "source", "receiver", source_pin, "source-to-receiver-2",
            one_file_frontier,
        )
        expect_sync_top(
            completing_receiver, "complete_with_unresolved_paths", "receiver",
            "source", "receiver remote-frontier completion sync",
            settled=False,
        )
        expect(require_object(
            completing_receiver, "local_pass",
            "receiver remote-frontier completion sync",
        ), {
            "regular_files": 1, "local_catalog_no_op": 1,
            "remote_applied": 1, "remote_apply_operations": 1,
            "remote_payload_snapshot_observations": 1,
            "remote_payload_snapshot_entries": 3,
            "deferred_remote_payload_candidates": 0,
            "remote_apply_revalidated_catalog_predecessors": 0,
            "remote_apply_started_after_path": "batch/item-000.txt",
            "remote_apply_resume_after_path": "batch/item-001.txt",
            "remote_apply_wrapped_projection": False,
            "remote_inspected_paths": 2,
            "remote_acknowledged_paths": 1,
            "remote_inspection_sweep_started_after_path":
                "batch/item-000.txt",
            "remote_inspection_sweep_seen_path_count": 1,
            "completed_remote_inspection_sweep": False,
            "remote_inspection_sweep_had_unresolved_paths": False,
            "deferred_remote_inspection_paths": 2,
            "deferred_remote_apply_candidates": 1,
            "remote_apply_stop_reason": "aggregate_file_byte_frontier",
        }, "receiver remote-frontier completion local pass")
        completing_pull = require_object(require_object(
            completing_receiver, "reconciliation",
            "receiver remote-frontier completion sync",
        ), "pull", "receiver remote-frontier completion reconciliation")
        expect(completing_pull, {
            "disposition": "complete", "round_trips": 1,
            "pages_applied": 1, "inserted_active": 0,
            "inserted_pending": 0, "inserted_quarantined": 0,
            "duplicate_operations": 3, "inserted_payloads": 0,
            "existing_payloads": 3, "has_more": False,
        }, "receiver remote-frontier completion pull")
        expect(require_object(
            completing_receiver, "remote_apply_pass",
            "receiver remote-frontier completion sync",
        ), {
            "regular_files": 1, "local_catalog_no_op": 1,
            "completed_local_scan_epoch": False,
            "local_scan_seen_path_count": 1,
            "local_scan_resume_after_path": "batch/item-000.txt",
            "local_scan_stop_reason": "aggregate_file_byte_frontier",
            "remote_applied": 1, "remote_apply_operations": 1,
            "remote_payload_snapshot_observations": 1,
            "remote_payload_snapshot_entries": 3,
            "deferred_remote_payload_candidates": 0,
            "remote_apply_revalidated_catalog_predecessors": 0,
            "remote_apply_started_after_path": "batch/item-001.txt",
            "remote_apply_resume_after_path": "batch/item-001.txt",
            "remote_apply_wrapped_projection": True,
            "remote_inspected_paths": 3,
            "remote_acknowledged_paths": 3,
            "remote_inspection_sweep_started_after_path":
                "batch/item-001.txt",
            "remote_inspection_sweep_seen_path_count": 3,
            "completed_remote_inspection_sweep": True,
            "remote_inspection_sweep_had_unresolved_paths": False,
            "deferred_remote_inspection_paths": 0,
            "deferred_remote_apply_candidates": 0,
            "remote_apply_stop_reason": "end_of_projection",
            "exact_remote_file_bytes": 42,
        }, "receiver remote-frontier completion remote apply")
        expect_server(
            completing_source, "receiver",
            "remote-frontier completion source server",
        )
        if tree_snapshot(receiver_files) != source_tree:
            fail("receiver remote frontier did not materialize the source tree")

        settling_receiver, settling_source = run_sync_once_session(
            replica, sync, certificates, source_manifest, receiver_manifest,
            "source", "receiver", source_pin, "source-to-receiver-3",
            one_file_frontier,
        )
        expect_sync_top(
            settling_receiver, "complete_changed", "receiver", "source",
            "receiver scan-frontier settlement sync",
        )
        expect(require_object(
            settling_receiver, "local_pass",
            "receiver scan-frontier settlement sync",
        ), {
            "completed_local_scan_epoch": False,
            "local_scan_seen_path_count": 2,
            "local_scan_resume_after_path": "batch/item-001.txt",
            "local_scan_stop_reason": "aggregate_file_byte_frontier",
            "local_catalog_no_op": 1, "remote_applied": 0,
            "remote_apply_started_after_path": "batch/item-001.txt",
            "remote_apply_resume_after_path": "batch/item-001.txt",
            "remote_apply_wrapped_projection": True,
            "remote_inspected_paths": 3,
            "remote_acknowledged_paths": 3,
            "remote_inspection_sweep_started_after_path":
                "batch/item-001.txt",
            "remote_inspection_sweep_seen_path_count": 3,
            "completed_remote_inspection_sweep": True,
            "remote_inspection_sweep_had_unresolved_paths": False,
            "deferred_remote_inspection_paths": 0,
            "deferred_remote_apply_candidates": 0,
            "remote_apply_stop_reason": "end_of_projection",
        }, "receiver scan-frontier settlement local pass")
        settling_pull = require_object(require_object(
            settling_receiver, "reconciliation",
            "receiver scan-frontier settlement sync",
        ), "pull", "receiver scan-frontier settlement reconciliation")
        expect(settling_pull, {
            "disposition": "complete", "round_trips": 1,
            "pages_applied": 1, "inserted_active": 0,
            "inserted_pending": 0, "inserted_quarantined": 0,
            "duplicate_operations": 3, "inserted_payloads": 0,
            "existing_payloads": 3, "has_more": False,
        }, "receiver scan-frontier settlement pull")
        expect(require_object(
            settling_receiver, "remote_apply_pass",
            "receiver scan-frontier settlement sync",
        ), {
            "completed_local_scan_epoch": True,
            "local_scan_seen_path_count": 0,
            "local_scan_resume_after_path": "",
            "local_scan_stop_reason": "end_of_namespace",
            "local_catalog_no_op": 1, "remote_applied": 0,
            "remote_apply_started_after_path": "batch/item-001.txt",
            "remote_apply_resume_after_path": "batch/item-001.txt",
            "remote_apply_wrapped_projection": True,
            "remote_inspected_paths": 3,
            "remote_acknowledged_paths": 3,
            "remote_inspection_sweep_started_after_path":
                "batch/item-001.txt",
            "remote_inspection_sweep_seen_path_count": 3,
            "completed_remote_inspection_sweep": True,
            "remote_inspection_sweep_had_unresolved_paths": False,
            "deferred_remote_inspection_paths": 0,
            "deferred_remote_apply_candidates": 0,
            "remote_apply_stop_reason": "end_of_projection",
        }, "receiver scan-frontier settlement remote apply")
        expect_server(
            settling_source, "receiver", "scan-frontier settlement source server"
        )
        before_settlement = require_object(
            settling_receiver, "before", "receiver scan-frontier settlement"
        )
        after_settlement = require_object(
            settling_receiver, "after", "receiver scan-frontier settlement"
        )
        for stable_field in (
            "catalog_generation", "catalog_entries", "catalog_digest",
            "remote_apply_resume_after_path",
            "replica_generation", "replica_cutpoint_digest",
            "replica_evidence_set_digest", "replica_visible_state_digest",
        ):
            if before_settlement.get(stable_field) != after_settlement.get(
                stable_field
            ):
                fail(
                    "scan-only settlement unexpectedly changed "
                    f"{stable_field}"
                )
        if (
            before_settlement.get("local_scan_seen_chain_digest") ==
            after_settlement.get("local_scan_seen_chain_digest")
        ):
            fail("scan-only settlement did not change its durable scan cutpoint")
        if tree_snapshot(receiver_files) != source_tree:
            fail("scan-only settlement changed the materialized receiver tree")

        source_status = run_json([
            str(replica), "status", "--manifest", str(source_manifest),
        ], label="source status after bounded convergence")
        receiver_status = run_json([
            str(replica), "status", "--manifest", str(receiver_manifest),
        ], label="receiver status after bounded convergence")
        require_replica_equivalence(
            source_status, receiver_status, "bounded convergence"
        )
        first_receiver_cutpoint = status_cutpoint(receiver_status)

        duplicate_receiver, duplicate_source = run_sync_once_session(
            replica, sync, certificates, source_manifest, receiver_manifest,
            "source", "receiver", source_pin, "source-to-receiver-4",
        )
        expect_sync_top(
            duplicate_receiver, "complete_no_op", "receiver", "source",
            "duplicate receiver sync",
        )
        if duplicate_receiver.get("before") != duplicate_receiver.get("after"):
            fail("duplicate sync changed its combined folder cutpoint")
        expect(require_object(
            duplicate_receiver, "local_pass", "duplicate receiver sync"
        ), {
            "used_idle_fast_path": True,
            "local_published": 0, "local_catalog_no_op": 3,
            "remote_applied": 0,
        }, "duplicate receiver local pass")
        duplicate_pull = require_object(require_object(
            duplicate_receiver, "reconciliation", "duplicate receiver sync"
        ), "pull", "duplicate receiver reconciliation")
        expect(duplicate_pull, {
            "disposition": "complete", "round_trips": 1,
            "pages_applied": 1, "inserted_active": 0,
            "inserted_pending": 0, "inserted_quarantined": 0,
            "duplicate_operations": 3, "inserted_payloads": 0,
            "existing_payloads": 3, "has_more": False,
        }, "duplicate receiver pull")
        expect_server(duplicate_source, "receiver", "duplicate source server")
        receiver_status_duplicate = run_json([
            str(replica), "status", "--manifest", str(receiver_manifest),
        ], label="receiver status after duplicate sync")
        if status_cutpoint(receiver_status_duplicate) != first_receiver_cutpoint:
            fail("duplicate sync changed receiver durable state")
        if tree_snapshot(receiver_files) != source_tree:
            fail("duplicate receiver sync changed materialized tree")

        reverse_path = receiver_files / "nested" / "from-receiver.txt"
        reverse_path.parent.mkdir(mode=0o700)
        reverse_path.write_bytes(b"reverse-direction AnonSync sync-once edit\n")
        reverse_publish, source_serves_old_state = run_sync_once_session(
            replica, sync, certificates, source_manifest, receiver_manifest,
            "source", "receiver", source_pin, "receiver-local-publication",
        )
        expect_sync_top(
            reverse_publish, "complete_changed", "receiver", "source",
            "receiver reverse publication sync",
        )
        expect(require_object(
            reverse_publish, "local_pass", "receiver reverse publication sync"
        ), {
            "regular_files": 4, "local_published": 1,
            "local_catalog_no_op": 3, "remote_applied": 0,
        }, "receiver reverse publication local pass")
        reverse_publish_pull = require_object(require_object(
            reverse_publish, "reconciliation",
            "receiver reverse publication sync"
        ), "pull", "receiver reverse publication reconciliation")
        expect(reverse_publish_pull, {
            "disposition": "complete", "duplicate_operations": 3,
            "inserted_payloads": 0, "existing_payloads": 3,
            "has_more": False,
        }, "receiver reverse publication pull")
        expect_server(
            source_serves_old_state, "receiver",
            "source server during receiver publication",
        )
        receiver_tree = tree_snapshot(receiver_files)

        reverse_source, receiver_serves_new_state = run_sync_once_session(
            replica, sync, certificates, receiver_manifest, source_manifest,
            "receiver", "source", receiver_pin, "receiver-to-source-1",
        )
        expect_sync_top(
            reverse_source, "complete_changed", "source", "receiver",
            "source reverse sync",
        )
        expect(require_object(
            reverse_source, "local_pass", "source reverse sync"
        ), {
            "used_idle_fast_path": True,
            "regular_files": 3, "local_published": 0,
            "local_catalog_no_op": 3, "remote_applied": 0,
        }, "source reverse local pass")
        reverse_pull = require_object(require_object(
            reverse_source, "reconciliation", "source reverse sync"
        ), "pull", "source reverse reconciliation")
        expect(reverse_pull, {
            "disposition": "complete", "round_trips": 1,
            "pages_applied": 1, "inserted_quarantined": 0,
            "duplicate_operations": 3, "inserted_payloads": 1,
            "existing_payloads": 3, "has_more": False,
        }, "source reverse pull")
        if reverse_pull.get("inserted_active", 0) + reverse_pull.get(
            "inserted_pending", 0
        ) != 1:
            fail("source reverse pull did not admit the receiver edit")
        expect(require_object(
            reverse_source, "remote_apply_pass", "source reverse sync"
        ), {
            "remote_applied": 1,
            "skipped_conflicted_remote_paths": 0,
            "skipped_tombstone_remote_paths": 0,
        }, "source reverse remote apply")
        expect_server(
            receiver_serves_new_state, "source",
            "receiver server with reverse edit",
        )
        if tree_snapshot(source_files) != receiver_tree:
            fail("source tree differs after reverse sync")

        source_after_reverse = run_json([
            str(replica), "status", "--manifest", str(source_manifest),
        ], label="source status after reverse sync")
        receiver_after_reverse = run_json([
            str(replica), "status", "--manifest", str(receiver_manifest),
        ], label="receiver status after reverse publication")
        require_replica_equivalence(
            source_after_reverse, receiver_after_reverse,
            "reverse convergence",
        )
        source_reverse_cutpoint = status_cutpoint(source_after_reverse)

        reverse_repeat, reverse_repeat_server = run_sync_once_session(
            replica, sync, certificates, receiver_manifest, source_manifest,
            "receiver", "source", receiver_pin, "receiver-to-source-2",
        )
        expect_sync_top(
            reverse_repeat, "complete_no_op", "source", "receiver",
            "reverse duplicate sync",
        )
        if reverse_repeat.get("before") != reverse_repeat.get("after"):
            fail("reverse duplicate sync changed combined cutpoint")
        repeat_pull = require_object(require_object(
            reverse_repeat, "reconciliation", "reverse duplicate sync"
        ), "pull", "reverse duplicate reconciliation")
        expect(repeat_pull, {
            "disposition": "complete", "round_trips": 1,
            "pages_applied": 1, "inserted_active": 0,
            "inserted_pending": 0, "inserted_quarantined": 0,
            "duplicate_operations": 4, "inserted_payloads": 0,
            "existing_payloads": 4, "has_more": False,
        }, "reverse duplicate pull")
        expect_server(
            reverse_repeat_server, "source", "reverse duplicate server"
        )
        source_after_repeat = run_json([
            str(replica), "status", "--manifest", str(source_manifest),
        ], label="source status after reverse duplicate sync")
        if status_cutpoint(source_after_repeat) != source_reverse_cutpoint:
            fail("reverse duplicate sync changed source durable state")

        for manifest, label in (
            (source_manifest, "source final folder no-op"),
            (receiver_manifest, "receiver final folder no-op"),
        ):
            value = run_json([
                str(folder), "run", "--manifest", str(manifest),
            ], label=label)
            expect(value, {
                "used_idle_fast_path": True,
                "local_published": 0, "remote_applied": 0,
                "local_catalog_no_op": 4,
            }, label)
        if (
            tree_snapshot(source_files) != receiver_tree or
            tree_snapshot(receiver_files) != receiver_tree
        ):
            fail("final no-op passes changed converged peer trees")

    print("anonsync sync-once process test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
