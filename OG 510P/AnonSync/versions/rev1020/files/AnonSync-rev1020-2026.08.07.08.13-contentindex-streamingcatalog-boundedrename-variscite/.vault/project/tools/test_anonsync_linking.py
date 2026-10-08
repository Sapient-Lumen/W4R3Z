#!/usr/bin/env python3
"""Prove signed public-card linking reaches the retained C++ service.

This is the operator-facing replacement for manual OpenSSL, SPKI extraction,
membership publication, and linked-peer provisioning.  Each peer creates one
share-scoped local identity, exchanges only its signed public card, explicitly
admits the other card, and then runs the existing configured service unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import tempfile
from typing import Any, Mapping, Sequence

from test_anonsync_provisioning import (
    expect_json_failure,
    run_json_environment,
    user_environment,
)
from test_anonsync_service_process import (
    finish_service,
    wait_for_service_listener,
    wait_for_tree_convergence,
)
from test_anonsync_sync_process import (
    fail,
    init_combined,
    reserve_port,
    run_json,
    tree_snapshot,
    unique_json_object_pairs,
)


def require_mode(path: Path, mode: int, label: str) -> None:
    if path.is_symlink() or not path.exists():
        fail(f"{label} is absent or symbolic: {path}")
    actual = stat.S_IMODE(path.stat().st_mode)
    if actual != mode:
        fail(f"{label} mode is {actual:o}, expected {mode:o}: {path}")


def verification_code(digest: str) -> str:
    return "-".join(digest[index : index + 4] for index in range(0, 32, 4))


def require_identity_summary(
    value: dict[str, Any],
    *,
    instance: str,
    home: Path,
    local_device: str,
    dispositions: str | tuple[str, str, str],
    label: str,
) -> tuple[Path, Path, Path, Path]:
    identity = (
        home
        / ".config"
        / "anonsync"
        / "linked-identities"
        / instance
    )
    key = identity / "local.key"
    certificate = identity / "local.pem"
    card = identity / "pairing-card.json"
    trust = identity / "peer-trust.pem"
    if isinstance(dispositions, str):
        key_disposition = dispositions
        certificate_disposition = dispositions
        card_disposition = dispositions
    else:
        (
            key_disposition,
            certificate_disposition,
            card_disposition,
        ) = dispositions
    expected: dict[str, Any] = {
        "command": "identity-create",
        "terminal_class": "completed",
        "instance": instance,
        "local_device_id": local_device,
        "local_epoch": 1,
        "identity_directory": str(identity),
        "private_key_path": str(key),
        "certificate_path": str(certificate),
        "pairing_card_path": str(card),
        "peer_trust_path": str(trust),
        "private_key_disposition": key_disposition,
        "certificate_disposition": certificate_disposition,
        "pairing_card_disposition": card_disposition,
        "pairing_card_is_public_only": True,
    }
    for field, wanted in expected.items():
        if value.get(field) != wanted:
            fail(
                f"{label} field {field!r} was {value.get(field)!r}, "
                f"expected {wanted!r}: {json.dumps(value, sort_keys=True)}"
            )
    pin = value.get("spki_sha256")
    if not isinstance(pin, str) or len(pin) != 64 or pin != pin.lower():
        fail(f"{label} did not report one lowercase SHA-256 SPKI pin")
    card_digest = hashlib.sha256(card.read_bytes()).hexdigest()
    if value.get("pairing_card_sha256") != card_digest:
        fail(f"{label} did not report the exact canonical card digest")
    if value.get("pairing_verification_code") != verification_code(card_digest):
        fail(f"{label} did not report the exact card verification code")
    for directory in (
        home / ".config",
        home / ".config" / "anonsync",
        home / ".config" / "anonsync" / "linked-identities",
        identity,
    ):
        require_mode(directory, 0o700, f"{label} private directory")
    for path in (key, certificate, card):
        require_mode(path, 0o600, f"{label} private identity file")
    return key, certificate, card, trust


def direct_link_command(
    sync: Path,
    manifest: Path,
    peer_card: Path,
    instance: str,
    listen_port: int,
    remote_port: int,
    peer_card_sha256: str | None = None,
) -> list[str]:
    command = [
        str(sync),
        "link",
        "--instance",
        instance,
        "--manifest",
        str(manifest),
        "--peer-card",
        str(peer_card),
    ]
    if peer_card_sha256 is not None:
        command.extend(["--peer-card-sha256", peer_card_sha256])
    command.extend(
        [
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
        "35",
        ]
    )
    return command


def require_link_summary(
    value: dict[str, Any],
    *,
    instance: str,
    home: Path,
    runtime: Path,
    local: str,
    remote: str,
    peer_card: Path,
    local_card_sha256: str,
    peer_card_sha256: str,
    listen_port: int,
    label: str,
) -> tuple[Path, Path]:
    identity = home / ".config/anonsync/linked-identities" / instance
    config = home / ".config/anonsync/linked-peers" / f"{instance}.json"
    status = runtime / f"anonsync-{instance}" / "status.sock"
    expected: dict[str, Any] = {
        "command": "link",
        "terminal_class": "completed",
        "configuration_created": True,
        "instance": instance,
        "configuration_schema": "anonsync.linked-peer-service.v2",
        "configuration_path": str(config),
        "runtime_directory": str(status.parent),
        "status_socket": str(status),
        "systemd_unit": f"anonsync-linked-peer@{instance}.service",
        "local_device_id": local,
        "local_epoch": 1,
        "remote_device_id": remote,
        "remote_epoch": 1,
        "transport": "direct_tcp",
        "ingress_transport": "direct_tcp",
        "numeric_listener_active": True,
        "bind_address": "127.0.0.1",
        "listen_port": listen_port,
        "identity_directory": str(identity),
        "private_key_path": str(identity / "local.key"),
        "certificate_path": str(identity / "local.pem"),
        "local_pairing_card_path": str(identity / "pairing-card.json"),
        "local_pairing_card_sha256": local_card_sha256,
        "local_pairing_verification_code": verification_code(
            local_card_sha256
        ),
        "peer_card_path": str(peer_card),
        "peer_card_sha256": peer_card_sha256,
        "peer_card_verification_code": verification_code(peer_card_sha256),
        "peer_card_sha256_pinned": True,
        "peer_trust_created": True,
        "membership_changed": True,
        "membership_state_generation": 1,
        "membership_policy_epoch": 1,
        "membership_entry_count": 1,
    }
    for field, wanted in expected.items():
        if value.get(field) != wanted:
            fail(
                f"{label} field {field!r} was {value.get(field)!r}, "
                f"expected {wanted!r}: {json.dumps(value, sort_keys=True)}"
            )
    for field in (
        "configuration_bytes",
        "network_step_horizon_seconds",
    ):
        if not isinstance(value.get(field), int) or value[field] <= 0:
            fail(f"{label} omitted positive integer field {field!r}")
    for field in ("local_spki_sha256", "membership_chain_digest"):
        digest = value.get(field)
        if not isinstance(digest, str) or len(digest) != 64:
            fail(f"{label} omitted exact digest field {field!r}")
    require_mode(config, 0o600, f"{label} service configuration")
    require_mode(identity / "peer-trust.pem", 0o600, f"{label} peer trust")
    require_mode(status.parent, 0o700, f"{label} runtime directory")
    return config, status


def membership_tuple(replica: Path, manifest: Path, label: str) -> tuple[Any, ...]:
    status = run_json(
        [str(replica), "status", "--manifest", str(manifest)], label=label
    )
    return (
        status.get("membership_status_present"),
        status.get("membership_state_generation"),
        status.get("membership_policy_epoch"),
        status.get("membership_entry_count"),
        status.get("membership_chain_digest"),
        status.get("membership_anchor_matches_current"),
    )


def start_service(
    sync: Path,
    config: Path,
    environment: Mapping[str, str],
) -> subprocess.Popen[str]:
    service_environment = dict(environment)
    service_environment.pop("NOTIFY_SOCKET", None)
    return subprocess.Popen(
        [str(sync), "run", "--config", str(config)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=service_environment,
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

    with tempfile.TemporaryDirectory(prefix="anonsync-linking-") as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        source_manifest, source_files = init_combined(
            replica, root / "source", "source"
        )
        receiver_manifest, receiver_files = init_combined(
            replica, root / "receiver", "receiver"
        )
        run_json(
            [str(folder), "init", "--manifest", str(source_manifest)],
            label="source linking folder catalog init",
        )
        run_json(
            [str(folder), "init", "--manifest", str(receiver_manifest)],
            label="receiver linking folder catalog init",
        )

        source_environment, source_home, source_runtime = user_environment(
            root, "source-link"
        )
        receiver_environment, receiver_home, receiver_runtime = user_environment(
            root, "receiver-link"
        )
        source_instance = "source-peer"
        receiver_instance = "receiver-peer"
        source_identity_command = [
            str(sync),
            "identity-create",
            "--instance",
            source_instance,
            "--manifest",
            str(source_manifest),
        ]
        receiver_identity_command = [
            str(sync),
            "identity-create",
            "--instance",
            receiver_instance,
            "--manifest",
            str(receiver_manifest),
        ]
        source_created = run_json_environment(
            source_identity_command,
            environment=source_environment,
            label="source linked identity creation",
        )
        receiver_created = run_json_environment(
            receiver_identity_command,
            environment=receiver_environment,
            label="receiver linked identity creation",
        )
        source_key, source_certificate, source_card, source_trust = (
            require_identity_summary(
                source_created,
                instance=source_instance,
                home=source_home,
                local_device="source",
                dispositions="created",
                label="source linked identity creation",
            )
        )
        receiver_key, receiver_certificate, receiver_card, receiver_trust = (
            require_identity_summary(
                receiver_created,
                instance=receiver_instance,
                home=receiver_home,
                local_device="receiver",
                dispositions="created",
                label="receiver linked identity creation",
            )
        )

        source_key_exact = source_key.read_bytes()
        receiver_key_exact = receiver_key.read_bytes()
        source_certificate_exact = source_certificate.read_bytes()
        receiver_certificate_exact = receiver_certificate.read_bytes()
        source_card_exact = source_card.read_bytes()
        receiver_card_exact = receiver_card.read_bytes()
        source_card_sha256 = hashlib.sha256(source_card_exact).hexdigest()
        receiver_card_sha256 = hashlib.sha256(receiver_card_exact).hexdigest()

        identity_root = source_home / ".config/anonsync/linked-identities"
        key_prefix_instance = "key-prefix"
        key_prefix_identity = identity_root / key_prefix_instance
        key_prefix_identity.mkdir(mode=0o700)
        os.chmod(key_prefix_identity, 0o700)
        key_prefix_path = key_prefix_identity / "local.key"
        key_prefix_path.write_bytes(source_key_exact)
        os.chmod(key_prefix_path, 0o600)
        key_prefix_created = run_json_environment(
            [
                str(sync),
                "identity-create",
                "--instance",
                key_prefix_instance,
                "--manifest",
                str(source_manifest),
            ],
            environment=source_environment,
            label="key-prefix linked identity resume",
        )
        require_identity_summary(
            key_prefix_created,
            instance=key_prefix_instance,
            home=source_home,
            local_device="source",
            dispositions=("reused_exact", "created", "created"),
            label="key-prefix linked identity resume",
        )

        certificate_prefix_instance = "certificate-prefix"
        certificate_prefix_identity = (
            identity_root / certificate_prefix_instance
        )
        certificate_prefix_identity.mkdir(mode=0o700)
        os.chmod(certificate_prefix_identity, 0o700)
        for basename, exact in (
            ("local.key", source_key_exact),
            ("local.pem", source_certificate_exact),
        ):
            path = certificate_prefix_identity / basename
            path.write_bytes(exact)
            os.chmod(path, 0o600)
        certificate_prefix_created = run_json_environment(
            [
                str(sync),
                "identity-create",
                "--instance",
                certificate_prefix_instance,
                "--manifest",
                str(source_manifest),
            ],
            environment=source_environment,
            label="certificate-prefix linked identity resume",
        )
        _, _, certificate_prefix_card, _ = require_identity_summary(
            certificate_prefix_created,
            instance=certificate_prefix_instance,
            home=source_home,
            local_device="source",
            dispositions=("reused_exact", "reused_exact", "created"),
            label="certificate-prefix linked identity resume",
        )
        if certificate_prefix_card.read_bytes() != source_card_exact:
            fail("certificate-prefix resume did not recreate the exact card")

        orphan_certificate_identity = identity_root / "orphan-certificate"
        orphan_certificate_identity.mkdir(mode=0o700)
        os.chmod(orphan_certificate_identity, 0o700)
        orphan_certificate = orphan_certificate_identity / "local.pem"
        orphan_certificate.write_bytes(receiver_certificate_exact)
        os.chmod(orphan_certificate, 0o600)
        expect_json_failure(
            [
                str(sync),
                "identity-create",
                "--instance",
                "orphan-certificate",
                "--manifest",
                str(source_manifest),
            ],
            environment=source_environment,
            label="orphaned linked-peer certificate",
            message_contains="certificate without its private key",
        )
        if (orphan_certificate_identity / "local.key").exists() or (
            orphan_certificate_identity / "pairing-card.json"
        ).exists():
            fail("orphaned certificate recovery published new identity bytes")

        orphan_card_identity = identity_root / "orphan-card"
        orphan_card_identity.mkdir(mode=0o700)
        os.chmod(orphan_card_identity, 0o700)
        orphan_card = orphan_card_identity / "pairing-card.json"
        orphan_card.write_bytes(source_card_exact)
        os.chmod(orphan_card, 0o600)
        expect_json_failure(
            [
                str(sync),
                "identity-create",
                "--instance",
                "orphan-card",
                "--manifest",
                str(source_manifest),
            ],
            environment=source_environment,
            label="orphaned linked-peer card",
            message_contains="without its complete key and certificate prefix",
        )
        if (orphan_card_identity / "local.key").exists() or (
            orphan_card_identity / "local.pem"
        ).exists():
            fail("orphaned card recovery published new identity bytes")

        for label, card_exact, key_exact, local, pin in (
            (
                "source",
                source_card_exact,
                source_key_exact,
                "source",
                source_created["spki_sha256"],
            ),
            (
                "receiver",
                receiver_card_exact,
                receiver_key_exact,
                "receiver",
                receiver_created["spki_sha256"],
            ),
        ):
            if key_exact in card_exact or b"BEGIN PRIVATE KEY" in card_exact:
                fail(f"{label} pairing card leaked private-key bytes")
            card_value = json.loads(
                card_exact.decode("utf-8"),
                object_pairs_hook=unique_json_object_pairs,
            )
            if not isinstance(card_value, dict):
                fail(f"{label} pairing card is not a JSON object")
            expected_keys = {
                "schema",
                "folder_id",
                "device_id",
                "epoch",
                "spki_sha256",
                "certificate_pem",
                "signature_ed25519",
            }
            if set(card_value) != expected_keys:
                fail(f"{label} pairing card has unexpected fields")
            if card_value.get("schema") != "anonsync.linked-peer-card.v1":
                fail(f"{label} pairing card schema is not exact")
            if card_value.get("folder_id") != "reconciliation-process":
                fail(f"{label} pairing card folder binding is not exact")
            if card_value.get("device_id") != local or card_value.get(
                "epoch"
            ) != 1:
                fail(f"{label} pairing card actor binding is not exact")
            if card_value.get("spki_sha256") != pin:
                fail(f"{label} pairing card SPKI binding is not exact")
            signature = card_value.get("signature_ed25519")
            if not isinstance(signature, str) or len(signature) != 128:
                fail(f"{label} pairing card signature is not exact Ed25519 hex")

        source_resumed = run_json_environment(
            source_identity_command,
            environment=source_environment,
            label="source linked identity resume",
        )
        receiver_resumed = run_json_environment(
            receiver_identity_command,
            environment=receiver_environment,
            label="receiver linked identity resume",
        )
        require_identity_summary(
            source_resumed,
            instance=source_instance,
            home=source_home,
            local_device="source",
            dispositions="reused_exact",
            label="source linked identity resume",
        )
        require_identity_summary(
            receiver_resumed,
            instance=receiver_instance,
            home=receiver_home,
            local_device="receiver",
            dispositions="reused_exact",
            label="receiver linked identity resume",
        )
        if (
            source_key.read_bytes() != source_key_exact
            or receiver_key.read_bytes() != receiver_key_exact
            or source_card.read_bytes() != source_card_exact
            or receiver_card.read_bytes() != receiver_card_exact
        ):
            fail("identity resume changed immutable key or card bytes")

        source_before = membership_tuple(
            replica, source_manifest, "source membership before linking"
        )
        tampered_card = root / "tampered-receiver-card.json"
        tampered_exact = receiver_card_exact.replace(
            b'"device_id":"receiver"', b'"device_id":"attacker"', 1
        )
        if tampered_exact == receiver_card_exact:
            fail("could not construct the signed-card substitution fixture")
        tampered_card.write_bytes(tampered_exact)
        os.chmod(tampered_card, 0o600)
        source_port = reserve_port()
        receiver_port = reserve_port()
        while receiver_port == source_port:
            receiver_port = reserve_port()
        wrong_pin_command = direct_link_command(
            sync,
            source_manifest,
            receiver_card,
            source_instance,
            source_port,
            receiver_port,
            "0" * 64,
        )
        expect_json_failure(
            wrong_pin_command,
            environment=source_environment,
            label="pairing-card fingerprint mismatch",
            message_contains="does not match the exact peer card",
        )
        tampered_command = direct_link_command(
            sync,
            source_manifest,
            tampered_card,
            source_instance,
            source_port,
            receiver_port,
        )
        expect_json_failure(
            tampered_command,
            environment=source_environment,
            label="signed pairing-card actor substitution",
            message_contains="signature does not verify",
        )
        source_config = (
            source_home
            / ".config/anonsync/linked-peers"
            / f"{source_instance}.json"
        )
        if source_config.exists() or source_trust.exists():
            fail("rejected pairing card created trust or service configuration")
        if membership_tuple(
            replica,
            source_manifest,
            "source membership after rejected linking",
        ) != source_before:
            fail("rejected pairing card changed durable membership")

        source_command = direct_link_command(
            sync,
            source_manifest,
            receiver_card,
            source_instance,
            source_port,
            receiver_port,
            receiver_card_sha256,
        )
        receiver_command = direct_link_command(
            sync,
            receiver_manifest,
            source_card,
            receiver_instance,
            receiver_port,
            source_port,
            source_card_sha256,
        )
        source_linked = run_json_environment(
            source_command,
            environment=source_environment,
            label="source explicit peer linking",
        )
        receiver_linked = run_json_environment(
            receiver_command,
            environment=receiver_environment,
            label="receiver explicit peer linking",
        )
        source_config, source_status = require_link_summary(
            source_linked,
            instance=source_instance,
            home=source_home,
            runtime=source_runtime,
            local="source",
            remote="receiver",
            peer_card=receiver_card,
            local_card_sha256=source_card_sha256,
            peer_card_sha256=receiver_card_sha256,
            listen_port=source_port,
            label="source explicit peer linking",
        )
        receiver_config, receiver_status = require_link_summary(
            receiver_linked,
            instance=receiver_instance,
            home=receiver_home,
            runtime=receiver_runtime,
            local="receiver",
            remote="source",
            peer_card=source_card,
            local_card_sha256=receiver_card_sha256,
            peer_card_sha256=source_card_sha256,
            listen_port=receiver_port,
            label="receiver explicit peer linking",
        )
        if source_trust.read_bytes() != receiver_certificate_exact:
            fail("source trust anchor is not the exact receiver certificate")
        if receiver_trust.read_bytes() != source_certificate_exact:
            fail("receiver trust anchor is not the exact source certificate")
        for label, config_exact, local_key in (
            ("source", source_config.read_bytes(), source_key_exact),
            ("receiver", receiver_config.read_bytes(), receiver_key_exact),
        ):
            if local_key in config_exact or b"BEGIN PRIVATE KEY" in config_exact:
                fail(f"{label} linked service configuration embedded key bytes")

        source_after_link = membership_tuple(
            replica, source_manifest, "source membership after linking"
        )
        receiver_after_link = membership_tuple(
            replica, receiver_manifest, "receiver membership after linking"
        )
        for label, value in (
            ("source", source_after_link),
            ("receiver", receiver_after_link),
        ):
            if value[0:4] != (True, 1, 1, 1) or value[5] is not True:
                fail(f"{label} durable membership was not exactly admitted: {value}")

        source_configuration_exact = source_config.read_bytes()
        expect_json_failure(
            source_command,
            environment=source_environment,
            label="duplicate linked-peer configuration",
            message_contains="already exists",
        )
        if source_config.read_bytes() != source_configuration_exact:
            fail("duplicate linking changed the immutable configuration")
        if membership_tuple(
            replica,
            source_manifest,
            "source membership after duplicate linking",
        ) != source_after_link:
            fail("configuration preflight failure changed durable membership")

        source_nested = source_files / "source-side" / "nested"
        receiver_nested = receiver_files / "receiver-side" / "nested"
        source_nested.mkdir(parents=True, mode=0o700)
        receiver_nested.mkdir(parents=True, mode=0o700)
        (source_nested / "alpha.txt").write_bytes(
            b"signed-card source payload\n"
        )
        (receiver_nested / "beta.txt").write_bytes(
            b"signed-card receiver payload\n"
        )

        source_service = start_service(sync, source_config, source_environment)
        receiver_service = start_service(
            sync, receiver_config, receiver_environment
        )
        try:
            wait_for_service_listener(
                source_service, source_port, "signed-card source service"
            )
            wait_for_service_listener(
                receiver_service, receiver_port, "signed-card receiver service"
            )
            wait_for_tree_convergence(
                source_files,
                receiver_files,
                "receiver-side/nested/beta.txt",
                "signed-card retained-service convergence",
                timeout=28.0,
            )
            source_service.send_signal(signal.SIGTERM)
            receiver_service.send_signal(signal.SIGTERM)
            source_terminal = finish_service(
                source_service, "signed-card source service", timeout=18.0
            )
            receiver_terminal = finish_service(
                receiver_service, "signed-card receiver service", timeout=18.0
            )
        finally:
            for process in (source_service, receiver_service):
                if process.poll() is None:
                    process.kill()
                    process.communicate(timeout=2.0)
        if source_terminal.get("stop_reason") != "stop_requested" or (
            receiver_terminal.get("stop_reason") != "stop_requested"
        ):
            fail("signed-card services did not classify controlled shutdown")
        if source_status.exists() or receiver_status.exists():
            fail("signed-card service shutdown left a status socket")
        if tree_snapshot(source_files) != tree_snapshot(receiver_files):
            fail("signed-card linked services did not converge exact trees")

    print(
        "anonsync signed-card linking process test: identity resume, "
        "signature rejection, explicit admission, and two-peer convergence passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
