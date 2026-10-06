import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/rival-set-packets-branch-budgets-and-non-forced-singularity.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK):
    if not path.exists():
        raise SystemExit(f"missing required rival-set surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Rival-set packets, branch budgets, and non-forced singularity",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Rival-set packets vs contradiction packets vs hold packets vs homing packets",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "ambiguity or decision class",
    "kept-alive rival set",
    "branch budget or survival cap",
    "next discriminating probe or settle condition",
    "prune / merge / abstain consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("rival-set contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0075" not in traj or "rival-set / branch-budget / non-forced-singularity" not in traj:
    raise SystemExit("trajectory map missing rival-set wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0034" not in prompt_text or "kept-alive rival set" not in prompt_text or "prune / merge / abstain consequence" not in prompt_text:
    raise SystemExit("prompt pairs missing rival-set ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "rival-set packet" not in runbook or "branch budget or survival cap" not in runbook:
    raise SystemExit("runbook missing rival-set guidance")

print("check_rival_set_contract: OK")
