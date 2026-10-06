import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/blind-packets-label-scrubbed-adjudication-and-attribution-guards.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Blind packets, label-scrubbed adjudication, and attribution guards",
    "## Practice / observation",
    "## Working synthesis",
    "## Blind packet vs negative-control handle vs observer/actuator split",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "judged artifact",
    "scrubbed or relabeled view",
    "hidden metadata",
    "reveal / unblinding rule",
    "disagreement / escalation consequence",
]
missing = [item for item in required if item not in text]
if missing:
    print("blind-packet contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "blind packet" not in body or "scrubbed or relabeled view" not in body or "disagreement or escalation consequence" not in body:
        print("blind-packet contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_blind_packet_contract: OK")
