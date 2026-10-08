#!/usr/bin/env python3
"""Fail-closed source audit for preallocation-safe manifest reconstruction."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sha256_digest.hpp"),
    Path("src/sync_manifest_validation.hpp"),
    Path("src/sync_manifest_validation.cpp"),
    Path("src/sync_manifest_stream_decoder.hpp"),
    Path("src/sync_manifest_stream_decoder.cpp"),
    Path("src/sync_sqlite_support.hpp"),
    Path("src/sync_sqlite_support.cpp"),
    Path("src/sync_domain.cpp"),
    Path("src/sync_peer_ingestion.cpp"),
    Path("tests/sync_manifest_stream_decoder_test.cpp"),
    Path("tools/audit_sync_manifest_stream_decoder.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def section(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    stop = text.find(end, start + len(begin)) if start >= 0 else -1
    return text[start:stop] if start >= 0 and stop > start else ""


def emit(root: Path, output: Path | None, checks: list[Check], metrics: dict) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-manifest-stream-decoder-audit-v1",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": metrics,
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
        "--root", type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    if missing:
        return emit(root, args.json, checks, {})

    texts = {path: (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    cmake = texts[Path("CMakeLists.txt")]
    sha_header = texts[Path("src/sha256_digest.hpp")]
    validation_header = texts[Path("src/sync_manifest_validation.hpp")]
    validation_owner = texts[Path("src/sync_manifest_validation.cpp")]
    decoder_header = texts[Path("src/sync_manifest_stream_decoder.hpp")]
    decoder_owner = texts[Path("src/sync_manifest_stream_decoder.cpp")]
    sqlite_header = texts[Path("src/sync_sqlite_support.hpp")]
    sqlite_owner = texts[Path("src/sync_sqlite_support.cpp")]
    domain = texts[Path("src/sync_domain.cpp")]
    peer = texts[Path("src/sync_peer_ingestion.cpp")]
    focused = texts[Path("tests/sync_manifest_stream_decoder_test.cpp")]
    verifier = texts[Path("tools/verify_release_package.py")]

    begin = section(
        decoder_owner,
        "SyncValidationResult SyncManifestEntryStreamDecoder::begin(",
        "\n\nSyncValidationResult SyncManifestEntryStreamDecoder::append_chunk(",
    )
    append_chunk = section(
        decoder_owner,
        "SyncValidationResult SyncManifestEntryStreamDecoder::append_chunk(",
        "\n\nSyncValidationResult SyncManifestEntryStreamDecoder::append_lineage(",
    )
    append_lineage = section(
        decoder_owner,
        "SyncValidationResult SyncManifestEntryStreamDecoder::append_lineage(",
        "\n\nSyncValidationResult SyncManifestEntryStreamDecoder::finish(",
    )
    finish = section(
        decoder_owner,
        "SyncValidationResult SyncManifestEntryStreamDecoder::finish(",
        "\n\nbool SyncManifestEntryStreamDecoder::active()",
    )
    failure = section(
        decoder_owner,
        "SyncValidationResult SyncManifestEntryStreamDecoder::fail(",
        "\n\n}  // namespace anonsync",
    )
    domain_loader = section(
        domain,
        "SyncManifestEntry load_sync_session_manifest_entry_from_checkpoint_or_throw(",
        "\n\nstd::uint64_t count_sync_session_checkpoint_file_transfer_intents_or_throw(",
    )
    peer_loader = section(
        peer,
        "bool load_peer_sidecar_remote_file_entry_for_path_or_throw(",
        "\n\nbool peer_sidecar_apply_entry_routes_remote_file_bytes_to_staging(",
    )
    invariant_inventory = section(
        cmake,
        "foreach(ANONSYNC_INVARIANT_OWNED_SOURCE",
        "\nendforeach()",
    )
    core_sources = section(
        cmake,
        "set(ANONSYNC_CORE_SOURCES",
        "\nforeach(ANONSYNC_INVARIANT_OWNED_SOURCE",
    )
    core_links = section(
        cmake,
        "target_link_libraries(anonsync_core_lib",
        "\nif(ANONSYNC_USE_BUNDLED_SQLITE)",
    )
    sanitizer_compile = section(
        cmake,
        "set(ANONSYNC_SANITIZER_COMPILE_TARGETS",
        "\n  # Keep the multi-megabyte reviewed amalgamation",
    )
    sanitizer_link = section(
        cmake,
        "  foreach(tgt\n      anonsync_core",
        "\n    target_link_options(${tgt} PRIVATE -fsanitize=address,undefined)",
    )

    require(
        "struct SyncManifestEntryStreamHeader final" in decoder_header
        and decoder_header.count("std::string_view") >= 5
        and "declared_chunk_count" in decoder_header
        and "declared_lineage_count" in decoder_header,
        "borrowed_header_with_declared_shape",
        "scalar observations are borrowed while nested cardinality is explicit",
    )
    require(
        decoder_header.count("SyncManifestEntryStreamDecoder(") >= 3
        and decoder_header.count(") = delete;") >= 4
        and "operator=(" in decoder_header,
        "single_location_nonmovable_owner",
        "an active reconstruction cannot be copied or relocated",
    )
    require(
        all(token in decoder_header for token in (
            "enum class State", "Empty,", "Active,", "Failed,", "Finished,"
        ))
        and all(token in decoder_owner for token in (
            "State::Empty", "State::Active", "State::Failed", "State::Finished"
        )),
        "explicit_single_use_state_machine",
        "empty, active, failed, and committed states are represented",
    )
    require(
        "class SyncManifestResourceBudget final" in validation_header
        and all(token in validation_header for token in (
            "admit_entry_count", "admit_entry_shape", "admit_metadata_bytes"
        )),
        "shared_typed_resource_budget",
        "typed traversal and streaming decode share one checked accounting owner",
    )
    require(
        all(token in validation_header for token in (
            "kSyncManifestIdMaxBytes",
            "kSyncManifestRelativePathMaxBytes",
            "kSyncManifestSha256TextBytes",
            "kSyncManifestKindTextMaxBytes",
        ))
        and "kSyncManifestIdMaxBytes" in validation_owner
        and "kSyncManifestRelativePathMaxBytes" in validation_owner,
        "named_scalar_copy_ceilings",
        "SQLite copy ceilings and semantic validators can consume one policy spelling",
    )
    require(
        "is_lowercase_sha256_hex(std::string_view value) noexcept" in sha_header,
        "nonowning_sha256_text_validation",
        "stream rows do not allocate merely to validate digest text",
    )

    require(
        begin.find("admit_entry_count") < begin.find("admit_entry_shape")
        < begin.find("validate_header_semantics")
        < begin.find("proposed.folder_id.assign"),
        "admission_precedes_scalar_retention",
        "counts, bytes, and semantics are accepted before any header string copy",
    )
    require(
        "reserve(" not in decoder_owner,
        "no_declared_count_reservation",
        "untrusted declared cardinality cannot trigger a speculative bulk allocation",
    )
    require(
        append_chunk.find("chunks_accepted() >= declared_chunk_count_")
        < append_chunk.find("admit_metadata_bytes")
        < append_chunk.find("candidate_.chunks.push_back"),
        "chunk_count_and_bytes_precede_growth",
        "extra or over-budget chunk rows fail before vector growth",
    )
    require(
        all(token in append_chunk for token in (
            "offset != next_chunk_offset_",
            "length == 0U",
            "is_lowercase_sha256_hex(sha256)",
            "max() - next_chunk_offset_",
        )),
        "chunk_semantics_checked_incrementally",
        "contiguity, positivity, digest spelling, and overflow fail at the event boundary",
    )
    require(
        append_lineage.find("lineage_entries_accepted() >= declared_lineage_count_")
        < append_lineage.find("admit_metadata_bytes")
        < append_lineage.find("candidate_.lineage.push_back"),
        "lineage_count_and_bytes_precede_growth",
        "extra or over-budget lineage rows fail before vector growth",
    )
    require(
        all(token in append_lineage for token in (
            "sync_id_is_valid(device_id)",
            "counter == 0U",
            "device_id.compare(candidate_.lineage.back().device_id) <= 0",
        )),
        "lineage_semantics_checked_incrementally",
        "identity, positive counters, uniqueness, and ordering fail at the event boundary",
    )
    require(
        finish.find("chunks_accepted() != declared_chunk_count_")
        < finish.find("validate_sync_manifest_entry_with_limits")
        < finish.find("usage_equal")
        < finish.find("out = std::move(candidate_)")
        < finish.find("state_ = State::Finished"),
        "commit_after_exact_independent_validation",
        "row counts, typed semantics, and independent accounting agree before publication",
    )
    require(
        "candidate_ = SyncManifestEntry{};" in failure
        and "failure_reason_ = std::move(reason);" in failure
        and "state_ = State::Failed;" in failure,
        "sticky_failure_discards_partial_value",
        "the first malformed event revokes and clears retained partial state",
    )
    require(
        all(token not in decoder_owner for token in (
            "std::ostringstream", "std::locale", "std::regex", "std::to_string"
        )),
        "decoder_excludes_ambient_formatting",
        "the boundary has no stream-locale or regex dependency",
    )

    require(
        "std::uint64_t max_bytes" in sqlite_header
        and "persistence::sqlite_exact_text_or_throw(\n        stmt, column, label, max_bytes)" in sqlite_owner,
        "bounded_exact_sqlite_text_gateway",
        "callers can reject oversized persistent text before constructing its C++ copy",
    )
    require(
        '#include "sync_manifest_stream_decoder.hpp"' in domain
        and "e.chunk_count, e.lineage_count" in domain_loader
        and domain_loader.find("expected_chunks") < domain_loader.find("const std::string folder_id"),
        "domain_loader_observes_shape_first",
        "checkpoint cardinality is frozen before bounded scalar copies",
    )
    require(
        domain_loader.count("kSyncManifestSha256TextBytes") >= 4
        and domain_loader.count("kSyncManifestIdMaxBytes") >= 3
        and "kSyncManifestKindTextMaxBytes" in domain_loader,
        "domain_loader_bounds_every_manifest_text",
        "ids, kind, content hash, stored identities, and row hashes have semantic caps",
    )
    require(
        "SyncManifestEntryStreamDecoder decoder;" in domain_loader
        and "decoder.append_chunk" in domain_loader
        and "decoder.append_lineage" in domain_loader
        and "decoder.finish(entry)" in domain_loader
        and ".chunks.push_back" not in domain_loader
        and ".lineage.push_back" not in domain_loader,
        "domain_loader_has_one_streaming_reconstruction",
        "the monolith cannot rebuild nested vectors outside the owner",
    )
    require(
        '#include "sync_manifest_stream_decoder.hpp"' in peer
        and peer_loader.find("expected_chunks") < peer_loader.find("const std::string folder_id"),
        "peer_loader_observes_shape_first",
        "peer-side recovery freezes cardinality before scalar retention",
    )
    require(
        peer_loader.count("kSyncManifestSha256TextBytes") >= 4
        and peer_loader.count("kSyncManifestIdMaxBytes") >= 3
        and "kSyncManifestKindTextMaxBytes" in peer_loader,
        "peer_loader_bounds_every_manifest_text",
        "peer checkpoint reconstruction applies the same scalar copy ceilings",
    )
    require(
        "SyncManifestEntryStreamDecoder decoder;" in peer_loader
        and "decoder.append_chunk" in peer_loader
        and "decoder.append_lineage" in peer_loader
        and "decoder.finish(decoded)" in peer_loader
        and ".chunks.push_back" not in peer_loader
        and ".lineage.push_back" not in peer_loader,
        "peer_loader_has_one_streaming_reconstruction",
        "the duplicate unbounded row loops have been removed",
    )
    require(
        peer_loader.find("sync_manifest_entry_digest(decoded)")
        < peer_loader.find("out = std::move(decoded)")
        and "out = SyncManifestEntry{};" not in peer_loader,
        "peer_output_published_after_digest",
        "missing, malformed, and digest-mismatched rows leave caller output unchanged",
    )

    require(
        "add_library(anonsync_sync_manifest_stream_decoder STATIC" in cmake
        and "${ANONSYNC_SYNC_MANIFEST_STREAM_DECODER_SOURCE}" in invariant_inventory
        and "src/sync_manifest_stream_decoder.cpp" not in core_sources,
        "separate_invariant_owned_decoder_target",
        "the decoder remains a small independently compiled boundary",
    )
    require(
        "anonsync_sync_manifest_stream_decoder" in core_links,
        "core_links_stream_decoder",
        "both production reconstruction paths resolve through the extracted owner",
    )
    require(
        "add_executable(anonsync_sync_manifest_stream_decoder_test" in cmake
        and "add_test(NAME anonsync_sync_manifest_stream_decoder_test" in cmake,
        "focused_test_registered",
        "the focused corpus is in build and CTest inventories",
    )
    require(
        "anonsync_sync_manifest_stream_decoder" in sanitizer_compile
        and "anonsync_sync_manifest_stream_decoder_test" in sanitizer_compile
        and "anonsync_sync_manifest_stream_decoder_test" in sanitizer_link,
        "sanitizer_compile_and_link_inventory",
        "owner and test receive compile and executable sanitizer instrumentation",
    )
    require(
        "anonsync_sync_manifest_stream_decoder_source_audit" in cmake
        and "audit_sync_manifest_stream_decoder.py" in cmake
        and "${Python3_EXECUTABLE} -B -S" in cmake,
        "source_audit_registered_without_site_init",
        "the structural proof is a hermetic registered test",
    )

    test_phrases = (
        "begin does not publish a partial output",
        "begin freezes admitted scalar bytes exactly once",
        "declared chunk count is rejected before allocation",
        "metadata is rejected before the final row is copied",
        "failure is sticky and discards retained partial rows",
        "extra chunk row fails before vector growth",
        "extra lineage row fails before vector growth",
        "failed finish leaves caller output unchanged",
        "coverage rejection never publishes partial entry",
    )
    require(
        all(phrase in focused for phrase in test_phrases),
        "focused_preallocation_and_commit_corpus",
        "freeze, exhaustion, sticky failure, row excess, and success-only publication are executable",
    )
    require(
        "sync manifest stream decoder checks=" in focused
        and focused.count("SyncManifestEntryStreamDecoder decoder") >= 15,
        "broad_direct_owner_corpus",
        "the owner is exercised through independent fresh state machines",
    )
    require(
        "revision_number >= 859" in verifier
        and "sync_manifest_stream_decoder" in verifier,
        "release_verifier_requires_rev0859_boundary",
        "publication cannot omit the decoder, focused test, or structural audit",
    )

    metrics = {
        "decoder_header_lines": len(decoder_header.splitlines()),
        "decoder_owner_lines": len(decoder_owner.splitlines()),
        "focused_test_lines": len(focused.splitlines()),
        "domain_loader_lines": len(domain_loader.splitlines()),
        "peer_loader_lines": len(peer_loader.splitlines()),
        "domain_direct_nested_pushes": domain_loader.count(".push_back"),
        "peer_direct_nested_pushes": peer_loader.count(".push_back"),
    }
    return emit(root, args.json, checks, metrics)


if __name__ == "__main__":
    raise SystemExit(main())
