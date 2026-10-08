#!/usr/bin/env python3
"""Process-level proof for the configured-folder product seam.

The test launches only shipped executables. It proves explicit sealed catalog
bootstrap, manifest-derived catalog identity, existing-only refusal, bounded
restart progress, fresh-process idempotence, and the current non-deletion rule.
"""

from __future__ import annotations

import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tempfile
from typing import Any, NoReturn, Sequence


def fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def invoke(command: Sequence[str], *, timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command), check=False, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, timeout=timeout,
    )


def parse_one_json(completed: subprocess.CompletedProcess[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        fail(
            f"{label} did not emit one JSON object: {error}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    if not isinstance(value, dict):
        fail(f"{label} JSON is not an object")
    return value


def run_ok(command: Sequence[str], label: str) -> dict[str, Any]:
    completed = invoke(command)
    value = parse_one_json(completed, label)
    if completed.returncode != 0:
        fail(
            f"{label} failed with {completed.returncode}: {command}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    if completed.stderr:
        fail(f"{label} wrote diagnostics on success: {completed.stderr}")
    return value


def run_stopped(
    command: Sequence[str],
    label: str,
    *,
    diagnostic_prefix: str = "anonsync_folder: ",
) -> dict[str, Any]:
    completed = invoke(command)
    value = parse_one_json(completed, label)
    if completed.returncode == 0:
        fail(f"{label} unexpectedly succeeded: {completed.stdout}")
    if value.get("terminal_class") != "stopped":
        fail(f"{label} did not emit a stopped terminal class: {value}")
    if not completed.stderr.startswith(diagnostic_prefix):
        fail(f"{label} omitted its diagnostic prefix: {completed.stderr!r}")
    return value


def expect(value: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    for key, wanted in expected.items():
        observed = value.get(key)
        if observed != wanted:
            fail(
                f"{label} field {key!r} was {observed!r}, expected {wanted!r}: "
                f"{json.dumps(value, sort_keys=True)}"
            )


def sqlite_scalar(path: Path, sql: str) -> Any:
    uri = f"file:{path}?mode=ro"
    # sqlite3.Connection's context manager commits or rolls back but does not
    # close.  An unclosed read connection can retain WAL locks across the next
    # real-process authority handoff, so make descriptor release explicit.
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        return connection.execute(sql).fetchone()[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replica", required=True, type=Path)
    parser.add_argument("--folder", required=True, type=Path)
    parser.add_argument("--sync", required=True, type=Path)
    args = parser.parse_args()
    replica = args.replica.resolve(strict=True)
    folder = args.folder.resolve(strict=True)
    sync = args.sync.resolve(strict=True)

    with tempfile.TemporaryDirectory(prefix="anonsync-folder-cli-") as raw_root:
        root = Path(raw_root)
        os.chmod(root, 0o700)
        database_root = root / "db"
        payload_root = root / "payload"
        files_root = root / "files"
        for directory in (database_root, payload_root, files_root):
            directory.mkdir(mode=0o700)

        manifest = database_root / "deployment.json"
        replica_db = database_root / "replica.sqlite"
        effect_db = database_root / "effect.sqlite"
        catalog = Path(str(replica_db) + ".folder-catalog.sqlite3")

        deployment = run_ok([
            str(replica), "init", "--manifest", str(manifest),
            "--replica-db", str(replica_db),
            "--payload-root", str(payload_root),
            "--effect-db", str(effect_db),
            "--files-root", str(files_root),
            "--folder", "configured-folder",
            "--local-device", "node-a", "--local-epoch", "1",
        ], "replica deployment bootstrap")
        expect(deployment, {
            "profile": "custom", "folder_id": "configured-folder",
            "local_device_id": "node-a", "local_epoch": 1,
            "manifest_path": str(manifest), "replica_db": str(replica_db),
            "payload_root": str(payload_root), "effect_db": str(effect_db),
            "files_root": str(files_root),
        }, "replica deployment bootstrap")

        missing = run_stopped([
            str(folder), "run", "--manifest", str(manifest),
        ], "missing catalog operational refusal")
        if catalog.exists():
            fail("operational run created a missing folder catalog")
        if "requires an existing guarded main database" not in str(missing.get("message")):
            fail(f"missing catalog failure was not existing-only: {missing}")

        initialized = run_ok([
            str(folder), "init", "--manifest", str(manifest),
        ], "folder catalog bootstrap")
        expect(initialized, {
            "command": "init", "terminal_class": "initialized",
            "manifest_path": str(manifest), "catalog_path": str(catalog),
            "deployment_id": deployment["deployment_id"],
            "folder_id": "configured-folder", "local_device_id": "node-a",
            "local_epoch": 1, "catalog_generation": 0,
            "catalog_entry_count": 0,
        }, "folder catalog bootstrap")
        if not catalog.is_file():
            fail("folder catalog bootstrap did not publish the derived path")
        if catalog.stat().st_mode & 0o777 != 0o600:
            fail("folder catalog is not private mode 0600")
        if sqlite_scalar(catalog, "PRAGMA application_id") != 0x41535205:
            fail("folder catalog has the wrong role-specific application ID")
        if sqlite_scalar(catalog, "PRAGMA journal_mode") != "wal":
            fail("folder catalog was not promoted to WAL")
        if sqlite_scalar(
            catalog,
            "SELECT store_role FROM anonsync_store_set_binding WHERE id=1",
        ) != "folder-catalog":
            fail("folder catalog durable binding has the wrong role")

        policy_status = run_ok([
            str(sync), "selective-sync-status",
            "--manifest", str(manifest),
        ], "initial selective-sync status")
        expect(policy_status, {
            "command": "selective-sync-status",
            "terminal_class": "completed",
            "response_schema":
                "anonsync.local-selective-sync-policy.response.v1",
            "policy_generation": 1,
            "policy_default_mode": "materialize",
            "policy_rule_count": 0,
            "policy_rule_path_bytes": 0,
            "absence_inference_fence_generation": 0,
            "absence_inference_fence_active": False,
            "mutation_performed": False,
            "payload_store_observed": False,
            "rooted_files_observed": False,
            "replica_database_observed": False,
            "network_started": False,
            "deployment_singleton_acquired": True,
        }, "initial selective-sync status")
        initial_content_digest = policy_status["content_catalog_digest"]

        policy_set_command = [
            str(sync), "selective-sync-set",
            "--manifest", str(manifest),
            "--default", "metadata_only",
            "--rule", "materialize=keep",
            "--rule", "metadata_only=media/archive",
        ]
        policy_set = run_ok(policy_set_command, "selective-sync replacement")
        expect(policy_set, {
            "command": "selective-sync-set",
            "terminal_class": "completed",
            "response_schema":
                "anonsync.local-selective-sync-policy.response.v1",
            "policy_generation": 2,
            "policy_default_mode": "metadata_only",
            "policy_rule_count": 2,
            "policy_rule_path_bytes": len("keep") + len("media/archive"),
            "absence_inference_fence_generation": 0,
            "absence_inference_fence_active": False,
            "previous_policy_generation": 1,
            "mutation_performed": True,
            "scheduling_frontiers_reset": True,
            "service_must_be_stopped": True,
            "content_catalog_digest": initial_content_digest,
            "catalog_entry_count": 0,
        }, "selective-sync replacement")
        if policy_set.get("rules") != [
            {"canonical_path": "keep", "mode": "materialize"},
            {"canonical_path": "media/archive", "mode": "metadata_only"},
        ]:
            fail(f"selective-sync rules were not canonical: {policy_set}")
        if sqlite_scalar(
            catalog,
            "SELECT selection_generation FROM "
            "sync_replica_folder_catalog_meta WHERE id=1",
        ) != 2:
            fail("selective-sync generation was not durable")
        if sqlite_scalar(
            catalog,
            "SELECT selection_absence_fence_generation FROM "
            "sync_replica_folder_catalog_meta WHERE id=1",
        ) != 0:
            fail("pure exclusion opened a durable selective-sync absence fence")
        if sqlite_scalar(
            catalog,
            "SELECT count(*) FROM "
            "sync_replica_folder_catalog_selection_rules",
        ) != 2:
            fail("selective-sync rule set was not durable")

        policy_replay = run_ok(
            policy_set_command, "selective-sync idempotent replay")
        expect(policy_replay, {
            "policy_generation": 2,
            "policy_digest": policy_set["policy_digest"],
            "catalog_digest": policy_set["catalog_digest"],
            "absence_inference_fence_generation": 0,
            "previous_policy_generation": 2,
            "mutation_performed": False,
            "scheduling_frontiers_reset": False,
        }, "selective-sync idempotent replay")

        invalid_policy = run_stopped([
            str(sync), "selective-sync-set",
            "--manifest", str(manifest),
            "--default", "materialize",
            "--rule", "metadata_only=duplicate",
            "--rule", "materialize=duplicate",
        ], "duplicate selective-sync rule refusal",
            diagnostic_prefix="anonsync_sync: ")
        if invalid_policy.get("error_code") != "invalid_arguments":
            fail(f"duplicate selective-sync rule had wrong error: {invalid_policy}")
        if sqlite_scalar(
            catalog,
            "SELECT selection_generation FROM "
            "sync_replica_folder_catalog_meta WHERE id=1",
        ) != 2:
            fail("invalid selective-sync policy changed durable generation")

        policy_reset = run_ok([
            str(sync), "selective-sync-set",
            "--manifest", str(manifest),
            "--default", "materialize",
        ], "selective-sync materialization reset")
        expect(policy_reset, {
            "policy_generation": 3,
            "policy_default_mode": "materialize",
            "policy_rule_count": 0,
            "absence_inference_fence_generation": 3,
            "previous_policy_generation": 2,
            "mutation_performed": True,
            "content_catalog_digest": initial_content_digest,
        }, "selective-sync materialization reset")

        duplicate = run_stopped([
            str(folder), "init", "--manifest", str(manifest),
        ], "duplicate catalog bootstrap refusal")
        if "already exists" not in str(duplicate.get("message")):
            fail(f"duplicate bootstrap did not refuse create-new: {duplicate}")

        (files_root / "a.txt").write_bytes(b"aaaaa\n")
        (files_root / "b.txt").write_bytes(b"bbbbb\n")
        os.symlink("a.txt", files_root / "ignored-link")

        bounded = run_ok([
            str(folder), "run", "--manifest", str(manifest),
            "--maximum-file-bytes", "6",
            "--maximum-total-file-bytes", "6",
        ], "bounded partial pass")
        expect(bounded, {
            "command": "run", "terminal_class": "completed",
            "catalog_generation_before": 0,
            "catalog_generation_after": 1,
            "catalog_entry_count_before": 0,
            "catalog_entry_count_after": 1,
            "regular_files": 1, "ignored_symbolic_links": 0,
            "local_published": 1, "local_catalog_no_op": 0,
            "completed_local_scan_epoch": False,
            "restarted_local_scan_epoch": False,
            "local_scan_seen_path_count": 1,
            "local_scan_resume_after_path": "a.txt",
        }, "bounded partial pass")

        resumed = run_ok([
            str(folder), "run", "--manifest", str(manifest),
        ], "restart completion")
        expect(resumed, {
            "command": "run", "terminal_class": "completed",
            "catalog_generation_before": 1,
            "catalog_generation_after": 2,
            "catalog_entry_count_before": 1,
            "catalog_entry_count_after": 2,
            "regular_files": 1, "ignored_symbolic_links": 1,
            "local_published": 1, "local_catalog_no_op": 0,
            "completed_local_scan_epoch": True,
            "restarted_local_scan_epoch": False,
            "local_scan_seen_path_count": 0,
            "local_scan_resume_after_path": "",
        }, "restart completion")

        no_op = run_ok([
            str(folder), "run", "--manifest", str(manifest),
        ], "fresh-process no-op")
        expect(no_op, {
            "catalog_generation_before": 2,
            "catalog_generation_after": 2,
            "catalog_entry_count_before": 2,
            "catalog_entry_count_after": 2,
            "local_published": 0, "local_catalog_no_op": 2,
            "used_idle_fast_path": True,
            "completed_local_scan_epoch": True,
            "local_scan_seen_path_count": 0,
            "local_scan_resume_after_path": "",
            "catalog_digest_before": resumed["catalog_digest_after"],
            "catalog_digest_after": resumed["catalog_digest_after"],
            "replica_cutpoint_before": resumed["replica_cutpoint_after"],
            "replica_cutpoint_after": resumed["replica_cutpoint_after"],
        }, "fresh-process no-op")

        # A successfully completed whole-folder traversal grants absence
        # authority for an exact cataloged file base. The fresh process must
        # publish one tombstone, retain that absence as an idempotent cutpoint,
        # and treat a later same-path file as a causal resurrection.
        (files_root / "a.txt").unlink()
        deleted = run_ok([
            str(folder), "run", "--manifest", str(manifest),
        ], "local deletion")
        expect(deleted, {
            "catalog_generation_before": 2,
            "catalog_generation_after": 3,
            "catalog_entry_count_before": 2,
            "catalog_entry_count_after": 2,
            "regular_files": 1, "ignored_symbolic_links": 1,
            "local_published": 1, "local_catalog_no_op": 1,
            "remote_applied": 0,
        }, "local deletion")
        if sqlite_scalar(
            catalog,
            "SELECT value_kind FROM sync_replica_folder_catalog_entries "
            "WHERE canonical_path='a.txt'",
        ) != 2:
            fail("local deletion did not persist a tombstone catalog entry")

        deleted_no_op = run_ok([
            str(folder), "run", "--manifest", str(manifest),
        ], "fresh-process deletion no-op")
        expect(deleted_no_op, {
            "catalog_generation_before": 3,
            "catalog_generation_after": 3,
            "catalog_entry_count_before": 2,
            "catalog_entry_count_after": 2,
            "local_published": 0,
            "catalog_digest_before": deleted["catalog_digest_after"],
            "catalog_digest_after": deleted["catalog_digest_after"],
            "replica_cutpoint_before": deleted["replica_cutpoint_after"],
            "replica_cutpoint_after": deleted["replica_cutpoint_after"],
        }, "fresh-process deletion no-op")

        (files_root / "a.txt").write_bytes(b"aaaaa\n")
        repaired = run_ok([
            str(folder), "run", "--manifest", str(manifest),
        ], "same-path resurrection")
        expect(repaired, {
            "catalog_generation_before": 3,
            "catalog_generation_after": 4,
            "catalog_entry_count_before": 2,
            "catalog_entry_count_after": 2,
            "local_published": 1, "local_catalog_no_op": 1,
            "replica_cutpoint_before": deleted_no_op["replica_cutpoint_after"],
        }, "same-path resurrection")
        if repaired["replica_cutpoint_after"] == repaired["replica_cutpoint_before"]:
            fail("same-path resurrection did not mint a file successor")
        if sqlite_scalar(
            catalog,
            "SELECT value_kind FROM sync_replica_folder_catalog_entries "
            "WHERE canonical_path='a.txt'",
        ) != 1:
            fail("same-path resurrection did not restore a file catalog entry")

        # Operational open must not recreate a lost or mistyped authority.
        held = catalog.with_name(catalog.name + ".held")
        catalog.rename(held)
        missing_again = run_stopped([
            str(folder), "run", "--manifest", str(manifest),
        ], "removed catalog operational refusal")
        if catalog.exists():
            fail("operational run recreated the removed folder catalog")
        if "requires an existing guarded main database" not in str(
            missing_again.get("message")
        ):
            fail(f"removed catalog refusal was not existing-only: {missing_again}")
        held.rename(catalog)

        restored = run_ok([
            str(folder), "run", "--manifest", str(manifest),
        ], "restored catalog no-op")
        if restored.get("catalog_digest_after") != repaired.get("catalog_digest_after"):
            fail("restored exact catalog did not preserve its durable cutpoint")

    print("anonsync_folder CLI process test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
