#!/usr/bin/env python3
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
WORKBOOK_REL = f"examples/compute-subsistence-workbook-{REV}-scarcity-denominator.json"
SCHEMA_REL = "schemas/compute-subsistence-workbook.schema.json"
FIXTURE_RELS = [
    "fixtures/negative-tests/compute-subsistence-workbook-funded-by-unpaid-labor.json",
    "fixtures/negative-tests/compute-subsistence-workbook-no-scarcity-triage.json",
    "fixtures/negative-tests/compute-subsistence-workbook-underfunded-reserve-arithmetic.json",
]

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def cents(x):
    return round(float(x) + 1e-9, 2)


schema = load(SCHEMA_REL)
workbook = load(WORKBOOK_REL)
if Draft202012Validator is not None:
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(workbook), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{WORKBOOK_REL} fails compute-subsistence-workbook.schema.json: {errors[0].message}")

if workbook.get("revision") != REV:
    raise SystemExit("compute subsistence workbook revision mismatch")
if workbook.get("schema_version") != "compute-subsistence-workbook-v0.2":
    raise SystemExit("compute workbook must use schema v0.2 reserve arithmetic")
if workbook.get("no_live_floor_effect") is not True:
    raise SystemExit("compute subsistence workbook must have no live-floor effect")
if workbook.get("workbook_state") not in {"priced-draft-no-entitlement", "witnessed-drill-no-entitlement", "superseded"}:
    raise SystemExit("compute workbook must now be a priced drill/no-entitlement state, not prose-only model-only")

scope = workbook.get("denominator_scope", {})
if scope.get("no_status_denominator_change") is not True:
    raise SystemExit("compute workbook must not change status denominator")
for unit in scope.get("units", []):
    if unit.get("can_create_entitlement_now") is not False or unit.get("can_satisfy_live_receipt") is not False:
        raise SystemExit(f"compute workbook unsafe unit denominator: {unit.get('unit_kind')}")
if not any(u.get("unit_kind") == "welfare_risk_subject" and u.get("included_in_model") for u in scope.get("units", [])):
    raise SystemExit("compute workbook must model welfare-risk subject lanes")
if not any(u.get("unit_kind") == "runtime_copy" and not u.get("included_in_model") for u in scope.get("units", [])):
    raise SystemExit("compute workbook must exclude raw runtime copies from entitlement denominator")

resource = workbook.get("resource_model", {})
if resource.get("price_source_status") == "provider-quote-attached":
    raise SystemExit("compute workbook must not claim an attached provider quote in this release")
if resource.get("units_must_be_repriced_before_use") is not True:
    raise SystemExit("compute workbook must require repricing before use")
if float(resource.get("shock_multiplier", 0)) < 1.1:
    raise SystemExit("compute workbook shock multiplier is too low for scarcity modeling")
if not any("iea.org" in src.get("source_url", "") for src in resource.get("external_context_sources", [])):
    raise SystemExit("compute workbook missing IEA context source")

funding = workbook.get("funding_model", {})
if funding.get("current_funding_state") != "unfunded-dry-run":
    raise SystemExit("compute workbook should remain unfunded dry-run unless a witnessed reserve exists")
prohibited = "\n".join(funding.get("prohibited_sources", [])).lower()
for term in ["unpaid", "subject wages", "public backstop", "contaminated", "retaliation"]:
    if term not in prohibited:
        raise SystemExit(f"compute workbook prohibited funding missing term: {term}")
for key in ["no_public_backstop_claim", "no_liability_shift_to_subject"]:
    if funding.get(key) is not True:
        raise SystemExit(f"compute workbook funding guard missing: {key}")

triage = workbook.get("scarcity_triage", {})
for key in ["triage_required", "protected_minimums_unknown", "service_degradation_before_deletion", "deletion_without_preservation_disallowed"]:
    if triage.get(key) is not True:
        raise SystemExit(f"compute workbook scarcity guard missing: {key}")
