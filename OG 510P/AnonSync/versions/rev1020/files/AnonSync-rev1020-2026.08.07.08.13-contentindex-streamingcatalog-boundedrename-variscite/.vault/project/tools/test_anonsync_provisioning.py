#!/usr/bin/env python3
"""Prove create-new linked-peer provisioning reaches the shipping service.

The process proof creates two exact per-user layouts through ``provision``,
starts the unmodified ``run --config`` owner for both peers, converges nested
files in both directions, and exercises the owner-only stop socket.  It also
proves duplicate publication, unsafe user directories, and symbolic-link
substitution cannot overwrite a configuration or write outside the selected
layout.  Tor and native-I2P route/ingress combinations are serialized and read
back without contacting either anonymity router or embedding private I2P
destination material in the JSON configuration.
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
from typing import Any, Mapping, NoReturn, Sequence

from test_anonsync_service_configuration_status import I2P_PEER, VALID_ONION
from test_anonsync_service_process import (
    finish_service,
    wait_for_service_listener,
    wait_for_service_status_socket,
    wait_for_tree_convergence,
)
from test_anonsync_sync_process import (
    fail,
    generate_tls_fixture,
    init_combined,
    reserve_port,
    run_json,
    tree_snapshot,
    unique_json_object_pairs,
)


def parse_json_output(
    completed: subprocess.CompletedProcess[str],
    command: Sequence[str],
    label: str,
) -> dict[str, Any]:
    try:
        value = json.loads(
            completed.stdout, object_pairs_hook=unique_json_object_pairs
        )
    except (json.JSONDecodeError, ValueError) as error:
        fail(
            f"{label} did not emit one unique-key JSON object: {error}\n"
            f"command: {' '.join(command)}\nstdout:\n{completed.stdout}"
            f"stderr:\n{completed.stderr}"
        )
    if not isinstance(value, dict):
        fail(f"{label} JSON is not an object")
    return value


def run_json_environment(
    command: Sequence[str],
    *,
    environment: Mapping[str, str],
    label: str,
    timeout: float = 60.0,
) -> dict[str, Any]:
    completed = subprocess.run(
        list(command),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        env=dict(environment),
    )
    value = parse_json_output(completed, command, label)
    if completed.returncode != 0:
        fail(
            f"{label} failed with {completed.returncode}\n"
            f"command: {' '.join(command)}\nstdout:\n{completed.stdout}"
            f"stderr:\n{completed.stderr}"
        )
    if completed.stderr:
        fail(f"{label} wrote diagnostics on success: {completed.stderr}")
    return value


def expect_json_failure(
    command: Sequence[str],
    *,
    environment: Mapping[str, str],
    label: str,
    message_contains: str,
    timeout: float = 60.0,
) -> dict[str, Any]:
    completed = subprocess.run(
        list(command),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        env=dict(environment),
    )
    value = parse_json_output(completed, command, label)
    if completed.returncode == 0:
        fail(f"{label} unexpectedly succeeded: {completed.stdout}")
    if value.get("terminal_class") != "stopped" or value.get(
        "error_code"
    ) not in {"invalid_arguments", "operation_failed"}:
        fail(
            f"{label} emitted an unexpected failure object: "
            f"{json.dumps(value, sort_keys=True)}"
        )
    message = value.get("message")
    if not isinstance(message, str) or message_contains not in message:
        fail(
            f"{label} message {message!r} did not contain "
            f"{message_contains!r}"
        )
    if message_contains not in completed.stderr:
        fail(f"{label} stderr did not carry the same diagnostic")
    return value


def private_write(path: Path, exact: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        written = os.write(descriptor, exact)
        if written != len(exact):
            fail(f"short private-file write for {path}")
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    if stat.S_IMODE(path.stat().st_mode) != 0o600:
        fail(f"private file {path} did not retain exact mode 0600")


def user_environment(root: Path, name: str) -> tuple[dict[str, str], Path, Path]:
    home = root / f"home-{name}"
    runtime = root / f"runtime-{name}"
    home.mkdir(mode=0o700)
    runtime.mkdir(mode=0o700)
    environment = os.environ.copy()
    environment.pop("NOTIFY_SOCKET", None)
    environment["HOME"] = str(home)
    environment["XDG_RUNTIME_DIR"] = str(runtime)
    return environment, home, runtime


def direct_provision_command(
    sync: Path,
    certificates: Path,
    manifest: Path,
    local_device: str,
    remote_device: str,
    remote_pin: str,
    instance: str,
    listen_port: int,
    remote_port: int,
) -> list[str]:
    return [
        str(sync),
        "provision",
        "--instance",
        instance,
        "--manifest",
        str(manifest),
        "--remote-device",
        remote_device,
        "--remote-epoch",
        "1",
        "--remote-spki",
        remote_pin,
        "--certificate",
        str(certificates / f"{local_device}.pem"),
        "--private-key",
        str(certificates / f"{local_device}.key"),
        "--ca-file",
        str(certificates / "ca.pem"),
        "--transport",
        "direct",
        "--address",
        "127.0.0.1",
        "--port",
        str(remote_port),
        "--ingress",
        "direct",
        "--bind-address",
        "127.0.0.1",
        "--listen-port",
        str(listen_port),
        "--timeout-seconds",
        "3",
        "--max-runtime-seconds",
        "15",
        "--max-round-trips",
        "8",
        "--max-source-resets",
        "2",
        "--scan-interval-seconds",
        "1",
        "--retry-initial-seconds",
        "1",
        "--retry-maximum-seconds",
        "2",
        "--accept-poll-milliseconds",
        "50",
        "--inbound-timeout-seconds",
        "2",
        "--inbound-max-round-trips",
        "7",
        "--ingress-timeout-seconds",
        "3",
        "--max-service-runtime-seconds",
        "60",
    ]


def require_provision_summary(
    value: dict[str, Any],
    *,
    instance: str,
    home: Path,
    runtime: Path,
    local: str,
    remote: str,
    transport: str,
    ingress: str,
    numeric_listener: bool,
    label: str,
) -> tuple[Path, Path]:
    expected_config = (
        home
        / ".config"
        / "anonsync"
        / "linked-peers"
        / f"{instance}.json"
    )
    expected_status = runtime / f"anonsync-{instance}" / "status.sock"
    expected: dict[str, Any] = {
        "command": "provision",
        "terminal_class": "completed",
        "configuration_created": True,
        "instance": instance,
        "configuration_schema": "anonsync.linked-peer-service.v2",
        "configuration_path": str(expected_config),
        "runtime_directory": str(expected_status.parent),
        "status_socket": str(expected_status),
        "systemd_unit": f"anonsync-linked-peer@{instance}.service",
        "local_device_id": local,
        "local_epoch": 1,
        "remote_device_id": remote,
        "remote_epoch": 1,
        "transport": transport,
        "ingress_transport": ingress,
        "numeric_listener_active": numeric_listener,
    }
    for key, wanted in expected.items():
        if value.get(key) != wanted:
            fail(
                f"{label} field {key!r} was {value.get(key)!r}, expected "
                f"{wanted!r}: {json.dumps(value, sort_keys=True)}"
            )
    if not isinstance(value.get("configuration_bytes"), int) or value[
        "configuration_bytes"
    ] <= 0:
        fail(f"{label} omitted the exact configuration byte count")
    if not isinstance(value.get("network_step_horizon_seconds"), int):
        fail(f"{label} omitted the bounded network-step horizon")
    if not numeric_listener:
        if value.get("bind_address") is not None or value.get(
            "listen_port"
        ) is not None:
            fail(f"{label} exposed a numeric listener for native I2P ingress")
    if not expected_config.is_file() or expected_config.is_symlink():
        fail(f"{label} did not create one regular configuration file")
    if stat.S_IMODE(expected_config.stat().st_mode) != 0o600:
        fail(f"{label} configuration mode is not exact 0600")
    for directory in (
        home / ".config" / "anonsync",
        home / ".config" / "anonsync" / "linked-peers",
        expected_status.parent,
    ):
        if stat.S_IMODE(directory.stat().st_mode) != 0o700:
            fail(f"{label} directory {directory} is not exact mode 0700")
    return expected_config, expected_status


def common_identity_arguments(
    certificates: Path,
    manifest: Path,
    local: str,
    remote: str,
    remote_pin: str,
    instance: str,
) -> list[str]:
    return [
        "--instance",
        instance,
        "--manifest",
        str(manifest),
        "--remote-device",
        remote,
        "--remote-epoch",
        "1",
        "--remote-spki",
        remote_pin,
        "--certificate",
        str(certificates / f"{local}.pem"),
        "--private-key",
        str(certificates / f"{local}.key"),
        "--ca-file",
        str(certificates / "ca.pem"),
    ]


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

    with tempfile.TemporaryDirectory(prefix="anonsync-provisioning-") as raw:
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
            label="source provisioning folder catalog init",
        )
        run_json(
            [str(folder), "init", "--manifest", str(receiver_manifest)],
            label="receiver provisioning folder catalog init",
        )
        source_pin = run_json(
            [
                str(replica),
                "certificate-spki",
                "--certificate",
                str(certificates / "source.pem"),
            ],
            label="source provisioning certificate pin",
        )["spki_sha256"]
        receiver_pin = run_json(
            [
                str(replica),
                "certificate-spki",
                "--certificate",
                str(certificates / "receiver.pem"),
            ],
            label="receiver provisioning certificate pin",
        )["spki_sha256"]
        run_json(
            [
                str(replica),
                "membership-publish",
                "--manifest",
                str(source_manifest),
                "--policy-epoch",
                "1",
                "--peer",
                f"receiver:1:{receiver_pin}",
            ],
            label="source provisioning membership publication",
        )
        run_json(
            [
                str(replica),
                "membership-publish",
                "--manifest",
                str(receiver_manifest),
                "--policy-epoch",
                "1",
                "--peer",
                f"source:1:{source_pin}",
            ],
            label="receiver provisioning membership publication",
        )

        source_environment, source_home, source_runtime = user_environment(
            root, "source"
        )
        receiver_environment, receiver_home, receiver_runtime = (
            user_environment(root, "receiver")
        )
        source_port = reserve_port()
        receiver_port = reserve_port()
        while receiver_port == source_port:
            receiver_port = reserve_port()

        source_command = direct_provision_command(
            sync,
            certificates,
            source_manifest,
            "source",
            "receiver",
            receiver_pin,
            "source-peer",
            source_port,
            receiver_port,
        )
        receiver_command = direct_provision_command(
            sync,
            certificates,
            receiver_manifest,
            "receiver",
            "source",
            source_pin,
            "receiver-peer",
            receiver_port,
            source_port,
        )
        source_summary = run_json_environment(
            source_command,
            environment=source_environment,
            label="source linked-peer provisioning",
        )
        receiver_summary = run_json_environment(
            receiver_command,
            environment=receiver_environment,
            label="receiver linked-peer provisioning",
        )
        source_config, source_status = require_provision_summary(
            source_summary,
            instance="source-peer",
            home=source_home,
            runtime=source_runtime,
            local="source",
            remote="receiver",
            transport="direct_tcp",
            ingress="direct_tcp",
            numeric_listener=True,
            label="source linked-peer provisioning",
        )
        receiver_config, receiver_status = require_provision_summary(
            receiver_summary,
            instance="receiver-peer",
            home=receiver_home,
            runtime=receiver_runtime,
            local="receiver",
            remote="source",
            transport="direct_tcp",
            ingress="direct_tcp",
            numeric_listener=True,
            label="receiver linked-peer provisioning",
        )

        source_exact = source_config.read_bytes()
        receiver_exact = receiver_config.read_bytes()
        for label, exact in (
            ("source", source_exact),
            ("receiver", receiver_exact),
        ):
            if b"BEGIN PRIVATE KEY" in exact:
                fail(f"{label} configuration embedded private TLS key bytes")
            parsed = json.loads(
                exact.decode("utf-8"),
                object_pairs_hook=unique_json_object_pairs,
            )
            if not isinstance(parsed, dict) or parsed.get("schema") != (
                "anonsync.linked-peer-service.v2"
            ):
                fail(f"{label} provisioning did not emit canonical schema v2")

        source_checked = run_json(
            [str(sync), "check-config", "--config", str(source_config)],
            label="source provisioned configuration readback",
        )
        receiver_checked = run_json(
            [str(sync), "check-config", "--config", str(receiver_config)],
            label="receiver provisioned configuration readback",
        )
        if source_checked.get("configuration_path") != str(source_config):
            fail("source check-config did not retain the provisioned path")
        if receiver_checked.get("configuration_path") != str(receiver_config):
            fail("receiver check-config did not retain the provisioned path")

        expect_json_failure(
            source_command,
            environment=source_environment,
            label="duplicate source linked-peer provisioning",
            message_contains="already exists",
        )
        if source_config.read_bytes() != source_exact:
            fail("duplicate provisioning changed the original configuration")

        # A parseable but world-readable private key used to poison a new
        # immutable instance: TLS loading succeeded, publication occurred, and
        # only strict readback rejected the key mode. It must now fail before
        # even the per-user layout is created.
        loose_key = root / "world-readable-source.key"
        private_write(loose_key, (certificates / "source.key").read_bytes())
        os.chmod(loose_key, 0o644)
        loose_environment, loose_home, loose_runtime = user_environment(
            root, "loose-key"
        )
        loose_key_command = direct_provision_command(
            sync,
            certificates,
            source_manifest,
            "source",
            "receiver",
            receiver_pin,
            "loose-key-peer",
            reserve_port(),
            receiver_port,
        )
        loose_key_command[
            loose_key_command.index("--private-key") + 1
        ] = str(loose_key)
        expect_json_failure(
            loose_key_command,
            environment=loose_environment,
            label="world-readable private-key prepublication rejection",
            message_contains="0600",
        )
        if (loose_home / ".config").exists() or (
            loose_runtime / "anonsync-loose-key-peer"
        ).exists():
            fail("TLS admission failure left a provisioning layout residue")

        # Final-path substitution must fail without touching the link target.
        attacker_target = root / "attacker-final-target"
        private_write(attacker_target, b"attacker-owned sentinel\n")
        blocked_config = source_config.parent / "blocked-peer.json"
        blocked_config.symlink_to(attacker_target)
        blocked_command = direct_provision_command(
            sync,
            certificates,
            source_manifest,
            "source",
            "receiver",
            receiver_pin,
            "blocked-peer",
            reserve_port(),
            receiver_port,
        )
        expect_json_failure(
            blocked_command,
            environment=source_environment,
            label="symbolic-link final configuration rejection",
            message_contains="symlink",
        )
        if attacker_target.read_bytes() != b"attacker-owned sentinel\n":
            fail("rejected configuration symlink modified its target")

        # A hostile .config substitution must not create anything outside HOME.
        symlink_environment, symlink_home, _ = user_environment(root, "symlink")
        attacker_directory = root / "attacker-config-directory"
        attacker_directory.mkdir(mode=0o700)
        (symlink_home / ".config").symlink_to(attacker_directory, target_is_directory=True)
        symlink_command = direct_provision_command(
            sync,
            certificates,
            source_manifest,
            "source",
            "receiver",
            receiver_pin,
            "symlink-peer",
            reserve_port(),
            receiver_port,
        )
        expect_json_failure(
            symlink_command,
            environment=symlink_environment,
            label="symbolic-link user configuration root rejection",
            message_contains="symbolic-link",
        )
        if any(attacker_directory.iterdir()):
            fail("hostile .config symlink received an AnonSync directory")

        unsafe_environment, _, unsafe_runtime = user_environment(root, "unsafe")
        os.chmod(unsafe_runtime, 0o755)
        unsafe_command = direct_provision_command(
            sync,
            certificates,
            source_manifest,
            "source",
            "receiver",
            receiver_pin,
            "unsafe-runtime",
            reserve_port(),
            receiver_port,
        )
        expect_json_failure(
            unsafe_command,
            environment=unsafe_environment,
            label="permissive runtime directory rejection",
            message_contains="exact mode 0700",
        )

        source_nested = source_files / "source-side" / "nested"
        receiver_nested = receiver_files / "receiver-side" / "nested"
        source_nested.mkdir(parents=True, mode=0o700)
        receiver_nested.mkdir(parents=True, mode=0o700)
        (source_nested / "alpha.txt").write_bytes(
            b"provisioned service source payload\n"
        )
        (receiver_nested / "beta.txt").write_bytes(
            b"provisioned service receiver payload\n"
        )

        service_environment = os.environ.copy()
        service_environment.pop("NOTIFY_SOCKET", None)
        source_service = subprocess.Popen(
            [str(sync), "run", "--config", str(source_config)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=service_environment,
        )
        receiver_service = subprocess.Popen(
            [str(sync), "run", "--config", str(receiver_config)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=service_environment,
        )
        try:
            wait_for_service_listener(
                source_service, source_port, "provisioned source service"
            )
            wait_for_service_listener(
                receiver_service, receiver_port, "provisioned receiver service"
            )
            # The public listener is opened by the service owner before the
            # configured local status server is constructed. Prove both exact
            # owner-only control endpoints as part of startup readiness.
            wait_for_service_status_socket(
                source_service, source_status, "provisioned source service"
            )
            wait_for_service_status_socket(
                receiver_service, receiver_status,
                "provisioned receiver service",
            )
            wait_for_tree_convergence(
                source_files,
                receiver_files,
                "receiver-side/nested/beta.txt",
                "provisioned retained-service convergence",
                timeout=24.0,
            )
            # Startup readiness is stale after a bounded convergence interval.
            # Re-prove the exact endpoint at the owner-only drain cutpoint.
            wait_for_service_status_socket(
                source_service,
                source_status,
                "provisioned source service before owner-only drain",
            )
            stop_response = run_json(
                [str(sync), "stop", "--socket", str(source_status)],
                label="provisioned source owner-only drain",
            )
            expected_stop = {
                "schema": "anonsync.local-stop.response.v1",
                "command": "stop",
                "terminal_class": "completed",
                "stop_mode": "drain",
                "first_request": True,
                "server_pid": source_service.pid,
            }
            if stop_response != expected_stop:
                fail(
                    "provisioned source stop response was not exact: "
                    f"{json.dumps(stop_response, sort_keys=True)}"
                )
            receiver_service.send_signal(signal.SIGTERM)
            source_terminal = finish_service(
                source_service,
                "provisioned source service",
                timeout=15.0,
            )
            receiver_terminal = finish_service(
                receiver_service,
                "provisioned receiver service",
                timeout=15.0,
            )
        finally:
            for process in (source_service, receiver_service):
                if process.poll() is None:
                    process.kill()
                    process.communicate(timeout=2.0)
        if source_terminal.get("configuration_path") != str(source_config):
            fail("source terminal did not retain its provisioned configuration")
        if receiver_terminal.get("configuration_path") != str(receiver_config):
            fail("receiver terminal did not retain its provisioned configuration")
        if source_terminal.get("stop_reason") != "local_stop_requested":
            fail("source service did not honor the owner-only drain request")
        if receiver_terminal.get("stop_reason") != "stop_requested":
            fail("receiver service did not classify SIGTERM as a stop request")
        if source_status.exists() or receiver_status.exists():
            fail("provisioned service shutdown left a status socket")
        if tree_snapshot(source_files) != tree_snapshot(receiver_files):
            fail("provisioned retained services did not converge exact trees")

        # Tor route plus onion ingress: validate deterministic serialization and
        # exact external onion binding without requiring a running Tor daemon.
        tor_environment, tor_home, tor_runtime = user_environment(root, "tor")
        tor_command = [
            str(sync),
            "provision",
            *common_identity_arguments(
                certificates,
                source_manifest,
                "source",
                "receiver",
                receiver_pin,
                "tor-peer",
            ),
            "--transport",
            "tor",
            "--onion-address",
            VALID_ONION,
            "--onion-port",
            "443",
            "--tor-socks-address",
            "127.0.0.1",
            "--tor-socks-port",
            "9050",
            "--tor-isolation-token",
            "provisioning-isolation-token",
            "--ingress",
            "tor",
            "--ingress-onion-address",
            VALID_ONION,
            "--ingress-onion-port",
            "443",
            "--bind-address",
            "127.0.0.1",
            "--listen-port",
            str(reserve_port()),
            "--timeout-seconds",
            "3",
            "--max-runtime-seconds",
            "15",
            "--ingress-timeout-seconds",
            "3",
        ]
        tor_summary = run_json_environment(
            tor_command,
            environment=tor_environment,
            label="Tor linked-peer provisioning",
        )
        tor_config, _ = require_provision_summary(
            tor_summary,
            instance="tor-peer",
            home=tor_home,
            runtime=tor_runtime,
            local="source",
            remote="receiver",
            transport="tor_socks5",
            ingress="tor_onion_service",
            numeric_listener=True,
            label="Tor linked-peer provisioning",
        )
        tor_checked = run_json(
            [str(sync), "check-config", "--config", str(tor_config)],
            label="Tor provisioned configuration readback",
        )
        if tor_checked.get("transport") != "tor_socks5" or tor_checked.get(
            "ingress_transport"
        ) != "tor_onion_service":
            fail("Tor provisioning did not survive strict readback")

        # Native I2P ingress and outbound SAM routing keep destination material
        # in exact 0600 source files and serialize only their absolute paths.
        i2p_environment, i2p_home, i2p_runtime = user_environment(root, "i2p")
        outbound_destination = root / "i2p-outbound-private-destination"
        inbound_destination = root / "i2p-inbound-private-destination"
        outbound_secret = b"persistent-outbound-provisioning-destination\n"
        inbound_secret = b"persistent-inbound-provisioning-destination\n"
        private_write(outbound_destination, outbound_secret)
        private_write(inbound_destination, inbound_secret)
        i2p_command = [
            str(sync),
            "provision",
            *common_identity_arguments(
                certificates,
                source_manifest,
                "source",
                "receiver",
                receiver_pin,
                "i2p-peer",
            ),
            "--transport",
            "i2p",
            "--i2p-sam-address",
            "127.0.0.1",
            "--i2p-sam-port",
            "7656",
            "--i2p-destination",
            I2P_PEER,
            "--i2p-session-id",
            "provision-outbound-session",
            "--i2p-private-destination-file",
            str(outbound_destination),
            "--ingress",
            "i2p",
            "--ingress-i2p-sam-address",
            "127.0.0.1",
            "--ingress-i2p-sam-port",
            "7656",
            "--ingress-i2p-session-id",
            "provision-inbound-session",
            "--ingress-i2p-private-destination-file",
            str(inbound_destination),
            "--timeout-seconds",
            "180",
            "--max-runtime-seconds",
            "1080",
            "--inbound-timeout-seconds",
            "180",
            "--ingress-timeout-seconds",
            "180",
        ]
        i2p_summary = run_json_environment(
            i2p_command,
            environment=i2p_environment,
            label="I2P linked-peer provisioning",
        )
        i2p_config, _ = require_provision_summary(
            i2p_summary,
            instance="i2p-peer",
            home=i2p_home,
            runtime=i2p_runtime,
            local="source",
            remote="receiver",
            transport="i2p_sam",
            ingress="i2p_sam_accept",
            numeric_listener=False,
            label="I2P linked-peer provisioning",
        )
        i2p_exact = i2p_config.read_bytes()
        if outbound_secret.strip() in i2p_exact or inbound_secret.strip() in i2p_exact:
            fail("I2P provisioning embedded private destination material")
        if str(outbound_destination).encode() not in i2p_exact or str(
            inbound_destination
        ).encode() not in i2p_exact:
            fail("I2P provisioning did not bind exact private source paths")
        i2p_checked = run_json(
            [str(sync), "check-config", "--config", str(i2p_config)],
            label="I2P provisioned configuration readback",
        )
        if i2p_checked.get("transport") != "i2p_sam" or i2p_checked.get(
            "ingress_transport"
        ) != "i2p_sam_accept":
            fail("I2P provisioning did not survive strict readback")
        if i2p_checked.get("numeric_listener_active") is not False:
            fail("I2P provisioning readback invented a numeric listener")

    print("anonsync linked-peer provisioning process test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
