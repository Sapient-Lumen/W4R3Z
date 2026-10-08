#!/usr/bin/env python3
"""Fail-closed source audit for bounded manifest and portable-path validation."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_manifest_validation.hpp"),
    Path("src/sync_manifest_validation.cpp"),
    Path("src/sync_domain.cpp"),
    Path("tests/sync_manifest_validation_test.cpp"),
    Path("tools/audit_sync_manifest_validation.py"),
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
        "format": "anonsync-sync-manifest-validation-audit-v1",
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
        "--root",
        type=Path,
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
    header = texts[Path("src/sync_manifest_validation.hpp")]
    owner = texts[Path("src/sync_manifest_validation.cpp")]
    domain = texts[Path("src/sync_domain.cpp")]
    focused = texts[Path("tests/sync_manifest_validation_test.cpp")]
    verifier = texts[Path("tools/verify_release_package.py")]

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
    normalization = section(
        owner,
        "SyncValidationResult normalize_sync_relative_path(",
        "\n\nSyncValidationResult validate_sync_manifest_entry_with_limits(",
    )
    manifest_preflight = section(
        owner,
        "SyncValidationResult preflight_manifest_shape(",
        "\n\n[[nodiscard]] SyncValidationResult validate_entry_semantics(",
    )

    required_limit_fields = (
        "max_entries",
        "max_chunks_per_entry",
        "max_lineage_entries_per_entry",
        "max_total_chunks",
        "max_total_lineage_entries",
        "max_total_path_bytes",
        "max_total_metadata_bytes",
    )
    require(
        "struct SyncManifestResourceLimits final" in header
        and all(field in header for field in required_limit_fields),
        "typed_resource_limits",
        "entry, nested-cardinality, path-byte, and metadata-byte ceilings are one typed policy",
    )
    require(
        "struct SyncManifestResourceUsage final" in header
        and all(field in header for field in (
            "entries", "chunks", "lineage_entries", "path_bytes", "metadata_bytes"
        )),
        "typed_resource_usage",
        "successful validation can publish exact bounded resource evidence",
    )
    require(
        "sync_manifest_default_resource_limits() noexcept" in header,
        "named_default_policy",
        "production wrappers consume one reviewable default limit set",
    )
    require(
        "validate_sync_manifest_entry_with_limits" in header
        and "validate_sync_folder_manifest_with_limits" in header,
        "testable_limit_surface",
        "focused tests can exercise exhaustion without allocating default-scale vectors",
    )
    require(
        "std::string_view" in header and "sync_id_is_valid" in header,
        "nonowning_identifier_boundary",
        "portable identifier validation does not require string copies",
    )

    require(
        "Phase one observes only vector cardinality" in manifest_preflight
        and "Phase two may inspect nested elements" in manifest_preflight,
        "two_phase_manifest_preflight",
        "nested contents are not traversed until aggregate counts are bounded",
    )
    require(
        manifest_preflight.find("entry.chunks.size()")
        < manifest_preflight.find("for (const SyncChunkRange& chunk"),
        "chunk_cardinality_precedes_chunk_traversal",
        "oversized chunk vectors fail before element inspection",
    )
    require(
        manifest_preflight.find("entry.lineage.size()")
        < manifest_preflight.find("for (const SyncVersionLineageEntry& lineage"),
        "lineage_cardinality_precedes_lineage_traversal",
        "oversized lineage vectors fail before element inspection",
    )
    require(
        "std::numeric_limits<std::uint64_t>::max() - total" in owner
        and "size_to_u64" in owner,
        "checked_budget_arithmetic",
        "size conversion and aggregate addition reject overflow",
    )
    require(
        "if (usage_out != nullptr) *usage_out = usage;" in owner
        and owner.count("if (usage_out != nullptr) *usage_out = usage;") == 2,
        "usage_published_only_after_success",
        "entry and folder evidence is committed only after semantic validation",
    )

    require(
        "std::string_view component" in owner
        and "component_begin" in owner
        and "split_manifest_path" not in owner,
        "allocation_free_component_scan",
        "portable path validation uses string views rather than component vectors",
    )
    require(
        "ascii_upper" in owner
        and "ascii_case_equal" in owner
        and "std::toupper" not in owner
        and "std::tolower" not in owner,
        "locale_independent_reserved_names",
        "Windows reserved-name checks use explicit ASCII folding",
    )
    require(
        "reserved_windows_device_digit" in owner
        and all(token in owner for token in ("\\xC2\\xB9", "\\xC2\\xB2", "\\xC2\\xB3"))
        and all(token in focused for token in ("\\xC2\\xB9", "\\xC2\\xB2", "\\xC2\\xB3")),
        "win32_superscript_device_names",
        "COM/LPT superscript 1, 2, and 3 spellings and extension forms fail closed",
    )
    require(
        all(token not in owner for token in (
            "std::locale", "setlocale", "<locale>", "<cctype>", "std::regex"
        )),
        "validation_owner_excludes_ambient_locale",
        "the boundary has no process-locale or regex dependency",
    )
    require(
        normalization.find("validate_relative_path_value(raw_path)")
        < normalization.find("out.value.clear()")
        and "out.value = raw_path;" in normalization,
        "alias_safe_output_order",
        "input is validated before output mutation so raw_path may alias out.value",
    )
    require(
        "valid_utf8(std::string_view input) noexcept" in owner
        and "codepoint >= 0xd800U" in owner
        and "codepoint > 0x10ffffU" in owner,
        "strict_utf8_validation_retained",
        "overlong, surrogate, and out-of-range code points remain rejected",
    )
    require(
        "std::string_view previous_device" in owner
        and "std::string_view previous_path" in owner,
        "ordering_checks_avoid_string_copies",
        "lineage and path ordering retain borrowed prior values",
    )
    require(
        "manifest entry has unknown kind" in owner
        and "entry.kind != SyncManifestEntryKind::File" in owner,
        "unknown_kind_fails_closed",
        "unrecognized enum values cannot enter identity or planning",
    )

    require(
        '#include "sync_manifest_validation.hpp"' in domain,
        "domain_consumes_validation_owner",
        "the monolith delegates the boundary to the extracted leaf",
    )
    require(
        "SyncValidationResult normalize_sync_relative_path(" not in domain
        and "SyncValidationResult validate_sync_manifest_entry(" not in domain
        and "SyncValidationResult validate_sync_folder_manifest(" not in domain,
        "domain_no_longer_defines_validation",
        "public normalization and manifest validation have one implementation",
    )
    require(
        all(token not in domain for token in (
            "split_manifest_path", "reserved_windows_device_name", "std::toupper", "<cctype>"
        )),
        "domain_old_path_helpers_removed",
        "the locale-sensitive allocating implementation cannot remain in parallel",
    )
    require(
        "bool valid_sync_id(const std::string& value) noexcept" in domain
        and "return sync_id_is_valid(value);" in domain
        and "bool ascii_lower_alnum" not in domain,
        "identifier_policy_not_duplicated",
        "the compatibility-local helper is a one-line delegate to the extracted owner",
    )

    require(
        "add_library(anonsync_sync_manifest_validation STATIC" in cmake
        and "${ANONSYNC_SYNC_MANIFEST_VALIDATION_SOURCE}" in cmake,
        "separate_validation_target",
        "the owner is separately compiled and linked",
    )
    require(
        "${ANONSYNC_SYNC_MANIFEST_VALIDATION_SOURCE}" in invariant_inventory
        and "src/sync_manifest_validation.cpp" not in core_sources,
        "validation_source_outside_monolith",
        "CMake fails if the extracted owner is reabsorbed into core sources",
    )
    require(
        "anonsync_sync_manifest_validation" in core_links,
        "core_links_validation_owner",
        "production domain references resolve through the extracted library",
    )
    require(
        "add_executable(anonsync_sync_manifest_validation_test" in cmake
        and "add_test(NAME anonsync_sync_manifest_validation_test" in cmake,
        "focused_test_registered",
        "the executable is part of both build and CTest inventories",
    )
    require(
        "anonsync_sync_manifest_validation" in sanitizer_compile
        and "anonsync_sync_manifest_validation_test" in sanitizer_compile
        and "anonsync_sync_manifest_validation_test" in sanitizer_link,
        "sanitizer_compile_and_link_inventory",
        "owner and test are instrumented and the executable is sanitizer-linked",
    )
    require(
        "anonsync_sync_manifest_validation_source_audit" in cmake
        and "audit_sync_manifest_validation.py" in cmake
        and "${Python3_EXECUTABLE} -B -S" in cmake,
        "source_audit_registered_without_site_init",
        "the audit runs in the registered hermetic Python lane",
    )

    required_test_phrases = (
        "normalization freezes aliased input before output mutation",
        "entry resource accounting is exact and deterministic",
        "folder resource accounting covers every nested semantic byte",
        "shape preflight rejects nested cardinality before semantic traversal",
        "failed validation never publishes partial resource evidence",
        "unknown manifest entry kinds fail closed",
    )
    require(
        all(phrase in focused for phrase in required_test_phrases),
        "focused_adversarial_corpus",
        "aliasing, exact accounting, exhaustion order, evidence commit, and enum closure are executable",
    )
    require(
        focused.count("max_total_") >= 5
        and "max_chunks_per_entry" in focused
        and "max_lineage_entries_per_entry" in focused,
        "every_budget_dimension_exercised",
        "focused tests tighten each independent limit",
    )
    require(
        "revision_number >= 858" in verifier
        and "sync_manifest_validation" in verifier,
        "release_verifier_requires_rev0858_boundary",
        "publication cannot omit the new owner, focused test, or audit",
    )

    metrics = {
        "owner_lines": len(owner.splitlines()),
        "domain_lines": len(domain.splitlines()),
        "focused_test_lines": len(focused.splitlines()),
        "domain_validation_definition_count": sum(
            domain.count(token)
            for token in (
                "SyncValidationResult normalize_sync_relative_path(",
                "SyncValidationResult validate_sync_manifest_entry(",
                "SyncValidationResult validate_sync_folder_manifest(",
            )
        ),
        "registered_limit_fields": len(required_limit_fields),
    }
    return emit(root, args.json, checks, metrics)


if __name__ == "__main__":
    raise SystemExit(main())
