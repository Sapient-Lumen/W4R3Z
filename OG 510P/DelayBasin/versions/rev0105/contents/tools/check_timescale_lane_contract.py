import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/timescale-stratification-and-consolidation-lanes.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required = [
    "# Timescale stratification and consolidation lanes",
    "## Practice / observation",
    "## Working synthesis",
    "## Fast lane vs medium lane vs slow lane",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "timescale",
    "transfer rule",
    "expire",
]
missing = [item for item in required if item not in text]
if missing:
    print("timescale-lane contract missing:", ", ".join(missing))
    sys.exit(1)
if "timescale stratification" not in prompt_text and "consolidation-lane" not in prompt_text:
    print("timescale-lane contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_timescale_lane_contract: OK")
