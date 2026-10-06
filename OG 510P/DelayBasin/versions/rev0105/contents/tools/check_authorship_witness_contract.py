import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/authorship-witnesses-autonomy-postures-and-maker-checker-traces.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"
RECEIPT_CONTRACT = ROOT / "docs/20-constitution/revision-receipt-contract.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG, RECEIPT_CONTRACT, RECEIPT):
    if not path.exists():
        raise SystemExit(f"missing required authorship-witness surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Authorship witnesses, autonomy postures, and maker-checker traces",
    "## Practice / observation",
    "## Pressure from neighboring datacubes",
    "## External pressure from adjacent provenance and human-AI governance practice",
    "## Working synthesis",
    "## Authorship witness vs status-lane witness vs scope witness vs revision receipt",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "initiating lane / request origin",
    "draft-authorship posture / accepted-text lane",
    "approval or admission lane / counted-decision surface",
    "execution or materialization lane / packaging or edit surface",
    "review or compensating-control lane",
    "autonomy posture / human-piloted vs assisted vs approval-bounded vs bounded-autonomous classification",
    "lane-collapse state / separated vs partially-collapsed vs collapsed-with-compensation",
    "fail-closed repair / ordinary-continuation vs record-compensating-control vs require-independent-review vs hold vs recover-resync consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("authorship-witness contract missing: " + ", ".join(missing))

if "OQ-0104" not in TRAJ.read_text(encoding="utf-8"):
    raise SystemExit("trajectory map missing OQ-0104 wiring")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0063" not in prompt_text or "initiating lane / request origin" not in prompt_text or "lane-collapse state / separated vs partially-collapsed vs collapsed-with-compensation" not in prompt_text:
    raise SystemExit("prompt pairs missing authorship-witness ratchet")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "authorship witness" not in runbook or "autonomy posture" not in runbook:
    raise SystemExit("runbook missing authorship-witness guidance")
if "CL-0104" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0104")
if "INV-0102" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0102")
if "OQ-0104" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0104")
if "PP-0063" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0063")
contract = RECEIPT_CONTRACT.read_text(encoding="utf-8")
if "authorship_witness" not in contract:
    raise SystemExit("revision-receipt contract missing authorship_witness")
receipt_text = RECEIPT.read_text(encoding="utf-8")
if '"authorship_witness"' not in receipt_text:
    raise SystemExit("revision receipt missing authorship_witness")

print("check_authorship_witness_contract: OK")
