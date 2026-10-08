#!/usr/bin/env python3
"""Audit the active MA equity-disaggregation/beneficiary-experience bridge.

Rev0378 refactor: resolve the newest revisioned bridge instead of assuming a same-revision copy exists.
"""
from pathlib import Path
import json, sys, re
ROOT = Path(__file__).resolve().parents[1]
CASE = "social-security-medicare-claim-security-rev0318"
REQUIRED_FIELDS = {"dual_eligible_status", "lis_or_low_income_cost_sharing_status", "original_reason_for_entitlement", "race_ethnicity_code_or_method", "county_fips", "subgroup_denominator", "subgroup_denial_rate", "beneficiary_reported_access_problem", "care_coordination_or_getting_needed_care_score", "mmd_disparity_context_measure", "eho4all_or_hei_reward_active_flag", "cell_suppression_or_disclosure_limit", "beneficiary_restoration_status", "provider_payment_restoration_status"}
REQUIRED_SOURCES = {"S600", "S601", "S602", "S603", "S604"}
REQUIRED_PHRASES = ["No aggregate-subgroup pass", "No Star Rating pass", "No survey-only pass", "No HEI/EHO4All pass"]

def load(rel): return json.loads((ROOT/rel).read_text(encoding="utf-8"))
def resolve_bridge():
    candidates=sorted((ROOT/'cases').glob(f'{CASE}-ma-equity-disaggregation-beneficiary-experience-bridge-rev*.json'))
    if not candidates: return ROOT/'cases'/f'{CASE}-ma-equity-disaggregation-beneficiary-experience-bridge-rev0376.json'
    def key(p):
        m=re.search(r'rev(\d{4})', p.name)
        return int(m.group(1)) if m else -1
    return sorted(candidates, key=key)[-1]

def main():
    path=resolve_bridge(); errors=[]
    if not path.exists(): print(f"ERROR: missing {path.relative_to(ROOT)}"); return 1
    bridge=json.loads(path.read_text(encoding="utf-8"))
    if bridge.get("certification_status_after_rev0376") != "not_certified_current": errors.append("bridge must remain not_certified_current")
    missing=sorted(REQUIRED_FIELDS-set(bridge.get("required_subgroup_join_fields") or []))
    if missing: errors.append(f"missing required subgroup fields: {missing}")
    blob=json.dumps(bridge, sort_keys=True)
    for sid in REQUIRED_SOURCES:
        if sid not in blob: errors.append(f"missing source {sid}")
    for phrase in REQUIRED_PHRASES:
        if phrase not in blob: errors.append(f"missing false-pass phrase {phrase}")
    if len(bridge.get("false_pass_blocks") or []) < 8: errors.append("false_pass_blocks too short")
    v=load("cases/VERIFIED_CLAIM_EDGE_LEDGER.json"); ids={r.get("verified_claim_edge_id") for r in v.get("verified_claim_edges", [])}
    req={f"VCEDGE-rev0376-{i:04d}" for i in range(202,210)}
    if not req.issubset(ids): errors.append(f"missing rev0376 evidence ids: {sorted(req-ids)}")
    if errors:
        for e in errors: print("ERROR:", e)
        print(f"FAILED: {len(errors)} MA equity bridge issue(s)")
        return 1
    print("PASSED: MA equity-disaggregation/beneficiary-experience bridge audit")
    return 0
if __name__ == "__main__": sys.exit(main())

# rev0378 live-surface exposure: this earlier bridge audit remains part of the current MA audit chain under rev0378.

# Retained in the rev0379 live-surface contract as an upstream MA guardrail audit.

# current_release_anchor: rev0380 retains this upstream bridge audit as active; do not clone same-revision boilerplate.
