#!/usr/bin/env python3
"""Validate compact machine-readable archive surfaces against JSON Schemas.

High-value control surfaces use bespoke schemas.  Every reports/*.json surface is
also schema-visible: reports without a bespoke schema are validated against a
permissive generic report floor and then counted by check_report_schema_coverage.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from jsonschema import Draft202012Validator

EXPLICIT_SCHEMA_TARGETS = {
    "RELEASE_MANIFEST.json": "schemas/release_manifest.schema.json",
    "REVISION_RECEIPT.json": "schemas/revision_receipt.schema.json",
    "REVISION_LINEAGE.json": "schemas/revision_lineage.schema.json",
    "ARCHIVE_INDEX.json": "schemas/archive_index.schema.json",
    "CONTEXT_PACK.json": "schemas/context_pack.schema.json",
    "publishing/control_surfaces.json": "schemas/control_surfaces.schema.json",
    "publishing/TOOLING_INVENTORY.json": "schemas/tooling_inventory.schema.json",
    "release_queue/QUEUE_INDEX.json": "schemas/queue_index.schema.json",
    "release_queue/REVIEW_INVENTORY.json": "schemas/review_inventory.schema.json",
    "release_queue/LATEST_DECISION.json": "schemas/latest_decision.schema.json",
    "release_queue/DECISION_INDEX.json": "schemas/decision_index.schema.json",
    "published/citation_heads.json": "schemas/citation_heads.schema.json",
    "published/PUBLIC_SURFACE.json": "schemas/public_surface.schema.json",
    "publishing/archive_invariants.json": "schemas/archive_invariants.schema.json",
    "TRANSFER_SOURCES.json": "schemas/transfer_sources.schema.json",
    "ASSURANCE_ARTIFACTS.json": "schemas/assurance_artifacts.schema.json",
    "publishing/archive_budget_policy.json": "schemas/archive_budget_policy.schema.json",
    "series/synthesis/paper17_worked_example_receipt_interlock/artifacts/support_manifest.json": "schemas/support_manifest.schema.json",
    "series/synthesis/paper17_worked_example_receipt_interlock/artifacts/example_artifact_inventory.json": "schemas/example_artifact_inventory.schema.json",
    "series/synthesis/paper17_worked_example_receipt_interlock/artifacts/example_support_bundle_map.json": "schemas/example_support_bundle_map.schema.json",
    "series/synthesis/paper17_worked_example_receipt_interlock/artifacts/example_validation_report.json": "schemas/example_validation_report.schema.json",
    "reports/review_inventory_coverage.json": "schemas/review_inventory_coverage.schema.json",
    "reports/review_inventory_integrity.json": "schemas/review_inventory_integrity.schema.json",
    "reports/operator_command_hygiene.json": "schemas/operator_command_hygiene.schema.json",
    "reports/citation_closure_audit.json": "schemas/citation_closure_audit.schema.json",
    "reports/release_readiness_audit.json": "schemas/release_readiness_audit.schema.json",
    "reports/evidence_pack_audit.json": "schemas/evidence_pack_audit.schema.json",
    "release_queue/EVIDENCE_PACK_REGISTRY.json": "schemas/evidence_pack_registry.schema.json",
    "reports/evidence_pack_integrity.json": "schemas/evidence_pack_integrity.schema.json",
    "release_queue/FREEZE_COMPILE_WITNESS.json": "schemas/freeze_compile_witness.schema.json",
    "reports/freeze_compile_witness.json": "schemas/freeze_compile_witness_report.schema.json",
    "reports/publication_boundary.json": "schemas/publication_boundary.schema.json",
    "release_queue/FREEZE_PACKET_REGISTRY.json": "schemas/freeze_packet_registry.schema.json",
    "reports/freeze_packet_integrity.json": "schemas/freeze_packet_integrity.schema.json",
    "release_queue/NEXT_RELEASE_FREEZE_PLAN.json": "schemas/release_freeze_plan.schema.json",
    "reports/research_metadata_integrity.json": "schemas/research_metadata_integrity.schema.json",
    "reports/publication_decision_template.json": "schemas/publication_decision_template.schema.json",
    "reports/publication_decision_authorization.json": "schemas/publication_decision_authorization.schema.json",
    "reports/archive_packaging_recipe.json": "schemas/archive_packaging_recipe.schema.json",
    "reports/freeze_toolchain.json": "schemas/freeze_toolchain.schema.json",
    "reports/publication_rehearsal.json": "schemas/publication_rehearsal.schema.json",
    "reports/tooling_inventory_integrity.json": "schemas/tooling_inventory_integrity.schema.json",
    "reports/report_schema_coverage.json": "schemas/report_schema_coverage.schema.json",
    "reports/rebuild_fixed_point_coverage.json": "schemas/rebuild_fixed_point_coverage.schema.json",
    "reports/assurance_catalog_integrity.json": "schemas/assurance_catalog_integrity.schema.json",
    "reports/revision_lineage.json": "schemas/revision_lineage_report.schema.json",
    "reports/archive_index_integrity.json": "schemas/archive_index_integrity.schema.json",
    "release_queue/PUBLICATION_BLOCKERS.json": "schemas/publication_blockers.schema.json",
    "reports/publication_blockers.json": "schemas/publication_blockers_report.schema.json",
    "reports/release_guard_negative_controls.json": "schemas/release_guard_negative_controls.schema.json",
    "reports/lifecycle_gate_status.json": "schemas/lifecycle_gate_status.schema.json",
    "reports/report_identity_coverage.json": "schemas/report_identity_coverage.schema.json",
    "reports/report_warning_policy.json": "schemas/report_warning_policy.schema.json",
    "reports/publication_artifact_quarantine.json": "schemas/publication_artifact_quarantine.schema.json",
    "reports/publication_target_portability.json": "schemas/publication_target_portability.schema.json",
    "reports/path_portability.json": "schemas/path_portability.schema.json",
    "reports/archive_packaging_reproducibility.json": "schemas/archive_packaging_reproducibility.schema.json",
    "reports/archive_entry_security.json": "schemas/archive_entry_security.schema.json",
    "reports/bundle_identity_consistency.json": "schemas/bundle_identity_consistency.schema.json",
    "reports/control_surface_path_integrity.json": "schemas/control_surface_path_integrity.schema.json",
    "reports/duplicate_content_policy.json": "schemas/duplicate_content_policy.schema.json",
    "reports/tex_source_safety.json": "schemas/tex_source_safety.schema.json",
    "reports/secret_material_quarantine.json": "schemas/secret_material_quarantine.schema.json",
    "reports/makefile_target_integrity.json": "schemas/makefile_target_integrity.schema.json",
    "reports/manifest_canonicality.json": "schemas/manifest_canonicality.schema.json",
    "reports/freeze_warning_resolution.json": "schemas/freeze_warning_resolution.schema.json",
    "reports/toolchain_fingerprint.json": "schemas/toolchain_fingerprint.schema.json",
    "reports/json_surface_catalog.json": "schemas/json_surface_catalog.schema.json",
    "reports/queue_note_source_binding.json": "schemas/queue_note_source_binding.schema.json",
    "reports/invariant_catalog_integrity.json": "schemas/invariant_catalog_integrity.schema.json",
    "reports/content_leakage.json": "schemas/content_leakage.schema.json",
    "reports/decision_note_integrity.json": "schemas/decision_note_integrity.schema.json",
    "reports/tooling_static_integrity.json": "schemas/tooling_static_integrity.schema.json",
    "reports/python_entrypoint_smoke.json": "schemas/python_entrypoint_smoke.schema.json",
    "reports/text_surface_normalization.json": "schemas/text_surface_normalization.schema.json",
    "reports/unicode_control_hygiene.json": "schemas/unicode_control_hygiene.schema.json",
    "reports/json_key_integrity.json": "schemas/json_key_integrity.schema.json",
    "reports/schema_catalog_integrity.json": "schemas/schema_catalog_integrity.schema.json",
}


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def schema_targets(root: pathlib.Path) -> list[tuple[str, str]]:
    targets: dict[str, str] = dict(EXPLICIT_SCHEMA_TARGETS)
    for manifest in sorted((root / "release_queue" / "evidence_packs").glob("*/EVIDENCE_PACK_MANIFEST.json")):
        targets[manifest.relative_to(root).as_posix()] = "schemas/evidence_pack_manifest.schema.json"
    for manifest in sorted((root / "release_queue" / "freeze_packets").glob("*/FREEZE_PACKET_MANIFEST.json")):
        targets[manifest.relative_to(root).as_posix()] = "schemas/freeze_packet_manifest.schema.json"
    for receipt in sorted((root / "published").glob("*/PUBLICATION_RECEIPT.json")):
        targets[receipt.relative_to(root).as_posix()] = "schemas/publication_receipt.schema.json"
    for report in sorted((root / "reports").glob("*.json")):
        targets.setdefault(report.relative_to(root).as_posix(), "schemas/generic_report.schema.json")
    return sorted(targets.items())


def check(root: pathlib.Path) -> dict:
    release = load_json(root / "RELEASE_MANIFEST.json")
    checks = []
    for target_rel, schema_rel in schema_targets(root):
        target = root / target_rel
        schema_path = root / schema_rel
        try:
            schema = load_json(schema_path)
            instance = load_json(target)
            validator = Draft202012Validator(schema)
            errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
            checks.append({
                "target": target_rel,
                "schema": schema_rel,
                "status": "pass" if not errors else "fail",
                "error_count": len(errors),
                "errors": [
                    {
                        "path": "/".join(str(p) for p in err.absolute_path),
                        "message": err.message,
                    }
                    for err in errors[:20]
                ],
            })
        except FileNotFoundError as exc:
            checks.append({"target": target_rel, "schema": schema_rel, "status": "fail", "error_count": 1, "errors": [{"path": "", "message": str(exc)}]})
        except Exception as exc:
            checks.append({"target": target_rel, "schema": schema_rel, "status": "fail", "error_count": 1, "errors": [{"path": "", "message": str(exc)}]})

    failures = [c for c in checks if c["status"] == "fail"]
    report_targets = [c for c in checks if c["target"].startswith("reports/")]
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "checked_targets": len(checks),
        "checks": checks,
        "summary": {
            "checks_passed": len(checks) - len(failures),
            "checks_failed": len(failures),
            "report_targets_checked": len(report_targets),
            "generic_report_targets_checked": sum(1 for c in report_targets if c["schema"] == "schemas/generic_report.schema.json"),
            "explicit_report_targets_checked": sum(1 for c in report_targets if c["schema"] != "schemas/generic_report.schema.json"),
        },
        "fail_closed_rule": "If schema validation fails, default to no publication and repair malformed machine-readable surfaces before trusting them.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = (root / args.write_report).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
