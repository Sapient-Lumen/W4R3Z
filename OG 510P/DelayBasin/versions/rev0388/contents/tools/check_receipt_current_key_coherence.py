import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "RELEASE-MANIFEST.json"
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
transfers = json.loads((ROOT / "DATACUBE-TRANSFER-LEDGER.json").read_text(encoding="utf-8"))["items"]
pressures = json.loads((ROOT / "FOREIGN-PRESSURE-LEDGER.json").read_text(encoding="utf-8"))["items"]
latest_import = transfers[-1]["id"]
latest_pressure = pressures[-1]["id"]

expected_revision = manifest.get("revision")
expected_bundle = manifest.get("bundle")
expected_slug = manifest.get("slug")
expected_stamp = manifest.get("timestamp")
for key, expected in (
    ("revision", expected_revision),
    ("bundle", expected_bundle),
    ("packaged_bundle_filename", expected_bundle),
    ("slug", expected_slug),
    ("stamp", expected_stamp),
):
    if receipt.get(key) != expected:
        raise SystemExit(f"receipt {key} {receipt.get(key)!r} != manifest {expected!r}")
if receipt.get("packaged_release") is not True:
    raise SystemExit("receipt packaged_release must be true for packaged current head")
if receipt.get("current_import_id") != latest_import:
    raise SystemExit(f"receipt current_import_id {receipt.get('current_import_id')} != latest {latest_import}")
if receipt.get("current_pressure_id") != latest_pressure:
    raise SystemExit(f"receipt current_pressure_id {receipt.get('current_pressure_id')} != latest {latest_pressure}")
violations = []

def walk(obj, path="receipt", historical=False):
    if isinstance(obj, dict):
        now_historical = historical or obj.get("historical_witness") is True
        for key, value in obj.items():
            child = f"{path}.{key}"
            if not now_historical and key == "current_import_id" and value != latest_import:
                violations.append(f"{child}={value!r} expected {latest_import!r}")
            if not now_historical and key == "current_pressure_id" and value != latest_pressure:
                violations.append(f"{child}={value!r} expected {latest_pressure!r}")
            walk(value, child, now_historical)
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            walk(value, f"{path}[{idx}]", historical)

walk(receipt)
if violations:
    raise SystemExit("stale current-key fields in receipt: " + "; ".join(violations[:12]))
print("check_receipt_current_key_coherence: OK")
