import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/arbitration-witnesses-tie-sets-and-confusability-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required arbitration surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Arbitration witnesses, tie sets, and confusability budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Arbitration witness vs applicability witness vs consultation packet vs contradiction packet",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "state claim or target objective being stress-tested",
    "candidate tie set / simultaneously eligible carry family",
    "shared applicability gate / eligibility surface that kept them alive",
    "arbitration rule / hierarchical router / confidence-aware selector",
    "compared abstain / fallback / defer-to-evidence baseline",
    "confusability slice / near-tie stress family / rival-eligible case",
    "matched task budget / context budget / compute budget",
    "tolerated misroute / tie-instability / confusability budget",
    "route-to-fallback / abstain / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("arbitration contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0099" not in traj or "arbitration witness" not in traj:
    raise SystemExit("trajectory map missing arbitration wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0058" not in prompt_text or "confusability budget" not in prompt_text or "candidate tie set / simultaneously eligible carry family" not in prompt_text:
    raise SystemExit("prompt pairs missing arbitration ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "arbitration witness / tie set / confusability budget" not in runbook:
    raise SystemExit("runbook missing arbitration guidance")

if "CL-0099" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0099")
if "INV-0097" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0097")
if "OQ-0099" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0099")
if "PP-0058" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0058")

print("check_arbitration_witness_contract: OK")
