import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/basin-fingerprints-future-probe-signatures-and-same-answer-is-not-same-state.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
runbook_text = RUNBOOK.read_text(encoding="utf-8")
required = [
    "# Basin fingerprints, future-probe signatures, and same-answer-is-not-same-state",
    "## Practice / observation",
    "## Working synthesis",
    "## Basin fingerprint vs triangulation vs predictive state vs future equivalence",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "anchor continuation property / judged branch",
    "compared loader, packet, or intervention family",
    "fingerprint panel / future-probe signature",
    "tolerated divergence / instability budget",
    "narrowing / fallback / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    print("bain-fingerprint contract missing:", ", ".join(missing))
    sys.exit(1)
for body in (prompt_text, runbook_text):
    if "future-probe signature" not in body or "tolerated divergence or instability budget" not in body or "narrowing, fallback, or quarantine consequence" not in body:
        print("basin-fingerprint contract missing prompt/runbook ratchet")
        sys.exit(1)
print("check_basin_fingerprint_contract: OK")
