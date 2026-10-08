#!/usr/bin/env python3
"""Prove offline replica-database backup and recovery authority.

The operator-visible commands share the retained deployment singleton. Backup
creation brackets one bounded canonical SQLite copy, publishes create-new, and
reopens the detached artifact. Inspection remains valid with the live database
family absent. Recovery rejects stale or noncanonical expectations before
writable SQLite open and advances only the in-database recovery epoch. None of
these commands requires payload, catalog, rooted-file, or network authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import sqlite3
import stat
import subprocess
import tempfile
import time
from typing import Any, NoReturn, Sequence


CHECKS = 0


def fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def require(condition: bool, message: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        fail(message)


def unique_json_object_pairs(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, member in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON object key {key!r}")
        value[key] = member
    return value


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
            f"{label} did not emit one strict JSON object: {error}\n"
            f"command: {' '.join(command)}\nstdout:\n{completed.stdout}"
            f"stderr:\n{completed.stderr}"
        )
    if not isinstance(value, dict):
        fail(f"{label} JSON is not an object")
    return value


def run_ok(
    command: Sequence[str], *, label: str, timeout: float = 60.0
) -> dict[str, Any]:
    completed = subprocess.run(
        list(command), check=False, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, timeout=timeout,
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


def run_failure(
    command: Sequence[str], *, label: str, returncode: int,
    error_code: str, message_fragment: str, timeout: float = 60.0,
) -> dict[str, Any]:
    completed = subprocess.run(
        list(command), check=False, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, timeout=timeout,
    )
    value = parse_json_output(completed, command, label)
    require(
        completed.returncode == returncode,
        f"{label} returned {completed.returncode}, expected {returncode}: {value}",
    )
    require(
        value.get("terminal_class") == "stopped" and
        value.get("error_code") == error_code,
        f"{label} returned the wrong failure class: {value}",
    )
    message = value.get("message")
    require(
        isinstance(message, str) and message_fragment in message,
        f"{label} omitted {message_fragment!r}: {value}",
    )
    require(
        message_fragment in completed.stderr,
        f"{label} stderr omitted {message_fragment!r}: {completed.stderr!r}",
    )
    return value


def require_exact_keys(value: dict[str, Any], keys: set[str], label: str) -> None:
    require(
        set(value) == keys,
        f"{label} keys differed: observed={sorted(value)} expected={sorted(keys)}",
    )


def require_fields(
    value: dict[str, Any], expected: dict[str, Any], label: str
) -> None:
    for key, wanted in expected.items():
        require(
            value.get(key) == wanted,
            f"{label} field {key!r} was {value.get(key)!r}, expected {wanted!r}",
        )


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str) and len(value) == 64 and
        all(byte in "0123456789abcdef" for byte in value)
    )


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def sqlite_family_fingerprint(database: Path) -> dict[str, tuple[int, int, str]]:
    result: dict[str, tuple[int, int, str]] = {}
    for suffix in ("", "-journal", "-wal", "-shm"):
        member = Path(str(database) + suffix)
        if not member.exists():
            continue
        observed = member.lstat()
        require(stat.S_ISREG(observed.st_mode), f"SQLite family member is not regular: {member}")
        result[suffix] = (
            stat.S_IMODE(observed.st_mode), observed.st_size, file_digest(member)
        )
    return result



RECEIPT_MAGIC = b"anonsync:replica-database-replacement-receipt:v1\n"
RECEIPT_PATH_DOMAIN = (
    b"anonsync:replica-database-replacement-receipt:path:v1\0"
)
RECEIPT_ACTION_DOMAIN = (
    b"anonsync:replica-database-replacement-receipt:action:v1\0"
)
RECEIPT_RECORD_DOMAIN = (
    b"anonsync:replica-database-replacement-receipt:record:v1\0"
)


def path_receipt_digest(path: Path) -> str:
    return hashlib.sha256(RECEIPT_PATH_DOMAIN + str(path).encode()).hexdigest()


def inspect_replacement_receipt(path: Path) -> dict[str, str]:
    observed = path.lstat()
    require(stat.S_ISREG(observed.st_mode), "replacement receipt is not regular")
    require(observed.st_nlink == 1, "replacement receipt is not single-linked")
    require(
        stat.S_IMODE(observed.st_mode) == 0o600,
        "replacement receipt is not owner-only mode 0600",
    )
    require(0 < observed.st_size <= 8 * 1024,
            "replacement receipt exceeded its 8 KiB boundary")
    encoded = path.read_bytes()
    require(encoded.startswith(RECEIPT_MAGIC),
            "replacement receipt magic is not canonical")
    require(encoded.endswith(b"\n") and b"\r" not in encoded and b"\0" not in encoded,
            "replacement receipt framing is not canonical")
    lines = encoded.splitlines(keepends=True)
    require(len(lines) > 4, "replacement receipt omitted canonical fields")
    require(lines[-2].startswith(b"action_sha256="),
            "replacement receipt omitted action digest")
    require(lines[-1].startswith(b"record_sha256="),
            "replacement receipt omitted record digest")
    action = lines[-2][len(b"action_sha256="):-1].decode("ascii")
    record = lines[-1][len(b"record_sha256="):-1].decode("ascii")
    immutable_fields = b"".join(lines[1:-2])
    record_prefix = b"".join(lines[:-1])
    require(is_sha256(action), "replacement receipt action digest is invalid")
    require(is_sha256(record), "replacement receipt record digest is invalid")
    require(
        hashlib.sha256(RECEIPT_ACTION_DOMAIN + immutable_fields).hexdigest() == action,
        "replacement receipt action digest disagreed with canonical bytes",
    )
    require(
        hashlib.sha256(RECEIPT_RECORD_DOMAIN + record_prefix).hexdigest() == record,
        "replacement receipt record digest disagreed with canonical bytes",
    )
    fields: dict[str, str] = {}
    for raw in lines[1:-2]:
        name, separator, value = raw[:-1].partition(b"=")
        require(separator == b"=" and name and name.decode("ascii") not in fields,
                "replacement receipt fields are malformed or duplicated")
        fields[name.decode("ascii")] = value.decode("ascii")
    fields["action_sha256"] = action
    fields["record_sha256"] = record
    return fields


def install_logical_sqlite_image(source: Path, destination: Path) -> None:
    """Simulate a crash cutpoint by logically copying source into destination."""
    source_uri = f"file:{source}?mode=ro&immutable=1"
    source_connection = sqlite3.connect(source_uri, uri=True)
    destination_connection = sqlite3.connect(str(destination))
    try:
        destination_connection.execute("PRAGMA busy_timeout=5000")
        source_connection.backup(destination_connection, pages=64, sleep=0.001)
        destination_connection.commit()
        # Leave the active deployment in its ordinary WAL profile and force all
        # copied pages durable before the shipping owner reopens it.
        mode = destination_connection.execute("PRAGMA journal_mode=WAL").fetchone()
        require(mode is not None and str(mode[0]).lower() == "wal",
                "test crash-cutpoint installation did not retain WAL mode")
        destination_connection.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchall()
    finally:
        destination_connection.close()
        source_connection.close()


def recovery_state(value: dict[str, Any]) -> tuple[str, int, int, str, str]:
    return (
        str(value.get("database_incarnation_sha256")),
        int(value.get("database_recovery_epoch", 0)),
        int(value.get("state_generation", 0)),
        str(value.get("cutpoint_digest")),
        str(value.get("recovery_expectation")),
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

    inspection_keys = {
        "command", "terminal_class", "response_schema", "manifest_path",
        "deployment_id", "folder_id", "local_device_id", "local_epoch",
        "replica_database", "offline_required",
        "deployment_singleton_acquired", "continuity_scope",
        "external_anti_rollback_authority", "payload_store_observed",
        "folder_catalog_observed", "rooted_files_observed", "network_started",
        "database_incarnation_sha256", "database_recovery_epoch",
        "state_generation", "cutpoint_digest", "recovery_expectation",
        "current_schema_required", "operator_assertion_required_before_advance",
        "mutation_performed",
    }
    advance_keys = {
        "command", "terminal_class", "response_schema", "manifest_path",
        "deployment_id", "folder_id", "local_device_id", "local_epoch",
        "replica_database", "offline_required",
        "deployment_singleton_acquired", "continuity_scope",
        "external_anti_rollback_authority", "payload_store_observed",
        "folder_catalog_observed", "rooted_files_observed", "network_started",
        "database_incarnation_sha256", "previous_database_recovery_epoch",
        "database_recovery_epoch", "state_generation",
        "previous_cutpoint_digest", "cutpoint_digest",
        "previous_recovery_expectation", "recovery_expectation",
        "operator_asserted_database_recovery",
        "forensic_preflight_before_writable_open",
        "exact_transaction_reproof", "recovery_epoch_advanced",
        "whole_image_rollback_reuse_excluded",
        "retention_age_reset_required_when_continuity_uncertain",
        "mutation_performed",
    }
    replacement_keys = {
        "command", "terminal_class", "response_schema", "manifest_path",
        "deployment_id", "folder_id", "local_device_id", "local_epoch",
        "replica_database", "offline_required",
        "deployment_singleton_acquired", "continuity_scope",
        "external_anti_rollback_authority", "payload_store_observed",
        "folder_catalog_observed", "rooted_files_observed", "network_started",
        "candidate_snapshot_path", "candidate_snapshot_sha256",
        "candidate_snapshot_byte_count", "candidate_snapshot_page_size",
        "candidate_snapshot_page_count", "rollback_snapshot_path",
        "rollback_snapshot_sha256", "rollback_snapshot_byte_count",
        "rollback_snapshot_page_size", "rollback_snapshot_page_count",
        "replacement_receipt_path", "replacement_receipt_action_sha256",
        "replacement_receipt_record_sha256", "replacement_entry_stage",
        "replacement_receipt_preexisting",
        "replacement_receipt_created_this_invocation",
        "rollback_artifact_published_this_invocation",
        "logical_database_replacement_performed_this_invocation",
        "recovery_epoch_advanced_this_invocation", "idempotent_reproof_only",
        "expected_current_recovery_expectation",
        "displaced_database_incarnation_sha256",
        "displaced_database_recovery_epoch", "displaced_state_generation",
        "displaced_cutpoint_digest",
        "restored_database_incarnation_sha256",
        "restored_database_recovery_epoch", "restored_state_generation",
        "restored_cutpoint_digest", "database_incarnation_sha256",
        "previous_database_recovery_epoch", "database_recovery_epoch",
        "state_generation", "cutpoint_digest", "recovery_expectation",
        "backup_step_calls", "maximum_reported_page_count",
        "maximum_reported_remaining_pages",
        "candidate_validated_before_mutation",
        "candidate_deployment_binding_attested", "replacement_receipt_immutable",
        "replacement_receipt_effect_authority",
        "progress_classified_from_active_database",
        "rollback_artifact_create_new",
        "rollback_artifact_postpublication_reverified",
        "rollback_represents_displaced_logical_database",
        "raw_sqlite_family_byte_identity_preserved",
        "descriptor_rooted_writable_destination",
        "sqlite_destination_transaction",
        "logical_database_replacement_complete",
        "logical_database_replacement_performed",
        "restored_cutpoint_reproved_before_advance",
        "recovery_epoch_advanced", "recovery_epoch_advance_complete",
        "final_database_reopened_and_reproved",
        "final_candidate_artifact_path_reproved",
        "final_rollback_artifact_path_reproved",
        "final_artifact_reproof_bracketed_by_database_cutpoint",
        "artifact_pathnames_continuously_reserved",
        "noncooperating_same_uid_artifact_replacement_excluded",
        "retention_age_reset_by_exact_source_change",
        "payload_store_replacement_performed",
        "other_database_replacement_performed", "mutation_performed",
    }
    backup_keys = {
        "command", "terminal_class", "response_schema", "manifest_path",
        "deployment_id", "folder_id", "local_device_id", "local_epoch",
        "replica_database", "snapshot_path", "offline_required",
        "deployment_singleton_acquired", "continuity_scope",
        "external_anti_rollback_authority", "payload_store_observed",
        "folder_catalog_observed", "rooted_files_observed", "network_started",
        "payload_bytes_included", "folder_catalog_included",
        "membership_database_included", "effect_database_included",
        "anchor_database_included", "snapshot_format", "snapshot_sha256",
        "snapshot_byte_count", "snapshot_page_size", "snapshot_page_count",
        "maximum_snapshot_bytes", "maximum_snapshot_pages",
        "database_incarnation_sha256", "database_recovery_epoch",
        "state_generation", "cutpoint_digest", "recovery_expectation",
        "canonical_standalone_sqlite", "single_file_sidecar_free",
        "logical_sqlite_snapshot", "current_schema_required",
        "deployment_binding_attested", "database_family_replacement_performed",
        "restore_performed", "recovery_epoch_advanced",
        "post_replacement_recovery_advance_required",
        "retention_age_reset_required_after_restore",
        "active_database_observed", "transactionally_pinned_source",
        "source_cutpoint_bracketed", "bounded_resident_copy",
        "immutable_create_new", "postpublication_reverified",
        "artifact_published", "source_database_mutation_performed",
        "mutation_performed",
    }

    with tempfile.TemporaryDirectory(prefix="anonsync-database-recovery-") as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        database_root = root / "db"
        payload_root = root / "payload"
        files_root = root / "files"
        backup_root = root / "backup"
        for directory in (database_root, payload_root, files_root, backup_root):
            directory.mkdir(mode=0o700)
        manifest = database_root / "deployment.json"
        replica_db = database_root / "replica.sqlite"
        catalog = Path(str(replica_db) + ".folder-catalog.sqlite3")

        initialized = run_ok([
            str(replica), "init", "--manifest", str(manifest),
            "--replica-db", str(replica_db),
            "--payload-root", str(payload_root),
            "--effect-db", str(database_root / "effect.sqlite"),
            "--files-root", str(files_root),
            "--membership-db", str(database_root / "membership.sqlite"),
            "--anchor-db", str(database_root / "anchor.sqlite"),
            "--folder", "database-recovery-process",
            "--local-device", "database-recovery-node", "--local-epoch", "1",
        ], label="combined deployment init")
        run_ok([
            str(folder), "init", "--manifest", str(manifest),
        ], label="folder catalog init")
        before_status = run_ok([
            str(replica), "status", "--manifest", str(manifest),
        ], label="status before recovery")

        common = {
            "manifest_path": str(manifest),
            "deployment_id": initialized["deployment_id"],
            "folder_id": "database-recovery-process",
            "local_device_id": "database-recovery-node",
            "local_epoch": 1,
            "replica_database": str(replica_db),
            "offline_required": True,
            "deployment_singleton_acquired": True,
            "continuity_scope": "in_database_only",
            "external_anti_rollback_authority": False,
            "payload_store_observed": False,
            "folder_catalog_observed": False,
            "rooted_files_observed": False,
            "network_started": False,
        }
        backup_artifact = backup_root / "replica-backup.sqlite"
        backup_common = {
            key: value for key, value in common.items()
            if key != "continuity_scope"
        }
        backup_common.update({
            "snapshot_path": str(backup_artifact),
            "continuity_scope": "single_replica_database_image",
            "payload_bytes_included": False,
            "folder_catalog_included": False,
            "membership_database_included": False,
            "effect_database_included": False,
            "anchor_database_included": False,
            "snapshot_format": "anonsync.replica-database-backup.v1",
            "maximum_snapshot_bytes": 512 * 1024 * 1024,
            "maximum_snapshot_pages": 262144,
            "canonical_standalone_sqlite": True,
            "single_file_sidecar_free": True,
            "logical_sqlite_snapshot": True,
            "current_schema_required": True,
            "deployment_binding_attested": True,
            "database_family_replacement_performed": False,
            "restore_performed": False,
            "recovery_epoch_advanced": False,
            "post_replacement_recovery_advance_required": True,
            "retention_age_reset_required_after_restore": True,
        })

        family_before_bad_paths = sqlite_family_fingerprint(replica_db)
        run_failure([
            str(sync), "database-backup-create", "--manifest", str(manifest),
            "--snapshot", str(files_root / "forbidden-backup.sqlite"),
        ], label="backup beneath synchronized root", returncode=2,
           error_code="invalid_arguments",
           message_fragment="outside payload storage and synchronized files")
        run_failure([
            str(sync), "database-backup-create", "--manifest", str(manifest),
            "--snapshot", str(replica_db) + "-wal",
        ], label="backup colliding with active SQLite family", returncode=2,
           error_code="invalid_arguments",
           message_fragment="overlaps an active SQLite family")
        require(
            sqlite_family_fingerprint(replica_db) == family_before_bad_paths,
            "rejected backup paths changed the source SQLite family",
        )
        require(
            not (files_root / "forbidden-backup.sqlite").exists(),
            "rejected synchronized-root backup path was created",
        )

        # The selected main artifact can be outside a protected root while one
        # deterministic SQLite sidecar name is the protected root itself. The
        # complete four-name artifact family, not only its main name, must be
        # rejected by the authority geometry before output-family preflight.
        family_geometry_root = root / "family-geometry"
        family_geometry_root.mkdir(mode=0o700)
        family_artifact = family_geometry_root / "artifact.sqlite"
        family_payload_root = Path(str(family_artifact) + "-wal")
        family_payload_root.mkdir(mode=0o700)
        family_files_root = family_geometry_root / "files"
        family_files_root.mkdir(mode=0o700)
        family_manifest = family_geometry_root / "deployment.json"
        family_replica_db = family_geometry_root / "replica.sqlite"
        run_ok([
            str(replica), "init", "--manifest", str(family_manifest),
            "--replica-db", str(family_replica_db),
            "--payload-root", str(family_payload_root),
            "--effect-db", str(family_geometry_root / "effect.sqlite"),
            "--files-root", str(family_files_root),
            "--folder", "artifact-family-root-collision",
            "--local-device", "artifact-family-root-node",
            "--local-epoch", "1",
        ], label="artifact family root-collision deployment init")
        family_source_before = sqlite_family_fingerprint(family_replica_db)
        run_failure([
            str(sync), "database-backup-create",
            "--manifest", str(family_manifest),
            "--snapshot", str(family_artifact),
        ], label="artifact family sidecar colliding with payload root",
           returncode=2, error_code="invalid_arguments",
           message_fragment="SQLite family must remain outside payload storage")
        require(
            not family_artifact.exists(),
            "artifact-family root collision published the main artifact",
        )
        require(
            family_payload_root.is_dir(),
            "artifact-family root collision changed the payload-root entry",
        )
        require(
            sqlite_family_fingerprint(family_replica_db) == family_source_before,
            "artifact-family root collision changed its source SQLite family",
        )

        hidden: list[tuple[Path, Path]] = []
        try:
            for live in (payload_root, files_root, catalog):
                concealed = Path(str(live) + ".outside-recovery-authority")
                live.rename(concealed)
                hidden.append((live, concealed))

            family_before_inspect = sqlite_family_fingerprint(replica_db)
            inspected = run_ok([
                str(sync), "database-recovery-inspect",
                "--manifest", str(manifest),
            ], label="offline database recovery inspection")
            require_exact_keys(inspected, inspection_keys, "inspection response")
            require_fields(inspected, {
                "command": "database-recovery-inspect",
                "terminal_class": "completed",
                "response_schema":
                    "anonsync.local-database-recovery-inspection.response.v1",
                **common,
                "current_schema_required": True,
                "operator_assertion_required_before_advance": True,
                "mutation_performed": False,
            }, "inspection response")
            require(is_sha256(inspected.get("database_incarnation_sha256")),
                    "inspection omitted canonical database incarnation")
            require(is_sha256(inspected.get("cutpoint_digest")),
                    "inspection omitted canonical cutpoint")
            require(
                isinstance(inspected.get("database_recovery_epoch"), int) and
                inspected["database_recovery_epoch"] > 0,
                "inspection omitted a positive database recovery epoch",
            )
            require(
                isinstance(inspected.get("state_generation"), int) and
                inspected["state_generation"] >= 0,
                "inspection omitted state generation",
            )
            expected_token = (
                f"v1:{inspected['database_incarnation_sha256']}:"
                f"{inspected['database_recovery_epoch']}:"
                f"{inspected['cutpoint_digest']}"
            )
            require(inspected.get("recovery_expectation") == expected_token,
                    "inspection emitted a noncanonical recovery expectation")
            require(
                sqlite_family_fingerprint(replica_db) == family_before_inspect,
                "read-only inspection changed SQLite family bytes, modes, or members",
            )

            hostile_output_sidecar = Path(str(backup_artifact) + "-wal")
            hostile_output_sidecar.write_bytes(b"preexisting-output-sidecar")
            os.chmod(hostile_output_sidecar, 0o600)
            source_before_blocked_backup = sqlite_family_fingerprint(replica_db)
            blocked_backup_family = sqlite_family_fingerprint(backup_artifact)
            run_failure([
                str(sync), "database-backup-create",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
            ], label="backup create with preexisting output sidecar",
               returncode=1, error_code="operation_failed",
               message_fragment="refuses SQLite snapshot sidecar -wal")
            require(
                not backup_artifact.exists(),
                "preexisting backup sidecar allowed the main artifact to publish",
            )
            require(
                sqlite_family_fingerprint(backup_artifact) ==
                    blocked_backup_family,
                "backup sidecar preflight changed the blocked output family",
            )
            require(
                sqlite_family_fingerprint(replica_db) ==
                    source_before_blocked_backup,
                "backup sidecar preflight changed the source SQLite family",
            )
            hostile_output_sidecar.unlink()

            family_before_backup = sqlite_family_fingerprint(replica_db)
            created_backup = run_ok([
                str(sync), "database-backup-create",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
            ], label="offline replica database backup create", timeout=90.0)
            require_exact_keys(created_backup, backup_keys, "backup create response")
            require_fields(created_backup, {
                "command": "database-backup-create",
                "terminal_class": "completed",
                "response_schema":
                    "anonsync.local-database-backup-create.response.v1",
                **backup_common,
                "active_database_observed": True,
                "transactionally_pinned_source": True,
                "source_cutpoint_bracketed": True,
                "bounded_resident_copy": True,
                "immutable_create_new": True,
                "postpublication_reverified": True,
                "artifact_published": True,
                "source_database_mutation_performed": False,
                "mutation_performed": True,
            }, "backup create response")
            require(
                recovery_state(created_backup) == recovery_state(inspected),
                "backup artifact did not bind the inspected source cutpoint",
            )
            require(is_sha256(created_backup.get("snapshot_sha256")),
                    "backup omitted canonical artifact SHA-256")
            artifact_stat = backup_artifact.lstat()
            require(stat.S_ISREG(artifact_stat.st_mode),
                    "backup artifact is not a regular file")
            require(artifact_stat.st_nlink == 1,
                    "backup artifact is not single-linked")
            require(stat.S_IMODE(artifact_stat.st_mode) == 0o600,
                    "backup artifact is not owner-only mode 0600")
            require(created_backup["snapshot_byte_count"] == artifact_stat.st_size,
                    "backup byte count disagreed with the artifact")
            require(created_backup["snapshot_sha256"] == file_digest(backup_artifact),
                    "backup digest disagreed with the artifact")
            require(
                created_backup["snapshot_byte_count"] ==
                    created_backup["snapshot_page_size"] *
                    created_backup["snapshot_page_count"],
                "backup page geometry disagreed with its exact byte count",
            )
            require(
                sqlite_family_fingerprint(replica_db) == family_before_backup,
                "backup creation changed source SQLite family bytes, modes, or members",
            )
            for suffix in ("-journal", "-wal", "-shm"):
                require(
                    not Path(str(backup_artifact) + suffix).exists(),
                    f"backup publication left a SQLite sidecar {suffix}",
                )

            source_before_duplicate = sqlite_family_fingerprint(replica_db)
            artifact_before_duplicate = sqlite_family_fingerprint(backup_artifact)
            run_failure([
                str(sync), "database-backup-create",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
            ], label="duplicate immutable backup create", returncode=1,
               error_code="operation_failed", message_fragment="already exists")
            require(sqlite_family_fingerprint(replica_db) == source_before_duplicate,
                    "duplicate create changed the source SQLite family")
            require(sqlite_family_fingerprint(backup_artifact) == artifact_before_duplicate,
                    "duplicate create changed the detached artifact")

            moved_source: list[tuple[Path, Path]] = []
            try:
                for suffix in ("", "-journal", "-wal", "-shm"):
                    member = Path(str(replica_db) + suffix)
                    if member.exists():
                        concealed = Path(str(member) + ".outside-backup-inspection")
                        member.rename(concealed)
                        moved_source.append((member, concealed))
                inspected_backup = run_ok([
                    str(sync), "database-backup-inspect",
                    "--manifest", str(manifest),
                    "--snapshot", str(backup_artifact),
                ], label="detached backup inspection without source database")
            finally:
                for member, concealed in reversed(moved_source):
                    if concealed.exists() and not member.exists():
                        concealed.rename(member)
            require_exact_keys(inspected_backup, backup_keys,
                               "backup inspection response")
            require_fields(inspected_backup, {
                "command": "database-backup-inspect",
                "terminal_class": "completed",
                "response_schema":
                    "anonsync.local-database-backup-inspection.response.v1",
                **backup_common,
                "active_database_observed": False,
                "transactionally_pinned_source": False,
                "source_cutpoint_bracketed": False,
                "bounded_resident_copy": True,
                "immutable_create_new": False,
                "postpublication_reverified": True,
                "artifact_published": False,
                "source_database_mutation_performed": False,
                "mutation_performed": False,
            }, "backup inspection response")
            require(
                recovery_state(inspected_backup) == recovery_state(inspected),
                "detached backup inspection changed its source cutpoint",
            )
            for key in ("snapshot_sha256", "snapshot_byte_count",
                        "snapshot_page_size", "snapshot_page_count"):
                require(inspected_backup[key] == created_backup[key],
                        f"detached backup inspection changed {key}")

            hostile_sidecar = Path(str(backup_artifact) + "-wal")
            hostile_sidecar.write_bytes(b"not-a-backup-sidecar")
            os.chmod(hostile_sidecar, 0o600)
            sidecar_family_before = sqlite_family_fingerprint(backup_artifact)
            run_failure([
                str(sync), "database-backup-inspect",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
            ], label="backup inspection with hostile sidecar", returncode=1,
               error_code="operation_failed",
               message_fragment="refuses SQLite snapshot sidecar -wal")
            require(
                sqlite_family_fingerprint(backup_artifact) ==
                    sidecar_family_before,
                "hostile-sidecar rejection changed the artifact family",
            )
            hostile_sidecar.unlink()

            hardlinked_backup = backup_root / "hardlinked-backup.sqlite"
            os.link(backup_artifact, hardlinked_backup)
            hardlink_bytes_before = backup_artifact.read_bytes()
            run_failure([
                str(sync), "database-backup-inspect",
                "--manifest", str(manifest),
                "--snapshot", str(hardlinked_backup),
            ], label="multiply linked backup inspection", returncode=1,
               error_code="operation_failed",
               message_fragment="refuses multiply-linked SQLite family member")
            require(
                backup_artifact.read_bytes() == hardlink_bytes_before and
                hardlinked_backup.read_bytes() == hardlink_bytes_before and
                backup_artifact.stat().st_nlink == 2,
                "multiply-linked rejection changed either artifact name",
            )
            hardlinked_backup.unlink()
            require(
                backup_artifact.stat().st_nlink == 1,
                "hardlink rejection cleanup did not restore one artifact name",
            )

            damaged_backup = backup_root / "damaged-backup.sqlite"
            damaged_backup.write_bytes(backup_artifact.read_bytes()[:-1])
            os.chmod(damaged_backup, 0o600)
            damaged_before = sqlite_family_fingerprint(damaged_backup)
            run_failure([
                str(sync), "database-backup-inspect",
                "--manifest", str(manifest),
                "--snapshot", str(damaged_backup),
            ], label="damaged detached backup inspection", returncode=1,
               error_code="operation_failed", message_fragment="SQLite")
            require(sqlite_family_fingerprint(damaged_backup) == damaged_before,
                    "damaged backup inspection changed the artifact")
            for suffix in ("-journal", "-wal", "-shm"):
                require(not Path(str(damaged_backup) + suffix).exists(),
                        f"damaged backup inspection created sidecar {suffix}")

            malformed = (
                f"v1:{inspected['database_incarnation_sha256']}:0"
                f"{inspected['database_recovery_epoch']}:"
                f"{inspected['cutpoint_digest']}"
            )
            family_before_noncanonical = sqlite_family_fingerprint(replica_db)
            run_failure([
                str(sync), "database-recovery-advance", "--manifest", str(manifest),
                "--expected", malformed,
            ], label="noncanonical recovery expectation", returncode=2,
               error_code="invalid_arguments", message_fragment="canonical v1:")
            require(
                sqlite_family_fingerprint(replica_db) ==
                    family_before_noncanonical,
                "noncanonical recovery expectation changed SQLite family bytes, "
                "modes, or members",
            )

            stale_tokens = (
                "v1:" + "0" * 64 +
                f":{inspected['database_recovery_epoch']}:" +
                str(inspected["cutpoint_digest"]),
                f"v1:{inspected['database_incarnation_sha256']}:"
                f"{inspected['database_recovery_epoch'] + 1}:"
                f"{inspected['cutpoint_digest']}",
                f"v1:{inspected['database_incarnation_sha256']}:"
                f"{inspected['database_recovery_epoch']}:" + "0" * 64,
            )
            baseline_state = recovery_state(inspected)
            for index, token in enumerate(stale_tokens, start=1):
                family_before_stale = sqlite_family_fingerprint(replica_db)
                run_failure([
                    str(sync), "database-recovery-advance",
                    "--manifest", str(manifest), "--expected", token,
                ], label=f"stale recovery expectation {index}", returncode=1,
                   error_code="operation_failed",
                   message_fragment="database recovery expectation is stale")
                require(
                    sqlite_family_fingerprint(replica_db) ==
                        family_before_stale,
                    f"stale recovery expectation {index} changed SQLite family "
                    "bytes, modes, or members",
                )
                unchanged = run_ok([
                    str(sync), "database-recovery-inspect",
                    "--manifest", str(manifest),
                ], label=f"inspection after stale expectation {index}")
                require(
                    recovery_state(unchanged) == baseline_state,
                    f"stale recovery expectation {index} changed durable lineage",
                )

            advanced = run_ok([
                str(sync), "database-recovery-advance", "--manifest", str(manifest),
                "--expected", expected_token,
            ], label="exact database recovery advance")
            require_exact_keys(advanced, advance_keys, "advance response")
            require_fields(advanced, {
                "command": "database-recovery-advance",
                "terminal_class": "completed",
                "response_schema":
                    "anonsync.local-database-recovery-advance.response.v1",
                **common,
                "database_incarnation_sha256":
                    inspected["database_incarnation_sha256"],
                "previous_database_recovery_epoch":
                    inspected["database_recovery_epoch"],
                "database_recovery_epoch":
                    inspected["database_recovery_epoch"] + 1,
                "state_generation": inspected["state_generation"] + 1,
                "previous_cutpoint_digest": inspected["cutpoint_digest"],
                "previous_recovery_expectation": expected_token,
                "operator_asserted_database_recovery": True,
                "forensic_preflight_before_writable_open": True,
                "exact_transaction_reproof": True,
                "recovery_epoch_advanced": True,
                "whole_image_rollback_reuse_excluded": False,
                "retention_age_reset_required_when_continuity_uncertain": True,
                "mutation_performed": True,
            }, "advance response")
            require(is_sha256(advanced.get("cutpoint_digest")),
                    "advance omitted canonical successor cutpoint")
            require(advanced["cutpoint_digest"] != inspected["cutpoint_digest"],
                    "advance did not invalidate the previous cutpoint")
            successor_token = (
                f"v1:{advanced['database_incarnation_sha256']}:"
                f"{advanced['database_recovery_epoch']}:"
                f"{advanced['cutpoint_digest']}"
            )
            require(advanced.get("recovery_expectation") == successor_token,
                    "advance emitted a noncanonical successor expectation")

            advanced_twice = run_ok([
                str(sync), "database-recovery-advance",
                "--manifest", str(manifest),
                "--expected", successor_token,
            ], label="second exact database recovery advance")
            require_exact_keys(advanced_twice, advance_keys,
                               "second advance response")
            require(
                advanced_twice["database_recovery_epoch"] ==
                    advanced["database_recovery_epoch"] + 1 and
                advanced_twice["state_generation"] ==
                    advanced["state_generation"] + 1,
                "second advance did not establish a distinct replacement source",
            )
            advanced_twice_token = str(advanced_twice["recovery_expectation"])

            overlapping_rollback = Path(str(backup_artifact) + "-wal")
            overlapping_receipt = backup_root / "overlap-replacement.receipt"
            active_before_overlap = sqlite_family_fingerprint(replica_db)
            candidate_before_overlap = sqlite_family_fingerprint(backup_artifact)
            run_failure([
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
                "--rollback", str(overlapping_rollback),
                "--receipt", str(overlapping_receipt),
                "--expected-current", advanced_twice_token,
            ], label="replacement with overlapping candidate and rollback families",
               returncode=2, error_code="invalid_arguments",
               message_fragment="SQLite artifact families overlap")
            require(
                not overlapping_rollback.exists(),
                "overlapping rollback family created a candidate sidecar",
            )
            require(
                sqlite_family_fingerprint(replica_db) == active_before_overlap,
                "overlapping artifact families changed the active SQLite family",
            )
            require(
                sqlite_family_fingerprint(backup_artifact) ==
                    candidate_before_overlap,
                "overlapping artifact families changed the candidate family",
            )

            blocked_rollback = backup_root / "blocked-replacement-rollback.sqlite"
            blocked_receipt = backup_root / "blocked-replacement.receipt"
            blocked_rollback_sidecar = Path(str(blocked_rollback) + "-wal")
            blocked_rollback_sidecar.write_bytes(b"preexisting-rollback-sidecar")
            os.chmod(blocked_rollback_sidecar, 0o600)
            blocked_rollback_family = sqlite_family_fingerprint(blocked_rollback)
            active_before_blocked_rollback = sqlite_family_fingerprint(replica_db)
            candidate_before_blocked_rollback = sqlite_family_fingerprint(
                backup_artifact
            )
            run_failure([
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
                "--rollback", str(blocked_rollback),
                "--receipt", str(blocked_receipt),
                "--expected-current", advanced_twice_token,
            ], label="replacement with preexisting rollback sidecar",
               returncode=1, error_code="operation_failed",
               message_fragment="refuses SQLite snapshot sidecar -wal")
            require(
                not blocked_rollback.exists(),
                "rollback sidecar preflight allowed the main artifact to publish",
            )
            require(
                sqlite_family_fingerprint(blocked_rollback) ==
                    blocked_rollback_family,
                "rollback sidecar preflight changed the blocked artifact family",
            )
            require(
                sqlite_family_fingerprint(replica_db) ==
                    active_before_blocked_rollback,
                "rollback sidecar preflight changed the active SQLite family",
            )
            require(
                sqlite_family_fingerprint(backup_artifact) ==
                    candidate_before_blocked_rollback,
                "rollback sidecar preflight changed the candidate family",
            )
            blocked_rollback_sidecar.unlink()

            stale_rollback = backup_root / "stale-replacement-rollback.sqlite"
            stale_receipt = backup_root / "stale-replacement.receipt"
            active_before_stale_replace = sqlite_family_fingerprint(replica_db)
            run_failure([
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
                "--rollback", str(stale_rollback),
                "--receipt", str(stale_receipt),
                "--expected-current", successor_token,
            ], label="stale database replacement expectation", returncode=1,
               error_code="operation_failed",
               message_fragment="current database expectation is stale",
               timeout=90.0)
            require(not stale_rollback.exists(),
                    "stale replacement published a rollback artifact")
            require(
                sqlite_family_fingerprint(replica_db) ==
                    active_before_stale_replace,
                "stale replacement changed the active SQLite family",
            )

            replacement_rollback = backup_root / "replacement-rollback.sqlite"
            replacement_receipt = backup_root / "replacement.receipt"
            replaced = run_ok([
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
                "--rollback", str(replacement_rollback),
                "--receipt", str(replacement_receipt),
                "--expected-current", advanced_twice_token,
            ], label="offline database replacement", timeout=120.0)
            require_exact_keys(replaced, replacement_keys,
                               "replacement response")
            require_fields(replaced, {
                "command": "database-recovery-replace",
                "terminal_class": "completed",
                "response_schema":
                    "anonsync.local-database-recovery-replacement.response.v3",
                **common,
                "candidate_snapshot_path": str(backup_artifact),
                "candidate_snapshot_sha256":
                    created_backup["snapshot_sha256"],
                "candidate_snapshot_byte_count":
                    created_backup["snapshot_byte_count"],
                "candidate_snapshot_page_size":
                    created_backup["snapshot_page_size"],
                "candidate_snapshot_page_count":
                    created_backup["snapshot_page_count"],
                "rollback_snapshot_path": str(replacement_rollback),
                "replacement_receipt_path": str(replacement_receipt),
                "replacement_entry_stage": "displaced_database_current",
                "replacement_receipt_preexisting": False,
                "replacement_receipt_created_this_invocation": True,
                "rollback_artifact_published_this_invocation": True,
                "logical_database_replacement_performed_this_invocation": True,
                "recovery_epoch_advanced_this_invocation": True,
                "idempotent_reproof_only": False,
                "expected_current_recovery_expectation": advanced_twice_token,
                "displaced_database_incarnation_sha256":
                    advanced_twice["database_incarnation_sha256"],
                "displaced_database_recovery_epoch":
                    advanced_twice["database_recovery_epoch"],
                "displaced_state_generation":
                    advanced_twice["state_generation"],
                "displaced_cutpoint_digest":
                    advanced_twice["cutpoint_digest"],
                "restored_database_incarnation_sha256":
                    inspected["database_incarnation_sha256"],
                "restored_database_recovery_epoch":
                    inspected["database_recovery_epoch"],
                "restored_state_generation": inspected["state_generation"],
                "restored_cutpoint_digest": inspected["cutpoint_digest"],
                "database_incarnation_sha256":
                    advanced["database_incarnation_sha256"],
                "previous_database_recovery_epoch":
                    inspected["database_recovery_epoch"],
                "database_recovery_epoch": advanced["database_recovery_epoch"],
                "state_generation": advanced["state_generation"],
                "cutpoint_digest": advanced["cutpoint_digest"],
                "recovery_expectation": successor_token,
                "candidate_validated_before_mutation": True,
                "candidate_deployment_binding_attested": True,
                "replacement_receipt_immutable": True,
                "replacement_receipt_effect_authority": False,
                "progress_classified_from_active_database": True,
                "rollback_artifact_create_new": True,
                "rollback_artifact_postpublication_reverified": True,
                "rollback_represents_displaced_logical_database": True,
                "raw_sqlite_family_byte_identity_preserved": False,
                "descriptor_rooted_writable_destination": True,
                "sqlite_destination_transaction": True,
                "logical_database_replacement_complete": True,
                "logical_database_replacement_performed": True,
                "restored_cutpoint_reproved_before_advance": True,
                "recovery_epoch_advanced": True,
                "recovery_epoch_advance_complete": True,
                "final_database_reopened_and_reproved": True,
                "final_candidate_artifact_path_reproved": True,
                "final_rollback_artifact_path_reproved": True,
                "final_artifact_reproof_bracketed_by_database_cutpoint": True,
                "artifact_pathnames_continuously_reserved": False,
                "noncooperating_same_uid_artifact_replacement_excluded": False,
                "retention_age_reset_by_exact_source_change": True,
                "payload_store_replacement_performed": False,
                "other_database_replacement_performed": False,
                "mutation_performed": True,
            }, "replacement response")
            require(
                isinstance(replaced.get("backup_step_calls"), int) and
                replaced["backup_step_calls"] > 0 and
                replaced["maximum_reported_page_count"] ==
                    replaced["candidate_snapshot_page_count"] and
                replaced["maximum_reported_remaining_pages"] <=
                    replaced["candidate_snapshot_page_count"],
                "replacement omitted bounded SQLite copy evidence",
            )
            rollback_stat = replacement_rollback.lstat()
            require(
                stat.S_ISREG(rollback_stat.st_mode) and
                rollback_stat.st_nlink == 1 and
                stat.S_IMODE(rollback_stat.st_mode) == 0o600,
                "replacement rollback artifact is not private single-link state",
            )
            require(
                replaced["rollback_snapshot_sha256"] ==
                    file_digest(replacement_rollback) and
                replaced["rollback_snapshot_byte_count"] == rollback_stat.st_size and
                replaced["rollback_snapshot_byte_count"] ==
                    replaced["rollback_snapshot_page_size"] *
                    replaced["rollback_snapshot_page_count"],
                "replacement rollback artifact evidence disagreed with bytes",
            )
            rollback_inspected = run_ok([
                str(sync), "database-backup-inspect",
                "--manifest", str(manifest),
                "--snapshot", str(replacement_rollback),
            ], label="displaced rollback artifact inspection")
            require(
                recovery_state(rollback_inspected) ==
                    recovery_state(advanced_twice),
                "rollback artifact did not preserve the displaced logical database",
            )
            require(
                rollback_inspected["snapshot_sha256"] ==
                    replaced["rollback_snapshot_sha256"],
                "rollback inspection changed the preserved artifact digest",
            )
            after_replacement = run_ok([
                str(sync), "database-recovery-inspect",
                "--manifest", str(manifest),
            ], label="inspection after database replacement")
            require(
                recovery_state(after_replacement) == recovery_state(advanced),
                "replacement did not durably restore and advance the candidate",
            )

            receipt_fields = inspect_replacement_receipt(replacement_receipt)
            require(
                replaced["replacement_receipt_action_sha256"] ==
                    receipt_fields["action_sha256"] and
                replaced["replacement_receipt_record_sha256"] ==
                    receipt_fields["record_sha256"],
                "replacement response disagreed with the immutable receipt",
            )
            require_fields(receipt_fields, {
                "deployment_id": common["deployment_id"],
                "manifest_path_sha256": path_receipt_digest(manifest),
                "replica_database_path_sha256": path_receipt_digest(replica_db),
                "candidate_path_sha256": path_receipt_digest(backup_artifact),
                "rollback_path_sha256": path_receipt_digest(replacement_rollback),
                "receipt_path_sha256": path_receipt_digest(replacement_receipt),
                "expected_database_incarnation_sha256":
                    advanced_twice["database_incarnation_sha256"],
                "expected_database_recovery_epoch":
                    str(advanced_twice["database_recovery_epoch"]),
                "expected_cutpoint_digest": advanced_twice["cutpoint_digest"],
                "candidate_artifact_sha256": created_backup["snapshot_sha256"],
                "rollback_artifact_sha256": replaced["rollback_snapshot_sha256"],
                "action_sha256": replaced["replacement_receipt_action_sha256"],
                "record_sha256": replaced["replacement_receipt_record_sha256"],
            }, "replacement receipt binding")
            require(is_sha256(receipt_fields.get("manifest_digest")),
                    "replacement receipt omitted manifest digest binding")
            receipt_bytes = replacement_receipt.read_bytes()
            require(
                all(str(path).encode() not in receipt_bytes for path in (
                    manifest, replica_db, backup_artifact,
                    replacement_rollback, replacement_receipt,
                )),
                "replacement receipt leaked selected absolute paths",
            )
            rollback_bytes = replacement_rollback.read_bytes()
            rollback_digest = file_digest(replacement_rollback)
            candidate_bytes = backup_artifact.read_bytes()
            candidate_digest = file_digest(backup_artifact)

            # The exact completed action is restart-idempotent. The immutable
            # receipt is re-read, while the active database itself proves that
            # both logical replacement and recovery-epoch advancement finished.
            replayed = run_ok([
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
                "--rollback", str(replacement_rollback),
                "--receipt", str(replacement_receipt),
                "--expected-current", advanced_twice_token,
            ], label="completed database replacement replay", timeout=120.0)
            require_exact_keys(replayed, replacement_keys,
                               "completed replacement replay response")
            require_fields(replayed, {
                "response_schema":
                    "anonsync.local-database-recovery-replacement.response.v3",
                "replacement_entry_stage": "recovery_epoch_advanced",
                "replacement_receipt_preexisting": True,
                "replacement_receipt_created_this_invocation": False,
                "rollback_artifact_published_this_invocation": False,
                "logical_database_replacement_performed_this_invocation": False,
                "recovery_epoch_advanced_this_invocation": False,
                "idempotent_reproof_only": True,
                "logical_database_replacement_complete": True,
                "logical_database_replacement_performed": False,
                "recovery_epoch_advanced": False,
                "recovery_epoch_advance_complete": True,
                "final_database_reopened_and_reproved": True,
                "final_candidate_artifact_path_reproved": True,
                "final_rollback_artifact_path_reproved": True,
                "final_artifact_reproof_bracketed_by_database_cutpoint": True,
                "artifact_pathnames_continuously_reserved": False,
                "noncooperating_same_uid_artifact_replacement_excluded": False,
                "mutation_performed": False,
                "backup_step_calls": 0,
                "maximum_reported_page_count": 0,
                "maximum_reported_remaining_pages": 0,
                "recovery_expectation": successor_token,
            }, "completed replacement replay response")
            require(
                recovery_state(replayed) == recovery_state(advanced),
                "completed replacement replay changed the final database",
            )

            # Stable selected artifact drift is rejected on every invocation,
            # independently of resident images retained by an earlier process.
            # The final in-invocation pathname reopening is bound separately by
            # the C++ source audit and the response-v3 success contract; this
            # oracle does not claim a continuous reservation against a hostile
            # same-UID writer.
            family_before_candidate_tamper = sqlite_family_fingerprint(replica_db)
            backup_artifact.write_bytes(rollback_bytes)
            os.chmod(backup_artifact, 0o600)
            run_failure([
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
                "--rollback", str(replacement_rollback),
                "--receipt", str(replacement_receipt),
                "--expected-current", advanced_twice_token,
            ], label="changed candidate artifact pathname", returncode=1,
               error_code="operation_failed",
               message_fragment="does not match the selected action")
            require(
                sqlite_family_fingerprint(replica_db) ==
                    family_before_candidate_tamper,
                "changed candidate artifact altered the active database",
            )
            backup_artifact.write_bytes(candidate_bytes)
            os.chmod(backup_artifact, 0o600)
            require(file_digest(backup_artifact) == candidate_digest,
                    "test candidate restoration changed immutable bytes")

            family_before_rollback_tamper = sqlite_family_fingerprint(replica_db)
            replacement_rollback.write_bytes(candidate_bytes)
            os.chmod(replacement_rollback, 0o600)
            run_failure([
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
                "--rollback", str(replacement_rollback),
                "--receipt", str(replacement_receipt),
                "--expected-current", advanced_twice_token,
            ], label="changed rollback artifact pathname", returncode=1,
               error_code="operation_failed",
               message_fragment="rollback artifact changed")
            require(
                sqlite_family_fingerprint(replica_db) ==
                    family_before_rollback_tamper,
                "changed rollback artifact altered the active database",
            )
            replacement_rollback.write_bytes(rollback_bytes)
            os.chmod(replacement_rollback, 0o600)
            require(file_digest(replacement_rollback) == rollback_digest,
                    "test rollback restoration changed immutable bytes")

            # The receipt remains evidence rather than effect authority: damage,
            # relaxed permissions, or another hard link all fail before any
            # database state can be trusted from it.
            family_before_bad_receipt = sqlite_family_fingerprint(replica_db)
            replacement_receipt.write_bytes(receipt_bytes[:-1] + b"X")
            run_failure([
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
                "--rollback", str(replacement_rollback),
                "--receipt", str(replacement_receipt),
                "--expected-current", advanced_twice_token,
            ], label="damaged replacement receipt", returncode=1,
               error_code="operation_failed", message_fragment="receipt framing is invalid")
            require(sqlite_family_fingerprint(replica_db) == family_before_bad_receipt,
                    "damaged receipt changed the active database")
            replacement_receipt.write_bytes(receipt_bytes)
            os.chmod(replacement_receipt, 0o600)

            os.chmod(replacement_receipt, 0o640)
            run_failure([
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
                "--rollback", str(replacement_rollback),
                "--receipt", str(replacement_receipt),
                "--expected-current", advanced_twice_token,
            ], label="nonprivate replacement receipt", returncode=1,
               error_code="operation_failed", message_fragment="mode 0600")
            os.chmod(replacement_receipt, 0o600)

            receipt_hardlink = backup_root / "replacement-receipt-hardlink"
            os.link(replacement_receipt, receipt_hardlink)
            run_failure([
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
                "--rollback", str(replacement_rollback),
                "--receipt", str(replacement_receipt),
                "--expected-current", advanced_twice_token,
            ], label="hardlinked replacement receipt", returncode=1,
               error_code="operation_failed", message_fragment="single-link")
            receipt_hardlink.unlink()
            require(file_digest(replacement_rollback) == rollback_digest,
                    "receipt rejection changed the rollback artifact")

            # A completed database without its rollback cannot be reconstructed
            # from the receipt: rollback recreation is admitted only while the
            # active state is still the exact displaced database.
            replacement_rollback.unlink()
            run_failure([
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
                "--rollback", str(replacement_rollback),
                "--receipt", str(replacement_receipt),
                "--expected-current", advanced_twice_token,
            ], label="missing rollback after completed replacement", returncode=1,
               error_code="operation_failed",
               message_fragment="current database expectation is stale")
            replacement_rollback.write_bytes(rollback_bytes)
            os.chmod(replacement_rollback, 0o600)
            require(file_digest(replacement_rollback) == rollback_digest,
                    "test rollback restoration changed immutable bytes")

            # Simulate a process crash after the candidate SQLite transaction
            # committed but before recovery-epoch advancement. The immutable
            # receipt plus active candidate cutpoint admits only the missing
            # epoch transition; no second logical database copy occurs.
            install_logical_sqlite_image(backup_artifact, replica_db)
            candidate_pending = run_ok([
                str(sync), "database-recovery-inspect", "--manifest", str(manifest),
            ], label="candidate-installed crash cutpoint inspection")
            require(recovery_state(candidate_pending) == recovery_state(inspected),
                    "test candidate-installed cutpoint differs from the artifact")
            resumed_pending = run_ok([
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
                "--rollback", str(replacement_rollback),
                "--receipt", str(replacement_receipt),
                "--expected-current", advanced_twice_token,
            ], label="candidate-installed replacement resume", timeout=120.0)
            require_exact_keys(resumed_pending, replacement_keys,
                               "candidate-installed resume response")
            require_fields(resumed_pending, {
                "replacement_entry_stage": "candidate_installed_epoch_pending",
                "replacement_receipt_preexisting": True,
                "replacement_receipt_created_this_invocation": False,
                "rollback_artifact_published_this_invocation": False,
                "logical_database_replacement_performed_this_invocation": False,
                "recovery_epoch_advanced_this_invocation": True,
                "idempotent_reproof_only": False,
                "logical_database_replacement_performed": False,
                "recovery_epoch_advanced": True,
                "mutation_performed": True,
                "backup_step_calls": 0,
                "maximum_reported_page_count": 0,
                "maximum_reported_remaining_pages": 0,
                "recovery_expectation": successor_token,
            }, "candidate-installed resume response")
            require(recovery_state(resumed_pending) == recovery_state(advanced),
                    "candidate-installed resume did not advance exactly once")

            # Simulate the earliest durable crash: receipt published, rollback
            # absent, active database still exact displaced state. The owner
            # recaptures and proves the rollback, then completes the action.
            install_logical_sqlite_image(replacement_rollback, replica_db)
            displaced_again = run_ok([
                str(sync), "database-recovery-inspect", "--manifest", str(manifest),
            ], label="receipt-only displaced cutpoint inspection")
            require(recovery_state(displaced_again) == recovery_state(advanced_twice),
                    "test receipt-only cutpoint differs from displaced database")
            replacement_rollback.unlink()
            resumed_receipt_only = run_ok([
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
                "--rollback", str(replacement_rollback),
                "--receipt", str(replacement_receipt),
                "--expected-current", advanced_twice_token,
            ], label="receipt-only database replacement resume", timeout=120.0)
            require_exact_keys(resumed_receipt_only, replacement_keys,
                               "receipt-only resume response")
            require_fields(resumed_receipt_only, {
                "replacement_entry_stage": "displaced_database_current",
                "replacement_receipt_preexisting": True,
                "replacement_receipt_created_this_invocation": False,
                "rollback_artifact_published_this_invocation": True,
                "logical_database_replacement_performed_this_invocation": True,
                "recovery_epoch_advanced_this_invocation": True,
                "idempotent_reproof_only": False,
                "logical_database_replacement_performed": True,
                "recovery_epoch_advanced": True,
                "mutation_performed": True,
                "recovery_expectation": successor_token,
            }, "receipt-only resume response")
            require(
                recovery_state(resumed_receipt_only) == recovery_state(advanced) and
                file_digest(replacement_rollback) == rollback_digest,
                "receipt-only resume did not restore exact rollback and successor",
            )

            # A state outside the three admitted exact cutpoints fails closed.
            unknown_first = run_ok([
                str(sync), "database-recovery-advance",
                "--manifest", str(manifest),
                "--expected", successor_token,
            ], label="first unknown-continuity setup advance")
            unknown_second = run_ok([
                str(sync), "database-recovery-advance",
                "--manifest", str(manifest),
                "--expected", str(unknown_first["recovery_expectation"]),
            ], label="second unknown-continuity setup advance")
            require(recovery_state(unknown_first) == recovery_state(advanced_twice),
                    "first setup advance did not reproduce displaced cutpoint")
            unknown_before = sqlite_family_fingerprint(replica_db)
            run_failure([
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
                "--rollback", str(replacement_rollback),
                "--receipt", str(replacement_receipt),
                "--expected-current", advanced_twice_token,
            ], label="unknown replacement continuity", returncode=1,
               error_code="operation_failed", message_fragment="continuity is unknown")
            require(sqlite_family_fingerprint(replica_db) == unknown_before,
                    "unknown continuity changed the active database")

            # Return to the exact candidate-pending cutpoint and prove ordinary
            # resume still completes after an unknown-state rejection.
            install_logical_sqlite_image(backup_artifact, replica_db)
            recovered_after_unknown = run_ok([
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
                "--rollback", str(replacement_rollback),
                "--receipt", str(replacement_receipt),
                "--expected-current", advanced_twice_token,
            ], label="replacement recovery after unknown-state rejection",
               timeout=120.0)
            require(
                recovered_after_unknown["replacement_entry_stage"] ==
                    "candidate_installed_epoch_pending" and
                recovery_state(recovered_after_unknown) == recovery_state(advanced),
                "replacement did not recover after unknown-state rejection",
            )

            old_backup_after_advance = run_ok([
                str(sync), "database-backup-inspect",
                "--manifest", str(manifest),
                "--snapshot", str(backup_artifact),
            ], label="immutable backup inspection after source advance")
            require(
                recovery_state(old_backup_after_advance) ==
                    recovery_state(inspected),
                "source recovery advance rewrote the detached backup lineage",
            )
            require(
                old_backup_after_advance["snapshot_sha256"] ==
                    created_backup["snapshot_sha256"],
                "source recovery advance changed detached backup bytes",
            )

            # Prove the final pathname reproof is a real post-effect cutpoint,
            # not merely a source-shape claim. First enlarge the exact active
            # SQLite image with dropped-table free pages. The logical cutpoint
            # stays unchanged, but publishing its rollback after the immutable
            # receipt creates a deterministic pause window. Stop the shipping
            # process as soon as the receipt becomes visible, replace the
            # already-sealed candidate pathname, and resume. The database effect
            # must commit from retained candidate bytes, final pathname reproof
            # must reject success, and a second process must complete by exact
            # active-database classification without repeating the effect.
            bloat_connection = sqlite3.connect(str(replica_db))
            try:
                bloat_connection.execute("PRAGMA busy_timeout=5000")
                bloat_connection.execute("PRAGMA secure_delete=OFF")
                bloat_connection.execute(
                    "CREATE TABLE main.anonsync_final_reproof_bloat("
                    "payload BLOB NOT NULL)"
                )
                bloat_connection.execute(
                    "INSERT INTO main.anonsync_final_reproof_bloat(payload) "
                    "VALUES(zeroblob(?))", (32 * 1024 * 1024,)
                )
                bloat_connection.commit()
                bloat_connection.execute(
                    "DROP TABLE main.anonsync_final_reproof_bloat"
                )
                bloat_connection.commit()
                checkpoint = bloat_connection.execute(
                    "PRAGMA wal_checkpoint(TRUNCATE)"
                ).fetchone()
                page_size_row = bloat_connection.execute(
                    "PRAGMA page_size"
                ).fetchone()
                freelist_row = bloat_connection.execute(
                    "PRAGMA freelist_count"
                ).fetchone()
                require(
                    checkpoint is not None and int(checkpoint[0]) == 0,
                    "final pathname reproof fixture could not checkpoint its "
                    "dropped-table free pages",
                )
                require(
                    page_size_row is not None and freelist_row is not None and
                    int(page_size_row[0]) * int(freelist_row[0]) >=
                        16 * 1024 * 1024,
                    "final pathname reproof fixture did not retain a bounded "
                    "rollback publication window",
                )
            finally:
                bloat_connection.close()

            bloated_active = run_ok([
                str(sync), "database-recovery-inspect",
                "--manifest", str(manifest),
            ], label="final pathname reproof bloated-source inspection")
            require(
                recovery_state(bloated_active) == recovery_state(advanced),
                "dropped-table free pages changed the active logical cutpoint",
            )

            race_candidate = replacement_rollback
            race_rollback = backup_root / "final-reproof-race-rollback.sqlite"
            race_receipt = backup_root / "final-reproof-race.receipt"
            race_candidate_held = (
                backup_root / "final-reproof-race-candidate-held.sqlite"
            )
            race_command = [
                str(sync), "database-recovery-replace",
                "--manifest", str(manifest),
                "--snapshot", str(race_candidate),
                "--rollback", str(race_rollback),
                "--receipt", str(race_receipt),
                "--expected-current", successor_token,
            ]
            race_process: subprocess.Popen[str] | None = None
            candidate_was_moved = False
            process_was_stopped = False
            try:
                race_process = subprocess.Popen(
                    race_command, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True,
                )
                publication_deadline = time.monotonic() + 20.0
                while not race_receipt.exists():
                    if race_process.poll() is not None:
                        stdout, stderr = race_process.communicate()
                        fail(
                            "final candidate pathname replacement race exited "
                            "before immutable receipt publication\n"
                            f"stdout:\n{stdout}stderr:\n{stderr}"
                        )
                    if time.monotonic() >= publication_deadline:
                        fail(
                            "final candidate pathname replacement race did not "
                            "publish its immutable receipt"
                        )
                    time.sleep(0.001)

                os.kill(race_process.pid, signal.SIGSTOP)
                stop_deadline = time.monotonic() + 5.0
                while True:
                    status_path = Path(f"/proc/{race_process.pid}/status")
                    if status_path.is_file():
                        status_text = status_path.read_text(encoding="utf-8")
                        if ("State:\tT" in status_text or
                                "State:\tt" in status_text):
                            process_was_stopped = True
                            break
                    if race_process.poll() is not None:
                        stdout, stderr = race_process.communicate()
                        fail(
                            "final candidate pathname replacement race exited "
                            "before SIGSTOP became effective\n"
                            f"stdout:\n{stdout}stderr:\n{stderr}"
                        )
                    if time.monotonic() >= stop_deadline:
                        fail(
                            "final candidate pathname replacement race did not "
                            "enter a stopped state"
                        )
                    time.sleep(0.001)

                race_candidate.rename(race_candidate_held)
                candidate_was_moved = True
                shutil.copyfile(backup_artifact, race_candidate)
                os.chmod(race_candidate, 0o600)
                os.kill(race_process.pid, signal.SIGCONT)
                process_was_stopped = False

                stdout, stderr = race_process.communicate(timeout=120.0)
                completed_race = subprocess.CompletedProcess(
                    race_command, race_process.returncode, stdout, stderr
                )
                race_failure = parse_json_output(
                    completed_race, race_command,
                    "final candidate pathname replacement race",
                )
                require(
                    race_process.returncode == 1 and
                    race_failure.get("terminal_class") == "stopped" and
                    race_failure.get("error_code") == "operation_failed",
                    "final candidate pathname replacement race returned the "
                    f"wrong failure class: {race_failure}",
                )
                require(
                    "candidate artifact changed" in
                        str(race_failure.get("message")) and
                    "candidate artifact changed" in stderr,
                    "final candidate pathname replacement race did not fail "
                    "at the final named-artifact reproof",
                )
            finally:
                if race_process is not None and race_process.poll() is None:
                    if process_was_stopped:
                        os.kill(race_process.pid, signal.SIGCONT)
                    race_process.kill()
                    race_process.communicate()
                if candidate_was_moved:
                    if race_candidate.exists():
                        race_candidate.unlink()
                    if race_candidate_held.exists():
                        race_candidate_held.rename(race_candidate)

            after_final_reproof_failure = run_ok([
                str(sync), "database-recovery-inspect",
                "--manifest", str(manifest),
            ], label="final candidate pathname reproof failure inspection")
            require(
                recovery_state(after_final_reproof_failure) ==
                    recovery_state(unknown_second),
                "final candidate pathname reproof failure did not preserve the "
                "exact committed recovery successor",
            )
            resumed_final_reproof = run_ok(
                race_command,
                label="final candidate pathname reproof resume",
                timeout=120.0,
            )
            require_exact_keys(
                resumed_final_reproof, replacement_keys,
                "final candidate pathname reproof resume response",
            )
            require_fields(resumed_final_reproof, {
                "response_schema":
                    "anonsync.local-database-recovery-replacement.response.v3",
                "replacement_entry_stage": "recovery_epoch_advanced",
                "idempotent_reproof_only": True,
                "mutation_performed": False,
                "final_candidate_artifact_path_reproved": True,
                "final_rollback_artifact_path_reproved": True,
                "final_artifact_reproof_bracketed_by_database_cutpoint": True,
                "artifact_pathnames_continuously_reserved": False,
                "noncooperating_same_uid_artifact_replacement_excluded": False,
            }, "final candidate pathname reproof resume response")
            require(
                recovery_state(resumed_final_reproof) ==
                    recovery_state(unknown_second),
                "final candidate pathname reproof resume changed the committed "
                "recovery successor",
            )

            # Return the primary deployment to the canonical post-backup recovery
            # lineage used by the remainder of this process oracle. Logical copy
            # also discards the test-only free-page inflation.
            install_logical_sqlite_image(backup_artifact, replica_db)
            restored_after_final_reproof = run_ok([
                str(sync), "database-recovery-advance",
                "--manifest", str(manifest),
                "--expected", expected_token,
            ], label="final candidate pathname reproof lineage restoration")
            require(
                recovery_state(restored_after_final_reproof) ==
                    recovery_state(advanced),
                "final candidate pathname reproof test did not restore the "
                "canonical final lineage",
            )

            family_before_reuse = sqlite_family_fingerprint(replica_db)
            run_failure([
                str(sync), "database-recovery-advance", "--manifest", str(manifest),
                "--expected", expected_token,
            ], label="reused recovery expectation", returncode=1,
               error_code="operation_failed",
               message_fragment="database recovery expectation is stale")
            require(
                sqlite_family_fingerprint(replica_db) == family_before_reuse,
                "reused recovery expectation changed SQLite family bytes, "
                "modes, or members",
            )
            final_inspection = run_ok([
                str(sync), "database-recovery-inspect",
                "--manifest", str(manifest),
            ], label="final database recovery inspection")
            require(
                recovery_state(final_inspection) == (
                    advanced["database_incarnation_sha256"],
                    advanced["database_recovery_epoch"],
                    advanced["state_generation"],
                    advanced["cutpoint_digest"],
                    successor_token,
                ),
                "final inspection disagreed with the committed recovery transition",
            )
        finally:
            for live, concealed in reversed(hidden):
                if concealed.exists() and not live.exists():
                    concealed.rename(live)

        after_status = run_ok([
            str(replica), "status", "--manifest", str(manifest),
        ], label="status after recovery")
        require(
            after_status.get("replica_state_generation") ==
                before_status.get("replica_state_generation") + 1,
            "recovery did not advance exactly one replica state generation",
        )
        require(
            after_status.get("replica_cutpoint_digest") !=
                before_status.get("replica_cutpoint_digest"),
            "recovery did not invalidate the public replica cutpoint",
        )
        ignored = {"replica_state_generation", "replica_cutpoint_digest"}
        require(
            {key: value for key, value in after_status.items() if key not in ignored} ==
            {key: value for key, value in before_status.items() if key not in ignored},
            "recovery changed causal, outbox, policy, payload, effect, or membership state",
        )

    print(f"anonsync database recovery process: {CHECKS} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
