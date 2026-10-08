#!/usr/bin/env python3
"""Fail-closed source-shape audit for durable peer-ingress payload authority.

This is deliberately narrower than a C++ parser. Compilation and adversarial
runtime tests prove behavior; this tool prevents the reviewed authority shape
from quietly regressing into ambient booleans, raw transaction adoption, or
SQLite TEMP-first name resolution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SENSITIVE_FILES = (
    Path("src/sync_sqlite_support.hpp"),
    Path("src/sync_sqlite_support.cpp"),
    Path("src/sync_sqlite_transaction.cpp"),
    Path("src/sync_sqlite_connection_authority.cpp"),
    Path("src/sync_peer_ingress_payload_store.hpp"),
    Path("src/sync_peer_ingress_payload_store.cpp"),
    Path("src/sync_peer_ingress_retention.hpp"),
    Path("src/sync_peer_ingress_retention.cpp"),
    Path("src/sync_peer_ingress_lifecycle.cpp"),
    Path("tests/sqlite_support_test.cpp"),
    Path("tests/sqlite_runtime_payload_store_test.cpp"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_contains(checks: list[Check], text: str, needle: str, check_id: str) -> None:
    checks.append(Check(check_id, needle in text, f"required source marker: {needle}"))


def forbid_contains(checks: list[Check], text: str, needle: str, check_id: str) -> None:
    checks.append(Check(check_id, needle not in text, f"forbidden source marker: {needle}"))


def source_locations(path: Path, pattern: re.Pattern[str], root: Path) -> list[dict[str, object]]:
    locations: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if pattern.search(line):
            locations.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "line": line_number,
                    "text": line.strip(),
                }
            )
    return locations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="AnonSync source root",
    )
    parser.add_argument("--json", type=Path, help="write the deterministic JSON report")
    args = parser.parse_args()
    root = args.root.resolve()

    missing = [path.as_posix() for path in SENSITIVE_FILES if not (root / path).is_file()]
    if missing:
        report = {
            "audit": "peer-payload-transaction-authority-v2",
            "passed": False,
            "violations": [f"missing sensitive file: {path}" for path in missing],
        }
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 2

    texts = {path: (root / path).read_text(encoding="utf-8") for path in SENSITIVE_FILES}
    support_hpp = texts[Path("src/sync_sqlite_support.hpp")]
    support_cpp = texts[Path("src/sync_sqlite_support.cpp")]
    transaction_cpp = texts[Path("src/sync_sqlite_transaction.cpp")]
    authority_cpp = texts[Path("src/sync_sqlite_connection_authority.cpp")]
    payload_hpp = texts[Path("src/sync_peer_ingress_payload_store.hpp")]
    payload_cpp = texts[Path("src/sync_peer_ingress_payload_store.cpp")]
    retention_hpp = texts[Path("src/sync_peer_ingress_retention.hpp")]
    lifecycle_cpp = texts[Path("src/sync_peer_ingress_lifecycle.cpp")]
    support_test = texts[Path("tests/sqlite_support_test.cpp")]
    payload_test = texts[Path("tests/sqlite_runtime_payload_store_test.cpp")]

    checks: list[Check] = []

    # Transaction construction is a typed, single-owner operation. A raw SQL
    # string or adopt-after-BEGIN API would reopen the exception-safety gap.
    require_contains(checks, support_hpp, "enum class SyncSqliteTransactionMode", "typed_transaction_mode")
    require_contains(checks, support_hpp, "SyncSqliteTransactionMode mode", "typed_transaction_constructor")
    forbid_contains(checks, support_hpp + support_cpp + lifecycle_cpp,
                    "SyncSqliteAdoptActiveTransaction", "no_transaction_adoption")
    forbid_contains(checks, support_hpp, "std::string begin_sql", "no_ambient_begin_sql")
    require_contains(checks, lifecycle_cpp,
                     "std::unique_ptr<SyncSqliteTransaction>\nbegin_peer_transport_write_transaction_or_throw",
                     "write_lock_helper_returns_owner")

    helper_start = lifecycle_cpp.find(
        "std::unique_ptr<SyncSqliteTransaction>\n"
        "begin_peer_transport_write_transaction_or_throw")
    helper_end = lifecycle_cpp.find(
        "PeerTransportIngressWriteConnection "
        "open_peer_transport_ingress_sqlite_readwrite_or_throw",
        helper_start,
    )
    helper_text = (
        lifecycle_cpp[helper_start:helper_end]
        if helper_start >= 0 and helper_end > helper_start
        else ""
    )
    checks.append(Check(
        "write_lock_helper_constructs_guard",
        "std::make_unique<SyncSqliteTransaction>" in helper_text,
        "write-lock acquisition must construct the RAII owner itself",
    ))
    checks.append(Check(
        "write_lock_helper_has_no_raw_begin",
        "BEGIN" not in helper_text and "sqlite_exec_or_throw" not in helper_text,
        "write-lock helper must not BEGIN before the owner exists",
    ))
    owner_after_lease_patterns = (
        "SyncSqliteConnectionAuthorityLease schema_authority_lease;\n"
        "        std::unique_ptr<SyncSqliteTransaction> transaction_owner",
        "SyncSqliteConnectionAuthorityLease claim_schema_authority_lease;\n"
        "            std::unique_ptr<SyncSqliteTransaction> claim_transaction_owner",
        "SyncSqliteConnectionAuthorityLease completion_schema_authority_lease;\n"
        "        std::unique_ptr<SyncSqliteTransaction> completion_transaction_owner",
        "SyncSqliteConnectionAuthorityLease handoff_schema_authority_lease;\n"
        "            std::unique_ptr<SyncSqliteTransaction> handoff_transaction_owner",
    )
    checks.append(Check(
        "transaction_destroys_before_schema_authority_lease",
        lifecycle_cpp.count(owner_after_lease_patterns[0]) == 3
        and all(pattern in lifecycle_cpp for pattern in owner_after_lease_patterns[1:]),
        "declaration order must roll back/destroy the transaction before releasing schema authority",
    ))

    # Authority is exact guard lifetime + exact main snapshot/write state. The
    # wrapper also states SQLite's public-API limit: raw transaction control on
    # an owned handle is forbidden because SQLite exposes no transaction id.
    for needle, check_id in (
        ("SyncSqliteTransactionAuthority snapshot_authority_", "schema_capability_uses_authority_lease"),
        ("snapshot_authority_.authorizes_snapshot(db)", "schema_capability_checks_live_snapshot"),
        ("const SyncSqliteTransaction& transaction", "payload_api_requires_transaction"),
        ("transaction.authorizes_write(db)", "payload_store_requires_write_generation"),
        ("sqlite3_get_autocommit(db) != 0", "authority_checks_explicit_transaction"),
        ("sqlite3_txn_state(db, \"main\")", "authority_checks_main_transaction_state"),
        ("mechanically denies raw BEGIN/COMMIT/ROLLBACK", "raw_boundary_limit_documented"),
    ):
        require_contains(
            checks,
            payload_hpp + payload_cpp + support_hpp + support_cpp + transaction_cpp + authority_cpp,
            needle,
            check_id,
        )

    # Every schema/data lookup in this boundary is pinned to main; TEMP is not
    # durable evidence and must never win name resolution.
    for needle, check_id in (
        ("PRAGMA main.table_xinfo('sync_peer_transport_ingress_payloads')", "payload_columns_main_qualified"),
        ("PRAGMA main.foreign_key_list('sync_peer_transport_ingress_payloads')", "payload_foreign_key_main_qualified"),
        ("FROM main.sqlite_schema", "payload_schema_catalog_main_qualified"),
        ("FROM main.sync_peer_transport_ingress_payloads", "payload_read_main_qualified"),
        ("INSERT INTO main.sync_peer_transport_ingress_payloads", "payload_write_main_qualified"),
        ("main_schema_creation_sql_or_throw", "payload_creation_main_qualified"),
        ("FROM main.sqlite_schema WHERE type='table'", "shared_table_probe_main_qualified"),
        ("PRAGMA main.table_xinfo(", "shared_column_probe_main_qualified"),
    ):
        require_contains(checks, payload_cpp + support_cpp, needle, check_id)

    for pattern, check_id in (
        (r"\bFROM\s+sync_peer_transport_ingress_payloads\b", "no_unqualified_payload_read"),
        (r"\bINSERT\s+INTO\s+sync_peer_transport_ingress_payloads\b", "no_unqualified_payload_write"),
        (r"\bPRAGMA\s+(?!main\.)table_(?:info|xinfo)\s*\(", "no_unqualified_payload_column_pragma"),
        (r"\bPRAGMA\s+(?!main\.)foreign_key_list\s*\(", "no_unqualified_payload_fk_pragma"),
    ):
        checks.append(Check(
            check_id,
            re.search(pattern, payload_cpp, re.IGNORECASE) is None,
            f"forbidden unqualified payload-boundary pattern: {pattern}",
        ))

    payload_access_pattern = re.compile(
        r"\b(?:FROM|JOIN|INTO|UPDATE|DELETE\s+FROM)\s+"
        r"sync_peer_transport_ingress_payloads\b",
        re.IGNORECASE,
    )
    unqualified_production_payload_locations: list[dict[str, object]] = []
    for source_path in sorted((root / "src").rglob("*.cpp")):
        unqualified_production_payload_locations.extend(
            source_locations(source_path, payload_access_pattern, root)
        )
    checks.append(Check(
        "production_payload_access_main_qualified",
        not unqualified_production_payload_locations,
        "every production payload-table access must name main explicitly",
    ))

    # Retention is destructive and must consume the same snapshot capability.
    require_contains(checks, retention_hpp,
                     "const SyncSqliteTransaction& transaction",
                     "retention_selector_requires_transaction")

    # Runtime proof markers. These do not replace execution; they keep the
    # adversarial cases visible during review and packaging.
    for needle, check_id in (
        ("CREATE TEMP TABLE sync_peer_transport_ingress_payloads", "test_temp_payload_shadow"),
        ("stale capability snapshot", "test_stale_schema_capability"),
        ("read-only payload transaction", "test_read_snapshot_rejected_for_write"),
        ("_exit(0)", "test_process_crash_without_destructors"),
        ("commit_before_crash", "test_crash_before_commit"),
        ("temp_only_column", "test_shared_probe_temp_shadow"),
        ("SyncSqliteTransactionMode::Exclusive", "test_typed_exclusive_mode"),
        ("bypassed boundary permanently revokes", "test_observed_raw_boundary_revocation"),
    ):
        require_contains(checks, payload_test + support_test, needle, check_id)

    raw_begin_locations = source_locations(
        root / "src/sync_peer_ingress_lifecycle.cpp",
        re.compile(r'"BEGIN(?:\s+IMMEDIATE|\s+EXCLUSIVE)?;"'),
        root,
    )
    allowed_raw_begin_labels = {
        "sqlite_exec_or_throw(writer.db, \"BEGIN IMMEDIATE;\", \"peer ingress read-only lock writer begin\");",
        "sqlite_exec_or_throw(writer.db, \"BEGIN IMMEDIATE;\", \"peer ingress handoff writer begin\");",
    }
    unexpected_raw_begins = [
        item for item in raw_begin_locations if item["text"] not in allowed_raw_begin_labels
    ]
    checks.append(Check(
        "no_production_raw_begin_handoff",
        not unexpected_raw_begins,
        "only selftest lock-holder fixtures may issue raw BEGIN in peer lifecycle",
    ))

    violations = [asdict(check) for check in checks if not check.passed]
    report = {
        "audit": "peer-payload-transaction-authority-v2",
        "root": str(root),
        "passed": not violations,
        "check_count": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
        "unexpected_raw_begin_locations": unexpected_raw_begins,
        "unqualified_production_payload_locations": unqualified_production_payload_locations,
        "sensitive_file_sha256": {
            path.as_posix(): sha256_file(root / path) for path in SENSITIVE_FILES
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
