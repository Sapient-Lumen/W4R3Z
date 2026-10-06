import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/interpolation-path-witnesses-ramp-schedules-and-endpoint-equivalence-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required interpolation-path surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Interpolation-path witnesses, ramp schedules, and endpoint-equivalence budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Interpolation-path witness vs mixed-direction witness vs probe-order witness vs backaction witness",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "cleanup or state claim being stress-tested",
    "start surface / source chart / initial packet",
    "compared interpolation path / ramp schedule / adaptive route family",
    "matched endpoint target / final mixed cue / fixed actuation budget",
    "protected kernel / pathwise invariant / same-task comparison surface",
    "tolerated arc-vs-chord residue / endpoint-equivalence budget",
    "rollback / schedule-lock / restage / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("interpolation-path contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0093" not in traj or "interpolation-path witness" not in traj:
    raise SystemExit("trajectory map missing interpolation-path wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0052" not in prompt_text or "compared interpolation path / ramp schedule / adaptive route family" not in prompt_text or "arc-vs-chord residue / endpoint-equivalence budget" not in prompt_text:
    raise SystemExit("prompt pairs missing interpolation-path ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "interpolation-path witness / ramp schedule / endpoint-equivalence budget" not in runbook:
    raise SystemExit("runbook missing interpolation-path guidance")

if "CL-0093" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0093")
if "INV-0091" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0091")
if "OQ-0093" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0093")
if "PP-0052" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0052")

print("check_interpolation_path_witness_contract: OK")
