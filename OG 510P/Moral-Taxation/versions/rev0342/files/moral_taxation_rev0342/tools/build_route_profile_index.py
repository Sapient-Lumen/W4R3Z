#!/usr/bin/env python3
"""Build the checked runtime profile index used by answer emission.

The older answer layer joined the route graph, remedy profiles, policy-action
profiles, and actor-accountability profiles at runtime. This builder creates a
single generated narrow-waist index for runtime use while audits keep the source
surfaces authoritative and drift-free.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from typing import Any, Dict


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    receipt = load_json(root / "REVISION-RECEIPT.json") if (root / "REVISION-RECEIPT.json").exists() else {}
    generated_at = receipt.get("created_at_utc") or load_json(root / "cube-index.json").get("generated_at_utc")

    cube_path = root / "cube-index.json"
    remedy_path = root / "docs/00-meta/remedy-profiles.json"
    action_path = root / "docs/00-meta/policy-action-profiles.json"
    actor_path = root / "docs/00-meta/actor-accountability-profiles.json"
    out_path = root / "docs/00-meta/route-profile-index.json"

    cube = load_json(cube_path)
    remedies = {p["route_id"]: p for p in load_json(remedy_path).get("profiles", [])}
    actions = {p["route_id"]: p for p in load_json(action_path).get("profiles", [])}
    actors = {p["route_id"]: p for p in load_json(actor_path).get("profiles", [])}

    entries = []
    errors = []
    for route in cube.get("route_records", []):
        rid = route.get("id")
        remedy = remedies.get(rid)
        action = actions.get(rid)
        actor = actors.get(rid)
        if not remedy or not action or not actor:
            errors.append(f"route {rid} lacks remedy/action/actor profile")
            continue
        entries.append({
            "route_id": rid,
            "family": route.get("family"),
            "route_path": route.get("path"),
            "route_axes": route.get("axes", {}),
            "primary_sources": route.get("primary_sources", []),
            "source_currentness_refs": route.get("source_currentness_refs", []),
            "source_currentness_claims": route.get("source_currentness_claims", []),
            "remedy": remedy,
            "policy_action": action,
            "accountability": actor,
        })
    extra_remedies = sorted(set(remedies) - {r.get("id") for r in cube.get("route_records", [])})
    extra_actions = sorted(set(actions) - {r.get("id") for r in cube.get("route_records", [])})
    extra_actors = sorted(set(actors) - {r.get("id") for r in cube.get("route_records", [])})
    if extra_remedies or extra_actions or extra_actors:
        errors.append(f"orphan profiles remedy={extra_remedies[:5]} action={extra_actions[:5]} actor={extra_actors[:5]}")
    if errors:
        raise SystemExit("\n".join(errors))

    payload = {
        "kind": "route_profile_runtime_index",
        "schema_version": 1,
        "revision": version,
        "generated_at_utc": generated_at,
        "purpose": "Generated narrow-waist runtime index joining live route records to remedy, policy-action, and actor-accountability profiles for answer emission; source profile surfaces remain authoritative and drift-audited.",
        "cube_index_path": "cube-index.json",
        "input_paths": {
            "remedy_profiles": "docs/00-meta/remedy-profiles.json",
            "policy_action_profiles": "docs/00-meta/policy-action-profiles.json",
            "actor_accountability_profiles": "docs/00-meta/actor-accountability-profiles.json",
        },
        "input_hashes": {
            "cube_index": sha256(cube_path),
            "remedy_profiles": sha256(remedy_path),
            "policy_action_profiles": sha256(action_path),
            "actor_accountability_profiles": sha256(actor_path),
        },
        "entry_count": len(entries),
        "entries": entries,
    }
    out_path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
