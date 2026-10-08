#!/usr/bin/env python3
"""Route-local source-role checks for amplitudes/bootstrap gravity-IR positivity pressure.

The amplitudes/bootstrap lane is useful as a constraint corridor, but gravity
makes the easy version dangerous: graviton poles, loops, IR/light-spectrum
assumptions, and kinematic-domain choices can change what a positivity or
bootstrap result means.  This check keeps current papers route-local and
prevents them from becoming acquired evidence or promotion.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/amplitudes-graviton-pole-bootstrap-audit.generated.md"
ROUTE_ID = "R-OQ0057-AMPLITUDES-BOOTSTRAP"
FORECAST_ID = "DF-0016-AMPLITUDES-GRAVITY-IR-LOOP-POSITIVITY-STABILITY"
DELTA_ID = "ED-0021-AMPLITUDES-GRAVITY-IR-POSITIVITY-PRESSURE"
DECISION_ID = "DX-0011-AMPLITUDES-BOOTSTRAP-CONSTRAINT-INVERSION"
EVIDENCE_ID = "EU-0007-AMPLITUDES-BOOTSTRAP-CONSISTENCY"
REQUIRED_REFS = ["REF-0652", "REF-0653", "REF-0654", "REF-0655", "REF-0656"]
CONDITION_REF_REQUIREMENTS = {
    ("STABILITY-POSITIVITY-LEDGER.json", "stability_rows", "stability_positivity_id", "STB-0007-AMPLITUDES-BOOTSTRAP"): ["REF-0652", "REF-0653", "REF-0654", "REF-0655"],
    ("SCATTERING-OBSERVABLE-LEDGER.json", "scattering_observable_rows", "scattering_observable_id", "SCAT-0007-AMPLITUDES-BOOTSTRAP"): ["REF-0652", "REF-0653", "REF-0656"],
    ("INFRARED-DRESSING-LEDGER.json", "infrared_dressing_rows", "infrared_dressing_id", "IRD-0007-AMPLITUDES-BOOTSTRAP"): ["REF-0654", "REF-0655"],
    ("ASYMPTOTIC-STATE-LEDGER.json", "asymptotic_state_rows", "asymptotic_state_id", "ASYM-0007-AMPLITUDES-BOOTSTRAP"): ["REF-0656"],
}
OLD_FAMILYC_DELTA_ID = "ED-0018-FAMILYC-SUBREGION-STATE-PORTABILITY-PRESSURE"
EXPECTED_FAMILYC_DELTA_ID = "ED-0020-FAMILYC-SUBREGION-STATE-PORTABILITY-PRESSURE"


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def find_row(rows: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    return next((row for row in rows if isinstance(row, dict) and row.get(key) == value), None)


def refs_text(refs: list[str]) -> str:
    return ", ".join(f"`{ref}`" for ref in refs) if refs else "—"


def empirical_delta_ordinal_status(root: Path) -> dict[str, Any]:
    rows = load_json(root, "EMPIRICAL-DELTA-LEDGER.json").get("empirical_deltas", [])
    stems: list[str] = []
    bad_ids: list[str] = []
    for row in rows:
        rid = row.get("delta_id", "") if isinstance(row, dict) else ""
        m = re.match(r"^(ED-\d{4})-", rid)
        if m:
            stems.append(m.group(1))
        else:
            bad_ids.append(rid)
    counts = {stem: stems.count(stem) for stem in set(stems)}
    duplicate_stems = sorted(stem for stem, count in counts.items() if count > 1)
    nums = sorted(int(stem.split("-")[1]) for stem in stems)
    missing = [n for n in range(nums[0], nums[-1] + 1) if n not in nums] if nums else []
    ids = {row.get("delta_id", "") for row in rows if isinstance(row, dict)}
    return {
        "row_count": len(rows),
        "duplicate_stems": duplicate_stems,
        "bad_ids": bad_ids,
        "missing_ordinals": missing,
        "old_familyc_present": OLD_FAMILYC_DELTA_ID in ids,
        "familyc_present": EXPECTED_FAMILYC_DELTA_ID in ids,
        "amplitudes_present": DELTA_ID in ids,
    }


def evaluate_amplitudes_gravity_bootstrap(root: Path) -> dict[str, Any]:
    failures: list[str] = []
    checks: list[dict[str, Any]] = []

    route_ledger = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json")
    forecast_ledger = load_json(root, "DISCRIMINATOR-FORECAST-LEDGER.json")
    delta_ledger = load_json(root, "EMPIRICAL-DELTA-LEDGER.json")
    decision_ledger = load_json(root, "DECISION-EXPERIMENT-LEDGER.json")
    evidence_ledger = load_json(root, "EVIDENCE-UNIT-LEDGER.json")

    route = find_row(route_ledger.get("route_rows", []), "route_id", ROUTE_ID)
    forecast = find_row(forecast_ledger.get("forecast_rows", []), "forecast_id", FORECAST_ID)
    delta = find_row(delta_ledger.get("empirical_deltas", []), "delta_id", DELTA_ID)
    decision = find_row(decision_ledger.get("decision_experiments", []), "experiment_id", DECISION_ID)
    evidence = find_row(evidence_ledger.get("evidence_units", []), "evidence_unit_id", EVIDENCE_ID)

    def add_check(label: str, passed: bool, detail: str) -> None:
        checks.append({"check": label, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{label}: {detail}")

    add_check("route-present", route is not None, f"route `{ROUTE_ID}` must exist")
    if route:
        add_check("route-current-state-capped", route.get("authority_state") == "S2", f"current authority is `{route.get('authority_state')}`; expected `S2`")
        add_check("route-promotion-ceiling-capped", route.get("promotion_ceiling") == "S2", f"promotion ceiling is `{route.get('promotion_ceiling')}`; expected `S2`")
        route_text = " ".join([route.get("stability_margin", ""), route.get("residual_cap", "")]).lower()
        missing_terms = [term for term in ["ir", "loop", "kinematic", "constraint"] if term not in route_text]
        add_check("route-names-gravity-ir-pressure", not missing_terms, f"route text missing terms {missing_terms}")

    add_check("forecast-present", forecast is not None, f"forecast `{FORECAST_ID}` must exist")
    if forecast:
        add_check("forecast-route-local", forecast.get("route_id") == ROUTE_ID, f"forecast route is `{forecast.get('route_id')}`")
        add_check("forecast-credit-capped", forecast.get("current_maximum_credit") == "S2", f"forecast current maximum is `{forecast.get('current_maximum_credit')}`; expected `S2`")
        missing = [ref for ref in REQUIRED_REFS if ref not in forecast.get("source_refs", [])]
        add_check("forecast-current-refs", not missing, f"missing refs {missing}; present {forecast.get('source_refs', [])}")
        warning = forecast.get("non_promotion_warning", "").lower()
        add_check("forecast-non-promotion", ("cannot" in warning or "not" in warning) and ("closure" in warning or "identity" in warning), "forecast must explicitly block closure/promotion spending")
        public_record = forecast.get("required_public_record", "").lower()
        required_terms = ["graviton", "loop", "ir", "light", "subtraction", "high-spin", "kinematic", "numerical"]
        missing_terms = [term for term in required_terms if term not in public_record]
        add_check("forecast-replay-denominators", not missing_terms, f"required_public_record missing terms {missing_terms}")

    add_check("delta-present", delta is not None, f"delta `{DELTA_ID}` must exist")
    if delta:
        add_check("delta-route-local", delta.get("route_ids") == [ROUTE_ID], f"delta route_ids are `{delta.get('route_ids')}`")
        add_check("delta-credit-capped", delta.get("promotion_ceiling") == "S2", f"delta promotion ceiling is `{delta.get('promotion_ceiling')}`; expected `S2`")
        missing = [ref for ref in REQUIRED_REFS if ref not in delta.get("source_refs", [])]
        add_check("delta-current-refs", not missing, f"missing refs {missing}; present {delta.get('source_refs', [])}")
        combined = " ".join([delta.get("record_delta", ""), delta.get("residual_cap", "")]).lower()
        required_terms = ["graviton", "loop", "ir", "light", "kinematic", "constraint"]
        missing_terms = [term for term in required_terms if term not in combined]
        add_check("delta-hard-denominators", not missing_terms, f"delta text missing terms {missing_terms}")

    add_check("decision-present", decision is not None, f"decision experiment `{DECISION_ID}` must exist")
    if decision:
        missing_refs = [ref for ref in REQUIRED_REFS if ref not in decision.get("source_refs", [])]
        add_check("decision-current-refs", not missing_refs, f"missing refs {missing_refs}; present {decision.get('source_refs', [])}")
        add_check("decision-hooks-delta", DELTA_ID in decision.get("empirical_delta_hooks", []), f"decision hooks {decision.get('empirical_delta_hooks', [])}")
        public_record = " ".join([decision.get("public_record", ""), decision.get("minimum_public_artifact", "")]).lower()
        required_terms = ["graviton", "loop", "ir", "kinematic", "stability", "competing-solution"]
        missing_terms = [term for term in required_terms if term not in public_record]
        add_check("decision-public-artifact-denominators", not missing_terms, f"decision artifact missing terms {missing_terms}")

    add_check("evidence-present", evidence is not None, f"evidence unit `{EVIDENCE_ID}` must exist")
    if evidence:
        present_forbidden = [ref for ref in REQUIRED_REFS if ref in evidence.get("source_refs", [])]
        add_check("fresh-refs-not-acquired-evidence", not present_forbidden, f"fresh refs incorrectly present on acquired evidence unit: {present_forbidden}")
        add_check("evidence-credit-capped", evidence.get("maximum_credit") == "S2", f"evidence maximum credit is `{evidence.get('maximum_credit')}`; expected `S2`")
        delta_ids = evidence.get("empirical_delta_ids", [])
        add_check("evidence-names-current-delta-handoff", DELTA_ID in delta_ids, f"evidence empirical_delta_ids should expose the route-local pressure handoff without carrying fresh refs: {delta_ids}")

    for (rel, collection, key, row_id), refs in CONDITION_REF_REQUIREMENTS.items():
        data = load_json(root, rel)
        row = find_row(data.get(collection, []), key, row_id)
        add_check(f"condition-row-present-{row_id}", row is not None, f"{rel}:{row_id}")
        if row is not None:
            missing = [ref for ref in refs if ref not in row.get("source_refs", [])]
            add_check(f"condition-row-refs-{row_id}", not missing, f"missing refs {missing}; present {row.get('source_refs', [])}")

    ns = empirical_delta_ordinal_status(root)
    add_check("empirical-delta-ordinal-stems-unique", not ns["duplicate_stems"], f"duplicate stems {ns['duplicate_stems']}")
    add_check("empirical-delta-ids-well-formed", not ns["bad_ids"], f"bad ids {ns['bad_ids']}")
    add_check("empirical-delta-ordinals-contiguous", not ns["missing_ordinals"], f"missing ordinals {ns['missing_ordinals']}")
    add_check("old-familyc-ordinal-absent", not ns["old_familyc_present"], f"old id present={ns['old_familyc_present']}")
    add_check("familyc-renumbered-present", ns["familyc_present"], f"expected id `{EXPECTED_FAMILYC_DELTA_ID}` present={ns['familyc_present']}")
    add_check("amplitudes-delta-present-in-namespace", ns["amplitudes_present"], f"expected id `{DELTA_ID}` present={ns['amplitudes_present']}")

    return {
        "audit_file": GENERATED_AUDIT,
        "route_id": ROUTE_ID,
        "forecast_id": FORECAST_ID,
        "delta_id": DELTA_ID,
        "decision_id": DECISION_ID,
        "evidence_id": EVIDENCE_ID,
        "required_refs": REQUIRED_REFS,
        "empirical_delta_namespace": ns,
        "checks": checks,
        "failures": failures,
    }


def write_amplitudes_gravity_bootstrap_audit(root: Path) -> None:
    result = evaluate_amplitudes_gravity_bootstrap(root)
    ns = result["empirical_delta_namespace"]
    lines = [
        "# Amplitudes/bootstrap gravity-IR positivity source-role audit (generated)",
        "",
        "Generated from the amplitudes/bootstrap route, forecast, decision, empirical-delta, evidence-unit, and route-control ledgers. Do not edit directly; run `make index` after changing these rows.",
        "",
        f"- Route checked: `{result['route_id']}`",
        f"- Required current refs: {refs_text(result['required_refs'])}",
        f"- Empirical-delta rows: `{ns['row_count']}`",
        f"- Duplicate empirical-delta ordinal stems: `{len(ns['duplicate_stems'])}`",
        f"- Missing empirical-delta ordinal stems: `{len(ns['missing_ordinals'])}`",
        f"- Gravity/IR positivity checks: `{len(result['checks'])}`",
        f"- Gravity/IR positivity failures: `{len(result['failures'])}`",
        "",
        "| Check | Passed | Detail |",
        "|---|---:|---|",
    ]
    for check in result["checks"]:
        detail = str(check["detail"]).replace("|", "\\|")
        lines.append(f"| `{check['check']}` | `{str(check['passed']).lower()}` | {detail} |")
    if result["failures"]:
        lines += ["", "## Failures", ""]
        for failure in result["failures"]:
            lines.append(f"- {failure}")
    lines += [
        "",
        "## Non-promotion rule",
        "",
        "Current gravitational S-matrix/bootstrap papers can strengthen only route-local constraint, IR/loop stability, and kinematic-domain pressure. They may be named by the acquired evidence unit only as an empirical-delta handoff handle; the fresh refs and source pressure remain route-local, and the route cannot move above S2 without an independent candidate-native bridge, observed-sector public record, and replayable gravity-specific stability controls.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_amplitudes_gravity_bootstrap_audit(root)
    outcome = evaluate_amplitudes_gravity_bootstrap(root)
    if outcome["failures"]:
        print("AMPLITUDES GRAVITY/IR POSITIVITY POLICY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("AMPLITUDES GRAVITY/IR POSITIVITY POLICY OK")
