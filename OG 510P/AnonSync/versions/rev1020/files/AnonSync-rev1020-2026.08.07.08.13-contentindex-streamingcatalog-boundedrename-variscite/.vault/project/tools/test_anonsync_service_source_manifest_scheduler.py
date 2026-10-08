#!/usr/bin/env python3
"""Prove source-manifest preparation continues after its requester exits.

One shipped reconciliation request discovers an exact large-file manifest
obligation and pays the first bounded 32 MiB pulse.  The retained linked-peer
service must finish the same process-local projection through bounded local
owner turns without a connected peer, preserve control-plane responsiveness,
and let a fresh requester reuse the completed manifest without another
preparing response.
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
from typing import Any

from test_anonsync_service_configuration_status import (
    linked_peer_configuration,
    require_payload_operator_status,
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
    unique_json_object_pairs,
)


SOURCE_STEP_BYTES = 32 * 1024 * 1024
PAYLOAD_BYTES = 2 * SOURCE_STEP_BYTES + 4097


def write_repeated_pattern(path: Path, size: int, pattern: bytes) -> None:
    if not pattern:
        fail("source-manifest scheduler pattern must be nonempty")
    remaining = size
    with path.open("wb") as stream:
        while remaining:
            block_size = min(1024 * 1024, remaining)
            repetitions = (block_size + len(pattern) - 1) // len(pattern)
            stream.write((pattern * repetitions)[:block_size])
            remaining -= block_size


def require_source_scheduler_counters(
    value: dict[str, Any], label: str, *, nested: bool
) -> dict[str, int]:
    source: Any = value.get("counters") if nested else value
    if not isinstance(source, dict):
        fail(f"{label} omitted source scheduler counters")
    expected = {
        "source_manifest_projection_scheduler_steps": 2,
        "source_manifest_projection_progress_steps": 1,
        "source_manifest_projection_completions": 1,
        "source_manifest_projection_payload_unavailable": 0,
        "source_manifest_projection_restarts": 0,
        "source_manifest_projection_hashed_bytes": SOURCE_STEP_BYTES + 4097,
    }
    observed: dict[str, int] = {}
    for name, wanted in expected.items():
        member = source.get(name)
        if member != wanted:
            fail(
                f"{label} counter {name!r} was {member!r}, expected "
                f"{wanted}: {json.dumps(value, sort_keys=True)}"
            )
        observed[name] = member
    yields = source.get("source_manifest_projection_ordinary_turn_yields")
    if not isinstance(yields, int) or yields < 1 or yields > 2:
        fail(
            f"{label} did not preserve an ordinary owner turn between "
            f"source hash pulses: {yields!r}"
        )
    observed["source_manifest_projection_ordinary_turn_yields"] = yields
    return observed


def wait_for_source_scheduler_completion(
    sync: Path,
    process: subprocess.Popen[str],
    socket_path: Path,
) -> dict[str, Any]:
    deadline = time.monotonic() + 30.0
    last: dict[str, Any] | None = None
    last_error = "no status response"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1.0)
            fail(
                "source-manifest service exited before local completion with "
                f"{process.returncode}\nstdout:\n{stdout}\nstderr:\n{stderr}"
            )
        try:
            value = run_json(
                [
                    str(sync), "status", "--socket", str(socket_path),
                    "--timeout-milliseconds", "1000",
                ],
                label="source-manifest scheduler status",
                timeout=3.0,
            )
            last = value
            require_payload_operator_status(
                value, "source-manifest scheduler service"
            )
            if value.get("pid") != process.pid:
                fail("source-manifest scheduler status changed serving PID")
            projection = value.get("source_manifest_projection")
            counters = value.get("counters")
            if not isinstance(projection, dict) or not isinstance(counters, dict):
                fail("source-manifest status omitted canonical domains")
            if (
                projection.get("pending") is False
                and counters.get("source_manifest_projection_scheduler_steps")
                == 2
            ):
                if value.get("ready") is not True:
                    fail("source-manifest completion lost service readiness")
                require_source_scheduler_counters(
                    value, "source-manifest live status", nested=True
                )
                return value
            last_error = json.dumps(value, sort_keys=True)
        except (FileNotFoundError, OSError, RuntimeError) as error:
            last_error = str(error)
        time.sleep(0.02)
    fail(
        "source-manifest scheduler did not finish its peer-independent work: "
        + (
            json.dumps(last, sort_keys=True)
            if last is not None
            else last_error
        )
    )


def reconcile_once(
    replica: Path,
    manifest: Path,
    certificates: Path,
    source_pin: str,
    port: int,
    label: str,
) -> dict[str, Any]:
    command = [
        str(replica), "reconcile-pull", "--manifest", str(manifest),
        "--remote-device", "source", "--remote-epoch", "1",
        "--remote-spki", source_pin,
        "--address", "127.0.0.1", "--port", str(port),
        "--certificate", str(certificates / "receiver.pem"),
        "--private-key", str(certificates / "receiver.key"),
        "--ca-file", str(certificates / "ca.pem"),
        "--timeout-seconds", "15", "--max-round-trips", "1",
        "--max-source-resets", "1",
    ]
    completed = subprocess.run(
        command, check=False, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, timeout=45.0,
    )
    try:
        value = json.loads(
            completed.stdout, object_pairs_hook=unique_json_object_pairs
        )
    except (json.JSONDecodeError, ValueError) as error:
        fail(
            f"{label} did not emit one strict JSON object: {error}\n"
            f"command: {' '.join(command)}\nstdout:\n{completed.stdout}"
            f"stderr:\n{completed.stderr}"
        )
    if not isinstance(value, dict):
        fail(f"{label} JSON is not an object")
    preparing = value.get("pull_disposition") == "source_payload_preparing"
    expected_returncode = 2 if preparing else 0
    if completed.returncode != expected_returncode:
        fail(
            f"{label} returned {completed.returncode}, expected "
            f"{expected_returncode}: {json.dumps(value, sort_keys=True)}\n"
            f"stderr:\n{completed.stderr}"
        )
    if completed.stderr:
        fail(f"{label} wrote diagnostics: {completed.stderr}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replica", required=True, type=Path)
    parser.add_argument("--folder", required=True, type=Path)
    parser.add_argument("--sync", required=True, type=Path)
    args = parser.parse_args()
    replica = args.replica.resolve(strict=True)
    folder = args.folder.resolve(strict=True)
    sync = args.sync.resolve(strict=True)
    openssl = shutil.which("openssl")
    if openssl is None:
        fail("openssl executable is unavailable")

    with tempfile.TemporaryDirectory(
        prefix="anonsync-source-manifest-scheduler-service-"
    ) as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        certificates = root / "certificates"
        certificates.mkdir(mode=0o700)
        generate_tls_fixture(certificates, openssl)

        source_manifest, source_files = init_combined(
            replica, root / "source", "source", PAYLOAD_BYTES
        )
        receiver_manifest, _ = init_combined(
            replica, root / "receiver", "receiver", PAYLOAD_BYTES
        )
        run_json(
            [str(folder), "init", "--manifest", str(source_manifest)],
            label="source-manifest source folder init",
        )
        run_json(
            [str(folder), "init", "--manifest", str(receiver_manifest)],
            label="source-manifest receiver folder init",
        )
        source_pin = run_json(
            [
                str(replica), "certificate-spki", "--certificate",
                str(certificates / "source.pem"),
            ],
            label="source-manifest source certificate pin",
        )["spki_sha256"]
        receiver_pin = run_json(
            [
                str(replica), "certificate-spki", "--certificate",
                str(certificates / "receiver.pem"),
            ],
            label="source-manifest receiver certificate pin",
        )["spki_sha256"]
        run_json(
            [
                str(replica), "membership-publish", "--manifest",
                str(source_manifest), "--policy-epoch", "1", "--peer",
                f"receiver:1:{receiver_pin}",
            ],
            label="source-manifest source membership",
        )
        run_json(
            [
                str(replica), "membership-publish", "--manifest",
                str(receiver_manifest), "--policy-epoch", "1", "--peer",
                f"source:1:{source_pin}",
            ],
            label="source-manifest receiver membership",
        )

        payload_path = source_files / "media" / "source-large.bin"
        payload_path.parent.mkdir(mode=0o700)
        write_repeated_pattern(
            payload_path, PAYLOAD_BYTES,
            b"AnonSync source-local content-defined scheduler proof\n",
        )
        published = run_json(
            [str(folder), "run", "--manifest", str(source_manifest)],
            label="source-manifest source publication",
            timeout=120.0,
        )
        if (
            published.get("terminal_class") != "completed"
            or published.get("regular_files") != 1
            or published.get("local_published") != 1
        ):
            fail(
                "source-manifest fixture was not published exactly: "
                f"{json.dumps(published, sort_keys=True)}"
            )

        runtime = root / "runtime"
        runtime.mkdir(mode=0o700)
        status_socket = runtime / "status.sock"
        config = runtime / "linked-peer.json"
        listen_port = reserve_port()
        remote_port = reserve_port()
        while remote_port == listen_port:
            remote_port = reserve_port()
        config_value = linked_peer_configuration(
            manifest=source_manifest,
            certificates=certificates,
            local_device="source",
            remote_device="receiver",
            remote_pin=receiver_pin,
            listen_port=listen_port,
            remote_port=remote_port,
            status_socket=status_socket,
        )
        config_value["service"]["maximum_service_runtime_seconds"] = 60
        config_value["service"]["inbound_max_round_trips"] = 8
        write_private_json(config, config_value)

        environment = os.environ.copy()
        environment.pop("NOTIFY_SOCKET", None)
        process = subprocess.Popen(
            [str(sync), "run", "--config", str(config)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=environment,
        )
        terminal: dict[str, Any] | None = None
        try:
            initial = wait_for_status(
                sync, process, status_socket, "source", "receiver", config,
                "source-manifest scheduler service",
            )
            if initial.get("pid") != process.pid:
                fail("initial source-manifest status changed PID")

            discovery = reconcile_once(
                replica, receiver_manifest, certificates, source_pin,
                listen_port, "source-manifest discovery pull",
            )
            expected_discovery = {
                "command": "reconcile-pull",
                "disposition": "pull_completed",
                "pull_disposition": "source_payload_preparing",
                "peer_authenticated": True,
                "peer_device_id": "source",
                "round_trips": 1,
                "source_payload_preparing_responses": 1,
                "pages_applied": 0,
                "staged_payload_ranges": 0,
                "staged_payload_bytes": 0,
                "has_more": True,
            }
            for key, wanted in expected_discovery.items():
                if discovery.get(key) != wanted:
                    fail(
                        f"source-manifest discovery field {key!r} was "
                        f"{discovery.get(key)!r}, expected {wanted!r}: "
                        f"{json.dumps(discovery, sort_keys=True)}"
                    )

            completed = wait_for_source_scheduler_completion(
                sync, process, status_socket
            )
            if completed.get("payload_integrity", {}).get("state") != "healthy":
                fail("source-local manifest work entered integrity degradation")

            replay = reconcile_once(
                replica, receiver_manifest, certificates, source_pin,
                listen_port, "source-manifest completed-cache replay",
            )
            expected_replay = {
                "command": "reconcile-pull",
                "disposition": "pull_completed",
                "pull_disposition": "round_trip_limit_reached",
                "peer_authenticated": True,
                "peer_device_id": "source",
                "round_trips": 1,
                "source_payload_preparing_responses": 0,
                "pages_applied": 0,
                "staged_payload_ranges": 16,
                "staged_payload_bytes": SOURCE_STEP_BYTES * 2,
                "payload_total_size_bytes": PAYLOAD_BYTES,
                "payload_next_offset_bytes": SOURCE_STEP_BYTES * 2,
                "has_more": True,
            }
            for key, wanted in expected_replay.items():
                if replay.get(key) != wanted:
                    fail(
                        f"source-manifest replay field {key!r} was "
                        f"{replay.get(key)!r}, expected {wanted!r}: "
                        f"{json.dumps(replay, sort_keys=True)}"
                    )

            after_replay = run_json(
                [
                    str(sync), "status", "--socket", str(status_socket),
                    "--timeout-milliseconds", "1000",
                ],
                label="source-manifest replay status",
            )
            require_payload_operator_status(
                after_replay, "source-manifest replay service"
            )
            require_source_scheduler_counters(
                after_replay, "source-manifest replay status", nested=True
            )
            if after_replay.get("pid") != process.pid:
                fail("fresh source-manifest requester changed daemon PID")

            stop = run_json(
                [str(sync), "stop", "--socket", str(status_socket)],
                label="source-manifest owner drain",
            )
            if (
                stop.get("schema") != "anonsync.local-stop.response.v1"
                or stop.get("server_pid") != process.pid
                or stop.get("stop_mode") != "drain"
            ):
                fail(
                    "source-manifest owner drain response was not exact: "
                    f"{json.dumps(stop, sort_keys=True)}"
                )
            terminal = finish_service(
                process, "source-manifest scheduler service", timeout=15.0
            )
        finally:
            if process.poll() is None:
                process.send_signal(signal.SIGTERM)
                try:
                    process.communicate(timeout=5.0)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate(timeout=2.0)

        if terminal is None:
            fail("source-manifest service emitted no terminal report")
        if terminal.get("stop_reason") != "local_stop_requested":
            fail(
                "source-manifest service did not stop through owner drain: "
                f"{json.dumps(terminal, sort_keys=True)}"
            )
        final_projection = terminal.get("source_manifest_projection")
        if not isinstance(final_projection, dict) or (
            final_projection.get("pending") is not False
        ):
            fail("terminal report lost settled source-manifest state")
        require_source_scheduler_counters(
            terminal, "source-manifest terminal report", nested=False
        )
        if status_socket.exists():
            fail("source-manifest service left its control socket behind")

    print(
        "source-local manifest scheduler process test passed "
        "(one peer discovery, two local pulses, fresh-session reuse)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
