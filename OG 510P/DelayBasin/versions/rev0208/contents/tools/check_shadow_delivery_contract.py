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
        raise SystemExit(f"missing required shadow-delivery surface: {path}")

doc = required[0].read_text(encoding="utf-8")
required_doc = [
    "delivery-assurance / best-effort clause",
    "guaranteed, best-effort, or fire-and-forget",
    "delivery witness or explicit best-effort note",
    "delivery uncertainty or mirror-drop risk",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("shadow-delivery contract missing from external-optimizer doc: " + ", ".join(missing))

prompt_text = required[1].read_text(encoding="utf-8")
if "guaranteed, best-effort, or fire-and-forget" not in prompt_text or "delivery witness or explicit best-effort note" not in prompt_text:
    raise SystemExit("prompt pairs missing shadow-delivery ratchet")

runbook = required[2].read_text(encoding="utf-8")
if "delivery-assurance / best-effort clause" not in runbook:
    raise SystemExit("runbook missing shadow-delivery guidance")

traj = required[3].read_text(encoding="utf-8")
if "OQ-0116" not in traj or "mirror-drop risk" not in traj:
    raise SystemExit("trajectory map missing shadow-delivery wording")

oq = required[4].read_text(encoding="utf-8")
if "OQ-0116" not in oq or "mirror-drop risk" not in oq:
    raise SystemExit("open-question registry missing shadow-delivery wording")

quar = required[5].read_text(encoding="utf-8")
if "QWS-0115" not in quar or "shadow-delivery registry" not in quar:
    raise SystemExit("quarantine missing shadow-delivery-registry counterfactual")

print("check_shadow_delivery_contract: OK")
