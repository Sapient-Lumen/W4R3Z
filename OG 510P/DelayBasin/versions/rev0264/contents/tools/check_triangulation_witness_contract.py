import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/triangulation-witnesses-multiloader-overlap-and-basin-checks.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Triangulation witnesses, multi-loader overlap, and basin checks",
    "## Practice / observation",
    "## Working synthesis",
    "## Triangulation witness vs conformance witness vs sufficiency witness vs rewrite witness",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "anchor continuation property / judged basin",
    "at least two non-trivially different loader surfaces",
    "shared support envelope / fixed execution family",
    "expected overlap / divergence signature",
    "narrowing / fallback / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    print("triangulation-witness contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "triangulation witness" not in body or "at least two non-trivially different loader surfaces" not in body or "narrowing, fallback, or quarantine consequence" not in body:
        print("triangulation-witness contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_triangulation_witness_contract: OK")
