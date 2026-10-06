import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/continuation-margins-guard-bands-and-perturbation-budgets.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required = [
    "# Continuation margins, guard bands, and perturbation budgets",
    "## Practice / observation",
    "## Working synthesis",
    "## Continuation margin vs witness panel vs sentinel panel vs loop-closure probe",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "protected property",
    "perturbation family",
    "failure signature",
    "guard band",
]
missing = [item for item in required if item not in text]
if missing:
    print("continuation-margin contract missing:", ", ".join(missing))
    sys.exit(1)
if "perturbation family" not in prompt_text and "guard band" not in prompt_text and "protected property" not in prompt_text:
    print("continuation-margin contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_continuation_margin_contract: OK")
