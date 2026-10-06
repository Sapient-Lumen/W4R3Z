import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]

resolution = json.loads((ROOT / "RESOLUTION-LEDGER.json").read_text(encoding="utf-8"))["items"]
registry_text = (ROOT / "docs/20-constitution/open-question-registry.md").read_text(encoding="utf-8")
trajectory_text = (ROOT / "docs/00-meta/trajectory-map.md").read_text(encoding="utf-8")
context = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
frontier = json.loads((ROOT / "frontier-ticket.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))

resolved = {}
for item in resolution:
    if item.get("closure_state") == "resolved":
        for oid in item.get("resolved_objects", []):
            if re.fullmatch(r"OQ-\d{4}", oid):
                resolved[oid] = item


def posture_line(text: str, oid: str):
    lines = text.splitlines()
    postures = []
    for idx, line in enumerate(lines):
        if line.startswith(f"- `{oid}` —"):
            for candidate in lines[idx + 1:idx + 6]:
                marker = "  - Current posture: "
                if candidate.startswith(marker):
                    postures.append(candidate[len(marker):].strip())
                    break
    return postures[-1] if postures else None

for oid in receipt["question_posture_witness"]["synced_resolved_questions"]:
    if oid not in resolved:
        raise SystemExit(f"question_posture_witness lists non-resolved OQ: {oid}")
    reg = posture_line(registry_text, oid)
    if reg is None:
        raise SystemExit(f"resolved question missing current posture in registry: {oid}")
    if "unresolved" in reg.lower() or "resolved by" not in reg.lower():
        raise SystemExit(f"registry posture drift for resolved {oid}: {reg}")
    succ = resolved[oid].get("successor_surface")
    if succ and succ not in reg:
        raise SystemExit(f"registry posture for {oid} must mention successor surface {succ}")
    traj = posture_line(trajectory_text, oid)
    if traj is not None:
        if "unresolved" in traj.lower() or "resolved by" not in traj.lower():
            raise SystemExit(f"trajectory posture drift for resolved {oid}: {traj}")
        if succ and succ not in traj:
            raise SystemExit(f"trajectory posture for {oid} must mention successor surface {succ}")

resolved_ids = set(resolved)
for item in context.get("open_questions", []):
    if item["id"] in resolved_ids:
        raise SystemExit(f"context-pack surfaced resolved open question: {item['id']}")
focus = frontier.get("primary_focus", {})
if focus.get("id") in resolved_ids:
    raise SystemExit(f"frontier-ticket surfaced resolved open question: {focus.get('id')}")

wit = receipt.get("question_posture_witness")
required = {"resolution_surface", "registry_surface", "trajectory_surface", "synced_resolved_questions", "frontier_selection_rule", "posture_state", "repair"}
if not isinstance(wit, dict):
    raise SystemExit("receipt question_posture_witness must be an object")
missing = required - wit.keys()
if missing:
    raise SystemExit("receipt question_posture_witness missing keys: " + ", ".join(sorted(missing)))
if wit["resolution_surface"] != "RESOLUTION-LEDGER.json":
    raise SystemExit("question_posture_witness.resolution_surface must be RESOLUTION-LEDGER.json")
if wit["registry_surface"] != "docs/20-constitution/open-question-registry.md":
    raise SystemExit("question_posture_witness.registry_surface must be docs/20-constitution/open-question-registry.md")
if wit["trajectory_surface"] != "docs/00-meta/trajectory-map.md":
    raise SystemExit("question_posture_witness.trajectory_surface must be docs/00-meta/trajectory-map.md")
if not isinstance(wit["synced_resolved_questions"], list) or not wit["synced_resolved_questions"]:
    raise SystemExit("question_posture_witness.synced_resolved_questions must be a non-empty list")
if len(set(wit["synced_resolved_questions"])) != len(wit["synced_resolved_questions"]):
    raise SystemExit("question_posture_witness.synced_resolved_questions must be unique")
if wit["posture_state"] != "resolved-sync-current":
    raise SystemExit("question_posture_witness.posture_state invalid")
if wit["repair"] != "ordinary-continuation":
    raise SystemExit("question_posture_witness.repair invalid")
print("check_open_question_posture_contract: OK")
