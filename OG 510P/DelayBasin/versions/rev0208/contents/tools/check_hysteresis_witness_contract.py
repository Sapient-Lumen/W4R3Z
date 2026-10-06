import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/hysteresis-witnesses-rival-histories-and-state-alias-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required hysteresis surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Hysteresis witnesses, rival histories, and state-alias budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Hysteresis witness vs basin fingerprint vs scale-fixing witness vs public memory-kernel claim",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "rival history family or route contrast",
    "matched endpoint / public summary / fixed current packet",
    "future discriminating probe or continuation property",
    "retained lag / hysteresis / alias budget",
    "rollback / quarantine / packet-splitting consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("hysteresis contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0084" not in traj or "hysteresis" not in traj:
    raise SystemExit("trajectory map missing hysteresis wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0043" not in prompt_text or "matched endpoint / public summary / fixed current packet" not in prompt_text or "retained lag / hysteresis / alias budget" not in prompt_text:
    raise SystemExit("prompt pairs missing hysteresis ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "hysteresis witness / rival histories / state-alias budget" not in runbook:
    raise SystemExit("runbook missing hysteresis guidance")

if "CL-0084" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0084")
if "INV-0082" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0082")
if "OQ-0084" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0084")
if "PP-0043" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0043")

print("check_hysteresis_witness_contract: OK")
