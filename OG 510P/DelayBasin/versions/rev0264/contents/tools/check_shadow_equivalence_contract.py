from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

required = [
    ROOT / "docs/10-method/external-optimizer-loops-public-slow-weights-and-archive-write-gates.md",
    ROOT / "docs/50-promptcraft/prompt-pairs.md",
    ROOT / "docs/00-meta/llm-runbook.md",
    ROOT / "docs/00-meta/trajectory-map.md",
    ROOT / "docs/20-constitution/open-question-registry.md",
    ROOT / "docs/90-quarantine/wild-speculations-2026-03-08.md",
]

for path in required:
    if not path.exists():
        raise SystemExit(f"missing required shadow-equivalence surface: {path}")

doc = required[0].read_text(encoding="utf-8")
required_doc = [
    "equivalence substrate / confounder clause",
    "metric-label alignment",
    "cache warmup",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("shadow-equivalence contract missing from external-optimizer doc: " + ", ".join(missing))

prompt_text = required[1].read_text(encoding="utf-8")
if "non-target deployment-shape or measurement-shape conditions" not in prompt_text or "metric-label alignment or confounder note" not in prompt_text:
    raise SystemExit("prompt pairs missing shadow-equivalence ratchet")

runbook = required[2].read_text(encoding="utf-8")
if "equivalence substrate or confounder note" not in runbook:
    raise SystemExit("runbook missing shadow-equivalence guidance")

traj = required[3].read_text(encoding="utf-8")
if "OQ-0116" not in traj or "metric-label alignment or confounder note" not in traj:
    raise SystemExit("trajectory map missing shadow-equivalence wording")

oq = required[4].read_text(encoding="utf-8")
if "OQ-0116" not in oq or "metric-label alignment or confounder note" not in oq:
    raise SystemExit("open-question registry missing shadow-equivalence wording")

quar = required[5].read_text(encoding="utf-8")
if "QWS-0110" not in quar or "baseline-equivalence registry" not in quar:
    raise SystemExit("quarantine missing baseline-equivalence-registry counterfactual")

print("check_shadow_equivalence_contract: OK")
