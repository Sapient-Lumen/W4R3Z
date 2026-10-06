import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/action-lanes-primary-next-step-routing-and-discharge-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
VOCAB = ROOT / "WITNESS-VOCABULARY.json"
FILES = [
    ROOT / "FOLLOWTHROUGH-QUEUE.json",
    ROOT / "RETROSPECTIVE-QUEUE.json",
    ROOT / "ASSUMPTION-LEDGER.json",
    ROOT / "OBLIGATION-LEDGER.json",
    ROOT / "APPLICABILITY-LEDGER.json",
    ROOT / "FOREIGN-PRESSURE-LEDGER.json",
    ROOT / "DATACUBE-TRANSFER-LEDGER.json",
    ROOT / "RESOLUTION-LEDGER.json",
    ROOT / "FIREBREAK-LEDGER.json",
]

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG, RECEIPT, VOCAB, *FILES):
    if not path.exists():
        raise SystemExit(f"missing required action-lane surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Action lanes, primary next-step routing, and discharge budgets",
    "## Practice / observation",
    "## Pressure from neighboring datacubes",
    "## External pressure from adjacent queue and issue practice",
    "## Working synthesis",
    "## Action lane vs state token vs discharge prose vs broader code court",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "action lane / primary next-step class",
    "governed discharge surfaces / durable queues / ledgers",
    "comparability budget / how much surrounding prose can vary while the lane still stays comparable",
    "narrow-lane / extend-registry / fail-closed-on-drift consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("action-lane contract missing: " + ", ".join(missing))

if "OQ-0113" not in TRAJ.read_text(encoding="utf-8"):
    raise SystemExit("trajectory map missing OQ-0113 wiring")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0072" not in prompt_text or "action lane / primary next-step class" not in prompt_text:
    raise SystemExit("prompt pairs missing action-lane ratchet")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "action lane / primary next-step class / discharge-routing token" not in runbook:
    raise SystemExit("runbook missing action-lane guidance")
if "CL-0113" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0113")
if "INV-0111" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0111")
if "OQ-0113" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0113")
if "PP-0072" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0072")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
families = vocab.get("families", {})
if "action_lane" not in families:
    raise SystemExit("WITNESS-VOCABULARY missing action_lane family")
allowed = set(families["action_lane"].get("allowed", []))
required_tokens = {"promote","replace","retest","rereview","retire","narrow","keep-compact","validate","await-adjudication"}
if allowed != required_tokens:
    raise SystemExit("action_lane family allowed tokens drifted")
if receipt.get("vocabulary_witness", {}).get("witness_surface") != "WITNESS-VOCABULARY.json":
    raise SystemExit("receipt vocabulary_witness must still point to WITNESS-VOCABULARY.json")
if "action_lane" not in receipt.get("vocabulary_witness", {}).get("controlled_families", []):
    raise SystemExit("receipt vocabulary_witness missing action_lane family")

for path in FILES:
    rel = path.relative_to(ROOT).as_posix()
    obj = json.loads(path.read_text(encoding="utf-8"))
    for item in obj.get("items", []):
        if "discharge" in item:
            lane = item.get("action_lane")
            if lane not in allowed:
                raise SystemExit(f"{rel} item {item.get('id')} missing valid action_lane")
            if rel not in families["action_lane"].get("surfaces", []):
                raise SystemExit(f"action_lane family missing governed surface {rel}")

print("check_action_lane_contract: OK")
