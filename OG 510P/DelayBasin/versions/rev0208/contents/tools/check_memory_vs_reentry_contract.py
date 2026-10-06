import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/memory-stores-vs-regime-reentry-packets.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required = [
    "# Memory stores vs regime-reentry packets",
    "## Practice / observation",
    "## Working synthesis",
    "## Memory store vs regime-reentry packet vs check/admission packet",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "memory store",
    "regime-reentry packet",
    "check/admission packet",
]
missing = [item for item in required if item not in text]
if missing:
    print("memory-vs-reentry contract missing:", ", ".join(missing))
    sys.exit(1)
if "memory store" not in prompt_text or "regime-reentry packet" not in prompt_text or "check/admission object" not in prompt_text:
    print("memory-vs-reentry contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_memory_vs_reentry_contract: OK")
