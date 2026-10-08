#!/usr/bin/env python3
"""Prove receiver-local terminal SHA-256 completion in the retained daemon.

A test-only fixture leaves one exact completed staged prefix with its canonical
whole-target verification deliberately deferred.  No peer process is started.
The shipping linked-peer daemon must discover that durable obligation during
its ordinary initial complete payload observation, advance it in bounded local
pulses separated by ordinary owner turns, publish the digest-named payload, and
remain controllable and ready throughout.
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
)


TERMINAL_STEP_BYTES = 32 * 1024 * 1024
PAYLOAD_BYTES = 2 * TERMINAL_STEP_BYTES + 4097


def require_scheduler_counters(
    value: dict[str, Any], label: str, *, nested: bool
) -> dict[str, int]:
    source: Any = value.get("counters") if nested else value
    if not isinstance(source, dict):
        fail(f"{label} omitted scheduler counters")
    expected = {
        "payload_terminal_verification_scheduler_steps": 3,
        "payload_terminal_verification_progress_steps": 2,
        "payload_terminal_verification_completions": 1,
        "payload_terminal_verification_insertions": 1,
        "payload_terminal_verification_reconciliations": 0,
        "payload_terminal_verification_hashed_bytes": PAYLOAD_BYTES,
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
    yields = source.get(
        "payload_terminal_verification_ordinary_turn_yields"
    )
    if not isinstance(yields, int) or yields < 2 or yields > 3:
        fail(
            f"{label} did not preserve an ordinary owner turn between local "
            f"hash pulses: {yields!r}"
        )
    observed["payload_terminal_verification_ordinary_turn_yields"] = yields
    return observed


def wait_for_scheduler_completion(
    sync: Path,
    process: subprocess.Popen[str],
    socket_path: Path,
    digest: str,
    payload_path: Path,
) -> dict[str, Any]:
    deadline = time.monotonic() + 30.0
    last: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1.0)
            fail(
                "terminal-verification service exited before local completion "
                f"with {process.returncode}\nstdout:\n{stdout}\nstderr:\n{stderr}"
            )
        try:
            value = run_json(
                [
                    str(sync), "status", "--socket", str(socket_path),
                    "--timeout-milliseconds", "1000",
                ],
                label="terminal-verification scheduler status",
                timeout=3.0,
            )
            last = value
            require_payload_operator_status(
                value, "terminal-verification scheduler service"
            )
            if value.get("pid") != process.pid:
                fail("terminal-verification status changed serving PID")
            terminal = value.get("payload_terminal_verification")
            counters = value.get("counters")
            if not isinstance(terminal, dict) or not isinstance(counters, dict):
                fail("terminal-verification status omitted canonical domains")
            if (
                terminal.get("observation_known") is True
                and terminal.get("pending_entry_count") == 0
                and counters.get(
                    "payload_terminal_verification_scheduler_steps"
                ) == 3
            ):
                if value.get("ready") is not True:
                    fail("terminal-verification completion lost service readiness")
                require_scheduler_counters(
                    value, "terminal-verification live status", nested=True
                )
                if not payload_path.is_file() or payload_path.is_symlink():
                    fail("terminal-verification scheduler did not publish payload")
                if payload_path.stat().st_size != PAYLOAD_BYTES:
                    fail("published terminal-verification payload size drifted")
                if payload_path.name != digest:
                    fail("published terminal-verification payload name drifted")
                return value
        except (FileNotFoundError, OSError, RuntimeError):
            pass
        time.sleep(0.02)
    fail(
        "terminal-verification scheduler did not finish its local durable work: "
        f"{json.dumps(last, sort_keys=True) if last is not None else 'no status'}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replica", required=True, type=Path)
    parser.add_argument("--folder", required=True, type=Path)
    parser.add_argument("--sync", required=True, type=Path)
    parser.add_argument("--fixture", required=True, type=Path)
    args = parser.parse_args()
    replica = args.replica.resolve(strict=True)
    folder = args.folder.resolve(strict=True)
    sync = args.sync.resolve(strict=True)
    fixture = args.fixture.resolve(strict=True)
    openssl = shutil.which("openssl")
    if openssl is None:
        fail("openssl executable is unavailable")

    with tempfile.TemporaryDirectory(
        prefix="anonsync-terminal-verification-service-"
    ) as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        certificates = root / "certificates"
        certificates.mkdir(mode=0o700)
        generate_tls_fixture(certificates, openssl)

        manifest, _ = init_combined(
            replica, root / "source", "source",
            max_payload_bytes=PAYLOAD_BYTES,
        )
        run_json(
            [str(folder), "init", "--manifest", str(manifest)],
            label="terminal-verification folder init",
        )
        receiver_pin = run_json(
            [
                str(replica), "certificate-spki", "--certificate",
                str(certificates / "receiver.pem"),
            ],
            label="terminal-verification receiver certificate pin",
        )["spki_sha256"]
        run_json(
            [
                str(replica), "membership-publish", "--manifest",
                str(manifest), "--policy-epoch", "1", "--peer",
                f"receiver:1:{receiver_pin}",
            ],
            label="terminal-verification source membership",
        )

        staged = run_json(
            [
                str(fixture), "--manifest", str(manifest),
                "--payload-bytes", str(PAYLOAD_BYTES), "--salt", "1006",
            ],
            label="deferred terminal-verification fixture",
            timeout=60.0,
        )
        digest = staged.get("content_sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            fail("terminal-verification fixture omitted exact digest")
        if staged.get("payload_bytes") != PAYLOAD_BYTES:
            fail("terminal-verification fixture changed payload extent")

        manifest_value = json.loads(manifest.read_text(encoding="utf-8"))
        payload_root = Path(manifest_value["payload_root"])
        payload_path = payload_root / digest
        if payload_path.exists():
            fail("terminal-verification fixture published payload prematurely")

        runtime = root / "runtime"
        runtime.mkdir(mode=0o700)
        status_socket = runtime / "status.sock"
        config = runtime / "linked-peer.json"
        listen_port = reserve_port()
        remote_port = reserve_port()
        while remote_port == listen_port:
            remote_port = reserve_port()
        config_value = linked_peer_configuration(
            manifest=manifest,
            certificates=certificates,
            local_device="source",
            remote_device="receiver",
            remote_pin=receiver_pin,
            listen_port=listen_port,
            remote_port=remote_port,
            status_socket=status_socket,
        )
        config_value["service"]["maximum_service_runtime_seconds"] = 45
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
                "terminal-verification scheduler service",
            )
            if initial.get("pid") != process.pid:
                fail("initial terminal-verification status changed PID")
            completed = wait_for_scheduler_completion(
                sync, process, status_socket, digest, payload_path
            )
            if completed.get("payload_integrity", {}).get("state") != "healthy":
                fail("local terminal verification entered integrity degradation")

            stop = run_json(
                [str(sync), "stop", "--socket", str(status_socket)],
                label="terminal-verification owner drain",
            )
            if (
                stop.get("schema") != "anonsync.local-stop.response.v1"
                or stop.get("server_pid") != process.pid
                or stop.get("stop_mode") != "drain"
            ):
                fail(
                    "terminal-verification owner drain response was not exact: "
                    f"{json.dumps(stop, sort_keys=True)}"
                )
            terminal = finish_service(
                process, "terminal-verification scheduler service", timeout=15.0
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
            fail("terminal-verification service emitted no terminal report")
        if terminal.get("stop_reason") != "local_stop_requested":
            fail(
                "terminal-verification service did not stop through owner drain: "
                f"{json.dumps(terminal, sort_keys=True)}"
            )
        final_status = terminal.get("payload_terminal_verification")
        if not isinstance(final_status, dict) or (
            final_status.get("observation_known") is not True
            or final_status.get("pending_entry_count") != 0
        ):
            fail("terminal report lost settled terminal-verification state")
        require_scheduler_counters(
            terminal, "terminal-verification terminal report", nested=False
        )
        if status_socket.exists():
            fail("terminal-verification service left its control socket behind")

    print(
        "receiver-local terminal-verification service process test passed "
        "(three bounded pulses, no peer process)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
