import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "REVISION-RECEIPT.json"
MANIFEST = ROOT / "RELEASE-MANIFEST.json"
TRANSFER = ROOT / "DATACUBE-TRANSFER-LEDGER.json"

for path in (RECEIPT, MANIFEST, TRANSFER):
    if not path.exists():
        raise SystemExit(f"missing import-hygiene surface: {path}")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
transfer = json.loads(TRANSFER.read_text(encoding="utf-8"))

for key in ("summary_highlight", "codename", "created_at", "packaged_bundle_filename", "comparison_witness", "changes"):
    if key not in receipt:
        raise SystemExit(f"receipt missing import-hygiene key: {key}")

for key in ("summary_highlight", "codename", "created_at", "packaged_bundle_filename"):
    if not isinstance(receipt.get(key), str) or not receipt[key]:
        raise SystemExit(f"receipt {key} must be a non-empty string")
if not isinstance(receipt.get("comparison_witness"), dict) or not receipt["comparison_witness"]:
    raise SystemExit("receipt comparison_witness must be a non-empty object")
if not isinstance(receipt.get("changes"), list) or not receipt["changes"]:
    raise SystemExit("receipt changes must be a non-empty list")

bundle = manifest.get("bundle")
if receipt["packaged_bundle_filename"] != bundle:
    raise SystemExit("receipt packaged_bundle_filename must match RELEASE-MANIFEST bundle")
if not re.fullmatch(r"DelayBasin-rev\d{4}-\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2}-[a-z0-9-]+\.zip", bundle or ""):
    raise SystemExit("RELEASE-MANIFEST bundle has invalid naming pattern")

items = transfer.get("items", [])
for item in items:
    if "source_datacubes" not in item:
        continue
    source = set(item.get("source_datacubes", []))
    reviewed = {pkt.get("datacube") for pkt in item.get("reviewed_datacubes", []) if isinstance(pkt, dict) and isinstance(pkt.get("datacube"), str) and not pkt["datacube"].startswith("DelayBasin-")}
    if source != reviewed:
        raise SystemExit(f"transfer item {item.get('id')} source_datacubes must match reviewed_datacubes externals")
    reviewed_surfaces = item.get("reviewed_surfaces", [])
    if reviewed_surfaces:
        for rel in reviewed_surfaces:
            if not isinstance(rel, str) or "/" not in rel:
                raise SystemExit(f"transfer item {item.get('id')} reviewed_surface malformed: {rel}")
            prefix = rel.split("/", 1)[0]
            if prefix not in source:
                raise SystemExit(f"transfer item {item.get('id')} reviewed_surface prefix not in source_datacubes: {rel}")

print("check_import_hygiene_contract: OK")
