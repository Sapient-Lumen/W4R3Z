import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/continuation-rate-distortion-and-prior-intrusion.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

doc_text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required_doc = [
    "# Continuation rate–distortion and prior intrusion",
    "## Practice / observation",
    "## Working synthesis",
    "## Rate budget vs distortion target vs mismatch budget",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "distortion target",
    "mismatch budget",
    "prior intrusion",
]
missing = [item for item in required_doc if item not in doc_text]
if missing:
    print("rate-distortion contract missing from doc:", ", ".join(missing))
    sys.exit(1)
if "If you claim a compression or innovation improvement, name the distortion target" not in prompt_text:
    print("rate-distortion contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_rate_distortion_contract: OK")
