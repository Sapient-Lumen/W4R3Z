import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/homing-packets-adaptive-distinguishing-probes-and-reorientation.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Homing packets, adaptive distinguishing probes, and reorientation under ambiguity",
    "## Practice / observation",
    "## Working synthesis",
    "## Identification packet vs homing packet vs sentinel panel vs witness panel",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "ambiguity class",
    "orientation/update rule",
    "stop or escalation condition",
    "homing packet",
]
missing = [item for item in required if item not in text]
if missing:
    print("homing-packet contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "homing packet" not in body or "ambiguity class" not in body or "orientation/update rule" not in body:
        print("homing-packet contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_homing_packet_contract: OK")
