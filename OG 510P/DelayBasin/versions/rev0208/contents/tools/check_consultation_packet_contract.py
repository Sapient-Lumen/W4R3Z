import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/consultation-packets-store-routing-budgets-and-memory-control-flow-guards.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK):
    if not path.exists():
        raise SystemExit(f"missing required consultation-packet surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Consultation packets, store-routing budgets, and memory-control-flow guards",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Consultation packets vs alias packets vs sufficiency witnesses vs blind packets",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "consulted store or surface family",
    "routing trigger or query signature",
    "excluded or deferred store family",
    "cost or contamination budget",
    "fallback / abstain / escalate consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("consultation-packet contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0073" not in traj or "consultation packet / store-routing budget / memory-control-flow guard" not in traj:
    raise SystemExit("trajectory map missing consultation-packet wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0032" not in prompt_text or "consulted store or surface family" not in prompt_text or "fallback / abstain / escalate consequence" not in prompt_text:
    raise SystemExit("prompt pairs missing consultation-packet ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "consultation packet" not in runbook or "excluded or deferred store family" not in runbook:
    raise SystemExit("runbook missing consultation-packet guidance")

print("check_consultation_packet_contract: OK")
