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

for path in (DOC, ALIAS, TRAJ, OPENQ, PROMPTS, RUNBOOK, QUAR, CHANGELOG):
    if not path.exists():
        raise SystemExit(f"missing required gpustorming-statusproof surface: {path}")

checks = [
    (DOC, ["wrapper-stripped, status-scrubbed, or direct-work variant", "status-wrapper privilege", "collateral-status privilege"], "operator-token doc"),
    (ALIAS, ["wrapper-stripped, status-scrubbed, or direct-work variant", "status-wrapper privilege", "collateral-status privilege"], "alias doc"),
    (TRAJ, [trajectory_problem_phrase("statusproof")], "trajectory map"),
    (OPENQ, ["wrapper-stripped/status-scrubbed/direct-work variant", "status-wrapper privilege", "collateral-status privilege"], "open-question registry"),
    (PROMPTS, ["wrapper-stripped, status-scrubbed, or direct-work variant worth checking", "collateral-status privilege"], "prompt pairs"),
    (RUNBOOK, ["wrapper-stripped, status-scrubbed, or direct-work variant", "signed letters"], "runbook"),
    (QUAR, ["QWS-0148", "status-wrapper carry or collateral-status scaffold"], "quarantine"),
    (CHANGELOG, ["wrapper-stripped / status-scrubbed / direct-work guard", "check_gpustorming_statusproof_contract.py"], "changelog"),
]

for path, needles, label in checks:
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"gpustorming-statusproof contract missing from {label}: " + ", ".join(missing))

print("check_gpustorming_statusproof_contract: OK")
