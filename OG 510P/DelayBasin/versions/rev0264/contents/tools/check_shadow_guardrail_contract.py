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
        raise SystemExit(f"missing required shadow-guardrail surface: {path}")

doc = DOC.read_text(encoding="utf-8")
required_doc = [
    "slice discipline / guardrail clause",
    "aggregate-only, first-point, or all-values",
    "critical metric or slice",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("shadow-guardrail contract missing from external-optimizer doc: " + ", ".join(missing))

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "aggregate-only, first-point, or all-values" not in prompt_text or "critical metric or slice" not in prompt_text:
    raise SystemExit("prompt pairs missing shadow-guardrail ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "slice-discipline / guardrail clause" not in runbook and "aggregate-only, first-point, or all-values" not in runbook:
    raise SystemExit("runbook missing shadow-guardrail guidance")

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0116" not in traj or "aggregate-only, first-point, or all-values" not in traj:
    raise SystemExit("trajectory map missing shadow-guardrail wording")

oq = OQ.read_text(encoding="utf-8")
if "OQ-0116" not in oq or "aggregate-only, first-point, or all-values" not in oq:
    raise SystemExit("open-question registry missing shadow-guardrail wording")

quar = QUAR.read_text(encoding="utf-8")
if "QWS-0108" not in quar or "critical-slice registry" not in quar:
    raise SystemExit("quarantine missing critical-slice-registry counterfactual")

print("check_shadow_guardrail_contract: OK")
