import pathlib

from ledger_coldstore_contract_lib import ledger_coldstore_canary_results

ROOT = pathlib.Path(__file__).resolve().parents[1]
rows = ledger_coldstore_canary_results(ROOT)
failures = [row for row in rows if row.get("status") != "pass"]
if failures:
    raise SystemExit("ledger coldstore mutation canaries failed: " + repr(failures[:3]))
if len(rows) < 7:
    raise SystemExit("ledger coldstore mutation canaries must include baseline plus six defect cases")
print("check_ledger_coldstore_mutation_canaries: OK")
