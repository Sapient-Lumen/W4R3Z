#!/usr/bin/env python3
"""Prove the retained two-direction peer service with real processes.

Two independently bootstrapped peers start together, each binding before its
first outbound cycle. They publish disjoint nested files, reconcile in both
directions through retained listeners, stop at an explicit cycle bound, restart
for edits, propagate deletion without echo, retain absence across fresh process
lifetimes, resurrect the same path causally, survive a real peer-late outage
without restarting the first service, and finally prove SIGTERM produces a
bounded graceful stop.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import tempfile
import time
from typing import Any, NoReturn, Sequence

from test_anonsync_sync_process import (
    fail,
    generate_tls_fixture,
    init_combined,
    linux_port_is_listening,
    reserve_port,
    run_json,
    tree_snapshot,
    unique_json_object_pairs,
)


def service_command(
    sync: Path,
    certificates: Path,
    manifest: Path,
    local_device: str,
    remote_device: str,
    remote_pin: str,
    listen_port: int,
    remote_port: int,
    *,
    maximum_cycles: int | None,
) -> list[str]:
    command = [
        str(sync), "run", "--manifest", str(manifest),
        "--remote-device", remote_device, "--remote-epoch", "1",
        "--remote-spki", remote_pin,
        "--transport", "direct", "--address", "127.0.0.1",
        "--port", str(remote_port),
        "--bind-address", "127.0.0.1", "--listen-port", str(listen_port),
        "--certificate", str(certificates / f"{local_device}.pem"),
        "--private-key", str(certificates / f"{local_device}.key"),
        "--ca-file", str(certificates / "ca.pem"),
        "--timeout-seconds", "3", "--max-runtime-seconds", "15",
        "--max-round-trips", "8", "--max-source-resets", "2",
        "--scan-interval-seconds", "1",
        "--retry-initial-seconds", "1",
        "--retry-maximum-seconds", "2",
        "--accept-poll-milliseconds", "50",
        "--inbound-timeout-seconds", "2",
        "--inbound-max-round-trips", "7",
        "--max-service-runtime-seconds", "30",
    ]
    if maximum_cycles is not None:
        command.extend(["--max-cycles", str(maximum_cycles)])
    return command


def finish_service(
    process: subprocess.Popen[str], label: str, *, timeout: float = 40.0
) -> dict[str, Any]:
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.send_signal(signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=8.0)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate(timeout=2.0)
        fail(
            f"{label} exceeded its bound (return {process.returncode})\n"
            f"stdout:\n{stdout}\nstderr:\n{stderr}"
        )
    if process.returncode != 0:
        fail(
            f"{label} failed with {process.returncode}\n"
            f"stdout:\n{stdout}\nstderr:\n{stderr}"
        )
    if stderr:
        fail(f"{label} wrote diagnostics on success: {stderr}")
    try:
        value = json.loads(
            stdout, object_pairs_hook=unique_json_object_pairs
        )
    except (json.JSONDecodeError, ValueError) as error:
        fail(f"{label} did not emit one JSON object: {error}: {stdout}")
    if not isinstance(value, dict):
        fail(f"{label} JSON is not an object")
    return value


def expect_service(
    value: dict[str, Any], local: str, remote: str, stop_reason: str,
    label: str,
) -> None:
    expected = {
        "command": "run",
        "terminal_class": "completed",
        "stop_reason": stop_reason,
        "listener_started": True,
        "local_device_id": local,
        "remote_device_id": remote,
        "transport": "direct_tcp",
    }
    for key, wanted in expected.items():
        if value.get(key) != wanted:
            fail(
                f"{label} field {key!r} was {value.get(key)!r}, expected "
                f"{wanted!r}: {json.dumps(value, sort_keys=True)}"
            )
    inbound = value.get("inbound")
    if not isinstance(inbound, dict):
        fail(f"{label} omitted inbound summary")
    service_limits = value.get("service_limits")
    if not isinstance(service_limits, dict):
        fail(f"{label} omitted service limits")
    expected_limits = {
        "stage_timeout_seconds": 3,
        "max_round_trips": 8,
        "inbound_stage_timeout_seconds": 2,
        "inbound_max_round_trips": 7,
    }
    for key, wanted in expected_limits.items():
        if service_limits.get(key) != wanted:
            fail(
                f"{label} effective limit {key!r} was "
                f"{service_limits.get(key)!r}, expected {wanted!r}: "
                f"{json.dumps(value, sort_keys=True)}"
            )
    if stop_reason == "maximum_cycles_reached":
        if value.get("cycles_attempted") != 5:
            fail(f"{label} did not execute its five configured cycles: {json.dumps(value, sort_keys=True)}")
        if value.get("cycles_complete") != 5:
            fail(
                f"{label} did not complete all five sync cycles: "
                f"{json.dumps(value, sort_keys=True)}"
            )
        if value.get("cycles_failed") != 0:
            fail(
                f"{label} reported a failed sync cycle: "
                f"{json.dumps(value, sort_keys=True)}"
            )
        if inbound.get("reconciliation_sessions", 0) < 1:
            fail(f"{label} retained listener served no reconciliation: {json.dumps(value, sort_keys=True)}")


def run_pair(
    sync: Path,
    certificates: Path,
    source_manifest: Path,
    receiver_manifest: Path,
    source_pin: str,
    receiver_pin: str,
    *,
    label: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    source_port = reserve_port()
    receiver_port = reserve_port()
    while receiver_port == source_port:
        receiver_port = reserve_port()
    source = subprocess.Popen(
        service_command(
            sync, certificates, source_manifest, "source", "receiver",
            receiver_pin, source_port, receiver_port, maximum_cycles=5,
        ),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    receiver = subprocess.Popen(
        service_command(
            sync, certificates, receiver_manifest, "receiver", "source",
            source_pin, receiver_port, source_port, maximum_cycles=5,
        ),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    try:
        source_value = finish_service(source, f"{label} source service")
        receiver_value = finish_service(
            receiver, f"{label} receiver service"
        )
    finally:
        for process in (source, receiver):
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=2.0)
    expect_service(
        source_value, "source", "receiver", "maximum_cycles_reached",
        f"{label} source service",
    )
    expect_service(
        receiver_value, "receiver", "source", "maximum_cycles_reached",
        f"{label} receiver service",
    )
    if source_value.get("terminal_handoff_drain_attempted") is not False:
        fail(f"{label} higher actor unexpectedly entered terminal drain")
    if (
        receiver_value.get("terminal_handoff_drain_attempted") is not True
        or receiver_value.get("terminal_handoff_drained") is not True
    ):
        fail(
            f"{label} recovery initiator did not drain the peer's final pull: "
            f"{json.dumps(receiver_value, sort_keys=True)}"
        )
    if receiver_value.get("terminal_handoff_drain_deadline_reached") is not False:
        fail(f"{label} terminal handoff drain reached its deadline")
    return source_value, receiver_value


def wait_for_service_listener(
    process: subprocess.Popen[str], port: int, label: str
) -> None:
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1.0)
            fail(
                f"{label} exited before listening with {process.returncode}\n"
                f"stdout:\n{stdout}\nstderr:\n{stderr}"
            )
        if linux_port_is_listening(port):
            return
        time.sleep(0.02)
    fail(f"{label} did not expose its retained listener")


def wait_for_service_status_socket(
    process: subprocess.Popen[str], socket_path: Path, label: str
) -> None:
    """Wait for the local control plane, not merely the public listener.

    ``SyncReplicaPeerServiceOwner`` can expose its network listener before the
    configured status server has finished binding. Tests that issue an
    owner-only stop must therefore prove the status socket itself is present;
    listener readiness is not a control-plane readiness witness.
    """
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1.0)
            fail(
                f"{label} exited before its status socket was ready with "
                f"{process.returncode}\nstdout:\n{stdout}\nstderr:\n{stderr}"
            )
        try:
            observed = socket_path.lstat()
        except FileNotFoundError:
            time.sleep(0.02)
            continue
        if stat.S_ISLNK(observed.st_mode):
            fail(f"{label} status socket is a symbolic link: {socket_path}")
        if not stat.S_ISSOCK(observed.st_mode):
            fail(f"{label} status path is not a socket: {socket_path}")
        mode = stat.S_IMODE(observed.st_mode)
        if mode != 0o600:
            fail(
                f"{label} status socket mode was {mode:o}, expected 600: "
                f"{socket_path}"
            )
        return
    fail(f"{label} did not expose its owner-only status socket")


def wait_for_tree_convergence(
    left: Path, right: Path, required_relative_path: str, label: str,
    *, timeout: float = 20.0,
) -> None:
    deadline = time.monotonic() + timeout
    last_left: dict[str, str] = {}
    last_right: dict[str, str] = {}
    while time.monotonic() < deadline:
        last_left = tree_snapshot(left)
        last_right = tree_snapshot(right)
        if (
            last_left == last_right
            and required_relative_path in last_left
        ):
            return
        time.sleep(0.05)
    fail(
        f"{label} did not converge before its deadline: "
        f"left={last_left}, right={last_right}"
    )


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

    with tempfile.TemporaryDirectory(prefix="anonsync-service-process-") as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        certificates = root / "certificates"
        certificates.mkdir(mode=0o700)
        generate_tls_fixture(certificates, openssl_executable)

        source_manifest, source_files = init_combined(
            replica, root / "source", "source"
        )
        receiver_manifest, receiver_files = init_combined(
            replica, root / "receiver", "receiver"
        )
        run_json([
            str(folder), "init", "--manifest", str(source_manifest),
        ], label="source service folder catalog init")
        run_json([
            str(folder), "init", "--manifest", str(receiver_manifest),
        ], label="receiver service folder catalog init")

        source_pin = run_json([
            str(replica), "certificate-spki", "--certificate",
            str(certificates / "source.pem"),
        ], label="source service certificate pin")["spki_sha256"]
        receiver_pin = run_json([
            str(replica), "certificate-spki", "--certificate",
            str(certificates / "receiver.pem"),
        ], label="receiver service certificate pin")["spki_sha256"]
        run_json([
            str(replica), "membership-publish", "--manifest",
            str(source_manifest), "--policy-epoch", "1", "--peer",
            f"receiver:1:{receiver_pin}",
        ], label="source service membership publication")
        run_json([
            str(replica), "membership-publish", "--manifest",
            str(receiver_manifest), "--policy-epoch", "1", "--peer",
            f"source:1:{source_pin}",
        ], label="receiver service membership publication")

        source_nested = source_files / "source-side" / "nested"
        receiver_nested = receiver_files / "receiver-side" / "nested"
        source_nested.mkdir(parents=True, mode=0o700)
        receiver_nested.mkdir(parents=True, mode=0o700)
        (source_nested / "alpha.txt").write_bytes(
            b"retained-service source payload\n"
        )
        (receiver_nested / "beta.txt").write_bytes(
            b"retained-service receiver payload\n"
        )

        run_pair(
            sync, certificates, source_manifest, receiver_manifest,
            source_pin, receiver_pin, label="initial",
        )
        source_tree = tree_snapshot(source_files)
        receiver_tree = tree_snapshot(receiver_files)
        if source_tree != receiver_tree or len(source_tree) != 2:
            fail(
                "simultaneous retained services did not converge both "
                f"nested files: source={source_tree}, receiver={receiver_tree}"
            )

        edited = source_files / "source-side" / "nested" / "alpha.txt"
        edited.write_bytes(b"retained-service source payload revision two\n")
        run_pair(
            sync, certificates, source_manifest, receiver_manifest,
            source_pin, receiver_pin, label="restart-edit",
        )
        source_tree = tree_snapshot(source_files)
        receiver_tree = tree_snapshot(receiver_files)
        if source_tree != receiver_tree or len(source_tree) != 2:
            fail("service restart did not converge the source edit")
        if (receiver_files / "source-side" / "nested" / "alpha.txt").read_bytes() != edited.read_bytes():
            fail("receiver did not materialize the edited source payload")

        deleted_relative = "receiver-side/nested/beta.txt"
        deleted_on_receiver = receiver_files / deleted_relative
        deleted_on_source = source_files / deleted_relative
        deleted_on_receiver.unlink()
        run_pair(
            sync, certificates, source_manifest, receiver_manifest,
            source_pin, receiver_pin, label="delete",
        )
        if deleted_on_receiver.exists() or deleted_on_source.exists():
            fail("retained services did not propagate a cataloged file deletion")
        source_tree = tree_snapshot(source_files)
        receiver_tree = tree_snapshot(receiver_files)
        if source_tree != receiver_tree or len(source_tree) != 1:
            fail(
                "deletion convergence left divergent trees: "
                f"source={source_tree}, receiver={receiver_tree}"
            )

        run_pair(
            sync, certificates, source_manifest, receiver_manifest,
            source_pin, receiver_pin, label="delete-restart",
        )
        if deleted_on_receiver.exists() or deleted_on_source.exists():
            fail("fresh service lifetimes resurrected a durably deleted path")

        resurrection = b"same path recreated after retained tombstone\n"
        deleted_on_source.write_bytes(resurrection)
        run_pair(
            sync, certificates, source_manifest, receiver_manifest,
            source_pin, receiver_pin, label="resurrection",
        )
        if (
            deleted_on_source.read_bytes() != resurrection
            or deleted_on_receiver.read_bytes() != resurrection
            or tree_snapshot(source_files) != tree_snapshot(receiver_files)
        ):
            fail("same-path resurrection did not converge as a causal successor")

        # Keep the deterministic recovery initiator alive while its peer is
        # absent, then start the peer later. The first process must reconnect
        # under bounded backoff and complete the reverse pull without being
        # restarted. This is the minimum honest outage behavior for a retained
        # Resilio-replacement service.
        outage_relative = "receiver-side/offline/gamma.txt"
        outage_file = receiver_files / outage_relative
        outage_file.parent.mkdir(parents=True, mode=0o700)
        outage_file.write_bytes(b"published while the peer was offline\n")
        source_port = reserve_port()
        receiver_port = reserve_port()
        while receiver_port == source_port:
            receiver_port = reserve_port()

        receiver_outage = subprocess.Popen(
            service_command(
                sync, certificates, receiver_manifest, "receiver", "source",
                source_pin, receiver_port, source_port, maximum_cycles=None,
            ),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        source_late: subprocess.Popen[str] | None = None
        try:
            wait_for_service_listener(
                receiver_outage, receiver_port,
                "outage recovery initiator service",
            )
            # The remote port is reserved but not listening. Leave enough time
            # for at least one actual failed outbound attempt and backoff turn.
            time.sleep(2.2)
            if receiver_outage.poll() is not None:
                stdout, stderr = receiver_outage.communicate(timeout=1.0)
                fail(
                    "outage recovery initiator exited before its peer joined "
                    f"with {receiver_outage.returncode}\nstdout:\n{stdout}"
                    f"\nstderr:\n{stderr}"
                )

            source_late = subprocess.Popen(
                service_command(
                    sync, certificates, source_manifest, "source", "receiver",
                    receiver_pin, source_port, receiver_port,
                    maximum_cycles=None,
                ),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            wait_for_service_listener(
                source_late, source_port, "late peer service",
            )
            wait_for_tree_convergence(
                source_files, receiver_files, outage_relative,
                "peer-late outage recovery",
            )
            receiver_outage.send_signal(signal.SIGTERM)
            source_late.send_signal(signal.SIGTERM)
            receiver_outage_value = finish_service(
                receiver_outage, "outage recovery initiator stop",
            )
            source_late_value = finish_service(
                source_late, "late peer stop",
            )
        finally:
            for process in (receiver_outage, source_late):
                if process is not None and process.poll() is None:
                    process.kill()
                    process.communicate(timeout=2.0)

        expect_service(
            receiver_outage_value, "receiver", "source", "stop_requested",
            "outage recovery initiator service",
        )
        expect_service(
            source_late_value, "source", "receiver", "stop_requested",
            "late peer service",
        )
        if receiver_outage_value.get("cycles_failed", 0) < 1:
            fail(
                "outage recovery initiator did not record the absent-peer "
                f"failure: {json.dumps(receiver_outage_value, sort_keys=True)}"
            )
        if receiver_outage_value.get("cycles_complete", 0) < 1:
            fail(
                "outage recovery initiator never recovered a complete cycle: "
                f"{json.dumps(receiver_outage_value, sort_keys=True)}"
            )
        if source_late_value.get("cycles_complete", 0) < 1:
            fail(
                "late peer never completed the reverse handoff cycle: "
                f"{json.dumps(source_late_value, sort_keys=True)}"
            )
        if (source_files / outage_relative).read_bytes() != outage_file.read_bytes():
            fail("late peer did not materialize the offline receiver payload")

        # A service with an unavailable remote still owns its listener and exits
        # cleanly after SIGTERM. The current bounded outbound cycle may finish
        # before the stop predicate is observed; that is deliberate.
        listen_port = reserve_port()
        absent_remote_port = reserve_port()
        while absent_remote_port == listen_port:
            absent_remote_port = reserve_port()
        stopping = subprocess.Popen(
            service_command(
                sync, certificates, source_manifest, "source", "receiver",
                receiver_pin, listen_port, absent_remote_port,
                maximum_cycles=None,
            ),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            wait_for_service_listener(stopping, listen_port, "stopping service")
            stopping.send_signal(signal.SIGTERM)
            stopped = finish_service(
                stopping, "SIGTERM service", timeout=12.0
            )
        finally:
            if stopping.poll() is None:
                stopping.kill()
                stopping.communicate(timeout=2.0)
        expect_service(
            stopped, "source", "receiver", "stop_requested",
            "SIGTERM service",
        )

    print("anonsync retained peer service process test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
