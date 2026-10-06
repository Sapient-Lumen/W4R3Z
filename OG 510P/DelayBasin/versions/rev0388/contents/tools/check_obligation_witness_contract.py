import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/obligation-witnesses-discharge-paths-and-evidence-debt-cues.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"
CONTRACT = ROOT / "docs/20-constitution/revision-receipt-contract.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
LEDGER = ROOT / "OBLIGATION-LEDGER.json"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG, CONTRACT, RECEIPT, LEDGER):
    if not path.exists():
        raise SystemExit(f"missing required obligation surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Obligation witnesses, discharge paths, and evidence-debt cues",
    "## Practice / observation",
    "## Pressure from neighboring datacubes",
    "## External pressure from adjacent proof, assurance, and evidence-mapping practice",
    "## Working synthesis",
    "## Obligation witness vs assumption witness vs followthrough witness vs open question",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "target claim or surface / what is being asked to carry authority",
    "missing support / undecided evidence or proof still owed",
    "current support / why the move is tolerated for now",
    "discharge path / evidence artifact / future proof that would retire the debt",
    "obligation state / open vs staged vs satisfied vs waived vs retired",
    "fail-closed repair / narrow-claim vs hold-via-followthrough vs quarantine-or-retire vs refresh-support vs recover-resync consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("obligation contract missing: " + ", ".join(missing))

if "OQ-0110" not in TRAJ.read_text(encoding="utf-8"):
    raise SystemExit("trajectory map missing OQ-0110 wiring")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0069" not in prompt_text or "missing support / undecided evidence or proof still owed" not in prompt_text or "discharge path / evidence artifact / future proof that would retire the debt" not in prompt_text:
    raise SystemExit("prompt pairs missing obligation-witness ratchet")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "obligation witness" not in runbook or "OBLIGATION-LEDGER.json" not in runbook:
    raise SystemExit("runbook missing obligation-witness guidance")
if "CL-0110" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0110")
if "INV-0108" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0108")
if "OQ-0110" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0110")
if "PP-0069" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0069")
if "obligation_witness" not in CONTRACT.read_text(encoding="utf-8"):
    raise SystemExit("revision receipt contract missing obligation_witness")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
obligation = receipt.get("obligation_witness")
if not isinstance(obligation, dict):
    raise SystemExit("receipt missing obligation_witness object")
if obligation.get("obligation_state") not in {"open", "staged", "satisfied", "waived", "retired"}:
    raise SystemExit("receipt obligation_witness has invalid state")
if obligation.get("obligation_state") != "open":
    raise SystemExit("shipped receipt must record open obligation state for rev0106")
ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
if ledger.get("project") != "DelayBasin":
    raise SystemExit("OBLIGATION-LEDGER project must be DelayBasin")
if ledger.get("revision") != receipt.get("revision"):
    raise SystemExit("OBLIGATION-LEDGER revision must match receipt revision")
items = ledger.get("items")
if not isinstance(items, list) or not items:
    raise SystemExit("OBLIGATION-LEDGER items must be a non-empty list")
seen = set()
items_by_id = {}
for item in items:
    for key in ["id", "title", "state", "target_surfaces", "missing_support", "current_support", "discharge_path", "origin_revision", "discharge"]:
        if key not in item:
            raise SystemExit(f"OBLIGATION-LEDGER item missing key: {key}")
    if item["id"] in seen:
        raise SystemExit(f"OBLIGATION-LEDGER duplicate id: {item['id']}")
    seen.add(item["id"])
    items_by_id[item["id"]] = item
    if item["state"] not in {"open", "staged", "satisfied", "waived", "retired"}:
        raise SystemExit(f"OBLIGATION-LEDGER invalid state: {item['state']}")
    if not isinstance(item["target_surfaces"], list) or not item["target_surfaces"]:
        raise SystemExit(f"OBLIGATION-LEDGER item {item['id']} target_surfaces must be a non-empty list")
    for rel in item["target_surfaces"]:
        base = rel.split('#', 1)[0]
        if base and not (ROOT / base).exists():
            raise SystemExit(f"OBLIGATION-LEDGER target surface missing: {rel}")
    if not isinstance(item["current_support"], list) or not item["current_support"]:
        raise SystemExit(f"OBLIGATION-LEDGER item {item['id']} current_support must be a non-empty list")
    for rel in item["current_support"]:
        base = rel.split('#', 1)[0]
        if base and not (ROOT / base).exists():
            raise SystemExit(f"OBLIGATION-LEDGER current support surface missing: {rel}")

current_support = obligation.get("current_support", [])
if not isinstance(current_support, list) or not current_support:
    raise SystemExit("receipt obligation_witness.current_support must be a non-empty list")
for rel in current_support:
    base = rel.split('#', 1)[0]
    if base and not (ROOT / base).exists():
        raise SystemExit(f"receipt obligation_witness current support surface missing: {rel}")
if not isinstance(obligation.get("target_surfaces"), list) or not obligation["target_surfaces"]:
    raise SystemExit("receipt obligation_witness.target_surfaces must be a non-empty list")
for rel in obligation.get("target_surfaces", []):
    base = rel.split('#', 1)[0]
    if base and not (ROOT / base).exists():
        raise SystemExit(f"receipt obligation_witness target surface missing: {rel}")
ledger_base = obligation.get("witness_surface", "").split('#', 1)[0]
if ledger_base != "OBLIGATION-LEDGER.json":
    raise SystemExit("receipt obligation_witness witness_surface must point to OBLIGATION-LEDGER.json")

ref = obligation.get("witness_surface", "")
ref_base, _, ref_frag = ref.partition('#')
if ref_base != "OBLIGATION-LEDGER.json":
    raise SystemExit("receipt obligation_witness witness_surface must point to OBLIGATION-LEDGER.json")
if not ref_frag or ref_frag not in items_by_id:
    raise SystemExit("receipt referenced ledger entry missing from OBLIGATION-LEDGER.json")
if items_by_id[ref_frag]["origin_revision"] != receipt.get("revision"):
    raise SystemExit("receipt-referenced OBLIGATION-LEDGER item must originate in the current revision")

print("check_obligation_witness_contract: OK")
