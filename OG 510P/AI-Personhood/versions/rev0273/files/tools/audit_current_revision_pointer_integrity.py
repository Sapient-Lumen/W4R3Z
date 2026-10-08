#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV_NUM = int(REV.replace("rev", ""))
REPORT_REL = f"examples/current-revision-pointer-integrity-report-{REV}.json"
SCHEMA_REL = "schemas/current-revision-pointer-integrity-report.schema.json"

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

report = load_json(REPORT_REL)
schema = load_json(SCHEMA_REL)
if Draft202012Validator is not None:
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(report), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{REPORT_REL} fails current-revision-pointer-integrity-report.schema.json: {errors[0].message}")
if report.get("revision") != REV or report.get("scan_state") != "clean-after-refactor":
    raise SystemExit("current-revision pointer report revision/state mismatch")
if report.get("stale_current_pointer_findings") != []:
    raise SystemExit("current-revision pointer report must be clean after refactor")

# Front-door opening/current blocks should cite only the current revision, except where explicitly historical.
frontdoor = ["README.md", "START_HERE.md", "docs/README.md"]
for rel in frontdoor:
    text = (ROOT / rel).read_text(encoding="utf-8")
    opening = text[:3000]
    if REV not in opening:
        raise SystemExit(f"{rel} opening lacks current revision {REV}")
    stale = sorted({m.group(0) for m in re.finditer(r"rev(0[0-9]{3})", opening) if int(m.group(1)) < REV_NUM})
    if stale:
        raise SystemExit(f"{rel} opening contains stale current pointer(s): {stale}")

status = load_json("SURFACE-STATUS.json")
if status.get("revision") != REV:
    raise SystemExit("SURFACE-STATUS revision mismatch")
# Current status lanes may not point to stale rev artifacts. This intentionally ignores changelog/history.
def walk(obj, path="SURFACE-STATUS"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        for match in re.finditer(r"rev(0[0-9]{3})", obj):
            n = int(match.group(1))
            if n < REV_NUM:
                # Allow explicit historical warnings only if field text says older/historical/legacy.
                lower = obj.lower()
                if not any(tok in lower for tok in ["older", "historical", "legacy", "previous"]):
                    yield (path, match.group(0), obj)
for path, stale, value in walk(status):
    raise SystemExit(f"SURFACE-STATUS current pointer stale at {path}: {stale} in {value!r}")

# Key active artifacts named in status must exist.
def require_ref(rel):
    if isinstance(rel, str) and (rel.startswith("examples/") or rel.startswith("docs/")):
        if not (ROOT / rel).exists():
            raise SystemExit(f"status referenced path missing: {rel}")
for lane in ["contact_layer_status", "formation_layer_status", "queue_layer_status", "resource_layer_status"]:
    for value in status.get(lane, {}).values():
        if isinstance(value, str):
            require_ref(value)

for rel in report.get("scanned_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"current-revision pointer report scanned missing surface: {rel}")
if report.get("frontdoor_current_revision_required") is not True or report.get("no_live_floor_effect") is not True:
    raise SystemExit("current-revision pointer report must be current-rev/no-floor")

print("audit_current_revision_pointer_integrity: OK")
