import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/stopping-packets-sequential-decision-thresholds-and-commit-certificates.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Stopping packets, sequential decision thresholds, and commit certificates",
    "## Practice / observation",
    "## Working synthesis",
    "## Probe-economics packet vs stopping packet",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "ambiguity class",
    "decision threshold or commit criterion",
    "continuation action licensed",
    "error / rollback posture",
    "budget-exhaustion fallback",
]
missing = [item for item in required if item not in text]
if missing:
    print("stopping-packet contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "stopping packet" not in body or "commit criterion" not in body or "budget-exhaustion fallback" not in body:
        print("stopping-packet contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_stopping_packet_contract: OK")
