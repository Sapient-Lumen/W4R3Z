import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/operational-heads-citation-heads-and-frozen-public-surfaces.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required operational-head surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Operational heads, citation heads, and frozen public surfaces",
    "## Practice / observation",
    "## Pressure from neighboring datacubes",
    "## External pressure from adjacent recordkeeping practice",
    "## Working synthesis",
    "## Operational head vs citation head vs revision receipt vs hold packet",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "surface lineage / family / stable id namespace",
    "current operational head / live working tip",
    "current citation head / frozen reference tip or explicit absence",
    "current state class / working vs hold vs released vs frozen",
    "durable status surface / register / ledger where that state lives",
    "promotion or freeze gate / admission witness that moved authority",
    "supersession edge / previous frozen head if any",
    "reopen / rollback / citation-warning consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("operational-head contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0100" not in traj or "operational-head register" not in traj:
    raise SystemExit("trajectory map missing operational-head wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0059" not in prompt_text or "current citation head / frozen reference tip or explicit absence" not in prompt_text or "surface lineage / family / stable id namespace" not in prompt_text:
    raise SystemExit("prompt pairs missing operational-head ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "operational-head register / citation-head witness / frozen-public-surface packet" not in runbook:
    raise SystemExit("runbook missing operational-head guidance")

if "CL-0100" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0100")
if "INV-0098" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0098")
if "OQ-0100" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0100")
if "PP-0059" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0059")

print("check_operational_head_contract: OK")
