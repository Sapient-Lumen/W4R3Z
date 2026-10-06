import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/basis-witnesses-expected-head-guards-and-session-honesty-bridges.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"
RECEIPT_CONTRACT = ROOT / "docs/20-constitution/revision-receipt-contract.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG, RECEIPT_CONTRACT, RECEIPT):
    if not path.exists():
        raise SystemExit(f"missing required basis-witness surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Basis witnesses, expected-head guards, and session-honesty bridges",
    "## Practice / observation",
    "## Pressure from neighboring datacubes",
    "## External pressure from adjacent update and provenance practice",
    "## Working synthesis",
    "## Basis witness vs innovation packet vs operational-head register vs revision receipt",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "judged move / continuation claim / active decision surface",
    "expected basis / anchor revision / reviewed head",
    "actual reread basis / loaded surfaces / observed head",
    "session provenance / explicit reread vs copied summary vs nearby-session carry posture",
    "basis state / current vs stale vs partial vs mismatched vs resynced",
    "basis-anchor precision / direct-underlier vs underlier-plus-wrapper vs wrapper-routed vs packet-only posture",
    "basis-omission basis / why stronger underliers were not reread",
    "fail-closed repair / bounded reread vs rerequest vs hold vs recover-resync consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("basis-witness contract missing: " + ", ".join(missing))

if "OQ-0101" not in TRAJ.read_text(encoding="utf-8"):
    raise SystemExit("trajectory map missing OQ-0101 wiring")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0060" not in prompt_text or "expected basis / anchor revision / reviewed head" not in prompt_text or "session provenance / explicit reread vs copied summary vs nearby-session carry posture" not in prompt_text:
    raise SystemExit("prompt pairs missing basis-witness ratchet")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "basis witness" not in runbook or "expected head" not in runbook:
    raise SystemExit("runbook missing basis-witness guidance")
if "CL-0101" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0101")
if "INV-0099" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0099")
if "OQ-0101" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0101")
if "PP-0060" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0060")
contract = RECEIPT_CONTRACT.read_text(encoding="utf-8")
if "basis_witness" not in contract:
    raise SystemExit("revision-receipt contract missing basis_witness")
receipt_text = RECEIPT.read_text(encoding="utf-8")
if '"basis_witness"' not in receipt_text:
    raise SystemExit("revision receipt missing basis_witness")

print("check_basis_witness_contract: OK")
