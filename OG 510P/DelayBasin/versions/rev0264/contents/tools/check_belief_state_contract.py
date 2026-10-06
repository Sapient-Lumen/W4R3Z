import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/public-belief-state-under-partial-observability.md"

text = DOC.read_text(encoding="utf-8")
required = [
    "# Public belief state under partial observability",
    "## Practice / observation",
    "## Working synthesis",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "partial observability",
    "public belief state",
]
missing = [item for item in required if item not in text]
if missing:
    print("belief-state contract missing:", ", ".join(missing))
    sys.exit(1)
print("check_belief_state_contract: OK")
