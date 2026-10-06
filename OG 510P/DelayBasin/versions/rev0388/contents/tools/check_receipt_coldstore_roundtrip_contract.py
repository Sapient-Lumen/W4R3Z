import pathlib

from receipt_coldstore_contract_lib import ReceiptColdstoreError, validate_receipt_coldstore

ROOT = pathlib.Path(__file__).resolve().parents[1]
try:
    observed = validate_receipt_coldstore(ROOT)
except ReceiptColdstoreError as exc:
    raise SystemExit(f"receipt coldstore roundtrip contract failed: {exc}") from exc
print(
    "check_receipt_coldstore_roundtrip_contract: OK "
    f"({observed['cold_key_count']} keys; net saved {observed['net_plaintext_saved_bytes']} bytes)"
)
