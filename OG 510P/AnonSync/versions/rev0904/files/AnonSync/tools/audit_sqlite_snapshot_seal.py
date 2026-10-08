#!/usr/bin/env python3
"""Fail-closed source audit for immutable, sidecar-free SQLite snapshot evidence.

A snapshot signature binds the bytes of one main database file.  SQLite's
ordinary read-only open may still merge a sibling WAL into the logical view,
and independently reopening an untrusted pathname creates a TOCTOU boundary.
This audit keeps manifest verification, logical verification, continuity
checking, and restore backup behind one process-local byte seal.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sqlite_path_security.hpp"),
    Path("src/sqlite_path_security.cpp"),
    Path("src/persistence/sqlite_snapshot_geometry.hpp"),
    Path("src/persistence/sqlite_snapshot_geometry.cpp"),
    Path("src/persistence/sqlite_live_backup.hpp"),
    Path("src/persistence/sqlite_live_backup.cpp"),
    Path("src/persistence/sqlite_snapshot_seal.hpp"),
    Path("src/persistence/sqlite_snapshot_seal.cpp"),
    Path("src/sqlite_replay_ledger.cpp"),
    Path("tests/sqlite_replay_ledger_selftests.cpp"),
    Path("tests/persistence/sqlite_snapshot_seal_tests.cpp"),
    Path("tests/persistence/sqlite_live_backup_tests.cpp"),
    Path("tests/sqlite_snapshot_sidecar_binding_test.cpp"),
    Path("tests/sqlite_ingress_sender_replay_integrity_test.cpp"),
    Path("tests/sqlite_backup_namespace_authority_test.cpp"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def require(checks: list[Check], condition: bool, check_id: str, detail: str) -> None:
    checks.append(Check(check_id, bool(condition), detail))


def function_body(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    end = text.find(end_marker, start + len(start_marker)) if start >= 0 else -1
    if start < 0 or end < 0 or end <= start:
        return ""
    return text[start:end]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="AnonSync source root",
    )
    parser.add_argument("--json", type=Path, help="write deterministic JSON report")
    args = parser.parse_args()
    root = args.root.resolve()

    missing = [item.as_posix() for item in REQUIRED if not (root / item).is_file()]
    if missing:
        report = {
            "format": "anonsync-sqlite-snapshot-seal-audit-v1",
            "passed": False,
            "violations": [f"missing required file: {item}" for item in missing],
        }
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 2

    texts = {
        item: (root / item).read_text(encoding="utf-8", errors="strict")
        for item in REQUIRED
    }
    cmake = texts[Path("CMakeLists.txt")]
    path_hpp = texts[Path("src/sqlite_path_security.hpp")]
    path_cpp = texts[Path("src/sqlite_path_security.cpp")]
    geometry_hpp = texts[Path("src/persistence/sqlite_snapshot_geometry.hpp")]
    geometry_cpp = texts[Path("src/persistence/sqlite_snapshot_geometry.cpp")]
    live_hpp = texts[Path("src/persistence/sqlite_live_backup.hpp")]
    live_cpp = texts[Path("src/persistence/sqlite_live_backup.cpp")]
    seal_hpp = texts[Path("src/persistence/sqlite_snapshot_seal.hpp")]
    seal_cpp = texts[Path("src/persistence/sqlite_snapshot_seal.cpp")]
    ledger = texts[Path("src/sqlite_replay_ledger.cpp")]
    ledger_selftests = texts[Path("tests/sqlite_replay_ledger_selftests.cpp")]
    focused = texts[Path("tests/persistence/sqlite_snapshot_seal_tests.cpp")]
    live_focused = texts[Path("tests/persistence/sqlite_live_backup_tests.cpp")]
    integrated = texts[Path("tests/sqlite_snapshot_sidecar_binding_test.cpp")]
    ingress_integrity = texts[Path("tests/sqlite_ingress_sender_replay_integrity_test.cpp")]
    backup_authority = texts[Path("tests/sqlite_backup_namespace_authority_test.cpp")]

    checks: list[Check] = []

    require(
        checks,
        "add_library(anonsync_sqlite_path_security STATIC" in cmake
        and "add_library(anonsync_sqlite_snapshot_seal STATIC" in cmake
        and "anonsync_sqlite_path_security" in cmake
        and "OpenSSL::Crypto" in cmake,
        "seal_and_path_owners_are_independent_libraries",
        "path identity and byte sealing must remain separately linkable production owners",
    )
    core_match = re.search(
        r"set\(ANONSYNC_CORE_SOURCES(?P<body>.*?)\)\s*foreach\(", cmake, re.S
    )
    require(
        checks,
        core_match is not None
        and "sqlite_path_security.cpp" not in core_match.group("body")
        and "sqlite_snapshot_seal.cpp" not in core_match.group("body"),
        "invariant_sources_are_not_reabsorbed_by_core",
        "focused security owners must not be compiled as private monolith sources",
    )
    require(
        checks,
        "anonsync_sqlite_snapshot_seal_test" in cmake
        and "focused persistence boundary must not depend on anonsync_core_lib" in cmake,
        "focused_test_has_no_core_dependency",
        "the adversarial seal proof must retain a configure-time no-core link fence",
    )
    require(
        checks,
        "anonsync_sqlite_snapshot_seal_source_audit" in cmake,
        "source_audit_is_registered",
        "the seal architecture must be enforced by CTest, not only described in notes",
    )

    for marker, check_id in (
        ("verify_sidecars_absent_or_throw", "path_owner_can_require_sidecar_absence"),
        ("open_readonly_file_or_throw", "path_owner_opens_bound_readonly_descriptor"),
        ("sync_posix_observe_relative_mount_noexcept", "path_owner_rejects_cross_mount_family_members"),
        ("O_NOFOLLOW", "path_owner_refuses_final_symlink"),
        ("openat(parent_fd_", "path_owner_opens_relative_to_retained_parent"),
        ("st_nlink != 1", "path_owner_refuses_hardlink_aliases"),
    ):
        require(checks, marker in path_hpp or marker in path_cpp, check_id,
                f"required path-identity marker: {marker}")

    require(
        checks,
        "class SealedSqliteSnapshot final" in seal_hpp
        and "SealedSqliteSnapshot(const SealedSqliteSnapshot&) = delete" in seal_hpp
        and "SealedSqliteSnapshot& operator=(const SealedSqliteSnapshot&) = delete" in seal_hpp
        and "std::unique_ptr<unsigned char, SqliteBufferDeleter> serialized_bytes_" in seal_hpp,
        "seal_is_move_only_capability",
        "a live process-resident byte capability must not be copyable",
    )
    require(
        checks,
        all(marker in seal_cpp for marker in ('"-wal"', '"-shm"', '"-journal"'))
        and seal_cpp.count("verify_sidecars_absent_or_throw") >= 3,
        "source_is_sidecar_free_through_capture",
        "WAL, SHM, and rollback-journal siblings must remain absent while source bytes are acquired",
    )
    require(
        checks,
        all(
            marker not in seal_hpp + seal_cpp
            for marker in (
                "mkdtemp",
                "staging_directory_",
                "staged_path_",
                "immutable_uri_",
                "::unlink(",
                "::rmdir(",
                "::rename(",
            )
        ),
        "seal_owns_no_cleanup_pathname",
        "capture and destruction must not create, rename, or delete filesystem staging names",
    )
    require(
        checks,
        "EVP_DigestUpdate" in seal_cpp
        and "SqliteAllocatedBytes bytes(" in seal_cpp
        and "sqlite3_malloc64(expected_bytes)" in seal_cpp
        and "::pread(" in seal_cpp
        and "source_stat_is_stable" in seal_cpp
        and "source snapshot grew beyond its captured byte count" in seal_cpp,
        "copy_and_digest_share_one_source_stream",
        "the digest must describe exactly the descriptor bytes copied into process memory",
    )
    require(
        checks,
        "out.finalize_resident_bytes_or_throw" in seal_cpp
        and "sha256_hex_ = sha256_bytes_or_throw(bytes" in seal_cpp
        and "out.sha256_hex_ != stream_sha256" in seal_cpp
        and "resident snapshot digest does not match captured source bytes" in seal_cpp,
        "resident_bytes_are_rehashed_before_promotion",
        "the process-owned image must independently reproduce the source-stream digest",
    )
    require(
        checks,
        "byte_count > policy.maximum_bytes" in geometry_cpp
        and "std::numeric_limits<std::size_t>::max()" in seal_cpp
        and "std::numeric_limits<sqlite3_int64>::max()" in seal_cpp
        and "const std::uint64_t remaining = expected_bytes - copied" in seal_cpp
        and "kMaximumUntrustedSqliteSnapshotBytes" in geometry_hpp,
        "copy_budget_arithmetic_is_overflow_safe",
        "hostile file sizes must fit policy, process, SQLite, and monotone copy arithmetic",
    )
    require(
        checks,
        "header[18] != 1U" in seal_cpp
        and "header[19] != 1U" in seal_cpp
        and seal_cpp.count("verify_deserializable_file_format_or_throw") >= 4
        and "rollback-journal file format versions 1/1" in seal_cpp,
        "wal_format_is_rejected_without_byte_rewrite",
        "a sidecar-free 2/2 WAL header cannot be promoted into deserialize authority",
    )
    require(
        checks,
        '":memory:"' in seal_cpp
        and "SQLITE_OPEN_READONLY" in seal_cpp
        and "SQLITE_OPEN_FULLMUTEX" in seal_cpp
        and "SQLITE_OPEN_PRIVATECACHE" in seal_cpp
        and "SQLITE_OPEN_MEMORY" in seal_cpp
        and "sqlite3_deserialize(" in seal_cpp
        and "SQLITE_DESERIALIZE_FREEONCLOSE | SQLITE_DESERIALIZE_READONLY" in seal_cpp
        and "sqlite3_db_filename(database, \"main\")" in seal_cpp,
        "sqlite_open_is_private_readonly_and_namespace_free",
        "SQLite must consume a private read-only in-memory image with no database pathname",
    )
    require(
        checks,
        "sqlite3_vfs_find(nullptr)" in seal_cpp
        and "pinned_vfs_name_" in seal_hpp
        and "verify_pinned_vfs_registration_or_throw" in seal_hpp
        and "sqlite3_vfs_find(pinned_vfs_name_.c_str())" in seal_cpp
        and "pinned_vfs_name_.c_str()" in seal_cpp,
        "sqlite_open_pins_exact_vfs_object",
        "capture-time VFS selection must survive default substitution and be observed after open",
    )
    require(
        checks,
        "sqlite3_malloc64(byte_count_)" in seal_cpp
        and "std::memcpy(copy, serialized_bytes_.get()," in seal_cpp
        and "static_cast<std::size_t>(byte_count_)" in seal_cpp
        and "sqlite3_free(copy)" in seal_cpp
        and "FREEONCLOSE transfers or releases copy" in seal_cpp
        and "deserialized handle depended on seal lifetime" in focused,
        "each_open_owns_an_independent_image",
        "a returned SQLite handle must not borrow bytes from the seal lifetime",
    )
    require(
        checks,
        "!serialized_bytes_ || byte_count_ == 0U" in seal_cpp
        and "current_geometry != geometry_" in seal_cpp
        and "sha256_bytes_or_throw(bytes" in seal_cpp
        and "serialized_bytes_.get(), static_cast<std::size_t>(byte_count_)" in seal_cpp
        and seal_cpp.count("verify_unchanged_or_throw(label)") >= 3,
        "resident_image_binds_every_sqlite_open",
        "size, geometry, digest, VFS registration, and process provenance must be rechecked",
    )
    require(
        checks,
        "serialized_bytes_.reset()" in seal_cpp
        and "snapshot destruction changed the staging namespace" in focused
        and "resident seal cleanup mutated /tmp staging state" in focused,
        "cleanup_is_memory_only_and_namespace_observed",
        "destruction must free resident authority without mutating the former staging namespace",
    )

    live_capture = function_body(
        seal_cpp,
        "SealedSqliteSnapshot SealedSqliteSnapshot::capture_database(",
        "SealedSqliteSnapshot::~SealedSqliteSnapshot()",
    )
    require(
        checks,
        bool(live_capture)
        and "sqlite3_db_mutex(source_database) == nullptr" in live_capture
        and "sqlite3_get_autocommit(source_database) == 0" in live_capture,
        "live_capture_requires_fullmutex_autocommit_source",
        "connection authority must not be borrowed from a no-mutex handle or an active transaction",
    )
    require(
        checks,
        '"PRAGMA trusted_schema;"' in live_capture
        and '"PRAGMA temp_store;"' in live_capture
        and '"VACUUM;"' in live_capture
        and "copy_sqlite_live_snapshot_bounded_or_throw" in live_capture
        and "sqlite3_backup_init" not in live_capture
        and "sqlite3_backup_step" not in live_capture
        and "sqlite3_backup_finish" not in live_capture
        and "sqlite3_backup_init" in live_cpp
        and "sqlite3_backup_finish" in live_cpp,
        "live_capture_builds_one_hardened_private_image",
        "one separately owned bounded backup, hardening readback, and in-memory canonicalization must precede serialization",
    )
    require(
        checks,
        "kSqliteLiveBackupPagesPerStep = 64U" in live_hpp
        and "sqlite3_backup_step" in live_cpp
        and "sqlite3_backup_step(backup, -1)" not in live_cpp
        and "maximum_step_calls" in live_cpp
        and "observed_page_count != expected_page_count" in live_cpp
        and "observed_remaining >= previous_remaining" in live_cpp,
        "live_capture_copy_effects_are_bounded_and_observable",
        "the seal must not delegate to an unbounded or restart-tolerant backup loop",
    )
    source_preflight = (
        'source_database, policy, label + " source preflight geometry"'
    )
    require(
        checks,
        source_preflight in live_capture
        and live_capture.find(source_preflight) < live_capture.find("sqlite3_open_v2"),
        "live_capture_rejects_source_geometry_before_private_open",
        "over-budget source geometry must fail before opening or allocating the in-memory destination",
    )
    require(
        checks,
        "SQLITE_SERIALIZE_NOCOPY" in live_capture
        and "checked_serialized_geometry_bytes_or_throw" in live_capture
        and "out.serialized_bytes_.reset(serialized)" in live_capture
        and "sqlite3_free(bytes)" in seal_cpp,
        "live_capture_preflights_and_adopts_exact_sqlite_allocation",
        "geometry must bound allocation and SQLite's exact buffer must move directly into the seal",
    )
    for marker, check_id in (
        ("live-database seal retained a filesystem source pathname", "focused_live_capture_has_no_source_path"),
        ("live-database capture opened a non-memory or named VFS file", "focused_live_capture_has_no_disk_open"),
        ("resident live capture followed later source mutations", "focused_live_capture_is_point_in_time"),
        ("oversized live capture opened a private destination before source geometry rejection", "focused_live_capture_rejects_oversize_before_private_open"),
        ("preflight-to-pin growth trace did not commit after early page-count observation", "focused_live_capture_rechecks_geometry_after_pin"),
        ("active-transaction live capture proof", "focused_live_capture_rejects_active_transaction"),
        ("no-mutex live capture proof", "focused_live_capture_rejects_no_mutex"),
    ):
        require(checks, marker in focused, check_id, f"focused live-capture marker: {marker}")
    for marker, check_id in (
        ("bounded backup did not expose multiple fixed-size steps", "focused_live_backup_uses_fixed_steps"),
        ("concurrent writer did not grow the durable source beyond policy", "focused_live_backup_pins_growth_boundary"),
        ("aborted live backup retained a partial destination image", "focused_live_backup_rolls_back_partial_destination"),
        ("source database has an active implicit transaction", "focused_live_backup_rejects_hidden_transaction"),
    ):
        require(checks, marker in live_focused, check_id, f"focused bounded-backup marker: {marker}")

    profile = function_body(
        ledger,
        "void apply_untrusted_snapshot_readonly_profile(",
        "void verify_sqlite_replay_ledger_schema_or_throw",
    )
    require(
        checks,
        all(
            marker in profile
            for marker in (
                "SQLITE_DBCONFIG_DEFENSIVE",
                "SQLITE_DBCONFIG_TRUSTED_SCHEMA",
                "SQLITE_DBCONFIG_ENABLE_TRIGGER",
                "SQLITE_DBCONFIG_ENABLE_VIEW",
                "SQLITE_LIMIT_LENGTH",
                "SQLITE_LIMIT_VDBE_OP",
                "PRAGMA cell_size_check=ON",
                "PRAGMA mmap_size=0",
                "SQLite untrusted snapshot hardening profile mismatch",
            )
        ),
        "untrusted_sqlite_profile_matches_upstream_guidance",
        "snapshot parsing must disable unused schema execution, mmap, and oversized inputs",
    )
    require(
        checks,
        "sqlite_query_optional_int64(" in ledger
        and "const bool mmap_size_reported" in profile
        and "sqlite3_db_filename(db, \"main\")" in profile
        and "database_filename[0] == '\\0'" in profile
        and "(!mmap_size_reported && !namespace_free_database)" in profile,
        "missing_mmap_row_requires_namespace_free_handle",
        "SQLite's rowless mmap pragma is safe only for a proven namespace-free deserialized database",
    )
    require(
        checks,
        "SealedSqliteSnapshot::capture_database" in ledger
        and '"PRAGMA temp_store=MEMORY;"' in seal_cpp
        and '"VACUUM;"' in seal_cpp
        and "SQLITE_SERIALIZE_NOCOPY" in seal_cpp
        and "private destination did not retain temp_store=MEMORY" in seal_cpp
        and "published backup is not canonical SQLite file format 1/1" in backup_authority,
        "backup_producer_emits_deserializable_rollback_image",
        "the producer must canonicalize one private live-copy image to 1/1 before exact-byte publication",
    )
    require(
        checks,
        "restore manifest binding expected snapshot read-only verifier" in ledger_selftests
        and "ReplayLedgerStats st = verify_sqlite_ledger_snapshot_readonly_for_selftest(" in ledger_selftests
        and "mutating observer" in ingress_integrity
        and "ordinary_reload_copy" in ingress_integrity
        and "reload_rejection(ordinary_reload_copy)" in ingress_integrity
        and "reload_rejection(clean_snapshot)" not in ingress_integrity
        and ingress_integrity.find("const std::string restore_orphan")
            < ingress_integrity.find("require_rejected(orphan"),
        "snapshot_summaries_avoid_mutable_backend_observation",
        "snapshot evidence must not be summarized through a backend that enables WAL before verification",
    )

    readonly_wrapper = function_body(
        ledger,
        "ReplayLedgerStats verify_sqlite_ledger_snapshot_readonly(",
        "struct PendingEffectReportRow",
    )
    manifest_verifier = function_body(
        ledger,
        "SqliteSnapshotManifestVerification verify_sqlite_snapshot_manifest_with_trust_profile_text(",
        "SqliteSnapshotManifestVerification verify_sqlite_snapshot_manifest(",
    )
    restore = function_body(
        ledger,
        "void restore_sqlite_snapshot_into_ledger_internal(",
        "void restore_sqlite_snapshot_into_ledger(",
    )
    prefix_reader = function_body(
        ledger,
        "std::string sqlite_entry_hash_at_sequence(",
        "std::string sqlite_entry_hash_at_sequence_from_open_db(",
    )
    # The following declaration follows the prefix helper in this revision; use
    # a bounded fallback when the historical marker is absent.
    if not prefix_reader:
        start = ledger.find("std::string sqlite_entry_hash_at_sequence(")
        prefix_reader = ledger[start : start + 2600] if start >= 0 else ""

    require(
        checks,
        "SealedSqliteSnapshot::capture" in readonly_wrapper
        and "verify_sealed_sqlite_ledger_snapshot_readonly" in readonly_wrapper,
        "direct_readonly_verifier_seals_before_logical_checks",
        "the public path-based verifier must immediately convert pathname evidence into a seal",
    )
    require(
        checks,
        "SealedSqliteSnapshot::capture" in manifest_verifier
        and "snapshot.sha256_hex()" in manifest_verifier
        and "verify_sealed_sqlite_ledger_snapshot_readonly" in manifest_verifier
        and "read_file(snapshot_path)" not in manifest_verifier,
        "manifest_digest_and_rows_share_one_seal",
        "manifest byte comparison and logical verification must consume identical captured bytes",
    )
    require(
        checks,
        restore.count("SealedSqliteSnapshot::capture") == 1
        and "sealed_snapshot.sha256_hex()" in restore
        and "verify_sealed_sqlite_ledger_snapshot_readonly" in restore
        and "sqlite_entry_hash_at_sequence(\n                            sealed_snapshot" in restore
        and "sealed_snapshot.publish_exact_copy_atomically_with_observer_or_throw" in restore
        and "read_file(snapshot_path)" not in restore
        and "sqlite_open_or_throw(snapshot_path" not in restore,
        "restore_reuses_one_seal_for_all_source_authority",
        "digest, full verification, prefix proof, and exact-byte publication must never reopen the source path",
    )
    require(
        checks,
        "persistence::SealedSqliteSnapshot& snapshot" in prefix_reader
        and "snapshot.open_database_owner_or_throw" in prefix_reader
        and "SyncSqliteDbHandleSlot owner" in prefix_reader
        and "owner.reset()" in prefix_reader,
        "prefix_continuity_consumes_existing_seal",
        "the append-continuity proof must not acquire a fresh pathname view",
    )
    require(
        checks,
        "sha256_hex(read_file(snapshot_path))" not in ledger,
        "legacy_main_file_digest_reopen_is_absent",
        "production must not hash the untrusted snapshot pathname independently",
    )

    for marker, check_id in (
        ("main_digest_after == main_digest_before", "focused_proves_main_digest_stays_constant"),
        ('integer("SELECT count(*) FROM evidence") == 2', "focused_proves_readonly_wal_merge"),
        ("snapshot sidecar -wal", "focused_rejects_wal"),
        ("snapshot with ? hash# percent%.sqlite", "focused_exercises_special_path_bytes"),
        ("source replacement fixture", "focused_proves_path_independence"),
        ("snapshot capture minted a staging pathname", "focused_proves_namespace_free_capture"),
        ("deserialized handle depended on seal lifetime", "focused_proves_independent_open_lifetime"),
        ("clean WAL fixture did not retain file-format versions 2/2", "focused_builds_quiescent_wal_header"),
        ("rollback-journal file format versions 1/1", "focused_rejects_quiescent_wal_format"),
        ("resident seal created a filesystem staging artifact", "focused_proves_memory_only_residency"),
        ("replacement process-default VFS", "focused_proves_default_vfs_substitution_is_ignored"),
        ("missing pinned-VFS registration", "focused_rejects_vfs_unregistration"),
    ):
        require(checks, marker in focused, check_id, f"focused adversarial marker: {marker}")
    require(
        checks,
        "attacker-controlled unsigned SQLite sidecar" in ledger_selftests
        and 'for (const char* suffix : {"-wal", "-shm", "-journal"})' in ledger_selftests,
        "integrated_verifier_rejects_all_portable_sidecars",
        "the production read-only verifier selftest must exercise the seal boundary",
    )
    require(
        checks,
        "anonsync_sqlite_snapshot_sidecar_binding_test" in cmake
        and "main_digest_before == main_digest_after" in integrated
        and "ordinary read-only SQLite did not merge unsigned WAL state" in integrated
        and "restore accepted unsigned WAL state" in integrated
        and "snapshot sidecar -wal" in integrated
        and "!fs::exists(destination)" in integrated,
        "integrated_restore_exploit_is_permanently_reproduced",
        "the production restore test must prove unchanged main bytes, merged WAL state, rejection, and no publication",
    )

    report = {
        "format": "anonsync-sqlite-snapshot-seal-audit-v1",
        "passed": all(item.passed for item in checks),
        "checks": [asdict(item) for item in checks],
        "metrics": {
            "check_count": len(checks),
            "seal_boundary_lines": len(seal_cpp.splitlines()),
            "focused_test_lines": len(focused.splitlines()),
            "integrated_test_lines": len(integrated.splitlines()),
            "production_capture_sites": ledger.count("SealedSqliteSnapshot::capture"),
            "production_live_capture_sites": ledger.count("SealedSqliteSnapshot::capture_database"),
            "production_sealed_open_sites": ledger.count(".open_database_or_throw("),
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
