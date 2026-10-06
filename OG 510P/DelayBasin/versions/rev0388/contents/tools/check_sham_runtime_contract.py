import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/sham-runtimes-decoy-archives-and-anti-self-sealing-compression-tests.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
SESSION = ROOT / "docs/40-session/foreign-pressure-2026-03-18-claude-self-sufficiency.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, SESSION):
    if not path.exists():
        raise SystemExit(f"missing required sham-runtime surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Sham runtimes, decoy archives, and anti-self-sealing compression tests",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Sham runtime vs runtime triplet vs archive self-sufficiency probe vs negative-control handle",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "candidate runtime",
    "matched sham or decoy runtime",
    "sequestered challenge suite",
    "within-family adjudication metric",
    "relatedness / leakage risk",
    "shrink / preserve / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("sham-runtime contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0064" not in traj or "sham runtime" not in traj:
    raise SystemExit("trajectory map missing sham-runtime wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0023" not in prompt_text or "sham or decoy runtime" not in prompt_text or "sequestered challenge suite" not in prompt_text:
    raise SystemExit("prompt pairs missing sham-runtime ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "anti-self-sealing" not in runbook or "sham runtime" not in runbook:
    raise SystemExit("runbook missing sham-runtime guidance")

session = SESSION.read_text(encoding="utf-8")
if "Fourth-pass recursive assimilation" not in session or "sequestered challenge suite" not in session:
    raise SystemExit("foreign-pressure receipt missing fourth-pass assimilation note")

print("check_sham_runtime_contract: OK")
