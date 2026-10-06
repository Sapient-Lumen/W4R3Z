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
        raise SystemExit(f"missing required shadow-sink surface: {path}")

doc = required[0].read_text(encoding="utf-8")
required_doc = [
    "serve-authority / sink-marking clause",
    "non-returning, log-only, or inspection-only",
    "shadow marker",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("shadow-sink contract missing from external-optimizer doc: " + ", ".join(missing))

prompt_text = required[1].read_text(encoding="utf-8")
if "what surface still served authoritative output" not in prompt_text or "candidate outputs were non-returning, log-only, or inspection-only" not in prompt_text:
    raise SystemExit("prompt pairs missing shadow-sink ratchet")

runbook = required[2].read_text(encoding="utf-8")
if "serve-authority / sink-marking clause" not in runbook:
    raise SystemExit("runbook missing shadow-sink guidance")

traj = required[3].read_text(encoding="utf-8")
if "OQ-0116" not in traj or "candidate outputs were non-returning, log-only, or inspection-only" not in traj:
    raise SystemExit("trajectory map missing shadow-sink wording")

oq = required[4].read_text(encoding="utf-8")
if "OQ-0116" not in oq or "candidate outputs were non-returning, log-only, or inspection-only" not in oq:
    raise SystemExit("open-question registry missing shadow-sink wording")

quar = required[5].read_text(encoding="utf-8")
if "QWS-0111" not in quar or "serve-authority registry" not in quar:
    raise SystemExit("quarantine missing serve-authority-registry counterfactual")

print("check_shadow_sink_contract: OK")
