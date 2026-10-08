#!/usr/bin/env python3
"""Lexical hygiene audit for rev1015 active-source fixed digest memory.

Source spelling is not semantic proof. Compiler, sanitizer, runtime allocation,
digest-equivalence, reconstruction, and package evidence remain load-bearing.
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
    Path("ACTIVE_SOURCE_MANIFEST_FIXED_DIGEST_AND_MULTISHARE_MEMORY_AUDIT_rev1015.md"),
    Path("REVISION_NOTES_rev1015.md"),
    Path("src/sha256_digest.hpp"),
    Path("src/resumable_sha256.hpp"),
    Path("src/resumable_sha256.cpp"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("src/sync_replica_source_manifest_checkpoint.hpp"),
    Path("src/sync_replica_source_manifest_checkpoint.cpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("tests/resumable_sha256_test.cpp"),
    Path("tests/sync_replica_file_payload_store_test.cpp"),
    Path("tests/sync_replica_reconciliation_source_frame_memory_test.cpp"),
    Path("tools/audit_sync_replica_active_source_manifest_memory.py"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


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
        "format": "anonsync-active-source-manifest-memory-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove allocation count, digest equality, "
            "whole-process RSS, sanitizer cleanliness, reconstruction, or package identity"
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
    require(bootstrap_path is not None, "bootstrap_exists", "release-root runbook is visible")
    if missing or bootstrap_path is None:
        return emit(root, args.json, checks)

    text = {path.as_posix(): (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text["ACTIVE_SOURCE_MANIFEST_FIXED_DIGEST_AND_MULTISHARE_MEMORY_AUDIT_rev1015.md"]
    notes = text["REVISION_NOTES_rev1015.md"]
    resumable_h = text["src/resumable_sha256.hpp"]
    resumable_c = text["src/resumable_sha256.cpp"]
    payload_h = text["src/sync_replica_file_payload_store.hpp"]
    payload_c = text["src/sync_replica_file_payload_store.cpp"]
    checkpoint_h = text["src/sync_replica_source_manifest_checkpoint.hpp"]
    checkpoint_c = text["src/sync_replica_source_manifest_checkpoint.cpp"]
    service = text["src/sync_replica_reconciliation_service.cpp"]
    sha_test = text["tests/resumable_sha256_test.cpp"]
    payload_test = text["tests/sync_replica_file_payload_store_test.cpp"]
    memory_test = text["tests/sync_replica_reconciliation_source_frame_memory_test.cpp"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]
    chunk = block(
        payload_h,
        "struct SyncReplicaFilePayloadStoreContentDefinedChunk final",
        "struct SyncReplicaFilePayloadStoreContentDefinedManifest final",
    )

    require(
        "std::uint64_t size_bytes" in chunk
        and "Sha256DigestValue sha256" in chunk
        and "std::string sha256;" not in chunk,
        "active_chunk_uses_fixed_digest",
        "the in-progress projection does not retain one digest string per chunk",
    )
    require(
        "sizeof(SyncReplicaFilePayloadStoreContentDefinedChunk) == 40U" in payload_h
        and "std::is_trivially_copyable_v<" in payload_h,
        "active_chunk_layout_is_exact_and_trivial",
        "one active record remains one extent plus one 32-byte digest",
    )
    require(
        "finish_binary_array()" in resumable_h
        and "std::array<std::uint8_t, 32U> ResumableSha256::finish_binary_array()" in resumable_c
        and "finish_hex_array()" in resumable_c,
        "resumable_sha256_exposes_one_binary_terminal_path",
        "fixed binary and textual terminal forms share the same finalization owner",
    )
    require(
        "Sha256DigestValue(chunk_digest_.finish_binary_array())" in payload_c
        and "chunk_digest_.finish_hex()" not in block(
            payload_c, "class ContentDefinedDigestAccumulator final", "[[nodiscard]] ContentDefinedDigestProjection"
        ),
        "chunk_completion_is_text_allocation_cold",
        "completed chunks are born from 32 digest bytes rather than a temporary string",
    )
    require(
        "SyncReplicaSourceManifestCheckpointChunk(" in checkpoint_h
        and "Sha256DigestValue sha256_value" in checkpoint_h
        and "sha256(std::move(sha256_value))" in checkpoint_c,
        "checkpoint_accepts_fixed_digest_directly",
        "active and complete checkpoint publication does not materialize digest text",
    )
    require(
        "restored.completed_chunks.emplace_back(" in service
        and "chunk.size_bytes, chunk.sha256" in service
        and "manifest.chunks.emplace_back(chunk.size_bytes, chunk.sha256)" in service,
        "service_copies_fixed_records_between_owners",
        "restore, checkpoint, protocol, and compact-cache transitions keep binary digests",
    )
    require(
        "!is_lowercase_sha256_hex(chunk.sha256)" not in payload_c
        and "restored projection checkpoint has a noncanonical completed chunk" in payload_c,
        "fixed_values_remove_only_redundant_text_syntax_validation",
        "extent and checkpoint consistency checks remain present",
    )
    require(
        "finish_binary_array" in sha_test
        and "Sha256DigestValue(binary).equals_lowercase_hex" in sha_test
        and "already finished" in sha_test,
        "binary_terminal_runtime_binds_digest_and_single_use",
        "the allocation-free terminal form has an executable standard vector and lifecycle proof",
    )
    require(
        "test_active_source_projection_uses_one_fixed_vector_per_share" in memory_test
        and "kConcurrentShares = 64U" in memory_test
        and "kVectorBytes == 327680U" in memory_test,
        "multishare_fixture_binds_the_hard_shape",
        "64 maximum source projections use the released 8192 by 40-byte frontier",
    )
    require(
        "direct.count == 0U" in memory_test
        and "construction.count == 0U" in memory_test
        and "binary digest completion allocated" in memory_test,
        "runtime_proves_heap_cold_digest_construction",
        "binary completion and each post-reserve fixed record add no allocation",
    )
    require(
        "copies.count == kConcurrentShares" in memory_test
        and "copies.peak_active_count == kConcurrentShares" in memory_test
        and "expected_bytes == 20U * 1024U * 1024U" in memory_test,
        "runtime_proves_one_vector_per_share_and_exact_20_mib",
        "the synthetic 64-share retained record shape is exact and linear",
    )
    require(
        "chunk.sha256.lowercase_hex()" in payload_test,
        "text_validation_occurs_at_an_explicit_boundary",
        "payload-store tests materialize lowercase text only when asserting reporting form",
    )
    require(
        "anonsync_sync_replica_active_source_manifest_memory_source_audit" in cmake
        and "tools/audit_sync_replica_active_source_manifest_memory.py" in cmake,
        "focused_audit_is_registered",
        "the source-shape fence participates in the complete registry",
    )
    require(
        "ACTIVE_SOURCE_MANIFEST_FIXED_DIGEST_AND_MULTISHARE_MEMORY_AUDIT_rev1015.md" in verifier
        and "REVISION_NOTES_rev1015.md" in verifier
        and "audit_sync_replica_active_source_manifest_memory.py" in verifier
        and "rev1015_active_source_manifest" in structural,
        "release_and_structural_policy_bind_rev1015_surfaces",
        "the package cannot omit code, runtime proof, design, notes, or focused audit",
    )
    prose = "\n".join((design, notes, readme, bootstrap))
    require(
        all(token in prose for token in (
            "8,192", "327,680", "860,160", "532,480", "40-byte",
            "64", "20 MiB", "52.5 MiB", "32.5 MiB", "4 TiB",
            "generation 9", "checkpoint format remains v2", "O(chunk count)",
            "RSS", "page cache", "multi-share", "rename/move", "directories",
            "conflict", "selective-sync", "ENOSPC", "Android", "Tor", "I2P",
        )),
        "benefit_compatibility_and_product_nonclaims_are_explicit",
        "record-memory improvement is not overstated as solved whole-process scale",
    )
    require(
        all(token not in prose for token in (
            "VALIDATION_PENDING_REV1015",
            "ARCHIVE_PENDING_REV1015",
            "CODENAME_PENDING_REV1015",
        )),
        "final_validation_and_release_cutpoint_are_sealed",
        "the focused audit stays red until exact publication facts replace placeholders",
    )
    self_text = Path(__file__).read_text(encoding="utf-8")
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "Source spelling is not semantic proof" in self_text,
        "lexical_audit_disclaims_semantic_authority",
        "runtime, sanitizer, reconstruction, and package proof remain load-bearing",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
