import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/external-optimizer-loops-public-slow-weights-and-archive-write-gates.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK):
    if not path.exists():
        raise SystemExit(f"missing required external-optimizer surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# External optimizer loops, public slow weights, and archive write gates",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## External optimizer loop vs memory store vs regime-reentry packet vs check/admission packet",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "writable public surfaces",
    "read path into continuation",
    "evaluation or admission gate",
    "fast-vs-slow timescale split",
    "quarantine / rollback consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("external-optimizer contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0066" not in traj or "external optimizer loop" not in traj:
    raise SystemExit("trajectory map missing external-optimizer wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0025" not in prompt_text or "writable public surfaces" not in prompt_text or "read path" not in prompt_text:
    raise SystemExit("prompt pairs missing external-optimizer ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "external optimizer loop" not in runbook or "writable public law" not in runbook:
    raise SystemExit("runbook missing external-optimizer guidance")

print("check_external_optimizer_contract: OK")
