#!/usr/bin/env python3
"""Audit the generated route-profile runtime index.

This is a refactor guard: runtime answer emission may use the single profile
index, but the source of truth remains the route graph plus remedy,
policy-action, and actor-accountability profile surfaces. Any drift blocks the
release.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from typing import Any, Dict, List

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors: List[str] = []
version = (root / "VERSION").read_text(encoding="utf-8").strip()


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

cube = load_json(root / "cube-index.json")
schema_path = root / "docs/00-meta/route-profile-index-schema.json"
index_path = root / "docs/00-meta/route-profile-index.json"
if not schema_path.exists():
    errors.append("route-profile-index-schema.json is missing")
    schema = {}
else:
    schema = load_json(schema_path)
if not index_path.exists():
    errors.append("route-profile-index.json is missing; run tools/build_route_profile_index.py")
    index = {"entries": []}
else:
    index = load_json(index_path)

if schema.get("revision") != version:
    errors.append("route-profile-index-schema.json revision must match VERSION")
if index.get("revision") != version:
    errors.append("route-profile-index.json revision must match VERSION")
if index.get("kind") != "route_profile_runtime_index":
    errors.append("route-profile-index.json kind is stale")

paths = {
    "cube_index": root / "cube-index.json",
    "remedy_profiles": root / "docs/00-meta/remedy-profiles.json",
    "policy_action_profiles": root / "docs/00-meta/policy-action-profiles.json",
    "actor_accountability_profiles": root / "docs/00-meta/actor-accountability-profiles.json",
}
expected_hashes = {name: sha256(path) for name, path in paths.items()}
if index.get("input_hashes") != expected_hashes:
    errors.append("route-profile-index.json input_hashes are stale; rebuild the index")

remedies = {p["route_id"]: p for p in load_json(paths["remedy_profiles"]).get("profiles", [])}
actions = {p["route_id"]: p for p in load_json(paths["policy_action_profiles"]).get("profiles", [])}
actors = {p["route_id"]: p for p in load_json(paths["actor_accountability_profiles"]).get("profiles", [])}
route_by_id = {r["id"]: r for r in cube.get("route_records", [])}
entries = index.get("entries", [])
entry_by_id = {e.get("route_id"): e for e in entries}

if index.get("entry_count") != len(entries):
    errors.append("route-profile-index.json entry_count is stale")
if len(entries) != len(entry_by_id):
    errors.append("route-profile-index.json route_id entries must be unique")
if set(entry_by_id) != set(route_by_id):
    errors.append(
        "route-profile-index.json route ids drifted: "
        f"missing={sorted(set(route_by_id)-set(entry_by_id))[:8]} "
        f"extra={sorted(set(entry_by_id)-set(route_by_id))[:8]}"
    )

drift_count = 0
for rid, route in route_by_id.items():
    entry = entry_by_id.get(rid)
    if not entry:
        continue
    expected_route_fields = {
        "family": route.get("family"),
        "route_path": route.get("path"),
        "route_axes": route.get("axes", {}),
        "primary_sources": route.get("primary_sources", []),
        "source_currentness_refs": route.get("source_currentness_refs", []),
        "source_currentness_claims": route.get("source_currentness_claims", []),
    }
    for key, expected_value in expected_route_fields.items():
        if entry.get(key) != expected_value:
            drift_count += 1
            errors.append(f"route-profile-index route {rid} field {key} drifted")
    if entry.get("remedy") != remedies.get(rid):
        drift_count += 1
        errors.append(f"route-profile-index route {rid} remedy profile drifted")
    if entry.get("policy_action") != actions.get(rid):
        drift_count += 1
        errors.append(f"route-profile-index route {rid} policy-action profile drifted")
    if entry.get("accountability") != actors.get(rid):
        drift_count += 1
        errors.append(f"route-profile-index route {rid} actor-accountability profile drifted")

summary = cube.get("audit_summary", {})
expected_summary = {
    "route_profile_index_required": True,
    "route_profile_index_count": len(route_by_id),
    "route_profile_index_drift_count": drift_count,
}
for key, expected_value in expected_summary.items():
    if summary.get(key) != expected_value:
        errors.append(f"cube audit_summary {key} is stale")

if cube.get("route_profile_index_path") != "docs/00-meta/route-profile-index.json":
    errors.append("cube-index.json route_profile_index_path must point to route-profile-index.json")
if cube.get("route_profile_index_schema_path") != "docs/00-meta/route-profile-index-schema.json":
    errors.append("cube-index.json route_profile_index_schema_path must point to route-profile-index-schema.json")
report_rel = cube.get("route_profile_index_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json route_profile_index_audit_report_path must point to an existing report")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    for line in [
        f"Route profile index entries: {len(route_by_id)}",
        f"Route profile index drift: {drift_count}",
    ]:
        if line not in report:
            errors.append(f"route-profile-index audit report is stale; missing line: {line}")

answer_source = (root / "tools/answer_case.py").read_text(encoding="utf-8")
if "route-profile-index.json" not in answer_source:
    errors.append("answer_case.py should load route-profile-index.json")
for direct in ["remedy-profiles.json", "policy-action-profiles.json", "actor-accountability-profiles.json"]:
    if direct in answer_source:
        errors.append(f"answer_case.py should use the runtime profile index instead of directly reading {direct}")

if errors:
    raise SystemExit("\n".join(errors))
print("route profile index audit ok")
