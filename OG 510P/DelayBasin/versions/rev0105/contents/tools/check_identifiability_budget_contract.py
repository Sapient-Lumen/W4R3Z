import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/identifiability-budgets-probe-horizons-and-observability-frontiers.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Identifiability budgets, probe horizons, and observability frontiers",
    "## Practice / observation",
    "## Working synthesis",
    "## Identifiability budget vs basin fingerprint vs identification packet vs gauge discipline",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "judged state or mechanism claim",
    "observable surface / public evidence family",
    "hidden-context / wrapper assumptions",
    "probe horizon / future family",
    "tolerated ambiguity class / equivalence remainder",
    "retreat / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    print("identifiability-budget contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "probe horizon or future family" not in body or "hidden-context or wrapper assumptions" not in body or "tolerated ambiguity class or equivalence remainder" not in body:
        print("identifiability-budget contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_identifiability_budget_contract: OK")
