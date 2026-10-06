import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/feedback-policy-witnesses-open-loop-baselines-and-contingency-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required feedback-policy surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Feedback-policy witnesses, open-loop baselines, and contingency budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Feedback-policy witness vs interpolation-path witness vs servo packet vs continuation monitor",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "cleanup or state claim being stress-tested",
    "observation channel / checkpoint signal / mid-course readout",
    "compared policy class / fixed open-loop schedule vs feedback-conditioned policy",
    "matched endpoint target / actuation budget / compute budget",
    "protected kernel / contingency invariant / same-task comparison surface",
    "tolerated open-loop substitution gap / contingency budget",
    "rollback / freeze-policy / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("feedback-policy contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0095" not in traj or "feedback-policy witness" not in traj:
    raise SystemExit("trajectory map missing feedback-policy wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0054" not in prompt_text or "compared policy class / fixed open-loop schedule vs feedback-conditioned policy" not in prompt_text or "open-loop substitution gap / contingency budget" not in prompt_text:
    raise SystemExit("prompt pairs missing feedback-policy ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "feedback-policy witness / open-loop baseline / contingency budget" not in runbook:
    raise SystemExit("runbook missing feedback-policy guidance")

if "CL-0095" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0095")
if "INV-0093" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0093")
if "OQ-0095" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0095")
if "PP-0054" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0054")

print("check_feedback_policy_witness_contract: OK")
