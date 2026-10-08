#!/usr/bin/env python3
"""Prove retained native I2P ingress startup, loss, and recovery.

The retained C++ peer service starts before its SAM router, reports degraded
rather than ready, and creates no numeric TLS listener for same-host bypass. A
fake SAM bridge then establishes SESSION CREATE + STREAM ACCEPT and hands the
accepted SAM stream directly to the common TLS dispatcher. An independent
sync-once client pulls through that path, the bridge is lost, and a replacement
bridge restores a second pull without restarting the service.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import stat
import subprocess
import tempfile
import threading
import time
from typing import Any, Callable

from test_anonsync_replica_anonymous_routes import (
    CheckedThread,
    I2P_PEER,
    PERSISTED_DESTINATION,
    SAM_SESSION_ID,
    expect_sam_hello,
    fake_outbound_sam,
    listener_port,
    make_listener,
    read_line,
    relay_bidirectional,
    runtime_sam_session_id,
    wait_for_process_event,
)
from test_anonsync_service_configuration_status import (
    require_payload_operator_status,
    require_payload_quarantine_inventory,
    write_private_json,
)
from test_anonsync_service_process import finish_service
from test_anonsync_sync_process import (
    fail,
    generate_tls_fixture,
    init_combined,
    reserve_port,
    run_json,
    tree_snapshot,
)


def make_listener_on_port(port: int) -> socket.socket:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", port))
    listener.listen(8)
    listener.settimeout(20.0)
    return listener


SAM_ACCEPT_PEER_DESTINATION = "A" * 516


def fake_inbound_accept_sam(
    listener: socket.socket,
    peer_listener: socket.socket,
    accept_ready: threading.Event,
) -> CheckedThread:
    """Model one persistent SAM session and one native accepted I2P stream."""

    def serve() -> None:
        with listener, peer_listener:
            control, _ = listener.accept()
            with control:
                control.settimeout(20.0)
                expect_sam_hello(
                    control, "inbound SAM control HELLO", selected_version="3.2"
                )
                session = read_line(control, "inbound SAM SESSION CREATE")
                session_id = runtime_sam_session_id(
                    session, "inbound SAM SESSION CREATE"
                )
                required = (
                    "SESSION CREATE STYLE=STREAM",
                    f"DESTINATION={PERSISTED_DESTINATION}",
                    "i2cp.leaseSetEncType=4",
                    "inbound.quantity=2",
                    "outbound.quantity=2",
                )
                if not all(token in session for token in required):
                    fail(f"inbound SAM session command is incomplete: {session}")
                if "SIGNATURE_TYPE=" in session:
                    fail("inbound persistent SAM identity received SIGNATURE_TYPE")
                control.sendall(
                    b"SESSION STATUS RESULT=OK DESTINATION=fake-inbound-public\n"
                )

                accepted, _ = listener.accept()
                with accepted:
                    accepted.settimeout(20.0)
                    expect_sam_hello(
                        accepted,
                        "inbound SAM accept HELLO",
                        selected_version="3.2",
                    )
                    command = read_line(accepted, "inbound SAM STREAM ACCEPT")
                    required_accept = (
                        "STREAM ACCEPT",
                        f"ID={session_id}",
                        "SILENT=false",
                    )
                    if not all(token in command for token in required_accept):
                        fail(f"inbound SAM accept command changed: {command}")
                    if any(token in command for token in (
                        "STREAM FORWARD", "HOST=", "PORT=", "SILENT=true"
                    )):
                        fail(
                            "native SAM accept introduced a numeric forwarding path: "
                            f"{command}"
                        )
                    accepted.sendall(b"STREAM STATUS RESULT=OK\n")
                    accept_ready.set()

                    remote, _ = peer_listener.accept()
                    with remote:
                        remote.settimeout(None)
                        accepted.settimeout(None)
                        # SAM 3.2 appends these port tokens to the full remote
                        # destination. They must be consumed before TLS begins.
                        peer_line = (
                            SAM_ACCEPT_PEER_DESTINATION
                            + " FROM_PORT=23456 TO_PORT=443\n"
                        ).encode("ascii")
                        # Cross more than one 100 ms worker poll with a partial
                        # destination. The exact prefix must remain bound to the
                        # same accepted socket rather than being discarded or
                        # passed into TLS as an invalid record.
                        accepted.sendall(peer_line[:137])
                        time.sleep(0.16)
                        accepted.sendall(peer_line[137:])
                        relay_bidirectional(
                            accepted, remote, "I2P accepted TLS stream"
                        )

    return CheckedThread(serve, "fake inbound SAM STREAM ACCEPT")


def fake_stalling_session_sam(
    listener: socket.socket,
    session_seen: threading.Event,
) -> CheckedThread:
    """Hold SESSION CREATE open to prove service shutdown cancels SAM setup."""

    def serve() -> None:
        with listener:
            control, _ = listener.accept()
            with control:
                control.settimeout(0.2)
                expect_sam_hello(control, "stalling SAM control HELLO")
                session = read_line(control, "stalling SAM SESSION CREATE")
                runtime_sam_session_id(session, "stalling SAM SESSION CREATE")
                required = (
                    "SESSION CREATE STYLE=STREAM",
                    f"DESTINATION={PERSISTED_DESTINATION}",
                    "i2cp.leaseSetEncType=4",
                    "inbound.quantity=2",
                    "outbound.quantity=2",
                )
                if not all(token in session for token in required):
                    fail(f"stalling SAM session command is incomplete: {session}")
                if "SIGNATURE_TYPE=" in session:
                    fail("stalling persistent SAM identity received SIGNATURE_TYPE")
                session_seen.set()
                # Deliberately never send SESSION STATUS. The application owns a
                # 180-second setup horizon, but SIGTERM must cancel this exact
                # attempt and close the descriptor in a bounded interval.
                while True:
                    try:
                        data = control.recv(1)
                    except socket.timeout:
                        continue
                    if not data:
                        return
                    fail(f"stalling SAM control received unexpected bytes: {data!r}")

    return CheckedThread(serve, "fake stalling SAM SESSION CREATE")


def private_file(path: Path, data: str) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(descriptor, data.encode("ascii"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    if stat.S_IMODE(path.stat().st_mode) != 0o600:
        fail(f"private file {path} did not retain mode 0600")


def source_configuration(
    *,
    manifest: Path,
    certificates: Path,
    receiver_pin: str,
    listen_port: int,
    unavailable_receiver_port: int,
    sam_port: int,
    private_destination: Path,
    status_socket: Path,
) -> dict[str, Any]:
    return {
        "schema": "anonsync.linked-peer-service.v2",
        "manifest": str(manifest),
        "peer": {
            "device_id": "receiver",
            "epoch": 1,
            "spki_sha256": receiver_pin,
        },
        "tls": {
            "certificate": str(certificates / "source.pem"),
            "private_key": str(certificates / "source.key"),
            "ca_file": str(certificates / "ca.pem"),
        },
        "listen": {"address": "127.0.0.1", "port": listen_port},
        "route": {
            "kind": "direct",
            "address": "127.0.0.1",
            "port": unavailable_receiver_port,
        },
        "ingress": {
            "kind": "i2p",
            "sam_address": "127.0.0.1",
            "sam_port": sam_port,
            "session_id": SAM_SESSION_ID,
            "private_destination_file": str(private_destination),
            "inbound_quantity": 2,
            "outbound_quantity": 2,
        },
        "status_socket": str(status_socket),
        "service": {
            "timeout_seconds": 2,
            "cycle_runtime_seconds": 8,
            "max_round_trips": 8,
            "max_source_resets": 2,
            "inbound_timeout_seconds": 2,
            "inbound_max_round_trips": 8,
            "ingress_timeout_seconds": 180,
            "accept_poll_milliseconds": 50,
            "scan_interval_seconds": 1,
            "retry_initial_seconds": 1,
            "retry_maximum_seconds": 1,
            "maximum_service_runtime_seconds": 90,
        },
    }


def query_status(sync: Path, socket_path: Path, label: str) -> dict[str, Any]:
    return run_json(
        [
            str(sync), "status", "--socket", str(socket_path),
            "--timeout-milliseconds", "1000",
        ],
        label=label,
    )


def wait_for_status(
    sync: Path,
    process: subprocess.Popen[str],
    socket_path: Path,
    predicate: Callable[[dict[str, Any]], bool],
    label: str,
    *,
    timeout: float = 15.0,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last: dict[str, Any] | None = None
    last_error = "status socket unavailable"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1.0)
            fail(
                f"{label} service exited with {process.returncode}\n"
                f"stdout:\n{stdout}\nstderr:\n{stderr}"
            )
        try:
            last = query_status(sync, socket_path, f"{label} status")
            require_payload_operator_status(last, label)
            if predicate(last):
                if last.get("ready") is True:
                    quarantine = last.get("payload_quarantine")
                    if not isinstance(quarantine, dict):
                        fail(f"{label} ready status omitted payload quarantine")
                    inventory = quarantine.get("inventory")
                    require_payload_quarantine_inventory(
                        inventory, f"{label} ready quarantine"
                    )
                    if inventory.get("observation_known") is not True:
                        fail(
                            f"{label} reported ready without a complete "
                            "quarantine observation: "
                            f"{json.dumps(last, sort_keys=True)}"
                        )
                return last
            last_error = json.dumps(last, sort_keys=True)
        except (FileNotFoundError, OSError, RuntimeError) as error:
            last_error = str(error)
        time.sleep(0.05)
    fail(f"{label} status predicate was not met: {last_error}")


def sync_once_base(
    sync: Path,
    receiver_manifest: Path,
    certificates: Path,
    source_pin: str,
    maximum_runtime_seconds: int = 180,
) -> list[str]:
    return [
        str(sync), "once", "--manifest", str(receiver_manifest),
        "--remote-device", "source", "--remote-epoch", "1",
        "--remote-spki", source_pin,
        "--certificate", str(certificates / "receiver.pem"),
        "--private-key", str(certificates / "receiver.key"),
        "--ca-file", str(certificates / "ca.pem"),
        "--max-round-trips", "8", "--max-source-resets", "2",
        "--max-runtime-seconds", str(maximum_runtime_seconds),
    ]


def run_i2p_pull(
    sync: Path,
    receiver_manifest: Path,
    certificates: Path,
    source_pin: str,
    sam_port: int,
    label: str,
) -> dict[str, Any]:
    value = run_json(
        [
            *sync_once_base(
                sync, receiver_manifest, certificates, source_pin
            ),
            "--transport", "i2p",
            "--i2p-destination", I2P_PEER,
            "--i2p-sam-address", "127.0.0.1",
            "--i2p-sam-port", str(sam_port),
            "--i2p-session-id", SAM_SESSION_ID,
            "--timeout-seconds", "180",
        ],
        label=label,
        timeout=35.0,
    )
    if value.get("terminal_class") != "completed":
        fail(f"{label} was not complete: {json.dumps(value, sort_keys=True)}")
    reconciliation = value.get("reconciliation")
    if not isinstance(reconciliation, dict):
        fail(f"{label} omitted reconciliation evidence")
    expected = {
        "transport": "i2p_sam",
        "route_disposition": "connected",
        "route_negotiated": True,
        "peer_authenticated": True,
        "peer_device_id": "source",
    }
    for key, wanted in expected.items():
        if reconciliation.get(key) != wanted:
            fail(
                f"{label} reconciliation field {key!r} was "
                f"{reconciliation.get(key)!r}, expected {wanted!r}: "
                f"{json.dumps(value, sort_keys=True)}"
            )
    return value


def expect_direct_pull_blocked(
    sync: Path,
    receiver_manifest: Path,
    certificates: Path,
    source_pin: str,
    source_port: int,
) -> None:
    command = [
        # The connector proof must run after the local repair pass. Three
        # seconds was below that scheduling frontier under an otherwise valid
        # concurrent compiler load and could yield an inconclusive
        # command_deadline_before_pull result. Keep the attempt bounded, but
        # leave enough horizon to require actual reconciliation evidence.
        *sync_once_base(
            sync, receiver_manifest, certificates, source_pin,
            maximum_runtime_seconds=8,
        ),
        "--transport", "direct", "--address", "127.0.0.1",
        "--port", str(source_port), "--timeout-seconds", "1",
    ]
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=15.0,
        check=False,
    )
    if completed.returncode == 0:
        fail(
            "degraded I2P service accepted a direct loopback pull: "
            f"{completed.stdout}"
        )
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        fail(
            "blocked direct pull did not emit JSON: "
            f"{error}: stdout={completed.stdout!r}, stderr={completed.stderr!r}"
        )
    reconciliation = value.get("reconciliation")
    if not isinstance(reconciliation, dict):
        fail(
            "blocked direct pull omitted reconciliation result: "
            f"{json.dumps(value, sort_keys=True)}"
        )
    if reconciliation.get("handshake_complete") is True:
        fail(
            "degraded I2P service completed a direct TLS handshake: "
            f"{json.dumps(value, sort_keys=True)}"
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
        prefix="anonsync-service-i2p-ingress-"
    ) as raw:
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
        run_json(
            [str(folder), "init", "--manifest", str(source_manifest)],
            label="I2P ingress source folder init",
        )
        run_json(
            [str(folder), "init", "--manifest", str(receiver_manifest)],
            label="I2P ingress receiver folder init",
        )
        source_pin = run_json(
            [
                str(replica), "certificate-spki", "--certificate",
                str(certificates / "source.pem"),
            ],
            label="I2P ingress source certificate pin",
        )["spki_sha256"]
        receiver_pin = run_json(
            [
                str(replica), "certificate-spki", "--certificate",
                str(certificates / "receiver.pem"),
            ],
            label="I2P ingress receiver certificate pin",
        )["spki_sha256"]
        run_json(
            [
                str(replica), "membership-publish", "--manifest",
                str(source_manifest), "--policy-epoch", "1", "--peer",
                f"receiver:1:{receiver_pin}",
            ],
            label="I2P ingress source membership",
        )
        run_json(
            [
                str(replica), "membership-publish", "--manifest",
                str(receiver_manifest), "--policy-epoch", "1", "--peer",
                f"source:1:{source_pin}",
            ],
            label="I2P ingress receiver membership",
        )

        initial = source_files / "i2p" / "initial.txt"
        initial.parent.mkdir(parents=True, mode=0o700)
        initial.write_bytes(b"retained native I2P ingress initial payload\n")

        source_port = reserve_port()
        unavailable_receiver_port = reserve_port()
        while unavailable_receiver_port == source_port:
            unavailable_receiver_port = reserve_port()
        source_sam_port = reserve_port()
        while source_sam_port in {source_port, unavailable_receiver_port}:
            source_sam_port = reserve_port()

        runtime = root / "source-runtime"
        runtime.mkdir(mode=0o700)
        status_socket = runtime / "status.sock"
        config_path = runtime / "linked-peer.json"
        private_destination = runtime / "i2p-private-destination.txt"
        private_file(private_destination, PERSISTED_DESTINATION + "\n")
        write_private_json(
            config_path,
            source_configuration(
                manifest=source_manifest,
                certificates=certificates,
                receiver_pin=receiver_pin,
                listen_port=source_port,
                unavailable_receiver_port=unavailable_receiver_port,
                sam_port=source_sam_port,
                private_destination=private_destination,
                status_socket=status_socket,
            ),
        )
        checked = run_json(
            [str(sync), "check-config", "--config", str(config_path)],
            label="native I2P ingress configuration check",
        )
        expected_checked = {
            "configuration_schema": "anonsync.linked-peer-service.v2",
            "transport": "direct_tcp",
            "ingress_transport": "i2p_sam_accept",
            "numeric_listener_active": False,
            "bind_address": None,
            "listen_port": None,
        }
        for key, wanted in expected_checked.items():
            if checked.get(key) != wanted:
                fail(
                    f"I2P ingress config field {key!r} was "
                    f"{checked.get(key)!r}, expected {wanted!r}"
                )

        source = subprocess.Popen(
            [str(sync), "run", "--config", str(config_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            degraded = wait_for_status(
                sync,
                source,
                status_socket,
                lambda value: (
                    value.get("schema") == "anonsync.peer-service.status.v26"
                    and value.get("service_state") == "degraded"
                    and value.get("ready") is False
                    and value.get("ingress_transport") == "i2p_sam_accept"
                    and value.get("ingress_ready") is False
                    and value.get("numeric_listener_active") is False
                    and value.get("bind_address") is None
                    and value.get("listen_port") is None
                    and isinstance(value.get("counters"), dict)
                    and value["counters"].get("ingress_setup_failures", 0) >= 1
                ),
                "delayed SAM startup",
            )
            unavailable = degraded.get("last_ingress")
            if not isinstance(unavailable, dict):
                fail("degraded I2P status omitted the last ingress event")
            if unavailable.get("disposition") != (
                "ingress_publication_unavailable"
            ):
                fail(
                    "degraded I2P status lost the unavailable disposition: "
                    f"{json.dumps(degraded, sort_keys=True)}"
                )
            unavailable_report = unavailable.get("report")
            if not isinstance(unavailable_report, dict):
                fail("degraded I2P status omitted typed SAM setup evidence")
            if (
                unavailable_report.get("route_kind") != "i2p_sam"
                or unavailable_report.get("terminal_stage")
                != "numeric_connect"
                or unavailable_report.get("disposition")
                != "numeric_connect_failed"
                or not isinstance(
                    unavailable_report.get("numeric_connect_error"), int
                )
            ):
                fail(
                    "degraded I2P status reported the wrong setup frontier: "
                    f"{json.dumps(unavailable, sort_keys=True)}"
                )
            baseline_accepted = degraded["counters"].get(
                "accepted_sessions", 0
            )

            # Native STREAM ACCEPT owns no local application listener at all;
            # the compatibility listen field must remain unreachable both while
            # the router is down and while publication is ready.
            expect_direct_pull_blocked(
                sync,
                receiver_manifest,
                certificates,
                source_pin,
                source_port,
            )
            still_degraded = query_status(
                sync, status_socket, "degraded no-listener probe status"
            )
            if still_degraded.get("ready") is not False:
                fail("degraded I2P source became ready without SAM")
            if still_degraded["counters"].get(
                "accepted_sessions", 0
            ) != baseline_accepted:
                fail("numeric no-listener probe reached the TLS dispatcher")

            first_inbound_listener = make_listener_on_port(source_sam_port)
            first_peer_listener = make_listener()
            first_peer_port = listener_port(first_peer_listener)
            first_accept_ready = threading.Event()
            first_inbound = fake_inbound_accept_sam(
                first_inbound_listener,
                first_peer_listener,
                first_accept_ready,
            )
            wait_for_process_event(
                first_accept_ready,
                source,
                first_inbound,
                15.0,
                "retained source first I2P STREAM ACCEPT",
            )
            first_ready = wait_for_status(
                sync,
                source,
                status_socket,
                lambda value: (
                    value.get("service_state") == "running"
                    and value.get("ready") is True
                    and value.get("ingress_ready") is True
                    and value.get("counters", {}).get(
                        "ingress_setup_successes", 0
                    ) >= 1
                ),
                "first native I2P publication",
            )
            first_event = first_ready.get("last_ingress")
            first_report = (
                first_event.get("report")
                if isinstance(first_event, dict)
                else None
            )
            if (
                not isinstance(first_event, dict)
                or first_event.get("disposition")
                != "ingress_publication_connected"
                or not isinstance(first_report, dict)
                or first_report.get("disposition") != "connected"
                or first_report.get("terminal_stage") != "complete"
                or first_report.get("sam_result") != "ok"
            ):
                fail(
                    "ready I2P status omitted its successful SAM frontier: "
                    f"{json.dumps(first_ready, sort_keys=True)}"
                )
            if (
                first_ready.get("numeric_listener_active") is not False
                or first_ready.get("bind_address") is not None
                or first_ready.get("listen_port") is not None
            ):
                fail(
                    "native I2P ready status exposed a numeric listener: "
                    f"{json.dumps(first_ready, sort_keys=True)}"
                )
            expect_direct_pull_blocked(
                sync,
                receiver_manifest,
                certificates,
                source_pin,
                source_port,
            )

            first_outbound_listener = make_listener()
            first_outbound_port = listener_port(first_outbound_listener)
            first_outbound = fake_outbound_sam(
                first_outbound_listener, first_peer_port
            )
            run_i2p_pull(
                sync,
                receiver_manifest,
                certificates,
                source_pin,
                first_outbound_port,
                "first retained-I2P pull",
            )
            first_outbound.join()
            first_inbound.join()
            if (receiver_files / "i2p" / "initial.txt").read_bytes() != (
                b"retained native I2P ingress initial payload\n"
            ):
                fail("first native I2P pull changed payload bytes")

            lost = wait_for_status(
                sync,
                source,
                status_socket,
                lambda value: (
                    value.get("service_state") == "degraded"
                    and value.get("ready") is False
                    and value.get("ingress_ready") is False
                    and value.get("counters", {}).get("ingress_losses", 0) >= 1
                ),
                "retained I2P publication loss",
            )
            lost_event = lost.get("last_ingress")
            lost_report = (
                lost_event.get("report")
                if isinstance(lost_event, dict)
                else None
            )
            if (
                not isinstance(lost_event, dict)
                or lost_event.get("disposition")
                != "ingress_publication_lost"
                or not isinstance(lost_event.get("diagnostic"), str)
                or not lost_event["diagnostic"]
                or not isinstance(lost_report, dict)
                or lost_report.get("route_kind") != "i2p_sam"
                or lost_report.get("disposition") not in {
                    "numeric_connect_failed", "route_rejected"
                }
                or lost_report.get("terminal_stage") not in {
                    "numeric_connect", "i2p_stream_hello", "i2p_stream_accept"
                }
            ):
                fail(
                    "lost I2P status omitted its typed accept-rearm frontier: "
                    f"{json.dumps(lost, sort_keys=True)}"
                )
            accepted_after_first = lost["counters"].get(
                "accepted_sessions", 0
            )

            prior_periodic_repairs = lost["counters"].get(
                "periodic_repairs", 0
            )
            after_restart = source_files / "i2p" / "after-restart.txt"
            after_restart.write_bytes(
                b"retained native I2P ingress restart payload\n"
            )
            # Give the retained folder owner one new periodic scan while ingress
            # is unavailable. Publication is local work and must not depend on SAM.
            wait_for_status(
                sync,
                source,
                status_socket,
                lambda value: value.get("counters", {}).get(
                    "periodic_repairs", 0
                ) > prior_periodic_repairs,
                "local publication during I2P outage",
                timeout=8.0,
            )
            expect_direct_pull_blocked(
                sync,
                receiver_manifest,
                certificates,
                source_pin,
                source_port,
            )
            if (receiver_files / "i2p" / "after-restart.txt").exists():
                fail("outage payload arrived through a direct fallback")
            after_direct_probe = query_status(
                sync, status_socket, "status after blocked direct pull"
            )
            if after_direct_probe["counters"].get(
                "accepted_sessions", 0
            ) != accepted_after_first:
                fail("blocked direct pull reached the degraded TLS server")

            second_inbound_listener = make_listener_on_port(source_sam_port)
            second_peer_listener = make_listener()
            second_peer_port = listener_port(second_peer_listener)
            second_accept_ready = threading.Event()
            second_inbound = fake_inbound_accept_sam(
                second_inbound_listener,
                second_peer_listener,
                second_accept_ready,
            )
            wait_for_process_event(
                second_accept_ready,
                source,
                second_inbound,
                15.0,
                "retained source replacement I2P STREAM ACCEPT",
            )
            wait_for_status(
                sync,
                source,
                status_socket,
                lambda value: (
                    value.get("ready") is True
                    and value.get("ingress_ready") is True
                    and value.get("counters", {}).get(
                        "ingress_setup_successes", 0
                    ) >= 2
                ),
                "replacement native I2P publication",
            )

            second_outbound_listener = make_listener()
            second_outbound_port = listener_port(second_outbound_listener)
            second_outbound = fake_outbound_sam(
                second_outbound_listener, second_peer_port
            )
            run_i2p_pull(
                sync,
                receiver_manifest,
                certificates,
                source_pin,
                second_outbound_port,
                "replacement retained-I2P pull",
            )
            second_outbound.join()
            second_inbound.join()

            source_tree = tree_snapshot(source_files)
            receiver_tree = tree_snapshot(receiver_files)
            if source_tree != receiver_tree or len(source_tree) != 2:
                fail(
                    "native I2P restart did not converge exact trees: "
                    f"source={source_tree}, receiver={receiver_tree}"
                )
            final_status = query_status(
                sync, status_socket, "final retained I2P status"
            )
            counters = final_status.get("counters", {})
            for key, minimum in {
                "ingress_setup_attempts": 3,
                "ingress_setup_successes": 2,
                "ingress_setup_failures": 1,
                "ingress_losses": 1,
                "accepted_sessions": 2,
            }.items():
                if counters.get(key, 0) < minimum:
                    fail(
                        f"final I2P status counter {key!r} was "
                        f"{counters.get(key)!r}, expected at least {minimum}: "
                        f"{json.dumps(final_status, sort_keys=True)}"
                    )

            source.send_signal(signal.SIGTERM)
            terminal = finish_service(
                source, "native I2P retained source stop", timeout=15.0
            )
        finally:
            if source.poll() is None:
                source.kill()
                source.communicate(timeout=2.0)

        expected_terminal = {
            "command": "run",
            "terminal_class": "completed",
            "stop_reason": "stop_requested",
            "transport": "direct_tcp",
            "ingress_transport": "i2p_sam_accept",
            "numeric_listener_active": False,
            "bind_address": None,
            "listen_port": None,
        }
        for key, wanted in expected_terminal.items():
            if terminal.get(key) != wanted:
                fail(
                    f"I2P service terminal field {key!r} was "
                    f"{terminal.get(key)!r}, expected {wanted!r}: "
                    f"{json.dumps(terminal, sort_keys=True)}"
                )
        ingress = terminal.get("ingress")
        if not isinstance(ingress, dict):
            fail("I2P service terminal omitted ingress accounting")
        if ingress.get("setup_successes", 0) < 2:
            fail("I2P service terminal lost restart accounting")
        if status_socket.exists():
            fail("I2P retained service left its status socket behind")

        # A legitimate I2P tunnel build can occupy most of the configured
        # 180-second setup deadline. It must not make daemon shutdown inherit
        # that deadline. Reopen the same deployment against a bridge that stops
        # after SESSION CREATE and prove the route-only worker is cancellable.
        stalled_listener = make_listener_on_port(source_sam_port)
        stalled_session_seen = threading.Event()
        stalled_bridge = fake_stalling_session_sam(
            stalled_listener, stalled_session_seen
        )
        stalled_source = subprocess.Popen(
            [str(sync), "run", "--config", str(config_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            wait_for_process_event(
                stalled_session_seen,
                stalled_source,
                stalled_bridge,
                10.0,
                "stalling I2P SESSION CREATE",
            )
            shutdown_started = time.monotonic()
            stalled_source.send_signal(signal.SIGTERM)
            stalled_terminal = finish_service(
                stalled_source,
                "cancellable I2P setup stop",
                timeout=5.0,
            )
            shutdown_elapsed = time.monotonic() - shutdown_started
            if shutdown_elapsed >= 3.0:
                fail(
                    "SIGTERM inherited the 180-second SAM setup horizon: "
                    f"shutdown took {shutdown_elapsed:.3f} seconds"
                )
        finally:
            if stalled_source.poll() is None:
                stalled_source.kill()
                stalled_source.communicate(timeout=2.0)
        stalled_bridge.join(timeout=5.0)
        for key, wanted in {
            "command": "run",
            "terminal_class": "completed",
            "stop_reason": "stop_requested",
            "ingress_transport": "i2p_sam_accept",
            "numeric_listener_active": False,
        }.items():
            if stalled_terminal.get(key) != wanted:
                fail(
                    f"cancellable setup terminal field {key!r} was "
                    f"{stalled_terminal.get(key)!r}, expected {wanted!r}: "
                    f"{json.dumps(stalled_terminal, sort_keys=True)}"
                )
        if status_socket.exists():
            fail("cancellable I2P setup left its status socket behind")

    print("anonsync retained native I2P ingress process test passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 - process-test boundary.
        print(
            f"anonsync retained native I2P ingress process test failed: {error}",
            file=os.sys.stderr,
        )
        raise SystemExit(1)
