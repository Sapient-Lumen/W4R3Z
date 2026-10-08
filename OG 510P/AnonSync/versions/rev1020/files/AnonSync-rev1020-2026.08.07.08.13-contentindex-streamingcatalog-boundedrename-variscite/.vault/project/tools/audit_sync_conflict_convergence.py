#!/usr/bin/env python3
"""Fail-closed source audit for deterministic sync-conflict convergence."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_conflict_resolution.hpp"),
    Path("src/sync_conflict_resolution.cpp"),
    Path("src/sync_domain.cpp"),
    Path("src/sync_domain_selftests.cpp"),
    Path("tests/sync_conflict_resolution_test.cpp"),
    Path("tests/sync_manifest_conflict_convergence_test.cpp"),
    Path("tools/audit_sync_conflict_convergence.py"),
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
        "format": "anonsync-sync-conflict-convergence-audit-v1",
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
    header = texts[Path("src/sync_conflict_resolution.hpp")]
    owner = texts[Path("src/sync_conflict_resolution.cpp")]
    domain = texts[Path("src/sync_domain.cpp")]
    selftests = texts[Path("src/sync_domain_selftests.cpp")]
    focused = texts[Path("tests/sync_conflict_resolution_test.cpp")]
    integration = texts[Path("tests/sync_manifest_conflict_convergence_test.cpp")]
    verifier = texts[Path("tools/verify_release_package.py")]

    header_includes = re.findall(
        r'^#include\s+[<"]([^>"]+)[>"]', header, flags=re.MULTILINE
    )
    resolution_struct = slice_between(
        header, "struct SyncConflictResolution final", "\n};"
    )
    equal_lineage_branch = slice_between(
        domain,
        "relation == SyncLineageRelation::Equal",
        "relation == SyncLineageRelation::RemoteNewer",
    )
    conflict_branch = slice_between(
        domain,
        "const SyncConflictResolution resolution",
        "candidate.entries.push_back(make_plan_entry",
    )
    path_owner = slice_between(
        domain,
        "std::string conflict_copy_relative_path_for_entry_or_throw",
        "struct StagedFileVerification",
    )
    core_links = slice_between(
        cmake,
        "target_link_libraries(anonsync_core_lib",
        "\nif(ANONSYNC_USE_BUNDLED_SQLITE)",
    )
    invariant_inventory = slice_between(
        cmake,
        "foreach(ANONSYNC_INVARIANT_OWNED_SOURCE",
        "\nendforeach()",
    )

    require(
        "enum class SyncConflictValueKind" in header
        and "enum class SyncConflictDisposition" in header
        and "struct SyncConflictResolution final" in header,
        "typed_policy_surface",
        "value kind, disposition, and frozen result are explicit types",
    )
    require(
        all(token in resolution_struct for token in (
            "winner_version_digest",
            "loser_version_digest",
            "canonical_first_kind",
            "canonical_first_version_digest",
            "canonical_second_kind",
            "canonical_second_version_digest",
        ))
        and "*" not in resolution_struct
        and "&" not in resolution_struct,
        "owning_resolution_value",
        "resolution owns winner, loser, and canonical identity evidence",
    )
    require(
        all(
            not any(token in include.lower() for token in (
                "anonsync_core", "sqlite", "filesystem"
            ))
            for include in header_includes
        ),
        "dependency_light_header",
        f"includes={header_includes}",
    )
    require(
        '#include "sha256_digest.hpp"' in owner
        and '#include "anonsync_core' not in owner
        and "sqlite" not in owner.lower()
        and "filesystem" not in owner.lower(),
        "dependency_light_implementation",
        "owner depends only on the SHA-256 leaf and standard facilities",
    )
    require(
        "std::to_chars" in owner
        and "std::ostringstream" not in owner
        and "std::locale" not in owner,
        "locale_independent_framing",
        "security-relevant lengths bypass ambient stream locale",
    )
    require(
        "Sha256DigestBuilder digest;" in owner
        and "append_framed_component(digest" in owner
        and "anonsync-sync-conflict-set-v2" in owner,
        "streamed_domain_separated_identity",
        "framed fields stream into one versioned SHA-256 domain",
    )
    require(
        "kind_is_valid(local_kind)" in owner
        and "is_lowercase_sha256_hex(local_version_digest)" in owner
        and "local_version_digest == remote_version_digest" in owner,
        "fail_closed_value_validation",
        "unknown kinds, malformed digests, and non-conflicts are rejected",
    )
    require(
        "if (local_kind != remote_kind)" in owner
        and "local_kind == SyncConflictValueKind::Tombstone" in owner,
        "tombstone_precedence",
        "mixed file/delete races prevent uncoordinated resurrection",
    )
    require(
        "return local_version_digest > remote_version_digest;" in owner,
        "same_kind_total_order",
        "equal-kind versions use one immutable total order",
    )
    require(
        "canonical_first_kind" in owner
        and "canonical_second_kind" in owner
        and "canonical_first_version_digest" in owner
        and "canonical_second_version_digest" in owner,
        "canonical_pair_binds_kinds_and_digests",
        "conflict identity freezes the kind paired with each sorted digest",
    )
    require(
        "folder_id.size() > 128U" in owner
        and "canonical_path.size() > 4096U" in owner
        and "contains a control byte" in owner,
        "bounded_conflict_scope",
        "folder and path inputs have byte and control-character bounds",
    )
    require(
        len(owner.splitlines()) <= 220,
        "small_leaf_owner",
        f"owner_lines={len(owner.splitlines())}",
    )

    require(
        "ANONSYNC_SYNC_CONFLICT_RESOLUTION_SOURCE" in cmake
        and "add_library(anonsync_sync_conflict_resolution STATIC" in cmake,
        "dedicated_library_target",
        "policy is separately compiled rather than hidden in the monolith",
    )
    require(
        "anonsync_sync_conflict_resolution" in core_links,
        "core_consumes_policy_owner",
        "domain runtime links the extracted policy owner",
    )
    require(
        all(name in cmake for name in (
            "add_executable(anonsync_sync_conflict_resolution_test",
            "add_executable(anonsync_sync_manifest_conflict_convergence_test",
            "add_test(NAME anonsync_sync_conflict_resolution_test",
            "add_test(NAME anonsync_sync_manifest_conflict_convergence_test",
        )),
        "focused_tests_registered",
        "pure-policy and integrated convergence corpora are CTest targets",
    )
    require(
        '"${ANONSYNC_SYNC_CONFLICT_RESOLUTION_SOURCE}"' in invariant_inventory,
        "invariant_source_inventory",
        "extracted source participates in the invariant-owned inventory",
    )
    require(
        cmake.count("anonsync_sync_conflict_resolution_test") >= 4
        and cmake.count("anonsync_sync_manifest_conflict_convergence_test") >= 4,
        "sanitizer_target_inventory",
        "focused executables participate in compile/link sanitizer lanes",
    )
    require(
        "revision_number is not None and revision_number >= 856" in verifier
        and all(path in verifier for path in (
            "src/sync_conflict_resolution.hpp",
            "src/sync_conflict_resolution.cpp",
            "tests/sync_conflict_resolution_test.cpp",
            "tests/sync_manifest_conflict_convergence_test.cpp",
            "tools/audit_sync_conflict_convergence.py",
        )),
        "release_verifier_revision_gate",
        "rev0856 packages cannot omit the new owner, corpora, or audit while older parents remain valid",
    )

    require(
        '#include "sync_conflict_resolution.hpp"' in domain
        and "stable_conflict_set_id" not in domain,
        "monolith_delegates_conflict_policy",
        "domain consumes the owner and the directional legacy helper is absent",
    )
    require(
        "resolve_sync_conflict_or_throw(" in conflict_branch
        and "SyncConflictDisposition::PublishLocalWinner" in conflict_branch
        and "SyncConflictDisposition::ApplyRemoteWinner" in conflict_branch
        and "SyncConflictDisposition::PreserveLocalFileThenApplyRemoteWinner" in conflict_branch,
        "domain_maps_all_dispositions",
        "genuinely concurrent plans map every typed disposition",
    )
    require(
        "counter reuse or equivocation" in equal_lineage_branch
        and "return fail_result(" in equal_lineage_branch
        and "resolve_sync_conflict_or_throw(" not in equal_lineage_branch,
        "equal_lineage_divergence_fails_closed",
        "equal causal history with different bytes is identity corruption, not ordinary concurrency",
    )
    require(
        "out = SyncManifestDiffPlan{};" in domain
        and "SyncManifestDiffPlan candidate;" in domain
        and "out = std::move(candidate);" in domain
        and "a late planner failure must discard an already-built candidate prefix" in integration,
        "manifest_plan_publication_is_failure_atomic",
        "planner builds privately and the corpus rejects leakage from a late multi-entry failure",
    )
    require(
        domain.count("make_sync_conflict_set_id_or_throw(") == 1
        and "plan.conflict_set_id = make_sync_conflict_set_id_or_throw(" in domain,
        "single_conflict_identity_gateway",
        "runtime mints conflict-set identity through one owner call",
    )
    require(
        "diff_plan.local_device_id" in path_owner
        and "diff_plan.remote_device_id" not in path_owner,
        "loser_publisher_names_conflict_artifact",
        "conflict path names the publisher whose local bytes are copied",
    )
    require(
        "entry.conflict_set_id.substr" not in path_owner
        and 'diff_plan.local_device_id + "-" + entry.conflict_set_id' in path_owner,
        "full_conflict_identity_reaches_artifact_path",
        "artifact naming retains all 128 identity bits instead of the legacy 36-bit prefix",
    )

    require(
        focused.count("make_sync_conflict_set_id_or_throw(") >= 7
        and "forward_id == reverse_id" in focused
        and "canonical_first_kind" in focused,
        "pure_orientation_and_binding_corpus",
        "focused tests cover reversal plus folder, path, kind, and digest binding",
    )
    require(
        "GroupedPunctuation" in integration
        and "hostile_locale_id == forward_id" in integration,
        "hostile_locale_corpus",
        "integrated identity is recomputed under a grouped global locale",
    )
    require(
        "std::next_permutation" in integration
        and "file_histories_checked == 6U" in integration
        and "mixed_histories_checked == 6U" in integration
        and "tombstone_histories_checked == 6U" in integration,
        "generated_delivery_permutations",
        "file, mixed, and tombstone histories cover all three-value orders",
    )
    require(
        "duplicate winner delivery was not idempotent" in integration
        and "duplicate ordinary conflict-artifact delivery" in integration,
        "duplicate_delivery_oracle",
        "winner and ordinary conflict-artifact duplication are exercised",
    )
    require(
        "expected_preserved_files" in integration
        and "folded.preserved_file_versions == expected_preserved_files" in integration,
        "loser_preservation_oracle",
        "mixed histories require every losing file to remain represented",
    )
    require(
        "expected_conflict_suffix" in integration
        and "loser_plan.conflict_set_id" in integration
        and "absolute_conflict_copy_path.ends_with" in integration,
        "exact_artifact_suffix_corpus",
        "integration proves the full shared identity is the exact terminal artifact suffix",
    )
    require(
        "alpha_preserves_conflict != bravo_preserves_conflict" in selftests
        and "conflict_winner_plan" in selftests
        and "orient_remote_file_as_deterministic_conflict_winner_or_throw" in selftests,
        "legacy_corpus_refactored_for_total_order",
        "broad selftests assert complementary views and orient apply fixtures",
    )

    metrics = {
        "owner_lines": len(owner.splitlines()),
        "domain_conflict_identity_calls": domain.count(
            "make_sync_conflict_set_id_or_throw("
        ),
        "focused_identity_calls": focused.count(
            "make_sync_conflict_set_id_or_throw("
        ),
        "registered_test_name_mentions": {
            "policy": cmake.count("anonsync_sync_conflict_resolution_test"),
            "integration": cmake.count(
                "anonsync_sync_manifest_conflict_convergence_test"
            ),
        },
    }
    return emit(root, args.json, checks, metrics)


if __name__ == "__main__":
    raise SystemExit(main())
