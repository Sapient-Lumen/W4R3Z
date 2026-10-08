#!/usr/bin/env python3
"""Lexical audit for rev1004 terminal payload-verification continuation.

This is lexical-hygiene-not-semantic-proof. Source spelling is not semantic
proof. Compiler, sanitizer, runtime, stress, reconstruction, performance, and
package evidence remain load-bearing.
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
    Path("BOUNDED_TERMINAL_PAYLOAD_VERIFICATION_CONTINUATION_AUDIT_rev1004.md"),
    Path("REVISION_NOTES_rev1004.md"),
    Path("src/sync_replica_file_payload_terminal_verification_state.hpp"),
    Path("src/sync_replica_file_payload_terminal_verification_state.cpp"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_protocol.cpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/anonsync_replica.cpp"),
    Path("tests/sync_replica_file_payload_terminal_verification_state_test.cpp"),
    Path("tests/sync_replica_file_payload_store_test.cpp"),
    Path("tests/sync_replica_reconciliation_protocol_test.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/test_anonsync_replica_reconciliation_process.py"),
    Path("tools/audit_sync_replica_bounded_predecessor_projection.py"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def function_body(text: str, signature: str) -> str:
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
                return text[start : index + 1]
    return ""


def ordered(text: str, *tokens: str) -> bool:
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
            return False
    return True


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-terminal-payload-verification-continuation-audit-v2",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove staged-inode identity, bounded byte "
            "work, crash recovery, SHA-256 authority, protocol continuity, "
            "sanitizer cleanliness, multi-terabyte performance, or package identity"
        ),
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
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

    text = {path.as_posix(): (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text["BOUNDED_TERMINAL_PAYLOAD_VERIFICATION_CONTINUATION_AUDIT_rev1004.md"]
    notes = text["REVISION_NOTES_rev1004.md"]
    state_h = text["src/sync_replica_file_payload_terminal_verification_state.hpp"]
    state_c = text["src/sync_replica_file_payload_terminal_verification_state.cpp"]
    store_h = text["src/sync_replica_file_payload_store.hpp"]
    store_c = text["src/sync_replica_file_payload_store.cpp"]
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    protocol_c = text["src/sync_replica_reconciliation_protocol.cpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    replica_cli = text["src/anonsync_replica.cpp"]
    state_test = text["tests/sync_replica_file_payload_terminal_verification_state_test.cpp"]
    store_test = text["tests/sync_replica_file_payload_store_test.cpp"]
    protocol_test = text["tests/sync_replica_reconciliation_protocol_test.cpp"]
    service_test = text["tests/sync_replica_reconciliation_service_test.cpp"]
    tls_test = text["tests/sync_replica_tls_transport_test.cpp"]
    process_test = text["tools/test_anonsync_replica_reconciliation_process.py"]
    predecessor_audit = text["tools/audit_sync_replica_bounded_predecessor_projection.py"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]

    stage = function_body(
        store_c,
        "SyncReplicaFilePayloadStore::stage_payload_prefix_impl_or_throw(",
    )
    range_entry = function_body(
        store_c,
        "SyncReplicaFilePayloadStore::stage_payload_prefix_or_throw(",
    )
    terminal_entry = function_body(
        store_c,
        "SyncReplicaFilePayloadStore::\ncontinue_staged_payload_prefix_verification_or_throw(",
    )
    validate_continuation = function_body(
        protocol_c, "void validate_payload_continuation_or_throw("
    )
    validate_request = function_body(
        protocol_c,
        "void validate_sync_replica_reconciliation_request_or_throw(",
    )
    # The templated response validator has an earlier forward declaration with
    # the same function spelling. Keep this lexical audit on the complete
    # translation unit rather than letting the small brace extractor select the
    # declaration and then the first nested block of the later definition.
    validate_response = protocol_c
    validate_response_for_request = function_body(
        protocol_c,
        "void validate_sync_replica_reconciliation_response_for_request_impl_or_throw(",
    )
    serve = function_body(
        service_c,
        "SyncReplicaReconciliationService::serve_request_frame_or_throw(\n"
        "    const SyncReplicaDeliveryChannelAuthority& channel_authority,\n"
        "    std::string_view request_frame,\n"
        "    SyncReplicaReconciliationServeSession& session)",
    )
    apply = function_body(
        service_c,
        "SyncReplicaReconciliationService::apply_response_or_throw(",
    )
    response_validation = validate_response + "\n" + validate_response_for_request
    sanitizer_link_inventory_start = cmake.index(
        "  foreach(tgt\n      anonsync_core")
    sanitizer_link_inventory_end = cmake.index(
        "    target_link_options(${tgt}", sanitizer_link_inventory_start)
    sanitizer_link_inventory = cmake[
        sanitizer_link_inventory_start:sanitizer_link_inventory_end]

    require(
        "anonsync_sync_replica_file_payload_terminal_verification_state" in cmake
        and "anonsync_sync_replica_file_payload_terminal_verification_state_test" in cmake
        and "anonsync_sync_replica_file_payload_terminal_verification_state_test"
            in sanitizer_link_inventory
        and "anonsync_sync_replica_terminal_verification_continuation_source_audit" in cmake,
        "implementation_test_focused_audit_and_sanitizer_link_are_registered",
        "the codec, runtime oracle, product lane, sanitizer compile/link graph, and lexical audit are ordinary build/test surfaces",
    )
    require(
        ".anonsync-payload-prefix-verification-v1-" in state_h
        and "32ULL * 1024ULL * 1024ULL" in state_h
        and "kSyncReplicaFilePayloadStoreMaximumTerminalVerificationBytesPerStep" in state_h,
        "canonical_journal_name_and_32_mib_frontier_exist",
        "one public hard frontier bounds a terminal owner call without increasing buffer memory",
    )
    require(
        "std::array<" in state_h
        and "std::optional<SyncReplicaFilePayloadTerminalVerificationState>, 2U>" in state_h
        and "slots;" in state_h
        and "kJournalBytes = 2U * kSlotBytes" in state_c
        and "sha256_hex(encoded)" in state_c,
        "journal_has_two_independent_fixed_checksum_slots",
        "progress is fixed-width and checksum-framed rather than raw mutable pathname state",
    )
    require(
        all(token in state_h for token in (
            "store_identity_sha256", "store_identity_metadata", "generation",
            "content_sha256", "total_size_bytes", "staged_prefix_metadata",
            "verified_offset_bytes", "ResumableSha256Checkpoint hash")),
        "slot_binds_store_target_inode_extent_generation_offset_and_hash",
        "restart computation cannot float free of the exact store and complete staged inode",
    )
    require(
        "state.generation == 0U" in state_c
        and "state.verified_offset_bytes >= state.total_size_bytes" in state_c
        and "state.hash.total_bytes != state.verified_offset_bytes" in state_c
        and "state.hash != initial_checkpoint()" in state_c,
        "codec_accepts_only_canonical_nonterminal_progress",
        "no serialized slot is permitted to become terminal content authority",
    )
    require(
        "journal has conflicting equal generations" in state_c
        and "journal has no valid committed slot" in state_c
        and "invalid_nonzero_slot_count" in state_h,
        "journal_parser_detects_conflict_and_torn_slot_shape",
        "equal-generation disagreement fails closed while a damaged newest slot may leave an older valid generation",
    )
    require(
        "for (const auto& slot : out.journal->slots)" in store_c
        and "slot->store_identity_sha256 == identity_sha256" in store_c
        and "slot->content_sha256 == content_sha256" in store_c
        and "slot->total_size_bytes == total_size_bytes" in store_c,
        "every_valid_slot_is_rebound_to_current_store_target_and_extent",
        "a foreign older valid slot cannot become fallback authority after a newer tear",
    )
    require(
        "return stage_payload_prefix_impl_or_throw(" in range_entry
        and "bytes, false" in range_entry
        and "return stage_payload_prefix_impl_or_throw(" in terminal_entry
        and "std::string_view{}, true" in terminal_entry,
        "range_and_terminal_entry_points_share_one_internal_owner_but_distinct_modes",
        "a zero-network-byte local proof cannot be confused with an admitted source range",
    )
    require(
        "if (terminal_verification_only)" in stage
        and "internal terminal verification call carries source range authority" in stage
        and "range_bytes == 0U || offset_bytes >= total_size_bytes" in stage
        and "staged payload prefix range digest does not match its bytes" in stage,
        "ordinary_range_and_terminal_sentinel_shapes_fail_closed",
        "the public range path rejects a terminal sentinel and the terminal path rejects source bytes",
    )
    require(
        "prefix.committed_prefix_bytes != total_size_bytes" in stage
        and "prefix.actual_size_bytes != total_size_bytes" in stage
        and "terminal staged-prefix verification has no completed prefix owner" in stage,
        "terminal_state_starts_only_after_complete_durable_prefix",
        "partial received data and whole-file computation progress remain separate authorities",
    )
    require(
        "SyncReplicaFilePayloadTerminalVerificationState prepared{" in stage
        and "ResumableSha256{}.checkpoint()" in stage
        and "staged-prefix verification reset" in stage
        and "while (rebuilt < prefix.committed_prefix_bytes)" not in stage
        and "update_resumable_hash_regular_file_range_or_throw" not in store_c,
        "missing_or_unusable_journal_restarts_at_zero_without_complete_rebuild",
        "legacy or damaged computation metadata never causes an unbounded compatibility read",
    )
    require(
        "kSyncReplicaFilePayloadStoreMaximumTerminalVerificationBytesPerStep" in stage
        and "const std::uint64_t step_bytes = std::min<std::uint64_t>(" in stage
        and "std::array<char, kStreamingBufferBytes> verification_buffer" in stage
        and "::pread(" in stage
        and "running.update(std::string_view(" in stage,
        "one_terminal_call_reads_at_most_32_mib_with_fixed_memory",
        "the byte frontier is real descriptor I/O rather than a result-only counter",
    )
    require(
        "same_regular_file_observation(\n                    prefix.status, verified_prefix_status)" in stage
        and "completed staged-prefix verification final name proof" in stage
        and "completed staged-prefix verification read lease cutpoint" in stage
        and "verify_named_regular_file_or_throw(" in stage,
        "each_step_reproves_descriptor_path_identity_and_lease",
        "durable hash progress remains attached to the exact complete staged inode",
    )
    require(
        "serialize_sync_replica_file_payload_terminal_verification_state_or_throw(" in stage
        and "pwrite_all_or_throw(" in stage
        and "fsync_or_throw(" in stage
        and "observe_terminal_verification_state_file_or_throw(" in stage
        and "(void)publish_terminal_verification(" in stage,
        "nonterminal_slot_is_synced_and_reopened_before_progress_returns",
        "a torn publication cannot be remembered only in process memory",
    )
    require(
        "const std::string completed_sha256 = running.finish_hex()" in stage
        and "completed_sha256 != content_sha256" in stage
        and "state.verified_offset_bytes >= state.total_size_bytes" in state_c,
        "terminal_digest_exists_only_in_current_process",
        "serialized computation progress never substitutes for exact final SHA-256",
    )
    require(
        ordered(
            stage,
            "const std::string completed_sha256 = running.finish_hex()",
            "final publication preflight",
            "completed staged prefix pre-publication",
            "staged prefix pre-publication lease cutpoint",
            "rename_noreplace_at_or_throw(",
        )
        and "final_prefix->status, prefix.status" in stage,
        "final_publication_reproves_namespace_exact_inode_path_and_lease",
        "whole digest equality alone does not skip final store and pathname authority",
    )
    require(
        "invalid completed staged prefix cleanup" in stage
        and "invalid staged-prefix verification-state cleanup" in stage
        and "completed staged prefix failed whole-file verification" in stage,
        "final_digest_mismatch_removes_exact_invalid_owner_and_state",
        "a false digest name cannot appear after local byte corruption",
    )
    require(
        "terminal verification journal count exceeds configured budget" in store_c
        and "terminal_verification_entry_count" in store_c
        and "bootstrap.terminal_verification_entry_count != 0U" in store_c,
        "hidden_journal_extent_count_and_bootstrap_influence_are_bounded",
        "excluding computation metadata from semantic roots does not make its namespace unlimited",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h
        and "request-frame-v9" in protocol_c
        and "response-frame-v9" in protocol_c
        and "reconciliation-request-v9" in protocol_c
        and "reconciliation-response-v9" in protocol_c,
        "terminal_continuation_survives_current_distinct_frame_and_semantic_domains",
        "the all-bytes-received obligation cannot be silently interpreted through an older generation",
    )
    require(
        "continuation.next_offset_bytes > continuation.total_size_bytes" in validate_continuation
        and "continuation.next_offset_bytes == 0U" in validate_continuation
        and "terminal verification continuation cannot carry a cached delta manifest" in validate_request,
        "request_validation_admits_only_exact_total_terminal_continuation",
        "terminal continuation is canonical and cannot retain an obsolete target-manifest cache",
    )
    require(
        "continuation.next_offset_bytes >" in replica_cli
        and "--payload-next-offset must be in [1, payload-total-size]" in replica_cli
        and "ranged-source-to-receiver-exact-cursor" in process_test
        and '"terminal_verification_steps": 3' in process_test
        and '"terminal_verification_local_continuation_steps": 2' in process_test
        and "payload-cold exact-cursor completion" in process_test
        and "generation-9 TLS final range and payload-cold source completion" in tls_test,
        "shipping_cli_and_end_to_end_oracles_accept_terminal_sentinel",
        "the command boundary carries exact-total continuation through a payload-cold restart instead of rejecting generation-8 authority",
    )
    require(
        "const bool terminal_continuation" in validate_response
        and "terminal_payload_cold_operation" in validate_response
        and "response.payloads.empty()" in response_validation
        and "response.next_after_operation_id !=" in validate_response_for_request
        and "request.after_operation_id" in validate_response_for_request
        and "!response.has_more" in validate_response_for_request,
        "terminal_response_is_payload_cold_cursor_stable_and_nonterminal",
        "the source cannot erase the receiver-local proof obligation or smuggle new payload authority",
    )
    require(
        "const bool terminal_verification_request" in serve
        and "response.payload_continuation = request.payload_continuation" in serve
        and "response.next_after_operation_id = request.after_operation_id" in serve
        and "page_requires_payload_access" in serve
        and "!terminal_verification_request" in serve,
        "source_terminal_turn_repeats_exact_operation_without_payload_access",
        "a high-latency proof turn carries metadata obligation but no source payload bytes",
    )
    require(
        "response.payload_continuation =\n                        SyncReplicaReconciliationPayloadContinuation" in serve
        and "operation.size_bytes,\n                            next_offset" in serve
        and "response.next_after_operation_id = request.after_operation_id" in serve
        and "payload_incomplete = true" in serve,
        "final_source_range_hands_off_total_offset_without_cursor_advance",
        "the operation remains reachable after the final payload bytes arrive",
    )
    require(
        "const bool terminal_verification_request" in apply
        and "continue_staged_payload_prefix_verification_or_throw(" in apply
        and "staged.accepted_range_bytes != 0U" in apply
        and "local terminal payload verification lost exact identity or admitted source authority" in apply,
        "receiver_terminal_branch_uses_separate_zero_byte_store_api",
        "no repeated source bytes are charged as local terminal proof",
    )
    progress_position = apply.find("ReceivedFilePayloadDisposition::Progress)")
    admission_position = apply.find("owner_.accept_remote_or_throw(operation)")
    require(
        progress_position >= 0
        and admission_position > progress_position
        and "return result;" in apply[progress_position:admission_position],
        "operation_admission_remains_after_complete_local_payload_publication",
        "metadata cannot get ahead of the exact digest-named immutable payload",
    )
    require(
        "generation-9 final range did not hand off" in protocol_test
        and "terminal payload verification response did not remain exact and payload-cold" in protocol_test
        and "terminal payload verification response advanced source operation authority" in protocol_test,
        "protocol_runtime_covers_positive_and_negative_generation_8_shapes",
        "canonical framing and semantic validation are exercised by compiled code",
    )
    require(
        "terminal_verification_page_count" in service_test
        and "terminal_verification_page_count == 0U" in service_test
        and "terminal_verification_local_continuation_steps == 1U" in service_test
        and "test_terminal_verification_step_budget_yields_exact_continuation" in service_test
        and "48U * mebibyte" in service_test,
        "service_runtime_proves_48_mib_two_step_local_proof_and_payload_cold_page",
        "the generation-8 handoff is integrated with real content-defined delta application",
    )
    require(
        "test_terminal_verification_journal_bounds_restart_work" in store_test
        and "nonterminal 32 MiB checkpoint" in store_test
        and "malformed terminal journal did not restart bounded verification" in store_test
        and "completed staged prefix failed whole-file verification" in store_c,
        "payload_store_runtime_covers_restart_damage_mismatch_and_capacity",
        "the fixed byte boundary survives owner restart without data loss or false publication",
    )
    require(
        "sync replica file payload terminal verification state:" in state_test
        and "conflicting equal generations" in state_test
        and "terminal verification advance frontier drifted" in state_test,
        "codec_runtime_covers_width_rotation_conflict_and_public_frontier",
        "the small durable owner has an independent compiled regression",
    )
    normalized = " ".join((design + "\n" + notes + "\n" + readme + "\n" + bootstrap).replace("**", "").split())
    require(
        "32 MiB" in normalized
        and "generation 8" in normalized
        and "payload-cold" in normalized
        and "complete compatibility reread" in normalized
        and "high-latency" in normalized
        and "source-side target-manifest" in normalized,
        "scope_crash_wire_and_scale_nonclaims_are_explicit",
        "rev1004 is not overstated as a complete multi-terabyte performance solution",
    )
    require(
        "rejected" in design.lower()
        and "per-range" in design.lower()
        and "raw resumable hash state" in design.lower()
        and "update_resumable_hash_regular_file_range_or_throw" not in store_c,
        "obsolete_per_range_and_raw_pathname_models_are_absent_and_documented",
        "the adjacent refactor removed dead authority vocabulary rather than preserving two designs",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in predecessor_audit
        and "running.finish_hex()" in predecessor_audit
        and "ResumableSha256Checkpoint" in predecessor_audit,
        "rev1003_focused_oracle_evolves_to_generation_8_final_authority",
        "the inherited delta audit follows the retained terminal implementation",
    )
    require(
        "anonsync-terminal-payload-verification-continuation-audit-v2" in Path(__file__).read_text(encoding="utf-8")
        and "BOUNDED_TERMINAL_PAYLOAD_VERIFICATION_CONTINUATION_AUDIT_rev1004.md" in verifier
        and "REVISION_NOTES_rev1004.md" in verifier
        and "rev1004" in structural,
        "release_and_structural_policy_bind_the_complete_rev1004_slice",
        "the archive must carry implementation, runtime, design, notes, focused audit, and integration",
    )
    require(
        all(token not in design + notes + readme + bootstrap for token in (
            "VALIDATION_PENDING_REV1004",
            "ARCHIVE_PENDING_REV1004",
            "CODENAME_PENDING_REV1004",
        )),
        "final_validation_and_visible_release_cutpoint_are_sealed",
        "rev1004 cannot pass the final release audit until every placeholder is replaced",
    )
    self_text = Path(__file__).read_text(encoding="utf-8")
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "Source spelling is not semantic proof" in self_text
        and "Compiler, sanitizer, runtime" in self_text,
        "lexical_audit_disclaims_load_bearing_semantic_authority",
        "source spelling cannot replace runtime, stress, reconstruction, or package evidence",
    )
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
