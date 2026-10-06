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
        raise SystemExit(f"missing required shadow-rewrite surface: {path}")

doc = required[0].read_text(encoding="utf-8")
required_doc = [
    "request-shape / rewrite-disclosure clause",
    "host / authority suffix, header mutation, host rewrite",
    "original-shape witness",
    "rewrite drift",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("shadow-rewrite contract missing from external-optimizer doc: " + ", ".join(missing))

prompt_text = required[1].read_text(encoding="utf-8")
if "host/authority suffix, header mutation, host rewrite" not in prompt_text or "original-shape witness" not in prompt_text:
    raise SystemExit("prompt pairs missing shadow-rewrite ratchet")

runbook = required[2].read_text(encoding="utf-8")
if "request-shape / rewrite-disclosure clause" not in runbook:
    raise SystemExit("runbook missing shadow-rewrite guidance")

traj = required[3].read_text(encoding="utf-8")
if "OQ-0116" not in traj or "original-shape witness" not in traj:
    raise SystemExit("trajectory map missing shadow-rewrite wording")

oq = required[4].read_text(encoding="utf-8")
if "OQ-0116" not in oq or "original-shape witness" not in oq:
    raise SystemExit("open-question registry missing shadow-rewrite wording")

quar = required[5].read_text(encoding="utf-8")
if "QWS-0114" not in quar or "request-shape registry" not in quar:
    raise SystemExit("quarantine missing request-shape-registry counterfactual")

print("check_shadow_rewrite_contract: OK")
