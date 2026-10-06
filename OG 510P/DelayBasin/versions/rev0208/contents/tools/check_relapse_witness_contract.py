import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/relapse-witnesses-recovery-probes-and-suppression-vs-washout-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required relapse-witness surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Relapse witnesses, recovery probes, and suppression-vs-washout budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Relapse witness vs reset witness vs hysteresis witness vs excitation witness",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "contamination family or influence claimed to be washed out",
    "reset / filter / suppression operator that produced the clean-looking state",
    "recovery trigger / adversarial cue / structured follow-up family",
    "protected kernel / matched-fresh baseline / same-task comparison surface",
    "tolerated relapse / recoverability budget",
    "rollback / reinject / quarantine / restage consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("relapse-witness contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0089" not in traj or "relapse witness" not in traj:
    raise SystemExit("trajectory map missing relapse-witness wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0048" not in prompt_text or "recovery trigger / adversarial cue / structured follow-up family" not in prompt_text or "recoverability budget" not in prompt_text:
    raise SystemExit("prompt pairs missing relapse-witness ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "relapse witness / recovery probe / suppression-vs-washout budget" not in runbook:
    raise SystemExit("runbook missing relapse-witness guidance")

if "CL-0089" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0089")
if "INV-0087" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0087")
if "OQ-0089" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0089")
if "PP-0048" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0048")

print("check_relapse_witness_contract: OK")
