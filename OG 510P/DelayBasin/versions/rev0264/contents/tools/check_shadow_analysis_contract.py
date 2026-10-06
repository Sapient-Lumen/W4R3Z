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
        raise SystemExit(f"missing required shadow-analysis surface: {path}")

doc = DOC.read_text(encoding="utf-8")
required_doc = [
    "analysis basis / pass-fail criterion",
    "success, failure, or inconclusive",
    "verify or approval surface",
    "abort trigger",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("shadow-analysis contract missing from external-optimizer doc: " + ", ".join(missing))

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "analysis basis or manual-only rubric" not in prompt_text or "success, failure, or inconclusive result" not in prompt_text:
    raise SystemExit("prompt pairs missing shadow-analysis ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "explicit analysis basis" not in runbook or "manual-only rubric" not in runbook:
    raise SystemExit("runbook missing shadow-analysis guidance")

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0116" not in traj or "observable or qualitative rubric" not in traj:
    raise SystemExit("trajectory map missing shadow-analysis wording")

oq = OQ.read_text(encoding="utf-8")
if "OQ-0116" not in oq or "observable or qualitative rubric" not in oq:
    raise SystemExit("open-question registry missing shadow-analysis wording")

quar = QUAR.read_text(encoding="utf-8")
if "QWS-0105" not in quar or "preregistered promotion scorecard" not in quar:
    raise SystemExit("quarantine missing scorecard-court counterfactual")

print("check_shadow_analysis_contract: OK")
