import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
MAP_PATH = ROOT / "examples" / f"research-tail-compaction-map-{REV}.json"
SCHEMA_PATH = ROOT / "schemas" / "research-tail-compaction-map.schema.json"
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
        raise SystemExit(f"{MAP_PATH.relative_to(ROOT)} fails research-tail-compaction-map.schema.json: {errors[0].message}")

actual = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "docs" / "20-world-design").glob("research-*.md"))
assigned = []
compact_now = 0
compacted = 0
for cluster in mp.get("clusters", []):
    recv = cluster.get("receiving_surface")
    if not (ROOT / recv).exists():
        raise SystemExit(f"cluster {cluster.get('cluster_id')} missing receiving_surface: {recv}")
    if cluster.get("action") == "compact-now":
        compact_now += 1
    if cluster.get("action") == "compacted":
        compacted += 1
    if not cluster.get("owner_role"):
        raise SystemExit(f"cluster {cluster.get('cluster_id')} missing owner_role")
    for surface in cluster.get("surfaces", []):
        rel = surface.get("path")
        if not (ROOT / rel).exists():
            raise SystemExit(f"cluster {cluster.get('cluster_id')} references missing research surface: {rel}")
        assigned.append(rel)

if len(assigned) != len(set(assigned)):
    dupes = sorted({p for p in assigned if assigned.count(p) > 1})
    raise SystemExit(f"research compaction assigns surfaces more than once: {dupes}")
if sorted(assigned) != actual:
    missing = sorted(set(actual) - set(assigned))
    extra = sorted(set(assigned) - set(actual))
    raise SystemExit(f"research compaction coverage mismatch: missing={missing}; extra={extra}")
if mp.get("research_surface_count") != len(actual):
    raise SystemExit("research_surface_count is stale")
if compact_now == 0 and compacted == 0:
    raise SystemExit("research compaction map has neither compact-now nor compacted clusters")
if compacted:
    for cluster in mp.get("clusters", []):
        if cluster.get("action") == "compacted" and not any(s.get("current_state") == "folded" for s in cluster.get("surfaces", [])):
            raise SystemExit(f"compacted cluster lacks folded source states: {cluster.get('cluster_id')}")

print("audit_research_tail_compaction: OK")
