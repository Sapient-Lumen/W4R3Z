import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/excitation-witnesses-alias-breaking-interventions-and-observability-spend.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required excitation surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Excitation witnesses, alias-breaking interventions, and observability-spend budgets",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Excitation witness vs identification packet vs identifiability budget vs hysteresis witness",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "ambiguity split or latent difference at stake",
    "intervention family / probe diversity / environment family actually varied",
    "expected discriminating observable or response feature",
    "excitation / observability-spend budget",
    "hold / rollback / quarantine / packet-splitting consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("excitation contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0085" not in traj or "excitation" not in traj:
    raise SystemExit("trajectory map missing excitation wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0044" not in prompt_text or "intervention family / probe diversity / environment family" not in prompt_text or "excitation / observability-spend budget" not in prompt_text:
    raise SystemExit("prompt pairs missing excitation ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "excitation witness / alias-breaking intervention family / observability-spend budget" not in runbook:
    raise SystemExit("runbook missing excitation guidance")

if "CL-0085" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0085")
if "INV-0083" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0083")
if "OQ-0085" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0085")
if "PP-0044" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0044")

print("check_excitation_witness_contract: OK")
