import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/dual-control-revisions-and-identification-packets.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required = [
    "# Dual-control revisions and identification packets",
    "## Practice / observation",
    "## Working synthesis",
    "## Innovation packet vs identification packet vs sentinel panel vs hold packet",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "identification packet",
    "observation sought",
    "recover-resync",
]
missing = [item for item in required if item not in text]
if missing:
    print("identification-packet contract missing:", ", ".join(missing))
    sys.exit(1)
if "identification packet" not in prompt_text:
    print("identification-packet contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_identification_packet_contract: OK")
