#!/usr/bin/env python3
"""Lexical audit for rev0988 targeted folder-catalog cutpoints.

This checks reviewed source and documentation shape. It is not semantic proof:
compiler, runtime, sanitizer, scale, reconstruction, and package evidence remain
load-bearing.
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
    Path("TARGETED_CATALOG_PATH_CUTPOINT_AND_DEMATERIALIZATION_SCALE_AUDIT_rev0988.md"),
    Path("REVISION_NOTES_rev0988.md"),
    Path("src/anonsync_folder.cpp"),
    Path("src/anonsync_sync.cpp"),
    Path("src/sync_replica_folder_scan_owner.hpp"),
    Path("src/sync_replica_folder_scan_owner.cpp"),
    Path("tests/sync_replica_folder_scan_owner_test.cpp"),
    Path("tools/audit_sync_replica_targeted_catalog_cutpoint.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def delimited_body(text: str, signature: str, opening: str = "{", closing: str = "}") -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    boundary = text.find(opening, start + len(signature))
    if boundary < 0:
        return ""
    depth = 0
    for index in range(boundary, len(text)):
        if text[index] == opening:
            depth += 1
        elif text[index] == closing:
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return ""


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-targeted-catalog-path-cutpoint-source-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove SQLite snapshot isolation, query "
            "complexity, allocator behavior, race freedom, crash recovery, "
            "target-scale RSS, or filesystem authority"
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
    bootstrap_path = root.parent.parent / "BOOTSTRAPROSE.md"
    require(bootstrap_path.is_file(), "release_root_bootstrap_exists", str(bootstrap_path))
    if missing or not bootstrap_path.is_file():
        return emit(root, args.json, checks)

    text = {
        path.as_posix(): (root / path).read_text(encoding="utf-8")
        for path in REQUIRED
    }
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text[
        "TARGETED_CATALOG_PATH_CUTPOINT_AND_DEMATERIALIZATION_SCALE_AUDIT_rev0988.md"
    ]
    notes = text["REVISION_NOTES_rev0988.md"]
    folder_h = text["src/sync_replica_folder_scan_owner.hpp"]
    folder_c = text["src/sync_replica_folder_scan_owner.cpp"]
    folder_test = text["tests/sync_replica_folder_scan_owner_test.cpp"]
    folder_cli = text["src/anonsync_folder.cpp"]
    sync_cli = text["src/anonsync_sync.cpp"]
    verifier = text["tools/verify_release_package.py"]
    self_text = text["tools/audit_sync_replica_targeted_catalog_cutpoint.py"]

    path_loader = delimited_body(
        folder_c, "load_folder_catalog_path_cutpoint_or_throw("
    )
    row_loader = delimited_body(
        folder_c, "load_modern_catalog_entry_row_or_throw("
    )
    convergence = delimited_body(
        folder_c,
        "SyncReplicaFolderScanOwner::run_convergence_pass_impl_or_throw(",
    )
    dematerialization_start = convergence.find(
        "const auto dematerialize_metadata_only_file_or_throw"
    )
    dematerialization_end = convergence.find(
        "bool completed_selected_remote_apply", dematerialization_start
    )
    dematerialization = (
        convergence[dematerialization_start:dematerialization_end]
        if dematerialization_start >= 0 and dematerialization_end >= 0
        else ""
    )

    require(
        "anonsync_sync_replica_targeted_catalog_cutpoint_source_audit" in cmake
        and "tools/audit_sync_replica_targeted_catalog_cutpoint.py" in cmake,
        "focused_audit_is_registered",
        "the rev0988 audit is part of the ordinary CTest registry",
    )
    require(
        "struct FolderCatalogPathCutpoint final" in folder_c
        and "std::optional<SyncReplicaFolderCatalogEntry> entry" in folder_c,
        "path_cutpoint_has_one_optional_entry",
        "the targeted projection cannot own a complete catalog vector",
    )
    require(
        "SyncSqliteTransactionMode::Deferred" in path_loader
        and path_loader.find("sync_replica_folder_catalog_meta")
        < path_loader.find("sync_replica_folder_catalog_entries"),
        "metadata_and_path_share_one_deferred_snapshot",
        "catalog identity is observed before the exact path in one read transaction",
    )
    require(
        'WHERE canonical_path=?;' in path_loader
        and "ORDER BY canonical_path" not in path_loader,
        "path_query_is_exact_not_complete_projection",
        "the effect reproof addresses the catalog primary key rather than walking it",
    )
    require(
        "validate_sync_relative_path(canonical_path)" in path_loader
        and "cutpoint.limits != expected_limits" in path_loader
        and "schema_version != kSchemaVersion" in path_loader,
        "path_cutpoint_reproves_path_identity_and_limits",
        "the optimized read does not skip configured catalog identity",
    )
    require(
        "selection_generation" in path_loader
        and "selection_absence_fence_generation" in path_loader
        and "selection_digest" in path_loader,
        "path_cutpoint_carries_selection_authority",
        "metadata-only effect cannot outlive a normal policy transition",
    )
    require(
        "load_modern_catalog_entry_row_or_throw" in path_loader
        and "validate_catalog_entry_or_throw" in row_loader,
        "targeted_and_complete_loaders_share_entry_decoder",
        "row validation is centralized rather than copied",
    )
    require(
        folder_c.count("load_modern_catalog_entry_row_or_throw(") >= 3,
        "shared_decoder_has_definition_and_both_callers",
        "complete and targeted current-format reads use the same codec",
    )
    require(
        dematerialization.count("load_targeted_catalog_path_cutpoint_or_throw(")
        >= 2
        and '"dematerialization planning reproof"' in dematerialization
        and '"pre-unlink reproof"' in dematerialization
        and '"post-unlink reproof"' in dematerialization,
        "unlink_is_bracketed_by_targeted_catalog_cutpoints",
        "successful removal has planning, pre-effect, and post-effect path reproof",
    )
    require(
        "snapshot_or_throw();" not in delimited_body(
            dematerialization,
            "const auto load_targeted_catalog_path_cutpoint_or_throw",
        ),
        "targeted_loader_does_not_call_complete_catalog_snapshot",
        "the helper cannot regress to the old full-catalog owner through a wrapper",
    )
    require(
        "remote_targeted_catalog_path_cutpoint_count" in folder_h
        and "remote_targeted_catalog_path_cutpoint_count" in folder_c,
        "targeted_cutpoints_are_counted",
        "operators can distinguish exact path reproof from complete projections",
    )
    require(
        "remote_targeted_catalog_path_cutpoints" in folder_cli
        and "remote_targeted_catalog_path_cutpoints" in sync_cli,
        "both_shipping_json_surfaces_expose_targeted_cutpoints",
        "low-level and configured convergence diagnostics remain aligned",
    )
    require(
        "struct CatalogEntryReadTrace final" in folder_test
        and "complete_projection_read_count" in folder_test
        and "exact_path_read_count" in folder_test,
        "sqlite_statement_trace_distinguishes_query_shapes",
        "the runtime oracle observes exact and complete entry reads separately",
    )
    require(
        (
            "test_selective_sync_dematerialization_catalog_reproof_is_path_local"
            in folder_test
            or "test_selective_sync_dematerialization_reproof_is_path_local"
            in folder_test
        )
        and "constexpr std::size_t kPathCount = 8U" in folder_test
        and "3U * kPathCount" in folder_test,
        "batch_regression_proves_three_exact_reads_per_effect",
        "the correction is tested beyond a one-file special case",
    )
    require(
        "trace.complete_projection_read_count <= 4U" in folder_test
        and "retained_catalog.entries.size() == kPathCount" in folder_test,
        "batch_regression_keeps_complete_projections_pass_bounded",
        "catalog evidence remains retained without one full projection per effect",
    )
    require(
        "12,288 complete catalog projections" in design
        and "1,000,000 paths" in design
        and "4,096 remote effects" in design,
        "audit_quantifies_the_removed_composition_defect",
        "the scaling correction is tied to production frontiers",
    )
    require(
        "does not claim to" in design
        and "recompute the aggregate catalog digest" in design
        and "Complete" in design
        and "catalog observations remain" in design,
        "path_local_authority_nonclaim_is_explicit",
        "targeted reads are not mislabeled as global catalog proof",
    )
    require(
        "O(history) reference owner" in design
        and "targeted" in design
        and "replica path/operation cutpoint" in design
        and "not a claim" in design,
        "remaining_replica_and_scale_seams_are_explicit",
        "rev0988 does not overstate multi-terabyte qualification",
    )
    require(
        "TARGETED_CATALOG_PATH_CUTPOINT_AND_DEMATERIALIZATION_SCALE_AUDIT_rev0988.md"
        in verifier
        and "REVISION_NOTES_rev0988.md" in verifier
        and "audit_sync_replica_targeted_catalog_cutpoint.py" in verifier,
        "release_verifier_requires_rev0988_chain",
        "a package cannot omit the implementation audit or revision record",
    )
    require(
        "rev0988" in readme.lower()
        and "targeted" in bootstrap.lower(),
        "visible_product_pages_name_the_current_slice",
        "restart context does not continue to describe the old multiplier",
    )
    require(
        "VALIDATION_PENDING_REV0988" not in notes
        and "ARCHIVE_PENDING_REV0988" not in notes
        and "VALIDATION_PENDING_REV0988" not in design
        and "VALIDATION_PENDING_REV0988" not in readme
        and "ARCHIVE_PENDING_REV0988" not in readme
        and "VALIDATION_PENDING_REV0988" not in bootstrap
        and "ARCHIVE_PENDING_REV0988" not in bootstrap,
        "final_validation_and_archive_identity_are_sealed",
        "the audit remains release-gated until exact evidence and filename are final",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "not semantic proof" in self_text
        and "runtime, sanitizer, scale, reconstruction, and package" in self_text,
        "lexical_audit_disclaims_semantic_authority",
        "source spelling cannot substitute for executable or package evidence",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