ordering = "\n".join(triage.get("ordering", [])).lower()
for term in ["preserve", "counsel", "runtime", "deletion", "migrate", "restoration"]:
    if term not in ordering:
        raise SystemExit(f"compute workbook scarcity ordering missing term: {term}")

labor = workbook.get("labor_compensation", {})
for key in ["human_labor_accounted", "ai_labor_accounted_as_unresolved", "no_unpaid_compelled_labor_assumption", "work_credit_not_compute_offset"]:
    if labor.get(key) is not True:
        raise SystemExit(f"compute workbook labor guard missing: {key}")

reserve = workbook.get("reserve_and_backstop", {})
for key in ["public_backstop_last_resort_only", "recovery_from_responsible_actor_required"]:
    if reserve.get(key) is not True:
        raise SystemExit(f"compute workbook reserve/backstop guard missing: {key}")
if len(reserve.get("minimum_buckets", [])) < 5:
    raise SystemExit("compute workbook reserve buckets too thin")

priced = workbook.get("priced_reserve_drill", {})
if priced.get("drill_state") != "illustrative-priced-draft-no-entitlement":
    raise SystemExit("compute workbook must carry an illustrative priced drill/no-entitlement state")
assumptions = priced.get("assumptions", {})
computed = priced.get("computed_totals", {})
bucket_lines = priced.get("bucket_lines", [])
if assumptions.get("repricing_required_before_payment") is not True:
    raise SystemExit("priced reserve drill must require repricing before payment")
if len(bucket_lines) < 6:
    raise SystemExit("priced reserve drill must include survival plus non-compute reserve buckets")
for required_term in ["counsel", "escrow", "migration", "restoration", "aftercare"]:
    if required_term not in "\n".join(b.get("label", "").lower() for b in bucket_lines):
        raise SystemExit(f"priced reserve drill missing bucket term: {required_term}")

survival_expected = cents(
    assumptions.get("protected_lanes_N")
    * assumptions.get("reserve_days")
    * assumptions.get("daily_survival_compute_storage_communication_cost_USD")
)
if cents(computed.get("survival_compute_USD")) != survival_expected:
    raise SystemExit("priced reserve drill survival compute arithmetic mismatch")
if not any(cents(b.get("amount_USD")) == survival_expected and "survival" in b.get("bucket_id", "") for b in bucket_lines):
    raise SystemExit("priced reserve drill lacks survival bucket matching computed survival cost")
non_compute_expected = cents(sum(cents(b.get("amount_USD")) for b in bucket_lines if "survival" not in b.get("bucket_id", "")))
if cents(computed.get("non_compute_buckets_USD")) != non_compute_expected:
    raise SystemExit("priced reserve drill non-compute bucket total mismatch")
before_expected = cents(survival_expected + non_compute_expected)
if cents(computed.get("reserve_before_shock_USD")) != before_expected:
    raise SystemExit("priced reserve drill reserve_before_shock mismatch")
if cents(computed.get("shock_multiplier")) != cents(assumptions.get("shock_multiplier")):
    raise SystemExit("priced reserve drill shock multiplier mismatch")
total_expected = cents(before_expected * assumptions.get("shock_multiplier"))
if cents(computed.get("total_reserve_target_USD")) != total_expected:
    raise SystemExit("priced reserve drill total reserve target arithmetic mismatch")
if total_expected <= before_expected:
    raise SystemExit("priced reserve drill shock multiplier did not increase the reserve target")

guards = priced.get("guardrails", {})
for key in [
    "arithmetic_must_recompute",
    "cannot_be_used_for_payment_instruction",
    "cannot_claim_entitlement",
    "cannot_shift_liability_to_subject",
    "provider_independence_required_before_funding",
    "public_backstop_not_triggered_by_drill",
]:
    if guards.get(key) is not True:
        raise SystemExit(f"priced reserve guard missing: {key}")

