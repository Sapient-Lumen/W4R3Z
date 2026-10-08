#!/usr/bin/env python3
"""Lexical audit for rev1000 bounded cross-file content-defined discovery.

This is source-shape hygiene, not semantic proof. Compiler, sanitizer, runtime,
stress, reconstruction, performance, and package evidence remain load-bearing.
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
    Path("CROSS_FILE_CONTENT_DEFINED_DISCOVERY_AUDIT_rev1000.md"),
    Path("REVISION_NOTES_rev1000.md"),
    Path("src/sync_replica_sqlite_owner.hpp"),
    Path("src/sync_replica_sqlite_owner.cpp"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.hpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.cpp"),
    Path("src/anonsync_sync.cpp"),
    Path("src/anonsync_replica.cpp"),
    Path("tests/sync_replica_sqlite_owner_test.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
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
        "format": "anonsync-cross-file-content-defined-discovery-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove SQLite query plans, transaction "
            "isolation, payload identity, bounded runtime latency, chunk reuse, "
            "sanitizer cleanliness, performance, or package identity"
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
    bootstrap_path = root.parent.parent / "BOOTSTRAPROSE.md"
    require(bootstrap_path.is_file(), "release_root_bootstrap_exists", str(bootstrap_path))
    if missing or not bootstrap_path.is_file():
        return emit(root, args.json, checks)

    text = {path.as_posix(): (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text["CROSS_FILE_CONTENT_DEFINED_DISCOVERY_AUDIT_rev1000.md"]
    notes = text["REVISION_NOTES_rev1000.md"]
    owner_h = text["src/sync_replica_sqlite_owner.hpp"]
    owner_c = text["src/sync_replica_sqlite_owner.cpp"]
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    tls_h = text["src/sync_replica_reconciliation_tls_exchange.hpp"]
    tls_c = text["src/sync_replica_reconciliation_tls_exchange.cpp"]
    sync_cli = text["src/anonsync_sync.cpp"]
    replica_cli = text["src/anonsync_replica.cpp"]
    owner_test = text["tests/sync_replica_sqlite_owner_test.cpp"]
    service_test = text["tests/sync_replica_reconciliation_service_test.cpp"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]

    require(
        "anonsync_sync_replica_cross_file_delta_source_audit" in cmake
        and "tools/audit_sync_replica_cross_file_delta.py" in cmake,
        "focused_audit_is_registered",
        "the rev1000 source audit is an ordinary CTest",
    )
    require(
        "kSyncReplicaSqliteVisibleFileCandidateMaximumPaths = 64U" in owner_h
        and "kSyncReplicaSqliteVisibleFileCandidateMaximumCanonicalBytes" in owner_h
        and "4ULL * 1024ULL * 1024ULL" in owner_h
        and "visible_file_candidate_page_or_throw" in owner_h,
        "candidate_page_has_hard_product_frontiers",
        "callers cannot raise the 64-path or four-MiB metadata bounds",
    )
    validator = function_body(
        owner_c,
        "validate_sync_replica_sqlite_visible_file_candidate_page_limits_or_throw",
    )
    require(
        "kSyncReplicaSqliteVisibleFileCandidateMaximumPaths" in validator
        and "kSyncReplicaSqliteVisibleFileCandidateMaximumCanonicalBytes" in validator
        and "outside the product frontier" in validator,
        "candidate_page_limits_are_enforced",
        "the public API rejects enlarged frontiers",
    )
    page = function_body(
        owner_c,
        "SyncReplicaSqliteOwner::visible_file_candidate_page_or_throw",
    )
    require(
        "WHERE v.canonical_path>? AND v.is_primary=1" in page
        and "ORDER BY v.canonical_path LIMIT ?" in page
        and "visible-file candidate lookahead limit" in page
        and "load_stored_operation_row_or_throw" in page,
        "candidate_page_is_primary_key_bounded",
        "one current-primary range plus lookahead supplies exact operation rows",
    )
    require(
        "load_state_or_throw" not in page
        and "all_evidence_operations" not in page
        and "std::sort" not in page
        and "snapshot_or_throw" not in page,
        "candidate_page_is_history_cold",
        "candidate discovery does not reconstruct or sort retained history",
    )
    require(
        ordered(
            page,
            "expected_source_visible_state_digest",
            "SyncReplicaSqliteVisibleFileCandidatePageDisposition::SourceChanged",
            "visible-file candidate cursor prepare",
            "visible-file candidate range prepare",
        ),
        "stale_source_fails_before_cursor_and_range_decode",
        "a changed visible projection cannot be paged through an old cursor",
    )
    require(
        "WHERE canonical_path=? AND is_primary=1" in page
        and "primary_rows != 1U" in page
        and "row.operation.kind == SyncReplicaValueKind::File" in page,
        "cursor_and_file_projection_are_exact",
        "the cursor names one current primary and tombstones remain accounting-only",
    )
    require(
        "struct CrossFileContentDefinedSearch final" in service_h
        and "pending_file_operations" in service_h
        and "next_pending_file_operation" in service_h
        and "struct CachedCrossFileContentDefinedManifest final" in service_h,
        "one_bounded_page_and_manifest_are_process_retained",
        "failed candidates do not force repeated SQL page-tail reads",
    )
    apply = function_body(
        service_c,
        "SyncReplicaReconciliationService::apply_response_or_throw",
    )
    require(
        "cross_file_candidate_page_attempted" in apply
        and (
            "cross_file_manifest_scan_attempted" in apply
            or "cross_file_manifest_step_attempted" in apply
        )
        and "owner_.visible_file_candidate_page_or_throw" in apply
        and "search.pending_file_operations =" in apply,
        "one_page_and_one_manifest_per_apply_turn",
        "the live apply path retains the page and caps expensive discovery effects",
    )
    require(
        "candidate.size_bytes - operation.size_bytes" in apply
        and "target.manifest.parameters.maximum_chunk_bytes" in apply
        and "open_optional_payload_for_operation_or_throw" in apply,
        "cheap_candidate_filters_precede_manifest_hash",
        "path, digest, size, and payload-presence filters reduce complete candidate reads",
    )
    require(
        "reuse_local_candidate_chunks_or_throw" in apply
        and apply.count("reuse_local_candidate_chunks_or_throw(") >= 3
        and "delta predecessor" in apply
        and "delta cross-file candidate" in apply,
        "same_path_and_cross_file_reuse_share_one_copy_boundary",
        "the adjacent refactor prevents two range-copy engines from drifting",
    )
    require(
        "chunk reopen" in apply
        and "copy_range_or_throw" in apply
        and "stage_payload_prefix_or_throw" in apply
        and "matching_candidate_chunk" in apply,
        "local_reuse_reopens_attests_and_stages_exact_chunks",
        "candidate discovery never becomes publication authority",
    )
    counter = "delta_cross_file_candidate_pages"
    require(
        counter in service_h and counter in tls_h and counter in tls_c
        and counter in sync_cli and counter in replica_cli,
        "operator_counters_cross_service_tls_and_cli_boundaries",
        "candidate work is observable in both shipping JSON surfaces",
    )
    require(
        "test_visible_file_candidate_page_is_path_bounded_and_history_cold" in owner_test
        and "visible_file_candidate_range_read_count == 1U" in owner_test
        and "accepted an unbounded path frontier" in owner_test
        and "accepted an unbounded byte frontier" in owner_test,
        "owner_runtime_binds_query_and_limit_shape",
        "the focused test rejects complete projections and raised frontiers",
    )
    require(
        "test_cross_file_content_defined_delta_reuses_renamed_media_chunks" in service_test
        and "48U * mebibyte" in service_test
        and (
            "00-unrelated-media.bin" in service_test
            or "01-unrelated-media.bin" in service_test
        )
        and (
            "candidate_pages == 1U" in service_test
            or "candidate_pages == 2U" in service_test
        )
        and "cross_manifest_scans == 2U" in service_test
        and "evidence_page_range_read_count == 0U" in service_test,
        "service_runtime_binds_renamed_media_and_page_retention",
        "one decoy and one matching source prove retained-page multi-turn discovery, including a later availability sweep",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h,
        "wire_generation_is_unchanged",
        "cross-file discovery is receiver-local acceleration",
    )
    require(
        "anonsync-cross-file-content-defined-discovery-audit-v1" in structural
        and "CROSS_FILE_CONTENT_DEFINED_DISCOVERY_AUDIT_rev1000.md" in verifier
        and "REVISION_NOTES_rev1000.md" in verifier
        and "tools/audit_sync_replica_cross_file_delta.py" in verifier,
        "release_policy_binds_rev1000_slice",
        "the archive cannot omit the implementation, runtime oracle, design, notes, or audit",
    )
    normalized = " ".join((design + "\n" + notes + "\n" + readme + "\n" + bootstrap).replace("**", "").split())
    require(
        "one complete candidate" in normalized
        and "not a global chunk index" in normalized
        and "multi-terabyte" in normalized
        and "identity-preserving rename" in normalized,
        "memory_latency_and_product_nonclaims_are_explicit",
        "the release does not overstate bounded memory as bounded candidate-hash latency or rename semantics",
    )
    require(
        all(
            token not in normalized
            for token in (
                "VALIDATION_PENDING_REV1000",
                "ARCHIVE_PENDING_REV1000",
                "CODENAME_PENDING_REV1000",
            )
        ),
        "final_validation_and_archive_identity_are_sealed",
        "rev1000 cannot pass release audit while placeholders remain",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in Path(__file__).read_text(encoding="utf-8")
        and "not semantic proof" in Path(__file__).read_text(encoding="utf-8"),
        "lexical_audit_disclaims_semantic_authority",
        "a source scan cannot substitute for compiler, runtime, sanitizer, performance, or package evidence",
    )
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
