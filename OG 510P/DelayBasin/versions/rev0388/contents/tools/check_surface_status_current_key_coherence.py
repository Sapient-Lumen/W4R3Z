import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
status = json.loads((ROOT / "SURFACE-STATUS.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))

rev = manifest.get("revision")
prev = receipt.get("previous_revision")
bundle = manifest.get("bundle")
stamp = manifest.get("timestamp")
slug = manifest.get("slug")
created = receipt.get("created_at", "")
created_minute = created[:16]
expected_updated_prefix = created_minute

checks = {
    "revision": rev,
    "current_head": rev,
    "latest_revision": rev,
    "current_revision": rev,
    "latest_bundle": bundle,
    "current_bundle": bundle,
    "latest_archive": bundle,
    "frozen_public_surface": bundle,
    "current_release_surface": bundle,
    "stamp": stamp,
    "slug": slug,
    "resolved_question": receipt.get("resolved_question"),
    "next_open_question": receipt.get("next_open_question"),
}
for key, expected in checks.items():
    if status.get(key) != expected:
        raise SystemExit(f"SURFACE-STATUS.{key}={status.get(key)!r} expected {expected!r}")

if status.get("operational_head", {}).get("revision") != rev:
    raise SystemExit("SURFACE-STATUS operational_head.revision must match manifest revision")
if status.get("operational_head", {}).get("surface") != bundle:
    raise SystemExit("SURFACE-STATUS operational_head.surface must match manifest bundle")
if status.get("citation_head", {}).get("revision") != rev:
    raise SystemExit("SURFACE-STATUS citation_head.revision must match manifest revision")
if status.get("citation_head", {}).get("surface") != bundle:
    raise SystemExit("SURFACE-STATUS citation_head.surface must match manifest bundle")
if status.get("status_lanes", {}).get("current_release_surface") != bundle:
    raise SystemExit("SURFACE-STATUS status_lanes.current_release_surface must match manifest bundle")
if status.get("status_lanes", {}).get("frozen_public_surface") != bundle:
    raise SystemExit("SURFACE-STATUS status_lanes.frozen_public_surface must match manifest bundle")
if status.get("previous_revision") != prev:
    raise SystemExit("SURFACE-STATUS.previous_revision must match receipt.previous_revision")
if status.get("previous_citation_head", {}).get("revision") != prev:
    raise SystemExit("SURFACE-STATUS previous_citation_head.revision must match receipt.previous_revision")
if status.get("previous_citation_head", {}).get("surface") == bundle:
    raise SystemExit("SURFACE-STATUS previous_citation_head.surface must not equal current bundle")
if not str(status.get("updated_at", "")).startswith(expected_updated_prefix):
    raise SystemExit("SURFACE-STATUS.updated_at must match receipt created_at minute")
summary = status.get("operational_summary", "")
if rev not in summary or receipt.get("resolved_question") not in summary or receipt.get("next_open_question") not in summary:
    raise SystemExit("SURFACE-STATUS.operational_summary must name current rev, resolved question, and next question")

current_surfaces = set(status.get("current_surfaces", []))
for rel in receipt.get("canon_additions", []) + receipt.get("touched_surfaces", []):
    if rel in {"REVISION-RECEIPT.json", "CHANGELOG.md", "RELEASE-MANIFEST.json"}:
        continue
    if rel.startswith("tools/check_surface_status_current_key_coherence.py") or rel.startswith("docs/10-method/pa-governance-retirement-threshold-scope-retirement-history-portability-currentness"):
        if rel not in current_surfaces:
            raise SystemExit(f"SURFACE-STATUS.current_surfaces missing current rel: {rel}")

print("check_surface_status_current_key_coherence: OK")
