import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/status-lane-witnesses-decision-execution-splits-and-frozen-public-transitions.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"
LEDGER = ROOT / "SURFACE-STATUS.json"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
MANIFEST = ROOT / "RELEASE-MANIFEST.json"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG, LEDGER, RECEIPT, MANIFEST):
    if not path.exists():
        raise SystemExit(f"missing required status-lane surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Status-lane witnesses, decision/execution splits, and frozen-public transitions",
    "## Practice / observation",
    "## Pressure from neighboring datacubes",
    "## External pressure from adjacent release and provenance practice",
    "## Working synthesis",
    "## Status-lane witness vs revision receipt vs release manifest vs operational-head register",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "candidate or explicit absence / merely nearby surface",
    "admitted decision / approval surface",
    "execution surface / materialized artifact",
    "frozen public / citation surface or explicit absence",
    "durable status ledger / register / pointer relation where that mapping lives",
    "mismatch / drift / rollback / citation-warning consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("status-lane contract missing: " + ", ".join(missing))

if "OQ-0102" not in TRAJ.read_text(encoding="utf-8"):
    raise SystemExit("trajectory map missing OQ-0102 wiring")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0061" not in prompt_text or "admitted decision / approval surface" not in prompt_text or "frozen public / citation surface or explicit absence" not in prompt_text:
    raise SystemExit("prompt pairs missing status-lane ratchet")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "status-lane witness" not in runbook or "decision-execution split" not in runbook:
    raise SystemExit("runbook missing status-lane guidance")
if "CL-0102" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0102")
if "INV-0100" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0100")
if "OQ-0102" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0102")
if "PP-0061" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0061")

ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
for key in ("project", "surface_family", "operational_head", "status_lanes", "citation_head", "state_class", "freeze_gate", "durable_status_surface"):
    if key not in ledger:
        raise SystemExit(f"SURFACE-STATUS.json missing key: {key}")
if ledger.get("project") != "DelayBasin":
    raise SystemExit("SURFACE-STATUS.json project must be DelayBasin")
if ledger.get("durable_status_surface") != "SURFACE-STATUS.json":
    raise SystemExit("SURFACE-STATUS.json durable_status_surface must self-point")
lanes = ledger["status_lanes"]
for key in ("decision_surface", "execution_surface", "frozen_public_surface"):
    if key not in lanes:
        raise SystemExit(f"SURFACE-STATUS.json status_lanes missing: {key}")
for rel in (lanes["decision_surface"], lanes["execution_surface"]):
    if rel and not (ROOT / rel).exists():
        raise SystemExit(f"SURFACE-STATUS.json referenced surface missing: {rel}")
if not str(lanes["frozen_public_surface"]).endswith('.zip'):
    raise SystemExit("SURFACE-STATUS.json frozen_public_surface must point to a zip bundle name")
if 'make lint' not in ledger.get('freeze_gate', {}).get('checks', []):
    raise SystemExit("SURFACE-STATUS.json freeze_gate must include make lint")

print("check_status_lane_contract: OK")
