#!/usr/bin/env python3
"""Observed matter-sector denominator source-role checks.

Current particle/Higgs/neutrino/muon, QCD/hadronic, and electroweak/flavor/neutrino sources are cross-route
denominators: every route must not overclaim observed-sector recovery against
them, but the sources must not be spent as acquired evidence-unit support or
route promotion.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/observed-sector-matter-source-role-audit.generated.md"
CURRENT_MATTER_REFS = ["REF-0392", "REF-0699", "REF-0700", "REF-0701", "REF-0712", "REF-0713", "REF-0714", "REF-0719", "REF-0720", "REF-0721", "REF-0722", "REF-0723", "REF-0724"]
QCD_HADRONIC_REFS = ["REF-0712", "REF-0713", "REF-0714"]
ELECTROWEAK_FLAVOR_REFS = ["REF-0719", "REF-0720", "REF-0721", "REF-0722", "REF-0723", "REF-0724"]
QCD_FORECAST_ID = "DF-0026-QCD-HADRONIC-OBSERVED-SECTOR-REPLAY"
QCD_DELTA_ID = "ED-0032-QCD-HADRONIC-OBSERVED-SECTOR-PRESSURE"
QCD_DECISION_ID = "DX-0019-QCD-HADRONIC-OBSERVED-SECTOR-REPLAY"
ELECTROWEAK_FORECAST_ID = "DF-0028-ELECTROWEAK-FLAVOR-NEUTRINO-OBSERVED-SECTOR-REPLAY"
ELECTROWEAK_DELTA_ID = "ED-0034-ELECTROWEAK-FLAVOR-NEUTRINO-OBSERVED-SECTOR-PRESSURE"
ELECTROWEAK_DECISION_ID = "DX-0021-ELECTROWEAK-FLAVOR-NEUTRINO-OBSERVED-SECTOR-REPLAY"
QCD_METADATA_WRAPPER_ID = "EU-0014-METADATA-PROVENANCE-WRAPPER"
MATTER_LEDGER_SPECS = [
    ("PARTICLE-SPECTRUM-LEDGER.json", "particle_spectrum_rows", "particle_spectrum_id", ["observed_sector_gap", "forbidden_inference", "observed_sector_matter_credit_rule"]),
    ("INTERACTION-COUPLING-LEDGER.json", "interaction_coupling_rows", "interaction_coupling_id", ["public_record_or_fit_gap", "forbidden_inference", "observed_sector_matter_credit_rule"]),
    ("MASS-HIERARCHY-LEDGER.json", "mass_hierarchy_rows", "mass_hierarchy_id", ["neutrino_flavor_or_hierarchy_gap", "hierarchy_naturalness_or_parameter_count_risk", "forbidden_inference", "observed_sector_matter_credit_rule"]),
]
S_LEVEL = {"S0": 0, "S1": 1, "S2": 2, "S3": 3, "S4": 4, "S5": 5}
SM_OBLIGATION = "OSR-STANDARD-MODEL-MATTER"
WRAPPER_TOKEN = "METADATA-PROVENANCE-WRAPPER"


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def route_ids_for_row(row: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key, val in row.items():
        if "route" not in key:
            continue
        if isinstance(val, str) and val.startswith("R-"):
            out.append(val)
        elif isinstance(val, list):
            out.extend(item for item in val if isinstance(item, str) and item.startswith("R-"))
    dedup: list[str] = []
    for rid in out:
        if rid not in dedup:
            dedup.append(rid)
    return dedup


def duplicate_refs(row: dict[str, Any]) -> list[str]:
    seen: set[str] = set()
    dup: list[str] = []
    for ref in row.get("source_refs", []) or []:
        if ref in seen and ref not in dup:
            dup.append(ref)
        seen.add(ref)
    return dup


def text_terms(row: dict[str, Any], keys: list[str]) -> str:
    parts: list[str] = []
    for key in keys:
        val = row.get(key)
        if isinstance(val, str):
            parts.append(val)
        elif isinstance(val, list):
            parts.extend(str(x) for x in val)
        elif isinstance(val, dict):
            parts.extend(str(x) for x in val.values())
    return " ".join(parts).lower()


def all_evidence_unit_refs(root: Path) -> dict[str, list[str]]:
    rows = load_json(root, "EVIDENCE-UNIT-LEDGER.json").get("evidence_units", [])
    return {row.get("evidence_unit_id", "<missing>"): list(row.get("source_refs", []) or []) for row in rows if isinstance(row, dict)}


def row_lookup(rows: list[dict[str, Any]], id_field: str, row_id: str) -> dict[str, Any] | None:
    for row in rows:
        if isinstance(row, dict) and row.get(id_field) == row_id:
            return row
    return None


def row_identifier(row: dict[str, Any], id_field: str) -> str:
    return str(row.get(id_field, "<missing>"))


def is_wrapper_row(row_id: str) -> bool:
    return WRAPPER_TOKEN in row_id


def evaluate_observed_sector_matter(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    failures: list[str] = []
    ledger_summaries: list[dict[str, Any]] = []

    route_rows = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json").get("route_rows", [])
    routes = {row.get("route_id"): row for row in route_rows if isinstance(row, dict) and isinstance(row.get("route_id"), str)}
    route_ceiling = {rid: row.get("promotion_ceiling") or row.get("authority_state") for rid, row in routes.items()}
    route_state = {rid: row.get("authority_state") for rid, row in routes.items()}
    sm_routes = {rid for rid, row in routes.items() if SM_OBLIGATION in row.get("observed_sector_obligations", [])}

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            failures.append(f"{name}: {detail}")

    add("route-count-unchanged", len(route_rows) == 13, f"route_rows={len(route_rows)}")
    add("standard-model-obligation-routes-present", sm_routes == {"R-OQ0057-STRINGM-ATLAS", "R-OQ0057-ASYMPTOTIC-SAFETY", "R-OQ0057-CAUSAL-SET"}, f"sm_routes={sorted(sm_routes)}")

    acquired_ref_hits: list[str] = []
    for eu_id, refs in all_evidence_unit_refs(root).items():
        bad = [ref for ref in CURRENT_MATTER_REFS if ref in refs]
        if bad:
            acquired_ref_hits.append(f"{eu_id}:{','.join(bad)}")
    add("current-matter-refs-not-acquired-evidence", not acquired_ref_hits, f"hits={acquired_ref_hits}")

    total_rows = 0
    route_bearing_rows = 0
    sm_burden_rows = 0
    denominator_only_rows = 0
    wrapper_rows = 0
    cap_checks = 0
    qcd_denominator_rows = 0
    electroweak_flavor_denominator_rows = 0

    for rel, collection, id_field, language_keys in MATTER_LEDGER_SPECS:
        rows = load_json(root, rel).get(collection, [])
        ledger_failures_before = len(failures)
        for row in rows:
            if not isinstance(row, dict):
                continue
            total_rows += 1
            row_id = row_identifier(row, id_field)
            routes_for_row = route_ids_for_row(row)
            if routes_for_row:
                route_bearing_rows += 1
            refs = row.get("source_refs", []) or []
            present_current_refs = [ref for ref in CURRENT_MATTER_REFS if ref in refs]
            wrapper = is_wrapper_row(row_id)

            if wrapper:
                wrapper_rows += 1
                add(f"matter-wrapper-no-current-refs-{row_id}", not present_current_refs, f"present_current_refs={present_current_refs}")
            else:
                missing = [ref for ref in CURRENT_MATTER_REFS if ref not in refs]
                add(f"matter-current-refs-present-{row_id}", not missing, f"missing_refs={missing}")

            dup = duplicate_refs(row)
            add(f"matter-source-refs-deduped-{row_id}", not dup, f"duplicate_refs={dup}")

            effect = row.get("maximum_authority_effect")
            for rid in routes_for_row:
                ceiling = route_ceiling.get(rid)
                passed = effect in S_LEVEL and ceiling in S_LEVEL and S_LEVEL[effect] <= S_LEVEL[ceiling]
                add(f"matter-row-ceiling-{row_id}-{rid}", passed, f"effect={effect}; route_ceiling={ceiling}; route_state={route_state.get(rid)}")

            role = row.get("observed_sector_matter_credit_role")
            cap = row.get("observed_sector_matter_credit_cap")
            rule = row.get("observed_sector_matter_credit_rule")
            add(f"matter-credit-role-present-{row_id}", isinstance(role, str) and bool(role), f"role={role}")
            add(f"matter-credit-cap-valid-{row_id}", cap in S_LEVEL, f"cap={cap}")
            add(f"matter-credit-rule-present-{row_id}", isinstance(rule, str) and ("not" in rule.lower() or "forbidden" in rule.lower()), f"rule={rule}")
            cap_checks += 1

            qcd_role = row.get("qcd_hadronic_credit_role")
            qcd_cap = row.get("qcd_hadronic_credit_cap")
            qcd_rule = str(row.get("qcd_hadronic_credit_rule", "")).lower()
            add(f"matter-qcd-credit-role-present-{row_id}", isinstance(qcd_role, str) and bool(qcd_role), f"role={qcd_role}")
            add(f"matter-qcd-credit-cap-S0-{row_id}", qcd_cap == "S0", f"cap={qcd_cap}")
            add(f"matter-qcd-nonpromotion-rule-{row_id}", "not" in qcd_rule and ("promotion" in qcd_rule or "support" in qcd_rule or "evidence" in qcd_rule), f"rule={row.get('qcd_hadronic_credit_rule')}")

            ew_role = row.get("electroweak_flavor_credit_role")
            ew_cap = row.get("electroweak_flavor_credit_cap")
            ew_rule = str(row.get("electroweak_flavor_credit_rule", "")).lower()
            ew_burden = row.get("electroweak_flavor_replay_burden")
            add(f"matter-ewflavor-credit-role-present-{row_id}", isinstance(ew_role, str) and bool(ew_role), f"role={ew_role}")
            add(f"matter-ewflavor-credit-cap-S0-{row_id}", ew_cap == "S0", f"cap={ew_cap}")
            add(f"matter-ewflavor-nonpromotion-rule-{row_id}", "not" in ew_rule and ("promotion" in ew_rule or "support" in ew_rule or "evidence" in ew_rule), f"rule={row.get('electroweak_flavor_credit_rule')}")
            add(f"matter-ewflavor-replay-burden-present-{row_id}", isinstance(ew_burden, str) and all(term in ew_burden.lower() for term in ["electroweak", "flavor", "neutrino"]), f"burden={ew_burden}")
            if not wrapper:
                qcd_denominator_rows += 1
                electroweak_flavor_denominator_rows += 1

            if wrapper:
                add(f"matter-wrapper-cap-S0-{row_id}", role == "metadata-wrapper-denominator-only" and cap == "S0", f"role={role}; cap={cap}")
                route_caps = row.get("route_observed_sector_matter_credit_caps", {})
                add(f"matter-wrapper-route-caps-S0-{row_id}", isinstance(route_caps, dict) and all(value == "S0" for value in route_caps.values()), f"route_caps={route_caps}")
                continue

            if len(routes_for_row) == 1:
                rid = routes_for_row[0]
                if rid in sm_routes:
                    sm_burden_rows += 1
                    state = route_state.get(rid)
                    ok = role == "observed-sector-burden-open" and cap in S_LEVEL and state in S_LEVEL and S_LEVEL[cap] <= S_LEVEL[state]
                    add(f"matter-sm-burden-cap-current-{row_id}", ok, f"route={rid}; role={role}; cap={cap}; route_state={state}")
                else:
                    denominator_only_rows += 1
                    ok = role == "denominator-control-only" and cap == "S0"
                    add(f"matter-non-sm-route-cap-S0-{row_id}", ok, f"route={rid}; role={role}; cap={cap}")
            else:
                add(f"matter-row-route-cardinality-{row_id}", False, f"unexpected routes={routes_for_row}")

            text = text_terms(row, language_keys)
            required_terms = ["not", "recover", "sector"]
            if rel == "INTERACTION-COUPLING-LEDGER.json":
                required_terms += ["fit"]
            if rel == "MASS-HIERARCHY-LEDGER.json":
                required_terms += ["neutrino"]
            missing_terms = [term for term in required_terms if term not in text]
            add(f"matter-denominator-language-{row_id}", not missing_terms, f"missing_terms={missing_terms}")
        ledger_summaries.append({"ledger_file": rel, "rows": len(rows), "failures": len(failures) - ledger_failures_before})

    qcd_pressure_rows = [
        ("forecast", row_lookup(load_json(root, "DISCRIMINATOR-FORECAST-LEDGER.json").get("forecast_rows", []), "forecast_id", QCD_FORECAST_ID)),
        ("delta", row_lookup(load_json(root, "EMPIRICAL-DELTA-LEDGER.json").get("empirical_deltas", []), "delta_id", QCD_DELTA_ID)),
        ("decision", row_lookup(load_json(root, "DECISION-EXPERIMENT-LEDGER.json").get("decision_experiments", []), "experiment_id", QCD_DECISION_ID)),
    ]
    ew_pressure_rows = [
        ("forecast", row_lookup(load_json(root, "DISCRIMINATOR-FORECAST-LEDGER.json").get("forecast_rows", []), "forecast_id", ELECTROWEAK_FORECAST_ID)),
        ("delta", row_lookup(load_json(root, "EMPIRICAL-DELTA-LEDGER.json").get("empirical_deltas", []), "delta_id", ELECTROWEAK_DELTA_ID)),
        ("decision", row_lookup(load_json(root, "DECISION-EXPERIMENT-LEDGER.json").get("decision_experiments", []), "experiment_id", ELECTROWEAK_DECISION_ID)),
    ]
    for family, refs, pressure_rows in [("qcd", QCD_HADRONIC_REFS, qcd_pressure_rows), ("ewflavor", ELECTROWEAK_FLAVOR_REFS, ew_pressure_rows)]:
        for label, row in pressure_rows:
            add(f"{family}-{label}-row-present", isinstance(row, dict), f"present={isinstance(row, dict)}")
            if isinstance(row, dict):
                missing = [ref for ref in refs if ref not in row.get("source_refs", [])]
                add(f"{family}-{label}-refs-present", not missing, f"missing={missing}")
                caps = row.get("route_authority_ceilings", {})
                add(f"{family}-{label}-caps-S0", isinstance(caps, dict) and caps and all(value == "S0" for value in caps.values()), f"caps={caps}")
                text_blob = " ".join(str(v) for v in row.values() if isinstance(v, (str, int, float))).lower()
                add(f"{family}-{label}-nonpromotion-language", "not" in text_blob and ("promotion" in text_blob or "evidence" in text_blob or "support" in text_blob), f"nonpromotion_present={('not' in text_blob)}")
    eu_rows = load_json(root, "EVIDENCE-UNIT-LEDGER.json").get("evidence_units", [])
    route_specific_eus = [row for row in eu_rows if isinstance(row, dict) and row.get("evidence_unit_id") != QCD_METADATA_WRAPPER_ID]
    missing_reciprocal_eus = [row.get("evidence_unit_id") for row in route_specific_eus if QCD_DELTA_ID not in (row.get("empirical_delta_ids", []) or [])]
    add("qcd-route-evidence-units-reciprocate-delta", not missing_reciprocal_eus, f"missing={missing_reciprocal_eus}")
    missing_ew_reciprocal_eus = [row.get("evidence_unit_id") for row in route_specific_eus if ELECTROWEAK_DELTA_ID not in (row.get("empirical_delta_ids", []) or [])]
    add("ewflavor-route-evidence-units-reciprocate-delta", not missing_ew_reciprocal_eus, f"missing={missing_ew_reciprocal_eus}")
    wrapper = row_lookup(eu_rows, "evidence_unit_id", QCD_METADATA_WRAPPER_ID)
    add("qcd-metadata-wrapper-lacks-delta-handle", isinstance(wrapper, dict) and QCD_DELTA_ID not in (wrapper.get("empirical_delta_ids", []) or []), f"empirical_delta_ids={wrapper.get('empirical_delta_ids') if isinstance(wrapper, dict) else None}")
    add("ewflavor-metadata-wrapper-lacks-delta-handle", isinstance(wrapper, dict) and ELECTROWEAK_DELTA_ID not in (wrapper.get("empirical_delta_ids", []) or []), f"empirical_delta_ids={wrapper.get('empirical_delta_ids') if isinstance(wrapper, dict) else None}")
    evidence_ref_hits = []
    ew_evidence_ref_hits = []
    for row in eu_rows:
        if not isinstance(row, dict):
            continue
        bad = [ref for ref in QCD_HADRONIC_REFS if ref in (row.get("source_refs", []) or [])]
        if bad:
            evidence_ref_hits.append(f"{row.get('evidence_unit_id')}:{','.join(bad)}")
        ew_bad = [ref for ref in ELECTROWEAK_FLAVOR_REFS if ref in (row.get("source_refs", []) or [])]
        if ew_bad:
            ew_evidence_ref_hits.append(f"{row.get('evidence_unit_id')}:{','.join(ew_bad)}")
    add("qcd-refs-not-in-any-evidence-unit-source-refs", not evidence_ref_hits, f"hits={evidence_ref_hits}")
    add("ewflavor-refs-not-in-any-evidence-unit-source-refs", not ew_evidence_ref_hits, f"hits={ew_evidence_ref_hits}")

    # Current matter refs are intentionally broad burden refs, but they may live
    # only on route-specific matter ledgers, the observed-sector obligation row,
    # freshness assertions, and the explicit QCD pressure rows. They must not leak
    # into metadata/evidence units.
    misplaced: list[str] = []
    allowed_files = {spec[0] for spec in MATTER_LEDGER_SPECS} | {"FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json", "OBSERVED-SECTOR-RECOVERY-LEDGER.json", "DISCRIMINATOR-FORECAST-LEDGER.json", "EMPIRICAL-DELTA-LEDGER.json", "DECISION-EXPERIMENT-LEDGER.json", "EVIDENCE-UNIT-LEDGER.json", "CANDIDATE-ROUTE-STATE-LEDGER.json"}
    for path in sorted(root.glob("*.json")):
        if path.name in allowed_files:
            continue
        try:
            obj = json.loads(path.read_text())
        except Exception:
            continue
        def walk(x: Any) -> bool:
            if isinstance(x, dict):
                return any(walk(v) for v in x.values())
            if isinstance(x, list):
                return any(walk(v) for v in x)
            return isinstance(x, str) and x in CURRENT_MATTER_REFS
        if walk(obj):
            misplaced.append(path.name)
    add("current-matter-refs-only-in-matter-ledgers", not misplaced, f"misplaced_files={misplaced}")

    return {
        "audit_file": GENERATED_AUDIT,
        "current_refs": CURRENT_MATTER_REFS,
        "ledger_summaries": ledger_summaries,
        "total_matter_rows": total_rows,
        "route_bearing_rows": route_bearing_rows,
        "standard_model_burden_rows": sm_burden_rows,
        "denominator_only_rows": denominator_only_rows,
        "wrapper_rows": wrapper_rows,
        "matter_credit_cap_checks": cap_checks,
        "qcd_denominator_rows": qcd_denominator_rows,
        "qcd_hadronic_refs": QCD_HADRONIC_REFS,
        "electroweak_flavor_denominator_rows": electroweak_flavor_denominator_rows,
        "electroweak_flavor_refs": ELECTROWEAK_FLAVOR_REFS,
        "checks": checks,
        "failures": failures,
    }


def refs_text(refs: list[str]) -> str:
    return ", ".join(f"`{ref}`" for ref in refs) if refs else "—"


def write_observed_sector_matter_audit(root: Path) -> None:
    result = evaluate_observed_sector_matter(root)
    lines = [
        "# Observed-sector matter source-role audit (generated)",
        "",
        "Generated from particle-spectrum, interaction-coupling, mass-hierarchy, evidence-unit, observed-sector, and route-state ledgers. Do not edit directly; run `make index` after changing matter-sector denominator pressure.",
        "",
        f"- Current matter/QCD denominator refs: {refs_text(result['current_refs'])}",
        f"- QCD/hadronic denominator refs: {refs_text(result['qcd_hadronic_refs'])}",
        f"- Electroweak/flavor/neutrino denominator refs: {refs_text(result['electroweak_flavor_refs'])}",
        f"- Matter rows checked: `{result['total_matter_rows']}`",
        f"- Route-bearing matter rows checked: `{result['route_bearing_rows']}`",
        f"- Standard-Model-obligation burden rows: `{result['standard_model_burden_rows']}`",
        f"- Denominator-only non-SM route rows: `{result['denominator_only_rows']}`",
        f"- Metadata wrapper rows capped at S0: `{result['wrapper_rows']}`",
        f"- Matter-credit cap checks: `{result['matter_credit_cap_checks']}`",
        f"- QCD/hadronic denominator route rows: `{result['qcd_denominator_rows']}`",
        f"- Electroweak/flavor/neutrino denominator route rows: `{result['electroweak_flavor_denominator_rows']}`",
        f"- Observed-sector matter checks: `{len(result['checks'])}`",
        f"- Observed-sector matter failures: `{len(result['failures'])}`",
        "",
        "## Ledger summary",
        "",
        "| Ledger | Rows | Failures |",
        "|---|---:|---:|",
    ]
    for item in result["ledger_summaries"]:
        lines.append(f"| `{item['ledger_file']}` | `{item['rows']}` | `{item['failures']}` |")
    lines += ["", "## Failure details", ""]
    if result["failures"]:
        lines.extend(f"- {failure}" for failure in result["failures"])
    else:
        lines.append("- None.")
    lines += [
        "",
        "## Non-promotion rule",
        "",
        "Current observed-particle, Higgs, muon, neutrino, QCD/hadronic, electroweak-precision, CKM/flavor, and neutrino-oscillation refs are denominator/burden refs. They make matter-sector, strong-coupling, confinement, hadron-spectrum, quark-mass, coupling, electroweak input-scheme, flavor/CKM, and neutrino-mass/mixing claims harder to spend; they do not supply acquired candidate-native evidence or promote any route. Routes without `OSR-STANDARD-MODEL-MATTER` carry explicit S0 observed-matter credit caps on these ledgers, and the explicit QCD and electroweak/flavor/neutrino pressure rows are capped at S0 for every route.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_observed_sector_matter_audit(root)
    outcome = evaluate_observed_sector_matter(root)
    if outcome["failures"]:
        print("OBSERVED SECTOR MATTER FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("OBSERVED SECTOR MATTER OK")
