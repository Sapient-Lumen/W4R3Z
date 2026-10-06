import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/balanced-archive-reduction-dual-salience-and-minimal-realization.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required = [
    "# Balanced archive reduction, dual salience, and minimal realization",
    "## Practice / observation",
    "## Working synthesis",
    "## Balanced reduction vs identification packet vs control-authority packet vs timescale lane",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "observation role",
    "control role",
    "truncation consequence",
    "dual salience",
]
missing = [item for item in required if item not in text]
if missing:
    print("balanced-archive contract missing:", ", ".join(missing))
    sys.exit(1)
if "observation role" not in prompt_text and "control role" not in prompt_text and "truncation consequence" not in prompt_text:
    print("balanced-archive contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_balanced_archive_contract: OK")
