import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/update-gain-surprise-gating-and-challenge-probes.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required = [
    "# Update gain, surprise gating, and challenge probes",
    "## Practice / observation",
    "## Working synthesis",
    "## Trigger vs update gain vs challenge probe",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "update gain",
    "challenge probe",
    "recover-resync",
]
missing = [item for item in required if item not in text]
if missing:
    print("revision-gain contract missing:", ", ".join(missing))
    sys.exit(1)
if "name the trigger, the update gain" not in prompt_text:
    print("revision-gain contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_revision_gain_contract: OK")
