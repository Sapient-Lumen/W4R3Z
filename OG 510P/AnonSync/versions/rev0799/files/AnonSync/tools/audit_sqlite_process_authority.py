#!/usr/bin/env python3
"""Audit AnonSync's live-process SQLite capability boundary.

This is a deterministic source-shape and inventory audit.  It does not claim
that lexical evidence proves runtime behavior; the fork-adversarial executables
and CTest lanes are separate release requirements.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}
SKIP_PARTS = {"third_party", ".git", "REVISION_EVIDENCE", "evidence", "audit"}


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


def function_body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    brace = text.find("{", start)
    if brace < 0:
        return ""
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[brace : index + 1]
    return ""


def ordered(text: str, *needles: str) -> bool:
    position = -1
    for needle in needles:
        position = text.find(needle, position + 1)
        if position < 0:
            return False
    return True


def source_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for top in ("include", "src", "tests", "fuzz"):
        base = root / top
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
                continue
            rel = path.relative_to(root)
            if any(part in SKIP_PARTS or part.startswith("build") for part in rel.parts):
                continue
            result.append(rel)
    return result


def line_inventory(root: Path, files: list[Path], pattern: re.Pattern[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for rel in files:
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), 1):
            code = line.split("//", 1)[0]
            match = pattern.search(code)
            if match:
                rows.append(
                    {
                        "path": rel.as_posix(),
                        "line": line_number,
                        "name": match.group(1) if match.groups() else "",
                        "text": line.strip()[:360],
                    }
                )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    sensitive = [
        Path("CMakeLists.txt"),
        Path("src/sync_sqlite_process_incarnation.hpp"),
        Path("src/sync_sqlite_process_incarnation.cpp"),
        Path("src/sync_sqlite_handle_slot.hpp"),
        Path("src/sync_sqlite_handle_slot.cpp"),
        Path("src/sync_sqlite_support.hpp"),
        Path("src/sync_sqlite_connection_authority.hpp"),
        Path("src/sync_sqlite_connection_authority.cpp"),
        Path("src/sync_sqlite_connection_authority_internal.hpp"),
        Path("src/sync_sqlite_mutex_capability.cpp"),
        Path("src/sync_sqlite_transaction.cpp"),
        Path("src/sync_peer_ingress_payload_store.cpp"),
        Path("src/sqlite_replay_ledger.cpp"),
        Path("tests/sqlite_process_authority_fork_test.cpp"),
        Path("tests/sqlite_connection_authority_test.cpp"),
    ]
    missing = [rel.as_posix() for rel in sensitive if not (root / rel).is_file()]
    if missing:
        report = {
            "format": "anonsync-sqlite-process-authority-audit-v3",
            "passed": False,
            "violations": [f"missing sensitive file: {path}" for path in missing],
        }
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 2

    texts = {rel: (root / rel).read_text(encoding="utf-8") for rel in sensitive}
    cmake = texts[Path("CMakeLists.txt")]
    process_hpp = texts[Path("src/sync_sqlite_process_incarnation.hpp")]
    process_cpp = texts[Path("src/sync_sqlite_process_incarnation.cpp")]
    slot_hpp = texts[Path("src/sync_sqlite_handle_slot.hpp")]
    slot_cpp = texts[Path("src/sync_sqlite_handle_slot.cpp")]
    support_hpp = texts[Path("src/sync_sqlite_support.hpp")]
    authority_hpp = texts[Path("src/sync_sqlite_connection_authority.hpp")]
    authority_cpp = texts[Path("src/sync_sqlite_connection_authority.cpp")]
    authority_internal = texts[Path("src/sync_sqlite_connection_authority_internal.hpp")]
    mutex_cpp = texts[Path("src/sync_sqlite_mutex_capability.cpp")]
    transaction_cpp = texts[Path("src/sync_sqlite_transaction.cpp")]
    payload_cpp = texts[Path("src/sync_peer_ingress_payload_store.cpp")]
    replay_cpp = texts[Path("src/sqlite_replay_ledger.cpp")]
    fork_test = texts[Path("tests/sqlite_process_authority_fork_test.cpp")]
    authority_test = texts[Path("tests/sqlite_connection_authority_test.cpp")]

    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    for source in (
        "src/sync_sqlite_process_incarnation.cpp",
        "src/sync_sqlite_handle_slot.cpp",
        "src/sync_sqlite_mutex_capability.cpp",
        "src/sync_sqlite_transaction.cpp",
        "src/sync_sqlite_connection_authority.cpp",
    ):
        require(source in cmake, f"linked_{Path(source).stem}", f"{source} must remain linked into the shared SQLite boundary")
    require("anonsync_sqlite_process_authority_fork_test" in cmake, "fork_test_registered", "the fork-adversarial executable must remain compiled and registered")

    require("using SyncSqliteProcessId = std::uint64_t" in process_hpp, "process_identity_has_named_type", "live process authority must use one explicit nonserializable type")
    require("kSyncSqliteCapabilityViolationExitCode = 86" in process_hpp, "fail_stop_exit_is_stable", "adversarial tests and operators need one stable violation status")
    require("::getpid()" in process_cpp or "::_getpid()" in process_cpp, "process_identity_reads_kernel_pid", "process identity must be reacquired at use time")
    process_fail_stop = function_body(process_cpp, "[[noreturn]] void fail_stop_on_sync_sqlite_capability_violation_noexcept()")
    require("std::_Exit(kSyncSqliteCapabilityViolationExitCode)" in process_fail_stop, "process_violation_uses_unhookable_exit", "a capability violation must bypass terminate and atexit handlers")
    require("std::terminate" not in process_cpp, "process_boundary_has_no_terminate_path", "replaceable terminate handlers must not own fail-stop policy")

    require("class ProcessBoundHandleSlot final" in slot_hpp, "typed_owner_slot_exists", "connection and statement ownership share one invariant-owned abstraction")
    require("class ProcessBoundHandleOutGuard final" in slot_hpp, "scoped_output_guard_exists", "SQLite output parameters must be adopted at full-expression completion")
    require("SyncSqliteDbHandlePolicy" in slot_hpp and "SyncSqliteStmtHandlePolicy" in slot_hpp, "connection_and_statement_policies_share_slot", "both SQLite owner kinds must use the same process fence")
    require(
        "sqlite3_get_autocommit(handle) == 0" in slot_cpp
        and "sqlite3_close(handle)" in slot_cpp
        and "sqlite3_close_v2(handle)" not in slot_cpp,
        "connection_disposal_is_strict",
        "connection disposal must reject open transactions and SQLite zombie-close semantics",
    )
    require("sqlite3_finalize(handle)" in slot_cpp, "statement_disposal_uses_finalize", "statement ownership must finalize exactly once")
    require("operator Handle**" in slot_hpp and "adopt_output_noexcept" in slot_hpp, "output_guard_adopts_error_handles", "non-null handles returned on SQLite error must still become owned")
    require("output_pending" in slot_hpp and "output acquisition is already pending" in slot_hpp, "simultaneous_output_guards_are_rejected", "two output parameters cannot race to own one slot")
    require("class ProcessBoundHandleBorrow final" in slot_hpp, "typed_generation_borrow_exists", "dependent work must be able to retain an exact owner generation")
    require(
        "const SyncSqliteProcessId state_process_id" in slot_hpp
        and "state_->state_process_id != process_id_" in slot_hpp,
        "shared_owner_storage_is_process_bound",
        "even closed or null-output shared ownership storage must retain immutable process provenance",
    )
    require(not re.search(r"\b(?:adopt|release|put)\s*\(\s*Handle\s*\*", slot_hpp), "no_public_raw_owner_adoption", "the owner slot exposes no raw-pointer laundering API")
    guarded_slot_functions = (
        ("Handle* get() const noexcept", "get_checks_process"),
        ("void dispose_owned_noexcept() noexcept", "destruction_checks_process"),
        ("void begin_output_or_throw()", "output_acquisition_checks_process"),
    )
    for signature, check_id in guarded_slot_functions:
        body = function_body(slot_hpp, signature)
        require(
            "ProcessBoundHandleStateGuard<Policy> guard" in body,
            check_id,
            f"{signature} must enter the process-aware state guard before ownership use",
        )
    move_body = function_body(
        slot_hpp, "void transfer_from_noexcept(ProcessBoundHandleSlot& other)")
    require(
        "other.require_current_if_owned_noexcept()" in move_body,
        "move_checks_process",
        "owner movement must validate the source process before moving shared state",
    )

    require(
        "SyncSqliteDbHandleSlot db;" in support_hpp
        and "SyncSqliteStmtHandleSlot statement_owner_;" in support_hpp
        and "HandleView stmt;" in support_hpp,
        "common_support_uses_typed_slots",
        "common RAII wrappers must keep raw SQLite ownership in private process-bound slots",
    )
    require("SyncSqliteDbHandleSlot db_;" in replay_cpp, "replay_ledger_long_lived_owner_is_fenced", "the long-lived WAL ledger connection must fail-stop if inherited")
    require("SyncSqliteStmtHandleSlot stmt;" in replay_cpp, "replay_ledger_statement_owner_is_fenced", "internal prepared statements must share the same owner policy")

    for text, marker, check_id, detail in (
        (authority_hpp, "SyncSqliteProcessId process_id_", "proof_and_lease_carry_process", "connection proofs and leases must carry their minting process"),
        (authority_internal, "SyncSqliteProcessId process_id", "transaction_boundary_carries_process", "transaction boundary proofs must carry process authority"),
        (transaction_cpp, "process_id_(current_sync_sqlite_process_id_noexcept())", "transaction_guard_is_process_stamped", "typed transactions must record their creation process"),
        (mutex_cpp, "SyncSqliteProcessId process_id", "retained_mutex_state_is_process_stamped", "SQLite-owned lifetime sentinels must reject child-side use"),
        (payload_cpp, "process_id_(current_sync_sqlite_process_id_noexcept())", "payload_savepoint_is_process_stamped", "rollback cleanup must not execute SQLite in an inheriting child"),
        (replay_cpp, "class SqliteRestoreLock", "restore_lock_is_present", "restore serialization remains explicit"),
        (replay_cpp, "class SqliteWriteGateLock", "write_gate_is_present", "writer serialization remains explicit"),
    ):
        require(marker in text, check_id, detail)

    restore_destructor = function_body(replay_cpp, "~SqliteRestoreLock()")
    write_gate_destructor = function_body(replay_cpp, "~SqliteWriteGateLock()")
    require(ordered(restore_destructor, "sync_sqlite_process_id_is_current", "release_flocked_descriptor_noexcept"), "restore_lock_destructor_checks_before_close", "an inherited destructor must not mutate the parent's lock lifetime")
    require(ordered(write_gate_destructor, "sync_sqlite_process_id_is_current", "release_flocked_descriptor_noexcept"), "write_gate_destructor_checks_before_close", "an inherited write-gate destructor must fail before close or TLS mutation")
    tls_body = function_body(replay_cpp, "current_process_held_sqlite_write_gate_paths()")
    require(ordered(tls_body, "current_sync_sqlite_process_id_noexcept", "state.process_id != current", "state.paths.clear()", "state.process_id = current"), "fork_copied_lock_recursion_is_discarded", "copied thread-local recursion evidence cannot authorize a child-side nested lock")

    require("fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept" in mutex_cpp, "mutex_violation_has_named_fail_stop", "thread and close-order violations share an explicit direct-exit primitive")
    require("std::terminate" not in mutex_cpp, "mutex_boundary_has_no_terminate_path", "a hostile terminate handler cannot intercept a SQLite mutex violation")
    require("hostile_affinity_terminate_handler" in authority_test and "kHostileTerminateExit" in authority_test, "mutex_tests_install_hostile_terminate_handler", "tests distinguish direct fail-stop from terminate-handler execution")

    required_fork_markers = [
        "child cannot read an inherited connection owner",
        "child cannot finalize an inherited statement owner",
        "child cannot move an inherited connection owner",
        "child destructor cannot close an inherited connection",
        "child can create and destroy a child-local connection",
        "an empty pre-fork slot may mint a child-local connection",
        "child cannot acquire authority from an inherited proof",
        "child cannot destroy an inherited authority lease",
        "child cannot destruct an inherited live transaction",
        "child cannot inspect inherited materialized owner storage",
        "child cannot move inherited materialized owner storage",
        "child destructor cannot release an inherited empty shared-state owner",
        "hostile_terminate_handler",
        "hostile_atexit_handler",
    ]
    for index, marker in enumerate(required_fork_markers, 1):
        require(marker in fork_test, f"fork_scenario_{index:02d}_is_present", f"fork test must retain scenario: {marker}")
    require("inherited recursion evidence" in replay_cpp and "inherited destructor did not fail stop" in replay_cpp, "file_lock_fork_scenarios_are_present", "file-lock ownership and copied TLS recursion must have executable probes")

    files = source_files(root)
    raw_declarations = line_inventory(root, files, re.compile(r"\bsqlite3(?:_stmt)?\s*\*\s*([A-Za-z_]\w*)"))
    raw_open_outputs = line_inventory(root, files, re.compile(r"\bsqlite3_open(?:16|_v2)?\s*\([^;]*&\s*([A-Za-z_]\w*)"))
    raw_prepare_outputs = line_inventory(root, files, re.compile(r"\bsqlite3_prepare(?:16)?_v[23]\s*\([^;]*&\s*([A-Za-z_]\w*)"))
    raw_header_fields = [
        row for row in raw_declarations
        if row["path"].endswith((".h", ".hpp", ".hh", ".hxx"))
        and re.search(r"\b[A-Za-z_]\w*_\s*(?:=\s*nullptr)?\s*;", str(row["text"]))
    ]

    residuals = [
        {
            "severity": "high",
            "id": "raw_borrowed_handle_laundering",
            "detail": "Raw sqlite3* compatibility overloads remain. The exact-generation borrow now protects migrated statements, transactions, and helpers, but a caller that caches a raw pointer beyond the borrow lifetime can still bypass owner revocation. Continue removing raw overloads at invariant-owned module boundaries.",
        },
        {
            "severity": "medium",
            "id": "stack_scoped_raw_sqlite_helpers",
            "detail": "Several replay-ledger and selftest helpers still open/finalize raw local SQLite handles. They are short-lived rather than long-lived members, but a fork in the middle of such a call is not made safe by rev0785.",
        },
        {
            "severity": "medium",
            "id": "post_fork_runtime_scope",
            "detail": "Child-local reopen tests assume a controlled single-threaded fork path. After fork from a multithreaded process, POSIX permits only async-signal-safe operations until exec; AnonSync does not claim arbitrary C++ or SQLite work is safe in that interval.",
        },
        {
            "severity": "low",
            "id": "pid_is_live_memory_only",
            "detail": "SyncSqliteProcessId is intentionally a live-memory PID fence, not restart or serialized authority. Durable authority remains evidence-based and must be reconstructed after process restart.",
        },
    ]

    passed = all(check.passed for check in checks)
    report = {
        "format": "anonsync-sqlite-process-authority-audit-v3",
        "passed": passed,
        "check_count": len(checks),
        "passed_check_count": sum(check.passed for check in checks),
        "checks": [asdict(check) for check in checks],
        "violations": [check.detail for check in checks if not check.passed],
        "sensitive_file_sha256": {rel.as_posix(): sha256_file(root / rel) for rel in sensitive},
        "inventory": {
            "source_files": len(files),
            "raw_sqlite_pointer_declarations": raw_declarations,
            "raw_sqlite_pointer_declaration_count": len(raw_declarations),
            "raw_header_field_candidates": raw_header_fields,
            "raw_header_field_candidate_count": len(raw_header_fields),
            "raw_open_output_candidates": raw_open_outputs,
            "raw_open_output_candidate_count": len(raw_open_outputs),
            "raw_prepare_output_candidates": raw_prepare_outputs,
            "raw_prepare_output_candidate_count": len(raw_prepare_outputs),
        },
        "residual_risks": residuals,
        "interpretation": [
            "A lexical pass is not behavioral proof; compilation and fork-adversarial execution remain required.",
            "A raw sqlite3* declaration may be a borrowed API parameter rather than an owner; candidates are retained for manual review.",
            "The audit intentionally reports unresolved raw-borrow boundaries instead of treating the new owner slot as universal coverage.",
        ],
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
