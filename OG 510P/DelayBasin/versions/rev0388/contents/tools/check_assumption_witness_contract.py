import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/assumption-witnesses-expiry-triggers-and-invalidation-cues.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"
CONTRACT = ROOT / "docs/20-constitution/revision-receipt-contract.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
LEDGER = ROOT / "ASSUMPTION-LEDGER.json"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG, CONTRACT, RECEIPT, LEDGER):
    if not path.exists():
        raise SystemExit(f"missing required assumption surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Assumption witnesses, expiry triggers, and invalidation cues",
    "## Practice / observation",
    "## Pressure from neighboring datacubes",
    "## External pressure from adjacent risk and assurance practice",
    "## Working synthesis",
    "## Assumption witness vs open question vs quarantine vs followthrough",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "assumption statement / live support condition",
    "scope / decision family / surface family where it is being spent",
    "supporting surfaces / current evidence family / local reason it is still tolerated",
    "invalidation or expiry triggers / what changes would stop it from holding",
    "assumption state / active vs discharged vs invalidated vs retired vs quarantined",
    "fail-closed repair / refresh-assumptions vs retest-and-shrink vs quarantine-or-retire vs hold vs recover-resync consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("assumption contract missing: " + ", ".join(missing))

if "OQ-0107" not in TRAJ.read_text(encoding="utf-8"):
    raise SystemExit("trajectory map missing OQ-0107 wiring")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0066" not in prompt_text or "assumption statement / live support condition" not in prompt_text or "invalidation or expiry triggers / what changes would stop it from holding" not in prompt_text:
    raise SystemExit("prompt pairs missing assumption-witness ratchet")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "assumption witness" not in runbook or "ASSUMPTION-LEDGER.json" not in runbook:
    raise SystemExit("runbook missing assumption-witness guidance")
if "CL-0107" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0107")
if "INV-0105" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0105")
if "OQ-0107" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0107")
if "PP-0066" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0066")
if "assumption_witness" not in CONTRACT.read_text(encoding="utf-8"):
    raise SystemExit("revision receipt contract missing assumption_witness")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
assumption = receipt.get("assumption_witness")
if not isinstance(assumption, dict):
    raise SystemExit("receipt missing assumption_witness object")
if assumption.get("assumption_state") not in {"active", "discharged", "invalidated", "retired", "quarantined"}:
    raise SystemExit("receipt assumption_witness has invalid state")
if assumption.get("assumption_state") != "active":
    raise SystemExit("shipped receipt must record active assumption state for rev0101")
ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
if ledger.get("project") != "DelayBasin":
    raise SystemExit("ASSUMPTION-LEDGER project must be DelayBasin")
if ledger.get("revision") != receipt.get("revision"):
    raise SystemExit("ASSUMPTION-LEDGER revision must match receipt revision")
items = ledger.get("items")
if not isinstance(items, list) or not items:
    raise SystemExit("ASSUMPTION-LEDGER items must be a non-empty list")
seen = set()
items_by_id = {}
for item in items:
    for key in ["id", "title", "state", "assumption", "scope", "supporting_surfaces", "invalidation_triggers", "origin_revision", "discharge"]:
        if key not in item:
            raise SystemExit(f"ASSUMPTION-LEDGER item missing key: {key}")
    if item["id"] in seen:
        raise SystemExit(f"ASSUMPTION-LEDGER duplicate id: {item['id']}")
    seen.add(item["id"])
    items_by_id[item["id"]] = item
    if item["state"] not in {"active", "discharged", "invalidated", "retired", "quarantined"}:
        raise SystemExit(f"ASSUMPTION-LEDGER invalid state: {item['state']}")
    if not isinstance(item["supporting_surfaces"], list) or not item["supporting_surfaces"]:
        raise SystemExit(f"ASSUMPTION-LEDGER item {item['id']} supporting_surfaces must be a non-empty list")
    for rel in item["supporting_surfaces"]:
        base = rel.split('#', 1)[0]
        if base and not (ROOT / base).exists():
            raise SystemExit(f"ASSUMPTION-LEDGER surface missing: {rel}")
    if not isinstance(item["invalidation_triggers"], list) or not item["invalidation_triggers"]:
        raise SystemExit(f"ASSUMPTION-LEDGER item {item['id']} invalidation_triggers must be a non-empty list")

supporting = assumption.get("supporting_surfaces", [])
if not isinstance(supporting, list) or not supporting:
    raise SystemExit("receipt assumption_witness.supporting_surfaces must be a non-empty list")
for rel in supporting:
    base = rel.split('#', 1)[0]
    if base and not (ROOT / base).exists():
        raise SystemExit(f"receipt assumption_witness supporting surface missing: {rel}")
ledger_base = assumption.get("assumption_surface", "").split('#', 1)[0]
if ledger_base != "ASSUMPTION-LEDGER.json":
    raise SystemExit("receipt assumption_witness assumption_surface must point to ASSUMPTION-LEDGER.json")

ref = assumption.get("assumption_surface", "")
ref_base, _, ref_frag = ref.partition('#')
if ref_base != "ASSUMPTION-LEDGER.json":
    raise SystemExit("receipt assumption_witness assumption_surface must point to ASSUMPTION-LEDGER.json")
if not ref_frag or ref_frag not in items_by_id:
    raise SystemExit("receipt referenced ledger entry missing from ASSUMPTION-LEDGER.json")
if items_by_id[ref_frag]["origin_revision"] != receipt.get("revision"):
    raise SystemExit("receipt-referenced ASSUMPTION-LEDGER item must originate in the current revision")

print("check_assumption_witness_contract: OK")
