import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/intervention-equivalence-and-causal-control-packets.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required = [
    "# Intervention-equivalence and causal-control packets",
    "## Practice / observation",
    "## Working synthesis",
    "## Passive-future equivalence vs intervention-equivalence vs local probe",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "intervention family",
    "branch divergence",
    "causal-control packets",
]
missing = [item for item in required if item not in text]
if missing:
    print("intervention-equivalence contract missing:", ", ".join(missing))
    sys.exit(1)
if "intervention-equivalence question" not in prompt_text or "branch divergence" not in prompt_text or "observationally safe" not in prompt_text:
    print("intervention-equivalence contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_intervention_equivalence_contract: OK")
