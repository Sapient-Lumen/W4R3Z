import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/mixed-direction-witnesses-cross-term-sweeps-and-superposition-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required mixed-direction surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Mixed-direction witnesses, cross-term sweeps, and superposition budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Mixed-direction witness vs directional-neighborhood witness vs probe-order witness vs backaction witness",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "cleanup or state claim being stress-tested",
    "single-direction passes / constituent perturbation families / basis sweeps",
    "mixed perturbation / composed cue / joint sweep",
    "matched marginal step sizes / local mixing rule / fixed baseline",
    "protected kernel / intended invariant readout / same-task comparison surface",
    "tolerated cross-term residue / superposition budget",
    "rollback / factorize-claim / widen-mix-test / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("mixed-direction contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0092" not in traj or "mixed-direction witness" not in traj:
    raise SystemExit("trajectory map missing mixed-direction wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0051" not in prompt_text or "mixed perturbation / composed cue / joint sweep" not in prompt_text or "cross-term residue / superposition budget" not in prompt_text:
    raise SystemExit("prompt pairs missing mixed-direction ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "mixed-direction witness / cross-term sweep / superposition budget" not in runbook:
    raise SystemExit("runbook missing mixed-direction guidance")

if "CL-0092" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0092")
if "INV-0090" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0090")
if "OQ-0092" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0092")
if "PP-0051" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0051")

print("check_mixed_direction_witness_contract: OK")
