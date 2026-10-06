import json
from packet_contract_common import require_packet_contract

require_packet_contract(
    kind="gate_class_packet_contract",
    surfaces=[
        ("docs/10-method/gate-class-packets-scheduled-windows-and-clock-honest-reopens.md", [
            "This is the compact successor surface for `OQ-0115`.",
            "`scheduled-window`",
            "## Practice / observation",
            "## External pressure from scheduled systems and bounded timed comparisons",
            "## Working synthesis",
            "## `scheduled-window` vs `repeat-pass`",
            "## Countermodels / probes",
            "## Design consequences",
            "## Transformer-facing implication",
        ], "gate-class packet doc"),
        ("docs/00-meta/llm-runbook.md", ["gate-class-packets-scheduled-windows-and-clock-honest-reopens.md"], "runbook"),
        ("docs/50-promptcraft/prompt-pairs.md", ["scheduled-window"], "prompt pairs"),
        ("docs/20-constitution/open-question-registry.md", ["OQ-0115", "RS-0124", "gate-class-packets-scheduled-windows-and-clock-honest-reopens.md"], "open-question registry"),
        ("docs/00-meta/trajectory-map.md", ["OQ-0115", "RS-0124", "gate-class-packets-scheduled-windows-and-clock-honest-reopens.md"], "trajectory map"),
        ("docs/90-quarantine/wild-speculations-2026-03-08.md", ["QWS-0200", "calendar court / timing senate / window-governance board"], "quarantine"),
        ("CHANGELOG.md", ["scheduled-window", "check_gate_class_packet_contract.py"], "changelog"),
        ("WITNESS-VOCABULARY.json", ["gate_class", "scheduled-window"], "vocabulary"),
    ],
)

vocab = json.loads((__import__("pathlib").Path(__file__).resolve().parents[1] / "WITNESS-VOCABULARY.json").read_text(encoding="utf-8"))
allowed = set(vocab["families"]["gate_class"].get("allowed", []))
if "scheduled-window" not in allowed:
    raise SystemExit("WITNESS-VOCABULARY gate_class family missing scheduled-window")