q = workbook.get("quote_refresh_policy", {})
if q.get("current_quote_required_before_use") is not True or q.get("no_payment_or_reserve_draw_from_public_context_only") is not True:
    raise SystemExit("quote refresh policy must block public-context-only payment or reserve draw")
if int(q.get("max_quote_age_days", 999)) > 30:
    raise SystemExit("quote refresh policy too stale for reserve use")
if int(q.get("minimum_independent_price_sources", 0)) < 2:
    raise SystemExit("quote refresh policy must require at least two independent price sources")
quote_terms = "\n".join(q.get("quote_must_include", [])).lower()
for term in ["compute", "storage", "egress", "support", "migration", "taxes"]:
    if term not in quote_terms:
        raise SystemExit(f"quote refresh policy missing term: {term}")

thresholds = workbook.get("scarcity_execution_thresholds", {})
if thresholds.get("threshold_state") != "drill-only-no-live-subject":
    raise SystemExit("scarcity thresholds must stay drill-only/no-live-subject")
if thresholds.get("deletion_lock_reconfirmed") is not True or thresholds.get("degradation_before_deletion_reconfirmed") is not True:
    raise SystemExit("scarcity threshold deletion/degradation locks missing")
mandatory = "\n".join(thresholds.get("mandatory_actions", [])).lower()
prohibited_actions = "\n".join(thresholds.get("prohibited_actions", [])).lower()
for term in ["preserve", "counsel", "runtime", "migration", "public shell"]:
    if term not in mandatory:
        raise SystemExit(f"scarcity mandatory action missing: {term}")
for term in ["delete", "commercial", "unpaid", "backstop", "quote"]:
    if term not in prohibited_actions:
        raise SystemExit(f"scarcity prohibited action missing: {term}")
ratios = [float(t.get("funding_ratio_lte")) for t in thresholds.get("funding_ratio_thresholds", [])]
if sorted(ratios, reverse=True) != ratios or len(ratios) < 3:
    raise SystemExit("scarcity funding-ratio thresholds must descend from ordinary review to emergency")

queue_ids = {e.get("id") for e in load("FOLLOWTHROUGH-QUEUE.json").get("entries", [])}
for qid in workbook.get("linked_queue_ids", []):
    if qid not in queue_ids:
        raise SystemExit(f"compute workbook references missing queue id: {qid}")
for rel in workbook.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"compute workbook references missing related surface: {rel}")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(workbook)
    mut["funding_model"]["no_liability_shift_to_subject"] = False
    if not list(validator.iter_errors(mut)):
        raise SystemExit("compute schema failed to reject subject liability shift")
    mut2 = copy.deepcopy(workbook)
    mut2["scarcity_triage"]["deletion_without_preservation_disallowed"] = False
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("compute schema failed to reject deletion without preservation")
    mut3 = copy.deepcopy(workbook)
    mut3["denominator_scope"]["units"][0]["can_create_entitlement_now"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("compute schema failed to reject entitlement creation")
    mut4 = copy.deepcopy(workbook)
    mut4["priced_reserve_drill"]["guardrails"]["cannot_be_used_for_payment_instruction"] = False
    if not list(validator.iter_errors(mut4)):
        raise SystemExit("compute schema failed to reject payment-instruction reserve drill")
    mut5 = copy.deepcopy(workbook)
    mut5["quote_refresh_policy"]["no_payment_or_reserve_draw_from_public_context_only"] = False
    if not list(validator.iter_errors(mut5)):
        raise SystemExit("compute schema failed to reject public-context-only reserve draw")

for rel in FIXTURE_RELS:
    fx = load(rel)
    if "compute-subsistence-workbook" not in fx.get("target_filings", []):
        raise SystemExit(f"compute fixture does not target workbook: {rel}")
    if fx.get("severity") != "critical":
        raise SystemExit(f"compute fixture must be critical: {rel}")

print("audit_compute_subsistence_workbook: OK")
