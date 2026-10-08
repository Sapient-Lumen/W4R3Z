#!/usr/bin/env python3
"""Small fail-closed surface checker for the cube."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_json(path: str):
    with (ROOT / path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    public = load_json("PUBLIC_SURFACE.json")
    claim = load_json("CLAIM_SURFACE.json")
    release = load_json("RELEASE_POSTURE.json")
    lifecycle = load_json("LIFECYCLE_GATES.json")
    next_rev = load_json("NEXT_REVISION.json")

    for entry in public["entry_points"]:
        require((ROOT / entry["path"]).exists(), f"missing public entry path: {entry['path']}")

    expected_revision = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    expected_next = "rev" + str(int(expected_revision[3:]) + 1).zfill(4)
    require(public["revision"] == expected_revision, "public surface revision drift")
    require(release["state"] == "no_release", "release posture drifted away from no_release")
    require(not release["release_candidate_ready"], "release candidate flag must remain false")
    require(claim["explicit_nonclaims"], "nonclaims must not be empty")
    require(next_rev["current_revision"] == expected_revision, "current revision pointer drift")
    require(next_rev["next_revision"] == expected_next, "next revision pointer drift")
    require(lifecycle["current_stage"]["code"] == "substrate_dht_design_cube", "unexpected lifecycle stage")

    out = ROOT / "artifacts/process/surface_check_snapshot.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "schema": "i2p_dht_lab.surface_check_snapshot.v1",
        "status": "pass",
        "checked_entry_points": len(public["entry_points"]),
        "release_state": release["state"],
        "current_revision": next_rev["current_revision"],
        "next_revision": next_rev["next_revision"],
    }, indent=2) + "\n", encoding="utf-8")
    print(f"surface check pass: wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
