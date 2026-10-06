import json
import pathlib

from current_receipt_lib import build_current_receipt

ROOT = pathlib.Path(__file__).resolve().parents[1]
path = ROOT / "CURRENT-RECEIPT.json"
if not path.exists():
    raise SystemExit("missing CURRENT-RECEIPT.json")
observed = json.loads(path.read_text(encoding="utf-8"))
expected = build_current_receipt(ROOT)
if observed != expected:
    raise SystemExit("CURRENT-RECEIPT.json drifted; run tools/gen_current_receipt.py")
if observed.get("revision") != json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8")).get("revision"):
    raise SystemExit("CURRENT-RECEIPT revision mismatch")
if not all(row.get("tail_matches_receipt") is True for row in observed.get("tail_witnesses", {}).values()):
    raise SystemExit("CURRENT-RECEIPT tail witnesses must match receipt slots")
for forbidden in ["receipt replacement", "witness court", "release notary", "deletion authority"]:
    if forbidden not in observed.get("non_claim", ""):
        raise SystemExit(f"CURRENT-RECEIPT non_claim missing {forbidden}")
print("check_current_receipt_contract: OK")
