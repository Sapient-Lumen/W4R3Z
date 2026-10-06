import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECEIPT = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))
TRANSFER = json.loads((ROOT / "DATACUBE-TRANSFER-LEDGER.json").read_text(encoding="utf-8"))
PRESSURE = json.loads((ROOT / "FOREIGN-PRESSURE-LEDGER.json").read_text(encoding="utf-8"))

fresh = RECEIPT.get("receipt_freshness_witness")
if not isinstance(fresh, dict):
    raise SystemExit("receipt_freshness_witness missing from REVISION-RECEIPT.json")

required = [
    "packaged_bundle_filename",
    "manifest_timestamp_token",
    "receipt_timestamp_token",
    "bundle_stem_suffix_relation",
    "current_import_id",
    "current_pressure_id",
    "change_anchor_surface",
    "freshness_state",
    "repair",
]
for key in required:
    if key not in fresh:
        raise SystemExit(f"receipt_freshness_witness missing key: {key}")

bundle = MANIFEST.get("bundle")
if fresh.get("packaged_bundle_filename") != bundle:
    raise SystemExit("receipt_freshness_witness.packaged_bundle_filename must match RELEASE-MANIFEST bundle")
if RECEIPT.get("packaged_bundle_filename") != bundle:
    raise SystemExit("receipt packaged_bundle_filename must match RELEASE-MANIFEST bundle")

m = re.fullmatch(r"DelayBasin-(rev\d{4})-(\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-([a-z0-9-]+)\.zip", bundle or "")
if not m:
    raise SystemExit("RELEASE-MANIFEST bundle has invalid naming pattern for freshness check")
rev_token, stamp_token, slug = m.groups()
if MANIFEST.get("revision") != rev_token or RECEIPT.get("revision") != rev_token:
    raise SystemExit("receipt/manifest revision must match bundle revision token")
if fresh.get("manifest_timestamp_token") != stamp_token:
    raise SystemExit("receipt_freshness_witness manifest timestamp token must match bundle timestamp token")
if MANIFEST.get("timestamp") != stamp_token:
    raise SystemExit("RELEASE-MANIFEST timestamp must match bundle timestamp token")

created = RECEIPT.get("created_at", "")
cm = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):\d{2}(?:Z|[+-]\d{2}:\d{2})", created)
if not cm:
    raise SystemExit("receipt created_at must be ISO-like with minute precision for freshness check")
receipt_stamp = f"{cm.group(1)}.{cm.group(2)}.{cm.group(3)}.{cm.group(4)}.{cm.group(5)}"
if fresh.get("receipt_timestamp_token") != receipt_stamp:
    raise SystemExit("receipt_freshness_witness receipt_timestamp_token must match created_at minute token")
if receipt_stamp != stamp_token:
    raise SystemExit("receipt created_at minute token must match manifest timestamp token")

summary = RECEIPT.get("summary_highlight")
codename = RECEIPT.get("codename")
if not isinstance(summary, str) or not summary or not isinstance(codename, str) or not codename:
    raise SystemExit("receipt summary_highlight and codename must be non-empty strings")
if not slug.endswith(f"-{summary}-{codename}"):
    raise SystemExit("bundle slug must end with -{summary_highlight}-{codename}")
relation = fresh.get("bundle_stem_suffix_relation", "")
for token in (summary, codename):
    if token not in relation:
        raise SystemExit("receipt_freshness_witness bundle_stem_suffix_relation must name current summary highlight and codename")

latest_transfer = TRANSFER.get("items", [])[-1]["id"]
latest_pressure = PRESSURE.get("items", [])[-1]["id"]
if fresh.get("current_import_id") != latest_transfer:
    raise SystemExit("receipt_freshness_witness current_import_id must match latest transfer id")
if fresh.get("current_pressure_id") != latest_pressure:
    raise SystemExit("receipt_freshness_witness current_pressure_id must match latest foreign-pressure id")
comparison = RECEIPT.get("comparison_witness", {})
if comparison.get("current_import_id") != latest_transfer or comparison.get("current_pressure_id") != latest_pressure:
    raise SystemExit("comparison_witness current ids must match latest transfer / foreign-pressure ids")

anchor = fresh.get("change_anchor_surface")
if not isinstance(anchor, str) or not anchor:
    raise SystemExit("receipt_freshness_witness change_anchor_surface must be a non-empty string")
base = anchor.split('#', 1)[0]
if base and not (ROOT / base).exists():
    raise SystemExit(f"receipt_freshness_witness change anchor surface missing: {anchor}")

if fresh.get("freshness_state") != "current-aligned":
    raise SystemExit("current released revision must keep receipt_freshness_witness in current-aligned state")
if fresh.get("repair") != "ordinary-continuation":
    raise SystemExit("current released revision must keep receipt_freshness_witness repair at ordinary-continuation")

print("check_receipt_freshness_contract: OK")
