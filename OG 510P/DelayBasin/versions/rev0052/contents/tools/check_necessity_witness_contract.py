import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/necessity-witnesses-support-cores-and-ablation-ladders.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Necessity witnesses, support cores, and ablation ladders",
    "## Practice / observation",
    "## Working synthesis",
    "## Necessity witness vs conformance witness vs rewrite witness vs assistant-echo filter",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "full candidate surface",
    "proposed support core",
    "smallest ablation / removal family",
    "tolerated degradation / continuation margin",
    "prune / promote / rollback consequence",
]
missing = [item for item in required if item not in text]
if missing:
    print("necessity-witness contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "necessity witness" not in body or "full candidate surface" not in body or "prune, promote, or rollback consequence" not in body:
        print("necessity-witness contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_necessity_witness_contract: OK")
