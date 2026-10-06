import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/assistant-echo-filters-self-carry-omission-packets-and-history-decontamination.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Assistant-echo filters, self-carry omission packets, and history decontamination",
    "## Practice / observation",
    "## Working synthesis",
    "## Assistant-echo filter vs execution witness vs memory-store distinction",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "judged task / continuation property",
    "kept user-side anchor / retained evidence surface",
    "omitted or thinned assistant-side surface",
    "invariance or gain signature",
    "reinclusion / escalation consequence",
]
missing = [item for item in required if item not in text]
if missing:
    print("assistant-echo-filter contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "assistant-echo filter" not in body or "kept user-side anchor" not in body or "reinclusion or escalation consequence" not in body:
        print("assistant-echo-filter contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_assistant_echo_filter_contract: OK")
