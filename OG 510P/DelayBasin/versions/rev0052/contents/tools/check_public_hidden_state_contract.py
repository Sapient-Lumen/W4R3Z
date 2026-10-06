import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/public-hidden-state-and-reentry-abi.md"

text = DOC.read_text(encoding="utf-8")
required = [
    "# Public hidden state and re-entry ABI",
    "## Practice / observation",
    "## Working synthesis",
    "## State packet vs evidence packet vs check packet",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "state packet",
    "evidence packet",
    "check packet",
]
missing = [item for item in required if item not in text]
if missing:
    print("public-hidden-state contract missing:", ", ".join(missing))
    sys.exit(1)
print("check_public_hidden_state_contract: OK")
