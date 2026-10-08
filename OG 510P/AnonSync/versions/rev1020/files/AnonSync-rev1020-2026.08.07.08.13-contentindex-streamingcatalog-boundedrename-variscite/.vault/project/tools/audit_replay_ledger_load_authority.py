#!/usr/bin/env python3
"""Fail-closed audit for nondestructive replay-ledger load and lock lifetime."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("include/anonsync_core_internal.hpp"),
    Path("src/anonsync_core.cpp"),
    Path("src/replay_ledger.cpp"),
    Path("src/persistence/local_jsonl_replay_namespace.cpp"),
    Path("src/reporting_selftests.cpp"),
    Path("src/sqlite_replay_ledger.cpp"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def require(checks: list[Check], condition: bool, check_id: str, detail: str) -> None:
    checks.append(Check(check_id, bool(condition), detail))


def ordered(text: str, *needles: str) -> bool:
    cursor = -1
    for needle in needles:
        cursor = text.find(needle, cursor + 1)
        if cursor < 0:
            return False
    return True


def slice_between(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    stop = text.find(end, start + len(begin)) if start >= 0 else -1
    return text[start:stop] if start >= 0 and stop > start else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="AnonSync source root",
    )
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    if missing:
        report = {
            "format": "anonsync-replay-ledger-load-authority-audit-v1",
            "root": str(root),
            "passed": False,
            "passed_checks": 0,
            "total_checks": 0,
            "checks": [],
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
    internal = text[Path("include/anonsync_core_internal.hpp")]
    cli = text[Path("src/anonsync_core.cpp")]
    local = text[Path("src/replay_ledger.cpp")]
    local_namespace = text[Path("src/persistence/local_jsonl_replay_namespace.cpp")]
    selftests = text[Path("src/reporting_selftests.cpp")]
    sqlite = text[Path("src/sqlite_replay_ledger.cpp")]
    verifier = text[Path("tools/verify_release_package.py")]
    checks: list[Check] = []

    interface = slice_between(
        internal, "struct IReplayLedgerBackend", "std::unique_ptr<IReplayLedgerBackend>"
    )
    local_struct = slice_between(internal, "struct ReplayLedger", "std::pair<std::string")
    local_load = slice_between(local, "void ReplayLedger::load(", "bool ReplayLedger::contains_jti(")
    local_stage = slice_between(local, "bool ReplayLedger::stage(", "bool ReplayLedger::flush(")
    local_commit = slice_between(local, "bool ReplayLedger::commit(", "bool ReplayLedger::backup_snapshot(")
    local_close = slice_between(local, "void ReplayLedger::close(", "}  // namespace anonsync")
    sqlite_load = slice_between(
        sqlite, "void SqliteWalReplayLedger::load(", "ReplayLedgerStats SqliteWalReplayLedger::stats("
    )
    sqlite_close = slice_between(
        sqlite, "void SqliteWalReplayLedger::close(", "ReplayLedgerStats SqliteWalReplayLedger::stats("
    )

    require(
        checks,
        "bool reset" not in interface
        and "virtual void load(const std::string& ledger_path, const std::string& mode" in interface,
        "backend_interface_has_no_destructive_load_bit",
        "ordinary backend load must not carry reset authority",
    )
    require(
        checks,
        "bool reset" not in local_load and "bool reset" not in sqlite_load,
        "both_load_implementations_are_nondestructive_signatures",
        "neither backend may hide the removed Boolean in its implementation",
    )

    active_files = sorted(
        list((root / "src").rglob("*.cpp"))
        + list((root / "src").rglob("*.hpp"))
        + list((root / "include").rglob("*.hpp"))
    )
    family_delete_hits = [
        path.relative_to(root).as_posix()
        for path in active_files
        if "unlink_sqlite_family(" in path.read_text(encoding="utf-8")
    ]
    require(
        checks,
        not family_delete_hits,
        "whole_sqlite_family_delete_authority_is_absent",
        "active production source must contain no ordinary family deletion primitive",
    )
    require(
        checks,
        all(token not in local_load for token in ("std::remove", "::unlink(", "rename(")),
        "local_load_performs_no_delete_or_replace",
        "opening a local ledger may acquire and verify but never erase or replace",
    )
    require(
        checks,
        all(token not in sqlite_load for token in ("std::remove", "::unlink(", "rename(")),
        "sqlite_load_performs_no_delete_or_replace",
        "opening a SQLite ledger may acquire and verify but never erase or replace",
    )

    private_at = local_struct.find("private:")
    release_at = local_struct.find("void release_lock() noexcept;")
    require(
        checks,
        private_at >= 0 and release_at > private_at,
        "local_lock_release_is_private",
        "callers cannot detach kernel serialization while leaving the object enabled",
    )
    require(
        checks,
        "ReplayLedger::~ReplayLedger()" in local
        and ordered(local, "ReplayLedger::~ReplayLedger()", "close();"),
        "local_destructor_uses_the_authority_expiry_path",
        "destruction and explicit close must share one lifetime transition",
    )
    require(
        checks,
        bool(local_load)
        and ordered(
            local_load,
            "close();",
            "if (ledger_path.empty())",
            "if (mode != \"immediate\" && mode != \"batch\")",
            "enabled = true;",
            "acquire_lock();",
        ),
        "local_reload_expires_old_authority_before_validation",
        "even an invalid or disabled replacement load must first release prior ownership",
    )
    require(
        checks,
        ordered(local_load, "if (ledger_path.empty())", "path.clear();", "lock_path.clear();", "return;"),
        "explicit_empty_load_clears_capability_identity",
        "the intentionally disabled state must be distinguishable from a closed path-bound object",
    )
    require(
        checks,
        "try {" in local_load
        and ordered(local_load, "try {", "acquire_lock();", "recover_or_reject_journal();", "} catch (...) {", "close();", "throw;"),
        "local_rejected_load_expires_new_partial_authority",
        "parse, journal, or path rejection cannot leave a live lock-backed object",
    )
    require(
        checks,
        bool(local_close) and ordered(local_close, "enabled = false;", "release_lock();"),
        "local_close_revokes_before_unlock",
        "the visible enabled bit expires before another process can acquire the kernel lock",
    )
    require(
        checks,
        "if (!enabled)" in local_stage
        and "if (!path.empty())" in local_stage
        and "durable replay ledger authority is closed" in local_stage
        and "return false;" in local_stage,
        "closed_local_stage_fails_instead_of_reporting_durability",
        "a revoked path-bound object cannot convert a skipped write into success",
    )
    require(
        checks,
        "if (!enabled)" in local_commit
        and "if (!path.empty())" in local_commit
        and "durable replay ledger authority is closed" in local_commit
        and "return false;" in local_commit,
        "closed_local_commit_fails_instead_of_reporting_durability",
        "a revoked path-bound object cannot convert a skipped flush into success",
    )
    require(
        checks,
        "LOCK_EX | LOCK_NB" in local_namespace
        and "::openat(directory_authority_.descriptor_no_verify()" in local_namespace
        and "regular_open_flags(O_RDWR" in local_namespace
        and "O_NOFOLLOW" in local_namespace
        and "O_CLOEXEC" in local_namespace
        and "O_NONBLOCK" in local_namespace
        and "validate_opened_regular_or_throw" in local_namespace
        and "S_ISREG" in local_namespace
        and "st_nlink != 1" in local_namespace
        and "::fstat(" in local_namespace,
        "local_lock_acquisition_is_nonblocking_and_nofollow",
        "the local serialization capability is explicit and hardened against final-component symlinks, special files, and multiple links",
    )

    require(
        checks,
        bool(sqlite_load)
        and ordered(sqlite_load, "close();", "if (ledger_path.empty())", "write_gate_ = std::make_unique"),
        "sqlite_reload_expires_old_authority_before_new_gate",
        "the SQLite backend cannot overlap old and new write-gate ownership",
    )
    require(
        checks,
        "SqliteReplayLedgerWriteGate" in sqlite_load
        and "write_gate_" in sqlite_load,
        "sqlite_load_consumes_the_extracted_write_gate_owner",
        "ordinary runtime writes and administrative reset serialize through one capability",
    )
    require(
        checks,
        bool(sqlite_close)
        and ordered(sqlite_close, "db_.reset();", "enabled_ = false;", "write_gate_.reset();"),
        "sqlite_close_revokes_before_gate_release",
        "the database handle closes and enabled state expires before the write gate is released",
    )

    require(
        checks,
        "--ledger-reset was removed because ordinary open must not mint destructive authority" in cli,
        "legacy_reset_flag_has_an_explicit_denial",
        "operators receive a stable explanation rather than a silently ignored destructive flag",
    )
    denial_at = cli.find("--ledger-reset was removed because ordinary open must not mint destructive authority")
    require(
        checks,
        denial_at >= 0 and "return 64;" in cli[denial_at : denial_at + 500],
        "legacy_reset_flag_returns_usage_failure",
        "removed destructive syntax must fail closed with a non-success status",
    )

    for needle, check_id, detail in (
        ("backend interface close retained enabled authority", "selftest_proves_close_revocation", "close must clear enabled authority"),
        ("closed authority reported a durable stage success", "selftest_proves_closed_stage_denial", "post-close stage must not claim success"),
        ("empty load retained stale authority or path", "selftest_proves_active_to_disabled_transition", "load of the empty path must release and clear prior identity"),
        ("rejected reload retained enabled authority", "selftest_proves_rejected_reload_cleanup", "a failed replacement load must leave the object disabled"),
        ("rejected reload reported a durable commit success", "selftest_proves_rejected_reload_commit_denial", "post-rejection commit must not claim durability"),
        ("ordinary reopen destructively changed prior rows", "selftest_proves_sqlite_reopen_preservation", "ordinary SQLite reopen must preserve prior rows"),
    ):
        require(checks, needle in selftests, check_id, detail)

    require(
        checks,
        "anonsync_core_ledger_backend_interface_selftest" in cmake
        and "--selftest-ledger-backend-interface" in cmake,
        "local_lifetime_oracle_is_in_ctest",
        "the executable capability proof must remain a release-gate obligation",
    )
    require(
        checks,
        "anonsync_replay_ledger_load_authority_source_audit" in cmake
        and "audit_replay_ledger_load_authority.py" in cmake,
        "this_source_audit_is_in_ctest",
        "source-shape authority checks must not rely on manual invocation",
    )
    require(
        checks,
        '"tools/audit_replay_ledger_load_authority.py"' in verifier,
        "release_verifier_requires_this_audit",
        "a sealed cube cannot omit the load-authority audit",
    )

    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-replay-ledger-load-authority-audit-v1",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
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
