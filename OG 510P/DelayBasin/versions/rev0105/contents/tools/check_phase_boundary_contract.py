import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/phase-boundaries-rollover-packets-and-event-cut-discipline.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required = [
    "# Phase boundaries, rollover packets, and event-cut discipline",
    "## Practice / observation",
    "## Working synthesis",
    "## Phase boundary vs timescale lane vs innovation packet vs hold packet",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "phase boundary",
    "rollover packet",
    "persists",
    "reset",
]
missing = [item for item in required if item not in text]
if missing:
    print("phase-boundary contract missing:", ", ".join(missing))
    sys.exit(1)
if "phase boundary" not in prompt_text and "rollover packet" not in prompt_text:
    print("phase-boundary contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_phase_boundary_contract: OK")
