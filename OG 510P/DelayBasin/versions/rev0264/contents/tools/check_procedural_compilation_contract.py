import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/procedural-compilation-skill-packets-and-declarative-vs-executable-carry.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK):
    if not path.exists():
        raise SystemExit(f"missing required procedural-compilation surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Procedural compilation, skill packets, and declarative-vs-executable carry",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Procedural packet vs declarative source vs episodic support",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "declarative source surface",
    "executable packet or compact operator",
    "activation condition or trigger",
    "expected gain / failure signature",
    "rollback / quarantine consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("procedural-compilation contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0068" not in traj or "procedural-compilation" not in traj:
    raise SystemExit("trajectory map missing procedural-compilation wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0027" not in prompt_text or "declarative source surface" not in prompt_text or "activation condition" not in prompt_text:
    raise SystemExit("prompt pairs missing procedural-compilation ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "procedural compilation" not in runbook or "executable packet or compact operator" not in runbook:
    raise SystemExit("runbook missing procedural-compilation guidance")

print("check_procedural_compilation_contract: OK")
