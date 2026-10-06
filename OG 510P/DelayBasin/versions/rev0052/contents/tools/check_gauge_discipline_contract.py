import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/gauge-discipline-canonical-charts-and-invariant-claims.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required = [
    "# Gauge discipline, canonical charts, and invariant claims",
    "## Practice / observation",
    "## Working synthesis",
    "## Invariant claim vs canonical chart vs metaphor",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "invariant claim",
    "chart switch",
    "coordinate-loaded",
    "canonical chart",
]
missing = [item for item in required if item not in text]
if missing:
    print("gauge-discipline contract missing:", ", ".join(missing))
    sys.exit(1)
if "chart switch" not in prompt_text and "chart-specific" not in prompt_text and "invariant claim" not in prompt_text:
    print("gauge-discipline contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_gauge_discipline_contract: OK")
