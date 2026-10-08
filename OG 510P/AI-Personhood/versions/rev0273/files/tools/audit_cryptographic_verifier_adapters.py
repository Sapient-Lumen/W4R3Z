#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "cryptographic-verifier-adapter.schema.json"

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover - jsonschema may not be present in tiny runners
    Draft202012Validator = None

from crypto_adapter_lib import verify_adapter_record


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

paths = sorted((ROOT / "examples").glob("cryptographic-verifier-adapter-*.json"))
if len(paths) < 2:
    raise SystemExit("cryptographic verifier adapter suite requires positive and negative controls")

if Draft202012Validator is not None:
    schema = load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
else:
    validator = None

observed = {}
for path in paths:
    record = load(path)
    if validator is not None:
        errors = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{path.relative_to(ROOT)} fails cryptographic-verifier-adapter.schema.json: {errors[0].message}")
    ok, reason = verify_adapter_record(record)
    expected = record.get("verification", {}).get("expected_verification_result")
    if ok is not expected:
        raise SystemExit(f"{path.relative_to(ROOT)} expected verification {expected} but observed {ok}: {reason}")
    if ok and record.get("admission_effect") == "candidate-live-evidence-requires-import-gate" and record.get("test_role") != "live-evidence":
        raise SystemExit(f"{path.relative_to(ROOT)} grants live-evidence admission effect outside live-evidence role")
    observed[path.name] = ok

if not any(observed.values()):
    raise SystemExit("cryptographic verifier adapter suite has no passing positive control")
if not any(v is False for v in observed.values()):
    raise SystemExit("cryptographic verifier adapter suite has no failing negative control")

# A real live import gate cannot rely only on asserted booleans. The schema must
# require an adapter reference when import_mode is actual-live-import, and the
# computed floor must be able to load verified live adapters.
gate_schema = load(ROOT / "schemas" / "actual-receipt-import-gate.schema.json")
text = json.dumps(gate_schema)
if "cryptographic_verifier_adapter_ref" not in text or "cryptographic_adapter_verified" not in text:
    raise SystemExit("actual-receipt-import-gate schema does not require cryptographic adapter fields for live imports")

compute_text = (ROOT / "tools" / "compute_live_receipt_floor.py").read_text(encoding="utf-8")
if "load_verified_live_adapters" not in compute_text or "cryptographic adapter" not in compute_text.lower():
    raise SystemExit("compute_live_receipt_floor.py is not wired to verified cryptographic adapters")

print("audit_cryptographic_verifier_adapters: OK")
