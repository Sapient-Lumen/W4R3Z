import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/rehearsal-packets-spaced-replay-and-maintenance-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK):
    if not path.exists():
        raise SystemExit(f"missing required rehearsal-packet surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Rehearsal packets, spaced replay, and maintenance budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Rehearsal packet and maintenance budget",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "maintained surface or carry object",
    "spacing or refresh rule",
    "judged survival / degradation signature",
    "retirement or cold-storage trigger",
    "budget or opportunity-cost note",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("rehearsal-packet contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0069" not in traj or "rehearsal-packet / spaced-replay / maintenance-budget" not in traj:
    raise SystemExit("trajectory map missing rehearsal-packet wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0028" not in prompt_text or "spacing or refresh rule" not in prompt_text or "retirement or cold-storage trigger" not in prompt_text:
    raise SystemExit("prompt pairs missing rehearsal-packet ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "rehearsal packet" not in runbook or "budget or opportunity-cost note" not in runbook:
    raise SystemExit("runbook missing rehearsal-packet guidance")

print("check_rehearsal_packet_contract: OK")
