import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/challenge-escrow-rotating-holdouts-and-future-slice-adjudication.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
SESSION = ROOT / "docs/40-session/foreign-pressure-2026-03-18-claude-self-sufficiency.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, SESSION):
    if not path.exists():
        raise SystemExit(f"missing required challenge-escrow surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Challenge escrow, rotating holdouts, and future-slice adjudication",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Challenge escrow vs sham runtime vs runtime triplet vs archive self-sufficiency probe",
    "## Countermodels / probes",
    "## Transformer-facing implication",
    "public challenge family",
    "escrowed or withheld slice",
    "refresh / rotation rule",
    "executable variant or metamorphic family",
    "evaluation horizon or preregistered future slice",
    "promotion / retirement consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("challenge-escrow contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0065" not in traj or "challenge-escrow" not in traj:
    raise SystemExit("trajectory map missing challenge-escrow wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0024" not in prompt_text or "escrowed or withheld slice" not in prompt_text or "refresh / rotation rule" not in prompt_text:
    raise SystemExit("prompt pairs missing challenge-escrow ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "challenge-escrow" not in runbook or "future slice" not in runbook:
    raise SystemExit("runbook missing challenge-escrow guidance")

session = SESSION.read_text(encoding="utf-8")
if "Fifth-pass recursive assimilation" not in session or "escrowed or withheld slice" not in session:
    raise SystemExit("foreign-pressure receipt missing fifth-pass assimilation note")

print("check_challenge_escrow_contract: OK")
