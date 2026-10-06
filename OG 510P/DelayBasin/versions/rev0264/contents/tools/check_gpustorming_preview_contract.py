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
        raise SystemExit(f"missing required gpustorming-preview surface: {path}")

checks = [
    (DOC, ["preview-stripped, display-scrubbed, or underlier-literal variant", "rendered-preview privilege", "metadata-wrapper privilege"], "operator-token doc"),
    (ALIAS, ["preview-stripped, display-scrubbed, or underlier-literal variant", "rendered-preview privilege", "sample-row privilege"], "alias doc"),
    (TRAJ, [trajectory_problem_phrase("preview")], "trajectory map"),
    (OPENQ, ["preview-stripped/display-scrubbed/underlier-literal variant", "metadata-wrapper privilege", "sample-row privilege"], "open-question registry"),
    (PROMPTS, ["preview-stripped, display-scrubbed, or underlier-literal variant worth checking", "sample-row privilege"], "prompt pairs"),
    (RUNBOOK, ["preview-stripped, display-scrubbed, or underlier-literal variant", "rendered previews"], "runbook"),
    (QUAR, ["QWS-0149", "preview-surface carry or rendering-layer scaffold"], "quarantine"),
    (CHANGELOG, ["preview-stripped / display-scrubbed / underlier-literal guard", "check_gpustorming_preview_contract.py"], "changelog"),
]

for path, needles, label in checks:
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"gpustorming-preview contract missing from {label}: " + ", ".join(missing))

print("check_gpustorming_preview_contract: OK")
