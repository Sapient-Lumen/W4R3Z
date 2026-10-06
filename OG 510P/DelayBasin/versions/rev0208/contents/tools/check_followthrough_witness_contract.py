import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/followthrough-witnesses-blocked-outputs-and-explicit-handoffs.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"
CONTRACT = ROOT / "docs/20-constitution/revision-receipt-contract.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
QUEUE = ROOT / "FOLLOWTHROUGH-QUEUE.json"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG, CONTRACT, RECEIPT, QUEUE):
    if not path.exists():
        raise SystemExit(f"missing required followthrough surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Followthrough witnesses, blocked outputs, and explicit handoffs",
    "## Practice / observation",
    "## Pressure from neighboring datacubes",
    "## External pressure from adjacent workflow and issue-tracking practice",
    "## Working synthesis",
    "## Followthrough witness vs hold packet vs scope witness vs status lane",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "blocked or handed-off objective / still-live candidate",
    "current local owner / source surface / current lane",
    "state / local vs queued vs handed-off vs blocked vs expired",
    "blocker or boundary causing non-completion",
    "next proof point / discharge surface / future receipt",
    "receiving surface / follow-up owner / linked issue or queue entry if work moved out",
    "expiry / supersession / reclaim consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("followthrough contract missing: " + ", ".join(missing))

if "OQ-0106" not in TRAJ.read_text(encoding="utf-8"):
    raise SystemExit("trajectory map missing OQ-0106 wiring")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0065" not in prompt_text or "blocked or handed-off objective / still-live candidate" not in prompt_text or "receiving surface / follow-up owner / linked issue or queue entry if work moved out" not in prompt_text:
    raise SystemExit("prompt pairs missing followthrough-witness ratchet")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "followthrough witness" not in runbook or "blocked-output queue" not in runbook:
    raise SystemExit("runbook missing followthrough-witness guidance")
if "CL-0106" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0106")
if "INV-0104" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0104")
if "OQ-0106" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0106")
if "PP-0065" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0065")
if "followthrough_witness" not in CONTRACT.read_text(encoding="utf-8"):
    raise SystemExit("revision receipt contract missing followthrough_witness")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
follow = receipt.get("followthrough_witness")
if not isinstance(follow, dict):
    raise SystemExit("receipt missing followthrough_witness object")
if follow.get("followthrough_state") not in {"local", "queued", "handed-off", "blocked", "expired", "none"}:
    raise SystemExit("receipt followthrough_witness has invalid state")
if follow.get("followthrough_state") != "queued":
    raise SystemExit("shipped receipt must record queued followthrough state for rev0100")
queue = json.loads(QUEUE.read_text(encoding="utf-8"))
if queue.get("project") != "DelayBasin":
    raise SystemExit("FOLLOWTHROUGH-QUEUE project must be DelayBasin")
if queue.get("revision") != receipt.get("revision"):
    raise SystemExit("FOLLOWTHROUGH-QUEUE revision must match receipt revision")
items = queue.get("items")
if not isinstance(items, list) or not items:
    raise SystemExit("FOLLOWTHROUGH-QUEUE items must be a non-empty list")
seen = set()
items_by_id = {}
for item in items:
    for key in ["id", "title", "state", "blocked_output", "boundary", "next_proof_surface", "owner_surface", "origin_revision", "discharge"]:
        if key not in item:
            raise SystemExit(f"FOLLOWTHROUGH-QUEUE item missing key: {key}")
    if item["id"] in seen:
        raise SystemExit(f"FOLLOWTHROUGH-QUEUE duplicate id: {item['id']}")
    seen.add(item["id"])
    items_by_id[item["id"]] = item
    if item["state"] not in {"queued", "handed-off", "blocked", "expired", "deferred"}:
        raise SystemExit(f"FOLLOWTHROUGH-QUEUE invalid state: {item['state']}")
    for field in ("next_proof_surface", "owner_surface"):
        base = item[field].split('#', 1)[0]
        if base and not (ROOT / base).exists():
            raise SystemExit(f"FOLLOWTHROUGH-QUEUE surface missing: {item[field]}")
    origin = item["origin_revision"]
    if not isinstance(origin, str) or not origin.startswith("rev"):
        raise SystemExit(f"FOLLOWTHROUGH-QUEUE item {item['id']} origin_revision must name a revision")

recv = follow.get("receiving_surface", "")
recv_base, _, recv_frag = recv.partition('#')
if recv_base != "FOLLOWTHROUGH-QUEUE.json":
    raise SystemExit("receipt followthrough_witness receiving_surface must point to FOLLOWTHROUGH-QUEUE.json")
if not recv_frag or recv_frag not in items_by_id:
    raise SystemExit("receipt followthrough_witness must point to an existing FOLLOWTHROUGH-QUEUE item")
if items_by_id[recv_frag]["origin_revision"] != receipt.get("revision"):
    raise SystemExit("receipt followthrough_witness must target a FOLLOWTHROUGH-QUEUE item originated by the current revision")

print("check_followthrough_witness_contract: OK")
