import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
registry = (ROOT / "docs/20-constitution/open-question-registry.md").read_text(encoding="utf-8")
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
question_witness = receipt.get("question_posture_witness", {})
synced_resolved = set(question_witness.get("synced_resolved_questions", []))
frontier = receipt.get("next_open_question") or question_witness.get("next_open_question")

blocks = re.split(r"(?=^- `OQ-\d{4}`)", registry, flags=re.M)
missing = []
bad = []
seen = set()
for block in blocks:
    m = re.match(r"- `(OQ-\d{4})`", block)
    if not m:
        continue
    oq = m.group(1)
    seen.add(oq)
    postures = re.findall(r"^\s*- Current posture:\s*(.+)$", block, flags=re.M)
    if len(postures) != 1:
        missing.append(oq)
        continue
    posture = postures[0].strip()
    if not posture:
        bad.append(f"{oq} has empty current posture")
    # Older registry entries predate the modern resolved-by wording.  The
    # completeness contract is global; the stricter resolved-pointer contract is
    # limited to the synchronized current frontier/history declared in the
    # receipt so this check does not require retroactive prose rewrites.
    if oq in synced_resolved and ("resolved by" not in posture or "RS-" not in posture):
        bad.append(f"{oq} synchronized resolved question lacks resolved-by posture")
    if oq == frontier and "unresolved" not in posture:
        bad.append(f"{oq} current frontier lacks unresolved posture")

if frontier and frontier not in seen:
    bad.append(f"current frontier {frontier} missing from registry")
if missing:
    raise SystemExit("open-question entries without exactly one posture: " + ", ".join(missing))
if bad:
    raise SystemExit("open-question posture mismatch: " + "; ".join(bad[:20]))
print("check_open_question_registry_posture_completeness: OK")
