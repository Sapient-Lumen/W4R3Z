#!/usr/bin/env python3
"""Lexical hygiene audit for the rev1008 source-local scheduler.

Source spelling is not semantic proof. Compiler, sanitizer, runtime,
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
    Path("SOURCE_LOCAL_MANIFEST_SCHEDULER_AND_OWNER_FAIRNESS_AUDIT_rev1008.md"),
    Path("REVISION_NOTES_rev1008.md"),
    Path("src/anonsync_sync.cpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_peer_server_owner.hpp"),
    Path("src/sync_replica_peer_server_owner.cpp"),
    Path("src/sync_replica_peer_service.hpp"),
    Path("src/sync_replica_peer_service.cpp"),
    Path("src/sync_replica_peer_service_status.hpp"),
    Path("src/sync_replica_peer_service_status.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tools/test_anonsync_service_source_manifest_scheduler.py"),
    Path("tools/test_anonsync_service_configuration_status.py"),
    Path("tools/test_anonsync_service_i2p_ingress.py"),
    Path("tools/audit_sync_replica_bounded_source_manifest_projection.py"),
    Path("tools/audit_sync_replica_receiver_local_terminal_scheduler.py"),
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
        "format": "anonsync-source-local-manifest-scheduler-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove exact payload identity, bounded disk "
            "work, owner fairness, TLS behavior, restart semantics, memory "
            "bounds, sanitizer cleanliness, or package identity"
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
    bootstrap_candidates = (
        root.parent.parent / "BOOTSTRAPROSE.md",
        root.parent / "BOOTSTRAPROSE.md",
    )
    bootstrap_path = next((path for path in bootstrap_candidates if path.is_file()), None)
    require(bootstrap_path is not None, "release_root_bootstrap_exists", str(bootstrap_candidates))
    if missing or bootstrap_path is None:
        return emit(root, args.json, checks)

    texts = {path.as_posix(): (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    reconciliation_h = texts["src/sync_replica_reconciliation_service.hpp"]
    reconciliation_c = texts["src/sync_replica_reconciliation_service.cpp"]
    server_h = texts["src/sync_replica_peer_server_owner.hpp"]
    server_c = texts["src/sync_replica_peer_server_owner.cpp"]
    peer_h = texts["src/sync_replica_peer_service.hpp"]
    peer_c = texts["src/sync_replica_peer_service.cpp"]
    status_h = texts["src/sync_replica_peer_service_status.hpp"]
    status_c = texts["src/sync_replica_peer_service_status.cpp"]
    sync_cli = texts["src/anonsync_sync.cpp"]
    runtime = texts["tests/sync_replica_reconciliation_service_test.cpp"]
    process = texts["tools/test_anonsync_service_source_manifest_scheduler.py"]
    config_status = texts["tools/test_anonsync_service_configuration_status.py"]
    i2p_status = texts["tools/test_anonsync_service_i2p_ingress.py"]
    cmake = texts["CMakeLists.txt"]
    verifier = texts["tools/verify_release_package.py"]
    structural = texts["tools/audit_sync_file_payload_store.py"]
    docs = "\n".join((
        texts["README.md"],
        texts["SOURCE_LOCAL_MANIFEST_SCHEDULER_AND_OWNER_FAIRNESS_AUDIT_rev1008.md"],
        texts["REVISION_NOTES_rev1008.md"],
        bootstrap,
    ))

    helper = body(reconciliation_c, "advance_source_content_defined_projection_or_throw(")
    local = body(reconciliation_c, "continue_source_manifest_projection_or_throw()")
    source_step = body(peer_c, "source_manifest_projection_step_or_throw()")
    owner_step = body(peer_c, "SyncReplicaPeerServiceOwner::run_next_or_throw()")
    append_projection = body(status_c, "append_source_manifest_projection_status(")

    require(
        "SyncReplicaReconciliationSourceManifestProjectionStatus" in reconciliation_h
        and all(name in reconciliation_h for name in (
            "operation_id", "content_sha256", "total_size_bytes",
            "next_offset_bytes", "completed_chunk_count")),
        "filesystem_cold_source_projection_status_is_exact",
        "status names one retained operation, payload, frontier, and completed chunk count",
    )
    require(
        "SyncReplicaOperation source_operation" in reconciliation_h
        and "source_content_defined_projection_->source_operation = operation" in helper,
        "retained_projection_keeps_exact_causal_operation",
        "local continuation does not invent a payload selector from digest alone",
    )
    require(
        "advance_source_content_defined_projection_or_throw" in reconciliation_h
        and bool(helper)
        and reconciliation_c.count("advance_source_content_defined_projection_or_throw(") >= 3,
        "network_and_local_paths_share_one_projection_helper",
        "restart, hashing, manifest construction, digest, and offsets have one implementation",
    )
    require(
        "opened.content_sha256()" in helper
        and "opened.size_bytes()" in helper
        and "opened.metadata()" in helper
        and "source_metadata ==" in helper,
        "shared_helper_reproves_content_and_inode_observation",
        "remembered projection state never substitutes for the current exact payload",
    )
    require(
        "max_source_manifest_projection_bytes_per_request_" in helper
        and "advance_content_defined_projection_or_throw" in helper,
        "every_source_pulse_reuses_the_32_mib_frontier",
        "peer-independent continuation cannot silently raise the shipping work bound",
    )
    require(
        "source_content_defined_manifest_ =" in helper
        and "SyncReplicaReconciliationCompactManifest::from_manifest_or_throw" in helper
        and "sync_replica_reconciliation_delta_manifest_digest_or_throw" in helper
        and "std::move(compact_manifest)" in helper
        and "chunk_offsets_or_throw" not in helper,
        "completion_reuses_canonical_compact_manifest_path",
        "network and source-local completion retain one cumulative fixed-digest projection and no second range planner",
    )
    require(
        bool(local)
        and "require_current_owner_identity_or_throw" in local
        and "begin_targeted_access_or_throw" in local
        and "open_optional_payload_for_operation_or_throw" in local,
        "local_pulse_requires_owner_identity_and_targeted_access",
        "source-local scheduling re-enters the existing payload-store authority boundary",
    )
    require(
        "source_content_defined_projection_.reset()" in local
        and "PayloadUnavailable" in local,
        "missing_payload_clears_stale_projection_with_typed_result",
        "a vanished payload cannot leave reusable manifest work pending",
    )
    require(
        "if (!result.before.pending)" in local
        and "result.after = result.before" in local
        and "return result" in local,
        "idle_local_call_is_explicit_and_filesystem_cold",
        "the scheduler can inspect absence without opening payload authority",
    )
    require(
        "continue_source_manifest_projection_or_throw" in server_h
        and "state_->reconciliation_service" in server_c
        and "->continue_source_manifest_projection_or_throw()" in server_c,
        "inbound_server_is_a_thin_owner_forwarder",
        "the peer server does not duplicate source projection logic",
    )
    require(
        "SourceManifestProjectionAdvanced = 21U" in peer_h
        and "source_manifest_projection" in peer_h,
        "peer_service_has_one_typed_source_local_step",
        "source disk progress remains distinguishable from network and repair work",
    )
    require(
        bool(source_step)
        and "local_payload_work_ordinary_turn_due" in source_step
        and "LocalPayloadWorkKind::SourceManifestProjection" in source_step
        and source_step.find("local_payload_work_ordinary_turn_due") < source_step.find("continue_source_manifest_projection_or_throw"),
        "fairness_obligation_precedes_source_payload_access",
        "even typed lease contention consumes the selected local-work turn",
    )
    require(
        "enum class LocalPayloadWorkKind" in peer_c
        and "TerminalVerification" in peer_c
        and "SourceManifestProjection" in peer_c
        and "local_payload_work_ordinary_turn_due.has_value()" in owner_step,
        "source_and_receiver_share_one_local_work_gate",
        "two independent fairness mechanisms cannot drift apart",
    )
    require(
        "local_payload_scheduler_may_run = false" in owner_step
        and "observe_folder_wake_or_throw" in owner_step
        and "refresh_ingress_worker" in owner_step,
        "every_local_hash_pulse_yields_one_ordinary_owner_turn",
        "control, ingress, watcher, repair, and network activity retain an observation opportunity",
    )
    require(
        "next_local_payload_work" in source_step
        and "LocalPayloadWorkKind::TerminalVerification" in source_step
        and "next_local_payload_work" in owner_step
        and "select_source" in owner_step,
        "simultaneously_pending_local_lanes_alternate_priority",
        "one source or receiver obligation cannot permanently dominate the other",
    )
    require(
        all(token not in source_step + owner_step for token in (
            "std::thread", "std::jthread", "std::async")),
        "scheduler_adds_no_worker_thread_or_executor",
        "all local payload work stays in the existing single owner loop",
    )
    require(
        '"anonsync.peer-service.status.v26"' in status_h
        and bool(append_projection)
        and "idle source-manifest projection status carries work" in append_projection
        and "pending source-manifest projection status is invalid" in append_projection,
        "status_v26_canonically_validates_source_projection",
        "live and terminal JSON reject impossible pending/frontier combinations",
    )
    counters = (
        "source_manifest_projection_scheduler_steps",
        "source_manifest_projection_progress_steps",
        "source_manifest_projection_completions",
        "source_manifest_projection_payload_unavailable",
        "source_manifest_projection_restarts",
        "source_manifest_projection_hashed_bytes",
        "source_manifest_projection_ordinary_turn_yields",
    )
    require(
        all(name in peer_h and name in status_c and name in sync_cli for name in counters),
        "all_source_scheduler_counters_reach_live_and_terminal_status",
        "shutdown cannot silently drop source-local work evidence",
    )
    require(
        "render_sync_replica_source_manifest_projection_status_json" in status_c
        and "append_source_manifest_projection_status" in status_c
        and "render_sync_replica_source_manifest_projection_status_json" in sync_cli,
        "live_and_terminal_surfaces_share_one_projection_renderer",
        "the terminal CLI does not maintain a divergent JSON shape",
    )
    require(
        "require_source_manifest_projection_status" in config_status
        and "require_source_manifest_projection_step" in config_status
        and "anonsync.peer-service.status.v26" in config_status,
        "configured_service_oracle_requires_the_v26_contract",
        "ordinary direct service tests cannot ignore the new status domain",
    )
    require(
        "require_payload_operator_status" in i2p_status
        and "anonsync.peer-service.status.v26" in i2p_status,
        "native_i2p_oracle_requires_the_same_v26_contract",
        "route-specific lifecycle coverage cannot retain an older status schema",
    )
    require(
        "test_source_manifest_projection_advances_without_a_peer_after_discovery" in runtime
        and "source_step_bytes" in runtime
        and "hashed_bytes == 173U" in runtime
        and "content_defined_manifest_reuses() == 1U" in runtime,
        "focused_cpp_runtime_proves_peer_independent_completion_and_reuse",
        "three local pulses finish the exact tail and a fresh session pays zero new source work",
    )
    require(
        "PAYLOAD_BYTES = 2 * SOURCE_STEP_BYTES + 4097" in process
        and '"source_payload_preparing_responses": 1' in process
        and '"source_manifest_projection_scheduler_steps": 2' in process
        and '"source_payload_preparing_responses": 0' in process
        and "server_pid" in process
        and "stop_mode" in process,
        "shipping_process_proves_one_discovery_two_local_pulses_and_reuse",
        "the same ready PID finishes work, serves a fresh requester, and drains cleanly",
    )
    require(
        "anonsync_sync_service_source_manifest_scheduler_process_test" in cmake
        and "tools/test_anonsync_service_source_manifest_scheduler.py" in cmake
        and "PROPERTIES TIMEOUT 120" in cmake,
        "shipping_process_oracle_is_registered",
        "the lifecycle proof is not a manual-only script",
    )
    require(
        cmake.count("anonsync_sync_service_source_manifest_scheduler_process_test") >= 2
        and "LABELS \"product\"" in cmake,
        "shipping_process_oracle_is_in_the_product_lane",
        "focused release validation executes the new daemon path",
    )
    require(
        "audit_sync_replica_source_local_manifest_scheduler.py" in cmake,
        "focused_source_audit_is_registered",
        "the lexical release boundary participates in the complete registry",
    )
    require(
        "SOURCE_LOCAL_MANIFEST_SCHEDULER_AND_OWNER_FAIRNESS_AUDIT_rev1008.md" in verifier
        and "REVISION_NOTES_rev1008.md" in verifier
        and "test_anonsync_service_source_manifest_scheduler.py" in verifier,
        "release_verifier_requires_the_complete_rev1008_slice",
        "implementation cannot be packaged without its runtime and authority documentation",
    )
    require(
        "rev1008" in structural
        and "source_manifest_projection_ordinary_turn_yields" in structural
        and "anonsync.peer-service.status.v26" in structural,
        "structural_audit_binds_status_fairness_and_release_surfaces",
        "the complete authority scan evolves with the focused rev1008 audit",
    )
    normalized = " ".join(docs.replace("**", "").split())
    require(
        all(token in normalized for token in (
            "32 MiB", "4 TiB", "131,072", "process-local",
            "O(chunk count)", "restart", "peer-independent",
            "ordinary owner turn", "Android", "ENOSPC")),
        "documentation_states_scale_cost_and_product_nonclaims",
        "peer independence is not overstated as solved multi-terabyte RSS or restart cost",
    )
    require(
        all(token in docs for token in (
            "rename/move", "directory", "selective", "Tor/I2P")),
        "documentation_keeps_product_priorities_visible",
        "scheduler work remains subordinate to the replacement-product mission",
    )
    require(
        "source-local scheduler" in texts["tools/audit_sync_replica_bounded_source_manifest_projection.py"]
        and "local_payload_work_ordinary_turn_due" in texts["tools/audit_sync_replica_receiver_local_terminal_scheduler.py"],
        "historical_focused_audits_follow_the_refactored_boundary",
        "rev1006 and rev1007 evidence no longer assumes removed inline implementations",
    )
    require(
        all(token not in docs for token in (
            "VALIDATION_PENDING_REV1008",
            "ARCHIVE_PENDING_REV1008",
            "CODENAME_PENDING_REV1008",
        )),
        "final_release_placeholders_are_sealed",
        "the focused audit cannot pass before exact validation and archive identity are published",
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
