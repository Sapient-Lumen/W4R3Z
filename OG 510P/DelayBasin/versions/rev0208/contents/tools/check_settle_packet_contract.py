import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/settle-packets-prune-witnesses-and-earned-singularity.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK):
    if not path.exists():
        raise SystemExit(f"missing required settle-packet surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Settle packets, prune witnesses, and earned singularity",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Settle packets vs rival-set packets vs stopping packets vs contradiction packets",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "ambiguity or rivalry class",
    "candidate winner or merge target",
    "losing or merged branch family",
    "settle witness or prune evidence",
    "reopen trigger or unresolved residue",
    "prune / merge / defer consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("settle-packet contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0076" not in traj or "settle packet / prune witness / earned singularity" not in traj:
    raise SystemExit("trajectory map missing settle-packet wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0035" not in prompt_text or "settle witness or prune evidence" not in prompt_text or "prune / merge / defer consequence" not in prompt_text:
    raise SystemExit("prompt pairs missing settle-packet ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "settle packet" not in runbook or "settle witness or prune evidence" not in runbook:
    raise SystemExit("runbook missing settle-packet guidance")

print("check_settle_packet_contract: OK")
