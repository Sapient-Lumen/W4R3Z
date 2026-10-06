import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
contract = ROOT / "docs/20-constitution/counterfactual-shadow-contract.md"
receipt = ROOT / "REVISION-RECEIPT.json"

if not contract.exists():
    raise SystemExit("missing counterfactual shadow contract")
if not receipt.exists():
    raise SystemExit("missing REVISION-RECEIPT.json")

shadow = json.loads(receipt.read_text(encoding="utf-8")).get("counterfactual_shadow")
if not isinstance(shadow, dict):
    raise SystemExit("counterfactual_shadow missing from receipt")
required = ["status", "nearby_rejected_move", "pivot_surface", "rejection_reason", "still_live"]
for key in required:
    if key not in shadow:
        raise SystemExit(f"counterfactual_shadow missing {key}")
if shadow["status"] == "recorded" and shadow["pivot_surface"]:
    if not (ROOT / shadow["pivot_surface"]).exists():
        raise SystemExit(f"missing pivot_surface target: {shadow['pivot_surface']}")
print("check_counterfactual_shadow_contract: OK")
