import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/template-law-audits-family-compression-frontiers-and-anti-ceremony-tests.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
SESSION = ROOT / "docs/40-session/foreign-pressure-2026-03-18-claude-self-sufficiency.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, SESSION):
    if not path.exists():
        raise SystemExit(f"missing required template-law surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Template-law audits, family compression frontiers, and anti-ceremony tests",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Template-law audit vs archive self-sufficiency probe vs foreign-pressure receipt",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "template/operator or family move",
    "smallest family summary / exemplar set",
    "sham or alien-noun test",
    "empirical grounding count / missing probe surface",
    "family-compression frontier",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("template-law contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0062" not in traj or "family law" not in traj:
    raise SystemExit("trajectory map missing template-law audit wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0021" not in prompt_text or "alien-noun test" not in prompt_text or "family-compression frontier" not in prompt_text:
    raise SystemExit("prompt pairs missing template-law audit ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "template-law audit" not in runbook or "anti-ceremony test" not in runbook:
    raise SystemExit("runbook missing template-law audit guidance")

session = SESSION.read_text(encoding="utf-8")
if "Second-pass recursive assimilation" not in session or "generative grammar" not in session:
    raise SystemExit("foreign-pressure receipt missing recursive assimilation note")

print("check_template_law_contract: OK")
