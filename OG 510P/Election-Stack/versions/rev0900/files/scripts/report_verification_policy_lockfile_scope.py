#!/usr/bin/env python3
from pathlib import Path
import argparse, csv, json, hashlib, re
ROOT=Path(__file__).resolve().parents[1]
VERSION=(ROOT/"VERSION").read_text(encoding="utf-8").strip()
VERSION_NUM=VERSION.removeprefix("v").zfill(4)
POL=ROOT/f"artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev{VERSION_NUM}.json"
REC=ROOT/f"artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev{VERSION_NUM}.publication-receipt.json"
def sha(p): return "sha256:"+hashlib.sha256(p.read_bytes()).hexdigest()
def public_fingerprint_profile():
 text=(ROOT/"tools"/"public_fingerprint_report.py").read_text(encoding="utf-8")
 for line in text.splitlines():
  if line.startswith("REPORT_FORMAT_VERSION") and "=" in line:
   return line.split("=",1)[1].split("#",1)[0].strip().strip("\'\"")
 return "unknown"
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--csv",default=f"artifacts/reports/verification-policy-lockfile-scope-rev{VERSION_NUM}.csv"); ap.add_argument("--json",default=f"artifacts/reports/verification-policy-lockfile-scope-rev{VERSION_NUM}.json"); args=ap.parse_args()
 pol=json.loads(POL.read_text()); rec=json.loads(REC.read_text()); expected_profile=public_fingerprint_profile()
 pol_sha=sha(POL); rec_sha=sha(REC); sidecar=(POL.with_suffix(POL.suffix+".sha256")).read_text().split()[0]; rec_sidecar=(REC.with_suffix(REC.suffix+".sha256")).read_text().split()[0]
 selector=pol.get("packet_selector",{}) if isinstance(pol.get("packet_selector"),dict) else {}
 rec_selector=rec.get("packet_selector",{}) if isinstance(rec.get("packet_selector"),dict) else {}
 rows=[
  {"check_id":"VPL-001","check":"policy_sidecar_matches","status":"PASS" if sidecar==pol_sha else "FAIL","observed":sidecar,"expected":pol_sha},
  {"check_id":"VPL-002","check":"receipt_sidecar_matches","status":"PASS" if rec_sidecar==rec_sha else "FAIL","observed":rec_sidecar,"expected":rec_sha},
  {"check_id":"VPL-003","check":"policy_receipt_digest_matches_policy","status":"PASS" if rec.get("verification_policy_lockfile_sha256")==pol_sha else "FAIL","observed":str(rec.get("verification_policy_lockfile_sha256") or ""),"expected":pol_sha},
  {"check_id":"VPL-004","check":"receipt_selector_matches_policy_selector","status":"PASS" if rec_selector==selector else "FAIL","observed":json.dumps(rec_selector,sort_keys=True),"expected":json.dumps(selector,sort_keys=True)},
  {"check_id":"VPL-005","check":"receipt_packet_public_fingerprint_matches_policy","status":"PASS" if rec.get("packet_public_fingerprint_sha256")==pol.get("packet_public_fingerprint_sha256") else "FAIL","observed":str(rec.get("packet_public_fingerprint_sha256") or ""),"expected":str(pol.get("packet_public_fingerprint_sha256") or "")},
  {"check_id":"VPL-006","check":"policy_packet_public_fingerprint_profile_declared","status":"PASS" if pol.get("packet_public_fingerprint_profile")==expected_profile else "FAIL","observed":str(pol.get("packet_public_fingerprint_profile") or ""),"expected":expected_profile},
  {"check_id":"VPL-007","check":"receipt_packet_public_fingerprint_profile_matches_policy","status":"PASS" if rec.get("packet_public_fingerprint_profile")==pol.get("packet_public_fingerprint_profile") else "FAIL","observed":str(rec.get("packet_public_fingerprint_profile") or ""),"expected":str(pol.get("packet_public_fingerprint_profile") or "")},
 ]
 failure_count=sum(1 for r in rows if r["status"]!="PASS")
 summary={"archive_version":VERSION,"policy_path":str(POL.relative_to(ROOT)),"receipt_path":str(REC.relative_to(ROOT)),"policy_id":pol.get("policy_id"),"policy_sha256":pol_sha,"receipt_sha256":rec_sha,"packet_selector":selector,"packet_public_fingerprint_sha256":pol.get("packet_public_fingerprint_sha256"),"packet_public_fingerprint_profile":pol.get("packet_public_fingerprint_profile"),"failure_count":failure_count,"non_claims":["synthetic_policy_scope_audit_only","not_production_publication_governance","not_live_pilot_authorization"]}
 cp=ROOT/args.csv; cp.parent.mkdir(parents=True,exist_ok=True)
 with cp.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=["check_id","check","status","observed","expected"]); w.writeheader(); w.writerows(rows)
 (ROOT/args.json).write_text(json.dumps({"summary":summary,"checks":rows},indent=2,sort_keys=True)+"\n",encoding="utf-8")
 print(f"policy_lockfile_failure_count={failure_count} sidecar_matches={sidecar==pol_sha and rec_sidecar==rec_sha}")
 return 0 if failure_count==0 else 2
if __name__=="__main__": raise SystemExit(main())
