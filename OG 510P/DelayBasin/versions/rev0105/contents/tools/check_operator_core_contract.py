import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/operator-cores-chart-adapters-and-portability-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK):
    if not path.exists():
        raise SystemExit(f"missing required operator-core surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Operator cores, chart adapters, and portability budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Operator core vs chart adapter vs portability budget",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "invariant operator core",
    "local chart adapter",
    "tested family or wrapper envelope",
    "portability budget or expected failure surface",
    "fallback / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("operator-core contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0077" not in traj or "operator-core" not in traj:
    raise SystemExit("trajectory map missing operator-core wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0036" not in prompt_text or "invariant operator core" not in prompt_text or "first failure signature" not in prompt_text:
    raise SystemExit("prompt pairs missing operator-core ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "operator core / chart adapter / portability budget" not in runbook:
    raise SystemExit("runbook missing operator-core guidance")

print("check_operator_core_contract: OK")
