#!/usr/bin/env python3
"""Lexical hygiene audit for rev1013 fixed binary source manifests.

Source spelling is not semantic proof. Compiler, sanitizer, runtime allocator,
wire-image, reconstruction, and package evidence remain load-bearing.
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
    Path("FIXED_BINARY_WIRE_MANIFEST_AND_SHARED_DIGEST_CODEC_AUDIT_rev1013.md"),
    Path("REVISION_NOTES_rev1013.md"),
    Path("src/sha256_digest.hpp"),
    Path("src/sha256_digest.cpp"),
    Path("src/sync_replica_reconciliation_protocol.hpp"),
    Path("src/sync_replica_reconciliation_protocol.cpp"),
    Path("src/sync_replica_reconciliation_compact_manifest.hpp"),
    Path("src/sync_replica_reconciliation_compact_manifest.cpp"),
    Path("src/sync_replica_source_manifest_checkpoint.hpp"),
    Path("src/sync_replica_source_manifest_checkpoint.cpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("tests/sync_replica_reconciliation_compact_manifest_test.cpp"),
    Path("tests/sync_replica_reconciliation_protocol_test.cpp"),
    Path("tests/sync_replica_source_manifest_checkpoint_test.cpp"),
    Path("tools/audit_sync_replica_fixed_binary_manifest.py"),
    Path("tools/audit_sync_replica_compact_source_manifest_cache.py"),
    Path("tools/audit_sync_replica_source_manifest_checkpoint_memory.py"),
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


def block(text: str, start_token: str, end_token: str) -> str:
    start = text.find(start_token)
    if start < 0:
        return ""
    end = text.find(end_token, start + len(start_token))
    if end < 0:
        return ""
    return text[start:end]


def normalized(text: str) -> str:
    return " ".join(text.split())


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [item.check_id for item in checks if not item.passed]
    report = {
        "format": "anonsync-fixed-binary-source-manifest-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove allocation counts, ABI layout, "
            "wire or durable compatibility, runtime authority, sanitizer "
            "cleanliness, whole-process RSS, or package identity"
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
    bootstrap_path = next(
        (path for path in bootstrap_candidates if path.is_file()), None
    )
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
    digest_h = text["src/sha256_digest.hpp"]
    digest_cpp = text["src/sha256_digest.cpp"]
    protocol_h = text["src/sync_replica_reconciliation_protocol.hpp"]
    protocol_cpp = text["src/sync_replica_reconciliation_protocol.cpp"]
    compact_h = text["src/sync_replica_reconciliation_compact_manifest.hpp"]
    compact_cpp = text["src/sync_replica_reconciliation_compact_manifest.cpp"]
    checkpoint_h = text["src/sync_replica_source_manifest_checkpoint.hpp"]
    checkpoint_cpp = text["src/sync_replica_source_manifest_checkpoint.cpp"]
    service = text["src/sync_replica_reconciliation_service.cpp"]
    compact_test = text["tests/sync_replica_reconciliation_compact_manifest_test.cpp"]
    protocol_test = text["tests/sync_replica_reconciliation_protocol_test.cpp"]
    checkpoint_test = text["tests/sync_replica_source_manifest_checkpoint_test.cpp"]
    cmake = text["CMakeLists.txt"]
    verifier = text["tools/verify_release_package.py"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    docs = (
        text["README.md"] + "\n"
        + text["FIXED_BINARY_WIRE_MANIFEST_AND_SHARED_DIGEST_CODEC_AUDIT_rev1013.md"]
        + "\n" + text["REVISION_NOTES_rev1013.md"] + "\n" + bootstrap
    )

    digest_class = block(
        digest_h, "class Sha256DigestValue final", "static_assert(sizeof(Sha256DigestValue)"
    )
    require(
        "std::array<std::uint8_t, kSha256DigestBytes> bytes_" in digest_class
        and "std::string" not in block(digest_class, "private:", "};"),
        "shared_digest_owns_only_fixed_binary_bytes",
        "the shared digest has no heap-backed member",
    )
    require(
        "sizeof(Sha256DigestValue) == kSha256DigestBytes" in digest_h
        and "std::is_trivially_copyable_v<Sha256DigestValue>" in digest_h
        and "std::is_standard_layout_v<Sha256DigestValue>" in digest_h,
        "shared_digest_layout_is_compile_time_fixed",
        "size, copy shape, and layout cannot drift silently",
    )
    assignment = body(digest_cpp, "Sha256DigestValue::operator=(")
    require(
        "const auto decoded = decode_lowercase_sha256_or_throw" in assignment
        and assignment.find("bytes_ = decoded") > assignment.find("decode_lowercase_sha256_or_throw"),
        "shared_digest_assignment_has_strong_canonicality_boundary",
        "failed text decoding cannot partially mutate the retained digest",
    )
    require(
        "append_lowercase_hex_to" in digest_cpp
        and "append_binary_to" in digest_cpp
        and "update_lowercase_hex" in digest_cpp
        and "equals_lowercase_hex" in digest_cpp,
        "shared_digest_exposes_explicit_text_binary_and_digest_boundaries",
        "callers do not need private duplicate codecs",
    )

    delta_chunk = block(
        protocol_h,
        "struct SyncReplicaReconciliationDeltaChunk final",
        "struct SyncReplicaReconciliationDeltaManifest final",
    )
    require(
        "Sha256DigestValue sha256" in delta_chunk
        and "std::string sha256" not in delta_chunk,
        "wire_manifest_chunk_uses_shared_fixed_digest",
        "a complete typed manifest has no per-chunk string owner",
    )
    require(
        "sizeof(SyncReplicaReconciliationDeltaChunk) == 40U" in protocol_h
        and "std::is_trivially_copyable_v<SyncReplicaReconciliationDeltaChunk>" in protocol_h,
        "wire_manifest_chunk_is_one_fixed_40_byte_record",
        "vector copy and materialization retain one contiguous allocation shape",
    )
    require(
        "kSyncReplicaReconciliationProtocolVersion = 9U" in protocol_h,
        "reconciliation_protocol_generation_is_unchanged",
        "the in-memory representation does not masquerade as a new wire generation",
    )
    parser = body(
        protocol_cpp,
        "parse_response_body_borrowing_payloads_without_validation_or_throw(",
    )
    require(
        'reader.read_view(\n                        kSyncManifestSha256TextBytes' in parser
        and "payload_content_defined_chunk_sha256" in parser,
        "wire_parser_borrows_digest_text_into_fixed_value",
        "decode does not allocate a temporary string for each digest",
    )
    require(
        "void append_framed(\n    std::string& out,\n    const Sha256DigestValue& digest)" in protocol_cpp
        and "digest.append_lowercase_hex_to(out)" in protocol_cpp,
        "wire_serializer_emits_fixed_digest_without_temporary_string",
        "generation-9 framing is produced directly into the final body",
    )
    require(
        "void append_digest_framed(\n    Sha256DigestBuilder& destination,\n    const Sha256DigestValue& digest)" in protocol_cpp
        and "digest.update_lowercase_hex(destination)" in protocol_cpp,
        "semantic_manifest_digest_uses_same_fixed_value",
        "wire and semantic digest paths cannot drift through separate text owners",
    )
    manifest_validator = body(
        protocol_cpp, "validate_delta_manifest_view_or_throw("
    )
    require(
        "is_lowercase_sha256_hex" not in manifest_validator
        and "chunk_size == 0U" in manifest_validator,
        "typed_digest_moves_syntax_out_of_late_manifest_validation",
        "extent, count, parameter, and coverage checks remain explicit",
    )

    compact_chunk = block(
        compact_h,
        "struct SyncReplicaReconciliationCompactManifestChunk final",
        "// Process-local exact source-manifest cache",
    )
    compact_aliases_cumulative = (
        "using SyncReplicaReconciliationCompactManifestChunk =" in compact_h
        and "SyncReplicaReconciliationCumulativeDeltaChunk" in compact_h
    )
    cumulative_chunk = block(
        protocol_h,
        "struct SyncReplicaReconciliationCumulativeDeltaChunk final",
        "// Borrowed complete manifest used only while one response frame is assembled.",
    )
    retained_chunk = cumulative_chunk if compact_aliases_cumulative else compact_chunk
    require(
        "Sha256DigestValue sha256" in retained_chunk
        and "sizeof(SyncReplicaReconciliationCompactManifestChunk) == 40U" in compact_h
        and "std::is_trivially_copyable_v" in compact_h,
        "compact_cache_reuses_shared_fixed_digest",
        "the resident cache and wire object share one bounded representation",
    )
    require(
        "digest_bytes_or_throw" not in compact_cpp
        and "digest_hex(" not in compact_cpp
        and "compact.chunks_.push_back({covered, chunk.sha256})" in compact_cpp
        and "chunk.sha256" in compact_cpp,
        "compact_cache_private_digest_codec_is_removed",
        "conversion and materialization copy fixed values rather than rebuilding text",
    )

    checkpoint_chunk = block(
        checkpoint_h,
        "struct SyncReplicaSourceManifestCheckpointChunk final",
        "// One bounded acceleration record",
    )
    require(
        "Sha256DigestValue sha256" in checkpoint_chunk
        and "sizeof(SyncReplicaSourceManifestCheckpointChunk) == 40U" in checkpoint_h
        and "std::is_trivially_copyable_v" in checkpoint_h,
        "durable_checkpoint_reuses_shared_fixed_digest",
        "restart acceleration keeps its released bounded record width",
    )
    require(
        "sha256_hex_to_binary_or_throw" not in checkpoint_cpp
        and "digest_binary_to_hex" not in checkpoint_cpp
        and "chunk.sha256.append_binary_to(output)" in checkpoint_cpp
        and 'chunk.sha256 = cursor.take_binary_digest("chunk")' in checkpoint_cpp,
        "checkpoint_private_digest_codec_is_removed",
        "durable bytes cross the shared binary boundary without text allocation",
    )
    require(
        '"anonsync:sync-replica-source-manifest-checkpoint:v2\\n"' in checkpoint_cpp
        and ".anonsync-payload-source-manifest-checkpoint-v1" in checkpoint_h,
        "checkpoint_magic_and_reserved_name_are_unchanged",
        "the shared codec does not create a new durable generation",
    )

    require(
        ".equals_lowercase_hex(wire.chunk_sha256)" in service
        and "target_chunk.sha256" in service,
        "shipping_apply_path_compares_fixed_digest_without_text_materialization",
        "delta reuse and full-chunk verification retain the compact representation",
    )

    require(
        all(token in compact_test for token in (
            "parser_shape.count == 1U",
            "parser_shape.requested_bytes == expected_wire_vector_bytes",
            "construction.count == 1U",
            "copy.count == 1U",
            "materialization.count == 1U",
            "lookup.count == 0U",
            "parsed_shape == wire.chunks",
            "materialized == wire",
        )),
        "runtime_binds_one_allocation_receive_cache_copy_and_materialization",
        "the 8,192-record allocation shape is executable",
    )
    require(
        "malformed fixed-width digest assignment was accepted" in compact_test
        and "failed fixed-width digest assignment changed the prior value" in compact_test,
        "runtime_binds_canonical_assignment_and_strong_failure_guarantee",
        "invalid text cannot survive in a live manifest chunk",
    )
    require(
        all(token in protocol_test for token in (
            "1e6ae4e901d86679e4219ad764dbb290d1fcb4a2f7520490f8a75b6045efab51",
            "29304b77ca55367bbcd259c9119cdc916a2ca918fe0ae5836560a6a673fa8119",
            "sealed rev1012 request frame",
            "sealed rev1012 response frame",
        )),
        "runtime_binds_exact_rev1012_generation9_wire_images",
        "request and response framing remain byte-for-byte compatible",
    )
    require(
        all(token in checkpoint_test for token in (
            "7227966f72190f3f30fd2c3b78c5bd6fbc06568b65da3be6b2f34f067317834f",
            "cc5eb04387b25fd6b5cc7f28796d025f67c010a4363a87743cea1ec0cc996ea2",
            "c50edf7819caaf3c51c898d479262473df55c42ff99d8775a43a5f9532261106",
        )),
        "runtime_retains_exact_rev1010_checkpoint_images",
        "shared codec refactoring does not alter durable restart bytes",
    )

    require(
        "anonsync_sync_replica_fixed_binary_manifest_source_audit" in cmake
        and "audit_sync_replica_fixed_binary_manifest.py" in cmake,
        "focused_rev1013_audit_is_registered",
        "the representation boundary participates in CTest",
    )
    require(
        "FIXED_BINARY_WIRE_MANIFEST_AND_SHARED_DIGEST_CODEC_AUDIT_rev1013.md" in verifier
        and "REVISION_NOTES_rev1013.md" in verifier
        and "audit_sync_replica_fixed_binary_manifest.py" in verifier,
        "release_verifier_requires_complete_rev1013_slice",
        "the package cannot omit code, rationale, notes, or focused audit",
    )
    require(
        "rev1013_fixed_binary_manifest" in structural,
        "structural_audit_binds_rev1013_representation_boundary",
        "the cumulative authority inventory evolves with the memory correction",
    )

    prose = normalized(docs)
    require(
        all(token in prose for token in (
            "8,192", "860,160", "532,480", "327,680", "one",
            "40 bytes", "32-byte", "generation 9", "rev1012",
        )),
        "documentation_records_exact_allocator_and_compatibility_boundary",
        "the release states measured counts rather than merely optimized",
    )
    require(
        all(token in prose for token in (
            "4 TiB", "131,072", "32 MiB", "1 GiB", "O(chunk count)",
            "RSS", "page-cache", "Android", "ENOSPC", "rename/move",
            "Tor", "I2P", "global", "multi-share",
        )),
        "documentation_keeps_scale_and_product_nonclaims_explicit",
        "one allocation correction is not overstated as product completion",
    )
    require(
        all(token not in docs for token in (
            "VALIDATION_PENDING_REV1013",
            "ARCHIVE_PENDING_REV1013",
            "CODENAME_PENDING_REV1013",
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
