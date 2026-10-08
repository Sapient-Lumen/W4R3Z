#!/usr/bin/env python3
"""Lexical hygiene audit for rev1007 bounded source-manifest projection.

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
    Path("BOUNDED_SOURCE_MANIFEST_PROJECTION_AND_SESSION_RESUME_AUDIT_rev1007.md"),
    Path("REVISION_NOTES_rev1007.md"),
    Path("src/anonsync_replica.cpp"),
    Path("src/anonsync_sync.cpp"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_protocol.cpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.hpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.cpp"),
    Path("src/sync_replica_sync_once.hpp"),
    Path("src/sync_replica_sync_once.cpp"),
    Path("tests/sync_replica_reconciliation_protocol_test.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tests/sync_replica_sync_once_test.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/test_anonsync_replica_reconciliation_process.py"),
    Path("tools/test_anonsync_sync_process.py"),
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


def last_body(text: str, signature: str) -> str:
    start = text.rfind(signature)
    if start < 0:
        return ""
    return body(text[start:], signature)


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [item.check_id for item in checks if not item.passed]
    report = {
        "format": "anonsync-bounded-source-manifest-projection-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove bounded wall time, exact inode "
            "identity, peer fairness, TLS behavior, SHA-256 authority, restart "
            "semantics, sanitizer cleanliness, or package identity"
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
    candidates = (
        root.parent.parent / "BOOTSTRAPROSE.md",
        root.parent / "BOOTSTRAPROSE.md",
    )
    bootstrap_path = next((path for path in candidates if path.is_file()), None)
    require(bootstrap_path is not None, "release_root_bootstrap_exists", str(candidates))
    if missing or bootstrap_path is None:
        return emit(root, args.json, checks)

    texts = {
        path.as_posix(): (root / path).read_text(encoding="utf-8")
        for path in REQUIRED
    }
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    protocol_h = texts["src/sync_replica_reconciliation_protocol.hpp"]
    protocol_c = texts["src/sync_replica_reconciliation_protocol.cpp"]
    service_h = texts["src/sync_replica_reconciliation_service.hpp"]
    service_c = texts["src/sync_replica_reconciliation_service.cpp"]
    tls_h = texts["src/sync_replica_reconciliation_tls_exchange.hpp"]
    tls_c = texts["src/sync_replica_reconciliation_tls_exchange.cpp"]
    sync_once_h = texts["src/sync_replica_sync_once.hpp"]
    sync_once_c = texts["src/sync_replica_sync_once.cpp"]
    replica_main = texts["src/anonsync_replica.cpp"]
    sync_main = texts["src/anonsync_sync.cpp"]
    protocol_test = texts["tests/sync_replica_reconciliation_protocol_test.cpp"]
    service_test = texts["tests/sync_replica_reconciliation_service_test.cpp"]
    sync_once_test = texts["tests/sync_replica_sync_once_test.cpp"]
    tls_test = texts["tests/sync_replica_tls_transport_test.cpp"]
    process_test = texts["tools/test_anonsync_replica_reconciliation_process.py"]
    cmake = texts["CMakeLists.txt"]
    verifier = texts["tools/verify_release_package.py"]
    structural = texts["tools/audit_sync_file_payload_store.py"]
    design = texts[
        "BOUNDED_SOURCE_MANIFEST_PROJECTION_AND_SESSION_RESUME_AUDIT_rev1007.md"
    ]
    notes = texts["REVISION_NOTES_rev1007.md"]
    prose = "\n".join((design, notes, texts["README.md"], bootstrap))

    serve = last_body(
        service_c,
        "SyncReplicaReconciliationService::serve_request_frame_or_throw(",
    )
    projection_helper = body(
        service_c,
        "advance_source_content_defined_projection_or_throw(",
    )
    local_projection = body(
        service_c,
        "continue_source_manifest_projection_or_throw()",
    )
    projection_authority = "\n".join(
        (serve, projection_helper, local_projection)
    )
    preparing_block_start = serve.find("if (!projection_step.completed)")
    preparing_block_end = serve.find("increment_or_throw(\n                            session.content_defined_manifest_scans_", preparing_block_start)
    preparing_block = (
        serve[preparing_block_start:preparing_block_end]
        if preparing_block_start >= 0 and preparing_block_end >= 0
        else ""
    )
    observe_tls = body(tls_c, "observe_served_response(")

    require(
        "kSyncReplicaReconciliationMaximumSourceManifestProjectionBytesPerRequest ="
        in service_h
        and "32ULL * 1024ULL * 1024ULL" in service_h,
        "shipping_source_projection_frontier_is_32_mib",
        "one authenticated request cannot hash an unbounded source payload",
    )
    require(
        "max_source_manifest_projection_bytes_per_request_ == 0U" in service_c
        and "source manifest projection byte frontier must be in [1, shipping maximum]"
        in service_c,
        "constructor_rejects_zero_or_raised_projection_frontier",
        "tests may lower but no caller may silently raise the shipping bound",
    )
    require(
        "struct SourceContentDefinedProjection final" in service_h
        and "SyncPosixRegularFileSnapshotMetadata source_metadata" in service_h
        and "SyncReplicaFilePayloadStoreContentDefinedProjection projection" in service_h,
        "projection_binds_exact_payload_identity_and_inode_observation",
        "process acceleration is tied to digest, extent, parameters, and exact source metadata",
    )
    session_region = service_h[
        service_h.find("class SyncReplicaReconciliationServeSession final"):
        service_h.find("enum class SyncReplicaReconciliationApplyDisposition")
    ]
    service_region = service_h[
        service_h.find("class SyncReplicaReconciliationService final"):
    ]
    require(
        "source_content_defined_projection_" not in session_region
        and "source_content_defined_projection_" in service_region
        and "source_content_defined_manifest_" in service_region,
        "projection_survives_session_turnover_but_not_process_restart",
        "one retained service owner, not one TLS session, owns bounded acceleration",
    )
    require(
        "open_source_payload_or_none" in serve
        and "begin_targeted_access_or_throw" in local_projection
        and "open_optional_payload_for_operation_or_throw" in local_projection
        and "opened.content_sha256()" in projection_helper
        and "opened.size_bytes()" in projection_helper
        and "source_content_defined_projection_->source_metadata" in projection_helper
        and "opened.metadata()" in projection_helper,
        "every_step_reopens_and_reproves_exact_digest_named_payload",
        "remembered projection state cannot substitute for current rooted source observation",
    )
    require(
        "content_defined_manifest_projection_restarts_" in serve
        and "projection_matches" in projection_helper
        and "source_content_defined_projection_ =" in projection_helper
        and "source_content_defined_manifest_.reset()" in serve,
        "identity_or_target_change_discards_stale_projection",
        "a different source cannot inherit another payload's resumable hashing state",
    )
    require(
        "advance_content_defined_projection_or_throw" in projection_helper
        and "max_source_manifest_projection_bytes_per_request_" in projection_helper
        and "content_defined_manifest_projection_steps_" in serve
        and "content_defined_manifest_hashed_bytes_" in serve,
        "one_request_advances_one_accounted_bounded_projection_step",
        "source work is explicit and operator-visible rather than hidden in frame construction",
    )
    require(
        "SourcePayloadPreparing" in serve
        and "response.blocked_operation_id =\n                                operation.operation_id" in serve
        and "source_payload_preparing_responses_" in serve,
        "incomplete_projection_returns_exact_blocked_operation",
        "the source cursor does not advance past payload bytes that were not framed",
    )
    require(
        bool(preparing_block)
        and "opened_payloads.push_back" not in preparing_block
        and "response.payload_continuation" not in preparing_block,
        "preparing_response_retains_no_source_descriptor_or_payload_continuation",
        "the exact source descriptor dies before TLS backpressure and no receiver byte authority is invented",
    )
    require(
        "source_content_defined_projection_.reset()" in projection_helper
        and "source_content_defined_manifest_ =" in projection_helper
        and "SyncReplicaReconciliationCompactManifest::from_manifest_or_throw" in projection_helper
        and "sync_replica_reconciliation_delta_manifest_digest_or_throw" in projection_helper
        and "std::move(compact_manifest)" in projection_helper
        and "chunk_offsets_or_throw" not in projection_helper,
        "completed_projection_enters_existing_compact_manifest_path",
        "bounded preparation retains one cumulative fixed-digest projection and does not create a second delta format or range planner",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h
        and "reconciliation-request-frame-v9" in protocol_c
        and "reconciliation-response-frame-v9" in protocol_c
        and "reconciliation-request-v9" in protocol_c
        and "reconciliation-response-v9" in protocol_c,
        "generation_9_has_distinct_frame_and_semantic_domains",
        "mixed generation-8 and generation-9 authority fails before application",
    )
    require(
        "SourcePayloadPreparing = 4U" in protocol_h
        and "source-preparing response lacks an exact blocked continuation" in protocol_c
        and "preparing operation is already included" in protocol_c
        and "preparing operation does not follow the transferable prefix" in protocol_c,
        "protocol_validates_exact_nonadvancing_preparing_response",
        "malformed blocked IDs and cursor advancement fail closed",
    )
    require(
        "SourcePayloadPreparing = 9U" in tls_h
        and "SourcePayloadPreparing = 7U" in tls_h
        and "source_payload_preparing_responses = 0U" in tls_h
        and "SourcePayloadPreparing" in tls_c
        and "result.source_payload_preparing_responses =" not in tls_c
        and "result.source_payload_preparing_responses" in observe_tls,
        "tls_maps_preparing_and_counts_each_response_once",
        "the adjacent audit removed duplicate service-session plus response-observer accounting",
    )
    require(
        tls_c.count("if (index + 1U < options.max_round_trips)") >= 2
        and "result.payload_continuation = payload_continuation;" in tls_c
        and "if (cursor.has_value() ||\n                        payload_continuation.has_value())" in tls_c
        and "source_digest.reset();" in tls_c,
        "tls_collapses_preparation_turns_without_inventing_continuation_authority",
        "the same authenticated stream advances while budget remains and preserves only already-authorized cursors or payload offsets",
    )
    require(
        "ReconciliationSourcePayloadPreparing = 21U" in sync_once_h
        and "reconciliation_source_payload_preparing" in sync_once_c
        and "ReconciliationSourcePayloadPreparing" in sync_once_c
        and "ReconciliationSourcePayloadPreparing" in sync_once_test,
        "sync_once_preserves_typed_bounded_progress",
        "an owner turn can retry later without misclassifying source disk work as availability failure",
    )
    require(
        "reconciliation_content_defined_manifest_projection_steps" in replica_main
        and "reconciliation_content_defined_manifest_projection_restarts" in replica_main
        and "reconciliation_source_payload_preparing_responses" in replica_main
        and "source_payload_preparing_responses" in replica_main
        and "source_payload_preparing_responses" in sync_main,
        "shipping_source_and_requester_json_expose_projection_work",
        "operators can distinguish collapsed source hashing turns from ranged payload transfer",
    )
    require(
        "test_source_manifest_projection_resumes_across_fresh_serve_sessions" in service_test
        and "preparing_responses == 3U" in service_test
        and "content_defined_manifest_projection_steps() == 1U" in service_test
        and "fresh_session.content_defined_manifest_hashed_bytes() == 173U" in service_test
        and "cross-session source projection did not complete once from retained bounded progress" in service_test,
        "service_runtime_proves_fresh_session_resume_and_exact_final_pulse",
        "three bounded preparing turns precede one canonical completed manifest",
    )
    require(
        "test_reconciliation_tls_source_manifest_preparing" in tls_test
        and "projection_budget = 512U * 1024U" in tls_test
        and "options.max_round_trips = 3U" in tls_test
        and "source_payload_preparing_responses == 2U" in tls_test
        and "pull_result.round_trips == 3U" in tls_test
        and "serve_result.ranged_payload_bytes == 8U" in tls_test,
        "tls_runtime_proves_same_stream_preparation_turn_collapse",
        "two bounded source pulses precede one ranged response on the same authenticated stream",
    )
    require(
        process_test.count('max_round_trips=3') >= 2
        and '"source_payload_preparing_responses": 2' in process_test
        and '"source_payload_preparing_responses": 0' in process_test
        and '"reconciliation_requests_received": 3' in process_test
        and '"reconciliation_requests_received": 2' in process_test
        and '"reconciliation_content_defined_manifest_hashed_bytes":\n                range_size'
            in process_test
        and '"reconciliation_content_defined_manifest_reuses": 1'
            in process_test
        and "restart-warm final ranged source completion" in process_test,
        "shipping_process_runtime_proves_one_shot_wire_progress_after_two_pulses",
        "the production 32 MiB frontier reaches the first wire range and a later service invocation restores the complete source manifest without new preparation pulses",
    )
    require(
        "bounded source-preparing response did not survive canonical generation-9 framing"
        in protocol_test
        and "SourcePayloadPreparing" in protocol_test,
        "protocol_runtime_covers_positive_and_malformed_preparing_shapes",
        "generation-9 canonical bytes and exact blocked identity have direct regressions",
    )
    require(
        "anonsync_sync_replica_bounded_source_manifest_projection_source_audit" in cmake
        and "BOUNDED_SOURCE_MANIFEST_PROJECTION_AND_SESSION_RESUME_AUDIT_rev1007.md"
        in verifier
        and "REVISION_NOTES_rev1007.md" in verifier
        and "rev1007" in structural,
        "release_policy_binds_complete_rev1007_slice",
        "implementation, tests, design, focused audit, structural audit, and package policy are mandatory",
    )
    normalized = " ".join(prose.replace("**", "").split())
    require(
        all(
            token in normalized
            for token in (
                "32 MiB",
                "generation 9",
                "process-local",
                "4 TiB",
                "131,072",
                "authenticated",
                "restart",
                "source-local scheduler",
                "same authenticated TLS stream",
                "2 GiB",
                "128 GiB",
            )
        ),
        "scale_cost_restart_boundary_and_next_scheduler_are_explicit",
        "bounded source work is not overstated as efficient multi-terabyte completion",
    )
    require(
        all(
            token not in prose
            for token in (
                "VALIDATION_PENDING_REV1007",
                "ARCHIVE_PENDING_REV1007",
                "CODENAME_PENDING_REV1007",
            )
        ),
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
