import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
ALIAS = ROOT / "docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
OPENQ = ROOT / "docs/20-constitution/open-question-registry.md"
QUAR = ROOT / "docs/90-quarantine/wild-speculations-2026-03-08.md"
CHANGELOG = ROOT / "CHANGELOG.md"

for path in (ALIAS, RUNBOOK, TRAJ, OPENQ, QUAR, CHANGELOG):
    if not path.exists():
        raise SystemExit(f"missing required sink-namespace surface: {path}")

checks = [
    (ALIAS, ["shadow-sink", "attention-sink", "sink-token"], "alias doc"),
    (RUNBOOK, ["shadow-sink", "attention-sink / sink-token"], "runbook"),
    (TRAJ, ["shadow-sink", "attention-sink / sink-token"], "trajectory map"),
    (OPENQ, ["shadow-sink language", "attention-sink language"], "open-question registry"),
    (QUAR, ["shadow-sink distinct from attention-sink / sink-token"], "quarantine"),
    (CHANGELOG, ["sink-namespace hygiene", "check_sink_namespace_contract.py"], "changelog"),
]

for path, needles, label in checks:
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"sink-namespace contract missing from {label}: " + ", ".join(missing))

print("check_sink_namespace_contract: OK")
