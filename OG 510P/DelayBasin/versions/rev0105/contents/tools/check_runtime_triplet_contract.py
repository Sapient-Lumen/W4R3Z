import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/runtime-triplets-core-exemplars-and-challenge-suites.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
SESSION = ROOT / "docs/40-session/foreign-pressure-2026-03-18-claude-self-sufficiency.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, SESSION):
    if not path.exists():
        raise SystemExit(f"missing required runtime-triplet surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Runtime triplets, core-exemplars splits, and challenge suites",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Runtime triplet vs archive self-sufficiency probe vs template-law audit vs sufficiency witness",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "constitutional core",
    "exemplar bank",
    "challenge suite",
    "selection policy under budget",
    "shrink / reinflate / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("runtime-triplet contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0063" not in traj or "runtime triplet" not in traj:
    raise SystemExit("trajectory map missing runtime-triplet wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0022" not in prompt_text or "constitutional core" not in prompt_text or "challenge suite" not in prompt_text:
    raise SystemExit("prompt pairs missing runtime-triplet ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "runtime triplet" not in runbook or "core-exemplars split" not in runbook:
    raise SystemExit("runbook missing runtime-triplet guidance")

session = SESSION.read_text(encoding="utf-8")
if "Third-pass recursive assimilation" not in session or "core-exemplars" not in session:
    raise SystemExit("foreign-pressure receipt missing third-pass assimilation note")

print("check_runtime_triplet_contract: OK")
