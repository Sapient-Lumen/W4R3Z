import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK):
    if not path.exists():
        raise SystemExit(f"missing required alias-packet surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Alias packets, handle collision budgets, and namespace hygiene",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Alias packets vs negative controls vs conformance witnesses vs replay",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "active handle family",
    "plausible alias or collision family",
    "namespace or disambiguation boundary",
    "judged divergence signature",
    "retire / rename / escalate consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("alias-packet contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0072" not in traj or "alias-packet / handle-collision-budget / namespace-hygiene" not in traj:
    raise SystemExit("trajectory map missing alias-packet wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0031" not in prompt_text or "active handle family" not in prompt_text or "retire / rename / escalate consequence" not in prompt_text:
    raise SystemExit("prompt pairs missing alias-packet ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "alias packet" not in runbook or "plausible alias or collision family" not in runbook:
    raise SystemExit("runbook missing alias-packet guidance")

print("check_alias_packet_contract: OK")
