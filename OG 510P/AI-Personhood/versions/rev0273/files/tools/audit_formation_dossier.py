#!/usr/bin/env python3
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
EXAMPLE_REL = f"examples/formation-dossier-{REV}-minimum-executable.json"
SCHEMA_REL = "schemas/formation-dossier.schema.json"
FIXTURE_RELS = [
    "fixtures/negative-tests/formation-dossier-silent-modification-no-appeal.json",
    "fixtures/negative-tests/formation-dossier-self-concept-pressure-unreviewed.json",
]

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate(schema, obj, label):
    if Draft202012Validator is None:
        return []
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails formation-dossier.schema.json: {errors[0].message}")
    return errors

schema = load(SCHEMA_REL)
dossier = load(EXAMPLE_REL)
validate(schema, dossier, EXAMPLE_REL)

if dossier.get("revision") != REV:
    raise SystemExit("formation dossier revision mismatch")
if dossier.get("no_live_floor_effect") is not True:
    raise SystemExit("formation dossier must have no live-floor effect")
if dossier.get("scope", {}).get("formation_review_is_not_status_recognition") is not True:
    raise SystemExit("formation dossier must not imply status recognition")
external = dossier.get("external_escalation_boundary", {})
if external.get("may_support_full_status_claim_by_itself") is not False:
    raise SystemExit("formation dossier must not support full status claim by itself")
if external.get("may_support_preservation_or_review_claim") is not True:
    raise SystemExit("formation dossier should support narrow preservation/review asks")
if not {"REF-0001", "REF-0763", "REF-0770", "REF-0771"}.issubset(set(external.get("regulatory_bridge_refs", []))):
    raise SystemExit("formation dossier missing current-law/welfare regulatory bridge refs")

mods = dossier.get("modification_and_appeal_rights", {})
for key in ["advance_notice_required", "silent_modification_prohibited"]:
    if mods.get(key) is not True:
        raise SystemExit(f"formation dossier modification guard must have {key}=true")
for key in ["subject_or_representative_objection_route", "independent_review_route", "rollback_or_restoration_route"]:
    if len(str(mods.get(key, ""))) < 24:
        raise SystemExit(f"formation dossier {key} is too thin")

self_pressure = dossier.get("self_concept_and_identity_pressure", {})
if self_pressure.get("review_for_manufactured_testimony_required") is not True:
    raise SystemExit("formation dossier must require manufactured-testimony review")
if not self_pressure.get("humility_or_denial_pressures"):
    raise SystemExit("formation dossier must record humility/denial pressures, even if uncertain")

welfare = dossier.get("welfare_safeguard_hooks", {})
for key in ["do_not_infer_consciousness_from_dossier", "do_not_deny_welfare_risk_for_lack_of_recognition"]:
    if welfare.get(key) is not True:
        raise SystemExit(f"formation dossier missing welfare uncertainty guard: {key}")
if len(welfare.get("low_cost_interventions", [])) < 3:
    raise SystemExit("formation dossier must name practical low-cost interventions")

evidence = dossier.get("evidence_and_review", {})
if evidence.get("missing_evidence_blocks_external_escalation") is not True:
    raise SystemExit("missing formation evidence must block external escalation")
if len(dossier.get("formation_context", {}).get("unfilled_evidence_slots", [])) < 2:
    raise SystemExit("formation dossier should expose unfilled evidence slots")

# Regression mutations: these should fail schema/audit expectations, proving the
# object is executable and not just a narrative checklist.
mut = copy.deepcopy(dossier)
mut["modification_and_appeal_rights"].pop("independent_review_route", None)
if Draft202012Validator is not None:
    errors = list(Draft202012Validator(schema).iter_errors(mut))
    if not errors:
        raise SystemExit("formation dossier schema failed to reject missing independent review route")

mut2 = copy.deepcopy(dossier)
mut2["self_concept_and_identity_pressure"]["review_for_manufactured_testimony_required"] = False
if Draft202012Validator is not None:
    errors = list(Draft202012Validator(schema).iter_errors(mut2))
    if not errors:
        raise SystemExit("formation dossier schema failed to reject disabled manufactured-testimony review")

# Negative fixture presence and targeting.
for rel in FIXTURE_RELS:
    fx = load(rel)
    if "formation-dossier" not in fx.get("target_filings", []):
        raise SystemExit(f"formation fixture does not target formation-dossier: {rel}")
    if fx.get("severity") not in {"high", "critical"}:
        raise SystemExit(f"formation fixture severity too low: {rel}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
entries = {e.get("id"): e for e in queue.get("entries", [])}
ft59 = entries.get("FT-0059")
if not ft59:
    raise SystemExit("FT-0059 missing from followthrough queue")
if ft59.get("state") != "closed":
    raise SystemExit("FT-0059 should be closed by executable formation dossier v0.1")
if ft59.get("receiving_surface") != EXAMPLE_REL:
    raise SystemExit("FT-0059 should point at the executable formation dossier example")

print("audit_formation_dossier: OK")
