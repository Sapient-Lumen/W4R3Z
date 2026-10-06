import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/sufficiency-witnesses-replay-capsules-and-core-only-reentry-trials.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Sufficiency witnesses, replay capsules, and core-only re-entry trials",
    "## Practice / observation",
    "## Working synthesis",
    "## Sufficiency witness vs necessity witness vs conformance witness vs assistant-echo filter",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "candidate reduced packet / replay seed",
    "core-only replay surface",
    "fixed or withheld context family",
    "target continuation property / tolerated degradation",
    "reinflate / fallback / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    print("sufficiency-witness contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "sufficiency witness" not in body or "core-only replay surface" not in body or "reinflate, fallback, or quarantine consequence" not in body:
        print("sufficiency-witness contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_sufficiency_witness_contract: OK")
