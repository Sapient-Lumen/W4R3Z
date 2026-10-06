import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/retrospective-writes-cooldown-windows-and-off-path-adjudication.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
QUEUE = ROOT / "RETROSPECTIVE-QUEUE.json"
CONTRACT = ROOT / "docs/20-constitution/revision-receipt-contract.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, RECEIPT, QUEUE, CONTRACT):
    if not path.exists():
        raise SystemExit(f"missing required retrospective-write surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Retrospective writes, cooldown windows, and off-path adjudication",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Retrospective write vs replay vs rehearsal vs reconsolidation",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "candidate write or provisional surface",
    "cooldown or defer window",
    "off-path adjudication family",
    "version or supersession link",
    "cooling state",
    "promotion / demotion / expire consequence",
    "RETROSPECTIVE-QUEUE.json",
    "retrospective_write_witness",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("retrospective-write contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0070" not in traj or "retrospective-write / cooldown-window / off-path-adjudication" not in traj:
    raise SystemExit("trajectory map missing retrospective-write wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0029" not in prompt_text or "cooldown or defer window" not in prompt_text or "current cooling state" not in prompt_text:
    raise SystemExit("prompt pairs missing retrospective-write ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "retrospective write" not in runbook or "RETROSPECTIVE-QUEUE.json" not in runbook:
    raise SystemExit("runbook missing retrospective-write guidance")

contract = CONTRACT.read_text(encoding="utf-8")
if "retrospective_write_witness" not in contract or "cooling-state classification" not in contract:
    raise SystemExit("revision receipt contract missing retrospective-write witness law")

queue = json.loads(QUEUE.read_text(encoding="utf-8"))
if queue.get("project") != "DelayBasin":
    raise SystemExit("RETROSPECTIVE-QUEUE project must be DelayBasin")
if not str(queue.get("revision", "")).startswith("rev"):
    raise SystemExit("RETROSPECTIVE-QUEUE revision missing rev####")
items = queue.get("items")
if not isinstance(items, list) or not items:
    raise SystemExit("RETROSPECTIVE-QUEUE items must be a non-empty list")
for item in items:
    if not isinstance(item, dict):
        raise SystemExit("RETROSPECTIVE-QUEUE entries must be objects")
    for key in ["id", "title", "state", "candidate_surface", "cooldown_window", "adjudication_family", "supersession_link", "origin_revision", "discharge"]:
        if key not in item:
            raise SystemExit(f"RETROSPECTIVE-QUEUE entry missing key: {key}")
    if item["state"] not in {"captured", "cooling", "promoted", "demoted", "expired", "quarantined"}:
        raise SystemExit("RETROSPECTIVE-QUEUE state invalid")
    for ref in [item["candidate_surface"], item["supersession_link"]]:
        base = ref.split('#', 1)[0]
        if base and not (ROOT / base).exists():
            raise SystemExit(f"RETROSPECTIVE-QUEUE referenced surface missing: {ref}")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
ret = receipt.get("retrospective_write_witness")
if not isinstance(ret, dict):
    raise SystemExit("receipt retrospective_write_witness must be an object")
for key in ["witness_surface", "candidate_surface", "cooldown_window", "adjudication_family", "supersession_link", "cooling_state", "disposition", "repair"]:
    if key not in ret:
        raise SystemExit(f"receipt retrospective_write_witness missing key: {key}")
for ref in [ret["witness_surface"], ret["candidate_surface"], ret["supersession_link"]]:
    base = ref.split('#', 1)[0]
    if base and not (ROOT / base).exists():
        raise SystemExit(f"receipt retrospective_write_witness referenced surface missing: {ref}")
if ret["cooling_state"] not in {"captured", "cooling", "promoted", "demoted", "expired", "quarantined"}:
    raise SystemExit("receipt retrospective_write_witness.cooling_state invalid")
if ret["disposition"] not in {"await-adjudication", "promote", "demote", "expire", "quarantine"}:
    raise SystemExit("receipt retrospective_write_witness.disposition invalid")
if ret["repair"] not in {"ordinary-continuation", "keep-cooling", "promote-now", "expire-candidate", "quarantine-or-retire", "recover-resync"}:
    raise SystemExit("receipt retrospective_write_witness.repair invalid")

print("check_retrospective_write_contract: OK")
