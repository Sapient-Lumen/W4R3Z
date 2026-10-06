#!/usr/bin/env python3
"""Guardrail for the fuzz target-class and flake-aware promotion boundary."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))
def main() -> int:
    errors=[]
    fuzz_schema=load_json("spec/fuzz.receipt.schema.json")
    crash_schema=load_json("spec/crash.case.schema.json")
    if (fuzz_schema.get("properties") or {}).get("authority_semantics",{}).get("const")!="fuzzing-evidence-only":
        errors.append("spec/fuzz.receipt.schema.json authority_semantics must stay fuzzing-evidence-only")
    if (crash_schema.get("properties") or {}).get("authority_semantics",{}).get("const")!="crash-case-evidence-only":
        errors.append("spec/crash.case.schema.json authority_semantics must stay crash-case-evidence-only")
    target_classes=set((((fuzz_schema.get("properties") or {}).get("target") or {}).get("properties") or {}).get("target_class",{}).get("enum") or [])
    expected={"uapi","parser","importer","broker","driver","other"}
    if target_classes!=expected:
        errors.append(f"fuzz.receipt target_class enum mismatch: {sorted(target_classes)} != {sorted(expected)}")
    result_props=(((fuzz_schema.get("properties") or {}).get("result_summary") or {}).get("properties") or {})
    req=set((((fuzz_schema.get("properties") or {}).get("result_summary") or {}).get("required") or []))
    for field in ["status","exec_count","wallclock_seconds","new_crash_case_count","reproducible_crash_case_count","flake_suspect_count"]:
        if field not in req:
            errors.append(f"fuzz.receipt result_summary missing required field: {field}")
    if "coverage_percent" in result_props or "coverage_percent" in (fuzz_schema.get("properties") or {}):
        errors.append("fuzz.receipt must not grow a raw coverage_percent field")
    repro_status=set((((crash_schema.get("properties") or {}).get("reproducibility") or {}).get("properties") or {}).get("status",{}).get("enum") or [])
    if repro_status!={"stable","flaky","unreproduced"}:
        errors.append(f"crash.case reproducibility.status enum mismatch: {sorted(repro_status)}")
    fuzz_example=load_json("spec/examples/fuzz.receipt.json")
    rs=fuzz_example.get("result_summary") or {}
    if rs.get("reproducible_crash_case_count",0)>rs.get("new_crash_case_count",0):
        errors.append("fuzz.receipt example reproducible_crash_case_count cannot exceed new_crash_case_count")
    if "coverage_percent" in fuzz_example or "coverage_percent" in rs:
        errors.append("fuzz.receipt example must not use coverage_percent")
    if rs.get("status")=="completed-with-crash" and not rs.get("crash_case_digests"):
        errors.append("fuzz.receipt example with crashes must point at crash_case_digests")
    crash_example=load_json("spec/examples/crash.case.json")
    replay=crash_example.get("replay") or {}
    if replay.get("isolation")!="microvm" or replay.get("network")!="none" or replay.get("lifetime")!="disposable":
        errors.append("crash.case example replay posture must stay microvm + none + disposable")
    profiles=load_json("spec/examples/product.profiles.json").get("profiles") or {}
    expected_defaults={
        "fleet_host":"required-classes-uapi-parser-driver-zero-open-reproducible-cases-flake-triage",
        "workstation":"required-classes-importer-broker-parser-zero-open-reproducible-cases-flake-triage",
        "general_os":"required-shipped-host-and-importer-classes-advisory-elsewhere",
        "appliance_factory":"approved-target-set-zero-open-production-cases-retained-corpora",
    }
    for pid,exp in expected_defaults.items():
        actual=((profiles.get(pid) or {}).get("defaults") or {}).get("fuzzing")
        if actual!=exp:
            errors.append(f"product profile {pid} fuzzing default mismatch: {actual!r} != {exp!r}")
    doc_checks={
        "docs/274-continuous-fuzzing-farm.md":["coverage percentages are advisory","`fuzz.receipt`","`crash.case`","target classes"],
        "docs/275-root-cause-certificates-and-bisection.md":["flaky","`crash.case.reproducibility.status`"],
        "docs/499-fuzz-target-classes-and-flake-aware-promotion-gate-boundary.md":["coverage percentages are advisory","`fuzz.receipt` is evidence-only","`crash.case` is the canonical minimized replay artifact","Flake accounting is explicit"],
        "docs/266-open-questions-and-risk-register.md":["Continuous fuzzing + regression localization (signal vs noise) [DECIDED]","ADR-0089"],
        "docs/99-llm-runbook.md":["`fuzz.receipt` evidence-only","`crash.case`","coverage percentages advisory"],
        "docs/98-archive-hygiene.md":["`python3 tools/check_fuzz_contract.py`","fuzz target classes","coverage percentages advisory"],
    }
    for rel,needles in doc_checks.items():
        text=(ROOT/rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    print("Fuzz target-class contract: OK")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
