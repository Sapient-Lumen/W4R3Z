import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/chart-transition-witnesses-overlap-maps-and-transport-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required chart-transition surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Chart transition witnesses, overlap maps, and transport budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Chart transition witness vs operator core vs local linearity budget vs loop closure",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "source chart",
    "target chart",
    "shared operator core",
    "overlap probe or shared test surface",
    "transport budget or tolerated residue",
    "fallback / rollback / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("chart-transition contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0080" not in traj or "chart-transition-witness" not in traj:
    raise SystemExit("trajectory map missing chart-transition wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0039" not in prompt_text or "overlap probe or shared test surface" not in prompt_text or "transport budget or tolerated residue" not in prompt_text:
    raise SystemExit("prompt pairs missing chart-transition ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "chart transition witness / overlap map / transport budget" not in runbook:
    raise SystemExit("runbook missing chart-transition guidance")

if "CL-0080" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0080")
if "INV-0078" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0078")
if "OQ-0080" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0080")
if "PP-0039" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0039")

print("check_chart_transition_contract: OK")
