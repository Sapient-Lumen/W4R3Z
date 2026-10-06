import json
import pathlib

from current_receipt_lib import build_current_receipt

ROOT = pathlib.Path(__file__).resolve().parents[1]
out = ROOT / "CURRENT-RECEIPT.json"
out.write_text(json.dumps(build_current_receipt(ROOT), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {out}")
