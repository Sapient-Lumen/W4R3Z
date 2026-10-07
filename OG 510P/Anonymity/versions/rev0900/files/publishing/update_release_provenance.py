#!/usr/bin/env python3
"""Regenerate the local in-toto/SLSA-style provenance statement.

The statement is intentionally unsigned and local: it is an archive-internal
attestation over key control/report surfaces, not a public claim that an external
builder produced the zip.  Keeping it generated prevents stale subject hashes
when report surfaces are refreshed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any

BASE_SUBJECTS = [
    'VERSION',
    'RELEASE_MANIFEST.json',
    'REVISION_RECEIPT.json',
    'CONTEXT_PACK.json',
    'CITATION.cff',
    'codemeta.json',
    'ro-crate-metadata.json',
    'NOTICE',
    'requirements.txt',
    'ASSURANCE_ARTIFACTS.json',
    'ASSURANCE_ARTIFACTS.md',
    'publishing/render_assurance_artifacts.py',
    'publishing/check_assurance_catalog.py',
    'reports/assurance_catalog_integrity.json',
    'publishing/check_manifest_canonicality.py',
    'reports/manifest_canonicality.json',
    'schemas/manifest_canonicality.schema.json',
    'publishing/TOOLING_INVENTORY.json',
    'publishing/build_tooling_inventory.py',
    'publishing/check_tooling_inventory_integrity.py',
    'reports/tooling_inventory_integrity.json',
    'publishing/check_report_schema_coverage.py',
    'reports/report_schema_coverage.json',
    'publishing/check_report_identity_coverage.py',
    'reports/report_identity_coverage.json',
    'schemas/report_identity_coverage.schema.json',
    'publishing/check_publication_artifact_quarantine.py',
    'reports/publication_artifact_quarantine.json',
    'schemas/publication_artifact_quarantine.schema.json',
    'publishing/check_path_portability.py',
    'reports/path_portability.json',
    'publishing/check_python_entrypoint_smoke.py',
    'reports/python_entrypoint_smoke.json',
    'schemas/path_portability.schema.json',
    'publishing/check_archive_packaging_reproducibility.py',
    'reports/archive_packaging_reproducibility.json',
    'schemas/archive_packaging_reproducibility.schema.json',
    'publishing/check_json_surface_catalog.py',
    'reports/json_surface_catalog.json',
    'schemas/json_surface_catalog.schema.json',
    'publishing/check_content_leakage.py',
    'reports/content_leakage.json',
    'schemas/content_leakage.schema.json',
    'publishing/check_schema_catalog_integrity.py',
    'reports/schema_catalog_integrity.json',
    'schemas/schema_catalog_integrity.schema.json',
    'publishing/check_json_key_integrity.py',
    'reports/json_key_integrity.json',
    'schemas/json_key_integrity.schema.json',
    'publishing/check_text_surface_normalization.py',
    'reports/text_surface_normalization.json',
    'schemas/text_surface_normalization.schema.json',
    'publishing/check_unicode_control_hygiene.py',
    'reports/unicode_control_hygiene.json',
    'schemas/unicode_control_hygiene.schema.json',
    'publishing/check_tooling_static_integrity.py',
    'reports/tooling_static_integrity.json',
    'schemas/tooling_static_integrity.schema.json',
    'schemas/rebuild_fixed_point_coverage.schema.json',
    'reports/rebuild_fixed_point_coverage.json',
    'publishing/check_rebuild_fixed_point_coverage.py',
    'publishing/check_publication_decision_authorization.py',
    'reports/publication_decision_authorization.json',
    'schemas/publication_decision_authorization.schema.json',
    'publishing/check_archive_index_integrity.py',
    'reports/archive_index_integrity.json',
    'schemas/archive_index_integrity.schema.json',
    'schemas/generic_report.schema.json',
    'publishing/CANONICAL_POLICY.json',
    'publishing/archive_invariants.json',
    'publishing/ARCHIVE_INVARIANTS.md',
    'publishing/render_archive_invariants.py',
    'publishing/check_invariant_catalog_integrity.py',
    'reports/invariant_catalog_integrity.json',
    'schemas/invariant_catalog_integrity.schema.json',
    'publishing/archive_budget_policy.json',
    'publishing/build_review_inventory.py',
    'publishing/check_review_inventory_coverage.py',
    'publishing/check_review_inventory_integrity.py',
    'publishing/check_operator_command_hygiene.py',
    'publishing/check_citation_closure.py',
    'publishing/check_release_readiness.py',
    'publishing/check_queue_note_source_binding.py',
    'publishing/check_decision_note_integrity.py',
    'publishing/check_evidence_pack_policy.py',
    'publishing/build_release_evidence_pack.py',
    'publishing/check_evidence_pack_integrity.py',
    'publishing/check_hostile_review_vectors.py',
    'publishing/check_threat_transfer_matrix.py',
    'publishing/build_external_hostile_review_packet.py',
    'publishing/check_external_hostile_review_packet.py',
    'release_queue/EXTERNAL_HOSTILE_REVIEW_PACKET.json',
    'release_queue/EXTERNAL_HOSTILE_REVIEW_PACKET.md',
    'publishing/check_freeze_compile_witness.py',
    'publishing/build_release_freeze_plan.py',
    'publishing/build_release_freeze_packet.py',
    'publishing/check_freeze_packet_integrity.py',
    'publishing/check_publication_boundary.py',
    'publishing/create_published_entry.py',
    'publishing/refresh_queue_source_hashes.py',
    'publishing/check_research_metadata.py',
    'publishing/check_support_manifest_integrity.py',
    'publishing/check_worked_example_payload_pointers.py',
    'publishing/build_transparency_anchor_request.py',
    'publishing/release_preflight.py',
    'publishing/rebuild_archive_surfaces.py',
    'publishing/build_freeze_compile_witness.py',
    'publishing/check_freeze_toolchain.py',
    'publishing/build_publication_rehearsal.py',
    'publishing/check_publication_decision_template.py',
    'publishing/build_archive_zip.py',
    'publishing/check_package_attestation.py',
    'publishing/sign_package_attestation_dsse.py',
    'publishing/verify_release_artifact_set.py',
    'publishing/check_release_guard_negative_controls.py',
    'reports/release_guard_negative_controls.json',
    'schemas/release_guard_negative_controls.schema.json',
    'signing/package_attestation_public_key.pem',
    'publishing/check_archive_packaging_recipe.py',
    'release_queue/PUBLICATION_DECISION_TEMPLATE.md',
    'reports/publication_decision_template.json',
    'release_queue/REVIEW_INVENTORY.json',
    'release_queue/EVIDENCE_PACK_REGISTRY.json',
    'release_queue/HOSTILE_REVIEW_VECTORS.json',
    'release_queue/COMPILE_EVIDENCE_REUSE.json',
    'release_queue/FREEZE_COMPILE_WITNESS.json',
    'release_queue/FREEZE_PACKET_REGISTRY.json',
    'release_queue/NEXT_RELEASE_FREEZE_PLAN.json',
    'release_queue/NEXT_RELEASE_FREEZE_PLAN.md',
    'reports/review_inventory_coverage.json',
    'reports/review_inventory_integrity.json',
    'reports/operator_command_hygiene.json',
    'reports/citation_closure_audit.json',
    'reports/release_readiness_audit.json',
    'reports/queue_note_source_binding.json',
    'schemas/queue_note_source_binding.schema.json',
    'schemas/decision_note_integrity.schema.json',
    'reports/decision_note_integrity.json',
    'reports/evidence_pack_audit.json',
    'reports/freeze_warning_resolution.json',
    'schemas/freeze_warning_resolution.schema.json',
    'publishing/check_freeze_warning_resolution.py',
    'reports/evidence_pack_integrity.json',
    'reports/freeze_compile_witness.json',
    'reports/freeze_toolchain.json',
    'reports/toolchain_fingerprint.json',
    'schemas/toolchain_fingerprint.schema.json',
    'publishing/check_toolchain_fingerprint.py',
    'reports/publication_rehearsal.json',
    'reports/freeze_packet_integrity.json',
    'reports/publication_boundary.json',
    'reports/support_manifest_integrity.json',
    'series/synthesis/paper17_worked_example_receipt_interlock/artifacts/support_manifest.json',
    'series/synthesis/paper17_worked_example_receipt_interlock/artifacts/example_validation_report.json'
]


def subject_paths(root: pathlib.Path) -> list[str]:
    paths = list(BASE_SUBJECTS)
    for pattern in [
        'release_queue/evidence_packs/*/EVIDENCE_PACK_MANIFEST.json',
        'release_queue/evidence_packs/*/CERTIFIED_MENU_CARD.json',
        'release_queue/evidence_packs/*/ROUTING_SIGNATURE_MANIFEST_CARD.json',
        'release_queue/evidence_packs/*/CONGESTION_EQ_ACCOUNTANT_CARD.json',
        'release_queue/evidence_packs/*/PSCQ_MECHANISM_CARD.json',
        'release_queue/evidence_packs/*/W_CONGESTION_EQ_REPLAY_CARD.json',
        'release_queue/evidence_packs/*/WCONGEQ_REPLAY_CARD.json',
        'release_queue/evidence_packs/*/CALIBRATION_RECIPE_CARD.json',
        'release_queue/evidence_packs/*/STATE_ANONYMITY_CARD.json',
        'release_queue/evidence_packs/*/MUCC_CONTACT_FLOOR_CARD.json',
        'release_queue/evidence_packs/*/SOURCE_BOUND_EVIDENCE_CARD.json',
        'release_queue/evidence_packs/*/release_preflight_static.json',
        'release_queue/freeze_packets/*/FREEZE_PACKET_MANIFEST.json',
        'release_queue/freeze_packets/*/FROZEN_SOURCE.tex',
        'release_queue/freeze_packets/*/PREPUBLICATION_CHECKLIST.md',
    ]:
        paths.extend(p.relative_to(root).as_posix() for p in sorted(root.glob(pattern)))
    # Preserve order while removing duplicates.
    out: list[str] = []
    for rel in paths:
        if rel not in out:
            out.append(rel)
    return out

DEPENDENCIES = [
    "TRANSFER_SOURCES.json",
    "TRANSFER_INPUTS.sha256",
]


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def digest_entry(root: pathlib.Path, rel: str, *, dependency: bool = False) -> dict[str, Any]:
    path = root / rel
    return {
        "uri" if dependency else "name": ("file:" + rel if dependency else rel),
        "digest": {"sha256": sha256_file(path)},
    }


def build(root: pathlib.Path) -> dict[str, Any]:
    release = json.loads((root / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
    receipt_path = root / "REVISION_RECEIPT.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.exists() else {}
    subjects = subject_paths(root)
    missing = [rel for rel in subjects + DEPENDENCIES if not (root / rel).exists()]
    if missing:
        raise FileNotFoundError("missing provenance inputs: " + ", ".join(missing))
    return {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [digest_entry(root, rel) for rel in subjects],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType": "https://example.invalid/anonymity-datacube/manual-release-hardening/v1",
                "externalParameters": {
                    "revision": release["revision"],
                    "timestamp": release["timestamp"],
                    "bundle": release["bundle"],
                    "publication_action": receipt.get("publication_action", "none"),
                    "release_focus": release.get("slug", ""),
                },
                "internalParameters": {
                    "checks": [
                        'python3 -B publishing/build_review_inventory.py --root .',
                        'python3 -B publishing/check_review_inventory_coverage.py --root . --write-report reports/review_inventory_coverage.json',
                        'python3 -B publishing/check_review_inventory_integrity.py --root . --write-report reports/review_inventory_integrity.json',
                        'python3 -B publishing/check_operator_command_hygiene.py --root . --write-report reports/operator_command_hygiene.json',
                        'python3 -B publishing/check_manifest_canonicality.py --root . --write-report reports/manifest_canonicality.json',
                        'python3 -B publishing/render_archive_invariants.py --root .',
                        'python3 -B publishing/render_assurance_artifacts.py --root .',
                        'python3 -B publishing/check_assurance_catalog.py --root . --write-report reports/assurance_catalog_integrity.json',
                        'python3 -B publishing/build_tooling_inventory.py --root .',
                        'python3 -B publishing/check_tooling_inventory_integrity.py --root . --write-report reports/tooling_inventory_integrity.json',
                        'python3 -B publishing/check_publication_decision_template.py --root . --write-report reports/publication_decision_template.json',
                        'python3 -B publishing/check_publication_decision_authorization.py --root . --write-report reports/publication_decision_authorization.json',
                        'python3 -B publishing/check_archive_index_integrity.py --root . --write-report reports/archive_index_integrity.json',
                        'python3 -B publishing/check_citation_closure.py --root . --write-report reports/citation_closure_audit.json',
                        'python3 -B publishing/check_release_readiness.py --root . --write-report reports/release_readiness_audit.json',
                        'python3 -B publishing/check_queue_note_source_binding.py --root . --write-report reports/queue_note_source_binding.json',
                        'python3 -B publishing/check_decision_note_integrity.py --root . --write-report reports/decision_note_integrity.json',
                        'python3 -B publishing/build_release_evidence_pack.py --root .',
                        'python3 -B publishing/check_evidence_pack_integrity.py --root . --write-report reports/evidence_pack_integrity.json',
                        'python3 -B publishing/check_hostile_review_vectors.py --root .',
                        'python3 -B publishing/check_threat_transfer_matrix.py --root .',
                        'python3 -B publishing/build_external_hostile_review_packet.py --root .',
                        'python3 -B publishing/check_external_hostile_review_packet.py --root .',
                        'python3 -B publishing/check_freeze_toolchain.py --root . --write-report reports/freeze_toolchain.json',
                        'python3 -B publishing/build_freeze_compile_witness.py --root .',
                        'python3 -B publishing/check_freeze_compile_witness.py --root . --write-report reports/freeze_compile_witness.json',
                        'python3 -B publishing/check_evidence_pack_policy.py --root . --write-report reports/evidence_pack_audit.json',
                        'python3 -B publishing/check_freeze_warning_resolution.py --root . --write-report reports/freeze_warning_resolution.json',
                        'python3 -B publishing/check_toolchain_fingerprint.py --root . --write-report reports/toolchain_fingerprint.json',
                        'python3 -B publishing/build_release_freeze_plan.py --root . --write-json release_queue/NEXT_RELEASE_FREEZE_PLAN.json --write-md release_queue/NEXT_RELEASE_FREEZE_PLAN.md',
                        'python3 -B publishing/build_release_freeze_packet.py --root .',
                        'python3 -B publishing/check_freeze_packet_integrity.py --root . --write-report reports/freeze_packet_integrity.json',
                        'python3 -B publishing/check_publication_boundary.py --root . --write-report reports/publication_boundary.json',
                        'python3 -B publishing/check_publication_artifact_quarantine.py --root . --write-report reports/publication_artifact_quarantine.json',
                        'python3 -B publishing/check_path_portability.py --root . --write-report reports/path_portability.json',
                        'python3 -B publishing/check_python_entrypoint_smoke.py --root . --write-report reports/python_entrypoint_smoke.json',
                        'python3 -B publishing/check_archive_packaging_reproducibility.py --root . --write-report reports/archive_packaging_reproducibility.json',
                        'python3 -B publishing/check_json_surface_catalog.py --root . --write-report reports/json_surface_catalog.json',
                        'python3 -B publishing/check_content_leakage.py --root . --write-report reports/content_leakage.json',
                        'python3 -B publishing/check_tex_source_safety.py --root . --write-report reports/tex_source_safety.json',
                        'python3 -B publishing/check_secret_material_quarantine.py --root . --write-report reports/secret_material_quarantine.json',
                        'python3 -B publishing/check_makefile_target_integrity.py --root . --write-report reports/makefile_target_integrity.json',
                        'python3 -B publishing/check_schema_catalog_integrity.py --root . --write-report reports/schema_catalog_integrity.json',
                        'python3 -B publishing/check_json_key_integrity.py --root . --write-report reports/json_key_integrity.json',
                        'python3 -B publishing/check_text_surface_normalization.py --root . --write-report reports/text_surface_normalization.json',
                        'python3 -B publishing/check_unicode_control_hygiene.py --root . --write-report reports/unicode_control_hygiene.json',
                        'python3 -B publishing/check_tooling_static_integrity.py --root . --write-report reports/tooling_static_integrity.json',
                        'python3 -B publishing/check_support_manifest_integrity.py --root . --write-report reports/support_manifest_integrity.json',
                        'python3 -B publishing/check_worked_example_payload_pointers.py --root .',
                        'python3 -B publishing/update_release_provenance.py --root .',
                        'python3 -B publishing/check_research_metadata.py --root . --write-report reports/research_metadata_integrity.json',
                        'python3 -B publishing/check_archive_packaging_recipe.py --root . --write-report reports/archive_packaging_recipe.json',
                        'python3 -B publishing/check_surface_schemas.py --root . --write-report reports/surface_schema_validation.json',
                        'python3 -B publishing/check_report_schema_coverage.py --root . --write-report reports/report_schema_coverage.json',
                        'python3 -B publishing/check_rebuild_fixed_point_coverage.py --root . --write-report reports/rebuild_fixed_point_coverage.json',
                        'python3 -B publishing/check_archive_invariants.py --root . --write-report reports/archive_invariants.json',
                        'python3 -B publishing/check_invariant_catalog_integrity.py --root . --write-report reports/invariant_catalog_integrity.json',
                        'python3 -B publishing/check_report_identity_coverage.py --root . --write-report reports/report_identity_coverage.json',
                        'python3 -B publishing/build_publication_rehearsal.py --root . --write-report reports/publication_rehearsal.json',
                        'python3 -B publishing/rebuild_archive_surfaces.py --root .'
                    ],
                    "notes": "Unsigned local attestation inside the archive. It records revision-bound control/report subjects and compared-bundle dependencies, not a self-reference to the final zip digest.",
                },
                "resolvedDependencies": [digest_entry(root, rel, dependency=True) for rel in DEPENDENCIES],
            },
            "runDetails": {
                "builder": {"id": "local-manual-archive-maintainer"},
                "metadata": {
                    "invocationId": f"{release['revision']}-{release['timestamp']}",
                    "finishedOn": release["timestamp"],
                },
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write", default="release_provenance.intoto.jsonl")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    statement = build(root)
    (root / args.write).write_text(json.dumps(statement, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"status": "pass", "subject_count": len(statement["subject"]), "dependency_count": len(statement["predicate"]["buildDefinition"]["resolvedDependencies"]), "written": args.write}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
