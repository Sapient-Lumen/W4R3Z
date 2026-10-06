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
        raise SystemExit(f"missing required shadow-topology surface: {path}")

doc = required[0].read_text(encoding="utf-8")
required_doc = [
    "substrate-compatibility / topology-support clause",
    "same endpoint or another backend/deployment class the mirroring substrate actually supports",
    "one-production/one-shadow, one-deployment, or same-backend-type limits",
    "unsupported backend, incompatible endpoint class, or topology shim",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("shadow-topology contract missing from external-optimizer doc: " + ", ".join(missing))

prompt_text = required[1].read_text(encoding="utf-8")
if "same endpoint or another backend/deployment class the mirroring substrate actually supports" not in prompt_text or "one-production/one-shadow, one-deployment, or same-backend-type limits" not in prompt_text:
    raise SystemExit("prompt pairs missing shadow-topology ratchet")

runbook = required[2].read_text(encoding="utf-8")
if "substrate-compatibility / topology-support clause" not in runbook:
    raise SystemExit("runbook missing shadow-topology guidance")

traj = required[3].read_text(encoding="utf-8")
if "OQ-0116" not in traj or "same-backend-type" not in traj:
    raise SystemExit("trajectory map missing shadow-topology wording")

oq = required[4].read_text(encoding="utf-8")
if "OQ-0116" not in oq or "same-backend-type" not in oq:
    raise SystemExit("open-question registry missing shadow-topology wording")

quar = required[5].read_text(encoding="utf-8")
if "QWS-0116" not in quar or "shadow-substrate registry" not in quar:
    raise SystemExit("quarantine missing shadow-substrate-registry counterfactual")

print("check_shadow_topology_contract: OK")
