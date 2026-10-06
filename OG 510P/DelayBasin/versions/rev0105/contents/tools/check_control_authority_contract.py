import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/control-authority-effort-leakage-and-resistance.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required = [
    "# Control authority, steering effort, leakage, and endogenous resistance",
    "## Practice / observation",
    "## Working synthesis",
    "## Control authority vs witness panel vs identification packet vs continuation margin",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "actuator surface",
    "target property",
    "effort",
    "leakage",
    "endogenous resistance",
]
missing = [item for item in required if item not in text]
if missing:
    print("control-authority contract missing:", ", ".join(missing))
    sys.exit(1)
if "actuator surface" not in prompt_text and "target property" not in prompt_text and "endogenous-resistance" not in prompt_text:
    print("control-authority contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_control_authority_contract: OK")
