#!/usr/bin/env python3
"""Lexical hygiene audit for rev1011 checkpoint heap compaction.

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
    Path("SOURCE_MANIFEST_CHECKPOINT_HEAP_COMPACTION_AUDIT_rev1011.md"),
    Path("REVISION_NOTES_rev1011.md"),
    Path("src/sync_replica_source_manifest_checkpoint.hpp"),
    Path("src/sync_replica_source_manifest_checkpoint.cpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("tests/sync_replica_source_manifest_checkpoint_test.cpp"),
    Path("tools/audit_sync_replica_source_manifest_checkpoint_memory.py"),
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
        "format": "anonsync-source-manifest-checkpoint-memory-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove allocation counts, ABI layout, "
            "wire compatibility, crash durability, sanitizer cleanliness, "
            "whole-process RSS, or package identity"
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
    require(
        bootstrap_path is not None,
        "release_root_bootstrap_exists",
        str(bootstrap_candidates),
    )
    if missing or bootstrap_path is None:
        return emit(root, args.json, checks)

    text = {
        path.as_posix(): (root / path).read_text(encoding="utf-8")
        for path in REQUIRED
    }
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    header = text["src/sync_replica_source_manifest_checkpoint.hpp"]
    codec = text["src/sync_replica_source_manifest_checkpoint.cpp"]
    service = text["src/sync_replica_reconciliation_service.cpp"]
    test = text["tests/sync_replica_source_manifest_checkpoint_test.cpp"]
    cmake = text["CMakeLists.txt"]
    verifier = text["tools/verify_release_package.py"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    docs = (
        text["README.md"] + "\n" +
        text["SOURCE_MANIFEST_CHECKPOINT_HEAP_COMPACTION_AUDIT_rev1011.md"] + "\n" +
        text["REVISION_NOTES_rev1011.md"] + "\n" + bootstrap
    )

    chunk_struct = block(
        header,
        "struct SyncReplicaSourceManifestCheckpointChunk final",
        "// One bounded acceleration record",
    )
    require(
        "Sha256DigestValue sha256" in chunk_struct
        and "std::string sha256;" not in chunk_struct,
        "checkpoint_chunk_digest_is_fixed_width_binary",
        "the bounded checkpoint no longer owns one heap string per chunk",
    )
    require(
        "kSyncReplicaSourceManifestCheckpointDigestBytes = kSha256DigestBytes" in header
        and "sizeof(SyncReplicaSourceManifestCheckpointChunk) == 40U" in header,
        "checkpoint_chunk_layout_has_compile_time_frontiers",
        "digest width and retained Linux record size cannot drift silently",
    )
    require(
        "sha256(sha256_hex_value)" in codec
        and "sha256_hex_to_binary_or_throw" not in codec
        and "Sha256DigestValue" in header,
        "text_to_binary_construction_validates_canonical_digest",
        "ordinary manifest text cannot enter checkpoint state unchecked",
    )
    require(
        "chunk.sha256.append_binary_to(output);" in codec
        and "append_digest_binary_or_throw" not in codec,
        "serialization_appends_retained_binary_digest_directly",
        "checkpoint publication does not rebuild per-chunk hexadecimal strings",
    )
    parse_body = body(
        codec,
        "parse_sync_replica_source_manifest_checkpoint_or_throw(",
    )
    require(
        "chunk.sha256 = cursor.take_binary_digest(\"chunk\")" in parse_body
        and "digest_binary_to_hex" not in parse_body,
        "parsing_retains_wire_digest_bytes_without_heap_text",
        "maximum-shape restart parsing does not allocate one digest string per chunk",
    )
    require(
        '"anonsync:sync-replica-source-manifest-checkpoint:v2\\n"' in codec
        and ".anonsync-payload-source-manifest-checkpoint-v1" in header,
        "durable_magic_and_reserved_basename_are_unchanged",
        "the representation refactor did not create a new storage generation",
    )
    require(
        all(token in test for token in (
            "7227966f72190f3f30fd2c3b78c5bd6fbc06568b65da3be6b2f34f067317834f",
            "cc5eb04387b25fd6b5cc7f28796d025f67c010a4363a87743cea1ec0cc996ea2",
            "c50edf7819caaf3c51c898d479262473df55c42ff99d8775a43a5f9532261106",
            "active checkpoint changed the sealed rev1010 wire image",
            "complete checkpoint changed the sealed rev1010 wire image",
            "8,192-chunk checkpoint changed the sealed rev1010 wire image",
        )),
        "runtime_binds_three_exact_rev1010_wire_images",
        "active, complete, and maximum records must remain byte-for-byte compatible",
    )
    require(
        "construction.count == 0U" in test
        and "fixed-width checkpoint chunk construction allocated per digest" in test,
        "runtime_proves_zero_post_reserve_chunk_construction_allocations",
        "8,192 digest records do not each enter the allocator",
    )
    require(
        "copy.count == 1U" in test
        and "expected_vector_bytes = kChunks * sizeof(Chunk)" in test
        and "maximum checkpoint chunk copy was not one contiguous allocation" in test,
        "runtime_proves_one_contiguous_maximum_vector_copy",
        "copying restart acceleration performs one bounded vector allocation",
    )
    require(
        "parsing.count < 128U" in test
        and "maximum checkpoint parse allocated once per chunk digest" in test,
        "runtime_rejects_per_chunk_parse_allocation_regression",
        "maximum wire parsing stays far below 8,192 allocator calls",
    )
    install = body(
        service,
        "install_source_content_defined_checkpoint_for_operation_or_throw(",
    )
    require(
        "restored.completed_chunks.emplace_back(" in install
        and "chunk.size_bytes, chunk.sha256" in install
        and "manifest.chunks.emplace_back(chunk.size_bytes, chunk.sha256)" in install
        and "chunk.sha256_hex()" not in install,
        "fixed_digest_crosses_checkpoint_and_manifest_boundaries_without_text_rebuild",
        "rev1015 preserves protocol semantics while removing the last per-chunk text bridge",
    )
    completion = block(
        service,
        "SyncReplicaSourceManifestCheckpoint checkpoint;",
        "std::vector<std::uint64_t> chunk_offsets",
    )
    # The first matching block can be active publication; inspect the exact final loop globally.
    require(
        "for (auto& chunk : projected.chunks)" in service
        and "checkpoint.chunks.emplace_back(chunk.size_bytes, chunk.sha256);" in service
        and "manifest.chunks.emplace_back(chunk.size_bytes, chunk.sha256);" in service
        and "std::move(chunk.sha256)" not in service,
        "fresh_completion_reuses_fixed_digest_for_checkpoint_and_protocol_manifest",
        "the completion bridge performs fixed-width copies without heap-backed digest ownership",
    )
    require(
        "test_fixed_width_chunk_memory_shape" in test
        and "std::string(64U, 'g')" in test
        and "nonhex checkpoint chunk digest was accepted" in test,
        "runtime_covers_layout_allocation_and_invalid_text",
        "the compact representation is tested beyond round-trip success",
    )
    normalized = " ".join(docs.split())
    require(
        all(token in normalized for token in (
            "8,192", "532,480", "860,160", "327,680",
            "zero", "one", "rev1010", "wire", "40-byte")),
        "documentation_records_measured_allocator_differential",
        "the release explains the exact bounded benefit rather than saying merely optimized",
    )
    require(
        all(token in normalized for token in (
            "131,072", "32 MiB", "4 TiB", "O(chunk count)",
            "offset index", "global", "RSS", "Android", "ENOSPC")),
        "documentation_keeps_scale_and_product_nonclaims_explicit",
        "checkpoint compaction is not overstated as solved multi-terabyte memory",
    )
    require(
        "anonsync_sync_replica_source_manifest_checkpoint_memory_source_audit" in cmake,
        "focused_rev1011_audit_is_registered",
        "the representation boundary participates in CTest",
    )
    require(
        "SOURCE_MANIFEST_CHECKPOINT_HEAP_COMPACTION_AUDIT_rev1011.md" in verifier
        and "REVISION_NOTES_rev1011.md" in verifier
        and "audit_sync_replica_source_manifest_checkpoint_memory.py" in verifier,
        "release_verifier_requires_complete_rev1011_slice",
        "the package cannot omit implementation rationale or focused audit",
    )
    require(
        "rev1011_source_manifest_checkpoint" in structural,
        "structural_audit_binds_rev1011_representation_boundary",
        "the cumulative authority inventory evolves with the memory refactor",
    )
    require(
        all(token not in docs for token in (
            "VALIDATION_PENDING_REV1011",
            "ARCHIVE_PENDING_REV1011",
            "CODENAME_PENDING_REV1011",
        )),
        "final_release_placeholders_are_sealed",
        "the focused audit cannot pass before exact validation and archive identity exist",
    )
    source_self = Path(__file__).read_text(encoding="utf-8")
    require(
        "lexical-hygiene-not-semantic-proof" in source_self
        and "not semantic proof" in source_self,
        "lexical_audit_disclaims_semantic_authority",
        "runtime and package evidence remain load-bearing",
    )
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
