import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/reasoning-firebreaks-scratchpad-quarantine-and-public-extract-packets.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Reasoning firebreaks, scratchpad quarantine, and public extract packets",
    "## Practice / observation",
    "## Working synthesis",
    "## Reasoning firebreak vs assistant-echo filter vs blind packet vs execution witness",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "judged task / decision / continuation property",
    "public extract / compact residue kept in canon",
    "trace or scratchpad surface withheld / thinned / quarantined",
    "allowed role",
    "exposure / reinclusion / escalation consequence",
]
missing = [item for item in required if item not in text]
if missing:
    print("reasoning-firebreak contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "reasoning firebreak" not in body or "public extract" not in body or "allowed role" not in body:
        print("reasoning-firebreak contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_reasoning_firebreak_contract: OK")
