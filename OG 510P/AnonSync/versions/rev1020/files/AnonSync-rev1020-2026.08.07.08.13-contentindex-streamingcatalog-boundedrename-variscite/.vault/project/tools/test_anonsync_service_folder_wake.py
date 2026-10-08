#!/usr/bin/env python3
"""Prove inotify wakes the retained service without becoming sync authority.

The service is configured with a sixty-second repair interval and an absent
peer. The lexically higher local actor therefore remains in its retained
inbound role: no outbound cycle can hide a local scan. Nested creation and an
in-place edit must each reach the existing configured-folder convergence pass
within seconds, while the periodic-repair counter stays at zero. A clean restart
must reconstruct the recursive watch set and repeat the behavior.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time
from typing import Any, NoReturn

from test_anonsync_service_configuration_status import (
    linked_peer_configuration,
    require_payload_quarantine_inventory,
    wait_for_status,
    write_private_json,
)
from test_anonsync_service_process import finish_service
from test_anonsync_sync_process import (
    fail,
    generate_tls_fixture,
    init_combined,
    reserve_port,
    run_json,
)


def status_query(sync: Path, socket_path: Path, label: str) -> dict[str, Any]:
    return run_json(
        [
            str(sync),
            "status",
            "--socket",
            str(socket_path),
            "--timeout-milliseconds",
            "1000",
        ],
        label=label,
    )


def require_watcher_health(value: dict[str, Any], label: str) -> dict[str, Any]:
    watcher = value.get("filesystem_watch")
    if not isinstance(watcher, dict):
        fail(f"{label} omitted filesystem_watch: {json.dumps(value, sort_keys=True)}")
    expected = {
        "platform_supported": True,
        "active": True,
        "complete": True,
        "diagnostic": None,
    }
    for key, wanted in expected.items():
        if watcher.get(key) != wanted:
            fail(
                f"{label} watcher field {key!r} was {watcher.get(key)!r}, "
                f"expected {wanted!r}: {json.dumps(value, sort_keys=True)}"
            )
    if watcher.get("watch_count", 0) < 1:
        fail(f"{label} watcher owned no root watch")
    return watcher


def require_counters(value: dict[str, Any], label: str) -> dict[str, Any]:
    counters = value.get("counters")
    if not isinstance(counters, dict):
        fail(f"{label} omitted counters: {json.dumps(value, sort_keys=True)}")
    return counters


def wait_for_wake_repair(
    sync: Path,
    process: subprocess.Popen[str],
    socket_path: Path,
    target: int,
    label: str,
    *,
    timeout: float = 8.0,
) -> tuple[dict[str, Any], float]:
    started = time.monotonic()
    deadline = started + timeout
    last_value: dict[str, Any] | None = None
    last_error = "no status response"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1.0)
            fail(
                f"{label} service exited before wake repair with "
                f"{process.returncode}\nstdout:\n{stdout}\nstderr:\n{stderr}"
            )
        try:
            value = status_query(sync, socket_path, f"{label} status")
            last_value = value
            watcher = require_watcher_health(value, label)
            counters = require_counters(value, label)
            observed = counters.get("filesystem_wake_repairs")
            if not isinstance(observed, int):
                fail(f"{label} wake-repair counter is not an integer")
            if counters.get("periodic_repairs") != 0:
                fail(
                    f"{label} reached a periodic repair before the sixty-second "
                    f"interval: {json.dumps(value, sort_keys=True)}"
                )
            if observed >= target:
                if watcher.get("wake_observations", 0) < target:
                    fail(
                        f"{label} repair count exceeded watcher wake observations: "
                        f"{json.dumps(value, sort_keys=True)}"
                    )
                return value, time.monotonic() - started
        except (FileNotFoundError, OSError, RuntimeError) as error:
            last_error = str(error)
        time.sleep(0.02)
    fail(
        f"{label} did not reach filesystem_wake_repairs={target}; "
        f"last_error={last_error}; last_status="
        f"{json.dumps(last_value, sort_keys=True) if last_value else 'null'}"
    )


def stop_service(
    process: subprocess.Popen[str], label: str
) -> dict[str, Any]:
    process.send_signal(signal.SIGTERM)
    value = finish_service(process, label, timeout=12.0)
    if value.get("stop_reason") != "stop_requested":
        fail(
            f"{label} stopped for {value.get('stop_reason')!r}, expected "
            f"'stop_requested': {json.dumps(value, sort_keys=True)}"
        )
    if value.get("periodic_repairs") != 0:
        fail(
            f"{label} performed a periodic repair despite the sixty-second "
            f"interval: {json.dumps(value, sort_keys=True)}"
        )
    require_watcher_health(value, label)
    return value


def start_service(sync: Path, config: Path) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [str(sync), "run", "--config", str(config)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
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

    with tempfile.TemporaryDirectory(
        prefix="anonsync-service-folder-wake-"
    ) as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        certificates = root / "certificates"
        certificates.mkdir(mode=0o700)
        generate_tls_fixture(certificates, openssl_executable)

        manifest, files_root = init_combined(replica, root / "source", "source")
        run_json(
            [str(folder), "init", "--manifest", str(manifest)],
            label="folder-wake catalog initialization",
        )
        receiver_pin = run_json(
            [
                str(replica),
                "certificate-spki",
                "--certificate",
                str(certificates / "receiver.pem"),
            ],
            label="folder-wake receiver certificate pin",
        )["spki_sha256"]
        run_json(
            [
                str(replica),
                "membership-publish",
                "--manifest",
                str(manifest),
                "--policy-epoch",
                "1",
                "--peer",
                f"receiver:1:{receiver_pin}",
            ],
            label="folder-wake membership publication",
        )

        listen_port = reserve_port()
        absent_remote_port = reserve_port()
        while absent_remote_port == listen_port:
            absent_remote_port = reserve_port()
        runtime = root / "runtime"
        runtime.mkdir(mode=0o700)
        status_socket = runtime / "status.sock"
        configuration = runtime / "linked-peer.json"
        config_value = linked_peer_configuration(
            manifest=manifest,
            certificates=certificates,
            local_device="source",
            remote_device="receiver",
            remote_pin=receiver_pin,
            listen_port=listen_port,
            remote_port=absent_remote_port,
            status_socket=status_socket,
        )
        config_value["service"]["scan_interval_seconds"] = 60
        # Deliberately request the maximum network accept window. The service
        # must still observe its single-threaded inotify owner promptly rather
        # than allowing network polling policy to hide local filesystem work.
        config_value["service"]["accept_poll_milliseconds"] = 60000
        config_value["service"]["maximum_service_runtime_seconds"] = 25
        write_private_json(configuration, config_value)

        process = start_service(sync, configuration)
        try:
            initial = wait_for_status(
                sync,
                process,
                status_socket,
                "source",
                "receiver",
                configuration,
                "folder-wake initial service",
            )
            if initial.get("local_recovery_initiator") is not False:
                fail(
                    "folder-wake proof selected an outbound recovery actor: "
                    + json.dumps(initial, sort_keys=True)
                )
            watcher = require_watcher_health(initial, "initial service")
            counters = require_counters(initial, "initial service")
            if counters.get("initial_repairs") != 1:
                fail(f"initial service did not complete exactly one initial repair")
            expected_initial_payload_cutpoint = {
                "initial_repair_payload_snapshot_handoffs": 1,
                "initial_repair_payload_snapshot_handoff_entries": 0,
                "initial_repair_convergence_snapshot_observations": 0,
                "initial_repair_convergence_mutation_full_scans": 0,
            }
            for field, wanted in expected_initial_payload_cutpoint.items():
                if counters.get(field) != wanted:
                    fail(
                        f"initial service payload cutpoint {field!r} was "
                        f"{counters.get(field)!r}, expected {wanted!r}: "
                        + json.dumps(initial, sort_keys=True)
                    )
            if counters.get("periodic_repairs") != 0:
                fail("initial service unexpectedly completed a periodic repair")
            if counters.get("filesystem_wake_repairs") != 0:
                fail("initial service reported a filesystem wake before mutation")
            if watcher.get("watch_count") != 1:
                fail(
                    "empty folder should begin with exactly one root watch: "
                    + json.dumps(initial, sort_keys=True)
                )
            initial_inventory = initial["payload_quarantine"]["inventory"]
            require_payload_quarantine_inventory(
                initial_inventory, "initial ready service"
            )
            if initial_inventory.get("observation_known") is not True:
                fail(
                    "initial readiness did not retain the complete payload-store "
                    "observation: " + json.dumps(initial, sort_keys=True)
                )

            # Let several 50 ms inbound windows expire. A periodic scan must not
            # occur merely because the service remains idle.
            time.sleep(0.30)
            quiet = status_query(sync, status_socket, "folder-wake quiet status")
            quiet_counters = require_counters(quiet, "quiet service")
            if quiet_counters.get("periodic_repairs") != 0 or quiet_counters.get(
                "filesystem_wake_repairs"
            ) != 0:
                fail(
                    "idle service scanned before either an event or repair interval: "
                    + json.dumps(quiet, sort_keys=True)
                )
            quiet_inventory = quiet["payload_quarantine"]["inventory"]
            require_payload_quarantine_inventory(
                quiet_inventory, "quiet ready service"
            )
            if quiet_inventory.get("observation_known") is not True:
                fail(
                    "status polling lost the initial payload-store observation: "
                    + json.dumps(quiet, sort_keys=True)
                )

            nested = files_root / "burst" / "nested"
            nested.mkdir(parents=True, mode=0o700)
            target = nested / "alpha.txt"
            target.write_bytes(b"first inotify-published payload\n")
            first_status, first_latency = wait_for_wake_repair(
                sync,
                process,
                status_socket,
                1,
                "nested creation wake",
            )
            first_watcher = require_watcher_health(
                first_status, "nested creation wake"
            )
            first_inventory = first_status["payload_quarantine"]["inventory"]
            require_payload_quarantine_inventory(
                first_inventory, "nested creation wake"
            )
            if (
                first_inventory.get("observation_known") is not True
                or first_inventory.get("entry_count") != 0
                or first_inventory.get("total_bytes") != 0
            ):
                fail(
                    "first eligible convergence did not preserve the initial "
                    "exact empty quarantine observation: "
                    + json.dumps(first_status, sort_keys=True)
                )
            if first_watcher.get("watch_count", 0) < 3:
                fail(
                    "nested creation did not rebuild recursive watches: "
                    + json.dumps(first_status, sort_keys=True)
                )
            if first_watcher.get("rebuilds", 0) < 2:
                fail(
                    "nested creation did not report a topology rebuild: "
                    + json.dumps(first_status, sort_keys=True)
                )

            # Drain any coalesced create/close events before attributing the next
            # counter increment to the explicit edit.
            time.sleep(0.20)
            settled = status_query(sync, status_socket, "post-create settled status")
            settled_counters = require_counters(settled, "post-create settled")
            edit_base = settled_counters.get("filesystem_wake_repairs")
            if not isinstance(edit_base, int) or edit_base < 1:
                fail("post-create wake-repair baseline is invalid")

            with target.open("r+b", buffering=0) as stream:
                stream.seek(0)
                stream.write(b"second")
                stream.flush()
                os.fsync(stream.fileno())
            edit_status, edit_latency = wait_for_wake_repair(
                sync,
                process,
                status_socket,
                edit_base + 1,
                "nested edit wake",
            )
            edit_counters = require_counters(edit_status, "nested edit wake")
            first_terminal = stop_service(process, "folder-wake first service")
            process = None

            if first_terminal.get("filesystem_wake_repairs", 0) < edit_base + 1:
                fail(
                    "terminal report lost live wake accounting: "
                    + json.dumps(first_terminal, sort_keys=True)
                )
            live_watcher = edit_status.get("filesystem_watch")
            terminal_watcher = first_terminal.get("filesystem_watch")
            if not isinstance(live_watcher, dict) or not isinstance(
                terminal_watcher, dict
            ):
                fail("live or terminal watcher projection is not an object")
            if set(live_watcher) != set(terminal_watcher):
                fail(
                    "live and terminal watcher schemas drifted: "
                    f"live={sorted(live_watcher)} terminal={sorted(terminal_watcher)}"
                )

            no_op = run_json(
                [str(folder), "run", "--manifest", str(manifest)],
                label="post-wake folder no-op",
            )
            if no_op.get("local_published") != 0:
                fail(
                    "the wake pass did not publish the changed local file: "
                    + json.dumps(no_op, sort_keys=True)
                )
            if no_op.get("catalog_entry_count_after") != 1:
                fail(
                    "the wake pass did not retain exactly one catalog entry: "
                    + json.dumps(no_op, sort_keys=True)
                )
            if no_op.get("local_catalog_no_op") != 1:
                fail(
                    "the post-wake pass did not observe the file as a no-op: "
                    + json.dumps(no_op, sort_keys=True)
                )

            process = start_service(sync, configuration)
            restarted = wait_for_status(
                sync,
                process,
                status_socket,
                "source",
                "receiver",
                configuration,
                "folder-wake restarted service",
            )
            restarted_watcher = require_watcher_health(
                restarted, "restarted service"
            )
            if restarted_watcher.get("watch_count", 0) < 3:
                fail(
                    "restart did not reconstruct recursive watches: "
                    + json.dumps(restarted, sort_keys=True)
                )
            restarted_counters = require_counters(restarted, "restarted service")
            # The private payload store is append-only at this revision. The
            # create and subsequent in-place edit therefore retain two distinct
            # current-byte payload identities even though the catalog contains
            # one current path. Initial repair must hand off that complete
            # two-entry namespace, not confuse catalog cardinality with payload
            # cardinality.
            expected_restart_payload_cutpoint = {
                "initial_repair_payload_snapshot_handoffs": 1,
                "initial_repair_payload_snapshot_handoff_entries": 2,
                "initial_repair_convergence_snapshot_observations": 0,
                "initial_repair_convergence_mutation_full_scans": 0,
            }
            for field, wanted in expected_restart_payload_cutpoint.items():
                if restarted_counters.get(field) != wanted:
                    fail(
                        f"restarted service payload cutpoint {field!r} was "
                        f"{restarted_counters.get(field)!r}, expected {wanted!r}: "
                        + json.dumps(restarted, sort_keys=True)
                    )
            if restarted_counters.get("filesystem_wake_repairs") != 0:
                fail("restart inherited transient wake-repair accounting")

            with target.open("ab", buffering=0) as stream:
                stream.write(b"restart-edit\n")
                stream.flush()
                os.fsync(stream.fileno())
            restart_status, restart_latency = wait_for_wake_repair(
                sync,
                process,
                status_socket,
                1,
                "restart edit wake",
            )
            restart_counters = require_counters(
                restart_status, "restart edit wake"
            )
            if restart_counters.get("periodic_repairs") != 0:
                fail("restart edit was processed by a periodic repair")
            second_terminal = stop_service(process, "folder-wake restarted service")
            process = None
            if second_terminal.get("filesystem_wake_repairs", 0) < 1:
                fail("restart terminal report omitted its wake repair")
        finally:
            if process is not None and process.poll() is None:
                process.kill()
                process.communicate(timeout=2.0)

    print(
        "anonsync service folder-wake process test passed: "
        f"create={first_latency:.3f}s edit={edit_latency:.3f}s "
        f"restart={restart_latency:.3f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
