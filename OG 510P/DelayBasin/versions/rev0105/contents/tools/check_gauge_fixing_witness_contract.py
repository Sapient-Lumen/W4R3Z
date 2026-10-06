import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/gauge-fixing-witnesses-reference-observables-and-defect-comparability.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required gauge-fixing surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Gauge-fixing witnesses, reference observables, and defect comparability",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Gauge-fixing witness vs gauge discipline vs triangle defect vs atlas synchronizer",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "invariant observable or reference observable",
    "chosen gauge / anchor / spanning-tree base",
    "comparison family or support set",
    "null / flatness expectation / zero-defect baseline",
    "defect-comparability budget",
    "demotion / rollback / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("gauge-fixing contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0082" not in traj or "gauge-fixing" not in traj:
    raise SystemExit("trajectory map missing gauge-fixing wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0041" not in prompt_text or "null / flatness expectation / zero-defect baseline" not in prompt_text or "defect-comparability budget" not in prompt_text:
    raise SystemExit("prompt pairs missing gauge-fixing ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "gauge-fixing witness / reference observable / defect comparability budget" not in runbook:
    raise SystemExit("runbook missing gauge-fixing guidance")

if "CL-0082" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0082")
if "INV-0080" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0080")
if "OQ-0082" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0082")
if "PP-0041" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0041")

print("check_gauge_fixing_witness_contract: OK")
