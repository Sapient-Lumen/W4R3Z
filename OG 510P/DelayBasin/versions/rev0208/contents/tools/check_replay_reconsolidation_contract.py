import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/replay-reconsolidation-and-public-restaging.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK):
    if not path.exists():
        raise SystemExit(f"missing required replay/reconsolidation surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Replay, reconsolidation, and public restaging",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Replay vs retrieval vs reconsolidation",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "replay seed or restaging surface",
    "judged continuation property actually recovered",
    "public surface eligible for rewrite",
    "challenge or destabilizing evidence family",
    "fallback / rollback consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("replay-reconsolidation contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0067" not in traj or "replay / reconsolidation" not in traj:
    raise SystemExit("trajectory map missing replay/reconsolidation wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0026" not in prompt_text or "replay seed" not in prompt_text or "destabilizing evidence" not in prompt_text:
    raise SystemExit("prompt pairs missing replay/reconsolidation ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "reconsolidation" not in runbook or "replay seed or restaging surface" not in runbook:
    raise SystemExit("runbook missing replay/reconsolidation guidance")

print("check_replay_reconsolidation_contract: OK")
