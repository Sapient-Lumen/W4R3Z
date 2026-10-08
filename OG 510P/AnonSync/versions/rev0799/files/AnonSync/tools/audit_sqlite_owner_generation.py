#!/usr/bin/env python3
"""Audit AnonSync's SQLite owner-generation and mutex-mode boundary.

The audit is deliberately lexical and deterministic so it can run in the
minimal release container. It separates release-blocking capability invariants
from enumerated raw-pointer migration debt; it does not substitute for the
compiler, runtime tests, sanitizers, or SQLite's own contracts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def line_sites(path: Path, pattern: re.Pattern[str]) -> list[dict[str, object]]:
    sites: list[dict[str, object]] = []
    for number, line in enumerate(read(path).splitlines(), 1):
        if pattern.search(line):
            sites.append(
                {
                    "path": path.relative_to(ROOT).as_posix(),
                    "line": number,
                    "text": line.strip(),
                }
            )
    return sites


def source_files() -> Iterable[Path]:
    yield from sorted(SRC.rglob("*.cpp"))
    yield from sorted(SRC.rglob("*.hpp"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def contains_all(text: str, snippets: Iterable[str]) -> bool:
    return all(snippet in text for snippet in snippets)


def slice_between(text: str, start: str, end: str) -> str:
    start_offset = text.find(start)
    if start_offset < 0:
        return ""
    end_offset = text.find(end, start_offset + len(start))
    if end_offset < 0:
        return ""
    return text[start_offset:end_offset]


def connection_struct_bodies(lifecycle: str) -> list[str]:
    pattern = re.compile(
        r"struct PeerTransportIngress(?:Write|Read)Connection\s*\{"
        r"(?P<body>.*?)\n\};",
        re.DOTALL,
    )
    return [match.group("body") for match in pattern.finditer(lifecycle)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    handle_header_path = SRC / "sync_sqlite_handle_slot.hpp"
    handle_cpp_path = SRC / "sync_sqlite_handle_slot.cpp"
    support_header_path = SRC / "sync_sqlite_support.hpp"
    support_cpp_path = SRC / "sync_sqlite_support.cpp"
    transaction_path = SRC / "sync_sqlite_transaction.cpp"
    lifecycle_path = SRC / "sync_peer_ingress_lifecycle.cpp"
    domain_path = SRC / "sync_domain.cpp"
    peer_ingestion_path = SRC / "sync_peer_ingestion.cpp"
    test_path = ROOT / "tests/sqlite_owner_generation_borrow_test.cpp"
    cmake_path = ROOT / "CMakeLists.txt"

    handle_header = read(handle_header_path)
    handle_cpp = read(handle_cpp_path)
    support_header = read(support_header_path)
    support_cpp = read(support_cpp_path)
    transaction = read(transaction_path)
    lifecycle = read(lifecycle_path)
    domain = read(domain_path)
    peer_ingestion = read(peer_ingestion_path)
    test = read(test_path)
    cmake = read(cmake_path)

    direct_managed_output_sites: list[dict[str, object]] = []
    raw_prepare_sites: list[dict[str, object]] = []
    close_v2_sites: list[dict[str, object]] = []
    raw_transaction_sites: list[dict[str, object]] = []
    generic_borrow_sites: list[dict[str, object]] = []
    sqlite_open_sites: list[dict[str, object]] = []
    raw_transaction_pattern = re.compile(
        r'"(?:BEGIN(?:\s+(?:DEFERRED|IMMEDIATE|EXCLUSIVE))?|COMMIT|ROLLBACK|'
        r'SAVEPOINT|RELEASE\s+SAVEPOINT|ROLLBACK\s+TO)\b',
        re.IGNORECASE,
    )
    transaction_boundary_implementation_files = {
        transaction_path,
        SRC / "sync_sqlite_connection_authority.cpp",
        SRC / "reporting_selftests.cpp",
    }
    for path in source_files():
        generic_borrow_sites.extend(line_sites(path, re.compile(r"\.borrow\(\)")))
        if path.suffix != ".cpp":
            continue
        sqlite_open_sites.extend(
            line_sites(path, re.compile(r"\bsqlite3_open_v2\s*\("))
        )
        if path != support_cpp_path:
            direct_managed_output_sites.extend(
                line_sites(
                    path,
                    re.compile(
                        r"\.stmt\.(?:out|reset)\s*\(|"
                        r"std::move\([^\n]*\.stmt\)"
                    ),
                )
            )
        raw_prepare_sites.extend(
            line_sites(path, re.compile(r"\bsqlite3_prepare(?:_v2|_v3)?\s*\("))
        )
        close_v2_sites.extend(
            line_sites(path, re.compile(r"\bsqlite3_close_v2\s*\("))
        )
        if path not in transaction_boundary_implementation_files:
            raw_transaction_sites.extend(line_sites(path, raw_transaction_pattern))

    peer_ingestion_raw_transaction_sites = line_sites(
        peer_ingestion_path, raw_transaction_pattern
    )
    raw_pointer_compatibility_declarations = line_sites(
        support_header_path,
        re.compile(
            r"(?:sqlite_exec_or_throw|sqlite_prepare_or_throw|"
            r"SyncSqliteTransaction)\(sqlite3\*"
        ),
    )

    owner_position = support_header.find(
        "SyncSqliteSerializedDbBorrow owner_borrow_;"
    )
    statement_position = support_header.find(
        "SyncSqliteStmtHandleSlot statement_owner_;"
    )
    view_position = support_header.find("HandleView stmt;")
    private_position = support_header.rfind("private:", 0, owner_position + 1)

    borrow_get = slice_between(
        handle_header,
        "[[nodiscard]] Handle* get() const noexcept {",
        "operator Handle*() const noexcept",
    )
    transferable = slice_between(
        handle_header,
        "void require_transferable_noexcept() const noexcept {",
        "void transfer_from_noexcept",
    )
    connection_structs = connection_struct_bodies(lifecycle)

    typed_support_mint_count = support_cpp.count(
        "borrow_sync_sqlite_serialized_db_or_throw("
    )
    typed_transaction_mint_count = transaction.count(
        "borrow_sync_sqlite_serialized_db_or_throw("
    )

    checks = {
        "strict_connection_close": (
            "sqlite3_get_autocommit(handle) == 0" in handle_cpp
            and "sqlite3_close(handle)" in handle_cpp
            and "sqlite3_close_v2(handle)" not in handle_cpp
            and "fail_stop_on_sync_sqlite_capability_violation_noexcept"
            in handle_cpp
        ),
        "process_aware_lifecycle_lock": contains_all(
            handle_header,
            (
                "std::atomic<SyncSqliteProcessId>::is_always_lock_free",
                "const SyncSqliteProcessId state_process_id",
                "state_->state_process_id != process_id_",
                "std::atomic<SyncSqliteProcessId> lifecycle_lock_owner",
                "ProcessBoundHandleStateGuard",
                "expected != process_id_",
            ),
        ),
        "lifecycle_lock_cannot_spuriously_fail_stop": (
            "lifecycle_lock_owner.compare_exchange_strong(" in handle_header
            and "lifecycle_lock_owner.compare_exchange_weak(" not in handle_header
        ),
        "exact_generation_borrow_count_and_evidence": contains_all(
            handle_header,
            (
                "std::uint64_t generation",
                "std::size_t active_borrows",
                "Evidence evidence{};",
                "state_->generation != generation_",
                "state_->evidence != evidence_",
                "state_->active_borrows != 0",
            ),
        ),
        "output_reservation_is_process_bound": contains_all(
            handle_header,
            (
                "SyncSqliteProcessId output_process_id",
                "state_->output_process_id != process_id",
            ),
        ),
        "connection_mutex_mode_is_explicit_generation_evidence": contains_all(
            handle_header,
            (
                "enum class SyncSqliteConnectionMutexMode",
                "Unknown = 0",
                "Unserialized = 1",
                "Serialized = 2",
                "SyncSqliteConnectionMutexMode mutex_mode",
                "sqlite3_mutex* mutex_identity",
            ),
        ),
        "mutex_mode_is_observed_not_inferred_from_open_flags": contains_all(
            handle_cpp,
            (
                "sqlite3_db_mutex(handle)",
                "SyncSqliteConnectionMutexMode::Serialized",
                "SyncSqliteConnectionMutexMode::Unserialized",
            ),
        ),
        "mutex_evidence_is_capture_once_and_use_checks_are_sqlite_free": (
            handle_cpp.count("sqlite3_db_mutex(handle)") == 1
            and "capture_evidence(Handle* handle)" in handle_cpp
            and "Re-reading sqlite3_db_mutex()" in handle_cpp
            and "validates only the frozen" in handle_cpp
        ),
        "foreign_process_is_rejected_before_generation_state_access": (
            borrow_get
            and transferable
            and borrow_get.find("require_current_noexcept();")
            < borrow_get.find("Policy::evidence_is_valid(handle_, evidence_)")
            and transferable.find("require_current_noexcept();")
            < transferable.find(
                "Policy::evidence_is_valid(handle_, evidence_)"
            )
        ),
        "serialized_capability_has_one_checked_mint": contains_all(
            handle_header,
            (
                "class SyncSqliteSerializedDbBorrow final",
                "SyncSqliteSerializedDbBorrow(const SyncSqliteSerializedDbBorrow&) = delete",
                "explicit SyncSqliteSerializedDbBorrow(\n        SyncSqliteDbHandleBorrow borrow)",
                "borrow_sync_sqlite_serialized_db_or_throw(",
                "borrow.connection_mutex_mode() !=",
                "SyncSqliteConnectionMutexMode::Serialized",
                "requires a serialized/FULLMUTEX SQLite connection",
            ),
        ) and "SyncSqliteSerializedDbBorrow(sqlite3*" not in handle_header,
        "serialized_capability_cannot_self_upgrade_from_raw_or_generic": contains_all(
            test,
            (
                "!std::is_constructible_v<\n                  anonsync::SyncSqliteSerializedDbBorrow, sqlite3*>",
                "anonsync::SyncSqliteDbHandleBorrow>",
                "a generic owner borrow must not self-upgrade",
            ),
        ),
        "statement_pin_is_private_and_destroyed_after_statement": (
            private_position >= 0
            and owner_position > private_position
            and statement_position > owner_position
            and view_position > statement_position
        ),
        "statement_view_cannot_launder_owner_slot": contains_all(
            support_header + support_cpp,
            (
                "class HandleView final",
                "HandleView(const HandleView&) = delete",
                "HandleView(HandleView&&) = delete",
                "SyncSqliteStmtHandleSlot statement_owner_;",
                "HandleView stmt;",
                "statement_owner_.out()",
            ),
        ) and "SyncSqliteStmtHandleSlot stmt;" not in support_header,
        "typed_prepare_retains_serialized_exact_owner": contains_all(
            support_cpp,
            (
                "SyncSqliteSerializedDbBorrow owner =",
                "borrow_sync_sqlite_serialized_db_or_throw(",
                "SyncSqliteStmt out(std::move(owner));",
                "out.prepare_or_throw(raw, sql, label);",
            ),
        ),
        "all_typed_support_helpers_mint_serialized_capability": (
            typed_support_mint_count == 5
            and "SyncSqliteDbHandleBorrow owner = db.borrow();" not in support_cpp
        ),
        "typed_transaction_retains_serialized_exact_owner": (
            typed_transaction_mint_count == 1
            and contains_all(
                support_header + transaction,
                (
                    "SyncSqliteSerializedDbBorrow owner_borrow_;",
                    "typed transaction owner",
                    "owner_borrow_.reset();",
                ),
            )
        ),
        "typed_statement_projects_owner_mutex_mode": contains_all(
            support_header + support_cpp,
            (
                "owner_connection_mutex_mode()",
                "return owner_borrow_.connection_mutex_mode();",
            ),
        ),
        "peer_ingress_connection_has_one_owner_truth_and_mode_proof": (
            len(connection_structs) == 2
            and all("sqlite3*" not in body for body in connection_structs)
            and all("SyncSqliteDb owner;" in body for body in connection_structs)
            and all(
                "SyncSqliteSerializedDbBorrow serialized;" in body
                and body.find("SyncSqliteDb owner;")
                < body.find("SyncSqliteSerializedDbBorrow serialized;")
                for body in connection_structs
            )
            and all(
                "PeerTransportIngress" in body
                and "operator=(" in body
                and ") = delete;" in body
                for body in connection_structs
            )
            and "connection.db = connection.owner.db" not in lifecycle
            and lifecycle.count(
                "connection.serialized = borrow_sync_sqlite_serialized_db_or_throw("
            ) == 2
            and lifecycle.count(
                "sqlite3* const db = connection.serialized.get();"
            ) == 2
        ),
        "peer_ingress_write_transactions_require_owner_slot": contains_all(
            lifecycle,
            (
                "begin_peer_transport_write_transaction_or_throw(\n    SyncSqliteDbHandleSlot& db,",
                "std::make_unique<SyncSqliteTransaction>(\n            db,",
            ),
        ),
        "peer_ingress_retention_branches_keep_capability_not_raw_address": (
            "const SyncSqliteSerializedDbBorrow* sqlite_authority = nullptr;"
            in lifecycle
            and "sqlite_authority = std::addressof(readonly_db->serialized);"
            in lifecycle
            and "sqlite_authority = std::addressof(write_db->serialized);"
            in lifecycle
            and "sqlite_authority->get()" in lifecycle
            and "sqlite3* sqlite_db = nullptr;" not in lifecycle
        ),
        "peer_ingestion_sidecar_transactions_are_typed": (
            peer_ingestion.count("SyncSqliteTransaction transaction(") >= 2
            and not peer_ingestion_raw_transaction_sites
            and "bool transaction_open" not in peer_ingestion
            and "peer_ingestion_exec_or_throw(sqlite3*" not in peer_ingestion
            and "ensure_peer_sidecar_review_events_schema_or_throw(\n    sqlite3*"
            not in peer_ingestion
            and "ensure_peer_sidecar_review_events_schema_or_throw(SyncSqliteDbHandleSlot&"
            in peer_ingestion
        ),
        "typed_helper_overloads_present": contains_all(
            support_header,
            (
                "sqlite_exec_or_throw(SyncSqliteDbHandleSlot& db",
                "sqlite_count_for_session_or_throw(\n    SyncSqliteDbHandleSlot& db",
                "sqlite_table_exists_or_throw(SyncSqliteDbHandleSlot& db",
                "sqlite_table_column_exists_or_throw(\n    SyncSqliteDbHandleSlot& db",
            ),
        ),
        "no_direct_managed_statement_output_bypass": (
            not direct_managed_output_sites
        ),
        "migrated_domain_and_ingress_paths_have_no_raw_prepare": (
            "sqlite3_prepare" not in domain
            and "sqlite3_prepare" not in peer_ingestion
        ),
        "nomutex_paths_reject_before_sql_and_release_pin": contains_all(
            test,
            (
                "SQLITE_OPEN_NOMUTEX",
                "typed_owner_paths_reject_unserialized_generation_before_sql",
                "observation.callbacks == 0",
                "owner.db.active_borrows() == 0",
                "serialized/FULLMUTEX",
            ),
        ),
        "serialized_capability_is_process_and_thread_exercised": contains_all(
            test,
            (
                "serialized_borrow_can_cross_threads_without_losing_generation",
                "serialized_capabilities_coordinate_concurrent_sqlite_use",
                "unserialized_borrow_evidence_is_serialized_under_contention",
                "inherited_serialized_borrow_fails_before_touching_sqlite",
                "inherited_serialized_borrow_cannot_move_or_destruct",
                "kSyncSqliteCapabilityViolationExitCode",
            ),
        ),
        "focused_test_registered": contains_all(
            cmake,
            (
                "anonsync_sqlite_owner_generation_borrow_test",
                "tests/sqlite_owner_generation_borrow_test.cpp",
            ),
        ),
    }

    findings = {
        "direct_managed_statement_output_sites": direct_managed_output_sites,
        "raw_sqlite_prepare_sites": raw_prepare_sites,
        "legacy_sqlite_close_v2_sites": close_v2_sites,
        "legacy_raw_transaction_control_sites": raw_transaction_sites,
        "peer_ingestion_raw_transaction_control_sites": (
            peer_ingestion_raw_transaction_sites
        ),
        "generic_owner_borrow_sites": generic_borrow_sites,
        "raw_pointer_compatibility_declarations": (
            raw_pointer_compatibility_declarations
        ),
        "sqlite_open_v2_sites": sqlite_open_sites,
        "peer_ingress_cached_connection_pointer_fields": [
            index
            for index, body in enumerate(connection_structs)
            if "sqlite3*" in body
        ],
    }

    required_passed = all(checks.values())
    scanned_paths = (
        cmake_path,
        handle_header_path,
        handle_cpp_path,
        support_header_path,
        support_cpp_path,
        transaction_path,
        lifecycle_path,
        domain_path,
        peer_ingestion_path,
        test_path,
    )
    result = {
        "format": "anonsync-sqlite-owner-generation-audit-v4",
        "required_passed": required_passed,
        "required_check_count": len(checks),
        "required_checks": checks,
        "findings": findings,
        "migration_debt": {
            "legacy_close_v2_count": len(close_v2_sites),
            "raw_prepare_site_count": len(raw_prepare_sites),
            "raw_transaction_control_site_count": len(raw_transaction_sites),
            "generic_owner_borrow_site_count": len(generic_borrow_sites),
            "raw_pointer_compatibility_declaration_count": len(
                raw_pointer_compatibility_declarations
            ),
            "sqlite_open_v2_site_count": len(sqlite_open_sites),
            "note": (
                "Typed owner-slot SQL now requires exact-generation serialized "
                "authority. Generic borrows, raw sqlite3* compatibility entry points, "
                "and legacy raw transaction/prepare/close sites remain explicit staged "
                "migration debt; the inventories do not claim those paths are typed."
            ),
        },
        "scanned_sha256": {
            path.relative_to(ROOT).as_posix(): sha256(path)
            for path in scanned_paths
        },
    }

    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        output = args.output
        if not output.is_absolute():
            output = ROOT / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    sys.stdout.write(encoded)
    return 0 if required_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
