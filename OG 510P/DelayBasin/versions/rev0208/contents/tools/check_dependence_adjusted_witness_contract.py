import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/dependence-adjusted-witnesses-effective-evidence-and-pseudoreplication-guards.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Dependence-adjusted witnesses, effective evidence, and pseudo-replication guards",
    "## Practice / observation",
    "## Working synthesis",
    "## Dependence-adjusted witness vs witness set vs blind packet vs continuation monitor",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "witness family / probe family",
    "shared-origin coupling / dependence structure",
    "effective evidence weight / discount rule",
    "what still counts as genuinely new evidence",
    "stop / escalation consequence",
]
missing = [item for item in required if item not in text]
if missing:
    print("dependence-adjusted-witness contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "dependence-adjusted witness" not in body or "shared-origin coupling" not in body or "genuinely new evidence" not in body:
        print("dependence-adjusted-witness contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_dependence_adjusted_witness_contract: OK")
