import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/witness-sets-boundary-panels-and-basin-support-vectors.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required = [
    "# Witness sets, boundary panels, and basin support vectors",
    "## Practice / observation",
    "## Working synthesis",
    "## Witness set vs recap example vs challenge probe",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "witness set",
    "boundary panel",
    "drift signature",
]
missing = [item for item in required if item not in text]
if missing:
    print("witness-set contract missing:", ", ".join(missing))
    sys.exit(1)
if "witness set" not in prompt_text and "boundary panel" not in prompt_text:
    print("witness-set contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_witness_set_contract: OK")
