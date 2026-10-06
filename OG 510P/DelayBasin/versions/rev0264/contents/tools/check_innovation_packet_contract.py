import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/innovation-packets-and-reconciliation-under-delay.md"

text = DOC.read_text(encoding="utf-8")
required = [
    "# Innovation packets and reconciliation under delay",
    "## Practice / observation",
    "## Working synthesis",
    "## Innovation packet vs recap blob vs rollback signal",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "innovation packet",
    "anchor",
    "recover-resync",
]
missing = [item for item in required if item not in text]
if missing:
    print("innovation-packet contract missing:", ", ".join(missing))
    sys.exit(1)
print("check_innovation_packet_contract: OK")
