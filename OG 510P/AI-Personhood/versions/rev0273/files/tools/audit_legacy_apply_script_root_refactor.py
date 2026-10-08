#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REPORT_REL = f"examples/legacy-apply-script-root-refactor-manifest-{REV}.json"
SCHEMA_REL = "schemas/legacy-apply-script-root-refactor-manifest.schema.json"
FIXTURE_REL = "fixtures/negative-tests/legacy-apply-root-script-treated-as-current-replay.json"

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha_bytes(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def validate(schema, obj, label):
    if Draft202012Validator is None:
        return
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails legacy-apply-script-root-refactor-manifest.schema.json: {errors[0].message}")

schema = load_json(SCHEMA_REL)
report = load_json(REPORT_REL)
validate(schema, report, REPORT_REL)

if report.get("revision") != REV:
    raise SystemExit("legacy apply root refactor revision mismatch")
if report.get("no_live_floor_effect") is not True:
    raise SystemExit("legacy apply root refactor must be no-floor")
if report.get("refactor_state") != "legacy-apply-scripts-moved-out-of-root-archival-only":
    raise SystemExit("legacy apply root refactor state mismatch")

root_scripts = sorted(ROOT.glob("apply_rev*.py"))
if root_scripts:
    raise SystemExit(f"legacy apply root refactor failed; root scripts remain: {[p.name for p in root_scripts]}")
legacy_dir = ROOT / report.get("legacy_directory", "")
if not legacy_dir.exists():
    raise SystemExit("legacy apply script directory missing")
actual = sorted(legacy_dir.glob("apply_rev*.py"))
if report.get("moved_script_count") != len(actual):
    raise SystemExit("legacy apply script count mismatch")
items = report.get("legacy_scripts", [])
if len(items) != len(actual):
    raise SystemExit("legacy apply script manifest count mismatch")
paths = {item.get("rel_path"): item for item in items}
for path in actual:
    rel = path.relative_to(ROOT).as_posix()
    item = paths.get(rel)
    if not item:
        raise SystemExit(f"legacy apply script missing from manifest: {rel}")
    if item.get("filename") != path.name:
        raise SystemExit(f"legacy apply script filename mismatch: {rel}")
    if item.get("sha256") != sha_bytes(rel):
        raise SystemExit(f"legacy apply script sha mismatch: {rel}")
    if item.get("size_bytes") != path.stat().st_size:
        raise SystemExit(f"legacy apply script size mismatch: {rel}")
    if item.get("archival_only") is not True:
        raise SystemExit(f"legacy apply script must be archival only: {rel}")

supported = " ".join(report.get("current_replay_path", {}).get("supported_commands", [])).lower()
for term in ["make context-pack", "make manifest", "make lint", "make package-release"]:
    if term not in supported:
        raise SystemExit(f"legacy apply current replay path missing: {term}")
if report.get("current_replay_path", {}).get("apply_scripts_are_current_replay_path") is not False:
    raise SystemExit("legacy apply scripts must not be current replay path")
checks = report.get("root_cleanup_checks", {})
if checks.get("root_contains_apply_rev_scripts") is not False:
    raise SystemExit("legacy apply root cleanup must record no root apply scripts")
if checks.get("legacy_scripts_preserved_with_hashes") is not True:
    raise SystemExit("legacy apply scripts must be preserved with hashes")
for key in ["root_script_absence_may_be_treated_as_missing_current_replay", "refactor_changes_no_send_or_floor_state"]:
    if checks.get(key) is not False:
        raise SystemExit(f"legacy apply root cleanup overclaims: {key}")
for key, value in report.get("downstream_locks", {}).items():
    if value is not False:
        raise SystemExit(f"legacy apply downstream lock must be false: {key}")
for rel in report.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"legacy apply related surface missing: {rel}")

fixture = load_json(FIXTURE_REL)
if "legacy-apply-script-root-refactor-manifest" not in fixture.get("target_filings", []):
    raise SystemExit("legacy apply fixture does not target manifest")
if fixture.get("severity") != "medium":
    raise SystemExit("legacy apply fixture must be medium")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(report)
    mut["current_replay_path"]["apply_scripts_are_current_replay_path"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("schema failed to reject legacy scripts as current replay")
    mut2 = copy.deepcopy(report)
    mut2["root_cleanup_checks"]["root_script_absence_may_be_treated_as_missing_current_replay"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("schema failed to reject root absence as current replay failure")
    mut3 = copy.deepcopy(report)
    mut3["downstream_locks"]["may_change_live_floor_state"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("schema failed to reject no-send/floor state change")

print("audit_legacy_apply_script_root_refactor: OK")
