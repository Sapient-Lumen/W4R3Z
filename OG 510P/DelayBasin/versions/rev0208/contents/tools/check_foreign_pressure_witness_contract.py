import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/foreign-pressure-witnesses-import-lineage-and-bounded-assimilation.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"
CONTRACT = ROOT / "docs/20-constitution/revision-receipt-contract.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
LEDGER = ROOT / "FOREIGN-PRESSURE-LEDGER.json"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG, CONTRACT, RECEIPT, LEDGER):
    if not path.exists():
        raise SystemExit(f"missing required foreign-pressure surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Foreign-pressure witnesses, import lineages, and bounded assimilation",
    "## Practice / observation",
    "## Pressure from neighboring datacubes",
    "## External pressure from adjacent provenance and derivation practice",
    "## Working synthesis",
    "## Foreign-pressure witness vs assumption witness vs counterfactual shadow vs bibliography",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "source datacubes / exact source surfaces",
    "extracted pressure / specific lesson or warning",
    "concrete local gap / why DelayBasin needed this now",
    "bounded take / compact imported ratchet",
    "explicit non-take / tempting neighboring machinery consciously left out",
    "assimilation state / imported vs supporting-only vs deferred vs rejected vs retired",
    "fail-closed repair / narrow-import vs defer-import vs quarantine-or-retire vs hold vs recover-resync consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("foreign-pressure contract missing: " + ", ".join(missing))

if "OQ-0108" not in TRAJ.read_text(encoding="utf-8"):
    raise SystemExit("trajectory map missing OQ-0108 wiring")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0067" not in prompt_text or "source datacubes / exact source surfaces" not in prompt_text or "bounded take / compact imported ratchet" not in prompt_text:
    raise SystemExit("prompt pairs missing foreign-pressure ratchet")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "foreign-pressure witness" not in runbook or "FOREIGN-PRESSURE-LEDGER.json" not in runbook:
    raise SystemExit("runbook missing foreign-pressure guidance")
if "CL-0108" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0108")
if "INV-0106" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0106")
if "OQ-0108" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0108")
if "PP-0067" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0067")
if "foreign_pressure_witness" not in CONTRACT.read_text(encoding="utf-8"):
    raise SystemExit("revision receipt contract missing foreign_pressure_witness")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
foreign = receipt.get("foreign_pressure_witness")
if not isinstance(foreign, dict):
    raise SystemExit("receipt missing foreign_pressure_witness object")
if foreign.get("assimilation_state") != "imported":
    raise SystemExit("shipped receipt must record imported foreign-pressure state for rev0102")
if foreign.get("repair") != "ordinary-continuation":
    raise SystemExit("shipped receipt must record ordinary-continuation foreign-pressure repair posture")

ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
if ledger.get("project") != "DelayBasin":
    raise SystemExit("FOREIGN-PRESSURE-LEDGER project must be DelayBasin")
if ledger.get("revision") != receipt.get("revision"):
    raise SystemExit("FOREIGN-PRESSURE-LEDGER revision must match receipt revision")
items = ledger.get("items")
if not isinstance(items, list) or not items:
    raise SystemExit("FOREIGN-PRESSURE-LEDGER items must be a non-empty list")
seen = set()
items_by_id = {}
for item in items:
    for key in ["id", "title", "state", "source_packets", "local_gap", "bounded_take", "explicit_non_take", "origin_revision", "discharge"]:
        if key not in item:
            raise SystemExit(f"FOREIGN-PRESSURE-LEDGER item missing key: {key}")
    if item["id"] in seen:
        raise SystemExit(f"FOREIGN-PRESSURE-LEDGER duplicate id: {item['id']}")
    seen.add(item["id"])
    items_by_id[item["id"]] = item
    items_by_id[item["id"]] = item
    if item["state"] not in {"imported", "supporting-only", "deferred", "rejected", "retired"}:
        raise SystemExit(f"FOREIGN-PRESSURE-LEDGER invalid state: {item['state']}")
    if not isinstance(item["source_packets"], list) or not item["source_packets"]:
        raise SystemExit(f"FOREIGN-PRESSURE-LEDGER item {item['id']} source_packets must be a non-empty list")
    for pkt in item["source_packets"]:
        for key in ["datacube", "surfaces", "pressure"]:
            if key not in pkt:
                raise SystemExit(f"FOREIGN-PRESSURE-LEDGER source packet missing key: {key}")
        if not isinstance(pkt["surfaces"], list) or not pkt["surfaces"]:
            raise SystemExit("FOREIGN-PRESSURE-LEDGER source packet surfaces must be a non-empty list")
    if not isinstance(item["explicit_non_take"], list) or not item["explicit_non_take"]:
        raise SystemExit(f"FOREIGN-PRESSURE-LEDGER item {item['id']} explicit_non_take must be a non-empty list")

surface = foreign.get("witness_surface", "")
base, _, frag = surface.partition('#')
if base != "FOREIGN-PRESSURE-LEDGER.json":
    raise SystemExit("receipt foreign_pressure_witness witness_surface must point to FOREIGN-PRESSURE-LEDGER.json")
if not frag or frag not in items_by_id:
    raise SystemExit("receipt foreign_pressure_witness must point to an existing FOREIGN-PRESSURE-LEDGER item")
if len(foreign.get("source_packets", [])) < 3:
    raise SystemExit("receipt foreign_pressure_witness should name multiple source packets for this cross-datacube import")

ref = foreign.get("witness_surface", "")
ref_base, _, ref_frag = ref.partition('#')
if ref_base != "FOREIGN-PRESSURE-LEDGER.json":
    raise SystemExit("receipt foreign_pressure_witness witness_surface must point to FOREIGN-PRESSURE-LEDGER.json")
if not ref_frag or ref_frag not in items_by_id:
    raise SystemExit("receipt referenced ledger entry missing from FOREIGN-PRESSURE-LEDGER.json")
if items_by_id[ref_frag]["origin_revision"] != receipt.get("revision"):
    raise SystemExit("receipt-referenced FOREIGN-PRESSURE-LEDGER item must originate in the current revision")

print("check_foreign_pressure_witness_contract: OK")
