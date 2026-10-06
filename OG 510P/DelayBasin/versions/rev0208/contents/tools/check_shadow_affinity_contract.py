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
        raise SystemExit(f"missing required shadow-affinity surface: {path}")

doc = required[0].read_text(encoding="utf-8")
required_doc = [
    "affinity / session-continuity clause",
    "stateless-routing versus client-IP, header, or cookie affinity posture",
    "affinity witness or explicit no-session-state note",
    "sticky-route drift, warm-connection mismatch, or cached-session-state mismatch",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("shadow-affinity contract missing from external-optimizer doc: " + ", ".join(missing))

prompt_text = required[1].read_text(encoding="utf-8")
if "SessionId-based same-instance routing" not in prompt_text or "affinity witness or explicit no-session-state note" not in prompt_text:
    raise SystemExit("prompt pairs missing shadow-affinity ratchet")

runbook = required[2].read_text(encoding="utf-8")
if "affinity / session-continuity clause" not in runbook:
    raise SystemExit("runbook missing shadow-affinity guidance")

traj = required[3].read_text(encoding="utf-8")
if "OQ-0116" not in traj or "sticky-route drift" not in traj:
    raise SystemExit("trajectory map missing shadow-affinity wording")

oq = required[4].read_text(encoding="utf-8")
if "OQ-0116" not in oq or "SessionId-based same-instance routing" not in oq:
    raise SystemExit("open-question registry missing shadow-affinity wording")

quar = required[5].read_text(encoding="utf-8")
if "QWS-0120" not in quar or "shadow-session registry" not in quar:
    raise SystemExit("quarantine missing shadow-session-registry counterfactual")

print("check_shadow_affinity_contract: OK")
