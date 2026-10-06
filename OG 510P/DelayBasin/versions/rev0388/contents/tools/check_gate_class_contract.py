import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/gate-classes-future-trigger-kinds-and-bounded-reopen-rules.md"
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
    ROOT / "ASSUMPTION-LEDGER.json",
    ROOT / "OBLIGATION-LEDGER.json",
    ROOT / "APPLICABILITY-LEDGER.json",
    ROOT / "FOREIGN-PRESSURE-LEDGER.json",
    ROOT / "RESOLUTION-LEDGER.json",
    ROOT / "RETROSPECTIVE-QUEUE.json",
    ROOT / "DATACUBE-TRANSFER-LEDGER.json",
    ROOT / "FIREBREAK-LEDGER.json",
]

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG, RECEIPT, VOCAB, *FILES):
    if not path.exists():
        raise SystemExit(f"missing required gate-class surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Gate classes, future-trigger kinds, and bounded reopen rules",
    "## Practice / observation",
    "## Pressure from neighboring datacubes",
    "## External pressure from adjacent workflow and issue practice",
    "## Working synthesis",
    "## Gate class vs state token vs action lane vs discharge prose vs broader code court",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "gate class / future-trigger kind",
    "governed discharge-bearing durable queues / ledgers",
    "comparability budget / how much surrounding prose can vary while the trigger class still stays comparable",
    "narrow-family / extend-registry / fail-closed-on-drift consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("gate-class contract missing: " + ", ".join(missing))

if "OQ-0115" not in TRAJ.read_text(encoding="utf-8"):
    raise SystemExit("trajectory map missing OQ-0115 wiring")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0074" not in prompt_text or "gate class / future-trigger kind" not in prompt_text:
    raise SystemExit("prompt pairs missing gate-class ratchet")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "gate class / future-trigger kind" not in runbook:
    raise SystemExit("runbook missing gate-class guidance")
if "CL-0115" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0115")
if "INV-0113" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0113")
if "OQ-0115" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0115")
if "PP-0074" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0074")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
families = vocab.get("families", {})
if "gate_class" not in families:
    raise SystemExit("WITNESS-VOCABULARY missing gate_class family")
allowed = set(families["gate_class"].get("allowed", []))
required_tokens = {"concrete-evidence", "repeat-pass", "scheduled-window", "overflow", "negative-transfer"}
if allowed != required_tokens:
    raise SystemExit("gate_class family allowed tokens drifted")
if receipt.get("vocabulary_witness", {}).get("witness_surface") != "WITNESS-VOCABULARY.json":
    raise SystemExit("receipt vocabulary_witness must still point to WITNESS-VOCABULARY.json")
if "gate_class" not in receipt.get("vocabulary_witness", {}).get("controlled_families", []):
    raise SystemExit("receipt vocabulary_witness missing gate_class family")

for path in FILES:
    rel = path.relative_to(ROOT).as_posix()
    obj = json.loads(path.read_text(encoding="utf-8"))
    if rel not in families["gate_class"].get("surfaces", []):
        raise SystemExit(f"gate_class family missing governed surface {rel}")
    for item in obj.get("items", []):
        gate = item.get("gate_class")
        if gate not in required_tokens:
            raise SystemExit(f"{rel} item {item.get('id')} missing valid gate_class")

print("check_gate_class_contract: OK")
