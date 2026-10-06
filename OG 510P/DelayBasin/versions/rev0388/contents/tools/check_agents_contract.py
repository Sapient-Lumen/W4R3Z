import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
DOC = ROOT / "docs/10-method/derivative-operator-contracts-low-entropy-reentry-wrappers-and-non-canon-read-first-surfaces.md"
START = ROOT / "START_HERE.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (AGENTS, DOC, START, RUNBOOK, TRAJ, PROMPTS, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required agents surface: {path}")

text = AGENTS.read_text(encoding="utf-8")
required = [
    "# Repo contract for careful DelayBasin passes",
    "This file is a compact derivative wrapper",
    "does not replace",
    "## Read first",
    "## Non-negotiables",
    "## Command posture",
    "## What good changes usually do",
    "reduce entropy without widening doctrine",
    "improve future operator recovery error with a smaller governed wrapper rather than more ambient prose",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("AGENTS contract missing: " + ", ".join(missing))

doc = DOC.read_text(encoding="utf-8")
required_doc = [
    "# Derivative operator contracts, low-entropy reentry wrappers, and non-canon read-first surfaces",
    "## Practice / observation",
    "## Pressure from neighboring datacubes",
    "## External pressure from adjacent startup and reentry practice",
    "## Working synthesis",
    "## Derivative operator contract vs START_HERE vs runbook vs canon",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "read-first surfaces / shortest honest startup path",
    "non-negotiables / what future passes must not silently break",
    "command posture / what checks to prefer before claiming admissibility",
    "good-change shapes / what kinds of revisions are usually worth making",
    "prior relied-on startup path / documented startup promise",
    "successor route / nearest safe reentry path",
    "added burden / cue refresh vs light bridge vs duplicate-reread vs hard-restart consequence",
]
missing = [item for item in required_doc if item not in doc]
if missing:
    raise SystemExit("derivative-operator contract missing: " + ", ".join(missing))

if "AGENTS.md" not in START.read_text(encoding="utf-8"):
    raise SystemExit("START_HERE.md missing AGENTS.md startup wrapper wiring")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "Use `AGENTS.md` as the shortest derivative startup wrapper" not in runbook:
    raise SystemExit("runbook missing AGENTS.md startup wrapper guidance")
if "OQ-0114" not in TRAJ.read_text(encoding="utf-8"):
    raise SystemExit("trajectory map missing OQ-0114 wiring")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0073" not in prompt_text or "read-first surfaces / shortest honest startup path" not in prompt_text or "successor route / nearest safe reentry path" not in prompt_text:
    raise SystemExit("prompt pairs missing derivative-startup-wrapper ratchet")
if "CL-0114" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0114")
if "INV-0112" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0112")
if "OQ-0114" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0114")
if "PP-0073" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0073")

print("check_agents_contract: OK")
