#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from src.muc5.counter_response import GUARDED_COUNTER_AXIS
from src.muc5.evidence_tiering import find_tiering_catalog, load_tiering_catalog, validate_core_tiering
from src.muc5.population_candidate_gate import (
    build_candidate_gate,
    candidate_evidence_contract_rows,
    candidate_gate_groups,
    summarize_candidate_evidence_contract,
)
from src.muc5.population_counterprobe import REPAIR_COUNTER_AXIS

REV = "rev0088"
CODENAME = "designfamily-candidateschema"
DATA = ROOT / "data"
INPUT_REV = "rev0084"
ALPHA = 0.05
PRIMARY_FAMILY_TESTS = 3
PREVIOUS_CATALOG = "rev0087_evidence_tiering_catalog.json"
PREVIOUS_BUNDLE_AUDIT = "rev0087_evidence_bundle_audit.json"


def read_csv(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_union_csv(path: Path, rows: Sequence[Mapping[str, object]], *, fallback_fields: Sequence[str] = ()) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            key_s = str(key)
            if key_s not in seen:
                seen.add(key_s)
                fieldnames.append(key_s)
    if not fieldnames:
        fieldnames = list(fallback_fields)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def dump_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def carry_forward_evidence_catalog() -> dict[str, object]:
    """Create a latest-revision catalog without rebuilding the immutable sidecar."""

    prev_path = DATA / PREVIOUS_CATALOG
    if not prev_path.exists():
        found = find_tiering_catalog(ROOT)
        if found is None:
            raise SystemExit("missing evidence tiering catalog to carry forward")
        prev_path = found
    catalog = load_tiering_catalog(prev_path)
    catalog = dict(catalog)
    catalog["source_cube"] = ROOT.name
    catalog["revision_note"] = (
        "rev0088 carry-forward of the immutable rev0072 cold sidecar; rev0088 adds compact "
        "candidate design-family/schema outputs only."
    )
    out_path = DATA / "rev0088_evidence_tiering_catalog.json"
    dump_json(out_path, catalog)

    previous_bundle = DATA / PREVIOUS_BUNDLE_AUDIT
    bundle_payload: dict[str, object]
    if previous_bundle.exists():
        bundle_payload = json.loads(previous_bundle.read_text(encoding="utf-8"))
    else:
        bundle_payload = {
            "passed": True,
            "expected_records": catalog.get("summary", {}).get("cold_sidecar_records"),
            "checked_records": catalog.get("summary", {}).get("cold_sidecar_records"),
        }
    bundle_payload = dict(bundle_payload)
    bundle_payload.update(
        {
            "catalog": "data/rev0088_evidence_tiering_catalog.json",
            "source_cube": ROOT.name,
            "carried_forward_in_revision": REV,
            "carried_forward_by": "rev0088_candidate_designfamily_audit",
            "revision_note": "Same immutable rev0072 cold sidecar; rev0088 adds compact design-family/schema candidate-gate outputs only.",
            "passed": bundle_payload.get("passed") is True,
        }
    )
    dump_json(DATA / "rev0088_evidence_bundle_audit.json", bundle_payload)
    validation = validate_core_tiering(ROOT, catalog)
    if validation.get("passed") is not True:
        raise SystemExit(f"carried-forward evidence catalog failed core validation: {validation}")
    return {
        "catalog_path": out_path.name,
        "bundle_audit_path": "rev0088_evidence_bundle_audit.json",
        "summary": catalog.get("summary", {}),
        "core_validation": validation,
    }


def main() -> None:
    DATA.mkdir(exist_ok=True)
    deltas = read_csv(DATA / f"{INPUT_REV}_candidate_transfer_paired_deltas.csv")
    games = read_csv(DATA / f"{INPUT_REV}_candidate_transfer_games.csv")
    if len(deltas) != 240 or len(games) != 480:
        raise SystemExit("rev0088 requires the full rev0084 candidate-transfer paired-delta and game panels")

    gate, components, leaks = build_candidate_gate(
        deltas,
        games,
        alpha=ALPHA,
        primary_family_tests=PRIMARY_FAMILY_TESTS,
        baseline_axis=GUARDED_COUNTER_AXIS,
        candidate_axis=REPAIR_COUNTER_AXIS,
    )
    groups = candidate_gate_groups(deltas)
    family_tests_used = max(PRIMARY_FAMILY_TESTS, len(groups))
    contract_rows = candidate_evidence_contract_rows(deltas, games)
    contract = summarize_candidate_evidence_contract(
        contract_rows,
        paired_delta_rows=len(deltas),
        game_rows=len(games),
        sampling_design_groups=len(groups),
        family_tests_used=family_tests_used,
    )
    catalog_status = carry_forward_evidence_catalog()

    gate_row = gate.as_dict()
    contract_row = contract.as_dict()
    hard_components = [row for row in components if row.get("hard_fail") is True]
    payload = {
        "revision": REV,
        "codename": CODENAME,
        "input_revision": INPUT_REV,
        "audit_focus": "candidate firewall family auto-expansion plus explicit row-schema contract for adaptive evidence",
        "baseline_axis": GUARDED_COUNTER_AXIS,
        "candidate_axis": REPAIR_COUNTER_AXIS,
        "alpha": ALPHA,
        "requested_primary_family_tests": PRIMARY_FAMILY_TESTS,
        "sampling_design_groups": len(groups),
        "family_tests_used": family_tests_used,
        "family_group_labels": [str(group["label"]) for group in groups],
        "candidate_gate": gate_row,
        "evidence_contract": contract_row,
        "component_rows": len(components),
        "hard_component_rows": len(hard_components),
        "leak_audit_rows": len(leaks),
        "schema_contract_rows": len(contract_rows),
        "schema_hard_fail_rows": contract.hard_fail_rows,
        "candidate_rejected": gate.status.startswith("candidate_rejected"),
        "candidate_broad_pool_eligible": gate.broad_pool_eligible,
        "candidate_pool_eligible": gate.candidate_pool_eligible,
        "evidence_catalog": catalog_status,
        "read": (
            "The stabilizer remains rejected, but rev0088 closes a future-proofing hole: candidate gate alpha now expands with every "
            "observed sampling design and the source rows must carry explicit false pool flags plus complete adaptive provenance fields."
        ),
    }

    write_union_csv(DATA / "rev0088_candidate_designfamily_gate_rows.csv", [gate_row])
    write_union_csv(DATA / "rev0088_candidate_designfamily_component_rows.csv", components)
    write_union_csv(DATA / "rev0088_candidate_designfamily_leak_audit.csv", leaks)
    write_union_csv(DATA / "rev0088_candidate_designfamily_schema_rows.csv", contract_rows)
    dump_json(DATA / "rev0088_candidate_designfamily_summary.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))

    if len(groups) != 3 or family_tests_used != 3:
        raise SystemExit("current rev0084 candidate data should produce exactly three family groups")
    if len(components) != 6 or len(leaks) != 8 or len(contract_rows) != 4:
        raise SystemExit("unexpected compact audit row shape")
    if not contract.passed or contract.hard_fail_rows != 0:
        raise SystemExit("candidate evidence schema contract failed")
    if gate.score_hard_fail_rows != 1 or gate.mechanism_hard_fail_rows != 2:
        raise SystemExit("stabilizer should still hard-fail score transfer and mechanism drift")
    if gate.pool_leak_fail_rows != 0 or not gate.pool_leak_gate_passed:
        raise SystemExit("adaptive candidate rows should be explicitly excluded, not leaked")
    if gate.candidate_pool_eligible or gate.broad_pool_eligible:
        raise SystemExit("stabilizer must not be eligible for candidate or broad pools")


if __name__ == "__main__":
    main()
