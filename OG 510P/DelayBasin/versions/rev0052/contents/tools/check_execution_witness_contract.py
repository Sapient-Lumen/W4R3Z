import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/execution-witnesses-substrate-perturbation-packets-and-runtime-variance-audits.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Execution witnesses, substrate perturbation packets, and runtime variance audits",
    "## Practice / observation",
    "## Working synthesis",
    "## Execution witness vs blind packet vs continuation margin",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "judged effect / continuation property",
    "substrate family",
    "fixed controls / allowed perturbation",
    "divergence signature",
    "rerun / escalation consequence",
]
missing = [item for item in required if item not in text]
if missing:
    print("execution-witness contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "execution witness" not in body or "substrate family" not in body or "rerun or escalation consequence" not in body:
        print("execution-witness contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_execution_witness_contract: OK")
