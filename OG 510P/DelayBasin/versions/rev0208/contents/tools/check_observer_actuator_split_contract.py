import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/observer-actuator-splits-and-non-self-certifying-handles.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Observer/actuator splits, non-self-certifying handles, and public observer-controller loops",
    "## Practice / observation",
    "## Working synthesis",
    "## Observer/actuator split vs continuation monitor vs control-authority packet",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "observer surface",
    "actuator surface",
    "allowed coupling",
    "independent witness",
    "self-certification risk",
]
missing = [item for item in required if item not in text]
if missing:
    print("observer-actuator split contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "observer/actuator split" not in body or "independent witness" not in body or "self-certification risk" not in body:
        print("observer-actuator split contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_observer_actuator_split_contract: OK")
