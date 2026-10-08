#!/usr/bin/env python3
"""Fail-closed source audit for streamed, locale-independent manifest identity."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/security_tuple_digest.hpp"),
    Path("src/security_tuple_digest.cpp"),
    Path("src/sync_manifest_identity.hpp"),
    Path("src/sync_manifest_identity.cpp"),
    Path("src/sync_domain.cpp"),
    Path("tests/sync_manifest_identity_test.cpp"),
    Path("tests/sync_manifest_hash_locale_test.cpp"),
    Path("tools/audit_sync_manifest_identity.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def emit(root: Path, output: Path | None, checks: list[Check], metrics: dict) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-manifest-identity-audit-v1",
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


def slice_between(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    stop = text.find(end, start + len(begin)) if start >= 0 else -1
    return text[start:stop] if start >= 0 and stop > start else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="AnonSync source root",
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
    tuple_header = texts[Path("src/security_tuple_digest.hpp")]
    tuple_owner = texts[Path("src/security_tuple_digest.cpp")]
    identity_header = texts[Path("src/sync_manifest_identity.hpp")]
    identity_owner = texts[Path("src/sync_manifest_identity.cpp")]
    domain = texts[Path("src/sync_domain.cpp")]
    focused = texts[Path("tests/sync_manifest_identity_test.cpp")]
    locale_test = texts[Path("tests/sync_manifest_hash_locale_test.cpp")]
    verifier = texts[Path("tools/verify_release_package.py")]

    invariant_inventory = slice_between(
        cmake,
        "foreach(ANONSYNC_INVARIANT_OWNED_SOURCE",
        "\nendforeach()",
    )
    core_links = slice_between(
        cmake,
        "target_link_libraries(anonsync_core_lib",
        "\nif(ANONSYNC_USE_BUNDLED_SQLITE)",
    )
    sanitizer_inventory = slice_between(
        cmake,
        "set(ANONSYNC_SANITIZER_COMPILE_TARGETS",
        "\n  # Keep the multi-megabyte reviewed amalgamation",
    )
    sanitizer_link_inventory = slice_between(
        cmake,
        "  foreach(tgt\n      anonsync_core",
        "\n    target_link_options(${tgt} PRIVATE -fsanitize=address,undefined)",
    )
    public_digest_gateway = slice_between(
        domain,
        "std::string sync_manifest_entry_digest",
        "\n\nstruct SyncSidecarReviewRepairResetReviewRow",
    )

    require(
        "struct SecurityTupleFieldView final" in tuple_header
        and "std::string_view name" in tuple_header
        and "std::string_view value" in tuple_header,
        "nonowning_tuple_field_view",
        "tuple fields borrow already-frozen names and values without aggregate copies",
    )
    require(
        "update_sha256_with_length_prefixed_security_tuple" in tuple_header
        and "Sha256DigestBuilder& digest" in tuple_header
        and "sha256_length_prefixed_security_tuple" in tuple_header,
        "streaming_and_terminal_tuple_apis",
        "one API extends an existing digest and one finalizes a standalone tuple",
    )
    require(
        '"anonsync-length-prefixed-tuple-v1"' in tuple_owner
        and "std::to_chars" in tuple_owner
        and "digest.update(\":\")" in tuple_owner,
        "exact_locale_free_v1_tuple_framing",
        "v1 prefix and decimal length framing bypass stream locale",
    )
    require(
        all(token not in tuple_owner for token in (
            "std::ostringstream",
            "std::to_string",
            "std::locale",
            "EVP_",
            "OPENSSL_",
        )),
        "tuple_owner_excludes_ambient_formatters",
        "owner has no stream locale, generic decimal formatter, or direct OpenSSL surface",
    )
    require(
        "std::string material" not in tuple_owner
        and "out +=" not in tuple_owner
        and "return sha256_hex" not in tuple_owner,
        "tuple_owner_does_not_materialize_aggregate",
        "framed bytes stream directly into the digest owner",
    )

    required_identity_apis = (
        "digest_sync_chunk_vector",
        "digest_validated_sync_manifest_entry",
        "digest_validated_sync_manifest_entry_version",
        "digest_validated_sync_folder_manifest",
        "digest_validated_sync_mutation_key",
    )
    require(
        all(name in identity_header for name in required_identity_apis),
        "typed_manifest_identity_surface",
        "chunk, entry, version, folder, and mutation identities are explicit APIs",
    )
    require(
        "class DecimalU64 final" in identity_owner
        and "std::to_chars" in identity_owner
        and "std::string_view view() const noexcept" in identity_owner,
        "bounded_locale_free_integer_owner",
        "all identity counters use one fixed-buffer decimal owner",
    )
    require(
        identity_owner.count("Sha256DigestBuilder digest;") >= 3
        and identity_owner.count(
            "update_sha256_with_length_prefixed_security_tuple(") >= 3
        and identity_owner.count("sha256_length_prefixed_security_tuple(") >= 4,
        "nested_aggregates_stream_into_sha256",
        "chunk, lineage, entry-list, and terminal tuple layers stream instead of concatenate",
    )
    identity_domains = (
        "anonsync-sync-chunk-v1",
        "anonsync-sync-lineage-v1",
        "anonsync-sync-folder-manifest-entry-digest-v1",
        "anonsync-sync-manifest-entry-v1",
        "anonsync-sync-manifest-entry-version-v1",
        "anonsync-sync-folder-manifest-v1",
        "anonsync-sync-mutation-key-v1",
    )
    require(
        all(domain_name in identity_owner for domain_name in identity_domains),
        "legacy_domain_separation_preserved",
        "every established manifest identity domain remains explicit",
    )
    require(
        all(token not in identity_owner for token in (
            "sha256_hex(",
            "std::ostringstream",
            "std::to_string",
            "EVP_",
            "OPENSSL_",
            "std::string material",
            "material +=",
        )),
        "identity_owner_excludes_aggregate_materialization",
        "identity implementation cannot fall back to the old nested material strings",
    )
    require(
        "manifest_kind_text_or_throw" in identity_owner
        and "throw std::invalid_argument" in identity_owner
        and 'return "unknown"' not in identity_owner,
        "unknown_manifest_kind_fails_closed",
        "identity minting rejects rather than hashes unknown enum values",
    )
    require(
        len(tuple_owner.splitlines()) <= 90
        and len(identity_owner.splitlines()) <= 180,
        "small_reviewable_identity_leaves",
        f"tuple_lines={len(tuple_owner.splitlines())}, identity_lines={len(identity_owner.splitlines())}",
    )

    require(
        '#include "sync_manifest_identity.hpp"' in domain
        and "std::to_chars" in domain,
        "domain_consumes_identity_owner",
        "monolith delegates manifest identity and uses locale-free integer conversion",
    )
    require(
        all(token not in domain for token in (
            "hex_from_digest",
            "EVP_MD_CTX",
            "EVP_DigestInit_ex",
            "EVP_DigestUpdate",
            "EVP_DigestFinal_ex",
            "EVP_sha256",
            "EVP_MAX_MD_SIZE",
            "std::ostringstream",
            "std::to_string",
        )),
        "domain_excludes_ambient_and_direct_digest_formatting",
        "file hashing no longer owns OpenSSL byte formatting or locale-sensitive streams",
    )
    file_hash_functions = (
        "hash_file_and_build_chunks",
        "hash_existing_regular_file_content_or_throw",
        "read_file_range_and_hash_or_throw",
        "verify_staged_file_matches_entry_or_throw",
    )
    require(
        all(name in domain for name in file_hash_functions)
        and domain.count("Sha256DigestBuilder") >= 5,
        "file_hash_paths_share_digest_builder",
        "scan, range, staged, and existing-file hashes use the canonical digest builder",
    )
    require(
        "const SyncManifestEntry& validated_entry_or_throw" in domain
        and "const SyncFolderManifest& validated_manifest_or_throw" in domain
        and "canonical_entry_or_throw" not in domain
        and "canonical_manifest_or_throw" not in domain,
        "validation_preserves_existing_ownership",
        "validation returns const references instead of copying complete entries or manifests",
    )
    require(
        all(name in public_digest_gateway for name in required_identity_apis[1:])
        and "length_prefixed_security_tuple" not in public_digest_gateway
        and "sha256_hex" not in public_digest_gateway,
        "single_manifest_identity_gateway",
        "public digest APIs validate then delegate without reconstructing security bytes",
    )

    require(
        "add_library(anonsync_security_tuple_digest STATIC" in cmake
        and "add_library(anonsync_sync_manifest_identity STATIC" in cmake
        and "anonsync_security_tuple_digest" in identity_owner + cmake,
        "separately_linked_identity_layers",
        "tuple framing and manifest identity are independently compiled owners",
    )
    require(
        "anonsync_sync_manifest_identity" in core_links,
        "core_links_manifest_identity_owner",
        "the production domain consumes the extracted library",
    )
    require(
        '"${ANONSYNC_SECURITY_TUPLE_DIGEST_SOURCE}"' in invariant_inventory
        and '"${ANONSYNC_SYNC_MANIFEST_IDENTITY_SOURCE}"' in invariant_inventory,
        "identity_sources_in_invariant_inventory",
        "extracted owners cannot drift back into the core source list",
    )
    require(
        all(token in cmake for token in (
            "add_executable(anonsync_sync_manifest_identity_test",
            "add_executable(anonsync_sync_manifest_hash_locale_test",
            "add_test(NAME anonsync_sync_manifest_identity_test",
            "add_test(NAME anonsync_sync_manifest_hash_locale_test",
        )),
        "focused_runtime_tests_registered",
        "compatibility and integrated hostile-locale corpora are CTest targets",
    )
    require(
        all(target in sanitizer_inventory for target in (
            "anonsync_security_tuple_digest",
            "anonsync_sync_manifest_identity",
            "anonsync_sync_manifest_identity_test",
            "anonsync_sync_manifest_hash_locale_test",
        )),
        "identity_targets_in_sanitizer_compile_inventory",
        "owners and both focused executables participate in sanitizer compilation",
    )
    require(
        all(target in sanitizer_link_inventory for target in (
            "anonsync_sync_manifest_identity_test",
            "anonsync_sync_manifest_hash_locale_test",
        )),
        "identity_executables_in_sanitizer_link_inventory",
        "both instrumented focused executables link the ASan and UBSan runtimes",
    )

    require(
        "legacy_tuple(" in focused
        and "legacy_entry_digest(" in focused
        and "legacy_manifest_digest(" in focused
        and "sha256_hex(tuple_reference)" in focused,
        "independent_legacy_byte_oracle",
        "focused tests independently reconstruct pre-refactor bytes",
    )
    require(
        'std::string binary_value("a\\0b:c", 5)' in focused
        and "GroupEveryDigit" in focused
        and "std::numeric_limits<std::uint64_t>::max()" in focused,
        "binary_locale_and_integer_extremes",
        "tuple NULs, hostile grouping, and maximum counters are covered",
    )
    require(
        "constexpr std::size_t kChunkCount = 20000" in focused
        and "large chunk aggregate must be deterministic" in focused,
        "large_aggregate_streaming_corpus",
        "a 20,000-chunk identity exercises bounded streaming behavior",
    )
    require(
        "static_cast<SyncManifestEntryKind>(99)" in focused
        and "unknown entry kinds must fail closed" in focused,
        "unknown_kind_runtime_corpus",
        "focused tests prove malformed enum values are rejected",
    )
    require(
        "build_sync_folder_manifest_from_directory" in locale_test
        and "GroupEveryDigit" in locale_test
        and "is_lowercase_sha256_hex(chunk.sha256)" in locale_test,
        "integrated_scan_locale_corpus",
        "real directory scanning proves canonical whole-file and chunk digest text",
    )
    require(
        "run_sync_fake_peer_file_fetch_session" in locale_test
        and "session.content_converged" in locale_test
        and "copied_bytes == bytes" in locale_test,
        "integrated_transfer_locale_corpus",
        "range hashing, staged verification, and materialization run under hostile locale",
    )
    require(
        "revision_number is not None and revision_number >= 857" in verifier
        and all(path in verifier for path in (
            "src/security_tuple_digest.hpp",
            "src/security_tuple_digest.cpp",
            "src/sync_manifest_identity.hpp",
            "src/sync_manifest_identity.cpp",
            "tests/sync_manifest_identity_test.cpp",
            "tests/sync_manifest_hash_locale_test.cpp",
            "tools/audit_sync_manifest_identity.py",
        )),
        "release_verifier_revision_gate",
        "rev0857 packages cannot omit identity owners, corpora, or audit while older parents remain valid",
    )

    metrics = {
        "tuple_owner_lines": len(tuple_owner.splitlines()),
        "identity_owner_lines": len(identity_owner.splitlines()),
        "domain_lines": len(domain.splitlines()),
        "identity_stream_update_calls": identity_owner.count(
            "update_sha256_with_length_prefixed_security_tuple("
        ),
        "direct_domain_evp_mentions": len(re.findall(r"\\bEVP_[A-Za-z0-9_]+", domain)),
        "focused_test_check_increment_sites": focused.count(", checks);"),
        "locale_test_check_increment_sites": locale_test.count(", checks);"),
    }
    return emit(root, args.json, checks, metrics)


if __name__ == "__main__":
    raise SystemExit(main())
