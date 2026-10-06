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
        raise SystemExit(f"missing required shadow-selection surface: {path}")

doc = required[0].read_text(encoding="utf-8")
required_doc = [
    "selection policy / exposure-fraction clause",
    "all eligible requests, a sampled percentage, or a prefiltered route subset",
    "selection bias or unseen slice",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("shadow-selection contract missing from external-optimizer doc: " + ", ".join(missing))

prompt_text = required[1].read_text(encoding="utf-8")
if "all eligible requests, a sampled percentage, or a prefiltered route subset" not in prompt_text or "selection bias or unseen slice" not in prompt_text:
    raise SystemExit("prompt pairs missing shadow-selection ratchet")

runbook = required[2].read_text(encoding="utf-8")
if "selection policy / exposure-fraction clause" not in runbook:
    raise SystemExit("runbook missing shadow-selection guidance")

traj = required[3].read_text(encoding="utf-8")
if "OQ-0116" not in traj or "sampled percentage" not in traj:
    raise SystemExit("trajectory map missing shadow-selection wording")

oq = required[4].read_text(encoding="utf-8")
if "OQ-0116" not in oq or "sampled percentage" not in oq:
    raise SystemExit("open-question registry missing shadow-selection wording")

quar = required[5].read_text(encoding="utf-8")
if "QWS-0113" not in quar or "shadow-selection registry" not in quar:
    raise SystemExit("quarantine missing shadow-selection-registry counterfactual")

print("check_shadow_selection_contract: OK")
