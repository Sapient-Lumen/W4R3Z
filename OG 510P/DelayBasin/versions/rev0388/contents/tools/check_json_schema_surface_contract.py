import pathlib

from schema_conformance_lib import SCHEMA_SURFACES, validate_schema_surface

ROOT = pathlib.Path(__file__).resolve().parents[1]
failures = []
for schema_rel, surface_rel in SCHEMA_SURFACES.items():
    row = validate_schema_surface(ROOT, schema_rel, surface_rel)
    if row.get("status") != "pass":
        failures.extend(row.get("failures", []))
if failures:
    preview = []
    for item in failures[:12]:
        preview.append(f"{item.get('path')} expected {item.get('expected')} observed {item.get('observed')}")
    raise SystemExit("JSON schema conformance failed: " + "; ".join(preview))
print("check_json_schema_surface_contract: OK")
