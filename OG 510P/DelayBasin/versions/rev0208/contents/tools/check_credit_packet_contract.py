import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/credit-packets-delayed-payoff-and-public-eligibility-traces.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK):
    if not path.exists():
        raise SystemExit(f"missing required credit-packet surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Credit packets, delayed payoff, and public eligibility traces",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Credit packets vs retrospective writes vs replay vs rehearsal",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "upstream candidate surface",
    "downstream payoff family",
    "credit horizon or adjudication delay",
    "alternative candidate or confound family",
    "credit assignment rule or consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("credit-packet contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0071" not in traj or "credit-packet / delayed-payoff / public-eligibility-trace" not in traj:
    raise SystemExit("trajectory map missing credit-packet wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0030" not in prompt_text or "upstream candidate surface" not in prompt_text or "credit assignment rule or consequence" not in prompt_text:
    raise SystemExit("prompt pairs missing credit-packet ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "credit packet" not in runbook or "downstream payoff family" not in runbook:
    raise SystemExit("runbook missing credit-packet guidance")

print("check_credit_packet_contract: OK")
