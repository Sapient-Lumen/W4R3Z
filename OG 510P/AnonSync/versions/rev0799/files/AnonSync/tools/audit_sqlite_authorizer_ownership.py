#!/usr/bin/env python3
"""Fail-closed lexical audit for AnonSync's SQLite authority boundary.

This tool deliberately proves only source-shape invariants. Runtime callback
replacement, generation fencing, and mutex retention are covered by the C++
adversarial tests. The audit prevents authority-sensitive calls from quietly
spreading back into lifecycle or schema monoliths.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}
OWNER = Path("src/sync_sqlite_connection_authority.cpp")
MUTEX_CAPABILITY_OWNER = Path("src/sync_sqlite_mutex_capability.cpp")
AUTHORITY_INTERNAL = Path("src/sync_sqlite_connection_authority_internal.hpp")
TRANSACTION_SOURCE = Path("src/sync_sqlite_transaction.cpp")
SCHEMA_HEADER = Path("src/sync_peer_ingress_schema.hpp")
SCHEMA_SOURCE = Path("src/sync_peer_ingress_schema.cpp")
LIFECYCLE_SOURCE = Path("src/sync_peer_ingress_lifecycle.cpp")
AUTHORITY_TEST = Path("tests/sqlite_connection_authority_test.cpp")
SCHEMA_TEST = Path("tests/peer_ingress_schema_attestation_test.cpp")


def source_files(root: Path, top: str) -> Iterable[Path]:
    base = root / top
    if not base.exists():
        return []
    return (
        path
        for path in base.rglob("*")
        if path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES
    )


def call_locations(root: Path, top: str, symbol: str) -> list[dict[str, object]]:
    pattern = re.compile(rf"\b{re.escape(symbol)}\s*\(")
    locations: list[dict[str, object]] = []
    for path in source_files(root, top):
        text = path.read_text(encoding="utf-8", errors="strict")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                locations.append(
                    {
                        "path": path.relative_to(root).as_posix(),
                        "line": line_number,
                        "text": line.strip(),
                    }
                )
    return locations


def require_contains(
    violations: list[str], text: str, needle: str, label: str
) -> None:
    if needle not in text:
        violations.append(f"missing {label}: {needle}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="AnonSync source root",
    )
    parser.add_argument("--json", type=Path, help="also write JSON report")
    args = parser.parse_args()
    root = args.root.resolve()

    violations: list[str] = []
    set_authorizer_production = call_locations(root, "src", "sqlite3_set_authorizer")
    set_authorizer_tests = call_locations(root, "tests", "sqlite3_set_authorizer")
    get_clientdata_production = call_locations(root, "src", "sqlite3_get_clientdata")
    set_clientdata_production = call_locations(root, "src", "sqlite3_set_clientdata")

    for location in set_authorizer_production:
        if Path(str(location["path"])) != OWNER:
            violations.append(
                "direct sqlite3_set_authorizer outside the authority owner at "
                f"{location['path']}:{location['line']}"
            )
    if len(set_authorizer_production) < 1:
        violations.append("authority owner contains no sqlite3_set_authorizer call")

    clientdata_owners = {OWNER, MUTEX_CAPABILITY_OWNER}
    for symbol, locations in (
        ("sqlite3_get_clientdata", get_clientdata_production),
        ("sqlite3_set_clientdata", set_clientdata_production),
    ):
        for location in locations:
            if Path(str(location["path"])) not in clientdata_owners:
                violations.append(
                    f"direct {symbol} outside reviewed client-data owners at "
                    f"{location['path']}:{location['line']}"
                )
        if not locations:
            violations.append(f"reviewed owners contain no {symbol} call")

    for required_owner in sorted(clientdata_owners, key=lambda path: path.as_posix()):
        for symbol, locations in (
            ("sqlite3_get_clientdata", get_clientdata_production),
            ("sqlite3_set_clientdata", set_clientdata_production),
        ):
            if not any(Path(str(location["path"])) == required_owner for location in locations):
                violations.append(
                    f"{required_owner.as_posix()} contains no {symbol} call"
                )

    owner_text = (root / OWNER).read_text(encoding="utf-8")
    capability_text = (root / MUTEX_CAPABILITY_OWNER).read_text(encoding="utf-8")
    for needle, label in (
        ("SQLITE_VERSION_NUMBER >= 3044000", "SQLite client-data version floor"),
        ("sqlite3_db_mutex", "serialized connection mutex acquisition"),
        ("connection_authorizer_bridge", "owned authorizer bridge"),
        ("connection_incarnation", "connection incarnation"),
        ("authorizer_generation", "authorizer generation"),
        ("probe_nonce", "prepare-time ownership challenge"),
        ("SQLITE_DENY", "fail-closed callback result"),
        ("SQLITE_TRANSACTION", "transaction-stack action interception"),
        ("SQLITE_SAVEPOINT", "savepoint-stack action interception"),
        ("active_transaction_generation", "exact active transaction generation"),
        ("transaction_permit_observed", "single-use transaction permit consumption"),
    ):
        require_contains(violations, owner_text, needle, label)
    for needle, label in (
        (
            "anonsync.sqlite.retained-mutex-capabilities.v1",
            "retained-mutex client-data namespace",
        ),
        (
            "destroy_retained_mutex_capability_state",
            "close-order lifetime sentinel destructor",
        ),
        ("active_capabilities", "retained-mutex lifetime counter"),
    ):
        require_contains(violations, capability_text, needle, label)

    authority_internal = (root / AUTHORITY_INTERNAL).read_text(encoding="utf-8")
    transaction_source = (root / TRANSACTION_SOURCE).read_text(encoding="utf-8")
    for needle, label in (
        ("retained_connection_mutex", "full-generation connection mutex retention"),
        ("transaction_generation", "transaction generation proof"),
        ("begin_sync_sqlite_transaction_boundary_or_throw", "typed begin boundary"),
        ("end_sync_sqlite_transaction_boundary_or_throw", "typed end boundary"),
    ):
        require_contains(violations, authority_internal, needle, label)
    for needle, label in (
        ("release_sync_sqlite_transaction_mutex_noexcept", "exact mutex release"),
        ("SyncSqliteTransaction::commit", "typed commit implementation"),
        ("SyncSqliteTransaction::rollback", "typed rollback implementation"),
    ):
        require_contains(violations, transaction_source, needle, label)

    schema_header = (root / SCHEMA_HEADER).read_text(encoding="utf-8")
    schema_source = (root / SCHEMA_SOURCE).read_text(encoding="utf-8")
    require_contains(
        violations,
        schema_header,
        "SyncSqliteConnectionAuthorityProof connection_authority_",
        "schema attestation authority proof",
    )
    require_contains(
        violations,
        schema_header,
        "SyncSqliteConnectionAuthorityLease",
        "schema verification lease return type",
    )
    require_contains(
        violations,
        schema_source,
        "install_sync_sqlite_connection_authority_or_throw",
        "owned bridge installation",
    )
    require_contains(
        violations,
        schema_source,
        "acquire_sync_sqlite_connection_authority_or_throw",
        "use-time bridge challenge",
    )

    lifecycle_text = (root / LIFECYCLE_SOURCE).read_text(encoding="utf-8")
    lifecycle_lines = lifecycle_text.splitlines()
    wrapper_names = (
        "verify_peer_transport_write_schema_snapshot_or_throw",
        "verify_peer_transport_read_schema_snapshot_or_throw",
    )
    lifecycle_calls: list[dict[str, object]] = []
    for index, line in enumerate(lifecycle_lines):
        for name in wrapper_names:
            if name not in line:
                continue
            stripped = line.strip()
            # Definitions have the explicit lease return type immediately
            # above. Wrapped calls can also begin with the function name, so
            # spelling alone is not enough to distinguish them.
            previous = lifecycle_lines[index - 1].strip() if index > 0 else ""
            if previous == "[[nodiscard]] SyncSqliteConnectionAuthorityLease":
                continue
            window = " ".join(
                item.strip() for item in lifecycle_lines[max(0, index - 3) : index + 1]
            )
            assignment = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*" + re.escape(name), window)
            retained = assignment is not None or "return " in window
            lease_name = assignment.group(1) if assignment else None
            declaration_line = None
            transaction_line = None
            if lease_name:
                declaration_pattern = re.compile(
                    r"\bSyncSqliteConnectionAuthorityLease\s+" +
                    re.escape(lease_name) + r"\b"
                )
                transaction_pattern = re.compile(
                    r"SyncSqliteTransaction|unique_ptr<SyncSqliteTransaction>"
                )
                for prior in range(index - 1, -1, -1):
                    if declaration_pattern.search(lifecycle_lines[prior]):
                        declaration_line = prior + 1
                        break
                if declaration_line is not None:
                    for prior in range(declaration_line, index):
                        if transaction_pattern.search(lifecycle_lines[prior]):
                            transaction_line = prior + 1
                            break
            rollback_safe_lifetime = (
                declaration_line is not None
                and transaction_line is not None
                and declaration_line < transaction_line < index + 1
            )
            lifecycle_calls.append(
                {
                    "line": index + 1,
                    "name": name,
                    "retained": retained,
                    "lease": lease_name,
                    "lease_declaration_line": declaration_line,
                    "transaction_declaration_line": transaction_line,
                    "rollback_safe_lifetime": rollback_safe_lifetime,
                }
            )
            if not retained:
                violations.append(
                    f"lifecycle schema verification discards its authority lease at "
                    f"{LIFECYCLE_SOURCE.as_posix()}:{index + 1}"
                )
            elif not rollback_safe_lifetime:
                violations.append(
                    "authority lease is not declared before its transaction guard at "
                    f"{LIFECYCLE_SOURCE.as_posix()}:{index + 1}; exception rollback "
                    "could occur after the connection mutex is released"
                )
    if not lifecycle_calls:
        violations.append("no lifecycle schema verification call sites were found")
    require_contains(
        violations,
        lifecycle_text,
        "SyncSqliteConnectionAuthorityLease schema_authority_lease;",
        "lease-before-transaction lifetime pattern",
    )

    authority_test = (root / AUTHORITY_TEST).read_text(encoding="utf-8")
    schema_test = (root / SCHEMA_TEST).read_text(encoding="utf-8")
    for needle, label in (
        ("prepared_before_fence", "pre-prepared statement reauthorization test"),
        ("alien authorizer replacement", "alien replacement test"),
        ("disabled authorizer", "authorizer disablement test"),
        ("authorizer generation changed", "stale generation test"),
        ("SQLITE_OPEN_NOMUTEX", "NOMUTEX rejection test"),
        ("replacement_finished", "lease concurrency test"),
        ("malformed_policy", "malformed callback result test"),
        ("throwing_policy", "exception boundary test"),
        ("test_transaction_stack_is_typed_and_generation_bound", "transaction-stack authority test"),
        ("test_transaction_retains_same_handle_serialization", "full-generation mutex retention test"),
        ("stale typed destructor rolled back a later alien transaction", "ambiguous destructor rollback rejection test"),
    ):
        require_contains(violations, authority_test, needle, label)
    for needle, label in (
        ("test_authorizer_ownership_and_generation", "schema integration test"),
        ("first.authorizes", "schema replacement invalidation assertion"),
        ("authorizer_generation", "schema generation assertion"),
    ):
        require_contains(violations, schema_test, needle, label)

    result = {
        "format": "anonsync-sqlite-authority-source-audit-v3",
        "ok": not violations,
        "owner": OWNER.as_posix(),
        "clientdata_owners": sorted(path.as_posix() for path in clientdata_owners),
        "production_set_authorizer_calls": set_authorizer_production,
        "test_set_authorizer_calls": set_authorizer_tests,
        "production_get_clientdata_calls": get_clientdata_production,
        "production_set_clientdata_calls": set_clientdata_production,
        "lifecycle_schema_verification_calls": lifecycle_calls,
        "violations": violations,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
