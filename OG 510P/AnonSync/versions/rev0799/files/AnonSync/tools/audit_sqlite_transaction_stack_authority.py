#!/usr/bin/env python3
"""Deterministic source-shape audit for SQLite transaction-stack authority.

Compilation and adversarial tests prove runtime behavior. This conservative
inventory prevents the reviewed boundary from quietly regressing into raw SQL,
ambient transaction adoption, same-handle interleaving, or SAVEPOINT bypasses.
It intentionally reports legacy raw boundaries in unrelated domains without
pretending they were migrated by this revision.
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
    Path("CMakeLists.txt"),
    Path("src/sync_sqlite_support.hpp"),
    Path("src/sync_sqlite_support.cpp"),
    Path("src/sync_sqlite_transaction.cpp"),
    Path("src/sync_sqlite_connection_authority.hpp"),
    Path("src/sync_sqlite_connection_authority.cpp"),
    Path("src/sync_sqlite_connection_authority_internal.hpp"),
    Path("src/sync_peer_ingress_schema.cpp"),
    Path("src/sync_peer_ingress_lifecycle.cpp"),
    Path("src/sync_peer_ingress_payload_store.cpp"),
    Path("tests/sqlite_connection_authority_test.cpp"),
    Path("tests/peer_ingress_schema_attestation_test.cpp"),
    Path("tests/sqlite_support_test.cpp"),
)

SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}
SKIP_PARTS = {".git", "build", "_build", "third_party", "vendor"}
RAW_BOUNDARY_LITERAL = re.compile(
    r'"\s*(?:BEGIN(?:\s+(?:DEFERRED|IMMEDIATE|EXCLUSIVE|TRANSACTION))*|'
    r'COMMIT(?:\s+TRANSACTION)?|END(?:\s+TRANSACTION)?|'
    r'ROLLBACK(?:\s+TRANSACTION)?(?:\s+TO(?:\s+SAVEPOINT)?)?|'
    r'SAVEPOINT|RELEASE(?:\s+SAVEPOINT)?)\b',
    re.IGNORECASE,
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


def require(checks: list[Check], condition: bool, check_id: str, detail: str) -> None:
    checks.append(Check(check_id, condition, detail))


def locations(root: Path, text: str, path: Path, pattern: re.Pattern[str]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for number, line in enumerate(text.splitlines(), 1):
        if pattern.search(line):
            out.append(
                {
                    "path": path.as_posix(),
                    "line": number,
                    "text": line.strip()[:300],
                }
            )
    return out


def source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted((root / "src").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        files.append(rel)
    return files


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

    missing = [path.as_posix() for path in SENSITIVE_FILES if not (root / path).is_file()]
    if missing:
        report = {
            "format": "anonsync-sqlite-transaction-stack-authority-audit-v1",
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

    texts = {
        path: (root / path).read_text(encoding="utf-8", errors="strict")
        for path in SENSITIVE_FILES
    }
    cmake = texts[Path("CMakeLists.txt")]
    support_hpp = texts[Path("src/sync_sqlite_support.hpp")]
    support_cpp = texts[Path("src/sync_sqlite_support.cpp")]
    transaction_cpp = texts[Path("src/sync_sqlite_transaction.cpp")]
    authority_cpp = texts[Path("src/sync_sqlite_connection_authority.cpp")]
    authority_internal = texts[Path("src/sync_sqlite_connection_authority_internal.hpp")]
    schema_cpp = texts[Path("src/sync_peer_ingress_schema.cpp")]
    lifecycle_cpp = texts[Path("src/sync_peer_ingress_lifecycle.cpp")]
    payload_cpp = texts[Path("src/sync_peer_ingress_payload_store.cpp")]
    authority_test = texts[Path("tests/sqlite_connection_authority_test.cpp")]
    schema_test = texts[Path("tests/peer_ingress_schema_attestation_test.cpp")]
    support_test = texts[Path("tests/sqlite_support_test.cpp")]

    checks: list[Check] = []

    require(
        checks,
        "src/sync_sqlite_transaction.cpp" in cmake,
        "transaction_implementation_is_independent_target_source",
        "the typed transaction implementation must remain an invariant-owned translation unit",
    )
    require(
        checks,
        "SyncSqliteTransaction::" not in support_cpp,
        "generic_sqlite_support_has_no_transaction_implementation",
        "generic statement/codec helpers must not reacquire transaction ownership",
    )
    for method in (
        "SyncSqliteTransaction::SyncSqliteTransaction",
        "SyncSqliteTransaction::~SyncSqliteTransaction",
        "SyncSqliteTransaction::commit",
        "SyncSqliteTransaction::rollback",
        "SyncSqliteTransactionAuthority::authorizes",
    ):
        require(
            checks,
            method in transaction_cpp,
            "transaction_owner_method_" + re.sub(r"[^a-z0-9]+", "_", method.lower()).strip("_"),
            f"typed owner method must remain in transaction implementation: {method}",
        )

    for needle, check_id in (
        ("process_salt", "proof_binds_process_salt"),
        ("connection_incarnation", "proof_binds_connection_incarnation"),
        ("authorizer_generation", "proof_binds_authorizer_generation"),
        ("transaction_generation", "proof_binds_transaction_generation"),
        ("retained_connection_mutex", "proof_retains_connection_mutex"),
        ("begin_sync_sqlite_transaction_boundary_or_throw", "typed_begin_internal_api"),
        ("end_sync_sqlite_transaction_boundary_or_throw", "typed_end_internal_api"),
        ("release_sync_sqlite_transaction_mutex_noexcept", "typed_mutex_release_api"),
    ):
        require(checks, needle in authority_internal, check_id, f"required boundary marker: {needle}")

    for needle, check_id in (
        ("if (action == SQLITE_SAVEPOINT) return SQLITE_DENY", "savepoint_stack_is_denied"),
        ("if (action == SQLITE_TRANSACTION)", "transaction_action_is_intercepted"),
        ("transaction_permit_active", "single_use_permit_has_active_state"),
        ("transaction_permit_observed", "single_use_permit_is_consumed"),
        ("active_transaction_generation", "connection_tracks_exact_transaction_generation"),
        ("transaction_operation_matches", "permit_matches_exact_boundary_operation"),
        ("run_authorizer_ownership_probe_or_throw", "boundary_challenges_owned_callback"),
        ("cannot replace connection authority inside an active transaction", "reinstall_rejects_live_generation"),
        ("rollback_newly_started_transaction_noexcept", "failed_begin_has_exact_cleanup"),
        ("Do not issue an unfenced fallback", "destructor_rejects_ambiguous_raw_rollback"),
    ):
        require(checks, needle in authority_cpp, check_id, f"required owner marker: {needle}")

    require(
        checks,
        authority_cpp.count("sqlite3_set_authorizer(") >= 2,
        "owned_bridge_can_install_and_supersede",
        "connection authority owner must install and deliberately supersede its bridge",
    )
    require(
        checks,
        "sqlite3_set_authorizer(" not in transaction_cpp,
        "transaction_owner_cannot_replace_authorizer",
        "typed transaction code must consume, not own, callback installation",
    )
    require(
        checks,
        "release_sync_sqlite_transaction_mutex_noexcept(*boundary_proof_)" in transaction_cpp,
        "revocation_releases_retained_connection_mutex",
        "every typed generation revocation must release its exact recursive mutex entry",
    )
    require(
        checks,
        "authority_state_->boundary.retained_connection_mutex = nullptr" in transaction_cpp,
        "copied_authority_is_not_a_mutex_owner",
        "copied transaction capabilities must never duplicate mutex ownership",
    )
    require(
        checks,
        "thread-affine transaction guard" in support_hpp,
        "thread_affinity_is_documented",
        "retaining SQLite's recursive mutex makes transaction ownership thread-affine",
    )

    require(
        checks,
        "sync_sqlite_connection_authority_state_present_or_throw" in schema_cpp
        and "recover prior connection authority" in schema_cpp,
        "schema_recovery_reinstalls_bridge_before_typed_begin",
        "alien callback recovery must occur before a typed schema snapshot begins",
    )
    require(
        checks,
        schema_cpp.find("recover prior connection authority")
        < schema_cpp.find("schema attestation read snapshot"),
        "schema_recovery_precedes_snapshot",
        "the restrictive policy must be current before schema BEGIN is compiled",
    )

    selftest_marker = "void run_sync_peer_ingress_lifecycle_selftests("
    marker_index = lifecycle_cpp.find(selftest_marker)
    require(
        checks,
        marker_index >= 0,
        "peer_lifecycle_selftest_boundary_found",
        "production/selftest split marker must remain reviewable",
    )
    production_lifecycle = lifecycle_cpp[:marker_index] if marker_index >= 0 else lifecycle_cpp
    production_raw_lifecycle = locations(
        root,
        production_lifecycle,
        Path("src/sync_peer_ingress_lifecycle.cpp"),
        RAW_BOUNDARY_LITERAL,
    )
    require(
        checks,
        not production_raw_lifecycle,
        "peer_ingress_production_has_no_raw_transaction_sql",
        "peer-ingress production lifecycle must use only the typed transaction owner",
    )

    payload_savepoint_locations = locations(
        root,
        payload_cpp,
        Path("src/sync_peer_ingress_payload_store.cpp"),
        RAW_BOUNDARY_LITERAL,
    )
    payload_ensure_occurrences = sum(
        (root / path).read_text(encoding="utf-8", errors="replace").count(
            "ensure_peer_transport_ingress_payload_store_schema_or_throw("
        )
        for path in source_files(root)
        if path.suffix.lower() in {".c", ".cc", ".cpp", ".cxx"}
    )
    require(
        checks,
        bool(payload_savepoint_locations),
        "legacy_payload_bootstrap_savepoint_is_inventoried",
        "the remaining bootstrap-only savepoint helper must stay visible until a typed savepoint API exists",
    )
    require(
        checks,
        payload_ensure_occurrences == 1,
        "legacy_payload_savepoint_has_no_production_caller",
        "the raw payload-schema savepoint helper may only exist as an isolated bootstrap definition",
    )

    for needle, check_id in (
        ("SAVEPOINT raw_outer", "test_outer_savepoint_bypass"),
        ("ROLLBACK TO nested_raw", "test_nested_savepoint_bypass"),
        ("BEGIN prepared before authority installation", "test_prepared_begin_reauthorization"),
        ("SQLITE_IGNORE acquired transaction-boundary authority", "test_ignore_fails_closed"),
        ("stale typed destructor rolled back a later alien transaction", "test_no_ambiguous_destructor_rollback"),
        ("typed transaction released the connection mutex before rollback", "test_full_generation_mutex_retention"),
        ("inside an active transaction", "test_authorizer_reinstall_blocked"),
    ):
        require(checks, needle in authority_test, check_id, f"required adversarial test marker: {needle}")
    require(
        checks,
        "sqlite_exec_or_throw(db.get(), \"BEGIN" not in schema_test[schema_test.find("void test_fresh_bootstrap"):],
        "post_attestation_schema_tests_use_typed_begin",
        "schema authority tests after bootstrap must not retain raw BEGIN call sites",
    )
    require(
        checks,
        "deliberate raw commit misuse" in support_test,
        "unowned_compatibility_boundary_is_tested",
        "unowned utility connections retain an explicit, isolated compatibility test",
    )

    raw_boundary_inventory: list[dict[str, object]] = []
    for rel in source_files(root):
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        raw_boundary_inventory.extend(locations(root, text, rel, RAW_BOUNDARY_LITERAL))

    owner_paths = {
        "src/sync_sqlite_transaction.cpp",
        "src/sync_sqlite_connection_authority.cpp",
    }
    legacy_raw_boundary_inventory = [
        item for item in raw_boundary_inventory if item["path"] not in owner_paths
    ]

    violations = [asdict(check) for check in checks if not check.passed]
    report = {
        "format": "anonsync-sqlite-transaction-stack-authority-audit-v1",
        "root": str(root),
        "passed": not violations,
        "check_count": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
        "production_peer_ingress_raw_boundary_locations": production_raw_lifecycle,
        "payload_bootstrap_savepoint_locations": payload_savepoint_locations,
        "raw_transaction_boundary_inventory": raw_boundary_inventory,
        "legacy_raw_transaction_boundary_inventory": legacy_raw_boundary_inventory,
        "legacy_raw_transaction_boundary_count": len(legacy_raw_boundary_inventory),
        "sensitive_file_sha256": {
            path.as_posix(): sha256_file(root / path) for path in SENSITIVE_FILES
        },
        "interpretation": (
            "Legacy raw boundaries outside peer-ingress are inventory, not proof of safety. "
            "They are migration candidates for later invariant-owned revisions."
        ),
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
