#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV_NUM = int(REV.replace("rev", ""))


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

# Front-door-adjacent surfaces must not announce an older current trajectory.
fronts = ["README.md", "START_HERE.md", "docs/README.md", "docs/00-meta/trajectory-map.md"]
for rel in fronts:
    text = (ROOT / rel).read_text(encoding="utf-8")
    opening = text[:3000]
    if REV not in opening:
        raise SystemExit(f"{rel} opening does not name active revision {REV}")

traj_first = (ROOT / "docs/00-meta/trajectory-map.md").read_text(encoding="utf-8").splitlines()[0]
if REV not in traj_first:
    raise SystemExit("trajectory map first heading is stale")
if re.search(r"Current trajectory .*rev(0[0-9]{3})", traj_first):
    m = re.search(r"rev(0[0-9]{3})", traj_first)
    if m and int(m.group(1)) != REV_NUM:
        raise SystemExit(f"trajectory map heading points at stale rev{m.group(1)}")

status = load("SURFACE-STATUS.json")
receipt = load("REVISION-RECEIPT.json")
release = load("RELEASE-MANIFEST.json")
if status.get("revision") != REV:
    raise SystemExit("SURFACE-STATUS revision mismatch")
if receipt.get("revision") != REV:
    raise SystemExit("REVISION-RECEIPT revision mismatch")
if release.get("revision") != REV:
    raise SystemExit("RELEASE-MANIFEST revision mismatch")

# Active map summaries must identify the active revision, so copy-forward public summaries cannot silently survive.
for stem in [
    "schema-fixture-domain-registry",
    "canon-surface-catalog",
    "doctrine-dependency-map",
    "rights-domain-coverage-map",
    "research-tail-compaction-map",
]:
    rel = f"examples/{stem}-{REV}.json"
    data = load(rel)
    summary = data.get("public_summary", "")
    if REV not in summary:
        raise SystemExit(f"{rel} public_summary does not name {REV}")
    if f"{REV[:-4]}0204" in summary and REV != "rev0204":
        raise SystemExit(f"{rel} public_summary appears copied from rev0204")

# Generated current examples must carry current revision and non-stale created_at.
for rel in [
    f"examples/live-receipt-floor-computed-snapshot-{REV}.json",
    f"examples/artifact-import-invariant-report-{REV}.json",
]:
    data = load(rel)
    if data.get("revision") != REV:
        raise SystemExit(f"{rel} revision mismatch")
    if data.get("created_at") == "2026-06-13T14:43:00Z" and REV != "rev0205":
        raise SystemExit(f"{rel} copied rev0205 created_at")

print("audit_revision_surface_freshness: OK")
