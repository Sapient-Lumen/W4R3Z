import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/reasoning-firebreaks-scratchpad-quarantine-and-public-extract-packets.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CONTRACT = ROOT / "docs/20-constitution/revision-receipt-contract.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
LEDGER = ROOT / "FIREBREAK-LEDGER.json"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

for path in (DOC, RUNBOOK, CONTRACT, RECEIPT, LEDGER, CLAIMS, INVS, OQS, PPREG, PROMPTS):
    if not path.exists():
        raise SystemExit(f"missing required reasoning-firebreak witness surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Reasoning firebreaks, scratchpad quarantine, and public extract packets",
    "## Pressure from neighboring datacubes",
    "## Mechanism pressure from outside the archive",
    "## Working synthesis",
    "## Reasoning firebreak vs assistant-echo filter vs blind packet vs execution witness",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "judged task / decision / continuation property",
    "public extract / compact residue kept in canon",
    "trace or scratchpad surface withheld / thinned / quarantined",
    "allowed role",
    "exposure / reinclusion / escalation consequence",
    "FIREBREAK-LEDGER.json",
    "reasoning_firebreak_witness",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("reasoning-firebreak witness contract missing: " + ", ".join(missing))

if "CL-0052" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0052")
if "INV-0050" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0050")
if "OQ-0052" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0052")
if "PP-0011" not in PPREG.read_text(encoding="utf-8") or "PP-0011" not in PROMPTS.read_text(encoding="utf-8"):
    raise SystemExit("prompt-pair wiring missing PP-0011")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "FIREBREAK-LEDGER.json" not in runbook or "reasoning_firebreak_witness" not in runbook:
    raise SystemExit("runbook missing firebreak ledger / receipt guidance")
contract = CONTRACT.read_text(encoding="utf-8")
if "reasoning_firebreak_witness" not in contract or "public extract" not in contract:
    raise SystemExit("revision receipt contract missing reasoning_firebreak_witness law")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
firebreak = receipt.get("reasoning_firebreak_witness")
if not isinstance(firebreak, dict):
    raise SystemExit("receipt missing reasoning_firebreak_witness object")
for key in ["witness_surface", "judged_property", "public_extract", "withheld_trace_surface", "allowed_role", "exposure_rule", "trace_state", "repair"]:
    if key not in firebreak:
        raise SystemExit(f"receipt reasoning_firebreak_witness missing key: {key}")
if firebreak.get("trace_state") not in {"withheld", "monitoring-only", "debug-only", "exposed", "retired", "quarantined"}:
    raise SystemExit("receipt reasoning_firebreak_witness.trace_state invalid")
if firebreak.get("repair") not in {"ordinary-continuation", "keep-withheld", "thicken-public-extract", "expose-temporarily", "quarantine-or-retire", "recover-resync"}:
    raise SystemExit("receipt reasoning_firebreak_witness.repair invalid")
ref = firebreak.get("witness_surface", "")
ref_base, _, ref_frag = ref.partition('#')
if ref_base != "FIREBREAK-LEDGER.json":
    raise SystemExit("receipt reasoning_firebreak_witness.witness_surface must point to FIREBREAK-LEDGER.json")

ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
if ledger.get("project") != "DelayBasin":
    raise SystemExit("FIREBREAK-LEDGER project must be DelayBasin")
if ledger.get("revision") != receipt.get("revision"):
    raise SystemExit("FIREBREAK-LEDGER revision must match receipt revision")
items = ledger.get("items")
if not isinstance(items, list) or not items:
    raise SystemExit("FIREBREAK-LEDGER items must be a non-empty list")
seen = set()
items_by_id = {}
for item in items:
    for key in ["id", "title", "state", "judged_property", "public_extract", "withheld_trace_surface", "allowed_role", "exposure_rule", "origin_revision", "discharge"]:
        if key not in item:
            raise SystemExit(f"FIREBREAK-LEDGER item missing key: {key}")
    if item["id"] in seen:
        raise SystemExit(f"FIREBREAK-LEDGER duplicate id: {item['id']}")
    seen.add(item["id"]); items_by_id[item["id"]]=item
    if item["state"] not in {"withheld", "monitoring-only", "debug-only", "exposed", "retired", "quarantined"}:
        raise SystemExit(f"FIREBREAK-LEDGER invalid state: {item['state']}")

if not ref_frag or ref_frag not in items_by_id:
    raise SystemExit("receipt referenced firebreak entry missing from FIREBREAK-LEDGER.json")
if items_by_id[ref_frag]["origin_revision"] != receipt.get("revision"):
    raise SystemExit("receipt-referenced FIREBREAK-LEDGER item must originate in the current revision")

print("check_reasoning_firebreak_witness_contract: OK")
