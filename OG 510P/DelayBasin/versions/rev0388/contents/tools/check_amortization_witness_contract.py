import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/amortization-witnesses-reuse-horizons-and-compiled-dividend-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required amortization surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Amortization witnesses, reuse horizons, and compiled-dividend budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Amortization witness vs dual-effect witness vs procedural-compilation packet vs replicate-bundle witness",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "state claim or target objective being stress-tested",
    "upfront acquisition cost / exploratory move / learning move",
    "carry object / stored tip / reusable skill / compiled packet",
    "future reuse family / neighboring task class / deployment slice",
    "compared one-shot baseline / no-reuse baseline / from-scratch baseline",
    "matched horizon / task volume / compute budget",
    "judged payback / reuse dividend / compiled-dividend budget",
    "rollback / one-shot demotion / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("amortization contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0097" not in traj or "amortization witness" not in traj:
    raise SystemExit("trajectory map missing amortization wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0056" not in prompt_text or "compiled-dividend budget" not in prompt_text or "no-reuse baseline / from-scratch baseline" not in prompt_text:
    raise SystemExit("prompt pairs missing amortization ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "amortization witness / reuse horizon / compiled-dividend budget" not in runbook:
    raise SystemExit("runbook missing amortization guidance")

if "CL-0097" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0097")
if "INV-0095" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0095")
if "OQ-0097" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0097")
if "PP-0056" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0056")

print("check_amortization_witness_contract: OK")
