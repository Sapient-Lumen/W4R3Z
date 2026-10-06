import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/conformance-witnesses-loader-contracts-and-abi-drift-guards.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Conformance witnesses, loader contracts, and ABI drift guards",
    "## Practice / observation",
    "## Working synthesis",
    "## Conformance witness vs public hidden state vs execution witness vs rewrite witness",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "interface surface / claimed loader",
    "supported model-wrapper-context family",
    "minimal conformance test or metamorphic check family",
    "non-conformance / drift signature",
    "narrowing / demotion / fallback consequence",
]
missing = [item for item in required if item not in text]
if missing:
    print("conformance-witness contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "conformance witness" not in body or "supported model-wrapper-context family" not in body or "narrowing, demotion, or fallback consequence" not in body:
        print("conformance-witness contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_conformance_witness_contract: OK")
