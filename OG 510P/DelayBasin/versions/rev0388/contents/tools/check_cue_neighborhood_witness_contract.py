import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/cue-neighborhood-witnesses-reactivation-radius-sweeps-and-basin-breadth-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required cue-neighborhood surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Cue-neighborhood witnesses, reactivation-radius sweeps, and basin-breadth budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Cue-neighborhood witness vs relapse witness vs excitation witness vs probe-order witness",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "cleanup or state claim being stress-tested",
    "seed recovery cue / relapse trigger / local chart anchor",
    "nearby cue family / paraphrase / alias / style / context-stem sweep",
    "protected kernel / matched-fresh baseline / same-task comparison surface",
    "tolerated reactivation radius / basin-breadth budget",
    "rollback / demote / widen-sweep / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("cue-neighborhood contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0090" not in traj or "cue-neighborhood witness" not in traj:
    raise SystemExit("trajectory map missing cue-neighborhood wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0049" not in prompt_text or "nearby cue family / paraphrase / alias / style / context-stem sweep" not in prompt_text or "reactivation radius / basin-breadth budget" not in prompt_text:
    raise SystemExit("prompt pairs missing cue-neighborhood ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "cue-neighborhood witness / reactivation-radius sweep / basin-breadth budget" not in runbook:
    raise SystemExit("runbook missing cue-neighborhood guidance")

if "CL-0090" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0090")
if "INV-0088" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0088")
if "OQ-0090" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0090")
if "PP-0049" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0049")

print("check_cue_neighborhood_witness_contract: OK")
