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

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
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
