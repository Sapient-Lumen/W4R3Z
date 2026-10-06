import json
import pathlib
from typing import Any

from schema_conformance_lib import SCHEMA_SURFACES

EXTERNAL_STANDARD_SURFACES = {
    "codemeta.json": ["tools/check_external_metadata_contract.py"],
    "ro-crate-metadata.json": ["tools/check_external_metadata_contract.py"],
    "SBOM.spdx.json": ["tools/check_external_metadata_contract.py"],
}

CONTRACT_ONLY_SURFACES = {
    "ALIAS-RETENTION-POLICY.json": ["tools/check_alias_retention_policy_contract.py"],
    "APPLICABILITY-LEDGER.json": ["tools/check_applicability_witness_contract.py"],
    "ARCHIVE-ECONOMY-AUDIT.json": ["tools/check_archive_economy_audit_contract.py"],
    "ASSUMPTION-LEDGER.json": ["tools/check_assumption_witness_contract.py"],
    "CANARY-PROTOCOL.json": ["tools/check_canary_protocol_contract.py"],
    "CANARY-RUNS.json": ["tools/check_canary_runs_contract.py"],
    "CURRENT-RECEIPT.json": ["tools/check_current_receipt_contract.py"],
    "DATACUBE-TRANSFER-LEDGER.json": ["tools/check_transfer_ledger_contract.py"],
    "FILE-MANIFEST.json": ["tools/check_release_integrity_contract.py"],
    "FIREBREAK-LEDGER.json": ["tools/check_reasoning_firebreak_witness_contract.py"],
    "FOLLOWTHROUGH-QUEUE.json": ["tools/check_followthrough_witness_contract.py"],
    "FOREIGN-PRESSURE-LEDGER.json": ["tools/check_foreign_pressure_witness_contract.py"],
    "FRONTIER-BACKLOG.json": ["tools/check_frontier_backlog_contract.py"],
    "HOT-SURFACE-COMPACTION.json": ["tools/check_hot_surface_compaction_contract.py"],
    "HOT-SURFACE-COMPACTION-ORIGINALS.json": ["tools/check_hot_surface_compaction_contract.py"],
    "LEDGER-AUDIT.json": ["tools/check_ledger_audit_contract.py"],
    "LEDGER-COLDSTORE.json": ["tools/check_ledger_coldstore_roundtrip_contract.py"],
    "LINK-INTEGRITY-POLICY.json": ["tools/check_link_integrity_policy_contract.py"],
    "OBLIGATION-LEDGER.json": ["tools/check_obligation_witness_contract.py"],
    "RECEIPT-COLDSTORE.json": ["tools/check_receipt_coldstore_roundtrip_contract.py"],
    "REENTRY-SURFACE-CONFORMANCE.json": ["tools/check_reentry_surface_contract.py"],
    "RELEASE-MANIFEST.json": ["tools/check_release_integrity_contract.py"],
    "RELEASE-PROVENANCE.json": ["tools/check_release_integrity_contract.py", "tools/check_lint_idempotence_audit_contract.py"],
    "RESOLUTION-LEDGER.json": ["tools/check_resolution_witness_contract.py"],
    "RETROSPECTIVE-QUEUE.json": ["tools/check_retrospective_write_contract.py"],
    "SELF-SUFFICIENCY-LEDGER.json": ["tools/check_self_sufficiency_assay_contract.py"],
    "WITNESS-FAMILY-HANDLES.json": ["tools/check_witness_family_handle_contract.py"],
    "WITNESS-VOCABULARY.json": ["tools/check_vocabulary_witness_contract.py"],
    "compact-surface-bundle.json": ["tools/check_compact_surface_bundle_contract.py"],
    "replay-capsule.json": ["tools/check_replay_capsule_contract.py"],
}

CLASS_RATIONALES = {
    "schema-backed": "surface has a local public JSON Schema and participates in SCHEMA-CONFORMANCE-AUDIT.json",
    "contract-only": "surface is governed by bespoke contract checks because its shape is large, heterogeneous, integrity-sensitive, or method-specific",
    "external-standard": "surface follows an external metadata/SBOM convention and is checked by DelayBasin metadata contracts rather than a local replacement schema",
}

NON_CLAIM = "schema-coverage-court, schema-completeness-sovereign, contract-exemption-board, coverage-waiver-senate, schema-taxonomy-tribunal, public-surface-notary, validator-monopoly, and schema-backfill-authority are forbidden; this surface inventories schema coverage and validator routing but does not certify semantic truth, canon sufficiency, legal status, release legitimacy, minimality, or continuation authority."


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def root_json_surfaces(root: pathlib.Path) -> list[str]:
    return sorted(path.name for path in root.glob("*.json") if path.is_file())


def schema_by_surface() -> dict[str, str]:
    return {surface: schema for schema, surface in SCHEMA_SURFACES.items()}


def _validator_status(root: pathlib.Path, validators: list[str]) -> tuple[str, list[str]]:
    missing = [validator for validator in validators if not (root / validator).exists()]
    return ("fail" if missing else "pass"), missing


