#!/usr/bin/env python3
"""Audit the canonical mission/debt artifacts without generating strategic evidence.

This is intentionally a reusable current-state audit rather than another
``run_rev####`` experiment runner.  By default it audits rev0090 and writes the
small machine-readable report used by the cube audit; callers may choose a
revision/output for later canonical mission updates.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--revision", default="rev0090")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    revision = str(args.revision)
    output = args.output or (root / "data" / f"{revision}_artifact_audit.json")
    if not output.is_absolute():
        output = root / output

    required = [
        "docs/CURRENT_MISSION.md",
        f"data/{revision}_mission_reassessment.json",
        f"data/{revision}_structure_inventory.json",
        f"data/{revision}_evidence_tiering_catalog.json",
        f"data/{revision}_evidence_bundle_audit.json",
        "scripts/audit_mission_debt.py",
    ]
    missing = [rel for rel in required if not (root / rel).is_file()]
    errors: list[str] = []

    mission: dict[str, Any] = {}
    inventory: dict[str, Any] = {}
    bundle: dict[str, Any] = {}
    if not missing:
        try:
            mission = load_json(root / "data" / f"{revision}_mission_reassessment.json")
            inventory = load_json(root / "data" / f"{revision}_structure_inventory.json")
            bundle = load_json(root / "data" / f"{revision}_evidence_bundle_audit.json")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"json_load: {type(exc).__name__}: {exc}")

    expected_critical = {
        "INFO-STATE-001",
        "JACE-MEMORY-001",
        "PUBLIC-EVENT-001",
        "SPEC-DRIFT-001",
        "CLAIM-LEDGER-DRIFT-001",
        "CPP-INDEPENDENCE-001",
        "AGENT-CACHE-001",
        "SIDECAR-PROVENANCE-001",
        "VALIDATION-MUTATION-001",
        "POLICY-REPLAY-COVERAGE-001",
    }
    observed_critical = {
        str(row.get("id"))
        for row in mission.get("critical_findings", [])
        if isinstance(row, dict)
    }
    if mission and mission.get("schema") != "muc5.mission_reassessment.v1":
        errors.append("mission schema mismatch")
    if mission and mission.get("revision") != revision:
        errors.append("mission revision mismatch")
    if mission and not expected_critical.issubset(observed_critical):
        errors.append(f"missing critical finding ids: {sorted(expected_critical - observed_critical)}")
    scope = mission.get("revision_scope", {}) if isinstance(mission, dict) else {}
    if mission and scope.get("game_semantics_changed") is not False:
        errors.append("rev0090 must not claim a game-semantics change")
    if mission and scope.get("strategic_evidence_generated") is not False:
        errors.append("rev0090 must not claim new strategic evidence")

    summary = inventory.get("summary", {}) if isinstance(inventory, dict) else {}
    inventory_floor_checks = {
        "files_at_least_2300": int(summary.get("files", 0)) >= 2300,
        "revision_docs_at_least_500": int(summary.get("revision_stamped_docs", 0)) >= 500,
        "one_off_runners_at_least_120": int(summary.get("one_off_run_rev_scripts", 0)) >= 120,
        "audit_cube_lines_at_least_4800": int(summary.get("audit_cube_lines", 0)) >= 4800,
        "hot_evidence_bytes_positive": int(summary.get("hot_evidence_bytes", 0)) > 0,
    }
    for name, passed in inventory_floor_checks.items():
        if inventory and not passed:
            errors.append(f"inventory check failed: {name}")

    current_verification = bundle.get("current_revision_verification", {}) if isinstance(bundle, dict) else {}
    availability = bundle.get("availability", {}) if isinstance(bundle, dict) else {}
    sidecar_semantics = {
        "schema_v2": bundle.get("schema") == "muc5.evidence_bundle_status.v2",
        "not_physically_reverified": current_verification.get("physically_reverified_this_revision") is False,
        "bundle_not_claimed_present": current_verification.get("bundle_physically_present") is False,
        "external_bundle_required": availability.get("status") == "external_bundle_required",
        "durable_uri_explicitly_unknown": "durable_uri" in availability and availability.get("durable_uri") is None,
        "generic_pass_not_asserted": bundle.get("passed") is None,
    }
    for name, passed in sidecar_semantics.items():
        if bundle and not passed:
            errors.append(f"sidecar semantic check failed: {name}")

    forbidden_docs = [
        root / "docs" / f"refactor_audit_{revision}.md",
        root / "docs" / f"priority_reconsideration_{revision}.md",
        root / "docs" / f"experiment_matrix_{revision}.md",
    ]
    forbidden_present = [p.relative_to(root).as_posix() for p in forbidden_docs if p.exists()]
    if forbidden_present:
        errors.append("rev0090 reintroduced repeated narrative boilerplate")

    forbidden_raw = []
    for pattern in (f"data/{revision}_*.csv", f"data/{revision}_*.jsonl", f"data/{revision}_*.csv.gz"):
        forbidden_raw.extend(p.relative_to(root).as_posix() for p in root.glob(pattern))
    if forbidden_raw:
        errors.append("mission-only revision unexpectedly contains raw strategic rows")

    report = {
        "schema": "muc5.mission_artifact_audit.v1",
        "revision": revision,
        "passed": not missing and not errors,
        "expected_count": len(required),
        "missing": missing,
        "errors": errors,
        "critical_finding_ids_expected": sorted(expected_critical),
        "critical_finding_ids_observed": sorted(observed_critical),
        "inventory_floor_checks": inventory_floor_checks,
        "sidecar_semantic_checks": sidecar_semantics,
        "forbidden_present": sorted(forbidden_present),
        "forbidden_raw_strategic_artifacts": sorted(set(forbidden_raw)),
        "note": "Canonical mission audit only; no game simulation or strategic evidence generation.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
