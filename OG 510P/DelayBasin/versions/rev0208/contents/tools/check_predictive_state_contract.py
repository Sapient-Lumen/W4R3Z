import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/predictive-state-representations-and-test-sufficient-packets.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required = [
    "# Predictive state representations and test-sufficient packets",
    "## Practice / observation",
    "## Working synthesis",
    "## Test-sufficient packet vs memory store vs predictive model vs local probe",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "test-sufficient packet",
    "future tests",
    "challenge probes",
]
missing = [item for item in required if item not in text]
if missing:
    print("predictive-state contract missing:", ", ".join(missing))
    sys.exit(1)
if "future tests" not in prompt_text or "predictive sufficiency" not in prompt_text or "challenge probes" not in prompt_text:
    print("predictive-state contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_predictive_state_contract: OK")
