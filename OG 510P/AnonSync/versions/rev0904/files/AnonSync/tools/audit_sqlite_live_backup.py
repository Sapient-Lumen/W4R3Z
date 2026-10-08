#!/usr/bin/env python3
"""Fail-closed audit for bounded, snapshot-pinned SQLite live backup authority."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/persistence/sqlite_snapshot_geometry.hpp"),
    Path("src/persistence/sqlite_snapshot_geometry.cpp"),
    Path("src/persistence/sqlite_live_backup.hpp"),
    Path("src/persistence/sqlite_live_backup.cpp"),
    Path("src/persistence/sqlite_snapshot_seal.cpp"),
    Path("tests/persistence/sqlite_live_backup_tests.cpp"),
    Path("tools/verify_release_package.py"),
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
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    if missing:
        report = {
            "format": "anonsync-sqlite-live-backup-audit-v1",
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

    text = {path: (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    cmake = text[Path("CMakeLists.txt")]
    header = text[Path("src/persistence/sqlite_live_backup.hpp")]
    owner = text[Path("src/persistence/sqlite_live_backup.cpp")]
    geometry_hpp = text[Path("src/persistence/sqlite_snapshot_geometry.hpp")]
    geometry_cpp = text[Path("src/persistence/sqlite_snapshot_geometry.cpp")]
    seal = text[Path("src/persistence/sqlite_snapshot_seal.cpp")]
    focused = text[Path("tests/persistence/sqlite_live_backup_tests.cpp")]
    verifier = text[Path("tools/verify_release_package.py")]
    checks: list[Check] = []

    live_link = re.search(
        r"target_link_libraries\(anonsync_sqlite_live_backup(?P<body>.*?)\)",
        cmake,
        re.S,
    )
    seal_link = re.search(
        r"target_link_libraries\(anonsync_sqlite_snapshot_seal(?P<body>.*?)\)",
        cmake,
        re.S,
    )
    core = re.search(r"set\(ANONSYNC_CORE_SOURCES(?P<body>.*?)\)\s*foreach\(", cmake, re.S)
    require(
        checks,
        "add_library(anonsync_sqlite_live_backup STATIC" in cmake
        and live_link is not None
        and all(name in live_link.group("body") for name in (
            "anonsync_sqlite_exact_value",
            "anonsync_process_incarnation",
            "anonsync_sqlite_snapshot_geometry",
        )),
        "live_backup_is_independent_production_owner",
        "the copy protocol and its evidence dependencies must remain separately linkable",
    )
    require(
        checks,
        core is not None and "sqlite_live_backup.cpp" not in core.group("body"),
        "live_backup_source_is_not_reabsorbed_by_core",
        "the bounded protocol must not become a private monolith helper",
    )
    require(
        checks,
        seal_link is not None and "anonsync_sqlite_live_backup" in seal_link.group("body")
        and "copy_sqlite_live_snapshot_bounded_or_throw" in seal
        and all(token not in seal for token in (
            "sqlite3_backup_init", "sqlite3_backup_step", "sqlite3_backup_finish"
        )),
        "snapshot_seal_delegates_raw_backup_lifecycle",
        "the seal consumes one reviewed owner and contains no second backup protocol",
    )
    require(
        checks,
        "add_executable(anonsync_sqlite_live_backup_test" in cmake
        and "add_test(NAME anonsync_sqlite_live_backup_test" in cmake
        and "anonsync_sqlite_live_backup_source_audit" in cmake
        and "anonsync_sqlite_live_backup_test" in cmake[cmake.find("focused persistence boundary"):],
        "focused_test_and_source_audit_are_release_gates",
        "the owner must retain a no-core executable oracle and structural CTest obligation",
    )

    require(
        checks,
        "kSqliteLiveBackupPagesPerStep = 64U" in header
        and "static_cast<int>(kSqliteLiveBackupPagesPerStep)" in owner
        and "sqlite3_backup_step" in owner
        and "sqlite3_backup_step(backup, -1)" not in owner
        and "sqlite3_backup_step(backup, -1)" not in seal,
        "backup_effects_are_fixed_size_not_unbounded",
        "no production live-copy call may request all remaining pages in one effect",
    )
    require(
        checks,
        'sqlite3_get_autocommit(source_database) == 0' in owner
        and 'sqlite3_txn_state(source_database, "main") != SQLITE_TXN_NONE' in owner
        and 'sqlite3_txn_state(destination, "main") != SQLITE_TXN_NONE' in owner,
        "explicit_and_implicit_entry_transactions_are_rejected",
        "the owner must acquire a fresh source snapshot and an unused destination",
    )
    begin = owner.find('source_database, "BEGIN;"')
    page_size = owner.find('"PRAGMA main.page_size;"', begin)
    page_count = owner.find('"PRAGMA main.page_count;"', page_size)
    geometry = owner.find("verify_sqlite_snapshot_page_geometry_or_throw", page_count)
    backup_init = owner.find("sqlite3_backup_init", geometry)
    require(
        checks,
        min(begin, page_size, page_count, geometry, backup_init) >= 0
        and begin < page_size < page_count < geometry < backup_init,
        "geometry_is_authorized_inside_pinned_read_snapshot",
        "policy evidence must be sampled after BEGIN and before backup initialization",
    )
    require(
        checks,
        "verify_pinned_source_or_throw(source_database, label)" in owner
        and owner.count("verify_pinned_source_or_throw(source_database, label)") >= 3
        and "SQLITE_TXN_READ" in owner,
        "read_snapshot_authority_is_reasserted_at_cutpoints",
        "entry, each step, and post-observer state must remain the same read transaction",
    )
    require(
        checks,
        "current_sync_process_incarnation_noexcept" in owner
        and "require_sync_process_incarnation_or_fail_stop" in owner,
        "process_incarnation_is_checked_each_step",
        "an inherited SQLite handle cannot continue the parent's backup protocol",
    )
    require(
        checks,
        "sqlite3_backup_pagecount" in owner
        and "sqlite3_backup_remaining" in owner
        and "observed_page_count != expected_page_count" in owner
        and "observed_remaining >= previous_remaining" in owner,
        "sqlite_step_evidence_is_exact_and_monotone",
        "restart, page-count drift, and non-progress must deny further effects",
    )
    require(
        checks,
        "maximum_step_calls" in owner
        and "step_index <= maximum_step_calls" in owner
        and "exceeded its derived step ceiling" in owner,
        "page_geometry_derives_a_finite_step_ceiling",
        "even anomalous SQLite progress cannot create an unbounded loop",
    )
    observer_call = owner.find("observer(observation, observer_context)")
    post_observer_pin = owner.find("verify_pinned_source_or_throw(source_database, label)", observer_call)
    done_branch = owner.find("if (step_rc == SQLITE_DONE)", observer_call)
    require(
        checks,
        observer_call >= 0 and post_observer_pin > observer_call
        and done_branch > post_observer_pin,
        "observer_cutpoint_cannot_silently_remove_snapshot_authority",
        "the deterministic cutpoint is followed by a pin proof before completion or another effect",
    )
    require(
        checks,
        "completed destination geometry" in owner
        and "destination_geometry != evidence.source_geometry" in owner
        and owner.find("sqlite3_backup_finish", owner.find("if (step_rc == SQLITE_DONE)"))
            < owner.find("completed destination geometry"),
        "completed_destination_reproduces_pinned_geometry",
        "backup completion alone is not accepted without exact destination page evidence",
    )
    require(
        checks,
        "struct CleanupResult" in owner
        and "cleanup_after_failure" in owner
        and "noexcept" in owner[owner.find("CleanupResult cleanup_after_failure"):owner.find("std::string cleanup_failure_text")]
        and "std::string" not in owner[owner.find("CleanupResult cleanup_after_failure"):owner.find("std::string cleanup_failure_text")]
        and 'sqlite3_exec(source, "ROLLBACK;"' in owner,
        "failure_cleanup_performs_nonallocating_finish_and_rollback",
        "diagnostic allocation must not interrupt release of backup and source transaction authority",
    )

    require(
        checks,
        "validate_sqlite_snapshot_geometry_policy_or_throw" in geometry_hpp
        and "verify_sqlite_snapshot_page_geometry_or_throw" in geometry_hpp
        and "may tighten but not widen" in geometry_cpp,
        "adjacent_boundaries_share_one_monotone_geometry_policy",
        "preflight, pinned copy, and byte verification cannot interpret limits differently",
    )
    for marker, check_id in (
        ("bounded backup did not expose multiple fixed-size steps", "fixed_step_progress_oracle"),
        ("concurrent writer did not grow the durable source beyond policy", "concurrent_growth_oracle"),
        ("lost its pinned source read transaction", "lost_pin_oracle"),
        ("aborted live backup retained a partial destination image", "partial_destination_rollback_oracle"),
        ("source database has an active implicit transaction", "implicit_transaction_oracle"),
    ):
        require(checks, marker in focused, check_id, f"focused corpus marker present: {marker}")
    require(
        checks,
        all(path in verifier for path in (
            "src/persistence/sqlite_live_backup.hpp",
            "src/persistence/sqlite_live_backup.cpp",
            "tests/persistence/sqlite_live_backup_tests.cpp",
            "tools/audit_sqlite_live_backup.py",
        )),
        "release_verifier_requires_owner_and_proofs",
        "a sealed archive cannot omit the new implementation, oracle, or audit",
    )

    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sqlite-live-backup-audit-v1",
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": {
            "owner_lines": len(owner.splitlines()),
            "test_lines": len(focused.splitlines()),
            "raw_backup_step_calls": owner.count("sqlite3_backup_step"),
            "pin_reassertions": owner.count("verify_pinned_source_or_throw(source_database, label)"),
        },
        "violations": violations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
