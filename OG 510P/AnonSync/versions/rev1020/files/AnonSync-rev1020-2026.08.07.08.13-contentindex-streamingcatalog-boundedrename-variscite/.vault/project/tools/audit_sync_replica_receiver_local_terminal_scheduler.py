#!/usr/bin/env python3
"""Lexical hygiene audit for the rev1006 receiver-local terminal scheduler.

Source spelling is not semantic proof. Compiler, sanitizer, runtime, stress,
reconstruction, and package evidence remain load-bearing.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("README.md"),
    Path("RECEIVER_LOCAL_TERMINAL_VERIFICATION_SCHEDULER_AUDIT_rev1006.md"),
    Path("REVISION_NOTES_rev1006.md"),
    Path("src/anonsync_sync.cpp"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("src/sync_replica_peer_service.hpp"),
    Path("src/sync_replica_peer_service.cpp"),
    Path("src/sync_replica_peer_service_status.hpp"),
    Path("src/sync_replica_peer_service_status.cpp"),
    Path("tests/sync_replica_file_payload_store_test.cpp"),
    Path("tests/sync_replica_terminal_verification_fixture.cpp"),
    Path("tools/test_anonsync_service_terminal_verification_scheduler.py"),
    Path("tools/test_anonsync_service_configuration_status.py"),
    Path("tools/test_anonsync_service_i2p_ingress.py"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    opening = text.find("{", start + len(signature))
    if opening < 0:
        return ""
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return ""


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [item.check_id for item in checks if not item.passed]
    report = {
        "format": "anonsync-receiver-local-terminal-scheduler-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove durable journal identity, bounded "
            "disk work, restart fairness, service responsiveness, SHA-256 "
            "authority, sanitizer cleanliness, or package identity"
        ),
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(item) for item in checks],
        "violations": violations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output is None:
        sys.stdout.write(rendered)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    return 0 if not violations else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    candidates = (root.parent.parent / "BOOTSTRAPROSE.md", root.parent / "BOOTSTRAPROSE.md")
    bootstrap_path = next((path for path in candidates if path.is_file()), None)
    require(bootstrap_path is not None, "release_root_bootstrap_exists", str(candidates))
    if missing or bootstrap_path is None:
        return emit(root, args.json, checks)

    texts = {path.as_posix(): (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = texts["CMakeLists.txt"]
    store_h = texts["src/sync_replica_file_payload_store.hpp"]
    store_c = texts["src/sync_replica_file_payload_store.cpp"]
    service_h = texts["src/sync_replica_peer_service.hpp"]
    service_c = texts["src/sync_replica_peer_service.cpp"]
    status_h = texts["src/sync_replica_peer_service_status.hpp"]
    status_c = texts["src/sync_replica_peer_service_status.cpp"]
    sync_main = texts["src/anonsync_sync.cpp"]
    store_test = texts["tests/sync_replica_file_payload_store_test.cpp"]
    fixture = texts["tests/sync_replica_terminal_verification_fixture.cpp"]
    process_test = texts["tools/test_anonsync_service_terminal_verification_scheduler.py"]
    config_status = texts["tools/test_anonsync_service_configuration_status.py"]
    i2p_status = texts["tools/test_anonsync_service_i2p_ingress.py"]
    structural = texts["tools/audit_sync_file_payload_store.py"]
    verifier = texts["tools/verify_release_package.py"]
    prose = "\n".join((
        texts["RECEIVER_LOCAL_TERMINAL_VERIFICATION_SCHEDULER_AUDIT_rev1006.md"],
        texts["REVISION_NOTES_rev1006.md"], texts["README.md"], bootstrap,
    ))

    scanner = store_c
    scheduler = body(
        store_c,
        "continue_one_pending_terminal_verification_or_throw()")
    status_method = body(store_c, "terminal_verification_status() const")
    service_step = body(service_c, "payload_terminal_verification_step_or_throw()")
    owner_step = body(service_c, "SyncReplicaPeerServiceOwner::run_next_or_throw()")
    append_status = body(status_c, "append_payload_terminal_verification_status(")
    sanitizer_compile_inventory = cmake.split(
        "set(ANONSYNC_SANITIZER_COMPILE_TARGETS", 1)[1].split(
            "foreach(tgt IN LISTS ANONSYNC_SANITIZER_COMPILE_TARGETS)", 1)[0]
    sanitizer_link_inventory = cmake.split(
        "foreach(tgt\n      anonsync_core", 1)[1].split(
            "target_link_options(${tgt} PRIVATE -fsanitize=address,undefined)", 1)[0]

    require(bool(scanner), "complete_store_scanner_exists", "durable work discovery has a complete scan owner")
    require(
        "terminal_verification_journals" in scanner
        and "terminal_verification_work" in scanner
        and "committed_prefix_bytes != prefix.total_size_bytes" in scanner,
        "complete_scan_discovers_only_complete_staged_obligations",
        "durable prefixes and exact usable journals produce the bounded work projection",
    )
    require(
        "verified_offset_bytes = 0U" in scanner
        and "journal->usable" in scanner
        and "state.staged_prefix_metadata == prefix_metadata" in scanner,
        "missing_stale_or_foreign_journal_restarts_conservatively",
        "journal acceleration is accepted only under exact identity and inode metadata",
    )
    require(
        "left.verified_offset_bytes <" in scanner
        and "left.content_sha256 < right.content_sha256" in scanner,
        "complete_scan_orders_work_by_frontier_then_digest",
        "selection fairness is deterministic across restart reconstruction",
    )
    require(
        "terminal_verification_observation_known = false" in store_c
        and "terminal_verification_observation_known = true" in store_c
        and "std::move(scanned.terminal_verification_work)" in store_c,
        "fresh_owner_is_unknown_until_complete_scan",
        "targeted mutation cannot manufacture global work-completeness authority",
    )
    require(
        "max_transient_entries" in store_c
        and "terminal-verification work exceeds entry budget" in store_c,
        "process_scheduler_cache_reuses_existing_transient_frontier",
        "the scheduler retains bounded metadata rather than payload bytes",
    )
    require(bool(status_method) and bool(scheduler), "store_status_and_one_step_api_exist", "owner-local scheduling API is explicit")
    require(
        "require_current_owner_or_throw" in status_method
        and "require_current_owner_or_throw" in scheduler,
        "store_scheduler_is_owner_thread_bound",
        "status and effects cannot migrate to a second scheduler thread",
    )
    require(
        "ReadOnlyInspect" in scheduler
        and "cannot advance terminal verification" in scheduler,
        "forensic_owner_cannot_run_scheduler_effects",
        "read-only inspection remains byte-cold and non-mutating",
    )
    require(
        "terminal_verification_work.front()" in scheduler
        and "continue_staged_payload_prefix_verification_or_throw" in scheduler,
        "one_step_reuses_existing_exact_terminal_verifier",
        "no second hashing or publication implementation was introduced",
    )
    require(
        "kSyncReplicaFilePayloadStoreMaximumTerminalVerificationBytesPerStep" in scheduler
        and "terminal_verification_steps != 1U" in scheduler,
        "one_local_step_is_bounded_to_one_shipping_pulse",
        "progress cannot silently consume multiple 32 MiB terminal steps",
    )
    require(
        "terminal_verification_steps == 0U" in scheduler
        and "result.hashed_bytes =" in scheduler,
        "stale_cache_reconciliation_does_not_invent_hash_work",
        "already-published payloads settle with zero byte-work accounting",
    )
    require(
        "scan_store_under_lease_or_throw" in store_c
        and "rename_noreplace_at_or_throw" in store_c,
        "final_publication_retains_complete_store_scan",
        "local scheduling never becomes namespace or publication authority",
    )
    require(
        "PayloadTerminalVerificationAdvanced" in service_h
        and "TerminalVerification" in service_c
        and bool(service_step),
        "peer_service_has_typed_receiver_local_lane",
        "integrity and lease failures retain their shared service-state handling",
    )
    require(
        "local_payload_work_ordinary_turn_due" in service_step
        and "LocalPayloadWorkKind::TerminalVerification" in service_step
        and "payload_terminal_verification_scheduler_steps" in service_step,
        "fairness_obligation_precedes_store_effect",
        "even a lease conflict forces the next owner call to yield",
    )
    require(
        "local_payload_work_ordinary_turn_due.has_value()" in owner_step
        and "local_payload_scheduler_may_run = false" in owner_step
        and "observe_folder_wake_or_throw" in owner_step
        and "refresh_ingress_worker" in owner_step,
        "service_forces_one_ordinary_turn_between_pulses",
        "control, ingress, watcher, repair, and network work retain observation opportunities",
    )
    require(
        "std::jthread" not in service_step
        and "std::thread" not in service_step
        and "std::async" not in service_step,
        "scheduler_adds_no_independent_worker_thread",
        "the receiver-local lane remains inside the existing owner loop",
    )
    require(
        '"anonsync.peer-service.status.v26"' in status_h
        and "payload_terminal_verification_scheduler_steps" in status_c
        and "payload_terminal_verification_ordinary_turn_yields" in status_c
        and "payload_terminal_verification" in sync_main,
        "status_v26_exposes_work_and_all_scheduler_counters",
        "live and terminal shipping surfaces retain exact diagnostics",
    )
    require(
        bool(append_status)
        and "unknown payload terminal-verification status carries work" in append_status
        and "status is internally inconsistent" in append_status
        and "exceeds its byte frontier" in append_status,
        "status_renderer_rejects_impossible_scheduler_projection",
        "diagnostic JSON cannot normalize contradictory internal state",
    )
    require(
        "test_receiver_local_terminal_scheduler_is_restart_fair_and_bounded" in store_test
        and "test_terminal_scheduler_stale_projection_reconciliation_reports_zero_hash" in store_test
        and "test_terminal_scheduler_stale_capacity_invalidates_without_postcommit_failure" in store_test
        and "staged-prefix scheduler cache" in store_c
        and "terminal_verification_observation_known = false" in store_c,
        "payload_store_runtime_covers_restart_fairness_and_stale_cache",
        "the focused regression exercises exact-name progress and final namespace authority",
    )
    require(
        "stage_payload_prefix_deferring_terminal_verification_or_throw" in fixture
        and "terminal_verification_steps != 0U" in fixture,
        "fixture_creates_exact_deferred_complete_prefix",
        "the real service starts from durable bytes with no prior hash pulse",
    )
    require(
        "PAYLOAD_BYTES = 2 * TERMINAL_STEP_BYTES + 4097" in process_test
        and "no peer process" in process_test
        and '"payload_terminal_verification_scheduler_steps": 3' in process_test
        and '"payload_terminal_verification_progress_steps": 2' in process_test
        and '"payload_terminal_verification_completions": 1' in process_test,
        "real_process_proves_three_local_pulses_without_peer",
        "the same ready service completes 64 MiB plus a tail locally",
    )
    require(
        "server_pid" in process_test
        and "stop_mode" in process_test
        and "status_socket.exists()" in process_test,
        "real_process_proves_owner_control_and_clean_shutdown",
        "local hashing does not hide the owner-only service lifecycle",
    )
    require(
        "require_payload_terminal_verification_status" in config_status
        and "require_payload_terminal_verification_step" in config_status
        and "anonsync.peer-service.status.v26" in config_status
        and "anonsync.peer-service.status.v26" in i2p_status,
        "existing_status_oracles_advance_with_schema_v26",
        "configured and native-I2P surfaces cannot silently retain the old contract",
    )
    require(
        "anonsync_sync_replica_terminal_verification_fixture" in cmake
        and "anonsync_sync_service_terminal_verification_scheduler_process_test" in cmake
        and "LABELS \"product\"" in cmake,
        "fixture_and_shipping_process_oracle_are_product_graph_members",
        "the new lifecycle path is not a manual-only test",
    )
    require(
        "anonsync_sync_replica_terminal_verification_fixture" in sanitizer_compile_inventory
        and "anonsync_sync_replica_terminal_verification_fixture" in sanitizer_link_inventory,
        "fixture_is_in_both_explicit_sanitizer_inventories",
        "instrumented static dependencies and the fixture final link share ASan/UBSan runtime authority",
    )
    require(
        "anonsync_sync_replica_receiver_local_terminal_scheduler_source_audit" in cmake
        and "RECEIVER_LOCAL_TERMINAL_VERIFICATION_SCHEDULER_AUDIT_rev1006.md" in verifier
        and "REVISION_NOTES_rev1006.md" in verifier
        and "rev1006" in structural,
        "release_policy_binds_complete_rev1006_slice",
        "implementation, runtime, prose, focused audit, and structural integration are mandatory",
    )
    normalized = " ".join(prose.replace("**", "").split())
    require(
        all(token in normalized for token in (
            "4 TiB", "131,072", "32 MiB", "complete payload-store scan",
            "source-side target-manifest", "single owner thread",
        )),
        "scale_cost_and_remaining_nonclaims_are_explicit",
        "peer independence is not overstated as zero disk work or complete multi-terabyte qualification",
    )
    require(
        all(token not in prose for token in (
            "VALIDATION_PENDING_REV1006", "ARCHIVE_PENDING_REV1006", "CODENAME_PENDING_REV1006",
        )),
        "final_release_placeholders_are_sealed",
        "the focused audit cannot pass before publication facts exist",
    )
    expected_archive = (
        "AnonSync-rev1006-2026.08.05.22.03-"
        "receiverlocalscheduler-restartdiscovery-ownerfairness-malachite.zip"
    )
    release_surfaces = (
        texts["RECEIVER_LOCAL_TERMINAL_VERIFICATION_SCHEDULER_AUDIT_rev1006.md"],
        texts["REVISION_NOTES_rev1006.md"], texts["README.md"], bootstrap,
    )
    require(
        all(expected_archive in surface and "malachite" in surface
            for surface in release_surfaces),
        "final_archive_identity_is_consistent_across_release_surfaces",
        "stale or divergent sealers cannot publish a different filename or codename in one required document",
    )
    self_text = Path(__file__).read_text(encoding="utf-8")
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "Source spelling is not semantic proof" in self_text
        and "Compiler, sanitizer, runtime" in self_text,
        "lexical_audit_disclaims_semantic_authority",
        "runtime and package evidence remain load-bearing",
    )
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
