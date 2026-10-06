import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/dual-effect-witnesses-explore-exploit-splits-and-information-premium-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required dual-effect surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Dual-effect witnesses, explore-exploit splits, and information-premium budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Dual-effect witness vs identification packet vs probe-economics packet vs feedback-policy witness",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "state claim or target objective being stress-tested",
    "control action family / exploitation move / current actuation",
    "epistemic dividend / information actually sought or acquired",
    "compared policy class / exploitation-only baseline / no-learning baseline",
    "matched task budget / actuation budget / horizon budget",
    "protected kernel / same-task comparison surface / judged downstream advantage",
    "tolerated exploration premium / dual-effect budget",
    "rollback / exploit-only fallback / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("dual-effect contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0096" not in traj or "dual-effect witness" not in traj:
    raise SystemExit("trajectory map missing dual-effect wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0055" not in prompt_text or "exploration premium / dual-effect budget" not in prompt_text or "exploitation-only baseline / no-learning baseline" not in prompt_text:
    raise SystemExit("prompt pairs missing dual-effect ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "dual-effect witness / explore-exploit split / information-premium budget" not in runbook:
    raise SystemExit("runbook missing dual-effect guidance")

if "CL-0096" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0096")
if "INV-0094" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0094")
if "OQ-0096" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0096")
if "PP-0055" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0055")

print("check_dual_effect_witness_contract: OK")
