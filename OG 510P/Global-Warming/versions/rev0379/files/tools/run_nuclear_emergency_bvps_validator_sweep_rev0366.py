#!/usr/bin/env python3
from __future__ import annotations
import csv, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TOOLS=['tools/validate_nuclear_emergency_bvps_evidence_gate_rev0364.py', 'tools/validate_nuclear_emergency_bvps_inert_fixture_policy_rev0364.py', 'tools/validate_nuclear_emergency_bvps_source_cluster_weighting_rev0364.py', 'tools/validate_nuclear_emergency_bvps_evidence_intake_contract_rev0365.py', 'tools/validate_nuclear_emergency_bvps_no_readiness_overclaim_rev0365.py', 'tools/validate_nuclear_emergency_bvps_proofcut_status_rev0366.py', 'tools/validate_bvps_exact_duplicate_aliases_rev0366.py', 'tools/validate_nuclear_emergency_bvps_package_overclaim_scanner_rev0366.py', 'tools/validate_bvps_active_hotpath_manifest_rev0366.py', 'tools/validate_bvps_fieldkit_pointer_manifest_rev0366.py', 'tools/validate_validation_report_status_vocabulary_rev0366.py']
rows=[]; failures=[]
for i,rel in enumerate(TOOLS,1):
    start=time.time(); proc=subprocess.run([sys.executable, str(ROOT/rel)], cwd=ROOT, text=True, capture_output=True, timeout=90)
    out=(proc.stdout or "").strip(); err=(proc.stderr or "").strip(); status="executed_pass" if proc.returncode==0 else "executed_fail"
    print(f"{rel}: exit={proc.returncode} {out.splitlines()[-1] if out else ''}")
    rows.append({"validator_id":f"VS-0366-{i:03d}","tool_path":rel,"status":status,"seconds":str(round(time.time()-start,3)),"stdout_tail":out[-500:],"stderr_tail":err[-500:]})
    if proc.returncode!=0: failures.append(rel)
out_path=ROOT/"cube/bvps-current-risk-validator-audit-rev0366.csv"
with out_path.open("w", newline="", encoding="utf-8") as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
if failures:
    print("FAIL validator_sweep failures="+",".join(failures)); sys.exit(1)
print("PASS validator_sweep executed_passes="+str(len(TOOLS)))
