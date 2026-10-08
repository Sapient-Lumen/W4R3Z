import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
MAP_PATH = ROOT / "examples" / f"doctrine-dependency-map-{REV}.json"
SCHEMA_PATH = ROOT / "schemas" / "doctrine-dependency-map.schema.json"

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

mp = load(MAP_PATH)
if Draft202012Validator is not None:
    schema = load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(mp), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{MAP_PATH.relative_to(ROOT)} fails doctrine-dependency-map.schema.json: {errors[0].message}")

paths = {}
for surface in mp.get("surfaces", []):
    sid = surface.get("surface_id")
    rel = surface.get("path")
    if sid in paths:
        raise SystemExit(f"duplicate dependency-map surface_id: {sid}")
    if not (ROOT / rel).exists():
        raise SystemExit(f"dependency-map path missing: {rel}")
    paths[sid] = rel
    for key in ["depends_on", "overlaps_with", "supersedes"]:
        for dep in surface.get(key, []):
            if not (ROOT / dep).exists():
                raise SystemExit(f"dependency-map {rel} references missing {key} path: {dep}")

status = load(ROOT / "SURFACE-STATUS.json")
markdown_current = [p for p in status.get("new_surfaces", []) if p.endswith(".md")]
mapped = {s.get("path") for s in mp.get("surfaces", [])}
missing = [p for p in markdown_current if p not in mapped]
if missing:
    raise SystemExit(f"current release markdown surfaces missing from dependency map: {missing}")

# Check cycles among current mapped paths using only dependencies that are also mapped.
graph = {s["path"]: [d for d in s.get("depends_on", []) if d in mapped] for s in mp.get("surfaces", [])}
visiting = set()
visited = set()
def dfs(node, stack):
    if node in visiting:
        raise SystemExit("dependency cycle: " + " -> ".join(stack + [node]))
    if node in visited:
        return
    visiting.add(node)
    for nxt in graph.get(node, []):
        dfs(nxt, stack + [node])
    visiting.remove(node)
    visited.add(node)
for node in graph:
    dfs(node, [])

print("audit_doctrine_dependency_map: OK")
