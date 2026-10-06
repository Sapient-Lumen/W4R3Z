import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/directional-neighborhood-witnesses-anisotropy-sweeps-and-local-shape-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required directional-neighborhood surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Directional-neighborhood witnesses, anisotropy sweeps, and local-shape budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Directional-neighborhood witness vs cue-neighborhood witness vs backaction witness vs probe-order witness",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "cleanup or state claim being stress-tested",
    "seed cue / local chart anchor / stressor starting point",
    "compared cue directions / perturbation modes / neighborhood axes",
    "matched step size / local sweep radius / fixed baseline",
    "protected kernel / intended invariant readout / same-task comparison surface",
    "tolerated directional asymmetry / local-shape budget",
    "rollback / narrow-claim / widen-sweep / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("directional-neighborhood contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0091" not in traj or "directional-neighborhood witness" not in traj:
    raise SystemExit("trajectory map missing directional-neighborhood wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0050" not in prompt_text or "compared cue directions / perturbation modes / neighborhood axes" not in prompt_text or "directional asymmetry / local-shape budget" not in prompt_text:
    raise SystemExit("prompt pairs missing directional-neighborhood ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "directional-neighborhood witness / anisotropy sweep / local-shape budget" not in runbook:
    raise SystemExit("runbook missing directional-neighborhood guidance")

if "CL-0091" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0091")
if "INV-0089" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0089")
if "OQ-0091" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0091")
if "PP-0050" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0050")

print("check_directional_neighborhood_witness_contract: OK")
