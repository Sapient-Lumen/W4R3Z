import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt_path = ROOT / "REVISION-RECEIPT.json"
contract_path = ROOT / "docs/20-constitution/revision-receipt-contract.md"

if not receipt_path.exists():
    raise SystemExit("missing REVISION-RECEIPT.json")
if not contract_path.exists():
    raise SystemExit("missing docs/20-constitution/revision-receipt-contract.md")

receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
required = [
    "project",
    "revision",
    "previous_revision",
    "summary",
    "move_classes",
    "canon_additions",
    "quarantine_additions",
    "refs_used",
    "checks_passed",
    "touched_surfaces",
    "packaged_release",
    "counterfactual_shadow",
]
for key in required:
    if key not in receipt:
        raise SystemExit(f"receipt missing key: {key}")

if receipt.get("project") != "DelayBasin":
    raise SystemExit("receipt project must be DelayBasin")
if not str(receipt.get("revision", "")).startswith("rev"):
    raise SystemExit("receipt revision missing rev####")
if not isinstance(receipt["move_classes"], list) or not receipt["move_classes"]:
    raise SystemExit("receipt move_classes must be a non-empty list")
if "make lint" not in receipt.get("checks_passed", []):
    raise SystemExit("receipt must record make lint")
if not isinstance(receipt.get("packaged_release"), bool):
    raise SystemExit("receipt packaged_release must be boolean")
move_registry_text = (ROOT / "docs/20-constitution/move-registry.md").read_text(encoding="utf-8")
certified_moves = set()
for line in move_registry_text.splitlines():
    line = line.strip()
    if line.startswith("- `MV-") and "—" in line:
        certified_moves.add(line.split("`")[1])
for move in receipt.get("move_classes", []):
    if move not in certified_moves:
        raise SystemExit(f"receipt move not in move registry: {move}")
for rel in receipt.get("touched_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"receipt touched surface missing: {rel}")

shadow = receipt.get("counterfactual_shadow")
if not isinstance(shadow, dict):
    raise SystemExit("receipt counterfactual_shadow must be an object")
for key in ["status", "nearby_rejected_move", "pivot_surface", "rejection_reason", "still_live"]:
    if key not in shadow:
        raise SystemExit(f"receipt counterfactual_shadow missing key: {key}")
if shadow["status"] not in {"recorded", "none"}:
    raise SystemExit("receipt counterfactual_shadow.status must be 'recorded' or 'none'")
if shadow["status"] == "recorded":
    if not shadow["nearby_rejected_move"] or not shadow["rejection_reason"]:
        raise SystemExit("recorded counterfactual_shadow requires nearby_rejected_move and rejection_reason")
    if not (ROOT / shadow["pivot_surface"]).exists():
        raise SystemExit(f"counterfactual_shadow pivot_surface missing: {shadow['pivot_surface']}")
    still_live = shadow["still_live"]
    base = still_live.split('#', 1)[0]
    if base and not (ROOT / base).exists():
        raise SystemExit(f"counterfactual_shadow still_live base path missing: {base}")

print("check_revision_receipt_contract: OK")
