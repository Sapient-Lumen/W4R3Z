import json
import pathlib

from schema_conformance_lib import build_schema_conformance_audit

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIT = ROOT / "SCHEMA-CONFORMANCE-AUDIT.json"
GUIDE = ROOT / "docs/00-meta/schema-conformance-audit.md"
SCHEMA = ROOT / "schemas/schema-conformance-audit.schema.json"
for path in (AUDIT, GUIDE, SCHEMA):
    if not path.exists():
        raise SystemExit(f"missing schema conformance surface: {path.relative_to(ROOT)}")
actual = json.loads(AUDIT.read_text(encoding="utf-8"))
expected = build_schema_conformance_audit(ROOT)
if actual != expected:
    raise SystemExit("SCHEMA-CONFORMANCE-AUDIT.json drifted from generated schema conformance audit")
if actual.get("counts", {}).get("failures") != 0 or actual.get("failures"):
    raise SystemExit("SCHEMA-CONFORMANCE-AUDIT.json must have zero failures")
text = GUIDE.read_text(encoding="utf-8")
for needle in ["not a schema-conformance-court", "public-shape hygiene witness", "does not certify semantic truth"]:
    if needle not in text:
        raise SystemExit(f"schema conformance guide missing {needle}")
for row in actual.get("schema_surfaces", []):
    if row.get("status") != "pass":
        raise SystemExit(f"schema conformance row failing: {row.get('schema')} -> {row.get('surface')}")
print("check_schema_conformance_audit_contract: OK")
