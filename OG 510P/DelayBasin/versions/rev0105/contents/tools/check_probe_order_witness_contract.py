import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/probe-order-witnesses-swapped-order-baselines-and-sequencing-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required probe-order surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Probe-order witnesses, swapped-order baselines, and sequencing budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Probe-order witness vs loop closure vs backaction witness vs excitation witness",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "fixed ambiguity or state claim",
    "probe family or staged intervention family being compared",
    "specific compared orderings or insertion points",
    "intended invariant readout or same-judgment target",
    "tolerated sequencing defect / order-sensitivity budget",
    "hold / rollback / quarantine / restage consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("probe-order contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0087" not in traj or "probe-order" not in traj:
    raise SystemExit("trajectory map missing probe-order wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0046" not in prompt_text or "specific compared orderings or insertion points" not in prompt_text or "order-sensitivity budget" not in prompt_text:
    raise SystemExit("prompt pairs missing probe-order ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "probe-order witness / swapped-order baseline / sequencing budget" not in runbook:
    raise SystemExit("runbook missing probe-order guidance")

if "CL-0087" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0087")
if "INV-0085" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0085")
if "OQ-0087" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0087")
if "PP-0046" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0046")

print("check_probe_order_witness_contract: OK")
