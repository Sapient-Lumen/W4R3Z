import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/sentinel-panels-border-inputs-and-reopen-canaries.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"

text = DOC.read_text(encoding="utf-8")
prompt_text = PROMPTS.read_text(encoding="utf-8")
required = [
    "# Sentinel panels, border inputs, and reopen canaries",
    "## Practice / observation",
    "## Working synthesis",
    "## Sentinel panel vs witness panel vs challenge probe",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "sentinel panel",
    "property monitored",
    "expected deviation signature",
    "recover-resync",
]
missing = [item for item in required if item not in text]
if missing:
    print("sentinel-panel contract missing:", ", ".join(missing))
    sys.exit(1)
if "sentinel panel" not in prompt_text and "reopen canary" not in prompt_text:
    print("sentinel-panel contract missing prompt-pair ratchet")
    sys.exit(1)
print("check_sentinel_panel_contract: OK")
