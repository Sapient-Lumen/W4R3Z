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
        raise SystemExit(f"missing required gpustorming-derivative surface: {path}")

checks = [
    (DOC, ["source-root, live-head, or derivative-scrubbed variant", "derivative-surface privilege", "snapshot-authority privilege"], "operator-token doc"),
    (ALIAS, ["source-root, live-head, or derivative-scrubbed variant", "derivative-surface privilege", "export-mirror privilege"], "alias doc"),
    (TRAJ, [trajectory_problem_phrase("derivative")], "trajectory map"),
    (OPENQ, ["source-root/live-head/derivative-scrubbed variant", "derivative-surface privilege", "snapshot-authority privilege"], "open-question registry"),
    (PROMPTS, ["source-root, live-head, or derivative-scrubbed variant worth checking", "export-mirror privilege"], "prompt pairs"),
    (RUNBOOK, ["source-root, live-head, or derivative-scrubbed variant", "curated exports"], "runbook"),
    (QUAR, ["QWS-0151", "derivative-surface carry or snapshot-authority scaffold"], "quarantine"),
    (CHANGELOG, ["source-root / live-head / derivative-scrubbed guard", "check_gpustorming_derivative_contract.py"], "changelog"),
]

for path, needles, label in checks:
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"gpustorming-derivative contract missing from {label}: " + ", ".join(missing))

print("check_gpustorming_derivative_contract: OK")
