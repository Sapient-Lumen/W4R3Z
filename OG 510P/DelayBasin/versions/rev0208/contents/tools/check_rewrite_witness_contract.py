import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/rewrite-witnesses-roundtrip-packets-and-recap-authority-tests.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Rewrite witnesses, round-trip packets, and recap-authority tests",
    "## Practice / observation",
    "## Working synthesis",
    "## Rewrite witness vs assistant-echo filter vs public extract vs dependence-adjusted witness",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "source packet / authority anchor",
    "rewritten packet / compressed rewrite",
    "round-trip or cross-exam witness",
    "divergence signature",
    "promotion / demotion / rollback consequence",
]
missing = [item for item in required if item not in text]
if missing:
    print("rewrite-witness contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "rewrite witness" not in body or "source packet or authority anchor" not in body or "promotion, demotion, or rollback consequence" not in body:
        print("rewrite-witness contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_rewrite_witness_contract: OK")
