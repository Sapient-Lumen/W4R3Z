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
        raise SystemExit(f"missing required shadow-sideeffect surface: {path}")

doc = required[0].read_text(encoding="utf-8")
required_doc = [
    "side-effect suppression / actuator-isolation clause",
    "read-only, dry-run-aware, isolated to a non-authoritative sink",
    "unsuppressed actuator or downstream-write risk",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("shadow-sideeffect contract missing from external-optimizer doc: " + ", ".join(missing))

prompt_text = required[1].read_text(encoding="utf-8")
if "read-only, dry-run-aware, isolated to a non-authoritative sink" not in prompt_text or "out-of-band writes could still occur" not in prompt_text:
    raise SystemExit("prompt pairs missing shadow-sideeffect ratchet")

runbook = required[2].read_text(encoding="utf-8")
if "read-only, dry-run-aware, isolated to a non-authoritative sink" not in runbook:
    raise SystemExit("runbook missing shadow-sideeffect guidance")

traj = required[3].read_text(encoding="utf-8")
if "OQ-0116" not in traj or "out-of-band writes could still occur" not in traj:
    raise SystemExit("trajectory map missing shadow-sideeffect wording")

oq = required[4].read_text(encoding="utf-8")
if "OQ-0116" not in oq or "out-of-band writes could still occur" not in oq:
    raise SystemExit("open-question registry missing shadow-sideeffect wording")

quar = required[5].read_text(encoding="utf-8")
if "QWS-0112" not in quar or "side-effect suppression registry" not in quar:
    raise SystemExit("quarantine missing side-effect-suppression-registry counterfactual")

print("check_shadow_sideeffect_contract: OK")
