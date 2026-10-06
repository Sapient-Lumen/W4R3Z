import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
GATE_REL = "assays/priority-zero-burden-gate-2026-06-15.json"
SMOKE_REL = "assays/priority-zero-smoke-slice-2026-06-15.json"

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

if not (ROOT / GATE_REL).exists():
    raise SystemExit("missing Priority-0 burden-gate fixture")

gate = load(GATE_REL)
smoke = load(SMOKE_REL)
self_suff = load("SELF-SUFFICIENCY-LEDGER.json")

if gate.get("revision") != "rev0362":
    raise SystemExit("burden-gate fixture must remain anchored to rev0362")
if gate.get("resolved_question") != "OQ-0253" or gate.get("next_open_question") != "OQ-0254":
    raise SystemExit("burden-gate historical question posture drifted")
if gate.get("surface") != GATE_REL:
    raise SystemExit("burden-gate fixture surface drifted")
if gate.get("method_surface") != "docs/40-session/priority-zero-burden-gate-audit-2026-06-15.md":
    raise SystemExit("burden-gate method surface drifted")
if gate.get("checker_surface") != "tools/check_priority_zero_burden_gate_contract.py":
    raise SystemExit("burden-gate checker surface drifted")
if gate.get("based_on_assay") != SMOKE_REL or gate.get("source_scorecard") != smoke.get("scorecard"):
    raise SystemExit("burden-gate source smoke scorecard drifted")
for token in ["not deletion authority", "not a review court", "not a minimality proof"]:
    if token not in gate.get("non_claim", ""):
        raise SystemExit(f"burden-gate non_claim missing {token}")
hot = gate.get("hot_cue_gate", {})
if hot.get("before_current_additions_count", 0) < 40 or hot.get("after_current_additions_count") != 18:
    raise SystemExit("burden-gate must preserve the recorded 48-to-18 hot cue compaction")
if not hot.get("implemented"):
    raise SystemExit("hot cue gate must be recorded as implemented")
ids = {row.get("id"): row for row in gate.get("decisions", [])}
expected_states = {"BG-0001": "implemented", "BG-0002": "gated", "BG-0003": "blocked", "BG-0004": "queued"}
for did, state in expected_states.items():
    if ids.get(did, {}).get("state") != state:
        raise SystemExit(f"burden-gate decision {did} must have state {state}")
if len(ids["BG-0002"].get("triggers", [])) < 4:
    raise SystemExit("full-archive gate must name concrete reopening/escalation triggers")
if "deletion-authority" not in ids["BG-0003"].get("blocked_non_takes", []):
    raise SystemExit("deletion authority must remain blocked")
if ids["BG-0004"].get("successor_open_question") != "OQ-0254":
    raise SystemExit("burden-gate rotated-slice successor drifted")
rows = [row for row in self_suff.get("items", []) if row.get("assay_fixture") == GATE_REL]
if len(rows) != 1:
    raise SystemExit("self-sufficiency ledger must contain exactly one burden-gate fixture row")
row = rows[0]
if row.get("id") != "SA-0049" or row.get("revision") != "rev0362" or row.get("frontier_id") != "OQ-0254":
    raise SystemExit("burden-gate ledger row identity drifted")
if row.get("scorecard", {}).get("state") != "scored-canary":
    raise SystemExit("burden-gate historical ledger row must remain scored")
for required in ["hot-cue-regrows-to-touched-surfaces", "deletion-authority-claimed", "rotated-slice-successor-omitted", "smoke-fixture-treated-as-current-tail-only"]:
    if required not in gate.get("negative_canaries", []):
        raise SystemExit(f"burden-gate fixture missing negative canary {required}")
print("check_priority_zero_burden_gate_contract: OK")
