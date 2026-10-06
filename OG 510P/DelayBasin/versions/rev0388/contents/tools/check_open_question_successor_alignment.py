import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
resolution_items = json.loads((ROOT / "RESOLUTION-LEDGER.json").read_text(encoding="utf-8"))["items"]
registry = (ROOT / "docs/20-constitution/open-question-registry.md").read_text(encoding="utf-8")
trajectory = (ROOT / "docs/00-meta/trajectory-map.md").read_text(encoding="utf-8")
context = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
frontier = json.loads((ROOT / "frontier-ticket.json").read_text(encoding="utf-8"))

resolved = receipt.get("resolved_question")
next_q = receipt.get("next_open_question")
res_w = receipt.get("resolution_witness", {})
if not re.fullmatch(r"OQ-\d{4}", str(resolved)) or not re.fullmatch(r"OQ-\d{4}", str(next_q)):
    raise SystemExit("receipt resolved_question and next_open_question must be OQ ids")
if resolved == next_q:
    raise SystemExit("resolved question and successor question must differ")

surface = res_w.get("witness_surface", "")
base, _, frag = surface.partition('#')
if base != "RESOLUTION-LEDGER.json" or not frag:
    raise SystemExit("receipt resolution_witness must point to a resolution-ledger item")
item = next((row for row in resolution_items if row.get("id") == frag), None)
if item is None:
    raise SystemExit(f"resolution ledger missing {frag}")
if resolved not in item.get("resolved_objects", []):
    raise SystemExit(f"resolution item {frag} does not resolve {resolved}")
expected_successor = f"docs/20-constitution/open-question-registry.md#{next_q}"
if item.get("successor_surface") != expected_successor or res_w.get("successor_surface") != expected_successor:
    raise SystemExit("resolution successor surface must match receipt.next_open_question")

for label, text in [("registry", registry), ("trajectory", trajectory)]:
    if f"`{resolved}`" not in text:
        raise SystemExit(f"{label} missing resolved OQ {resolved}")
    if f"`{next_q}`" not in text:
        raise SystemExit(f"{label} missing successor OQ {next_q}")
    lines = text.splitlines()
    postures = []
    for idx, line in enumerate(lines):
        if line.startswith(f"- `{resolved}` —"):
            for candidate in lines[idx + 1:idx + 6]:
                marker = "  - Current posture: "
                if candidate.startswith(marker):
                    postures.append(candidate[len(marker):])
                    break
    if not postures:
        raise SystemExit(f"{label} missing current posture for {resolved}")
    posture = postures[-1]
    if frag not in posture or expected_successor not in posture:
        raise SystemExit(f"{label} posture for {resolved} must mention {frag} and {expected_successor}")

ctx = context.get("open_questions", [])[-1]
ft = frontier.get("primary_focus", {})
for label, focus in [("context-pack", ctx), ("frontier-ticket", ft)]:
    if focus.get("id") != next_q:
        raise SystemExit(f"{label} must surface successor {next_q}")
    if focus.get("id") == resolved:
        raise SystemExit(f"{label} still surfaces resolved {resolved}")
print("check_open_question_successor_alignment: OK")
