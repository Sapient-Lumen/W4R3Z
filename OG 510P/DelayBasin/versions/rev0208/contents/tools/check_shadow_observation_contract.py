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
        raise SystemExit(f"missing required shadow-observation surface: {path}")

doc = DOC.read_text(encoding="utf-8")
required_doc = [
    "observation budget / warm-up clause",
    "minimum measurement count or comparison duration",
    "advisory or inconclusive",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("shadow-observation contract missing from external-optimizer doc: " + ", ".join(missing))

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "minimum measurement count or comparison duration" not in prompt_text or "quick advisory look" not in prompt_text:
    raise SystemExit("prompt pairs missing shadow-observation ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "explicit observation budget or quick-look note" not in runbook and "minimum observation budget makes the verdict mature enough to count" not in runbook:
    raise SystemExit("runbook missing shadow-observation guidance")

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0116" not in traj or "initial delay, minimum measurement count, or comparison duration" not in traj:
    raise SystemExit("trajectory map missing shadow-observation wording")

oq = OQ.read_text(encoding="utf-8")
if "OQ-0116" not in oq or "initial delay, minimum measurement count, or comparison duration" not in oq:
    raise SystemExit("open-question registry missing shadow-observation wording")

quar = QUAR.read_text(encoding="utf-8")
if "QWS-0107" not in quar or "observation-budget scheduler" not in quar:
    raise SystemExit("quarantine missing observation-budget-scheduler counterfactual")

print("check_shadow_observation_contract: OK")
