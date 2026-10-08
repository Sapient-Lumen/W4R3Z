#!/usr/bin/env python3
"""Fail-closed audit for the SQLite replay-ledger schema authority boundary.

A database can expose the expected rows and column names while omitting the
constraints and indexes that future writes rely on. This audit keeps one exact,
versioned DDL owner for both creation and attestation, and prevents startup from
repairing an existing database before its schema has been verified.
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
    Path("src/persistence/sqlite_replay_ledger_schema_contract.hpp"),
    Path("src/persistence/sqlite_replay_ledger_schema_contract.cpp"),
    Path("src/sqlite_replay_ledger.cpp"),
    Path("tests/persistence/sqlite_replay_ledger_schema_contract_tests.cpp"),
    Path("tests/sqlite_replay_ledger_schema_integrity_test.cpp"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def require(checks: list[Check], condition: bool, check_id: str, detail: str) -> None:
    checks.append(Check(check_id, bool(condition), detail))


def function_body(text: str, signature: str, next_signature: str) -> str:
    start = text.find(signature)
    end = text.find(next_signature, start + len(signature))
    if start < 0 or end < 0:
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

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    if missing:
        report = {
            "format": "anonsync-sqlite-replay-ledger-schema-contract-audit-v1",
            "passed": False,
            "violations": [f"missing required file: {path}" for path in missing],
        }
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 2

    texts = {
        path: (root / path).read_text(encoding="utf-8", errors="strict")
        for path in REQUIRED
    }
    cmake = texts[Path("CMakeLists.txt")]
    header = texts[Path("src/persistence/sqlite_replay_ledger_schema_contract.hpp")]
    owner = texts[Path("src/persistence/sqlite_replay_ledger_schema_contract.cpp")]
    ledger = texts[Path("src/sqlite_replay_ledger.cpp")]
    focused = texts[Path("tests/persistence/sqlite_replay_ledger_schema_contract_tests.cpp")]
    integrated = texts[Path("tests/sqlite_replay_ledger_schema_integrity_test.cpp")]

    checks: list[Check] = []
    require(
        checks,
        "add_library(anonsync_sqlite_replay_ledger_schema_contract STATIC" in cmake
        and "${ANONSYNC_SQLITE_REPLAY_LEDGER_SCHEMA_CONTRACT_SOURCE}" in cmake,
        "schema_contract_is_independent_library",
        "the exact DDL owner must remain separately linkable",
    )
    core_match = re.search(
        r"set\(ANONSYNC_CORE_SOURCES(?P<body>.*?)\)\s*foreach\(", cmake, re.S
    )
    require(
        checks,
        core_match is not None
        and "sqlite_replay_ledger_schema_contract.cpp" not in core_match.group("body"),
        "schema_contract_is_not_reabsorbed_by_core_sources",
        "the owner source must not be compiled into the monolithic core archive",
    )
    require(
        checks,
        "anonsync_sqlite_replay_ledger_schema_contract_test" in cmake
        and "focused persistence boundary must not depend on anonsync_core_lib" in cmake,
        "focused_dependency_fence_is_configured",
        "CMake must retain a no-core dependency guard for the focused proof",
    )
    require(
        checks,
        '#include "sqlite_replay_ledger_schema_contract.hpp"' in ledger,
        "ledger_includes_single_schema_owner",
        "creation and verification must delegate to the invariant owner",
    )
    require(
        checks,
        "std::array<Definition, 14>" in owner
        and owner.count('{"table",') == 8
        and owner.count('{"index",') == 6,
        "contract_has_expected_fourteen_objects",
        "schema version 10 consists of exactly eight tables and six named indexes",
    )
    require(
        checks,
        "IF NOT EXISTS" not in owner,
        "contract_ddl_is_not_repair_capable",
        "canonical creation SQL must fail rather than preserve an existing weak object",
    )
    require(
        checks,
        "PRAGMA table_info" not in ledger
        and "lower_sql.find(\"create unique index\")" not in ledger,
        "weak_column_and_substring_attestation_is_absent",
        "column-name sets and SQL substrings do not prove constraints or index identity",
    )
    require(
        checks,
        "SELECT type, name, tbl_name, sql FROM sqlite_schema" in ledger
        and "WHERE sql IS NOT NULL;" in ledger
        and "ORDER BY type, name" not in ledger
        and "sqlite_exact_text_or_throw" in ledger
        and "verify_sqlite_replay_ledger_schema(observed)" in ledger,
        "observed_schema_is_exactly_extracted_and_verified",
        "the SQLite adapter must preserve exact type/name/table/SQL evidence and reject explicit sqlite_* objects while excluding only SQL-NULL autoindexes",
    )
    require(
        checks,
        "if (observed.size() > contract.size()) break;" in ledger
        and '"SQLite replay-ledger schema SQL", 16384' in ledger,
        "schema_evidence_has_allocation_bounds",
        "an untrusted schema must not force unbounded object or SQL accumulation",
    )

    load_body = function_body(
        ledger,
        "void SqliteWalReplayLedger::load(",
        "void SqliteWalReplayLedger::create_schema()",
    )
    require(
        checks,
        bool(load_body)
        and load_body.find("existing-database preflight")
        < load_body.find("PRAGMA journal_mode=WAL")
        < load_body.find("create_schema()"),
        "existing_schema_is_attested_before_mutation_or_creation",
        "startup must not change journal mode or invoke schema creation before attestation",
    )
    require(
        checks,
        "if (!opened_existing_database_) create_schema();" in load_body
        and "if (opened_existing_database_)" in load_body,
        "existing_database_never_enters_creation_path",
        "missing objects in durable state must be rejected, not recreated",
    )

    create_body = function_body(
        ledger,
        "void SqliteWalReplayLedger::create_schema()",
        "void SqliteWalReplayLedger::verify_backend_profile()",
    )
    require(
        checks,
        "sqlite_replay_ledger_schema_contract()" in create_body
        and "sqlite_replay_ledger_schema_create_statement" in create_body
        and "CREATE TABLE" not in create_body
        and "CREATE INDEX" not in create_body,
        "creation_uses_contract_without_second_ddl_copy",
        "new-database DDL must come only from the exact owner",
    )
    begin_position = create_body.find('"BEGIN IMMEDIATE;"')
    contract_position = create_body.find(
        "sqlite_replay_ledger_schema_contract()", begin_position
    )
    commit_position = create_body.find('"COMMIT;"', contract_position)
    catch_position = create_body.find("catch (...)", commit_position)
    rollback_without_errmsg = re.search(
        r'sqlite3_exec\s*\(\s*db_,\s*"ROLLBACK;",\s*nullptr,\s*nullptr,\s*nullptr\s*\)',
        create_body[catch_position:] if catch_position >= 0 else "",
        re.S,
    )
    require(
        checks,
        0 <= begin_position < contract_position < commit_position < catch_position
        and rollback_without_errmsg is not None,
        "new_schema_and_seed_rows_are_transactional",
        "creation, seed rows, exact commit, and best-effort rollback must remain one ordered transaction",
    )
    require(
        checks,
        rollback_without_errmsg is not None
        and "rollback_error" not in create_body
        and "sqlite3_free" not in create_body,
        "schema_rollback_avoids_optional_exec_errmsg_allocation",
        "error cleanup must not create another allocator cut while unwinding schema creation",
    )
    require(
        checks,
        "new-database post-create" in create_body,
        "new_schema_is_attested_after_creation",
        "the owner must prove the SQL SQLite actually stored, not just the SQL requested",
    )
    require(
        checks,
        ledger.count("verify_sqlite_replay_ledger_schema_or_throw(") >= 4,
        "live_restore_and_new_database_paths_share_attestation",
        "one definition plus snapshot, live-startup, and post-create calls must remain",
    )
    require(
        checks,
        "foreign_key_check" in ledger and "integrity_check" in ledger,
        "row_and_storage_checks_remain_complementary",
        "exact DDL does not replace foreign-key, integrity, or semantic row verification",
    )
    require(
        checks,
        "constraint-free ingress replay table" in focused
        and "generated hidden column" in focused
        and "widened nonce uniqueness identity" in focused,
        "focused_proof_covers_enforcement_aliases",
        "pure tests must cover stripped constraints, generated columns, and widened uniqueness",
    )
    for marker, check_id in (
        ("PRAGMA writable_schema=ON", "integrated_test_models_hostile_schema_bytes"),
        ("failed live load silently repaired", "integrated_test_proves_no_repair"),
        ("restore_sqlite_snapshot_into_ledger", "integrated_test_exercises_restore"),
        ("schema_sql_mismatch", "integrated_test_checks_exact_mismatch"),
        ("missing_object", "integrated_test_checks_missing_index"),
        ("sqlite_stat1", "integrated_test_checks_reserved_prefix_objects"),
    ):
        require(checks, marker in integrated, check_id, f"integrated proof marker: {marker}")
    require(
        checks,
        "attacker-sensitive-marker" in focused
        and "summary leaked hostile schema bytes" in focused,
        "diagnostics_are_proven_value_free",
        "untrusted DDL and object bytes must not enter logs through verification summaries",
    )
    require(
        checks,
        "sqlite3_" not in owner,
        "pure_owner_has_no_sqlite_handle_authority",
        "the exact contract compares values and cannot open or mutate a database",
    )
    for marker, check_id in (
        ("kSqliteReplayLedgerSchemaVersion", "schema_version_has_single_owner"),
        ("kSqliteReplayLedgerEntryMaterialVersion", "material_version_has_single_owner"),
        ("kSqliteReplayLedgerCommitProtocol", "commit_protocol_has_single_owner"),
    ):
        require(checks, marker in header and marker in ledger, check_id, marker)

    report = {
        "format": "anonsync-sqlite-replay-ledger-schema-contract-audit-v1",
        "passed": all(check.passed for check in checks),
        "checks": [asdict(check) for check in checks],
        "metrics": {
            "contract_lines": len(owner.splitlines()),
            "focused_test_lines": len(focused.splitlines()),
            "integrated_test_lines": len(integrated.splitlines()),
            "contract_objects": owner.count('{"table",') + owner.count('{"index",'),
            "ledger_attestation_mentions": ledger.count(
                "verify_sqlite_replay_ledger_schema_or_throw("
            ),
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
