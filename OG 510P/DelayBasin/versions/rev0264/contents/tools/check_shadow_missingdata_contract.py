import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/external-optimizer-loops-public-slow-weights-and-archive-write-gates.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
OQ = ROOT / "docs/20-constitution/open-question-registry.md"
QUAR = ROOT / "docs/90-quarantine/wild-speculations-2026-03-08.md"

for path in (DOC, PROMPTS, RUNBOOK, TRAJ, OQ, QUAR):
    if not path.exists():
        raise SystemExit(f"missing required shadow-missingdata surface: {path}")

doc = DOC.read_text(encoding="utf-8")
required_doc = [
    "missing-data / evidence-availability clause",
    "empty arrays, NaN or infinity, nil-like results, or absent telemetry",
    "must-have-data",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("shadow-missingdata contract missing from external-optimizer doc: " + ", ".join(missing))

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "empty arrays, NaN-like outputs, nil-like results, or absent telemetry" not in prompt_text or "had to have data to count at all" not in prompt_text:
    raise SystemExit("prompt pairs missing shadow-missingdata ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "missing-data / evidence-availability clause" not in runbook and "absent telemetry" not in runbook:
    raise SystemExit("runbook missing shadow-missingdata guidance")

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0116" not in traj or "absent telemetry" not in traj:
    raise SystemExit("trajectory map missing shadow-missingdata wording")

oq = OQ.read_text(encoding="utf-8")
if "OQ-0116" not in oq or "absent telemetry" not in oq:
    raise SystemExit("open-question registry missing shadow-missingdata wording")

quar = QUAR.read_text(encoding="utf-8")
if "QWS-0109" not in quar or "must-have-data registry" not in quar:
    raise SystemExit("quarantine missing must-have-data-registry counterfactual")

print("check_shadow_missingdata_contract: OK")
