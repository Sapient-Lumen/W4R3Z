#!/usr/bin/env python3
"""Fail-closed source audit for source-first SQLite ownership transfer.

SQLite close/finalize may invoke application callbacks.  A move assignment must
therefore validate and escrow its source before destroying the destination, and
the destination's close/finalize transition must be fenced against reentrant
inspection or mutation.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_sqlite_handle_slot.hpp"),
    Path("src/sync_sqlite_support.hpp"),
    Path("src/sync_sqlite_support.cpp"),
    Path("tests/sqlite_source_first_move_test.cpp"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def section(text: str, start: str, end: str) -> str:
    begin = text.find(start)
    finish = text.find(end, begin + len(start)) if begin >= 0 else -1
    return text[begin:finish] if begin >= 0 and finish > begin else ""


def ordered(text: str, *markers: str) -> bool:
    cursor = 0
    for marker in markers:
        cursor = text.find(marker, cursor)
        if cursor < 0:
            return False
        cursor += len(marker)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path,
                        default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    missing = [p.as_posix() for p in REQUIRED if not (root / p).is_file()]
    if missing:
        report = {
            "format": "anonsync-sqlite-source-first-move-audit-v1",
            "passed": False,
            "violations": [f"missing required file: {p}" for p in missing],
        }
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 2

    cmake = (root / REQUIRED[0]).read_text(encoding="utf-8")
    slot = (root / REQUIRED[1]).read_text(encoding="utf-8")
    support_hpp = (root / REQUIRED[2]).read_text(encoding="utf-8")
    support_cpp = (root / REQUIRED[3]).read_text(encoding="utf-8")
    test = (root / REQUIRED[4]).read_text(encoding="utf-8")

    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    state = section(slot, "struct ProcessBoundHandleState final", "template <typename Policy>\nclass ProcessBoundHandleStateGuard")
    require("bool disposal_pending = false;" in state,
            "disposal_fence_is_synchronized_owner_state",
            "close/finalize reentrancy must be represented inside lifecycle-locked shared state")
    require("disposal_pending_" not in slot,
            "no_unsynchronized_slot_disposal_flag",
            "a plain flag on the movable slot would race with concurrent owner operations")

    assignment = section(
        slot,
        "ProcessBoundHandleSlot& operator=(ProcessBoundHandleSlot&& other) noexcept",
        "[[nodiscard]] Handle* get() const noexcept",
    )
    require(ordered(assignment,
                    "other.require_current_if_owned_noexcept();",
                    "require_current_if_owned_noexcept();",
                    "std::shared_ptr<State> incoming_state = std::move(other.state_);",
                    "dispose_owned_noexcept();",
                    "state_ = std::move(incoming_state);"),
            "owner_slot_move_is_validate_escrow_dispose_install",
            "an invalid source must be rejected before destination destruction and callbacks must see an emptied source")

    dispose = section(slot, "void dispose_owned_noexcept() noexcept", "void transfer_from_noexcept")
    require(ordered(dispose,
                    "const std::shared_ptr<State> disposing_state = state_;",
                    "disposing_state->disposal_pending = true;",
                    "Policy::dispose(owned);",
                    "disposing_state->disposal_pending = false;"),
            "close_finalize_transition_is_fenced_until_return",
            "the exact shared generation must stay alive and fenced across SQLite callback execution")
    require("require_transition_idle_noexcept" in slot
            and "require_consistent_state_noexcept" in slot
            and "state_->disposal_pending || !state_->output_pending" in slot,
            "all_owner_entry_paths_reject_disposal_overlap",
            "inspection, move, reset, borrow, and C output adoption must not cross an active disposal transition")

    require("void require_transferable_noexcept() const noexcept;" in support_hpp,
            "composite_statement_has_preflight",
            "the fused database-pin/statement owner needs one no-side-effect source validation boundary")
    stmt_ctor = section(support_cpp,
                        "SyncSqliteStmt::SyncSqliteStmt(SyncSqliteStmt&& other) noexcept",
                        "SyncSqliteStmt& SyncSqliteStmt::operator=")
    require(ordered(stmt_ctor,
                    "other.require_transferable_noexcept();",
                    "SyncSqliteSerializedDbBorrow incoming_owner",
                    "SyncSqliteStmtHandleSlot incoming_statement",
                    "owner_borrow_ = std::move(incoming_owner);",
                    "statement_owner_ = std::move(incoming_statement);"),
            "statement_move_constructor_escrows_complete_source",
            "no component of a fused statement capability may transfer before the complete source validates")
    stmt_assign = section(support_cpp,
                          "SyncSqliteStmt& SyncSqliteStmt::operator=(SyncSqliteStmt&& other) noexcept",
                          "void SyncSqliteStmt::require_transferable_noexcept")
    require(ordered(stmt_assign,
                    "other.require_transferable_noexcept();",
                    "require_transferable_noexcept();",
                    "SyncSqliteSerializedDbBorrow incoming_owner",
                    "SyncSqliteStmtHandleSlot incoming_statement",
                    "reset();",
                    "owner_borrow_ = std::move(incoming_owner);",
                    "statement_owner_ = std::move(incoming_statement);"),
            "statement_move_assignment_is_source_first_and_fused",
            "finalize callbacks must run only after both source components are out of the caller-visible object")

    required_test_markers = (
        "inherited_database_source_is_rejected_before_destination_close",
        "inherited_statement_source_is_rejected_before_destination_finalize",
        "pending_output_source_is_rejected_before_destination_close",
        "destination_database_reentrancy_is_fail_stopped",
        "destination_statement_reentrancy_is_fail_stopped",
        "database_source_is_escrowed_before_close_callback",
        "statement_source_is_escrowed_before_finalize_callback",
    )
    for index, marker in enumerate(required_test_markers, 1):
        require(marker in test, f"adversarial_scenario_{index:02d}_is_present",
                f"focused executable must retain scenario: {marker}")

    require(cmake.count("anonsync_sqlite_source_first_move_test") >= 6
            and "focused persistence boundary must not depend on anonsync_core_lib" in cmake,
            "focused_executable_is_registered_and_sanitized",
            "the source-first proof must remain no-core, CTest-registered, and present in sanitizer compile/link lanes")
    require("anonsync_sqlite_source_first_move_source_audit" in cmake,
            "architecture_audit_is_registered",
            "the transfer ordering contract must be enforced by CTest")

    passed = all(c.passed for c in checks)
    report = {
        "format": "anonsync-sqlite-source-first-move-audit-v1",
        "passed": passed,
        "check_count": len(checks),
        "passed_check_count": sum(c.passed for c in checks),
        "checks": [asdict(c) for c in checks],
        "violations": [c.detail for c in checks if not c.passed],
        "metrics": {
            "slot_header_lines": len(slot.splitlines()),
            "statement_support_lines": len(support_cpp.splitlines()),
            "focused_test_lines": len(test.splitlines()),
        },
        "residual_risks": [
            "Raw sqlite3* compatibility code can still create lifetime relationships outside the typed owner graph.",
            "Fail-stop reentrancy is intentional; application callbacks must not recursively manipulate the owner whose SQLite resource is closing.",
        ],
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
