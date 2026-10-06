import pathlib

from receipt_coldstore_contract_lib import receipt_coldstore_canary_results

ROOT = pathlib.Path(__file__).resolve().parents[1]
rows = receipt_coldstore_canary_results(ROOT)
failures = [row for row in rows if row.get("status") != "pass"]
if failures:
    raise SystemExit("receipt coldstore mutation canaries failed: " + repr(failures[:3]))
if len(rows) < 7:
    raise SystemExit("receipt coldstore mutation canaries expected at least 7 rows")
print(f"check_receipt_coldstore_mutation_canaries: OK ({len(rows)} rows)")
