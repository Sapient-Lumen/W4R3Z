import pathlib

from ledger_coldstore_contract_lib import LedgerColdstoreError, validate_ledger_coldstore

ROOT = pathlib.Path(__file__).resolve().parents[1]

try:
    validate_ledger_coldstore(ROOT)
except LedgerColdstoreError as exc:
    raise SystemExit(str(exc)) from exc

print("check_ledger_coldstore_roundtrip_contract: OK")
