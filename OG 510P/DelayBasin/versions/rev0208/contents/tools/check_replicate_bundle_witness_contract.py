import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/replicate-bundle-witnesses-repeated-inference-sweeps-and-lucky-path-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required replicate-bundle surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Replicate-bundle witnesses, repeated-inference sweeps, and lucky-path budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Replicate-bundle witness vs interpolation-path witness vs execution witness vs cue-neighborhood witness",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "state claim being stress-tested",
    "fixed prompt / route / control protocol / operational conditions",
    "replicate bundle / repeated-inference family / decode regime",
    "protected kernel / invariant readout / same-task success criterion",
    "tolerated between-run dispersion / lucky-path budget",
    "widen-bundle / lower-confidence / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("replicate-bundle contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0094" not in traj or "replicate-bundle witness" not in traj:
    raise SystemExit("trajectory map missing replicate-bundle wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0053" not in prompt_text or "fixed prompt / route / control protocol / operational conditions" not in prompt_text or "between-run dispersion / lucky-path budget" not in prompt_text:
    raise SystemExit("prompt pairs missing replicate-bundle ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "replicate-bundle witness / repeated-inference sweep / lucky-path budget" not in runbook:
    raise SystemExit("runbook missing replicate-bundle guidance")

if "CL-0094" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0094")
if "INV-0092" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0092")
if "OQ-0094" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0094")
if "PP-0053" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0053")

print("check_replicate_bundle_witness_contract: OK")
