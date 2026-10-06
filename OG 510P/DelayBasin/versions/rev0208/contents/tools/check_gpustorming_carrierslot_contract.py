import pathlib

from gpustorming_contract_lib import trajectory_problem_phrase

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/operator-tokens-and-bootstrap-grammar.md"
ALIAS = ROOT / "docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
OPENQ = ROOT / "docs/20-constitution/open-question-registry.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
QUAR = ROOT / "docs/90-quarantine/wild-speculations-2026-03-08.md"
CHANGELOG = ROOT / "CHANGELOG.md"

for path in [DOC, ALIAS, TRAJ, OPENQ, PROMPTS, RUNBOOK, QUAR, CHANGELOG]:
    if not path.exists():
        raise SystemExit(f"missing required gpustorming-carrierslot surface: {path}")

checks = [
    (DOC, ["slot-swapped, rung-shifted, or reveal-order-scrubbed variant", "carrier-slot privilege", "reveal-order privilege"], "operator-token doc"),
    (ALIAS, ["slot-swapped, rung-shifted, or reveal-order-scrubbed variant", "first-answer privilege", "escalation-rung privilege"], "alias doc"),
    (TRAJ, [trajectory_problem_phrase("carrierslot")], "trajectory map"),
    (OPENQ, ["slot-swapped/rung-shifted/reveal-order-scrubbed variant", "carrier-slot privilege", "first-answer privilege"], "open-question registry"),
    (PROMPTS, ["slot-swapped, rung-shifted, or reveal-order-scrubbed variant worth checking", "reveal-order privilege"], "prompt pairs"),
    (RUNBOOK, ["slot-swapped, rung-shifted, or reveal-order-scrubbed variant", "favored answer carriers"], "runbook"),
    (QUAR, ["QWS-0150", "carrier-slot carry or reveal-order scaffold"], "quarantine"),
    (CHANGELOG, ["slot-swapped / rung-shifted / reveal-order-scrubbed guard", "check_gpustorming_carrierslot_contract.py"], "changelog"),
]

for path, needles, label in checks:
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"gpustorming-carrierslot contract missing from {label}: " + ", ".join(missing))

print("check_gpustorming_carrierslot_contract: OK")
