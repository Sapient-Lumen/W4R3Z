import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/resolution-witnesses-closure-reasons-and-reopen-triggers.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"
CONTRACT = ROOT / "docs/20-constitution/revision-receipt-contract.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
LEDGER = ROOT / "RESOLUTION-LEDGER.json"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG, CONTRACT, RECEIPT, LEDGER):
    if not path.exists():
        raise SystemExit(f"missing required resolution surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Resolution witnesses, closure reasons, and reopen triggers",
    "## Practice / observation",
    "## Pressure from neighboring datacubes",
    "## External pressure from adjacent decision, deprecation, and issue-closure practice",
    "## Working synthesis",
    "## Resolution witness vs open question vs followthrough witness vs counterfactual shadow",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "closed object / exact target surfaces",
    "prior live state / what kind of object it was",
    "closure reason / what counted as enough to stop treating it as live",
    "successor surface or explicit absence",
    "reopen trigger / what future evidence would legitimately reactivate it",
    "closure state / resolved vs superseded vs retired vs deprecated vs rejected",
    "fail-closed repair / reopen-via-successor vs recover-closure-basis vs quarantine-or-retire vs hold vs recover-resync consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("resolution contract missing: " + ", ".join(missing))

if "OQ-0109" not in TRAJ.read_text(encoding="utf-8"):
    raise SystemExit("trajectory map missing OQ-0109 wiring")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0068" not in prompt_text or "closed object / exact target surfaces" not in prompt_text or "reopen trigger / what future evidence would legitimately reactivate it" not in prompt_text:
    raise SystemExit("prompt pairs missing resolution-witness ratchet")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "resolution witness" not in runbook or "closure reason" not in runbook:
    raise SystemExit("runbook missing resolution-witness guidance")
if "CL-0109" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0109")
if "INV-0107" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0107")
if "OQ-0109" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0109")
if "PP-0068" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0068")
if "resolution_witness" not in CONTRACT.read_text(encoding="utf-8"):
    raise SystemExit("revision receipt contract missing resolution_witness")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
resolution = receipt.get("resolution_witness")
if not isinstance(resolution, dict):
    raise SystemExit("receipt missing resolution_witness object")
if resolution.get("closure_state") != "resolved":
    raise SystemExit("shipped receipt must record resolved closure state for rev0103")
if resolution.get("repair") != "ordinary-continuation":
    raise SystemExit("shipped receipt must record ordinary-continuation resolution repair posture")

ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
if ledger.get("project") != "DelayBasin":
    raise SystemExit("RESOLUTION-LEDGER project must be DelayBasin")
if ledger.get("revision") != receipt.get("revision"):
    raise SystemExit("RESOLUTION-LEDGER revision must match receipt revision")
items = ledger.get("items")
if not isinstance(items, list) or not items:
    raise SystemExit("RESOLUTION-LEDGER items must be a non-empty list")
seen = set()
items_by_id = {}
for item in items:
    for key in ["id", "title", "state", "target_surfaces", "prior_state", "closure_reason", "successor_surface", "reopen_trigger", "origin_revision", "discharge"]:
        if key not in item:
            raise SystemExit(f"RESOLUTION-LEDGER item missing key: {key}")
    if item["id"] in seen:
        raise SystemExit(f"RESOLUTION-LEDGER duplicate id: {item['id']}")
    seen.add(item["id"])
    items_by_id[item["id"]] = item
    items_by_id[item["id"]] = item
    if item["state"] not in {"resolved", "superseded", "retired", "deprecated", "rejected"}:
        raise SystemExit(f"RESOLUTION-LEDGER invalid state: {item['state']}")
    if not isinstance(item["target_surfaces"], list) or not item["target_surfaces"]:
        raise SystemExit(f"RESOLUTION-LEDGER item {item['id']} target_surfaces must be a non-empty list")
    for rel in item["target_surfaces"]:
        base = rel.split('#', 1)[0]
        if base and not (ROOT / base).exists():
            raise SystemExit(f"RESOLUTION-LEDGER target surface missing: {rel}")
    base = item["successor_surface"].split('#', 1)[0]
    if base and not (ROOT / base).exists():
        raise SystemExit(f"RESOLUTION-LEDGER successor surface missing: {item['successor_surface']}")

surface = resolution.get("witness_surface", "")
base, _, frag = surface.partition('#')
if base != "RESOLUTION-LEDGER.json":
    raise SystemExit("receipt resolution_witness witness_surface must point to RESOLUTION-LEDGER.json")
if not frag or frag not in items_by_id:
    raise SystemExit("receipt resolution_witness must point to an existing RESOLUTION-LEDGER item")
if not isinstance(resolution.get("resolved_objects"), list) or not resolution["resolved_objects"]:
    raise SystemExit("receipt resolution_witness.resolved_objects must be a non-empty list")
reopen = resolution.get("reopen_triggers")
if not isinstance(reopen, list) or not reopen:
    raise SystemExit("receipt resolution_witness.reopen_triggers must be a non-empty list")

ref = resolution.get("witness_surface", "")
ref_base, _, ref_frag = ref.partition('#')
if ref_base != "RESOLUTION-LEDGER.json":
    raise SystemExit("receipt resolution_witness witness_surface must point to RESOLUTION-LEDGER.json")
if not ref_frag or ref_frag not in items_by_id:
    raise SystemExit("receipt referenced ledger entry missing from RESOLUTION-LEDGER.json")
if items_by_id[ref_frag]["origin_revision"] != receipt.get("revision"):
    raise SystemExit("receipt-referenced RESOLUTION-LEDGER item must originate in the current revision")

print("check_resolution_witness_contract: OK")
