#!/usr/bin/env python3
"""Classify every JSON surface so untyped machine data is not silent.

This is not a demand that every artifact JSON have a bespoke schema.  It is a
coverage ledger: every JSON file must either be schema-checked, a schema file,
covered by a named integrity validator/registry, or explicitly classified as a
legacy/reference payload.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
from typing import Any

ROOT_RESEARCH_METADATA = {"codemeta.json", "ro-crate-metadata.json"}
ROOT_DIGEST_OR_LEDGER = {"MANIFEST.json", "DATACUBE_TRANSFER_LEDGER.json"}
POLICY_CONTROL_JSON = {"publishing/CANONICAL_POLICY.json", "publishing/lifecycle_gates.json"}
PUBLISHED_REFERENCE_JSON = {
    "published/2026-01-23_spectral_anonymity/supplement/spectral_sanity_outputs.json",
    "published/legacy_published_links.json",
    "published/publication_classification.json",
}
EVIDENCE_PACK_PAYLOAD_NAMES = {"CERTIFIED_MENU_CARD.json", "ROUTING_SIGNATURE_MANIFEST_CARD.json", "CONGESTION_EQ_ACCOUNTANT_CARD.json", "PSCQ_MECHANISM_CARD.json",
    "W_CONGESTION_EQ_REPLAY_CARD.json", "WCONGEQ_REPLAY_CARD.json", "CALIBRATION_RECIPE_CARD.json", "STATE_ANONYMITY_CARD.json", "MUCC_CONTACT_FLOOR_CARD.json", "SOURCE_BOUND_EVIDENCE_CARD.json", "release_preflight_static.json"}
FREEZE_PACKET_PAYLOAD_NAMES = {"FREEZE_COMPILE_WITNESS.snapshot.json"}
RELEASE_QUEUE_VALIDATED_JSON = {
    "release_queue/HOLD_COMPILE_TRIAGE.json": "publishing/check_queue_compile_smoke.py hold-scope compile triage",
    "release_queue/UNQUEUED_COMPILE_TRIAGE.json": "publishing/check_unqueued_compile_triage.py unqueued-source compile triage",
    "release_queue/HOSTILE_REVIEW_VECTORS.json": "publishing/check_evidence_pack_integrity.py hostile arithmetic vector overlay",
    "release_queue/COMPILE_EVIDENCE_REUSE.json": "compile evidence reuse report with downstream compile-surface verifiers",
    "release_queue/EXTERNAL_HOSTILE_REVIEW_PACKET.json": "publishing/check_external_hostile_review_packet.py external hostile review packet",
}
PUBLISHED_VALIDATED_JSON = {
    "published/PUBLISHED_COMPILE_TRIAGE.json": "publishing/check_published_compile_triage.py published TeX compile triage",
}
AUXILIARY_VALIDATED_JSON = {
    "index/AUXILIARY_TEX_COMPILE_TRIAGE.json": "publishing/check_auxiliary_tex_compile_triage.py auxiliary non-paper TeX compile triage",
}
SYNTHESIS17_ARTIFACT_PREFIX = "series/synthesis/paper17_worked_example_receipt_interlock/artifacts/"


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def import_surface_schema_module(root: pathlib.Path):
    path = root / "publishing" / "check_surface_schemas.py"
    spec = importlib.util.spec_from_file_location("check_surface_schemas_for_catalog", path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot import check_surface_schemas.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def classify(rel: str, schema_targets: dict[str, str]) -> tuple[str, str, bool]:
    if rel in schema_targets:
        return "schema_checked_surface", schema_targets[rel], True
    if rel.startswith("schemas/") and rel.endswith(".schema.json"):
        return "json_schema_document", "schema_document", True
    if rel.startswith("reports/"):
        return "machine_report_missing_schema_binding", "reports_should_be_schema_checked", False
    if rel in ROOT_RESEARCH_METADATA:
        return "research_object_metadata", "publishing/check_research_metadata.py", True
    if rel in ROOT_DIGEST_OR_LEDGER:
        return "manifest_or_transfer_ledger", "manifest_or_ledger_semantics", True
    if rel in PUBLISHED_REFERENCE_JSON:
        return "legacy_published_reference_payload", "published_surface_register_or_legacy_supplement", True
    if rel in POLICY_CONTROL_JSON:
        return "policy_control_surface", "publishing/control_surfaces.json or lifecycle policy", True
    if rel in RELEASE_QUEUE_VALIDATED_JSON:
        return "release_queue_validated_payload", RELEASE_QUEUE_VALIDATED_JSON[rel], True
    if rel in PUBLISHED_VALIDATED_JSON:
        return "published_validated_payload", PUBLISHED_VALIDATED_JSON[rel], True
    if rel.startswith("published/") and rel.endswith("/METADATA.json"):
        return "published_validated_payload", "published publication receipt and metadata boundary", True
    if rel.startswith("published/") and rel.endswith("/FREEZE_COMPILE_WITNESS.snapshot.json"):
        return "published_validated_payload", "publishing/check_published_compile_triage.py plus publication receipt", True
    if rel in AUXILIARY_VALIDATED_JSON:
        return "auxiliary_validated_payload", AUXILIARY_VALIDATED_JSON[rel], True
    if rel.startswith("release_queue/evidence_packs/") and rel.rsplit("/", 1)[-1] in EVIDENCE_PACK_PAYLOAD_NAMES:
        return "evidence_pack_payload", "publishing/check_evidence_pack_integrity.py", True
    if rel.startswith("release_queue/freeze_packets/") and rel.rsplit("/", 1)[-1] in FREEZE_PACKET_PAYLOAD_NAMES:
        return "freeze_packet_payload", "publishing/check_freeze_packet_integrity.py", True
    if rel.startswith(SYNTHESIS17_ARTIFACT_PREFIX):
        return "synthesis17_worked_example_artifact", "series/synthesis/paper17_worked_example_receipt_interlock/tools/validate_example.py", True
    return "unclassified_json_surface", "none", False


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    module = import_surface_schema_module(root)
    schema_targets = {target: schema for target, schema in module.schema_targets(root)}
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.json"), key=lambda p: p.relative_to(root).as_posix()):
        rel = path.relative_to(root).as_posix()
        category, coverage, ok = classify(rel, schema_targets)
        row = {
            "path": rel,
            "category": category,
            "coverage": coverage,
            "schema_checked": rel in schema_targets,
            "status": "pass" if ok else "fail",
        }
        rows.append(row)
        if not ok:
            failures.append({"category": category, "path": rel, "coverage": coverage})

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["category"]] = counts.get(row["category"], 0) + 1
    schema_checked_count = sum(1 for row in rows if row["schema_checked"])
    validator_or_registry_count = sum(1 for row in rows if not row["schema_checked"] and row["status"] == "pass" and row["category"] != "json_schema_document")
    summary = {
        "checks_failed": len(failures),
        "json_file_count": len(rows),
        "schema_checked_json_count": schema_checked_count,
        "json_schema_document_count": counts.get("json_schema_document", 0),
        "validator_or_registry_classified_count": validator_or_registry_count,
        "unclassified_json_count": len(failures),
        "category_counts": counts,
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "schema_target_source": "publishing/check_surface_schemas.py",
        "json_surfaces": rows,
        "failures": failures[:100],
        "summary": summary,
        "fail_closed_rule": "If a JSON surface is neither schema-checked nor explicitly governed by a validator, registry, or legacy/reference classification, default to no publication and classify or schema it before relying on the archive.",
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
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
