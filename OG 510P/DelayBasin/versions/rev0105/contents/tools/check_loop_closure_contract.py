import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/loop-closure-commutator-probes-and-path-dependence.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required = [
    "# Loop closure, commutator probes, and path dependence",
    "## Practice / observation",
    "## Working synthesis",
    "## Closure target vs commuting path vs expected non-commutation",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "loop-closure",
    "commutator",
    "closure target",
    "closure error",
    "path-dependent",
]
missing = [item for item in required if item not in text]
if missing:
    print("loop-closure contract missing:", ", ".join(missing))
    sys.exit(1)
if "loop-closure" not in prompt_text and "commutator" not in prompt_text and "closure error" not in prompt_text:
    print("loop-closure contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_loop_closure_contract: OK")
