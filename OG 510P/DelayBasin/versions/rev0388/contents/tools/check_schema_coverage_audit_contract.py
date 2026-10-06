import json
import pathlib

from schema_coverage_lib import build_schema_coverage_audit

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIT = ROOT / "SCHEMA-COVERAGE-AUDIT.json"
GUIDE = ROOT / "docs/00-meta/schema-coverage-audit.md"
SCHEMA = ROOT / "schemas/schema-coverage-audit.schema.json"
for path in (AUDIT, GUIDE, SCHEMA):
    if not path.exists():
        raise SystemExit(f"missing schema coverage surface: {path.relative_to(ROOT)}")
actual = json.loads(AUDIT.read_text(encoding="utf-8"))
expected = build_schema_coverage_audit(ROOT)
if actual != expected:
    raise SystemExit("SCHEMA-COVERAGE-AUDIT.json drifted from generated schema coverage audit")
counts = actual.get("counts", {})
if counts.get("failures") != 0 or counts.get("unclassified_count") != 0 or actual.get("failures"):
    raise SystemExit("SCHEMA-COVERAGE-AUDIT.json must have zero failures and zero unclassified root JSON surfaces")
if not any(row.get("surface") == "SCHEMA-COVERAGE-AUDIT.json" and row.get("coverage_class") == "schema-backed" for row in actual.get("coverage_rows", [])):
    raise SystemExit("SCHEMA-COVERAGE-AUDIT.json must be schema-backed by its own public schema")
text = GUIDE.read_text(encoding="utf-8")
for needle in ["not a schema-coverage-court", "inventory and validator-routing witness", "does not certify semantic truth"]:
    if needle not in text:
        raise SystemExit(f"schema coverage guide missing {needle}")
print("check_schema_coverage_audit_contract: OK")
