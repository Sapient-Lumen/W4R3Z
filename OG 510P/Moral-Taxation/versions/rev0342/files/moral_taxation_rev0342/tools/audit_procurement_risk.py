#!/usr/bin/env python3
import json, pathlib, sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors = []

cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
records = {rec.get("id"): rec for rec in cube.get("route_records", [])}
procurement_records = [rec for rec in cube.get("route_records", []) if rec.get("family") == "public_procurement_industrial_policy"]

if len(procurement_records) != 5:
    errors.append(f"public procurement family should have 5 route records, got {len(procurement_records)}")

total_bytes = 0
for rec in procurement_records:
    path = root / rec.get("path", "")
    if not path.exists():
        errors.append(f"procurement route points to missing file: {rec.get('path')}")
        continue
    total_bytes += path.stat().st_size

if total_bytes > 18000:
    errors.append(f"procurement route memos total {total_bytes} bytes; keep durable slack under 18000")

required_currentness = {
    "procurement_subsidy_industrial_policy_public_upside": {"S512", "S513", "S514"},
    "defense_security_procurement_secrecy_industrial_base": {"S610", "S611", "S612", "S613", "S673"},
}
for rid, refs in required_currentness.items():
    rec = records.get(rid)
    if not rec:
        errors.append(f"missing procurement currentness route: {rid}")
        continue
    primary = set(rec.get("primary_sources", []))
    currentness = set(rec.get("source_currentness_refs", []))
    claims = {c.get("source_id") for c in rec.get("source_currentness_claims", [])}
    missing_refs = sorted(refs - currentness)
    if missing_refs:
        errors.append(f"{rid} missing procurement currentness refs {missing_refs}")
    if not refs.issubset(primary):
        errors.append(f"{rid} currentness refs must also be primary sources")
    if not refs.issubset(claims):
        errors.append(f"{rid} currentness refs must each have a local claim")

# The defense route must keep the lifecycle-cost signal, not just acquisition-stage cost growth.
defense = records.get("defense_security_procurement_secrecy_industrial_base", {})
if "S673" not in defense.get("primary_sources", []):
    errors.append("defense procurement route must retain S673 lifecycle/sustainment cost source")
if "S673" not in defense.get("source_currentness_refs", []):
    errors.append("defense procurement route must currentness-track S673 lifecycle/sustainment cost source")

if errors:
    raise SystemExit("\n".join(errors))
print("procurement risk audit ok")
