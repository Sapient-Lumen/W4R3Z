#!/usr/bin/env python3
"""Lexical hygiene audit for rev1015 terminal source-manifest cache release.

Source spelling is not semantic proof. Compiler, sanitizer, runtime, wire,
filesystem, restart, reconstruction, and package evidence remain load-bearing.
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
    Path("TERMINAL_SOURCE_MANIFEST_CACHE_RELEASE_AUDIT_rev1015.md"),
    Path("REVISION_NOTES_rev1015.md"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tests/sync_replica_source_manifest_checkpoint_test.cpp"),
    Path("tools/audit_sync_replica_terminal_manifest_cache.py"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def function_body(text: str, signature: str, occurrence: int = 0) -> str:
    search = 0
    start = -1
    for _ in range(occurrence + 1):
        start = text.find(signature, search)
        if start < 0:
            return ""
        search = start + len(signature)
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


def block(text: str, start_token: str, end_token: str) -> str:
    start = text.find(start_token)
    if start < 0:
        return ""
    end = text.find(end_token, start + len(start_token))
    if end < 0:
        return ""
    return text[start:end]


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [item.check_id for item in checks if not item.passed]
    report = {
        "format": "anonsync-terminal-source-manifest-cache-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove exception safety, borrowed-view "
            "lifetime, exact restart replay, allocation count, RSS, sanitizer "
            "cleanliness, reconstruction, or package identity"
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
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
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

    text = {
        path.as_posix(): (root / path).read_text(encoding="utf-8")
        for path in REQUIRED
    }
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text["TERMINAL_SOURCE_MANIFEST_CACHE_RELEASE_AUDIT_rev1015.md"]
    notes = text["REVISION_NOTES_rev1015.md"]
    store_h = text["src/sync_replica_file_payload_store.hpp"]
    store_c = text["src/sync_replica_file_payload_store.cpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service_c = text["src/sync_replica_reconciliation_service.cpp"]
    service_test = text["tests/sync_replica_reconciliation_service_test.cpp"]
    checkpoint_test = text["tests/sync_replica_source_manifest_checkpoint_test.cpp"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]

    store_publish_h = block(
        store_h,
        "void publish_source_manifest_checkpoint_or_throw(",
        "// Filesystem-cold owner-thread scheduling witness",
    )
    store_publish_c = function_body(
        store_c,
        "SyncReplicaFilePayloadStore::publish_source_manifest_checkpoint_or_throw(",
    )
    pending_publish = function_body(
        service_c,
        "void SyncReplicaReconciliationService::\n"
        "publish_pending_source_manifest_checkpoint_if_possible_or_throw(",
    )
    release = function_body(
        service_c,
        "release_terminal_source_manifest_cache_if_possible_or_throw(",
    )
    serve = function_body(
        service_c,
        "SyncReplicaReconciliationService::serve_request_frame_or_throw(",
        1,
    )
    cache_status = function_body(
        service_c,
        "SyncReplicaReconciliationService::source_manifest_cache_status() const",
    )
    cache_type = block(
        service_h,
        "struct CachedSourceContentDefinedManifest final",
        "struct SourceContentDefinedProjection final",
    )
    public_status = block(
        service_h,
        "struct SyncReplicaReconciliationSourceManifestCacheStatus final",
        "enum class SyncReplicaReconciliationSourceManifestProjectionStepDisposition",
    )

    require(
        "SyncReplicaSourceManifestCheckpoint& checkpoint" in store_publish_h
        and "SyncReplicaSourceManifestCheckpoint checkpoint" not in store_publish_h,
        "checkpoint_publication_signature_is_caller_owned",
        "publisher accepts a mutable lvalue rather than copying the 8192-record vector",
    )
    require(
        "SyncReplicaSourceManifestCheckpoint& committed" in pending_publish
        and "*pending_source_manifest_checkpoint_" in pending_publish
        and "SyncReplicaSourceManifestCheckpoint candidate" not in pending_publish
        and "std::move(candidate)" not in pending_publish,
        "pending_checkpoint_is_published_in_place",
        "typed deferral retains the same optional candidate without an O(chunk-count) copy",
    )
    require(
        "committed.checkpoint != checkpoint" in store_publish_c
        and "final lease cutpoint" in store_publish_c
        and "return checkpoint" not in store_publish_c,
        "in_place_publication_retains_exact_committed_reproof",
        "removing the return object does not remove postpublication reproof",
    )
    require(
        "std::string operation_id" in cache_type
        and "std::string canonical_path" in cache_type
        and "source.operation_id" in cache_status
        and "source.canonical_path" in cache_status,
        "completed_cache_binds_exact_causal_origin",
        "terminal release cannot rely on content identity alone",
    )
    require(
        "source_durable_checkpoint_manifest_digest_" in service_h
        and "committed.manifest_digest" in pending_publish
        and "source.manifest_digest" in release,
        "durable_witness_binds_complete_manifest_digest",
        "operation completion cannot authorize release of a different compact sequence",
    )
    require(
        all(token in release for token in (
            "pending_source_manifest_checkpoint_.has_value()",
            "source.operation_id != operation.operation_id",
            "source.canonical_path != operation.canonical_path",
            "source.content_sha256 != operation.content_sha256",
            "source.total_size_bytes != operation.size_bytes",
            "!source_durable_checkpoint_complete_",
            "source_durable_checkpoint_manifest_digest_ != source.manifest_digest",
        )),
        "terminal_release_is_exact_and_checkpoint_gated",
        "deferred or cross-operation cache state remains resident",
    )
    reset_position = release.find("source_content_defined_manifest_.reset()")
    require(
        0 <= release.find("next_release_count") < reset_position
        and 0 <= release.find("next_released_capacity") < reset_position
        and reset_position < release.find("source_manifest_cache_terminal_releases_ ="),
        "release_counters_are_preflighted_before_cache_mutation",
        "diagnostic overflow cannot report failure after destroying the cache",
    )
    require(
        0 <= serve.find("assembly.finish_or_throw()")
        < serve.find("opened_payloads.clear()")
        < serve.find("post-frame source manifest checkpoint publication")
        < serve.find("release_terminal_source_manifest_cache_if_possible_or_throw"),
        "borrowed_view_descriptor_and_checkpoint_order_precede_release",
        "the compact vector is not destroyed while framing or source descriptors still depend on it",
    )
    require(
        "next_offset == operation.size_bytes" in serve
        and "terminal_source_manifest_operation = &operation" in serve
        and "source_manifest_cache_terminal_releases" in service_h
        and "source_manifest_cache_terminal_released_capacity_bytes" in service_h,
        "terminal_frame_exposes_exact_release_accounting",
        "shipping framed results report whether and how much cache capacity was released",
    )
    require(
        all(token in public_status for token in (
            "bool resident",
            "retained_chunk_capacity_bytes",
            "exact_complete_checkpoint_durable",
            "complete_checkpoint_restorations",
            "terminal_releases",
            "terminal_released_capacity_bytes",
        ))
        and "payload_store_." not in cache_status,
        "cache_status_is_bounded_and_filesystem_cold",
        "status does not open payloads or durable checkpoint state",
    )
    require(
        "complete source manifest checkpoint restorations" in service_c
        and "source_manifest_complete_checkpoint_restorations_" in service_h
        and "source_manifest_cache_status()" in service_h,
        "durable_rehydration_is_observable",
        "lost-response replay can be distinguished from fresh source hashing",
    )
    require(
        "SourceCheckpointPublicationSignature" in service_test
        and "publish_source_manifest_checkpoint_or_throw" in service_test
        and "SyncReplicaSourceManifestCheckpoint&" in service_test,
        "test_compile_time_binds_reference_publication",
        "future by-value regression fails the focused C++ build",
    )
    require(
        all(token in service_test for token in (
            "cache_before_terminal.resident",
            "exact_complete_checkpoint_durable",
            "source_manifest_cache_terminal_releases == 1U",
            "!cache_after_terminal.resident",
            "complete_checkpoint_restorations == 1U",
            "content_defined_manifest_scans() == 1U",
            "content_defined_manifest_hashed_bytes() ==",
        )),
        "runtime_proves_release_and_zero_rehash_rehydration",
        "terminal release, replay restore, and unchanged source hashing are executable",
    )
    require(
        "kSyncReplicaSourceManifestCheckpointMaximumChunks" in checkpoint_test
        and "sizeof(Chunk) == 40U" in checkpoint_test
        and "expected_vector_bytes = kChunks * sizeof(Chunk)" in checkpoint_test
        and "copy.requested_bytes == expected_vector_bytes" in checkpoint_test,
        "existing_maximum_shape_proof_quantifies_removed_copy",
        "8192 fixed records retain an independently measured 327680-byte copy cost",
    )
    require(
        "anonsync_sync_replica_terminal_manifest_cache_source_audit" in cmake
        and "audit_sync_replica_terminal_manifest_cache.py" in cmake,
        "dedicated_audit_is_registered",
        "the revision-specific lexical gate participates in the test registry",
    )
    require(
        "TERMINAL_SOURCE_MANIFEST_CACHE_RELEASE_AUDIT_rev1015.md" in verifier
        and "REVISION_NOTES_rev1015.md" in verifier
        and "audit_sync_replica_terminal_manifest_cache.py" in verifier,
        "release_verifier_requires_rev1015_surfaces",
        "the package cannot omit code-adjacent design and audit evidence",
    )
    require(
        "rev1015_terminal_manifest_cache" in structural,
        "structural_audit_carries_rev1015_boundary",
        "the accumulated authority audit follows the new lifetime rules",
    )
    combined = design + "\n" + notes + "\n" + readme + "\n" + bootstrap
    require(
        all(token in combined for token in (
            "8,192", "327,680", "40-byte", "generation-9", "4 TiB",
            "131,072", "32 MiB", "1 GiB", "O(chunk count)", "RSS",
            "multi-share", "rename/move", "directory", "conflict",
            "ENOSPC", "Android", "Tor", "I2P",
        )),
        "benefit_and_nonclaims_are_explicit",
        "two bounded memory corrections are not overstated as solved product memory",
    )
    require(
        all(token not in combined for token in (
            "VALIDATION_PENDING_REV1015",
            "ARCHIVE_PENDING_REV1015",
            "CODENAME_PENDING_REV1015",
        )),
        "final_validation_and_archive_are_sealed",
        "rev1015 cannot pass its final structural gate with publication placeholders",
    )
    self_text = Path(__file__).read_text(encoding="utf-8")
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "not semantic proof" in self_text,
        "lexical_audit_disclaims_semantic_authority",
        "passing source spelling cannot be mistaken for runtime or sanitizer proof",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
