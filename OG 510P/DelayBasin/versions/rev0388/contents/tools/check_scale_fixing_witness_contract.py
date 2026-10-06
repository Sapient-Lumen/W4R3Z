import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/scale-fixing-witnesses-coarse-graining-maps-and-separation-of-scales-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required scale-fixing surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Scale-fixing witnesses, coarse-graining maps, and separation-of-scales budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Scale-fixing witness vs timescale lane vs gauge-fixing witness vs public beta-function claim",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "source scale or resolution",
    "target scale or resolution",
    "coarse-graining map or aggregation rule",
    "protected observable or operator-core commitment",
    "discarded modes / nuisance family / residual remainder",
    "relevance criterion / separation-of-scales budget",
    "demotion / rollback / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("scale-fixing contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0083" not in traj or "scale-fixing" not in traj:
    raise SystemExit("trajectory map missing scale-fixing wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0042" not in prompt_text or "coarse-graining map or aggregation rule" not in prompt_text or "relevance criterion / separation-of-scales budget" not in prompt_text:
    raise SystemExit("prompt pairs missing scale-fixing ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "scale-fixing witness / coarse-graining map / separation-of-scales budget" not in runbook:
    raise SystemExit("runbook missing scale-fixing guidance")

if "CL-0083" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0083")
if "INV-0081" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0081")
if "OQ-0083" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0083")
if "PP-0042" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0042")

print("check_scale_fixing_witness_contract: OK")
