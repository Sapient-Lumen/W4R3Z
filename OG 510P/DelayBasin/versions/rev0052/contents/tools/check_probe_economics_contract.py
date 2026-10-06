import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/probe-economics-value-of-information-and-budgeted-disambiguation.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Probe economics, value of information, and budgeted disambiguation",
    "## Practice / observation",
    "## Working synthesis",
    "## Identification packet vs homing packet vs probe-economics packet",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "candidate probe family",
    "gated continuation decision",
    "rough cost class",
    "expected split power",
    "nearest deferred alternative",
]
missing = [item for item in required if item not in text]
if missing:
    print("probe-economics contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "probe-economics packet" not in body or "expected split power" not in body or "nearest deferred alternative" not in body:
        print("probe-economics contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_probe_economics_contract: OK")
