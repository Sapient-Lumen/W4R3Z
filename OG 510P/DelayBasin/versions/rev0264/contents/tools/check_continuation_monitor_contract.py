import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/continuation-monitors-anytime-validity-and-public-observer-loops.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Continuation monitors, anytime-validity pressure, and public observer loops",
    "## Practice / observation",
    "## Working synthesis",
    "## Stopping packet vs continuation monitor",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "monitored property or ambiguity split",
    "accumulating evidence state or score",
    "update or shrink rule",
    "reset or stitching rule",
    "coupling to stop rule",
]
missing = [item for item in required if item not in text]
if missing:
    print("continuation-monitor contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "continuation monitor" not in body or "reset or stitching rule" not in body or "couples to the stop rule" not in body:
        print("continuation-monitor contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_continuation_monitor_contract: OK")
