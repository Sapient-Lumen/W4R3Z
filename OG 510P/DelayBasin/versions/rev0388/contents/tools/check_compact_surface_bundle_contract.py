import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SURFACE = ROOT / "compact-surface-bundle.json"
START = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
RUNBOOK = (ROOT / "docs/00-meta/llm-runbook.md").read_text(encoding="utf-8")
METHOD = (ROOT / "docs/10-method/compact-surface-bundles-closed-family-contracts-and-bundle-status.md").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
CONTEXT = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))

if not SURFACE.exists():
    raise SystemExit("compact-surface-bundle.json missing")

payload = json.loads(SURFACE.read_text(encoding="utf-8"))
expected_members = [
    "context-pack.json",
    "frontier-ticket.json",
    "innovation-packet.json",
    "replay-capsule.json",
    "VALIDATION-INDEX.json",
    "REENTRY-CONTRACT.json",
    "REENTRY-SURFACE-CONFORMANCE.json",
]

if payload.get("surface") != "compact-surface-bundle.json":
    raise SystemExit("compact surface bundle missing self surface field")
if payload.get("derivative_note") != "Derivative compact-surface family card; canon wins.":
    raise SystemExit("compact surface bundle derivative note drift")
if payload.get("bundle_status", {}).get("present_members") != expected_members:
    raise SystemExit("compact surface bundle present_members drift")
if payload.get("bundle_status", {}).get("member_count") != len(expected_members):
    raise SystemExit("compact surface bundle member_count drift")
if payload.get("bundle_status", {}).get("borrowed_members") != []:
    raise SystemExit("compact surface bundle borrowed_members must stay empty for now")
members = payload.get("members")
if [row.get("surface") for row in members] != expected_members:
    raise SystemExit("compact surface bundle member rows drift")
for row in members:
    if not row.get("role"):
        raise SystemExit(f"member missing role: {row}")
    if row.get("mode") not in {"generated", "authored"}:
        raise SystemExit(f"member mode drift: {row}")
    for underlier in row.get("governing_underliers", []):
        if not (ROOT / underlier).exists():
            raise SystemExit(f"missing compact-surface governing underlier: {underlier}")
    gen = row.get("generator")
    if row.get("mode") == "generated" and (not gen or not (ROOT / gen).exists()):
        raise SystemExit(f"generated member missing generator: {row['surface']}")
    if row.get("mode") == "authored" and gen is not None:
        raise SystemExit(f"authored member should not name generator: {row['surface']}")

for text, label in [
    (START, "START_HERE.md"),
    (AGENTS, "AGENTS.md"),
    (RUNBOOK, "llm-runbook.md"),
    (METHOD, "compact-surface-bundle method note"),
    (README, "README.md"),
]:
    if "compact-surface-bundle.json" not in text:
        raise SystemExit(f"{label} must mention compact-surface-bundle.json")

if CONTEXT.get("compact_surface_bundle", {}).get("surface") != "compact-surface-bundle.json":
    raise SystemExit("context-pack missing compact_surface_bundle projection")
if "compact-surface-bundle.json" not in CONTEXT.get("typed_reentry", {}).get("state_surfaces", []):
    raise SystemExit("context-pack typed_reentry missing compact-surface-bundle.json")
if CONTEXT.get("commands", {}).get("compact_surface_bundle") != "python3 tools/gen_compact_surface_bundle.py":
    raise SystemExit("context-pack commands missing compact surface bundle generator")

print("check_compact_surface_bundle_contract: OK")
