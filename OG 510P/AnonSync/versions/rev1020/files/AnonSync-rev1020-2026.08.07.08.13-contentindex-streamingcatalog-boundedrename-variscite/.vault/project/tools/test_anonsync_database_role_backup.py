#!/usr/bin/env python3
"""Prove bounded role-bound offline SQLite backup and detached inspection."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
from typing import Any, NoReturn, Sequence

CHECKS = 0


def fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def require(condition: bool, message: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        fail(message)


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def parse_json(
    completed: subprocess.CompletedProcess[str],
    command: Sequence[str],
    label: str,
) -> dict[str, Any]:
    try:
        value = json.loads(
            completed.stdout, object_pairs_hook=unique_object
        )
    except (json.JSONDecodeError, ValueError) as error:
        fail(
            f"{label} did not emit strict JSON: {error}\n"
            f"command: {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    if not isinstance(value, dict):
        fail(f"{label} JSON is not an object")
    return value


def run_ok(
    command: Sequence[str], *, label: str, timeout: float = 90.0
) -> dict[str, Any]:
    completed = subprocess.run(
        list(command), check=False, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, timeout=timeout,
    )
    value = parse_json(completed, command, label)
    if completed.returncode != 0:
        fail(
            f"{label} failed with {completed.returncode}: {value}\n"
            f"stderr:\n{completed.stderr}"
        )
    require(not completed.stderr, f"{label} wrote stderr on success")
    return value


def run_failure(
    command: Sequence[str], *, label: str, expected_code: str,
    message_fragment: str,
) -> dict[str, Any]:
    completed = subprocess.run(
        list(command), check=False, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, timeout=60.0,
    )
    value = parse_json(completed, command, label)
    require(completed.returncode != 0, f"{label} unexpectedly succeeded")
    require(
        value.get("terminal_class") == "stopped" and
        value.get("error_code") == expected_code,
        f"{label} returned the wrong failure class: {value}",
    )
    message = value.get("message")
    require(
        isinstance(message, str) and message_fragment in message,
        f"{label} omitted {message_fragment!r}: {value}",
    )
    require(
        message_fragment in completed.stderr,
        f"{label} stderr omitted {message_fragment!r}",
    )
    return value


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str) and len(value) == 64 and
        all(character in "0123456789abcdef" for character in value)
    )


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def family_fingerprint(path: Path) -> dict[str, tuple[int, int, str]]:
    result: dict[str, tuple[int, int, str]] = {}
    for suffix in ("", "-journal", "-wal", "-shm"):
        member = Path(str(path) + suffix)
        if not member.exists():
            continue
        observed = member.lstat()
        require(
            stat.S_ISREG(observed.st_mode),
            f"SQLite family member is not regular: {member}",
        )
        result[suffix] = (
            stat.S_IMODE(observed.st_mode), observed.st_size,
            file_sha256(member),
        )
    return result


def hide_path(source: Path, hidden_root: Path) -> tuple[Path, Path]:
    destination = hidden_root / source.name
    source.rename(destination)
    return source, destination


def hide_family(path: Path, hidden_root: Path) -> list[tuple[Path, Path]]:
    moved: list[tuple[Path, Path]] = []
    for suffix in ("", "-journal", "-wal", "-shm"):
        source = Path(str(path) + suffix)
        if source.exists():
            destination = hidden_root / f"{path.name}{suffix}"
            source.rename(destination)
            moved.append((source, destination))
    return moved


def restore_all(moved: list[tuple[Path, Path]]) -> None:
    for original, concealed in reversed(moved):
        if concealed.exists() and not original.exists():
            concealed.rename(original)


def require_role_response(
    value: dict[str, Any], *, role: str, source: Path, artifact: Path,
    command: str, creating: bool,
) -> None:
    expected_schema = (
        "anonsync.local-database-backup-create.response.v2"
        if creating else
        "anonsync.local-database-backup-inspection.response.v2"
    )
    expected_flags = {
        "replica_database_included": role == "replica",
        "effect_database_included": role == "file-effect",
        "membership_database_included": role == "tls-membership",
        "anchor_database_included": role == "tls-membership-anchor",
        "folder_catalog_included": role == "folder-catalog",
    }
    expected = {
        "command": command,
        "terminal_class": "completed",
        "response_schema": expected_schema,
        "database_role": role,
        "source_database": str(source),
        "snapshot_path": str(artifact),
        "offline_required": True,
        "deployment_singleton_acquired": True,
        "continuity_scope": "single_role_database_image",
        "cross_database_atomicity": False,
        "complete_share_backup": False,
        "external_anti_rollback_authority": False,
        "payload_store_observed": False,
        "rooted_files_observed": False,
        "network_started": False,
        "payload_bytes_included": False,
        "configuration_included": False,
        "credentials_included": False,
        "snapshot_format": "anonsync.role-bound-database-backup.v1",
        "canonical_standalone_sqlite": True,
        "single_file_sidecar_free": True,
        "logical_sqlite_snapshot": True,
        "current_schema_required": True,
        "deployment_binding_attested": True,
        "restore_supported": role == "replica",
        "inspection_only": role != "replica",
        "database_family_replacement_performed": False,
        "restore_performed": False,
        "recovery_epoch_advanced": False,
        "active_database_observed": creating,
        "transactionally_pinned_source": creating,
        "source_cutpoint_bracketed": creating,
        "bounded_resident_copy": True,
        "immutable_create_new": creating,
        "postpublication_reverified": True,
        "artifact_published": creating,
        "source_database_mutation_performed": False,
        "mutation_performed": creating,
        **expected_flags,
    }
    for key, expected_value in expected.items():
        require(
            value.get(key) == expected_value,
            f"{command} {role} field {key!r} was {value.get(key)!r}, "
            f"expected {expected_value!r}",
        )
    for key in (
        "snapshot_sha256", "role_state_digest", "role_auxiliary_digest",
    ):
        require(is_sha256(value.get(key)), f"{command} {role} omitted {key}")
    for key in (
        "snapshot_byte_count", "snapshot_page_size", "snapshot_page_count",
        "role_state_generation", "role_logical_record_count",
    ):
        require(
            isinstance(value.get(key), int) and value[key] >= 0,
            f"{command} {role} omitted nonnegative {key}",
        )
    require(
        value["snapshot_byte_count"] ==
        value["snapshot_page_size"] * value["snapshot_page_count"],
        f"{command} {role} emitted inconsistent SQLite geometry",
    )
    if role == "replica":
        require(is_sha256(value.get("database_incarnation_sha256")),
                f"{command} replica omitted database incarnation")
        require(is_sha256(value.get("cutpoint_digest")),
                f"{command} replica omitted cutpoint")
        require(
            isinstance(value.get("database_recovery_epoch"), int) and
            value["database_recovery_epoch"] > 0,
            f"{command} replica omitted recovery epoch",
        )
        require(
            isinstance(value.get("recovery_expectation"), str) and
            value["recovery_expectation"].startswith("v1:"),
            f"{command} replica omitted recovery expectation",
        )
        require(value.get("post_replacement_recovery_advance_required") is True,
                f"{command} replica weakened post-restore epoch requirement")
    else:
        for key in (
            "database_incarnation_sha256", "database_recovery_epoch",
            "cutpoint_digest", "recovery_expectation",
        ):
            require(value.get(key) is None,
                    f"{command} {role} invented replica lineage field {key}")
        require(
            value.get("post_replacement_recovery_advance_required") is False,
            f"{command} {role} claimed unsupported replacement semantics",
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

    with tempfile.TemporaryDirectory(prefix="anonsync-role-backup-") as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        database_root = root / "db"
        payload_root = root / "payload"
        files_root = root / "files"
        artifact_root = root / "artifacts"
        hidden_root = root / "hidden"
        for directory in (
            database_root, payload_root, files_root, artifact_root, hidden_root,
        ):
            directory.mkdir(mode=0o700)

        manifest = database_root / "deployment.json"
        replica_db = database_root / "replica.sqlite"
        effect_db = database_root / "effect.sqlite"
        membership_db = database_root / "membership.sqlite"
        anchor_db = database_root / "anchor.sqlite"
        catalog_db = Path(str(replica_db) + ".folder-catalog.sqlite3")
        role_sources = {
            "replica": replica_db,
            "file-effect": effect_db,
            "tls-membership": membership_db,
            "tls-membership-anchor": anchor_db,
            "folder-catalog": catalog_db,
        }

        initialized = run_ok([
            str(replica), "init", "--manifest", str(manifest),
            "--replica-db", str(replica_db),
            "--payload-root", str(payload_root),
            "--effect-db", str(effect_db),
            "--files-root", str(files_root),
            "--membership-db", str(membership_db),
            "--anchor-db", str(anchor_db),
            "--folder", "role-bound-backup",
            "--local-device", "role-bound-backup-node",
            "--local-epoch", "1",
        ], label="role-bound deployment init")
        run_ok([
            str(folder), "init", "--manifest", str(manifest),
        ], label="role-bound folder catalog init")
        require(is_sha256(initialized.get("deployment_id")),
                "deployment init omitted deployment identity")

        invalid_artifact = artifact_root / "invalid.sqlite"
        run_failure([
            str(sync), "database-backup-create",
            "--manifest", str(manifest),
            "--snapshot", str(invalid_artifact),
            "--role", "payload-store",
        ], label="invalid database role", expected_code="invalid_arguments",
           message_fragment="--role must be")
        require(not invalid_artifact.exists(),
                "invalid role created an artifact")

        # The role-bound database backup deliberately does not observe payload
        # bytes or the synchronized root. Prove creation remains possible with
        # both roots absent while every selected SQLite authority remains live.
        moved: list[tuple[Path, Path]] = []
        moved.append(hide_path(payload_root, hidden_root))
        moved.append(hide_path(files_root, hidden_root))
        created: dict[str, dict[str, Any]] = {}
        artifacts: dict[str, Path] = {}
        try:
            source_before = {
                role: family_fingerprint(source)
                for role, source in role_sources.items()
            }
            for role, source in role_sources.items():
                artifact = artifact_root / f"{role}.sqlite"
                artifacts[role] = artifact
                value = run_ok([
                    str(sync), "database-backup-create",
                    "--manifest", str(manifest),
                    "--snapshot", str(artifact),
                    "--role", role,
                ], label=f"{role} backup create")
                require_role_response(
                    value, role=role, source=source, artifact=artifact,
                    command="database-backup-create", creating=True,
                )
                observed = artifact.lstat()
                require(stat.S_ISREG(observed.st_mode),
                        f"{role} artifact is not regular")
                require(observed.st_nlink == 1,
                        f"{role} artifact is not single-linked")
                require(stat.S_IMODE(observed.st_mode) == 0o600,
                        f"{role} artifact is not mode 0600")
                require(value["snapshot_byte_count"] == observed.st_size,
                        f"{role} artifact byte count disagreed")
                require(value["snapshot_sha256"] == file_sha256(artifact),
                        f"{role} artifact digest disagreed")
                for suffix in ("-journal", "-wal", "-shm"):
                    require(not Path(str(artifact) + suffix).exists(),
                            f"{role} artifact left sidecar {suffix}")
                require(
                    family_fingerprint(source) == source_before[role],
                    f"{role} backup changed its source SQLite family",
                )
                created[role] = value

            require(
                len({value["snapshot_sha256"] for value in created.values()}) ==
                len(created),
                "role-bound deployment bindings did not distinguish artifacts",
            )

            # Explicit replica artifacts remain compatible with the released v1
            # inspector and therefore with the existing replacement ceremony.
            legacy = run_ok([
                str(sync), "database-backup-inspect",
                "--manifest", str(manifest),
                "--snapshot", str(artifacts["replica"]),
            ], label="explicit replica artifact legacy inspection")
            require(
                legacy.get("response_schema") ==
                "anonsync.local-database-backup-inspection.response.v1",
                "explicit replica artifact broke the released v1 inspector",
            )
            require(
                legacy.get("snapshot_sha256") ==
                created["replica"]["snapshot_sha256"],
                "legacy replica inspection changed artifact identity",
            )

            wrong_before = artifacts["file-effect"].read_bytes()
            run_failure([
                str(sync), "database-backup-inspect",
                "--manifest", str(manifest),
                "--snapshot", str(artifacts["file-effect"]),
                "--role", "folder-catalog",
            ], label="wrong role artifact inspection",
               expected_code="operation_failed",
               message_fragment="deployment binding")
            require(
                artifacts["file-effect"].read_bytes() == wrong_before,
                "wrong-role inspection changed the artifact",
            )

            # Remove every live selected database family. Detached role
            # inspection must rely only on the immutable artifact plus manifest,
            # while the already absent payload/files roots remain unobserved.
            for source in role_sources.values():
                moved.extend(hide_family(source, hidden_root))
            for role, source in role_sources.items():
                value = run_ok([
                    str(sync), "database-backup-inspect",
                    "--manifest", str(manifest),
                    "--snapshot", str(artifacts[role]),
                    "--role", role,
                ], label=f"detached {role} backup inspection")
                require_role_response(
                    value, role=role, source=source, artifact=artifacts[role],
                    command="database-backup-inspect", creating=False,
                )
                for key in (
                    "snapshot_sha256", "snapshot_byte_count",
                    "snapshot_page_size", "snapshot_page_count",
                    "role_state_generation", "role_logical_record_count",
                    "role_state_digest", "role_auxiliary_digest",
                ):
                    require(
                        value.get(key) == created[role].get(key),
                        f"detached {role} inspection changed {key}",
                    )

            for source in role_sources.values():
                require(
                    not source.exists(),
                    f"detached inspection recreated source database {source}",
                )
            require(not payload_root.exists(),
                    "detached inspection recreated payload root")
            require(not files_root.exists(),
                    "detached inspection recreated synchronized root")
        finally:
            restore_all(moved)

    print(f"anonsync role-bound database backup: {CHECKS} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
