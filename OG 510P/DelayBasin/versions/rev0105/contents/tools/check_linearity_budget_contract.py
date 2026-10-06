import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/local-linearity-budgets-curved-chart-adapters-and-tangent-steering.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required local-linearity surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Local linearity budgets, curved chart adapters, and tangent steering",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Local linearity budget vs operator core vs servo packet vs gauge discipline",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "target property or operator core",
    "local chart neighborhood or execution family",
    "assumed linear / monotone region or small-step budget",
    "curvature or distortion warning sign",
    "relinearize / rollback / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("local-linearity contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0079" not in traj or "local-linearity-budget" not in traj:
    raise SystemExit("trajectory map missing local-linearity-budget wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0038" not in prompt_text or "local chart neighborhood or execution family" not in prompt_text or "first curvature or distortion warning sign" not in prompt_text:
    raise SystemExit("prompt pairs missing local-linearity ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "local linearity budget / curved chart adapter / tangent steering" not in runbook:
    raise SystemExit("runbook missing local-linearity guidance")

if "CL-0079" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0079")
if "INV-0077" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0077")
if "OQ-0079" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0079")
if "PP-0038" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0038")

print("check_linearity_budget_contract: OK")
