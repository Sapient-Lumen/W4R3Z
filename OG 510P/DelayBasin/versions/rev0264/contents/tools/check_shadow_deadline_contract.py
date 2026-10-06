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
        raise SystemExit(f"missing required shadow-deadline surface: {path}")
doc = required[0].read_text(encoding="utf-8")
required_doc = [
    "deadline / completion-horizon clause",
    "route timeout, max stream duration, request-timeout posture, or regular-vs-streaming response mode",
    "timeout witness or explicit deadline note",
    "deadline mismatch, truncated stream, or response-mode mismatch",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("shadow-deadline contract missing from external-optimizer doc: " + ", ".join(missing))
prompt_text = required[1].read_text(encoding="utf-8")
if "regular-vs-streaming response mode" not in prompt_text or "timeout witness or explicit deadline note" not in prompt_text:
    raise SystemExit("prompt pairs missing shadow-deadline ratchet")
runbook = required[2].read_text(encoding="utf-8")
if "deadline / completion-horizon clause" not in runbook:
    raise SystemExit("runbook missing shadow-deadline guidance")
traj = required[3].read_text(encoding="utf-8")
if "OQ-0116" not in traj or "regular-vs-streaming response mode" not in traj:
    raise SystemExit("trajectory map missing shadow-deadline wording")
oq = required[4].read_text(encoding="utf-8")
if "OQ-0116" not in oq or "regular-vs-streaming response mode" not in oq:
    raise SystemExit("open-question registry missing shadow-deadline wording")
quar = required[5].read_text(encoding="utf-8")
if "QWS-0118" not in quar or "shadow-deadline registry" not in quar:
    raise SystemExit("quarantine missing shadow-deadline-registry counterfactual")
print("check_shadow_deadline_contract: OK")
