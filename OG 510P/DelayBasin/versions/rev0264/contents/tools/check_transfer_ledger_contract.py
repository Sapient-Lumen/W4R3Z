import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/transfer-ledgers-adopted-non-takes-and-repeat-argument-brakes.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"
CONTRACT = ROOT / "docs/20-constitution/revision-receipt-contract.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
LEDGER = ROOT / "DATACUBE-TRANSFER-LEDGER.json"
VOCAB = ROOT / "WITNESS-VOCABULARY.json"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG, CONTRACT, RECEIPT, LEDGER, VOCAB):
    if not path.exists():
        raise SystemExit(f"missing required transfer-ledger surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Transfer ledgers, adopted non-takes, and repeat-argument brakes",
    "## Practice / observation",
    "## Pressure from neighboring datacubes",
    "## External pressure from adjacent review and decision practice",
    "## Working synthesis",
    "## Transfer ledger vs foreign-pressure witness vs applicability witness vs changelog",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "reviewed datacubes / exact source surfaces",
    "pattern or warning under review",
    "disposition / imported vs supporting-only vs deferred vs rejected vs retired",
    "local gap / why the comparison mattered now",
    "bounded take / compact admitted ratchet if any",
    "explicit non-take / tempting neighboring machinery consciously left out",
    "anchor surfaces / where the admitted result now lives",
    "open transfer question / what remains live after the pass",
    "fail-closed repair / rereview vs narrow-import vs retire-ledger-entry vs recover-resync consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("transfer-ledger contract missing: " + ", ".join(missing))

if "OQ-0112" not in TRAJ.read_text(encoding="utf-8"):
    raise SystemExit("trajectory map missing OQ-0112 wiring")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0071" not in prompt_text or "reviewed datacubes / exact source surfaces" not in prompt_text or "open transfer question / what remains live after the pass" not in prompt_text:
    raise SystemExit("prompt pairs missing transfer-ledger ratchet")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "transfer witness / adopted-non-take memory / repeat-argument brake" not in runbook or "DATACUBE-TRANSFER-LEDGER.json" not in runbook:
    raise SystemExit("runbook missing transfer-ledger guidance")
if "CL-0112" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0112")
if "INV-0110" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0110")
if "OQ-0112" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0112")
if "PP-0071" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0071")
if "transfer_witness" not in CONTRACT.read_text(encoding="utf-8"):
    raise SystemExit("revision receipt contract missing transfer_witness")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
transfer = receipt.get("transfer_witness")
if not isinstance(transfer, dict):
    raise SystemExit("receipt missing transfer_witness object")
if transfer.get("transfer_state") not in {"imported", "supporting-only", "deferred", "rejected", "retired"}:
    raise SystemExit("receipt transfer_witness has invalid transfer_state")

ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
if ledger.get("project") != "DelayBasin":
    raise SystemExit("DATACUBE-TRANSFER-LEDGER project must be DelayBasin")
if ledger.get("revision") != receipt.get("revision"):
    raise SystemExit("DATACUBE-TRANSFER-LEDGER revision must match receipt revision")
items = ledger.get("items")
if not isinstance(items, list) or not items:
    raise SystemExit("DATACUBE-TRANSFER-LEDGER items must be a non-empty list")
seen = set()
items_by_id = {}
for item in items:
    for key in ["id", "title", "state", "reviewed_datacubes", "local_gap", "bounded_take", "explicit_non_take", "anchor_surfaces", "open_transfer_question", "origin_revision", "discharge"]:
        if key not in item:
            raise SystemExit(f"DATACUBE-TRANSFER-LEDGER item missing key: {key}")
    if item["id"] in seen:
        raise SystemExit(f"DATACUBE-TRANSFER-LEDGER duplicate id: {item['id']}")
    seen.add(item["id"])
    items_by_id[item["id"]] = item
    if item["state"] not in {"imported", "supporting-only", "deferred", "rejected", "retired"}:
        raise SystemExit(f"DATACUBE-TRANSFER-LEDGER invalid state: {item['state']}")
    if not isinstance(item["reviewed_datacubes"], list) or not item["reviewed_datacubes"]:
        raise SystemExit(f"DATACUBE-TRANSFER-LEDGER item {item['id']} reviewed_datacubes must be a non-empty list")
    if not isinstance(item["explicit_non_take"], list) or not item["explicit_non_take"]:
        raise SystemExit(f"DATACUBE-TRANSFER-LEDGER item {item['id']} explicit_non_take must be a non-empty list")
    if not isinstance(item["anchor_surfaces"], list) or not item["anchor_surfaces"]:
        raise SystemExit(f"DATACUBE-TRANSFER-LEDGER item {item['id']} anchor_surfaces must be a non-empty list")
    for pkt in item["reviewed_datacubes"]:
        for key in ["datacube", "surfaces", "pattern", "pressure"]:
            if key not in pkt:
                raise SystemExit(f"DATACUBE-TRANSFER-LEDGER reviewed datacube missing key: {key}")
        if not isinstance(pkt["surfaces"], list) or not pkt["surfaces"]:
            raise SystemExit("DATACUBE-TRANSFER-LEDGER reviewed_datacubes surfaces must be a non-empty list")

ref = transfer.get("witness_surface", "")
ref_base, _, ref_frag = ref.partition('#')
if ref_base != "DATACUBE-TRANSFER-LEDGER.json":
    raise SystemExit("receipt transfer_witness witness_surface must point to DATACUBE-TRANSFER-LEDGER.json")
if not ref_frag or ref_frag not in items_by_id:
    raise SystemExit("receipt referenced transfer-ledger entry missing from DATACUBE-TRANSFER-LEDGER.json")
if items_by_id[ref_frag]["origin_revision"] != receipt.get("revision"):
    raise SystemExit("receipt-referenced transfer-ledger item must originate in the current revision")
if len(transfer.get("reviewed_datacubes", [])) < 4:
    raise SystemExit("receipt transfer_witness should name multiple reviewed datacubes for this revision")

vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
assim = vocab.get("families", {}).get("assimilation_state", {})
if "DATACUBE-TRANSFER-LEDGER.json" not in assim.get("surfaces", []):
    raise SystemExit("WITNESS-VOCABULARY assimilation_state must govern DATACUBE-TRANSFER-LEDGER.json")

print("check_transfer_ledger_contract: OK")
