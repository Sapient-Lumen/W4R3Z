import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/applicability-witnesses-precondition-gates-and-negative-transfer-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"
CONTRACT = ROOT / "docs/20-constitution/revision-receipt-contract.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
LEDGER = ROOT / "APPLICABILITY-LEDGER.json"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG, CONTRACT, RECEIPT, LEDGER):
    if not path.exists():
        raise SystemExit(f"missing required applicability surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Applicability witnesses, precondition gates, and negative-transfer budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Applicability witness vs amortization witness vs feedback-policy witness vs consultation packet",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "state claim or target objective being stress-tested",
    "candidate carry object / reusable skill / memory / plan template",
    "applicability conditions / belief-state signature / domain-fit cue family",
    "compared no-reuse baseline / gated baseline / alternative carry baseline",
    "out-of-family stress slice / conflict case / neighboring non-fit family",
    "matched task budget / context budget / compute budget",
    "tolerated negative-transfer / misuse / conflict budget",
    "rollback / gate-closed / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("applicability contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0098" not in traj or "applicability witness" not in traj:
    raise SystemExit("trajectory map missing applicability wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0057" not in prompt_text or "negative-transfer budget" not in prompt_text or "applicability conditions / belief-state signature / domain-fit cue family" not in prompt_text:
    raise SystemExit("prompt pairs missing applicability ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "applicability witness / precondition gate / negative-transfer budget" not in runbook:
    raise SystemExit("runbook missing applicability guidance")

if "CL-0098" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0098")
if "INV-0096" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0096")
if "OQ-0098" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0098")
if "PP-0057" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0057")

print("check_applicability_witness_contract: OK")

if "applicability_witness" not in CONTRACT.read_text(encoding="utf-8"):
    raise SystemExit("revision receipt contract missing applicability_witness")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
app = receipt.get("applicability_witness")
if not isinstance(app, dict):
    raise SystemExit("receipt missing applicability_witness object")
if app.get("applicability_state") not in {"gated", "narrow-fit", "eligible", "negative-transfer", "quarantined", "retired"}:
    raise SystemExit("receipt applicability_witness has invalid state")
ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
if ledger.get("project") != "DelayBasin":
    raise SystemExit("APPLICABILITY-LEDGER project must be DelayBasin")
if ledger.get("revision") != receipt.get("revision"):
    raise SystemExit("APPLICABILITY-LEDGER revision must match receipt revision")
items = ledger.get("items")
if not isinstance(items, list) or not items:
    raise SystemExit("APPLICABILITY-LEDGER items must be a non-empty list")
seen = set()
items_by_id = {}
for item in items:
    for key in ["id", "title", "state", "target_objective", "carry_object", "applicability_conditions", "baselines", "non_fit_slice", "budget", "negative_transfer_budget", "origin_revision", "discharge"]:
        if key not in item:
            raise SystemExit(f"APPLICABILITY-LEDGER item missing key: {key}")
    if item["id"] in seen:
        raise SystemExit(f"APPLICABILITY-LEDGER duplicate id: {item['id']}")
    seen.add(item["id"])
    items_by_id[item["id"]] = item
    if item["state"] not in {"gated", "narrow-fit", "eligible", "negative-transfer", "quarantined", "retired"}:
        raise SystemExit(f"APPLICABILITY-LEDGER invalid state: {item['state']}")
    if not isinstance(item["applicability_conditions"], list) or not item["applicability_conditions"]:
        raise SystemExit(f"APPLICABILITY-LEDGER item {item['id']} applicability_conditions must be a non-empty list")
    if not isinstance(item["baselines"], list) or not item["baselines"]:
        raise SystemExit(f"APPLICABILITY-LEDGER item {item['id']} baselines must be a non-empty list")
ref = app.get("witness_surface", "")
ref_base, _, ref_frag = ref.partition('#')
if ref_base != "APPLICABILITY-LEDGER.json":
    raise SystemExit("receipt applicability_witness witness_surface must point to APPLICABILITY-LEDGER.json")
if not ref_frag or ref_frag not in items_by_id:
    raise SystemExit("receipt referenced ledger entry missing from APPLICABILITY-LEDGER.json")
if items_by_id[ref_frag]["origin_revision"] != receipt.get("revision"):
    raise SystemExit("receipt-referenced APPLICABILITY-LEDGER item must originate in the current revision")

