import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/triangle-defects-cocycle-witnesses-and-atlas-consistency-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required triangle-defect surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Triangle defects, cocycle witnesses, and atlas consistency budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Triangle defect vs chart-transition witness vs loop closure vs global atlas claim",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "three chart realizations or family members",
    "shared operator core",
    "existing pairwise chart-transition witnesses",
    "triangle overlap probe or family-level shared test surface",
    "composition defect / cocycle residue / atlas-consistency budget",
    "demotion / rollback / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("triangle-defect contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0081" not in traj or "triangle-defect" not in traj:
    raise SystemExit("trajectory map missing triangle-defect wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0040" not in prompt_text or "triangle overlap probe or family-level shared test surface" not in prompt_text or "composition defect / cocycle residue / atlas-consistency budget" not in prompt_text:
    raise SystemExit("prompt pairs missing triangle-defect ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "triangle defect / cocycle witness / atlas consistency budget" not in runbook:
    raise SystemExit("runbook missing triangle-defect guidance")

if "CL-0081" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0081")
if "INV-0079" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0079")
if "OQ-0081" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0081")
if "PP-0040" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0040")

print("check_triangle_defect_contract: OK")
