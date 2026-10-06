import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACK = ROOT / "replay-capsule.json"
START = ROOT / "START_HERE.md"
AGENTS = ROOT / "AGENTS.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
README = ROOT / "README.md"
METHOD = ROOT / "docs/10-method/sufficiency-witnesses-replay-capsules-and-core-only-reentry-trials.md"
OVERVIEW = ROOT / "docs/10-method/method-overview.md"
CONTEXT = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
STATUS = json.loads((ROOT / "SURFACE-STATUS.json").read_text(encoding="utf-8"))
INNOVATION = json.loads((ROOT / "innovation-packet.json").read_text(encoding="utf-8"))
FRONTIER = json.loads((ROOT / "frontier-ticket.json").read_text(encoding="utf-8"))
BUNDLE = json.loads((ROOT / "compact-surface-bundle.json").read_text(encoding="utf-8"))

if not PACK.exists():
    raise SystemExit("replay-capsule.json missing")

payload = json.loads(PACK.read_text(encoding="utf-8"))
required = {
    "project",
    "revision",
    "surface",
    "derivative_note",
    "packet_sources",
    "candidate_reduced_packet",
    "bounded_sufficiency",
    "reinflate_route",
    "current_projection",
    "explicit_non_claim",
}
missing = sorted(required - set(payload))
if missing:
    raise SystemExit("replay-capsule missing keys: " + ", ".join(missing))
if payload["project"] != "DelayBasin":
    raise SystemExit("replay-capsule project mismatch")
if payload["surface"] != "replay-capsule.json":
    raise SystemExit("replay-capsule surface self-id drift")
if payload["revision"] != CONTEXT["revision"]:
    raise SystemExit("replay-capsule revision must match context-pack")
if payload["derivative_note"] != "Derivative bounded replay-capsule aid; canon wins.":
    raise SystemExit("replay-capsule derivative_note drift")

for rel in payload["packet_sources"]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"replay-capsule packet source missing: {rel}")

cand = payload["candidate_reduced_packet"]
expected_surfaces = [
    "START_HERE.md",
    "SURFACE-STATUS.json",
    "innovation-packet.json",
    "frontier-ticket.json",
    "compact-surface-bundle.json",
]
if cand.get("surfaces") != expected_surfaces:
    raise SystemExit("replay-capsule candidate_reduced_packet.surfaces drift")
for rel in expected_surfaces + cand.get("governing_underliers", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"replay-capsule candidate or underlier missing: {rel}")

bounded = payload["bounded_sufficiency"]
for key in [
    "core_only_replay_surface",
    "fixed_context_family",
    "withheld_context_family",
    "target_continuation_property",
    "tolerated_degradation",
    "sufficiency_state",
]:
    if key not in bounded:
        raise SystemExit(f"replay-capsule bounded_sufficiency missing {key}")
if bounded["core_only_replay_surface"] != "replay-capsule.json":
    raise SystemExit("replay-capsule core_only_replay_surface drift")
if bounded["sufficiency_state"] != "bounded-ordinary-reentry-only":
    raise SystemExit("replay-capsule sufficiency_state drift")

reinflate = payload["reinflate_route"]
for key in ["reinflate_triggers", "fallback_surfaces", "repair", "quarantine_consequence"]:
    if key not in reinflate:
        raise SystemExit(f"replay-capsule reinflate_route missing {key}")
for rel in reinflate["fallback_surfaces"]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"replay-capsule fallback surface missing: {rel}")

proj = payload["current_projection"]
if proj.get("citation_head") != STATUS["citation_head"]["surface"]:
    raise SystemExit("replay-capsule current_projection citation_head drift")
if proj.get("anchor_revision") != INNOVATION["anchor"]["previous_revision"]:
    raise SystemExit("replay-capsule current_projection anchor_revision drift")
if proj.get("selected_focus_id") != FRONTIER["primary_focus"]["id"]:
    raise SystemExit("replay-capsule current_projection selected_focus_id drift")
if proj.get("compact_family_surface") != BUNDLE["surface"]:
    raise SystemExit("replay-capsule current_projection compact_family_surface drift")

if "Not a proven minimal seed" not in payload["explicit_non_claim"] or "make lint" not in payload["explicit_non_claim"]:
    raise SystemExit("replay-capsule explicit_non_claim drift")

for path in [START, AGENTS, RUNBOOK, README, METHOD, OVERVIEW]:
    text = path.read_text(encoding="utf-8")
    if "replay-capsule.json" not in text:
        raise SystemExit(f"{path.relative_to(ROOT)} must mention replay-capsule.json")

if CONTEXT.get("replay_capsule", {}).get("surface") != "replay-capsule.json":
    raise SystemExit("context-pack missing replay_capsule projection")
state_surfaces = set(CONTEXT.get("typed_reentry", {}).get("state_surfaces", []))
if "replay-capsule.json" not in state_surfaces:
    raise SystemExit("context-pack typed_reentry missing replay-capsule.json")
if CONTEXT.get("commands", {}).get("replay_capsule") != "python3 tools/gen_replay_capsule.py":
    raise SystemExit("context-pack commands missing replay capsule generator")

members = [row.get("surface") for row in BUNDLE.get("members", [])]
if "replay-capsule.json" not in members:
    raise SystemExit("compact-surface-bundle missing replay-capsule member")

print("check_replay_capsule_contract: OK")
