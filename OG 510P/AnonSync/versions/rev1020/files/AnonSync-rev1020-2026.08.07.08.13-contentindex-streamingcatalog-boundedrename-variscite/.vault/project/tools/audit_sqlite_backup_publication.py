#!/usr/bin/env python3
"""Fail-closed audit of live SQLite backup capture and publication authority.

A backup destination is an ordinary filesystem namespace, not a disposable
SQLite family.  Production backup must therefore obtain one transactionally
consistent image from the already-owned source connection, canonicalize and
seal it without a staging pathname, verify its logical anchors, and publish the
exact resident bytes through the typed atomic-file owner.  Foreign WAL, SHM,
journal, and publisher-temp names are evidence failures or unrelated entries;
they are never cleanup authority.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def slice_between(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    stop = text.find(end, start + len(begin)) if start >= 0 else -1
    return text[start:stop] if start >= 0 and stop > start else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    paths = {
        "cmake": root / "CMakeLists.txt",
        "ledger": root / "src/sqlite_replay_ledger.cpp",
        "seal_header": root / "src/persistence/sqlite_snapshot_seal.hpp",
        "seal_source": root / "src/persistence/sqlite_snapshot_seal.cpp",
        "live_header": root / "src/persistence/sqlite_live_backup.hpp",
        "live_source": root / "src/persistence/sqlite_live_backup.cpp",
        "publisher_header": root / "src/sync_atomic_file_publication.hpp",
        "test": root / "tests/sqlite_backup_namespace_authority_test.cpp",
        "seal_test": root / "tests/persistence/sqlite_snapshot_seal_tests.cpp",
        "live_test": root / "tests/persistence/sqlite_live_backup_tests.cpp",
        "live_audit": root / "tools/audit_sqlite_live_backup.py",
        "package_verifier": root / "tools/verify_release_package.py",
    }
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        result = {
            "format": "anonsync-sqlite-backup-publication-audit-v1",
            "passed": False,
            "checks": [],
            "violations": [f"missing required file: {name}" for name in missing],
        }
        rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 2

    text = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    backup = slice_between(
        text["ledger"],
        "bool SqliteWalReplayLedger::backup_snapshot(",
        "void SqliteWalReplayLedger::close()",
    )
    capture = slice_between(
        text["seal_source"],
        "SealedSqliteSnapshot SealedSqliteSnapshot::capture_database(",
        "SealedSqliteSnapshot::~SealedSqliteSnapshot()",
    )
    checks: list[Check] = []

    def require(check_id: str, condition: bool, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    require(
        "backup_function_was_located", bool(backup),
        "the production backup implementation must remain discoverable",
    )
    require(
        "live_capture_function_was_located", bool(capture),
        "the namespace-free live-database capture owner must remain discoverable",
    )
    preflight_guard = slice_between(
        backup,
        "SqlitePathFamilyGuard destination_preflight =",
        "// The source connection is the current-process ledger capability.",
    )
    publication_guard = slice_between(
        backup,
        "SqlitePathFamilyGuard destination_guard =",
        "snapshot.publish_exact_copy_atomically_or_throw(",
    )
    require(
        "destination_preflight_is_nonmutating_and_publication_guard_is_late",
        "snapshot_path" in preflight_guard
        and "false" in preflight_guard
        and "snapshot_path" in publication_guard
        and "true" in publication_guard
        and backup.find("SqlitePathFamilyGuard destination_guard =")
            > backup.find("verifier_stats.ledger_instance_id != ledger_instance_id_"),
        "an early sidecar check may not create directories; only verified source evidence may reacquire a mutating publication guard",
    )
    require(
        "backup_rejects_foreign_sidecars_before_effects",
        backup.find("verify_sidecars_absent_or_throw") >= 0
        and backup.find("verify_sidecars_absent_or_throw")
        < backup.find("SealedSqliteSnapshot::capture_database"),
        "WAL, SHM, or journal evidence must reject before capture or publication",
    )
    require(
        "backup_uses_one_live_seal_and_exact_atomic_publication",
        backup.count("SealedSqliteSnapshot::capture_database") == 1
        and backup.count("publish_exact_copy_atomically_or_throw") == 1
        and "verify_sealed_sqlite_ledger_snapshot_readonly" in backup,
        "one resident image must feed logical verification and exact-byte publication",
    )
    forbidden_backup = (
        "unlink_sqlite_family", "sqlite3_open", "sqlite_open_or_throw",
        "sqlite3_backup_init", "sqlite3_backup_step", "sqlite3_backup_finish",
        "std::filesystem::rename", "std::remove", "::unlink(",
        "canonicalize_backup_snapshot_for_deserialization_or_throw",
    )
    require(
        "backup_owns_no_writable_sqlite_staging_namespace",
        all(token not in backup for token in forbidden_backup),
        "backup must not open, pre-delete, canonicalize, rename, or clean a destination SQLite family",
    )
    require(
        "backup_binds_full_committed_ledger_anchors",
        all(token in backup for token in (
            "verifier_stats.loaded_entries != durable_line_count_",
            "verifier_stats.durable_line_count != durable_line_count_",
            "verifier_stats.durable_head_hash != durable_head_hash_",
            "verifier_stats.ledger_instance_id != ledger_instance_id_",
            "verifier_stats.effect_transition_line_count !=",
            "verifier_stats.effect_transition_head_hash !=",
            "verifier_stats.effect_outbox_reserved != effect_outbox_reserved_",
            "verifier_stats.effect_outbox_inflight != effect_outbox_inflight_",
            "verifier_stats.effect_outbox_terminal != effect_outbox_terminal_",
        )),
        "publication authority must bind durable decision, transition-chain, and outbox state rather than a row count alone",
    )
    require(
        "backup_excludes_session_local_transition_telemetry",
        "verifier_stats.effect_terminal_transitions" not in backup,
        "backup authorization must not compare durable transition rows with a session-local success counter that resets on reopen",
    )
    require(
        "backup_reasserts_sidecar_absence_after_publication",
        backup.count("verify_sidecars_absent_or_throw") >= 2
        and "published_and_directory_synced" in backup,
        "a postpublication namespace race must be reported as an effectful classified failure",
    )
    require(
        "backup_preserves_typed_atomic_failure_evidence",
        "catch (const SyncAtomicFilePublicationError& error)" in backup
        and "sync_atomic_file_publication_outcome_name" in backup
        and "sync_atomic_file_publication_residue_name" in backup,
        "the bool facade must retain the atomic owner's outcome and residue classification",
    )
    require(
        "family_deletion_authority_is_absent",
        text["ledger"].count("unlink_sqlite_family(") == 0
        and backup.count("unlink_sqlite_family(") == 0,
        "whole-family deletion authority must remain absent from ordinary load and backup",
    )

    require(
        "live_capture_requires_current_connection_shape",
        "sqlite3_db_mutex(source_database) == nullptr" in capture
        and "sqlite3_get_autocommit(source_database) == 0" in capture,
        "the source must be full-mutex protected and outside an active transaction",
    )
    require(
        "live_capture_destination_is_private_memory",
        '":memory:"' in capture
        and "SQLITE_OPEN_MEMORY" in capture
        and "SQLITE_OPEN_FULLMUTEX" in capture
        and "SQLITE_OPEN_PRIVATECACHE" in capture
        and "pinned_vfs_name_.c_str()" in capture,
        "the online-backup destination must have no filesystem pathname and use the pinned VFS",
    )
    source_preflight = (
        'source_database, policy, label + " source preflight geometry"'
    )
    require(
        "source_geometry_rejects_before_private_destination_open",
        source_preflight in capture
        and capture.find(source_preflight) < capture.find("sqlite3_open_v2"),
        "the source byte/page ceiling must fail before SQLite opens or allocates a private destination",
    )
    require(
        "live_capture_delegates_complete_online_backup_lifecycle",
        "copy_sqlite_live_snapshot_bounded_or_throw" in capture
        and "sqlite3_backup_init" not in capture
        and "sqlite3_backup_step" not in capture
        and "sqlite3_backup_finish" not in capture
        and "sqlite3_backup_init" in text["live_source"]
        and "sqlite3_backup_step" in text["live_source"]
        and "sqlite3_backup_finish" in text["live_source"],
        "a live image is authoritative only after one separately owned, complete backup protocol",
    )
    require(
        "live_backup_is_pinned_bounded_and_finite",
        "kSqliteLiveBackupPagesPerStep = 64U" in text["live_header"]
        and "sqlite3_backup_step(backup, -1)" not in text["live_source"]
        and "verify_pinned_source_or_throw" in text["live_source"]
        and "maximum_step_calls" in text["live_source"]
        and "observed_page_count != expected_page_count" in text["live_source"]
        and "observed_remaining >= previous_remaining" in text["live_source"],
        "the copy owner must pin one read image and bound every page effect and loop",
    )
    require(
        "live_capture_canonicalizes_without_disk_temp",
        '"PRAGMA temp_store=MEMORY;"' in capture
        and '"VACUUM;"' in capture
        and "finalize_resident_bytes_or_throw" in capture
        and "verify_deserializable_file_format_or_throw" in text["seal_source"],
        "the private image must become standalone 1/1 format and independently prove that header",
    )
    require(
        "live_capture_preflights_exact_geometry_before_serialization",
        "checked_serialized_geometry_bytes_or_throw" in capture
        and "SQLITE_SERIALIZE_NOCOPY" in capture
        and "reported_size" in capture
        and "serialized_size" in capture
        and "private serialization size does not match page geometry" in capture,
        "page geometry and SQLite's exact serialized extent must agree before resident authority is minted",
    )
    require(
        "serialized_allocation_is_adopted_without_extra_copy",
        "std::unique_ptr<unsigned char, SqliteBufferDeleter> serialized_bytes_" in text["seal_header"]
        and "out.serialized_bytes_.reset(serialized)" in capture
        and "sqlite3_free(bytes)" in text["seal_source"],
        "the seal must directly own SQLite's allocation with the matching deleter",
    )
    forbidden_capture = (
        "std::filesystem", "SqlitePathFamilyGuard", "open_readonly_file_or_throw",
        "publish_exact_copy", "std::remove", "::unlink(", "::rename(",
    )
    require(
        "live_capture_has_no_pathname_effects",
        all(token not in capture for token in forbidden_capture),
        "live capture must be a connection-to-memory operation with no namespace cleanup or publication",
    )

    require(
        "focused_namespace_authority_test_is_registered",
        "add_executable(anonsync_sqlite_backup_namespace_authority_test" in text["cmake"]
        and "add_test(NAME anonsync_sqlite_backup_namespace_authority_test" in text["cmake"]
        and "foreign-publisher-collision" in text["test"]
        and 'for (const std::string_view suffix : {"-wal", "-shm", "-journal"})' in text["test"],
        "CTest must preserve foreign publisher temps and every portable SQLite sidecar class",
    )
    require(
        "focused_test_proves_live_source_reuse_and_canonical_header",
        "source ledger stopped accepting rows after live capture" in text["test"]
        and "published backup is not canonical SQLite file format 1/1" in text["test"]
        and "sealed_entry_count(snapshot) == 2" in text["test"]
        and "backup accepted a substituted durable ledger identity" in text["test"]
        and "invalid source evidence created a destination directory or file" in text["test"],
        "the capture must leave the source usable and publish a verified standalone image",
    )
    require(
        "focused_test_proves_oversize_rejection_precedes_private_open",
        "oversized live capture opened a private destination before source geometry rejection"
            in text["seal_test"]
        and "oversized live capture changed the staging namespace before source geometry rejection"
            in text["seal_test"],
        "the focused observer must prove an over-budget source consumes no destination or namespace authority",
    )
    require(
        "focused_live_backup_proves_growth_and_failure_cutpoints",
        "concurrent writer did not grow the durable source beyond policy" in text["live_test"]
        and "resident destination followed a commit outside the pinned snapshot" in text["live_test"]
        and "aborted live backup retained a partial destination image" in text["live_test"]
        and "source database has an active implicit transaction" in text["live_test"]
        and "preflight-to-pin growth trace did not commit after early page-count observation"
            in text["seal_test"],
        "concurrent growth, lost pin, rollback, and hidden transaction authority require executable oracles",
    )
    require(
        "source_audit_is_registered",
        "anonsync_sqlite_backup_publication_source_audit" in text["cmake"],
        "backup publication architecture must remain a normal CTest obligation",
    )
    require(
        "release_verifier_requires_new_proofs",
        "tests/sqlite_backup_namespace_authority_test.cpp" in text["package_verifier"]
        and "tools/audit_sqlite_backup_publication.py" in text["package_verifier"]
        and "src/persistence/sqlite_live_backup.cpp" in text["package_verifier"]
        and "tests/persistence/sqlite_live_backup_tests.cpp" in text["package_verifier"]
        and "tools/audit_sqlite_live_backup.py" in text["package_verifier"],
        "a release archive cannot omit the executable proof or structural audit",
    )
    require(
        "binary_publisher_accepts_exact_bytes",
        "std::span<const unsigned char> payload" in text["publisher_header"],
        "SQLite serialization must remain binary and byte-exact through publication",
    )

    violations = [check.check_id for check in checks if not check.passed]
    result = {
        "format": "anonsync-sqlite-backup-publication-audit-v1",
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": {
            "backup_lines": len(backup.splitlines()),
            "live_capture_lines": len(capture.splitlines()),
            "ledger_unlink_family_occurrences": text["ledger"].count("unlink_sqlite_family("),
        },
        "violations": violations,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
