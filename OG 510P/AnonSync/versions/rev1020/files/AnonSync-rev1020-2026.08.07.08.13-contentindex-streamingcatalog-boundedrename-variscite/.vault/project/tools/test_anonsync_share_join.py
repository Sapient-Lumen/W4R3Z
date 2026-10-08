#!/usr/bin/env python3
"""Prove one pinned second-peer command reaches the retained C++ service.

The origin starts as an ordinary populated folder and uses share-create.  The
joining peer receives only the origin's signed public card plus an out-of-band
SHA-256 pin, explicitly chooses populated-folder adoption, and runs share-join.
That one command must create the matching local share, publish its response
card, admit exact trust and membership, and provision the existing service.
The origin then links the response card and both unmodified retained services
must converge the two pre-existing trees in both directions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import stat
import subprocess
import tempfile
from typing import Any, Mapping, Sequence

from test_anonsync_replica_anonymous_routes import I2P_PEER, VALID_ONION
from test_anonsync_linking import (
    direct_link_command,
    membership_tuple,
    require_link_summary,
    start_service,
    verification_code,
)
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
from test_anonsync_sync_process import fail, reserve_port, run_json, tree_snapshot


def require_mode(path: Path, mode: int, label: str) -> None:
    status = path.lstat()
    if stat.S_ISLNK(status.st_mode):
        fail(f"{label} is a symbolic link: {path}")
    observed = stat.S_IMODE(status.st_mode)
    if observed != mode:
        fail(f"{label} mode is {observed:o}, expected {mode:o}: {path}")


def require_fields(
    value: Mapping[str, Any], expected: Mapping[str, Any], label: str
) -> None:
    for key, wanted in expected.items():
        observed = value.get(key)
        if observed != wanted:
            fail(
                f"{label} field {key!r} was {observed!r}, expected "
                f"{wanted!r}: {json.dumps(value, sort_keys=True)}"
            )


def direct_join_command(
    sync: Path,
    *,
    instance: str,
    state: Path,
    files: Path,
    local_device: str,
    peer_card: Path,
    peer_card_sha256: str | None,
    listen_port: int,
    remote_port: int,
    initial_files: str,
) -> list[str]:
    command = [
        str(sync),
        "share-join",
        "--instance",
        instance,
        "--state-directory",
        str(state),
        "--files-root",
        str(files),
        "--initial-files",
        initial_files,
        "--local-device",
        local_device,
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


def anonymous_join_command(
    sync: Path,
    *,
    transport: str,
    instance: str,
    state: Path,
    files: Path,
    local_device: str,
    peer_card: Path,
    peer_card_sha256: str,
    listen_port: int,
) -> list[str]:
    command = [
        str(sync),
        "share-join",
        "--instance",
        instance,
        "--state-directory",
        str(state),
        "--files-root",
        str(files),
        "--initial-files",
        "empty",
        "--local-device",
        local_device,
        "--peer-card",
        str(peer_card),
        "--peer-card-sha256",
        peer_card_sha256,
        "--transport",
        transport,
    ]
    if transport == "tor":
        command.extend(
            [
                "--onion-address",
                VALID_ONION,
                "--onion-port",
                "443",
                "--tor-socks-address",
                "127.0.0.1",
                "--tor-socks-port",
                "9050",
                # Deliberately omit --tor-isolation-token: the retained
                # configuration must derive one stable exact-replay default.
            ]
        )
        timeout = "3"
        maximum_runtime = "15"
    elif transport == "i2p":
        command.extend(
            [
                "--i2p-sam-address",
                "127.0.0.1",
                "--i2p-sam-port",
                "7656",
                "--i2p-destination",
                I2P_PEER,
                # Deliberately omit --i2p-session-id and a private destination:
                # the transient retained session name must still be replayable.
            ]
        )
        timeout = "180"
        maximum_runtime = "1080"
    else:
        fail(f"unsupported anonymous replay transport: {transport}")
    command.extend(
        [
            "--ingress",
            "direct",
            "--bind-address",
            "127.0.0.1",
            "--listen-port",
            str(listen_port),
            "--timeout-seconds",
            timeout,
            "--max-runtime-seconds",
            maximum_runtime,
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
            "1200" if transport == "i2p" else "35",
        ]
    )
    return command


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replica", required=True, type=Path)
    parser.add_argument("--folder", required=True, type=Path)
    parser.add_argument("--sync", required=True, type=Path)
    args = parser.parse_args()
    replica = args.replica.resolve(strict=True)
    folder = args.folder.resolve(strict=True)
    sync = args.sync.resolve(strict=True)
    if replica.parent != sync.parent or folder.parent != sync.parent:
        fail("share-join proof requires exact co-installed sibling binaries")

    with tempfile.TemporaryDirectory(prefix="anonsync-share-join-") as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        origin_environment, origin_home, origin_runtime = user_environment(
            root, "origin"
        )
        join_environment, join_home, join_runtime = user_environment(
            root, "join"
        )
        state_parent = root / "state"
        state_parent.mkdir(mode=0o700)
        origin_files = root / "origin-files"
        join_files = root / "join-files"
        refused_files = root / "refused-files"
        for directory in (origin_files, join_files, refused_files):
            directory.mkdir(mode=0o700)

        (origin_files / "origin" / "nested").mkdir(
            parents=True, mode=0o700
        )
        (origin_files / "origin" / "nested" / "alpha.txt").write_bytes(
            b"origin before pairing\n"
        )
        (join_files / "join" / "nested").mkdir(parents=True, mode=0o700)
        (join_files / "join" / "nested" / "beta.txt").write_bytes(
            b"joining peer before pairing\n"
        )
        (refused_files / "must-not-adopt.txt").write_bytes(b"occupied\n")

        origin_instance = "origin-peer"
        origin_state = state_parent / origin_instance
        origin_created = run_json_environment(
            [
                str(sync),
                "share-create",
                "--instance",
                origin_instance,
                "--state-directory",
                str(origin_state),
                "--files-root",
                str(origin_files),
                "--local-device",
                "origin-device",
            ],
            environment=origin_environment,
            label="origin populated share creation",
        )
        require_fields(
            origin_created,
            {
                "command": "share-create",
                "terminal_class": "ready_to_pair",
                "local_device_id": "origin-device",
                "initial_files": "adopt_existing",
            },
            "origin populated share creation",
        )
        origin_manifest = Path(origin_created["manifest_path"])
        origin_card = Path(origin_created["pairing_card_path"])
        origin_card_sha256 = hashlib.sha256(origin_card.read_bytes()).hexdigest()
        if origin_created.get("pairing_card_sha256") != origin_card_sha256:
            fail("origin share did not report the exact public-card digest")
        folder_id = origin_created.get("folder_id")
        if not isinstance(folder_id, str) or not folder_id.startswith("share-"):
            fail("origin share did not report its generated folder ID")

        origin_port = reserve_port()
        join_port = reserve_port()
        while join_port == origin_port:
            join_port = reserve_port()

        missing_pin_instance = "missing-pin"
        missing_pin_state = state_parent / missing_pin_instance
        missing_pin_command = direct_join_command(
            sync,
            instance=missing_pin_instance,
            state=missing_pin_state,
            files=refused_files,
            local_device="missing-pin-device",
            peer_card=origin_card,
            peer_card_sha256=None,
            listen_port=reserve_port(),
            remote_port=origin_port,
            initial_files="adopt-existing",
        )
        expect_json_failure(
            missing_pin_command,
            environment=join_environment,
            label="unpinned second-peer join",
            message_contains="--peer-card-sha256 is required",
        )
        if missing_pin_state.exists():
            fail("unpinned join created local share state")

        wrong_pin_instance = "wrong-pin"
        wrong_pin_state = state_parent / wrong_pin_instance
        wrong_pin_command = direct_join_command(
            sync,
            instance=wrong_pin_instance,
            state=wrong_pin_state,
            files=refused_files,
            local_device="wrong-pin-device",
            peer_card=origin_card,
            peer_card_sha256="0" * 64,
            listen_port=reserve_port(),
            remote_port=origin_port,
            initial_files="adopt-existing",
        )
        expect_json_failure(
            wrong_pin_command,
            environment=join_environment,
            label="wrong-pinned second-peer join",
            message_contains="does not match the exact peer card",
        )
        if wrong_pin_state.exists():
            fail("wrong-pinned join created local share state")

        empty_refusal_instance = "empty-refusal"
        empty_refusal_state = state_parent / empty_refusal_instance
        empty_refusal_command = direct_join_command(
            sync,
            instance=empty_refusal_instance,
            state=empty_refusal_state,
            files=refused_files,
            local_device="empty-refusal-device",
            peer_card=origin_card,
            peer_card_sha256=origin_card_sha256,
            listen_port=reserve_port(),
            remote_port=origin_port,
            initial_files="empty",
        )
        expect_json_failure(
            empty_refusal_command,
            environment=join_environment,
            label="populated join without adoption",
            message_contains="files root must be empty for fresh bootstrap",
        )
        if (empty_refusal_state / "deployment.json").exists():
            fail("failed empty-folder join published a deployment manifest")
        refused_config = (
            join_home
            / ".config/anonsync/linked-peers"
            / f"{empty_refusal_instance}.json"
        )
        if refused_config.exists():
            fail("failed empty-folder join published a service configuration")

        join_instance = "joining-peer"
        join_state = state_parent / join_instance
        join_command = direct_join_command(
            sync,
            instance=join_instance,
            state=join_state,
            files=join_files,
            local_device="joining-device",
            peer_card=origin_card,
            peer_card_sha256=origin_card_sha256,
            listen_port=join_port,
            remote_port=origin_port,
            initial_files="adopt-existing",
        )
        joined = run_json_environment(
            join_command,
            environment=join_environment,
            label="pinned populated second-peer join",
        )
        join_config = (
            join_home
            / ".config/anonsync/linked-peers"
            / f"{join_instance}.json"
        )
        join_status = join_runtime / f"anonsync-{join_instance}" / "status.sock"
        join_identity = (
            join_home
            / ".config/anonsync/linked-identities"
            / join_instance
        )
        join_card = join_identity / "pairing-card.json"
        join_card_sha256 = hashlib.sha256(join_card.read_bytes()).hexdigest()
        require_fields(
            joined,
            {
                "command": "share-join",
                "terminal_class": "ready_to_start",
                "configuration_created": True,
                "configuration_disposition": "created",
                "instance": join_instance,
                "configuration_path": str(join_config),
                "status_socket": str(join_status),
                "systemd_unit": f"anonsync-linked-peer@{join_instance}.service",
                "folder_id": folder_id,
                "local_device_id": "joining-device",
                "remote_device_id": "origin-device",
                "transport": "direct_tcp",
                "ingress_transport": "direct_tcp",
                "peer_card_path": str(origin_card),
                "peer_card_sha256": origin_card_sha256,
                "peer_card_sha256_pinned": True,
                "peer_card_verification_code": verification_code(
                    origin_card_sha256
                ),
                "local_pairing_card_path": str(join_card),
                "local_pairing_card_sha256": join_card_sha256,
                "local_pairing_verification_code": verification_code(
                    join_card_sha256
                ),
                "state_directory": str(join_state),
                "files_root": str(join_files),
                "initial_files": "adopt_existing",
                "deployment_disposition": "initialized",
                "catalog_disposition": "initialized",
                "initial_local_published": 1,
                "initial_catalog_entry_count": 1,
                "ready_to_start": True,
                "systemd_start_command": (
                    "systemctl --user enable --now "
                    f"anonsync-linked-peer@{join_instance}.service"
                ),
            },
            "pinned populated second-peer join",
        )
        for path in (join_state, join_state / "payload", join_identity):
            require_mode(path, 0o700, "joined private directory")
        for path in (
            join_state / "deployment.json",
            join_config,
            join_identity / "local.key",
            join_identity / "local.pem",
            join_card,
            join_identity / "peer-trust.pem",
        ):
            require_mode(path, 0o600, "joined private file")
        if origin_card.read_bytes().find(b"BEGIN PRIVATE KEY") >= 0:
            fail("origin public card leaked private-key material")

        join_manifest = Path(joined["manifest_path"])
        join_membership = membership_tuple(
            replica, join_manifest, "joining membership after share-join"
        )
        if join_membership[0:4] != (True, 1, 1, 1) or join_membership[5] is not True:
            fail(f"share-join did not admit exact durable membership: {join_membership}")

        origin_link_command = direct_link_command(
            sync,
            origin_manifest,
            join_card,
            origin_instance,
            origin_port,
            join_port,
            join_card_sha256,
        )
        origin_linked = run_json_environment(
            origin_link_command,
            environment=origin_environment,
            label="origin response-card linking",
        )
        origin_config, origin_status = require_link_summary(
            origin_linked,
            instance=origin_instance,
            home=origin_home,
            runtime=origin_runtime,
            local="origin-device",
            remote="joining-device",
            peer_card=join_card,
            local_card_sha256=origin_card_sha256,
            peer_card_sha256=join_card_sha256,
            listen_port=origin_port,
            label="origin response-card linking",
        )

        join_membership_before_duplicate = membership_tuple(
            replica, join_manifest, "joining membership before duplicate join"
        )
        join_config_exact = join_config.read_bytes()
        resumed = run_json_environment(
            join_command,
            environment=join_environment,
            label="exact repeated second-peer join",
        )
        require_fields(
            resumed,
            {
                "command": "share-join",
                "terminal_class": "ready_to_start",
                "configuration_created": False,
                "configuration_disposition": "resumed_exact",
                "deployment_disposition": "resumed_exact",
                "catalog_disposition": "reused_existing",
                "initial_local_published": 0,
                "peer_trust_created": False,
                "membership_changed": False,
                "ready_to_start": True,
            },
            "exact repeated second-peer join",
        )
        if join_config.read_bytes() != join_config_exact:
            fail("repeated share-join changed immutable service configuration")
        if membership_tuple(
            replica, join_manifest, "joining membership after repeated join"
        ) != join_membership_before_duplicate:
            fail("repeated share-join changed durable membership")

        # Fresh-folder policy is a bootstrap admission choice, not a permanent
        # ban on replay after the share becomes live. An exact retry requesting
        # the conservative empty policy must therefore resume the committed
        # deployment even though its files root is already populated.
        empty_replay_command = list(join_command)
        empty_replay_command[
            empty_replay_command.index("--initial-files") + 1
        ] = "empty"
        empty_replay = run_json_environment(
            empty_replay_command,
            environment=join_environment,
            label="committed share-join empty-policy replay",
        )
        require_fields(
            empty_replay,
            {
                "command": "share-join",
                "configuration_created": False,
                "configuration_disposition": "resumed_exact",
                "deployment_disposition": "resumed_exact",
                "initial_files": "empty",
                "membership_changed": False,
            },
            "committed share-join empty-policy replay",
        )
        if join_config.read_bytes() != join_config_exact:
            fail("empty-policy replay changed immutable service configuration")
        if membership_tuple(
            replica, join_manifest, "membership after empty-policy replay"
        ) != join_membership_before_duplicate:
            fail("empty-policy replay changed durable membership")

        # Omitted Tor and I2P retained-session tokens must be deterministic for
        # the exact linked-share scope. Before this regression, a retry minted a
        # new random token and collided with its own immutable configuration.
        for transport in ("tor", "i2p"):
            replay_environment, replay_home, _ = user_environment(
                root, f"{transport}-stable-replay"
            )
            replay_instance = f"{transport}-stable-replay"
            replay_state = state_parent / replay_instance
            replay_files = root / f"{transport}-stable-files"
            replay_files.mkdir(mode=0o700)
            replay_command = anonymous_join_command(
                sync,
                transport=transport,
                instance=replay_instance,
                state=replay_state,
                files=replay_files,
                local_device=f"{transport}-stable-device",
                peer_card=origin_card,
                peer_card_sha256=origin_card_sha256,
                listen_port=reserve_port(),
            )
            first_route_join = run_json_environment(
                replay_command,
                environment=replay_environment,
                label=f"{transport} stable-default first join",
            )
            replay_config = Path(first_route_join["configuration_path"])
            replay_exact = replay_config.read_bytes()
            second_route_join = run_json_environment(
                replay_command,
                environment=replay_environment,
                label=f"{transport} stable-default repeated join",
            )
            require_fields(
                second_route_join,
                {
                    "configuration_created": False,
                    "configuration_disposition": "resumed_exact",
                    "deployment_disposition": "resumed_exact",
                    "membership_changed": False,
                },
                f"{transport} stable-default repeated join",
            )
            if replay_config.read_bytes() != replay_exact:
                fail(f"{transport} stable-default replay changed config bytes")

            if transport == "tor":
                # Install a same-peer but non-exact immutable document in a new
                # instance. The new local share may be bootstrapped, but exact
                # service inspection must reject before peer membership/trust
                # admission mutates it.
                conflict_instance = "tor-conflict-preflight"
                conflict_environment = dict(replay_environment)
                conflict_state = state_parent / conflict_instance
                conflict_files = root / "tor-conflict-files"
                conflict_files.mkdir(mode=0o700)
                # Prepare the same local share/identity without admitting a
                # peer, then provide a bounded placeholder CA file so exact
                # configuration encoding can reach the immutable-byte conflict
                # check before membership admission.
                run_json_environment(
                    [
                        str(sync),
                        "share-create",
                        "--instance",
                        conflict_instance,
                        "--state-directory",
                        str(conflict_state),
                        "--files-root",
                        str(conflict_files),
                        "--folder",
                        folder_id,
                        "--local-device",
                        "tor-conflict-device",
                    ],
                    environment=conflict_environment,
                    label="conflicting preflight local share",
                )
                conflict_identity = (
                    replay_home
                    / ".config/anonsync/linked-identities"
                    / conflict_instance
                )
                conflict_trust = conflict_identity / "peer-trust.pem"
                marker = b"preflight-only trust placeholder\n"
                descriptor = os.open(
                    conflict_trust, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
                )
                try:
                    if os.write(descriptor, marker) != len(marker):
                        fail("short conflicting-preflight trust write")
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
                conflict_config = (
                    replay_home
                    / ".config/anonsync/linked-peers"
                    / f"{conflict_instance}.json"
                )
                shutil.copyfile(replay_config, conflict_config)
                conflict_config.chmod(0o600)
                conflict_command = anonymous_join_command(
                    sync,
                    transport="tor",
                    instance=conflict_instance,
                    state=conflict_state,
                    files=conflict_files,
                    local_device="tor-conflict-device",
                    peer_card=origin_card,
                    peer_card_sha256=origin_card_sha256,
                    listen_port=reserve_port(),
                )
                expect_json_failure(
                    conflict_command,
                    environment=conflict_environment,
                    message_contains="existing configuration conflicts",
                    label="conflicting exact-service preflight",
                )
                conflict_manifest = conflict_state / "deployment.json"
                conflict_status = run_json(
                    [str(replica), "status", "--manifest", str(conflict_manifest)],
                    label="conflicting preflight membership status",
                )
                if conflict_status.get("membership_entry_count") != 0:
                    fail("configuration conflict admitted peer membership")
                if conflict_trust.read_bytes() != marker:
                    fail("configuration conflict changed peer trust")

        origin_service = start_service(sync, origin_config, origin_environment)
        join_service = start_service(sync, join_config, join_environment)
        try:
            wait_for_service_listener(
                origin_service, origin_port, "origin joined service"
            )
            wait_for_service_listener(
                join_service, join_port, "joining retained service"
            )
            wait_for_tree_convergence(
                origin_files,
                join_files,
                "join/nested/beta.txt",
                "share-join initial bidirectional convergence",
                timeout=30.0,
            )
            (join_files / "join" / "after-start.txt").write_bytes(
                b"post-start edit from joining peer\n"
            )
            wait_for_tree_convergence(
                origin_files,
                join_files,
                "join/after-start.txt",
                "share-join post-start convergence",
                timeout=25.0,
            )
            origin_service.send_signal(signal.SIGTERM)
            join_service.send_signal(signal.SIGTERM)
            origin_terminal = finish_service(
                origin_service, "origin joined service", timeout=18.0
            )
            join_terminal = finish_service(
                join_service, "joining retained service", timeout=18.0
            )
        finally:
            for process in (origin_service, join_service):
                if process.poll() is None:
                    process.kill()
                    process.communicate(timeout=2.0)
        if origin_terminal.get("stop_reason") != "stop_requested" or (
            join_terminal.get("stop_reason") != "stop_requested"
        ):
            fail("share-join services did not classify controlled shutdown")
        if origin_status.exists() or join_status.exists():
            fail("share-join service shutdown left a status socket")
        if tree_snapshot(origin_files) != tree_snapshot(join_files):
            fail("share-join retained services did not converge exact trees")

    print(
        "anonsync share-join process test: mandatory pin, explicit adoption, "
        "exact restart, stable Tor/I2P defaults, conflict preflight, "
        "response-card linking, and retained two-peer convergence passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
