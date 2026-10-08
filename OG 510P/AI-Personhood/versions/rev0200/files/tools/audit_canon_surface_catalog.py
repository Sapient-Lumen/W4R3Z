import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CATALOG_PATH = ROOT / "examples" / f"canon-surface-catalog-{REV}.json"
SCHEMA_PATH = ROOT / "schemas" / "canon-surface-catalog.schema.json"

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

catalog = load(CATALOG_PATH)
if Draft202012Validator is not None:
    schema = load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(catalog), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{CATALOG_PATH.relative_to(ROOT)} fails canon-surface-catalog.schema.json: {errors[0].message}")

ids = set()
paths = set()
counts = {"surfaces": 0, "markdown": 0, "schemas": 0, "examples": 0, "fixtures": 0, "tools": 0}
for surface in catalog.get("surfaces", []):
    sid = surface.get("surface_id")
    rel = surface.get("path")
    if sid in ids:
        raise SystemExit(f"duplicate catalog surface_id: {sid}")
    ids.add(sid)
    if rel in paths:
        raise SystemExit(f"duplicate catalog path: {rel}")
    paths.add(rel)
    path = ROOT / rel
    if not path.exists():
        raise SystemExit(f"catalog path missing: {rel}")
    cls = surface.get("surface_class")
    counts["surfaces"] += 1
    if cls in {"meta", "doctrine", "transition"}:
        counts["markdown"] += 1
        text = path.read_text(encoding="utf-8").splitlines()
        if not text or not text[0].startswith("# "):
            raise SystemExit(f"cataloged markdown lacks h1 title: {rel}")
    elif cls == "schema":
        counts["schemas"] += 1
        if not rel.startswith("schemas/"):
            raise SystemExit(f"schema surface outside schemas/: {rel}")
    elif cls == "example":
        counts["examples"] += 1
        if not rel.startswith("examples/"):
            raise SystemExit(f"example surface outside examples/: {rel}")
    elif cls == "fixture":
        counts["fixtures"] += 1
        if not rel.startswith("fixtures/negative-tests/"):
            raise SystemExit(f"fixture surface outside fixtures/negative-tests/: {rel}")
    elif cls == "tool":
        counts["tools"] += 1
        if not rel.startswith("tools/"):
            raise SystemExit(f"tool surface outside tools/: {rel}")
    else:
        raise SystemExit(f"unknown surface class: {cls}")

if catalog.get("counts") != counts:
    raise SystemExit(f"catalog counts mismatch: expected {counts}, got {catalog.get('counts')}")

status = load(ROOT / "SURFACE-STATUS.json")
missing = [p for p in status.get("new_surfaces", []) if p not in paths]
if missing:
    raise SystemExit(f"current release SURFACE-STATUS paths missing from catalog: {missing}")

print("audit_canon_surface_catalog: OK")
