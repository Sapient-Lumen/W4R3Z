import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/contradiction-packets-precedence-ladders-and-conflict-transparent-abstention.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK):
    if not path.exists():
        raise SystemExit(f"missing required contradiction-packet surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Contradiction packets, precedence ladders, and conflict-transparent abstention",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Contradiction packets vs consultation packets vs belief state vs blind packets",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "conflicting claim or decision surface",
    "disagreeing evidence or surface family",
    "precedence or arbitration rule",
    "surviving ambiguity or unresolved residue",
    "abstain / escalate / supersession consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("contradiction-packet contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0074" not in traj or "contradiction-packet / precedence-ladder / conflict-transparent-abstention" not in traj:
    raise SystemExit("trajectory map missing contradiction-packet wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0033" not in prompt_text or "conflicting claim or decision surface" not in prompt_text or "abstain / escalate / supersession consequence" not in prompt_text:
    raise SystemExit("prompt pairs missing contradiction-packet ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "contradiction packet" not in runbook or "precedence or arbitration rule" not in runbook:
    raise SystemExit("runbook missing contradiction-packet guidance")

print("check_contradiction_packet_contract: OK")
