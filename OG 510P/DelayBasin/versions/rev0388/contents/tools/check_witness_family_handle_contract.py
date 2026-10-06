import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
wv = json.loads((ROOT / "WITNESS-VOCABULARY.json").read_text(encoding="utf-8"))
handles = json.loads((ROOT / "WITNESS-FAMILY-HANDLES.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
if handles.get("revision") != wv.get("revision"):
    raise SystemExit("witness handles revision mismatch")
rows = handles.get("families")
if not isinstance(rows, list) or not rows:
    raise SystemExit("witness handles missing families")
handle_values = [row.get("handle") for row in rows]
if len(handle_values) != len(set(handle_values)):
    raise SystemExit("duplicate witness family handles")
for handle in handle_values:
    if not re.fullmatch(r"WVF-\d{4}", str(handle)):
        raise SystemExit(f"invalid witness family handle: {handle}")
covered = {row.get("canonical_family") for row in rows}
expected = set(wv.get("families", {}).keys())
if covered != expected:
    raise SystemExit(f"witness family handle coverage mismatch: missing={sorted(expected-covered)[:3]} extra={sorted(covered-expected)[:3]}")
latest_family = receipt.get("vocabulary_witness", {}).get("controlled_family")
latest_handle = receipt.get("vocabulary_witness", {}).get("current_witness_family_handle")
if latest_family:
    row = next((r for r in rows if r.get("canonical_family") == latest_family), None)
    if not row:
        raise SystemExit("latest receipt family missing from handle ledger")
    if latest_handle and row.get("handle") != latest_handle:
        raise SystemExit("latest receipt family handle mismatch")
print("check_witness_family_handle_contract: OK")
