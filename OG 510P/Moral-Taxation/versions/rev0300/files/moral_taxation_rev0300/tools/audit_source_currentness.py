#!/usr/bin/env python3
import json, pathlib, sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors = []

cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
sources = json.loads((root / "SOURCES.json").read_text(encoding="utf-8")).get("sources", [])
source_ids = {s["id"] for s in sources}
registry = json.loads((root / "docs/00-meta/source-currentness-registry.json").read_text(encoding="utf-8"))
registry_ids = {e["source_id"] for e in registry.get("entries", [])}
used_registry_ids = set()

allowed_s15_records = {
    "data_center_local_burden",
    "frontier_ai_host_market_controller_jurisdiction",
    "frontier_scarce_capacity_threshold",
}

for rec in cube.get("route_records", []):
    rid = rec.get("id", "")
    primary = set(rec.get("primary_sources", []))
    refs = rec.get("source_currentness_refs", [])
    claims = rec.get("source_currentness_claims", [])
    claim_ids = [c.get("source_id") for c in claims]

    if len(refs) != len(set(refs)):
        errors.append(f"{rid} has duplicate source_currentness_refs")
    if set(refs) != set(claim_ids):
        errors.append(f"{rid} source_currentness_refs must match source_currentness_claims ids refs={refs} claims={claim_ids}")
    if len(claim_ids) != len(set(claim_ids)):
        errors.append(f"{rid} has duplicate source_currentness_claims ids")
    for claim in claims:
        sid = claim.get("source_id")
        if not claim.get("current_claim") or not claim.get("review_reason"):
            errors.append(f"{rid} currentness claim for {sid} must include current_claim and review_reason")
    for sid in refs:
        used_registry_ids.add(sid)
        if sid not in source_ids:
            errors.append(f"{rid} source_currentness_ref {sid} missing from SOURCES.json")
        if sid not in registry_ids:
            errors.append(f"{rid} source_currentness_ref {sid} missing from source-currentness registry")
        if sid not in primary:
            errors.append(f"{rid} source_currentness_ref {sid} must also be in primary_sources")
        if sid == "S15" and rid not in allowed_s15_records:
            errors.append(f"{rid} uses S15 as a currentness ref outside the AI/data-center scope")

dangling = sorted(registry_ids - used_registry_ids, key=lambda s: int(s[1:]) if s[1:].isdigit() else 10**9)
if dangling:
    errors.append(f"source-currentness registry entries are not referenced by any route: {dangling}")

summary = cube.get("audit_summary", {})
expected_records = sum(1 for rec in cube.get("route_records", []) if rec.get("source_currentness_refs"))
expected_refs = sum(len(rec.get("source_currentness_refs", [])) for rec in cube.get("route_records", []))
if summary.get("source_currentness_record_count") != expected_records:
    errors.append("cube audit_summary source_currentness_record_count is stale")
if summary.get("source_currentness_ref_count") != expected_refs:
    errors.append("cube audit_summary source_currentness_ref_count is stale")
if summary.get("s15_currentness_records") != sorted(allowed_s15_records):
    errors.append("cube audit_summary s15_currentness_records must match the allowed post-repair set")

if errors:
    raise SystemExit("\n".join(errors))
print("source currentness audit ok")
