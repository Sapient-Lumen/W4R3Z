import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/negative-control-handles-sham-packets-and-placebo-guards.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Negative-control handles, sham packets, and placebo guards",
    "## Practice / observation",
    "## Working synthesis",
    "## Negative-control handle vs observer/actuator split vs witness set",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "active handle",
    "matched sham",
    "expected differential signature",
    "pass/fail rule",
    "retire / escalate rule",
]
missing = [item for item in required if item not in text]
if missing:
    print("negative-control handle contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "negative-control handle" not in body or "matched sham" not in body or "expected differential signature" not in body:
        print("negative-control handle contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_negative_control_handle_contract: OK")
