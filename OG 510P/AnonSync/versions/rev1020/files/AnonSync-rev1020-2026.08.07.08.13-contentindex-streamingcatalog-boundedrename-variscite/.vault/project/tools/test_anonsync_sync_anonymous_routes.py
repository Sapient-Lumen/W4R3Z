#!/usr/bin/env python3
"""Prove the product sync-once command pulls over Tor SOCKS5 and I2P SAM."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
from typing import Any, NoReturn

from test_anonsync_replica_anonymous_routes import (
    I2P_PEER,
    SAM_SESSION_ID,
    TOR_TOKEN,
    VALID_ONION,
    fake_outbound_sam,
    fake_tor_socks5,
    listener_port,
    make_listener,
)
from test_anonsync_replica_cli import (
    expect_fields,
    fail,
    generate_tls_fixture,
    reserve_port,
    run_json,
    wait_until_listening,
)


def require_object(value: dict[str, Any], key: str, label: str) -> dict[str, Any]:
    observed = value.get(key)
    if not isinstance(observed, dict):
        fail(f"{label} field {key!r} is not an object: {value!r}")
    return observed


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


def terminate_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.send_signal(signal.SIGTERM)
    try:
        process.communicate(timeout=2.0)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate(timeout=2.0)


def init_combined(
    replica: Path, root: Path, device: str
) -> tuple[Path, Path]:
    root.mkdir(mode=0o700)
    db = root / "db"
    payload = root / "payload"
    files = root / "files"
    for directory in (db, payload, files):
        directory.mkdir(mode=0o700)
    manifest = db / "deployment.json"
    run_json([
        str(replica), "init", "--manifest", str(manifest),
        "--replica-db", str(db / "replica.sqlite"),
        "--payload-root", str(payload),
        "--effect-db", str(db / "effect.sqlite"),
        "--files-root", str(files),
        "--membership-db", str(db / "membership.sqlite"),
        "--anchor-db", str(db / "anchor.sqlite"),
        "--folder", "sync-anonymous-routes", "--local-device", device,
        "--local-epoch", "1",
    ])
    return manifest, files


def start_source(
    replica: Path,
    manifest: Path,
    certificates: Path,
    port: int,
) -> subprocess.Popen[str]:
    process = subprocess.Popen([
        str(replica), "serve-one", "--manifest", str(manifest),
        "--bind-address", "127.0.0.1", "--port", str(port),
        "--certificate", str(certificates / "sender.pem"),
        "--private-key", str(certificates / "sender.key"),
        "--ca-file", str(certificates / "ca.pem"),
        "--timeout-seconds", "10", "--max-round-trips", "8",
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    wait_until_listening(process, port)
    return process


def client_base(
    sync: Path,
    receiver_manifest: Path,
    certificates: Path,
    sender_pin: str,
) -> list[str]:
    return [
        str(sync), "once", "--manifest", str(receiver_manifest),
        "--remote-device", "sender", "--remote-epoch", "1",
        "--remote-spki", sender_pin,
        "--certificate", str(certificates / "receiver.pem"),
        "--private-key", str(certificates / "receiver.key"),
        "--ca-file", str(certificates / "ca.pem"),
        "--max-round-trips", "8", "--max-runtime-seconds", "180",
    ]


def assert_sync(
    value: dict[str, Any],
    transport: str,
    duplicate_operations: int,
    label: str,
) -> dict[str, Any]:
    expect_fields(value, {
        "command": "once", "terminal_class": "completed",
        "disposition": "complete_changed", "settled": True,
        "bounded_progress": True, "durable_progress": True,
        "local_device_id": "receiver",
        "remote_device_id": "sender", "transport": transport,
        "pull_attempted": True, "remote_apply_attempted": True,
    }, label)
    reconciliation = require_object(value, "reconciliation", label)
    expect_fields(reconciliation, {
        "client_disposition": "pull_completed", "connected": True,
        "handshake_complete": True, "peer_authenticated": True,
        "peer_device_id": "sender", "transport": transport,
        "route_disposition": "connected", "route_negotiated": True,
    }, f"{label} reconciliation")
    pull = require_object(reconciliation, "pull", f"{label} reconciliation")
    expect_fields(pull, {
        "disposition": "complete", "round_trips": 1,
        "pages_applied": 1, "duplicate_operations": duplicate_operations,
        "inserted_payloads": 1, "has_more": False,
    }, f"{label} pull")
    remote = require_object(value, "remote_apply_pass", label)
    expect_fields(remote, {
        "remote_applied": 1, "skipped_conflicted_remote_paths": 0,
        "skipped_tombstone_remote_paths": 0,
    }, f"{label} remote apply")
    return reconciliation


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

    with tempfile.TemporaryDirectory(prefix="anonsync-sync-routes-") as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        certificates = root / "certificates"
        certificates.mkdir(mode=0o700)
        generate_tls_fixture(certificates, openssl_executable)

        source_manifest, source_files = init_combined(
            replica, root / "source", "sender"
        )
        receiver_manifest, receiver_files = init_combined(
            replica, root / "receiver", "receiver"
        )
        run_json([
            str(folder), "init", "--manifest", str(source_manifest),
        ])
        run_json([
            str(folder), "init", "--manifest", str(receiver_manifest),
        ])
        sender_pin = run_json([
            str(replica), "certificate-spki", "--certificate",
            str(certificates / "sender.pem"),
        ])["spki_sha256"]
        receiver_pin = run_json([
            str(replica), "certificate-spki", "--certificate",
            str(certificates / "receiver.pem"),
        ])["spki_sha256"]
        run_json([
            str(replica), "membership-publish", "--manifest",
            str(source_manifest), "--policy-epoch", "1", "--peer",
            f"receiver:1:{receiver_pin}",
        ])

        routes = source_files / "routes"
        routes.mkdir(mode=0o700)
        tor_bytes = b"AnonSync sync-once route proof: Tor\n"
        (routes / "tor.txt").write_bytes(tor_bytes)
        source_pass = run_json([
            str(folder), "run", "--manifest", str(source_manifest),
        ])
        expect_fields(source_pass, {
            "local_published": 1, "remote_applied": 0,
        }, "Tor source publication")

        source_port = reserve_port()
        source = start_source(
            replica, source_manifest, certificates, source_port
        )
        socks = make_listener()
        socks_port = listener_port(socks)
        proxy = fake_tor_socks5(socks, source_port)
        try:
            tor = run_json([
                *client_base(sync, receiver_manifest, certificates, sender_pin),
                "--transport", "tor", "--onion-address", VALID_ONION,
                "--onion-port", "443", "--tor-socks-address", "127.0.0.1",
                "--tor-socks-port", str(socks_port),
                "--tor-isolation-token", TOR_TOKEN,
                "--timeout-seconds", "10",
            ], timeout=30.0)
            tor_server = finish_server(source, "Tor sync source")
        finally:
            terminate_process(source)
        proxy.join()
        tor_reconciliation = assert_sync(tor, "tor_socks5", 0, "Tor sync")
        expect_fields(tor_reconciliation, {
            "route_control_session_created": False,
            "route_control_session_reused": False,
        }, "Tor route state")
        expect_fields(tor_server, {
            "application_disposition": "reconciliation",
            "reconciliation_disposition": "complete",
            "peer_device_id": "receiver",
        }, "Tor sync source")
        if (receiver_files / "routes" / "tor.txt").read_bytes() != tor_bytes:
            fail("Tor sync changed payload bytes")

        i2p_bytes = b"AnonSync sync-once route proof: I2P\n"
        (routes / "i2p.txt").write_bytes(i2p_bytes)
        source_pass = run_json([
            str(folder), "run", "--manifest", str(source_manifest),
        ])
        expect_fields(source_pass, {
            "local_published": 1, "local_catalog_no_op": 1,
            "remote_applied": 0,
        }, "I2P source publication")

        source_port = reserve_port()
        source = start_source(
            replica, source_manifest, certificates, source_port
        )
        sam = make_listener()
        sam_port = listener_port(sam)
        bridge = fake_outbound_sam(sam, source_port)
        try:
            i2p = run_json([
                *client_base(sync, receiver_manifest, certificates, sender_pin),
                "--transport", "i2p", "--i2p-destination", I2P_PEER,
                "--i2p-sam-address", "127.0.0.1", "--i2p-sam-port",
                str(sam_port), "--i2p-session-id", SAM_SESSION_ID,
                "--timeout-seconds", "180",
            ], timeout=30.0)
            i2p_server = finish_server(source, "I2P sync source")
        finally:
            terminate_process(source)
        bridge.join()
        i2p_reconciliation = assert_sync(i2p, "i2p_sam", 1, "I2P sync")
        expect_fields(i2p_reconciliation, {
            "route_control_session_created": True,
            "route_control_session_reused": False,
            "route_numeric_connect_attempts": 2,
            "route_sam_result": "ok",
        }, "I2P route state")
        expect_fields(i2p_server, {
            "application_disposition": "reconciliation",
            "reconciliation_disposition": "complete",
            "peer_device_id": "receiver",
        }, "I2P sync source")
        if (receiver_files / "routes" / "tor.txt").read_bytes() != tor_bytes:
            fail("I2P sync changed the existing Tor payload")
        if (receiver_files / "routes" / "i2p.txt").read_bytes() != i2p_bytes:
            fail("I2P sync changed payload bytes")

    print("anonsync sync-once anonymous route process checks passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 - one diagnostic boundary.
        print(
            f"anonsync sync-once anonymous route process checks failed: {error}",
            flush=True,
        )
        raise
