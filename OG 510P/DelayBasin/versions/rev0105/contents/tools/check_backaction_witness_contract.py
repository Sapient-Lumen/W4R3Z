import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/backaction-witnesses-diagnostic-probes-and-non-demolition-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required backaction surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Backaction witnesses, diagnostic probes, and non-demolition budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Backaction witness vs excitation witness vs execution witness vs observer-actuator split",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "ambiguity or state claim being probed",
    "diagnostic probe / intervention family actually applied",
    "expected readout or discriminating observable",
    "matched sham / no-op / commuted-order baseline",
    "tolerated backaction / non-demolition budget",
    "hold / rollback / quarantine / restage consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("backaction contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0086" not in traj or "backaction" not in traj:
    raise SystemExit("trajectory map missing backaction wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0045" not in prompt_text or "diagnostic probe / intervention family" not in prompt_text or "non-demolition budget" not in prompt_text:
    raise SystemExit("prompt pairs missing backaction ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "backaction witness / diagnostic probe family / non-demolition budget" not in runbook:
    raise SystemExit("runbook missing backaction guidance")

if "CL-0086" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0086")
if "INV-0084" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0084")
if "OQ-0086" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0086")
if "PP-0045" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0045")

print("check_backaction_witness_contract: OK")
