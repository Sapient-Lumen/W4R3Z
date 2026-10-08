#!/usr/bin/env python3
"""Exercise the populated-folder first-share workflow through shipped C++ owners.

The proof starts with ordinary nested files, no deployment, no catalog, and no
identity.  One share-create invocation must bootstrap the full local state,
publish the existing regular files, and emit a signed public pairing card.  A
repeat must be an exact no-op, while a later file addition must publish exactly
one new operation.  The test also keeps fresh replica bootstrap fail-closed
unless populated-folder adoption was selected explicitly and proves ambient
PATH cannot substitute the composed replica/folder executables.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
from typing import Any, Mapping, NoReturn, Sequence


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


def parse_json(text: str, label: str) -> dict[str, Any]:
    try:
        value = json.loads(text, object_pairs_hook=unique_json_object_pairs)
    except (json.JSONDecodeError, ValueError) as error:
        fail(f"{label} did not emit one unique-key JSON object: {error}: {text}")
    if not isinstance(value, dict):
        fail(f"{label} JSON is not an object")
    return value


def run_json(
    command: Sequence[str],
    *,
    environment: Mapping[str, str],
    label: str,
    timeout: float = 60.0,
) -> dict[str, Any]:
    completed = subprocess.run(
        list(command), check=False, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, env=dict(environment),
        timeout=timeout,
    )
    value = parse_json(completed.stdout, label)
    if completed.returncode != 0:
        fail(
            f"{label} failed with {completed.returncode}\n"
            f"command: {' '.join(command)}\nstdout:\n{completed.stdout}"
            f"stderr:\n{completed.stderr}"
        )
    if completed.stderr:
        fail(f"{label} wrote diagnostics on success: {completed.stderr}")
    return value


def expect_sync_failure(
    command: Sequence[str],
    *,
    environment: Mapping[str, str],
    error_code: str,
    message_fragment: str,
    label: str,
) -> dict[str, Any]:
    completed = subprocess.run(
        list(command), check=False, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, env=dict(environment),
        timeout=30.0,
    )
    if completed.returncode == 0:
        fail(f"{label} unexpectedly succeeded: {completed.stdout}")
    value = parse_json(completed.stdout, label)
    if value.get("terminal_class") != "stopped":
        fail(f"{label} did not report a stopped terminal class: {value}")
    if value.get("error_code") != error_code:
        fail(f"{label} error code was not {error_code!r}: {value}")
    message = value.get("message")
    if not isinstance(message, str) or message_fragment not in message:
        fail(
            f"{label} message omitted {message_fragment!r}: "
            f"{json.dumps(value, sort_keys=True)}"
        )
    if message_fragment not in completed.stderr:
        fail(f"{label} stderr omitted the same diagnostic: {completed.stderr}")
    return value


def expect_fields(
    value: Mapping[str, Any], expected: Mapping[str, Any], label: str
) -> None:
    for key, wanted in expected.items():
        observed = value.get(key)
        if observed != wanted:
            fail(
                f"{label} field {key!r} was {observed!r}, expected "
                f"{wanted!r}: {json.dumps(value, sort_keys=True)}"
            )


def require_mode(path: Path, mode: int, label: str) -> None:
    status = path.lstat()
    if stat.S_ISLNK(status.st_mode):
        fail(f"{label} is a symbolic link: {path}")
    observed = stat.S_IMODE(status.st_mode)
    if observed != mode:
        fail(f"{label} mode is {observed:o}, expected {mode:o}: {path}")


def require_digest(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or value != value.lower()
        or any(byte not in "0123456789abcdef" for byte in value)
    ):
        fail(f"{label} is not one lowercase SHA-256 digest: {value!r}")
    return value


SHARE_CREATE_DEFAULT_MAX_PAYLOAD_BYTES = 64 * 1024 * 1024 * 1024


def share_command(
    sync: Path, instance: str, state: Path, files: Path
) -> list[str]:
    return [
        str(sync), "share-create",
        "--instance", instance,
        "--state-directory", str(state),
        "--files-root", str(files),
    ]


def replica_init_command(
    replica: Path,
    *,
    state: Path,
    files: Path,
    folder_id: str,
    local_device: str,
    adopt_existing: bool,
) -> list[str]:
    command = [
        str(replica), "init",
        "--manifest", str(state / "deployment.json"),
        "--replica-db", str(state / "replica.sqlite3"),
        "--payload-root", str(state / "payload"),
        "--effect-db", str(state / "effects.sqlite3"),
        "--files-root", str(files),
        "--membership-db", str(state / "membership.sqlite3"),
        "--anchor-db", str(state / "membership-anchor.sqlite3"),
        "--folder", folder_id,
        "--local-device", local_device,
        "--local-epoch", "1",
        "--max-payload-bytes", "67108864",
    ]
    if adopt_existing:
        command.extend(["--initial-files", "adopt-existing"])
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
        fail("share-create process proof requires co-installed sibling binaries")

    with tempfile.TemporaryDirectory(prefix="anonsync-share-create-") as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        home = root / "home"
        state_parent = root / "state"
        files = root / "files"
        shadow = root / "path-shadow"
        for directory in (home, state_parent, files, shadow):
            directory.mkdir(mode=0o700)
        # Linux can propagate this bit into mkdir children. The C++ layout owner
        # must normalize only the directories it created and preserve the parent.
        os.chmod(state_parent, 0o2700)

        (files / "nested").mkdir(mode=0o700)
        (files / "alpha.txt").write_text("alpha\n", encoding="utf-8")
        (files / "nested" / "beta.txt").write_text(
            "nested beta\n", encoding="utf-8"
        )
        (files / "ignored-link").symlink_to("alpha.txt")
        os.mkfifo(files / "ignored-fifo", mode=0o600)

        marker = root / "ambient-path-was-used"
        for basename in ("anonsync_replica", "anonsync_folder"):
            fake = shadow / basename
            fake.write_text(
                "#!/bin/sh\nprintf '%s\\n' invoked >> "
                + repr(str(marker))
                + "\nexit 99\n",
                encoding="utf-8",
            )
            os.chmod(fake, 0o700)

        environment = os.environ.copy()
        environment.pop("NOTIFY_SOCKET", None)
        environment["HOME"] = str(home)
        environment["PATH"] = str(shadow)

        instance = "photos-main"
        state = state_parent / instance
        command = share_command(sync, instance, state, files)
        first = run_json(
            command, environment=environment, label="first populated share"
        )
        expect_fields(
            first,
            {
                "command": "share-create",
                "terminal_class": "ready_to_pair",
                "instance": instance,
                "state_directory": str(state),
                "state_directory_disposition": "created",
                "payload_root": str(state / "payload"),
                "payload_root_disposition": "created",
                "deployment_disposition": "initialized",
                "manifest_path": str(state / "deployment.json"),
                "files_root": str(files),
                "catalog_path": str(
                    state / "replica.sqlite3.folder-catalog.sqlite3"
                ),
                "catalog_disposition": "initialized",
                "catalog_entry_count_before": 0,
                "catalog_entry_count_after": 2,
                "local_epoch": 1,
                "max_payload_bytes": SHARE_CREATE_DEFAULT_MAX_PAYLOAD_BYTES,
                "private_key_disposition": "created",
                "certificate_disposition": "created",
                "pairing_card_disposition": "created",
                "ready_to_link": True,
            },
            "first populated share",
        )
        folder_id = first.get("folder_id")
        local_device = first.get("local_device_id")
        if not isinstance(folder_id, str) or not folder_id.startswith("share-"):
            fail("first share did not generate one share ID")
        if not isinstance(local_device, str) or not local_device.startswith(
            "device-"
        ):
            fail("first share did not generate one local device ID")
        deployment_id = require_digest(
            first.get("deployment_id"), "deployment ID"
        )
        manifest_digest = require_digest(
            first.get("deployment_manifest_digest"), "manifest digest"
        )
        card_digest = require_digest(
            first.get("pairing_card_sha256"), "pairing-card digest"
        )
        initial_pass = first.get("initial_pass")
        if not isinstance(initial_pass, dict):
            fail("first share omitted the initial folder pass")
        expect_fields(
            initial_pass,
            {
                "regular_files": 2,
                "ignored_symbolic_links": 1,
                "ignored_special_files": 1,
                "local_published": 2,
                "local_catalog_no_op": 0,
                "remote_applied": 0,
                "used_idle_fast_path": False,
            },
            "first populated share pass",
        )
        if marker.exists():
            fail("share-create selected an ambient PATH executable")

        require_mode(state_parent, 0o2700, "selected state parent")
        require_mode(state, 0o700, "created share state")
        require_mode(state / "payload", 0o700, "created payload root")
        for private_file in (
            state / "deployment.json",
            state / "replica.sqlite3",
            state / "replica.sqlite3.folder-catalog.sqlite3",
            state / "effects.sqlite3",
            state / "membership.sqlite3",
            state / "membership-anchor.sqlite3",
        ):
            require_mode(private_file, 0o600, "local-share private file")

        identity = home / ".config/anonsync/linked-identities" / instance
        key = identity / "local.key"
        certificate = identity / "local.pem"
        card = identity / "pairing-card.json"
        require_mode(identity, 0o700, "share identity directory")
        for identity_file in (key, certificate, card):
            require_mode(identity_file, 0o600, "share identity file")
        if hashlib.sha256(card.read_bytes()).hexdigest() != card_digest:
            fail("share-create did not report the exact pairing-card digest")
        card_value = parse_json(card.read_text(encoding="utf-8"), "pairing card")
        expect_fields(
            card_value,
            {
                "schema": "anonsync.linked-peer-card.v1",
                "folder_id": folder_id,
                "device_id": local_device,
                "epoch": 1,
            },
            "pairing card",
        )
        if any("private" in key_name.lower() for key_name in card_value):
            fail("public pairing card contains a private-key field")

        status_first = run_json(
            [str(replica), "status", "--manifest", str(state / "deployment.json")],
            environment=environment,
            label="first share replica status",
        )
        expect_fields(
            status_first,
            {
                "folder_id": folder_id,
                "local_device_id": local_device,
                "replica_visible_paths": 2,
                "replica_evidence_operations": 2,
                "payload_entries": 2,
            },
            "first share replica status",
        )

        second = run_json(
            command, environment=environment, label="repeated populated share"
        )
        expect_fields(
            second,
            {
                "deployment_disposition": "resumed_exact",
                "catalog_disposition": "reused_existing",
                "state_directory_disposition": "reused_exact",
                "payload_root_disposition": "reused_exact",
                "catalog_entry_count_before": 2,
                "catalog_entry_count_after": 2,
                "folder_id": folder_id,
                "local_device_id": local_device,
                "deployment_id": deployment_id,
                "deployment_manifest_digest": manifest_digest,
                "pairing_card_sha256": card_digest,
                "private_key_disposition": "reused_exact",
                "certificate_disposition": "reused_exact",
                "pairing_card_disposition": "reused_exact",
            },
            "repeated populated share",
        )
        second_pass = second.get("initial_pass")
        if not isinstance(second_pass, dict):
            fail("repeated share omitted its folder pass")
        expect_fields(
            second_pass,
            {
                "local_published": 0,
                "local_catalog_no_op": 2,
                "used_idle_fast_path": True,
            },
            "repeated populated share pass",
        )

        (files / "nested" / "gamma.txt").write_text(
            "gamma\n", encoding="utf-8"
        )
        third = run_json(
            command, environment=environment, label="share after one addition"
        )
        expect_fields(
            third,
            {
                "catalog_entry_count_before": 2,
                "catalog_entry_count_after": 3,
                "folder_id": folder_id,
                "local_device_id": local_device,
                "pairing_card_sha256": card_digest,
            },
            "share after one addition",
        )
        third_pass = third.get("initial_pass")
        if not isinstance(third_pass, dict):
            fail("share after addition omitted its folder pass")
        expect_fields(
            third_pass,
            {
                "regular_files": 3,
                "local_published": 1,
                "local_catalog_no_op": 2,
                "used_idle_fast_path": False,
            },
            "share after one addition pass",
        )

        before_conflict = hashlib.sha256(
            (state / "deployment.json").read_bytes()
        ).hexdigest()
        conflict = [*command, "--folder", "share-conflicting"]
        expect_sync_failure(
            conflict,
            environment=environment,
            error_code="invalid_arguments",
            message_fragment="conflicts with the existing deployment",
            label="conflicting resumed folder ID",
        )
        if hashlib.sha256((state / "deployment.json").read_bytes()).hexdigest() != before_conflict:
            fail("conflicting resumed identity mutated the deployment manifest")

        overlap_files = root / "overlap-files"
        overlap_files.mkdir(mode=0o700)
        expect_sync_failure(
            share_command(
                sync, "inside-files", overlap_files / "inside-files",
                overlap_files,
            ),
            environment=environment,
            error_code="invalid_arguments",
            message_fragment="must be disjoint",
            label="overlapping state and files roots",
        )
        if (overlap_files / "inside-files").exists():
            fail("overlap rejection created a state directory")

        wrong_name = state_parent / "actual-name"
        expect_sync_failure(
            share_command(sync, "expected-name", wrong_name, files),
            environment=environment,
            error_code="invalid_arguments",
            message_fragment="basename must equal the instance ID",
            label="state basename mismatch",
        )
        if wrong_name.exists():
            fail("basename rejection created a state directory")

        wrong_mode_state = state_parent / "wrong-mode"
        wrong_mode_state.mkdir(mode=0o755)
        os.chmod(wrong_mode_state, 0o755)
        expect_sync_failure(
            share_command(sync, "wrong-mode", wrong_mode_state, files),
            environment=environment,
            error_code="operation_failed",
            message_fragment="must have exact mode 0700",
            label="existing public state directory",
        )
        require_mode(wrong_mode_state, 0o755, "rejected existing state")
        if (wrong_mode_state / "payload").exists():
            fail("wrong-mode rejection extended the state directory")

        fail_state = root / "default-empty-gate"
        fail_files = root / "default-empty-files"
        fail_state.mkdir(mode=0o700)
        (fail_state / "payload").mkdir(mode=0o700)
        fail_files.mkdir(mode=0o700)
        (fail_files / "existing.txt").write_text("existing\n", encoding="utf-8")
        default_bootstrap = replica_init_command(
            replica,
            state=fail_state,
            files=fail_files,
            folder_id="share-default-empty-gate",
            local_device="device-default-empty-gate",
            adopt_existing=False,
        )
        rejected = subprocess.run(
            default_bootstrap, check=False, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, env=environment, timeout=30.0,
        )
        if rejected.returncode == 0:
            fail("fresh replica bootstrap silently adopted a populated folder")
        if "must be empty for fresh bootstrap" not in rejected.stderr:
            fail(f"fresh populated-folder rejection was unclear: {rejected.stderr}")
        if (fail_state / "deployment.json").exists():
            fail("default populated-folder rejection published a deployment")

        partial_instance = "partial-share"
        partial_state = state_parent / partial_instance
        partial_files = root / "partial-files"
        partial_state.mkdir(mode=0o700)
        os.chmod(partial_state, 0o700)
        (partial_state / "payload").mkdir(mode=0o700)
        partial_files.mkdir(mode=0o700)
        (partial_files / "already-here.txt").write_text(
            "already here\n", encoding="utf-8"
        )
        partial_folder = "share-partial-explicit"
        partial_device = "device-partial-explicit"
        explicit = subprocess.run(
            replica_init_command(
                replica,
                state=partial_state,
                files=partial_files,
                folder_id=partial_folder,
                local_device=partial_device,
                adopt_existing=True,
            ),
            check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, env=environment, timeout=30.0,
        )
        if explicit.returncode != 0 or explicit.stderr:
            fail(
                "explicit populated-folder bootstrap failed\n"
                f"stdout:\n{explicit.stdout}stderr:\n{explicit.stderr}"
            )
        if (partial_state / "replica.sqlite3.folder-catalog.sqlite3").exists():
            fail("replica bootstrap unexpectedly created the folder catalog")
        partial = run_json(
            [
                *share_command(
                    sync, partial_instance, partial_state, partial_files
                ),
                "--folder", partial_folder,
                "--local-device", partial_device,
            ],
            environment=environment,
            label="share-create after explicit partial bootstrap",
        )
        expect_fields(
            partial,
            {
                "deployment_disposition": "resumed_exact",
                "catalog_disposition": "initialized",
                "folder_id": partial_folder,
                "local_device_id": partial_device,
                "catalog_entry_count_after": 1,
                "ready_to_link": True,
            },
            "share-create after explicit partial bootstrap",
        )
        partial_pass = partial.get("initial_pass")
        if not isinstance(partial_pass, dict) or partial_pass.get("local_published") != 1:
            fail("partial bootstrap completion did not publish its existing file")
        if marker.exists():
            fail("a later share-create selected an ambient PATH executable")

    print("anonsync share-create process test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
