#!/usr/bin/env python3
"""Fail-closed source audit for durable ingress sender-replay reservations.

The replay row is auxiliary durable evidence, not authority merely because a
SQLite SELECT returned it. This audit keeps semantic validation in one small
pure C++ owner and requires both restart and read-only restore paths to invoke
that owner after reconstructing the prepared decision chain.
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
    Path("src/persistence/ingress_sender_replay_record.hpp"),
    Path("src/persistence/ingress_sender_replay_record.cpp"),
    Path("src/sqlite_replay_ledger.cpp"),
    Path("tests/persistence/ingress_sender_replay_record_tests.cpp"),
    Path("tests/sqlite_ingress_sender_replay_integrity_test.cpp"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def require(checks: list[Check], condition: bool, check_id: str, detail: str) -> None:
    checks.append(Check(check_id, bool(condition), detail))


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
            "format": "anonsync-ingress-sender-replay-integrity-audit-v1",
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
    header = texts[Path("src/persistence/ingress_sender_replay_record.hpp")]
    boundary = texts[Path("src/persistence/ingress_sender_replay_record.cpp")]
    ledger = texts[Path("src/sqlite_replay_ledger.cpp")]
    focused = texts[Path("tests/persistence/ingress_sender_replay_record_tests.cpp")]
    integration = texts[Path("tests/sqlite_ingress_sender_replay_integrity_test.cpp")]

    checks: list[Check] = []
    require(
        checks,
        "add_library(anonsync_ingress_sender_replay_record STATIC" in cmake and
        "${ANONSYNC_INGRESS_SENDER_REPLAY_RECORD_SOURCE}" in cmake,
        "semantic_owner_is_independent_library",
        "the semantic verifier must remain a separately linkable invariant owner",
    )
    core_match = re.search(
        r"set\(ANONSYNC_CORE_SOURCES(?P<body>.*?)\)\s*foreach\(", cmake, re.S
    )
    require(
        checks,
        core_match is not None and
        "ingress_sender_replay_record.cpp" not in core_match.group("body"),
        "semantic_owner_is_not_reabsorbed_by_core_sources",
        "the focused verifier source must not be compiled into the monolithic core archive",
    )
    require(
        checks,
        "anonsync_ingress_sender_replay_record_test" in cmake and
        "focused persistence boundary must not depend on anonsync_core_lib" in cmake,
        "focused_test_dependency_fence_is_configured",
        "CMake must retain a no-core dependency guard for the focused proof",
    )
    require(
        checks,
        '#include "persistence/ingress_sender_replay_record.hpp"' in ledger or
        '#include "ingress_sender_replay_record.hpp"' in ledger,
        "ledger_delegates_to_semantic_owner",
        "the ledger implementation must include the single semantic owner",
    )
    require(
        checks,
        ledger.count("verify_ingress_sender_replay_rows(") == 3,
        "restart_and_restore_each_scan_replay_rows",
        "one definition plus exactly two trust-path invocations must remain present",
    )
    require(
        checks,
        ("verify_foreign_key_integrity(db, label);" in ledger or
         "verify_foreign_key_integrity(db, label, &budget);" in ledger) and
        'verify_foreign_key_integrity(db_, "sqlite-wal replay ledger load");' in ledger and
        "PRAGMA foreign_key_check;" in ledger,
        "referential_integrity_is_checked_on_both_trust_paths",
        "integrity_check alone is insufficient; restart and restore must also run foreign_key_check",
    )
    require(
        checks,
        ledger.count("sqlite_exact_text_or_throw(") >= 9 and
        ledger.count("sqlite_exact_i64_or_throw(") >= 4 and
        "kIngressSenderReplayMaximumPrincipalBytes" in ledger,
        "durable_replay_scalars_are_exact_and_bounded",
        "row verification must reject coercion, embedded-control laundering, and oversized identity fields",
    )
    require(
        checks,
        "prepared.sender_replay_seen" in ledger and
        "multiple ingress sender replay rows reference one prepared effect" in ledger and
        "ingress_sender_replay_nonce_unique" in
            (root / "src/persistence/sqlite_replay_ledger_schema_contract.cpp").read_text(
                encoding="utf-8", errors="strict"),
        "cross_row_aliases_are_rejected",
        "one prepared effect and one protocol nonce identity must not acquire multiple replay reservations",
    )
    require(
        checks,
        "staged_ingress_sender_replay_nonce_keys_.clear();" in ledger and
        ledger.find("staged_ingress_sender_replay_nonce_keys_.clear();") <
        ledger.find("Stmt stmt(db_, \"SELECT sequence"),
        "reload_clears_ephemeral_nonce_state",
        "restart reconstruction must not retain staged nonce authority from an earlier in-memory state",
    )
    require(
        checks,
        "is_replay_printable_token" not in ledger and
        "is_sender_nonce_for_ledger" not in ledger and
        "ingress_sender_replay_issued_at_epoch" not in ledger,
        "legacy_duplicate_validation_is_absent",
        "the replay ledger must not retain a second field-by-field validator or the former flattened record",
    )
    require(
        checks,
        "observed_at_epoch - evidence.issued_at_epoch" in boundary and
        "issued_at_epoch - evidence.observed_at_epoch" in boundary and
        "observed_at_epoch +" not in boundary,
        "time_window_checks_are_overflow_safe",
        "hostile signed 64-bit SQLite INTEGER values must not trigger arithmetic overflow",
    )
    require(
        checks,
        "prepared_binding_mismatch" in header and
        "record.prepared.sequence != expected_prepared.sequence" in boundary and
        "record.prepared.entry_hash != expected_prepared.entry_hash" in boundary and
        "record.prepared.effect_idempotency_key !=" in boundary,
        "prepared_binding_compares_complete_tuple",
        "sequence, entry hash, and idempotency key must all match reconstructed decision evidence",
    )
    require(
        checks,
        "sqlite3_" not in boundary,
        "pure_semantic_owner_has_no_sqlite_authority",
        "the focused verifier must accept values, not acquire database handles or statements",
    )
    for marker, check_id in (
        ("INT64_MAX", "focused_test_covers_overflow_edges"),
        ("principal\\0hidden", "focused_test_covers_embedded_nul"),
        ("prepared sequence alias", "focused_test_covers_prepared_aliasing"),
        ("sensitive-marker", "focused_test_checks_value_free_diagnostics"),
    ):
        require(checks, marker in focused, check_id, f"focused proof marker: {marker}")
    for marker, check_id in (
        ("prepared_sequence=999", "integration_preserves_orphan_reproducer"),
        ("wrong_storage_class", "integration_rejects_numeric_coercion"),
        ("char(0)", "integration_rejects_embedded_nul"),
        ("multiple ingress sender replay rows", "integration_rejects_cross_row_alias"),
        ("restore_sqlite_snapshot_into_ledger", "integration_exercises_restore_path"),
    ):
        require(checks, marker in integration, check_id, f"integration proof marker: {marker}")

    report = {
        "format": "anonsync-ingress-sender-replay-integrity-audit-v1",
        "passed": all(item.passed for item in checks),
        "checks": [asdict(item) for item in checks],
        "metrics": {
            "boundary_lines": len(boundary.splitlines()),
            "focused_test_lines": len(focused.splitlines()),
            "integration_test_lines": len(integration.splitlines()),
            "ledger_row_scan_invocations": ledger.count(
                "verify_ingress_sender_replay_rows("
            ) - 1,
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
