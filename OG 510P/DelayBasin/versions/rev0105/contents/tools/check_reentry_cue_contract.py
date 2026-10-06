import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/reentry-cue-witnesses-durable-latest-paths-and-navigation-integrity-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"
CONTRACT = ROOT / "docs/20-constitution/revision-receipt-contract.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
MANIFEST = ROOT / "RELEASE-MANIFEST.json"
LEDGER = ROOT / "SURFACE-STATUS.json"
INDEX = ROOT / "ARCHIVE_INDEX.md"
CHANGELOG = ROOT / "CHANGELOG.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG, CONTRACT, RECEIPT, MANIFEST, LEDGER, INDEX, CHANGELOG):
    if not path.exists():
        raise SystemExit(f"missing required reentry-cue surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Reentry-cue witnesses, durable latest paths, and navigation-integrity budgets",
    "## Practice / observation",
    "## Pressure from neighboring datacubes",
    "## External pressure from adjacent navigation and recordkeeping practice",
    "## Working synthesis",
    "## Reentry-cue witness vs operational head vs status lane vs context pack",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "surface lineage / latest-path family",
    "primary landing surface / first trusted cue",
    "supporting durable cue set / agreeing latest-path surfaces",
    "excluded stale / broken / overwritten / generic-success path family",
    "cue state / fresh-aligned vs stale vs split-brain vs broken-jump vs overwritten",
    "fail-closed repair / refresh-cues vs re-open-primary vs narrow-scope vs recover-resync consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("reentry-cue contract missing: " + ", ".join(missing))

if "OQ-0105" not in TRAJ.read_text(encoding="utf-8"):
    raise SystemExit("trajectory map missing OQ-0105 wiring")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0064" not in prompt_text or "primary landing surface / first trusted cue" not in prompt_text or "supporting durable cue set / agreeing latest-path surfaces" not in prompt_text:
    raise SystemExit("prompt pairs missing reentry-cue ratchet")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "reentry-cue witness" not in runbook or "durable latest-path" not in runbook:
    raise SystemExit("runbook missing reentry-cue guidance")
if "CL-0105" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0105")
if "INV-0103" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0103")
if "OQ-0105" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0105")
if "PP-0064" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0064")
if "reentry_cue_witness" not in CONTRACT.read_text(encoding="utf-8"):
    raise SystemExit("revision receipt contract missing reentry_cue_witness")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

reentry = receipt.get("reentry_cue_witness")
if not isinstance(reentry, dict):
    raise SystemExit("receipt missing reentry_cue_witness object")
expected_supporting = {"SURFACE-STATUS.json", "RELEASE-MANIFEST.json", "ARCHIVE_INDEX.md", "REVISION-RECEIPT.json"}
if reentry.get("primary_landing_surface") != "START_HERE.md":
    raise SystemExit("reentry_cue_witness primary_landing_surface must be START_HERE.md")
if set(reentry.get("supporting_cues", [])) != expected_supporting:
    raise SystemExit("reentry_cue_witness supporting_cues must be the durable latest-path set")
if reentry.get("cue_state") != "fresh-aligned":
    raise SystemExit("shipped receipt must record fresh-aligned reentry cue state")
if reentry.get("repair") != "ordinary-continuation":
    raise SystemExit("shipped receipt must record ordinary-continuation reentry repair posture")

current_rev = manifest.get("revision")
if receipt.get("revision") != current_rev:
    raise SystemExit("receipt and manifest revisions disagree")
if ledger.get("operational_head", {}).get("revision") != current_rev:
    raise SystemExit("SURFACE-STATUS operational_head revision disagrees with manifest")
if ledger.get("citation_head", {}).get("revision") != current_rev:
    raise SystemExit("SURFACE-STATUS citation_head revision disagrees with manifest")
if ledger.get("previous_citation_head", {}).get("revision") != receipt.get("previous_revision"):
    raise SystemExit("SURFACE-STATUS previous_citation_head revision must match receipt previous_revision")
if ledger.get("status_lanes", {}).get("frozen_public_surface") != manifest.get("bundle"):
    raise SystemExit("SURFACE-STATUS frozen_public_surface must match manifest bundle")
if manifest.get("bundle") not in INDEX.read_text(encoding="utf-8"):
    raise SystemExit("ARCHIVE_INDEX missing current bundle row")
if current_rev not in CHANGELOG.read_text(encoding="utf-8"):
    raise SystemExit("CHANGELOG missing current revision header")

print("check_reentry_cue_contract: OK")
