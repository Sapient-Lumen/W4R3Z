import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/future-equivalence-classes-and-causal-state-compression.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required = [
    "# Future-equivalence classes and causal-state compression",
    "## Practice / observation",
    "## Working synthesis",
    "## Future-equivalence class vs test-sufficient packet vs local probe",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "future-equivalence classes",
    "future family",
    "lost distinction",
]
missing = [item for item in required if item not in text]
if missing:
    print("future-equivalence contract missing:", ", ".join(missing))
    sys.exit(1)
if "future-equivalence class" not in prompt_text or "lost distinction" not in prompt_text or "compression was too aggressive" not in prompt_text:
    print("future-equivalence contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_future_equivalence_contract: OK")
