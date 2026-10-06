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
        raise SystemExit(f"missing required shadow-protocol surface: {path}")

doc = required[0].read_text(encoding="utf-8")
required_doc = [
    "protocol / transport-semantics clause",
    "HTTPRoute versus GRPCRoute or HTTP/1.1 versus HTTP/2 versus gRPC",
    "trailer-status witness or explicit protocol note",
    "protocol mismatch, bridge normalization, or trailer-status loss",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("shadow-protocol contract missing from external-optimizer doc: " + ", ".join(missing))

prompt_text = required[1].read_text(encoding="utf-8")
if "HTTPRoute versus GRPCRoute" not in prompt_text or "trailer-status witness or explicit protocol note" not in prompt_text:
    raise SystemExit("prompt pairs missing shadow-protocol ratchet")

runbook = required[2].read_text(encoding="utf-8")
if "protocol / transport-semantics clause" not in runbook:
    raise SystemExit("runbook missing shadow-protocol guidance")

traj = required[3].read_text(encoding="utf-8")
if "OQ-0116" not in traj or "HTTPRoute versus GRPCRoute" not in traj:
    raise SystemExit("trajectory map missing shadow-protocol wording")

oq = required[4].read_text(encoding="utf-8")
if "OQ-0116" not in oq or "HTTPRoute versus GRPCRoute" not in oq:
    raise SystemExit("open-question registry missing shadow-protocol wording")

quar = required[5].read_text(encoding="utf-8")
if "QWS-0119" not in quar or "shadow-protocol registry" not in quar:
    raise SystemExit("quarantine missing shadow-protocol-registry counterfactual")

print("check_shadow_protocol_contract: OK")