def classify_surface(root: pathlib.Path, surface: str) -> dict[str, Any]:
    schema_map = schema_by_surface()
    if surface in schema_map:
        validators = ["tools/check_json_schema_surface_contract.py", "tools/check_schema_conformance_audit_contract.py"]
        status, missing = _validator_status(root, validators + [schema_map[surface]])
        return {
            "surface": surface,
            "coverage_class": "schema-backed",
            "schema": schema_map[surface],
            "validators": validators,
            "rationale": CLASS_RATIONALES["schema-backed"],
            "status": status,
            "missing": missing,
        }
    if surface in CONTRACT_ONLY_SURFACES:
        validators = CONTRACT_ONLY_SURFACES[surface]
        status, missing = _validator_status(root, validators)
        return {
            "surface": surface,
            "coverage_class": "contract-only",
            "schema": None,
            "validators": validators,
            "rationale": CLASS_RATIONALES["contract-only"],
            "status": status,
            "missing": missing,
        }
    if surface in EXTERNAL_STANDARD_SURFACES:
        validators = EXTERNAL_STANDARD_SURFACES[surface]
        status, missing = _validator_status(root, validators)
        return {
            "surface": surface,
            "coverage_class": "external-standard",
            "schema": None,
            "validators": validators,
            "rationale": CLASS_RATIONALES["external-standard"],
            "status": status,
            "missing": missing,
        }
    return {
        "surface": surface,
        "coverage_class": "unclassified",
        "schema": None,
        "validators": [],
        "rationale": "no schema coverage policy row admitted yet",
        "status": "fail",
        "missing": ["coverage classification"],
    }


def build_schema_coverage_audit(root: pathlib.Path) -> dict[str, Any]:
    receipt = _load_json(root / "REVISION-RECEIPT.json")
    surfaces = root_json_surfaces(root)
    rows = [classify_surface(root, surface) for surface in surfaces]
    failures = [row for row in rows if row["status"] != "pass"]
    counts: dict[str, int] = {
        "root_json_count": len(surfaces),
        "schema_backed_count": sum(1 for row in rows if row["coverage_class"] == "schema-backed"),
        "contract_only_count": sum(1 for row in rows if row["coverage_class"] == "contract-only"),
        "external_standard_count": sum(1 for row in rows if row["coverage_class"] == "external-standard"),
        "unclassified_count": sum(1 for row in rows if row["coverage_class"] == "unclassified"),
        "failures": len(failures),
    }
    return {
        "project": "DelayBasin",
        "revision": receipt["revision"],
        "surface": "SCHEMA-COVERAGE-AUDIT.json",
        "guide_surface": "docs/00-meta/schema-coverage-audit.md",
        "state": "generated-schema-coverage-audit",
        "generated_from": [
            "REVISION-RECEIPT.json",
            "tools/schema_coverage_lib.py",
            "tools/schema_conformance_lib.py",
            "schemas/*.schema.json",
            "root *.json surfaces",
        ],
        "coverage_policy": {
            "schema_backed": "local schemas must be present in schema_conformance_lib.SCHEMA_SURFACES and checked by schema conformance contracts",
            "contract_only": "bespoke contract checks are allowed only when named as validators in this audit row",
            "external_standard": "external metadata standards are checked by metadata contracts, not replaced by DelayBasin-local schema authority",
            "unclassified": "not allowed in a release package",
        },
        "non_claim": NON_CLAIM,
        "coverage_rows": rows,
        "counts": counts,
        "failures": failures,
    }


def render_schema_coverage_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Schema coverage audit",
        "",
        "This generated surface inventories every root JSON surface and records whether it is local-schema-backed, contract-only, or governed as an external-standard metadata surface.",
        "It exists because schema conformance can be green while unclassified JSON surfaces remain outside the schema/contract coverage map.",
        "",
        "## Non-authority boundary",
        "",
        "This is not a schema-coverage-court, schema-completeness-sovereign, contract-exemption-board, coverage-waiver-senate, schema-taxonomy-tribunal, public-surface-notary, validator-monopoly, or schema-backfill-authority.",
        "Schema coverage is an inventory and validator-routing witness only; it does not certify semantic truth, canon sufficiency, release legitimacy, legal status, minimality, or continuation authority.",
        "",
        "## Counts",
        "",
        f"- Root JSON surfaces: `{audit['counts']['root_json_count']}`",
        f"- Schema-backed: `{audit['counts']['schema_backed_count']}`",
        f"- Contract-only: `{audit['counts']['contract_only_count']}`",
        f"- External-standard: `{audit['counts']['external_standard_count']}`",
        f"- Unclassified: `{audit['counts']['unclassified_count']}`",
        f"- Failures: `{audit['counts']['failures']}`",
        "",
        "## Coverage rows",
    ]
    for row in audit["coverage_rows"]:
        schema = row.get("schema") or "—"
        validators = ", ".join(f"`{item}`" for item in row.get("validators", [])) or "—"
        lines.append(f"- `{row['surface']}` — `{row['coverage_class']}`; schema `{schema}`; validators {validators}; status `{row['status']}`")
    if audit["failures"]:
        lines.append("")
        lines.append("## Failures")
        for row in audit["failures"]:
            lines.append(f"- `{row['surface']}` — `{row['coverage_class']}` missing {row.get('missing')}")
    return "\n".join(lines).rstrip() + "\n"


def write_schema_coverage_audit(root: pathlib.Path) -> dict[str, Any]:
    audit = build_schema_coverage_audit(root)
    (root / "SCHEMA-COVERAGE-AUDIT.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "docs/00-meta/schema-coverage-audit.md").write_text(render_schema_coverage_markdown(audit), encoding="utf-8")
    return audit
