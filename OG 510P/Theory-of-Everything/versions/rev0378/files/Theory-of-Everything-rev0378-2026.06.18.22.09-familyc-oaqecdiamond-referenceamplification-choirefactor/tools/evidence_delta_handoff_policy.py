#!/usr/bin/env python3
"""Check empirical-delta/evidence-unit handoff reciprocity.

Empirical deltas are route/source pressure. Evidence units may name those deltas
as accounting handles, but a metadata/provenance wrapper must not absorb route-
local pressure, and every delta->evidence link should be visible in both
ledgers.  This prevents pressure from becoming one-way, invisible, or smeared
through an S0 wrapper.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/evidence-delta-handoff-audit.generated.md"
METADATA_WRAPPER_ID = "EU-0014-METADATA-PROVENANCE-WRAPPER"


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def route_ids_for_handoff_row(row: dict[str, Any]) -> set[str]:
    route_ids = set(row.get("route_ids") or [])
    route_id = row.get("route_id")
    if isinstance(route_id, str) and route_id:
        route_ids.add(route_id)
    ceilings = row.get("route_authority_ceilings")
    if isinstance(ceilings, dict):
        route_ids.update(str(key) for key in ceilings if str(key).startswith("R-"))
    return route_ids


def evaluate_evidence_delta_handoff(root: Path) -> dict[str, Any]:
    deltas = load_json(root, "EMPIRICAL-DELTA-LEDGER.json").get("empirical_deltas", [])
    evidence_rows = load_json(root, "EVIDENCE-UNIT-LEDGER.json").get("evidence_units", [])
    delta_by_id = {row.get("delta_id", ""): row for row in deltas if isinstance(row, dict)}
    evidence_by_id = {row.get("evidence_unit_id", ""): row for row in evidence_rows if isinstance(row, dict)}
    failures: list[str] = []
    route_overlap_failures: list[str] = []

    delta_ids = [row.get("delta_id", "") for row in deltas if isinstance(row, dict)]
    duplicate_delta_ids = sorted({did for did in delta_ids if delta_ids.count(did) > 1})
    for did in duplicate_delta_ids:
        failures.append(f"duplicate empirical-delta id `{did}`")

    stems: dict[str, list[str]] = {}
    bad_delta_ids: list[str] = []
    for did in delta_ids:
        m = re.match(r"^(ED-\d{4})-", did)
        if not m:
            bad_delta_ids.append(did)
            continue
        stems.setdefault(m.group(1), []).append(did)
    duplicate_stems = {stem: ids for stem, ids in sorted(stems.items()) if len(ids) > 1}
    for stem, ids in duplicate_stems.items():
        failures.append(f"duplicate empirical-delta ordinal stem `{stem}`: {ids}")
    for did in bad_delta_ids:
        failures.append(f"malformed empirical-delta id `{did}`")

    handoffs = []
    for delta in deltas:
        did = delta.get("delta_id", "")
        for eu_id in delta.get("evidence_unit_ids", []) or []:
            handoffs.append((did, eu_id))
            evidence = evidence_by_id.get(eu_id)
            if evidence is None:
                failures.append(f"delta `{did}` references unknown evidence unit `{eu_id}`")
                continue
            if did not in (evidence.get("empirical_delta_ids") or []):
                failures.append(f"delta `{did}` -> evidence `{eu_id}` missing reciprocal evidence.empirical_delta_ids handle")
            delta_routes = route_ids_for_handoff_row(delta)
            evidence_routes = route_ids_for_handoff_row(evidence)
            if delta_routes and evidence_routes and not (delta_routes & evidence_routes):
                msg = f"delta `{did}` routes {sorted(delta_routes)} do not overlap evidence `{eu_id}` routes {sorted(evidence_routes)}"
                route_overlap_failures.append(msg)
                failures.append(msg)

    reciprocal_refs = []
    for evidence in evidence_rows:
        eu_id = evidence.get("evidence_unit_id", "")
        for did in evidence.get("empirical_delta_ids", []) or []:
            reciprocal_refs.append((eu_id, did))
            delta = delta_by_id.get(did)
            if delta is None:
                failures.append(f"evidence `{eu_id}` references unknown empirical delta `{did}`")
                continue
            expected = delta.get("evidence_unit_ids", []) or []
            if expected and eu_id not in expected:
                failures.append(f"evidence `{eu_id}` names delta `{did}`, but delta.evidence_unit_ids lacks that evidence unit")
            evidence_routes = route_ids_for_handoff_row(evidence)
            delta_routes = route_ids_for_handoff_row(delta)
            if evidence_routes and delta_routes and not (evidence_routes & delta_routes):
                msg = f"evidence `{eu_id}` routes {sorted(evidence_routes)} do not overlap delta `{did}` routes {sorted(delta_routes)}"
                route_overlap_failures.append(msg)
                failures.append(msg)

    wrapper = evidence_by_id.get(METADATA_WRAPPER_ID, {})
    wrapper_delta_count = len(wrapper.get("empirical_delta_ids", []) or [])
    if wrapper_delta_count:
        failures.append(f"metadata wrapper `{METADATA_WRAPPER_ID}` carries {wrapper_delta_count} route-local empirical-delta handles")

    return {
        "audit_file": GENERATED_AUDIT,
        "delta_rows": len(deltas),
        "evidence_rows": len(evidence_rows),
        "handoffs": handoffs,
        "reciprocal_refs": reciprocal_refs,
        "duplicate_delta_ids": duplicate_delta_ids,
        "duplicate_stems": duplicate_stems,
        "bad_delta_ids": bad_delta_ids,
        "metadata_wrapper_delta_count": wrapper_delta_count,
        "route_overlap_failures": route_overlap_failures,
        "failures": failures,
    }


def write_evidence_delta_handoff_audit(root: Path) -> None:
    result = evaluate_evidence_delta_handoff(root)
    lines = [
        "# Evidence-delta handoff audit (generated)",
        "",
        "Generated from `EMPIRICAL-DELTA-LEDGER.json` and `EVIDENCE-UNIT-LEDGER.json`. Do not edit directly; run `make index` after changing empirical-delta or evidence-unit rows.",
        "",
        f"- Empirical-delta rows: `{result['delta_rows']}`",
        f"- Evidence units: `{result['evidence_rows']}`",
        f"- Declared delta→evidence handoffs: `{len(result['handoffs'])}`",
        f"- Evidence→delta reciprocal handles: `{len(result['reciprocal_refs'])}`",
        f"- Evidence-delta handoff failures: `{len(result['failures'])}`",
        f"- Numeric-prefix duplicate failures: `{len(result['duplicate_stems'])}`",
        f"- Metadata-wrapper delta references: `{result['metadata_wrapper_delta_count']}`",
        f"- Route-overlap handoff failures: `{len(result['route_overlap_failures'])}`",
        "",
        "| Delta | Evidence unit | Reciprocal handle present | Route overlap |",
        "|---|---|---:|---:|",
    ]
    evidence_by_id = {row.get("evidence_unit_id", ""): row for row in load_json(root, "EVIDENCE-UNIT-LEDGER.json").get("evidence_units", [])}
    delta_by_id = {row.get("delta_id", ""): row for row in load_json(root, "EMPIRICAL-DELTA-LEDGER.json").get("empirical_deltas", [])}
    for did, eu_id in result["handoffs"]:
        present = did in (evidence_by_id.get(eu_id, {}).get("empirical_delta_ids", []) or [])
        delta_routes = route_ids_for_handoff_row(delta_by_id.get(did, {}))
        evidence_routes = route_ids_for_handoff_row(evidence_by_id.get(eu_id, {}))
        overlap = bool(delta_routes & evidence_routes) if delta_routes and evidence_routes else True
        lines.append(f"| `{did}` | `{eu_id}` | `{str(present).lower()}` | `{str(overlap).lower()}` |")
    if result["failures"]:
        lines += ["", "## Failures", ""]
        for failure in result["failures"]:
            lines.append(f"- {failure}")
    lines += [
        "",
        "## Non-promotion rule",
        "",
        "This audit only makes pressure accounting bidirectional and removes S0 metadata-wrapper bleed. Evidence units that name an empirical-delta handle do not acquire the delta's fresh source refs or promote a route; they expose where source-pressure is being accounted.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_evidence_delta_handoff_audit(root)
    outcome = evaluate_evidence_delta_handoff(root)
    if outcome["failures"]:
        print("EVIDENCE-DELTA HANDOFF POLICY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("EVIDENCE-DELTA HANDOFF POLICY OK")
