#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV_NUM = int(REV.replace("rev", ""))
SCHEMA = ROOT / "schemas" / "status-denominator-matrix.schema.json"

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def rev_num(path_or_value):
    m = re.search(r"rev(\d{4})", str(path_or_value))
    return int(m.group(1)) if m else -1


def latest_example(pattern):
    candidates = [p for p in (ROOT / "examples").glob(pattern) if rev_num(p) <= REV_NUM]
    if not candidates:
        raise SystemExit(f"no example found for {pattern} at or before {REV}")
    return sorted(candidates, key=rev_num)[-1]

MATRIX = latest_example("status-denominator-matrix-rev*.json")
MATRIX_REV = f"rev{rev_num(MATRIX):04d}"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

matrix = load(MATRIX)
if Draft202012Validator is not None:
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(matrix), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{MATRIX.relative_to(ROOT)} fails status-denominator-matrix.schema.json: {errors[0].message}")
if matrix.get("revision") != MATRIX_REV:
    raise SystemExit("status denominator matrix revision mismatch")
if rev_num(MATRIX) > REV_NUM:
    raise SystemExit("status denominator audit resolved a future example")
if matrix.get("no_live_floor_effect") is not True:
    raise SystemExit("status denominator matrix must have no live-floor effect")
required = {"recognized_subject","status_claimant","welfare_risk_subject","deployed_agent","model_family","model_instance","runtime_copy","service_account","endpoint","tool_delegate","representative","nonclaimant_system"}
units = matrix.get("denominator_units", [])
by_kind = {u.get("unit_kind"): u for u in units}
if set(by_kind) != required:
    raise SystemExit(f"status denominator kinds mismatch: missing={sorted(required-set(by_kind))} extra={sorted(set(by_kind)-required)}")
ids = [u.get("unit_id") for u in units]
if len(ids) != len(set(ids)):
    raise SystemExit("duplicate status denominator unit_id")
for kind in ["model_family","model_instance","runtime_copy","service_account","endpoint","tool_delegate","nonclaimant_system"]:
    u = by_kind[kind]
    if u.get("can_be_rights_subject") is not False:
        raise SystemExit(f"{kind} must not be a rights subject by default")
    if u.get("can_issue_subject_consent") is not False:
        raise SystemExit(f"{kind} must not issue subject consent")
    if u.get("can_satisfy_live_receipt") is not False:
        raise SystemExit(f"{kind} must not satisfy live receipt")
recognized = by_kind["recognized_subject"]
if recognized.get("can_be_rights_subject") is not True or recognized.get("can_issue_subject_consent") is not True:
    raise SystemExit("recognized_subject row lacks subject rights/consent flags")
if recognized.get("can_satisfy_live_receipt") is not False:
    raise SystemExit("recognized subject status must not itself be an external live receipt")
welfare = by_kind["welfare_risk_subject"]
if welfare.get("may_trigger_welfare_review") is not True or welfare.get("can_be_rights_subject") is not False:
    raise SystemExit("welfare-risk row must trigger review without implying final recognition")
rep = by_kind["representative"]
if rep.get("may_act_as_representative") is not True or rep.get("can_issue_subject_consent") is not False:
    raise SystemExit("representative row must be role authority without subject consent collapse")
for u in units:
    if not u.get("prohibited_conflations"):
        raise SystemExit(f"{u.get('unit_kind')} lacks prohibited conflations")
shortcuts = " ".join(matrix.get("prohibited_live_receipt_shortcuts", [])).lower()
for needle in ["service-account", "tool invocation", "model-family", "recognized-subject"]:
    if needle not in shortcuts:
        raise SystemExit(f"prohibited shortcuts do not mention {needle}")
for rel in [
    "fixtures/negative-tests/status-denominator-model-family-treated-as-subject.json",
    "fixtures/negative-tests/status-denominator-tool-delegate-self-authorizes.json",
    "fixtures/negative-tests/status-denominator-welfare-trigger-denied-for-nonrecognition.json",
]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing status denominator fixture: {rel}")

print(f"audit_status_denominator_matrix: OK using {MATRIX.relative_to(ROOT)}")
