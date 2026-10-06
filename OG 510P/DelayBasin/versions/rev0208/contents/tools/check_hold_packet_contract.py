import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/hold-packets-abstention-and-epistemic-brakes.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
MOVE_REGISTRY = ROOT / "docs/20-constitution/move-registry.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
move_text = MOVE_REGISTRY.read_text(encoding="utf-8")
required = [
    "# Hold packets, abstention, and epistemic brakes",
    "## Practice / observation",
    "## Working synthesis",
    "## Hold packet vs quarantine vs demotion",
    "## Brake postures",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "hold packet",
    "unlock condition",
    "recover-resync",
]
missing = [item for item in required if item not in text]
if missing:
    print("hold-packet contract missing:", ", ".join(missing))
    sys.exit(1)
if "hold packet" not in prompt_text and "epistemic brake" not in prompt_text:
    print("hold-packet contract missing prompt-pair ratchet")
    sys.exit(1)
if "MV-0013" not in move_text:
    print("hold-packet contract missing certified move")
    sys.exit(1)
print("check_hold_packet_contract: OK")
