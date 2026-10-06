import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/archive-self-sufficiency-probe-minimal-core-and-priority-zero.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
SESSION = ROOT / "docs/40-session/foreign-pressure-2026-03-18-claude-self-sufficiency.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, SESSION):
    if not path.exists():
        raise SystemExit(f"missing required self-sufficiency surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Archive self-sufficiency probe, minimal-core replay, and priority zero",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Archive self-sufficiency probe vs packet-level sufficiency witness vs foreign-pressure receipt",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "candidate minimal core",
    "withheld archive mass / omitted family",
    "judged continuation family",
    "admissibility rubric",
    "foreign-pressure receipt",
    "non-independence caveat",
    "Priority 0",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("self-sufficiency-priority contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "Priority 0" not in traj or "self-sufficiency probe" not in traj:
    raise SystemExit("trajectory map missing priority-0 self-sufficiency probe")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0020" not in prompt_text or "foreign-pressure receipt" not in prompt_text or "self-sufficiency probe" not in prompt_text:
    raise SystemExit("prompt pairs missing self-sufficiency / foreign-pressure ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "foreign-pressure receipt" not in runbook or "archive self-sufficiency probe" not in runbook:
    raise SystemExit("runbook missing self-sufficiency / foreign-pressure guidance")

session = SESSION.read_text(encoding="utf-8")
for item in ["Core imported claim", "Assimilation posture", "Non-independence caveat", "Immediate consequences"]:
    if item not in session:
        raise SystemExit("foreign-pressure receipt missing required sections")

print("check_self_sufficiency_priority_contract: OK")
