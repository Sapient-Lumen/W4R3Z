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
        raise SystemExit(f"missing required shadow-comparability surface: {path}")

doc = DOC.read_text(encoding="utf-8")
required_doc = [
    "comparison frame / comparability clause",
    "equal comparison",
    "explicit non-comparability note",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("shadow-comparability contract missing from external-optimizer doc: " + ", ".join(missing))

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "matched request family, population, traffic slice, or time window" not in prompt_text or "only advisory or inconclusive" not in prompt_text:
    raise SystemExit("prompt pairs missing shadow-comparability ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "comparison frame or non-comparability note" not in runbook:
    raise SystemExit("runbook missing shadow-comparability guidance")

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0116" not in traj or "population, traffic slice, or time window" not in traj:
    raise SystemExit("trajectory map missing shadow-comparability wording")

oq = OQ.read_text(encoding="utf-8")
if "OQ-0116" not in oq or "population, traffic slice, or time window" not in oq:
    raise SystemExit("open-question registry missing shadow-comparability wording")

quar = QUAR.read_text(encoding="utf-8")
if "QWS-0106" not in quar or "comparison-frame registry" not in quar:
    raise SystemExit("quarantine missing comparison-frame-registry counterfactual")

print("check_shadow_comparability_contract: OK")
