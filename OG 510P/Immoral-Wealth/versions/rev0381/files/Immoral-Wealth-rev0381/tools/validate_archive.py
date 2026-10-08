#!/usr/bin/env python3
from pathlib import Path
import json, re, sys, hashlib, ast, collections

ROOT = Path(__file__).resolve().parents[1]
errors = []
warnings = []
CURRENT_REVISION = 'rev0381'
sys.dont_write_bytecode = True

def fail(msg): errors.append(msg)
def warn(msg): warnings.append(msg)

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"JSON parse failed: {path.relative_to(ROOT)}: {e}")
        return None

def source_ids():
    data = load_json(ROOT/"SOURCES.json") or {}
    ids = {s.get("id") for s in data.get("sources", [])}
    return {i for i in ids if i}


def iter_source_ids_in_json(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "source_ids" and isinstance(v, list):
                for sid in v:
                    yield sid
            else:
                yield from iter_source_ids_in_json(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_source_ids_in_json(item)

def check_json_source_ids():
    ids = source_ids()
    for p in ROOT.rglob("*.json"):
        if ".git" in p.parts: continue
        data = load_json(p)
        if data is None: continue
        for sid in iter_source_ids_in_json(data):
            if not isinstance(sid, str) or sid not in ids:
                fail(f"Missing JSON source ref {sid!r} in {p.relative_to(ROOT)}")

def check_json():
    for p in ROOT.rglob("*.json"):
        if ".git" in p.parts: continue
        load_json(p)

def check_scoreboards():
    schema_path = ROOT/"docs/20-program/scoreboard-schema.json"
    schema = load_json(schema_path)
    if not schema: return
    try:
        import jsonschema
        Validator = jsonschema.validators.validator_for(schema)
        Validator.check_schema(schema)
        validator = Validator(schema)
    except Exception as e:
        warn(f"jsonschema unavailable or schema invalid; skipped schema validation: {e}")
        return
    for p in sorted((ROOT/"cases").glob("*scoreboard.json")):
        data = load_json(p)
        if data is None: continue
        try:
            validator.validate(data)
        except Exception as e:
            fail(f"Scoreboard schema failed: {p.relative_to(ROOT)}: {e}")

def check_source_refs():
    ids = source_ids()
    for p in ROOT.rglob("*.md"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        for sid in re.findall(r"\[S(\d{2,3})\]", text):
            full = "S"+sid
            if full not in ids:
                fail(f"Missing source ref {full} in {p.relative_to(ROOT)}")

def check_links():
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for p in ROOT.rglob("*.md"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        for target in link_re.findall(text):
            if target.startswith(("http://","https://","mailto:")): continue
            path = target.split("#",1)[0]
            if not path: continue
            # Ignore URI-looking bare references
            if ":" in path and not path.startswith("."): continue
            dest = (p.parent / path).resolve()
            try:
                dest.relative_to(ROOT.resolve())
            except Exception:
                fail(f"Link escapes archive: {p.relative_to(ROOT)} -> {target}")
                continue
            if not dest.exists():
                fail(f"Broken link: {p.relative_to(ROOT)} -> {target}")

def check_frontmatter():
    for p in ROOT.rglob("*.md"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        if not text.startswith("---\n"):
            warn(f"No frontmatter: {p.relative_to(ROOT)}")
            continue
        end = text.find("\n---", 4)
        if end == -1:
            fail(f"Unclosed frontmatter: {p.relative_to(ROOT)}")



def check_source_sequence():
    data = load_json(ROOT/"SOURCES.json") or {}
    nums = []
    for s in data.get("sources", []):
        sid = s.get("id", "")
        if not re.match(r"^S[0-9]{2,3}$", sid):
            fail(f"Bad source id format: {sid}")
            continue
        nums.append(int(sid[1:]))
    if nums and nums != list(range(1, max(nums)+1)):
        fail("Source ids are not contiguous from S01")


def check_rev0308_measurement_scoreboards():
    # Cases introduced in rev0308 must include at least one measurement/visibility field.
    required_cases = [
        "canada-top-tail-measurement-rev0308-scoreboard.json",
        "united-kingdom-wealth-statistics-reliability-rev0308-scoreboard.json",
        "uk-offshore-property-transparency-rev0308-scoreboard.json",
        "macro-consistent-wealth-accounts-rev0308-scoreboard.json",
    ]
    measurement_keys = {"source_family", "survey_accreditation_status", "top_tail_adjustment_required", "top_tail_audit_required", "national_accounts_reconciliation", "beneficial_ownership_verification", "offshore_property_visibility"}
    for name in required_cases:
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0308 measurement scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        fields = set((data.get("fields") or {}).keys())
        if not (fields & measurement_keys):
            fail(f"Rev0308 measurement scoreboard lacks measurement fields: cases/{name}")



def check_rev0309_enforcement_scoreboards():
    required_cases = [
        "united-states-tax-enforcement-rev0309-scoreboard.json",
        "united-states-beneficial-ownership-reversal-rev0309-scoreboard.json",
        "eu-beneficial-ownership-legitimate-interest-rev0309-scoreboard.json",
        "global-tax-cooperation-and-offshore-rails-rev0309-scoreboard.json",
        "procurement-public-value-leakage-rev0309-scoreboard.json",
    ]
    enforcement_keys = {"enforceability_and_remedy_access", "high_wealth_audit_capacity", "beneficial_ownership_scope_stability", "international_tax_cooperation", "public_procurement_capture", "asset_recovery_capacity", "legal_attack_surface"}
    for name in required_cases:
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0309 enforcement scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        fields = set((data.get("fields") or {}).keys())
        if not (fields & enforcement_keys):
            fail(f"Rev0309 enforcement scoreboard lacks enforcement fields: cases/{name}")


def check_rev0310_democratic_power_scoreboards():
    required_cases = [
        "united-states-democratic-wealth-power-rev0310-scoreboard.json",
        "united-kingdom-political-finance-rev0310-scoreboard.json",
        "eu-media-pluralism-agenda-power-rev0310-scoreboard.json",
        "local-land-use-homeowner-veto-rev0310-scoreboard.json",
    ]
    democratic_keys = {"democratic_nondomination_gate", "large_donor_dependence", "independent_expenditure_exposure", "dark_money_or_nontransparent_spending", "party_access_market", "foreign_or_cross_border_political_finance_risk", "media_ownership_transparency", "media_market_plurality", "local_land_use_veto", "homeowner_outsider_exclusion", "reform_countermobilization_risk"}
    for name in required_cases:
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0310 democratic-power scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        fields = set((data.get("fields") or {}).keys())
        if not (fields & democratic_keys):
            fail(f"Rev0310 democratic-power scoreboard lacks democratic-power fields: cases/{name}")



def check_rev0311_jurisdictional_mobility_scoreboards():
    required_cases = [
        "eu-investor-citizenship-residence-rev0311-scoreboard.json",
        "united-kingdom-non-dom-transition-rev0311-scoreboard.json",
        "global-high-wealth-migration-exit-threat-rev0311-scoreboard.json",
        "gulf-migrant-public-wealth-perimeter-rev0311-scoreboard.json",
        "remittance-dependence-transnational-family-burden-rev0311-scoreboard.json",
    ]
    mobility_keys = {"jurisdictional_mobility_gate", "high_wealth_exit_threat", "residence_citizenship_by_investment_risk", "tax_residency_enforcement", "exit_tax_and_deemed_disposal_rails", "capital_flow_or_asset_flight_risk", "crs_aeoi_information_exchange_coverage", "migrant_claimant_perimeter_exclusion", "portable_social_rights_for_migrants", "remittance_or_transnational_support_burden", "remittance_fee_leakage", "non_dom_or_preferential_newcomer_tax_regime"}
    for name in required_cases:
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0311 jurisdictional-mobility scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        fields = set((data.get("fields") or {}).keys())
        if not (fields & mobility_keys):
            fail(f"Rev0311 jurisdictional-mobility scoreboard lacks mobility fields: cases/{name}")



def check_rev0312_workplace_power_scoreboards():
    required_cases = [
        "united-states-union-density-wealth-formation-rev0312-scoreboard.json",
        "united-states-noncompete-worker-mobility-rev0312-scoreboard.json",
        "united-states-fissured-workplace-joint-employer-rev0312-scoreboard.json",
        "eu-platform-work-employment-presumption-rev0312-scoreboard.json",
        "employee-ownership-esop-wealth-formation-rev0312-scoreboard.json",
    ]
    workplace_keys = {"workplace_power_gate", "collective_bargaining_coverage", "union_density_and_access", "noncompete_or_mobility_restraint", "job_switching_claimability", "misclassification_risk", "platform_algorithmic_management", "joint_employer_responsibility", "fissured_workplace_accountability", "temporary_contingent_work_security", "worker_ownership_breadth", "profit_sharing_or_broad_based_equity", "employee_ownership_liquidity_and_concentration_risk", "worker_voice_in_firm_governance", "wage_theft_and_pay_remedy_access"}
    for name in required_cases:
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0312 workplace-power scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        fields = set((data.get("fields") or {}).keys())
        if not (fields & workplace_keys):
            fail(f"Rev0312 workplace-power scoreboard lacks workplace-power fields: cases/{name}")



def check_rev0313_place_public_finance_scoreboards():
    required_cases = [
        "united-states-school-finance-property-tax-rev0313-scoreboard.json",
        "united-states-municipal-infrastructure-fiscal-capacity-rev0313-scoreboard.json",
        "united-states-utility-burden-disconnection-rev0313-scoreboard.json",
        "local-disaster-fiscal-capacity-rev0313-scoreboard.json",
        "transportation-access-and-place-affordability-rev0313-scoreboard.json",
    ]
    place_keys = {"place_public_finance_gate", "school_finance_equalization", "property_tax_base_fragmentation", "school_facility_capital_gap", "municipal_fiscal_capacity", "infrastructure_backlog", "water_wastewater_need_pressure", "utility_affordability_burden", "utility_disconnection_protection", "transportation_access_cost_burden", "disaster_recovery_fiscal_bridge", "climate_municipal_bond_risk", "intergovernmental_transfer_reliability", "capital_grant_absorption_capacity", "user_fee_special_assessment_regressivity"}
    for name in required_cases:
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0313 place-public-finance scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        fields = set((data.get("fields") or {}).keys())
        if not (fields & place_keys):
            fail(f"Rev0313 place-public-finance scoreboard lacks place-public-finance fields: cases/{name}")



def check_rev0314_household_market_extraction_scoreboards():
    required_cases = [
        "united-states-consumer-finance-fee-drain-rev0314-scoreboard.json",
        "united-states-auto-finance-repossession-rev0314-scoreboard.json",
        "bnpl-earned-wage-credit-visibility-rev0314-scoreboard.json",
        "united-states-childcare-cost-time-wealth-rev0314-scoreboard.json",
        "oecd-long-term-care-asset-spenddown-rev0314-scoreboard.json",
    ]
    household_keys = {"household_market_extraction_gate", "consumer_credit_fee_drag", "credit_card_late_fee_exposure", "overdraft_nsf_fee_drag", "high_cost_small_dollar_credit", "unbanked_underbanked_cost_burden", "auto_finance_negative_equity", "auto_repossession_mobility_loss", "bnpl_fragmented_credit_visibility", "earned_wage_access_fee_visibility", "junk_fee_or_drip_pricing", "negative_option_subscription_trap", "childcare_cost_time_wealth_drag", "childcare_labor_force_interruption", "long_term_care_asset_spenddown", "informal_care_family_burden", "household_market_remedy_access"}
    for name in required_cases:
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0314 household-market-extraction scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        fields = set((data.get("fields") or {}).keys())
        if not (fields & household_keys):
            fail(f"Rev0314 household-market-extraction scoreboard lacks household-market-extraction fields: cases/{name}")



def check_rev0315_score_mediated_exclusion_scoreboards():
    required_cases = [
        "united-states-credit-reporting-medical-debt-rev0315-scoreboard.json",
        "tenant-screening-eviction-records-rev0315-scoreboard.json",
        "insurance-scoring-surveillance-pricing-rev0315-scoreboard.json",
        "data-broker-fraud-identity-lockout-rev0315-scoreboard.json",
        "algorithmic-public-benefit-eligibility-rev0315-scoreboard.json",
    ]
    score_keys = {"score_mediated_exclusion_gate", "credit_reporting_accuracy_and_dispute_access", "credit_invisibility_or_unscored_status", "medical_debt_credit_file_risk", "specialty_consumer_report_coverage", "tenant_screening_record_accuracy", "eviction_record_shadow_penalty", "algorithmic_tenant_denial_explainability", "employment_background_algorithmic_score", "insurance_credit_score_use", "insurance_external_data_algorithmic_pricing", "surveillance_pricing_personalization", "data_broker_fraud_flag_lockout", "identity_verification_access_and_error_correction", "public_benefit_algorithmic_eligibility", "automated_decision_notice_explanation_appeal", "adverse_action_reason_specificity", "record_suppression_clean_slate_rails", "model_audit_disparate_impact_testing", "score_repair_claimability"}
    for name in required_cases:
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0315 score-mediated-exclusion scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        fields = set((data.get("fields") or {}).keys())
        if not (fields & score_keys):
            fail(f"Rev0315 score-mediated-exclusion scoreboard lacks score-mediated fields: cases/{name}")



def check_rev0316_fresh_start_scoreboards():
    required_cases = [
        "united-states-bankruptcy-fresh-start-rev0316-scoreboard.json",
        "united-states-garnishment-bank-levy-rev0316-scoreboard.json",
        "debt-collection-default-judgment-rev0316-scoreboard.json",
        "eviction-foreclosure-record-recovery-rev0316-scoreboard.json",
        "reentry-clean-slate-collateral-consequences-rev0316-scoreboard.json",
    ]
    fresh_keys = {"fresh_start_capacity_gate", "bankruptcy_access_and_discharge", "exemption_floor_adequacy", "exemption_self_execution", "wage_garnishment_protection", "bank_account_levy_protection", "judgment_lien_and_property_seizure", "debt_collection_litigation_due_process", "default_judgment_repair", "post_judgment_interest_and_renewal", "foreclosure_loss_mitigation", "eviction_foreclosure_record_sealing", "record_afterlife_housing_entry", "criminal_record_clearance", "collateral_consequence_repair", "protected_recovery_floor", "vendor_record_suppression_after_clearance"}
    for name in required_cases:
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0316 fresh-start scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        fields = set((data.get("fields") or {}).keys())
        if not (fields & fresh_keys):
            fail(f"Rev0316 fresh-start scoreboard lacks fresh-start fields: cases/{name}")


def check_rev0317_intergenerational_transfer_scoreboards():
    required_cases = [
        "united-states-inheritance-lifetime-transfer-rev0317-scoreboard.json",
        "united-states-estate-tax-trust-perimeter-rev0317-scoreboard.json",
        "heirs-property-probate-title-finality-rev0317-scoreboard.json",
        "medicaid-estate-recovery-home-equity-rev0317-scoreboard.json",
        "guardianship-elder-exploitation-fiduciary-rev0317-scoreboard.json",
        "divorce-child-support-family-wealth-rev0317-scoreboard.json",
    ]
    intergen_keys = {"intergenerational_transfer_gate", "inheritance_lifetime_transfer_access", "early_lifetime_gift_gate", "estate_tax_gift_gst_perimeter", "dynasty_trust_rule_against_perpetuities", "trust_beneficial_ownership_visibility", "probate_access_cost_timing", "intestacy_title_finality", "heirs_property_partition_protection", "medicaid_estate_recovery_scope", "long_term_care_home_equity_spenddown", "caregiver_inheritance_recognition", "guardianship_due_process", "fiduciary_accounting_oversight", "elder_financial_exploitation_response", "divorce_property_division_claimability", "retirement_asset_division_qdro_access", "child_support_pass_through_to_family", "child_support_debt_burden"}
    for name in required_cases:
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0317 intergenerational-transfer scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        fields = set((data.get("fields") or {}).keys())
        if not (fields & intergen_keys):
            fail(f"Rev0317 intergenerational-transfer scoreboard lacks Gate 19 fields: cases/{name}")



def check_rev0318_public_balance_sheet_scoreboards():
    required_cases = [
        "united-states-federal-fiscal-interest-risk-rev0318-scoreboard.json",
        "social-security-medicare-claim-security-rev0318-scoreboard.json",
        "us-state-local-public-pension-risk-rev0318-scoreboard.json",
        "deposit-insurance-bank-backstop-rev0318-scoreboard.json",
        "housing-finance-guarantee-fha-gse-rev0318-scoreboard.json",
        "federal-reserve-balance-sheet-quasi-fiscal-rev0318-scoreboard.json",
        "norway-gpfg-public-asset-governance-rev0318-scoreboard.json",
    ]
    public_balance_keys = {"public_balance_sheet_gate", "public_debt_interest_crowdout", "primary_balance_sustainability", "fiscal_risk_register_quality", "contingent_liability_disclosure", "implicit_bailout_expectation", "sovereign_backstop_upside_recovery", "deposit_insurance_prefunding", "financial_stability_backstop_governance", "social_insurance_trust_fund_adequacy", "benefit_claim_security", "public_pension_funding_risk", "pension_assumption_stress_testing", "state_local_intergovernmental_burden_shift", "federal_credit_program_subsidy_transparency", "loan_guarantee_loss_visibility", "housing_finance_guarantee_exposure", "student_loan_public_balance_sheet_exposure", "sovereign_wealth_fund_rule_bound_governance", "public_asset_distributional_claim", "resource_revenue_smoothing_rule", "public_asset_raiding_firewall", "central_bank_quasi_fiscal_loss_visibility", "debt_service_distributional_incidence", "tax_expenditure_vs_direct_spending_transparency", "crisis_backstop_conditionality", "countercyclical_capacity_for_lower_half", "generational_incidence"}
    for name in required_cases:
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0318 public-balance-sheet scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        fields = set((data.get("fields") or {}).keys())
        if not (fields & public_balance_keys):
            fail(f"Rev0318 public-balance-sheet scoreboard lacks Gate 20 fields: cases/{name}")



def current_gate_keys():
    schema = load_json(ROOT/"docs/20-program/scoreboard-schema.json") or {}
    return (((schema.get("properties") or {}).get("gate_inventory") or {}).get("required") or [])


def check_duplicate_frontmatter_blocks():
    # A valid markdown file may use horizontal rules, but it should not contain a
    # second YAML-looking block with a status key after the top frontmatter.
    for p in ROOT.rglob("*.md"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        if not text.startswith("---\n"):
            continue
        end = text.find("\n---", 4)
        if end == -1:
            continue
        rest = text[end+4:]
        if re.search(r"(?m)^---\s*\nstatus:\s*", rest):
            fail(f"Embedded duplicate frontmatter block: {p.relative_to(ROOT)}")


def check_current_release_surfaces():
    contract = load_json(ROOT/"docs/00-meta/live-surface-contract.json") or {}
    if contract.get("revision_current") != CURRENT_REVISION:
        fail("live-surface-contract revision_current mismatch")
    expected_files = contract.get("required_current_release_files") or []
    if not expected_files:
        fail("live-surface-contract has no required_current_release_files")
    for rel in expected_files:
        path = ROOT/rel
        if not path.exists():
            fail(f"Missing contracted current-release surface: {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if CURRENT_REVISION not in text:
            fail(f"Current release {CURRENT_REVISION} not visible in {rel}")
    version = (ROOT/"VERSION").read_text(encoding="utf-8", errors="ignore").strip()
    if version != CURRENT_REVISION:
        fail(f"VERSION mismatch: expected {CURRENT_REVISION}, found {version}")
    receipt = load_json(ROOT/"REVISION-RECEIPT.json") or {}
    if receipt.get("revision") != CURRENT_REVISION:
        fail("REVISION-RECEIPT.json revision mismatch")
    if receipt.get("source_count") != (load_json(ROOT/"SOURCES.json") or {}).get("source_count"):
        fail("REVISION-RECEIPT source_count mismatch")


def check_live_operator_surface_parity():
    try:
        from validate_live_surfaces import validate_live_surfaces
        for issue in validate_live_surfaces(ROOT, CURRENT_REVISION):
            fail(issue)
    except Exception as exc:
        fail(f"Live-surface parity validator failed to run: {exc}")

def check_source_metadata_completeness():
    data = load_json(ROOT/"SOURCES.json") or {}
    srcs = data.get("sources", [])
    if data.get("source_count") != len(srcs):
        fail("SOURCES.json source_count does not equal number of sources")
    if data.get("revision_current") != CURRENT_REVISION:
        fail("SOURCES.json revision_current mismatch")
    if data.get("current_revision") != CURRENT_REVISION:
        fail("SOURCES.json current_revision mismatch")
    if srcs:
        expected_range = f"{srcs[0].get('id')}-{srcs[-1].get('id')}"
        if data.get("source_range") != expected_range:
            fail(f"SOURCES.json source_range {data.get('source_range')!r} != {expected_range!r}")
    required = {"id", "title", "org", "date", "url", "why_it_matters", "accessed", "source_type", "evidence_role", "refresh_due", "used_by_cases", "used_by_fields"}
    for s in srcs:
        sid = s.get("id", "<missing-id>")
        for key in required:
            if key not in s:
                fail(f"Source {sid} missing metadata key {key}")
            elif s.get(key) in (None, ""):
                fail(f"Source {sid} has empty metadata key {key}")
        if not isinstance(s.get("used_by_cases"), list):
            fail(f"Source {sid} used_by_cases must be a list")
        if not isinstance(s.get("used_by_fields"), list):
            fail(f"Source {sid} used_by_fields must be a list")
        if str(s.get("date", "")).startswith("accessed"):
            fail(f"Source {sid} mixes access date into publication date")
        date_val = str(s.get("date", "")).strip()
        if not re.fullmatch(r"undated|\d{4}(?:-\d{2}(?:-\d{2})?)?", date_val):
            fail(f"Source {sid} has ambiguous publication date {date_val!r}; use undated, YYYY, YYYY-MM, or YYYY-MM-DD and move access/update ranges to date_notes")
        if ";" in date_val or re.search(r"\d{4}\s*[-–]\s*\d{4}", date_val):
            fail(f"Source {sid} keeps update/range text in date field {date_val!r}")
    coverage = data.get("coverage_map", {})
    if not isinstance(coverage, dict):
        fail("SOURCES.json coverage_map must be an object")
        return
    for key, val in coverage.items():
        if not isinstance(val, dict):
            fail(f"coverage_map.{key} must be an object with why and sources")
            continue
        if not isinstance(val.get("why"), str) or not val.get("why"):
            fail(f"coverage_map.{key} missing nonempty why")
        if not isinstance(val.get("sources"), list):
            fail(f"coverage_map.{key} sources must be a list")


def check_gate_inventory_coverage():
    gates = current_gate_keys()
    if len(gates) != 20:
        fail(f"Gate inventory schema should require 20 gates; found {len(gates)}")
    allowed = {"passed", "watch", "blocked", "missing", "not_applicable"}
    for p in sorted((ROOT/"cases").glob("*scoreboard.json")):
        data = load_json(p) or {}
        inv = data.get("gate_inventory")
        if not isinstance(inv, dict):
            fail(f"Missing gate_inventory: {p.relative_to(ROOT)}")
            continue
        for g in gates:
            item = inv.get(g)
            if not isinstance(item, dict):
                fail(f"Missing gate inventory key {g}: {p.relative_to(ROOT)}")
                continue
            status = item.get("status")
            if status not in allowed:
                fail(f"Bad gate inventory status {status!r} for {g}: {p.relative_to(ROOT)}")


def is_gate20_scoreboard(data):
    fields = data.get("fields") or {}
    cert = data.get("certification_gates") or {}
    text = " ".join([str(data.get("case_type", "")), str(data.get("calibration_class", "")), " ".join(fields.keys()), " ".join(cert.keys())])
    gate20_markers = [
        "public_balance_sheet", "sovereign_backstop", "contingent_liability", "deposit_insurance", "central_bank_quasi", "tax_expenditure", "private_credit_nonbank", "stablecoin", "student_loan_public_balance_sheet", "ai_data_center", "healthcare_financialization", "critical_minerals", "industrial_policy_public_upside", "gate_20"
    ]
    return any(m in text for m in gate20_markers)


def check_gate20_register_presence():
    subgate_keys = {"20A_debt_interest_capacity", "20B_claim_security", "20C_contingent_liabilities_guarantees", "20D_crisis_backstop_governance", "20E_public_upside_recovery", "20F_central_bank_quasi_fiscal_visibility", "20G_public_asset_sovereign_wealth_governance", "20H_generational_intergovernmental_incidence"}
    for p in sorted((ROOT/"cases").glob("*scoreboard.json")):
        data = load_json(p) or {}
        if not is_gate20_scoreboard(data):
            continue
        sub = data.get("gate_20_subgates")
        reg = data.get("public_balance_sheet_register")
        waterfall = data.get("seniority_waterfall")
        if not isinstance(sub, dict) or not subgate_keys.issubset(sub.keys()):
            fail(f"Gate 20 scoreboard missing full gate_20_subgates: {p.relative_to(ROOT)}")
        if not isinstance(reg, list) or not reg:
            fail(f"Gate 20 scoreboard missing nonempty public_balance_sheet_register: {p.relative_to(ROOT)}")
        else:
            req = {"exposure_name", "legal_authority", "claimant_perimeter", "beneficiaries", "maximum_exposure", "expected_loss", "stress_scenario", "correlation_with_household_need", "funding_source", "loss_sharing", "public_upside_recovery", "ordinary_claimant_protection", "sunset_or_review", "evidence_quality", "source_ids"}
            for i, item in enumerate(reg):
                if not isinstance(item, dict):
                    fail(f"Gate 20 register item {i} not object: {p.relative_to(ROOT)}")
                    continue
                for key in req:
                    if key not in item:
                        fail(f"Gate 20 register item missing {key}: {p.relative_to(ROOT)}")
        if not isinstance(waterfall, list) or not waterfall:
            fail(f"Gate 20 scoreboard missing nonempty seniority_waterfall: {p.relative_to(ROOT)}")


def check_case_ledger_coverage():
    ledger = load_json(ROOT/"cases/CASE_LEDGER.json") or {}
    rows = ledger.get("cases", [])
    if ledger.get("revision_current") != CURRENT_REVISION:
        fail("CASE_LEDGER revision_current mismatch")
    score_ids = set()
    for p in (ROOT/"cases").glob("*scoreboard.json"):
        data = load_json(p) or {}
        if data.get("case_id"):
            score_ids.add(data["case_id"])
    row_ids = {r.get("case_id") for r in rows if isinstance(r, dict)}
    if ledger.get("case_count") != len(rows):
        fail("CASE_LEDGER case_count does not equal number of rows")
    if len(rows) != len(score_ids):
        fail(f"CASE_LEDGER row count {len(rows)} does not match scoreboard count {len(score_ids)}")
    for cid in sorted(score_ids - row_ids):
        fail(f"Scoreboard case_id missing from CASE_LEDGER: {cid}")
    case_memos = list((ROOT/"cases").glob("*case.md"))
    if len(case_memos) != len(score_ids):
        fail(f"Case memo count {len(case_memos)} does not match scoreboard count {len(score_ids)}")


def check_scoreboard_spec_schema_sync():
    spec_path = ROOT/"docs/20-program/scoreboard-spec.md"
    schema = load_json(ROOT/"docs/20-program/scoreboard-schema.json") or {}
    actual = len((((schema.get("properties") or {}).get("fields") or {}).get("properties") or {}))
    text = spec_path.read_text(encoding="utf-8", errors="ignore") if spec_path.exists() else ""
    m = re.search(r"schema_field_count:\s*(\d+)", text)
    if not m:
        fail("scoreboard-spec.md missing schema_field_count")
    elif int(m.group(1)) != actual:
        fail(f"scoreboard-spec.md schema_field_count {m.group(1)} != schema field count {actual}")


def check_gate20_generic_proof_debt_repetition():
    seen = {}
    for p in sorted((ROOT/"cases").glob("*scoreboard.json")):
        data = load_json(p) or {}
        if not is_gate20_scoreboard(data):
            continue
        proof = tuple(str(x).strip().lower() for x in data.get("proof_debt", []) if str(x).strip())
        if not proof:
            fail(f"Gate 20 scoreboard has empty proof_debt: {p.relative_to(ROOT)}")
            continue
        seen.setdefault(proof, []).append(str(p.relative_to(ROOT)))
    for proof, paths in seen.items():
        if len(paths) >= 3:
            fail(f"Generic repeated Gate 20 proof_debt across {len(paths)} scoreboards: {paths[:5]}")



def check_case_scoreboard_pairing():
    scoreboard_bases = set()
    memo_bases = set()
    for p in (ROOT/"cases").glob("*scoreboard.json"):
        base = p.name[:-len("-scoreboard.json")]
        scoreboard_bases.add(base)
        # Historical case_id values sometimes already include "-case". Pairing is by filename base.
        expected = ROOT/"cases"/(base + "-case.md")
        if not expected.exists():
            fail(f"Scoreboard lacks matching case memo by filename base: {p.relative_to(ROOT)} -> {expected.relative_to(ROOT)}")
    for p in (ROOT/"cases").glob("*case.md"):
        base = p.name[:-len("-case.md")]
        memo_bases.add(base)
        expected = ROOT/"cases"/(base + "-scoreboard.json")
        if not expected.exists():
            fail(f"Case memo lacks matching scoreboard by filename base: {p.relative_to(ROOT)} -> {expected.relative_to(ROOT)}")
    if scoreboard_bases != memo_bases:
        for base in sorted(scoreboard_bases - memo_bases):
            fail(f"Scoreboard base missing memo base: {base}")
        for base in sorted(memo_bases - scoreboard_bases):
            fail(f"Memo base missing scoreboard base: {base}")



def check_case_memo_scoreboard_refresh_sync():
    """Prevent a memo from claiming a slower refresh cadence than its paired scoreboard."""
    date_re = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for memo in sorted((ROOT/"cases").glob("*case.md")):
        base = memo.name[:-len("-case.md")]
        score = ROOT/"cases"/(base + "-scoreboard.json")
        if not score.exists():
            continue
        fm = extract_frontmatter(memo.read_text(encoding="utf-8", errors="ignore")) or ""
        m = re.search(r"^source_refresh_due:\s*([^\n#]+)", fm, re.M)
        if not m:
            fail(f"Case memo missing source_refresh_due: {memo.relative_to(ROOT)}")
            continue
        memo_due = m.group(1).strip().strip('"\'')
        data = load_json(score) or {}
        score_due = str(data.get("source_refresh_due", "")).strip()
        if memo_due != score_due:
            fail(f"Case memo/scoreboard source_refresh_due mismatch: {memo.relative_to(ROOT)} has {memo_due}, {score.relative_to(ROOT)} has {score_due}")
        for label, val in [("memo", memo_due), ("scoreboard", score_due)]:
            if val and not date_re.match(val):
                fail(f"Bad {label} source_refresh_due format for {base}: {val}")

def check_no_cache_artifacts():
    for p in ROOT.rglob("*"):
        if "__pycache__" in p.parts or p.suffix == ".pyc":
            fail(f"Cache/build artifact present: {p.relative_to(ROOT)}")



def check_source_use_register_sync():
    reg = load_json(ROOT/"docs/00-meta/source-use-register.json") or {}
    if reg.get("revision_current") != CURRENT_REVISION:
        fail("source-use-register revision_current mismatch")
    sources = load_json(ROOT/"SOURCES.json") or {}
    ids = {s.get("id") for s in sources.get("sources", [])}
    rows = reg.get("sources", [])
    row_ids = {r.get("source_id") for r in rows if isinstance(r, dict)}
    if ids != row_ids:
        fail("source-use-register source set does not match SOURCES.json")
    recomputed_cases = {sid: set() for sid in ids}
    recomputed_fields = {sid: set() for sid in ids}
    def walk(obj, prefix=""):
        if isinstance(obj, dict):
            if isinstance(obj.get("source_ids"), list):
                yield prefix.rstrip("."), obj.get("source_ids"), obj
            for k, v in obj.items():
                if k != "source_ids":
                    yield from walk(v, prefix + k + ".")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                yield from walk(v, prefix + str(i) + ".")
    base_to_case_id = {}
    for p in (ROOT/"cases").glob("*scoreboard.json"):
        data = load_json(p) or {}
        cid = data.get("case_id")
        base = p.name[:-len("-scoreboard.json")]
        base_to_case_id[base] = cid
        for path, sids, container in walk(data):
            claim = path
            if path.startswith("fields."):
                claim = path.split(".")[1]
            elif path.startswith("gate_inventory.") or path.startswith("gate_20_subgates.") or path.startswith("certification_gates."):
                claim = path.split(".")[1]
            for sid in sids:
                if sid in ids:
                    recomputed_cases[sid].add(cid)
                    recomputed_fields[sid].add(claim)
    # rev0340: case-memo narrative citations are evidence lineage too.
    for p in (ROOT/"cases").glob("*case.md"):
        base = p.name[:-len("-case.md")]
        cid = base_to_case_id.get(base, base)
        text = p.read_text(encoding="utf-8", errors="ignore")
        for n in re.findall(r"\[S(\d{2,3})\]", text):
            sid = "S" + n
            if sid in ids:
                recomputed_cases[sid].add(cid)
                recomputed_fields[sid].add("case_memo")
    for s in sources.get("sources", []):
        sid = s.get("id")
        # Retained aliases must have no active case payload or memo usage.
        if s.get("retained_alias"):
            if recomputed_cases.get(sid):
                fail(f"Retained alias source still has active case use: {sid}")
            if s.get("used_by_cases") or s.get("used_by_fields"):
                fail(f"Retained alias source should have empty used_by_* metadata: {sid}")
            continue
        if sorted(recomputed_cases.get(sid, set())) != sorted(s.get("used_by_cases", [])):
            fail(f"SOURCES.json used_by_cases out of sync for {sid}")
        if sorted(recomputed_fields.get(sid, set())) != sorted(s.get("used_by_fields", [])):
            fail(f"SOURCES.json used_by_fields out of sync for {sid}")



def check_evidence_ledger_sync():
    ledger = load_json(ROOT/"cases/EVIDENCE_LEDGER.json") or {}
    if ledger.get("revision_current") != CURRENT_REVISION:
        fail("EVIDENCE_LEDGER revision_current mismatch")
    rows = ledger.get("edge_rows", [])
    if ledger.get("evidence_edge_count") != len(rows):
        fail("EVIDENCE_LEDGER evidence_edge_count mismatch")
    ledger_keys = {(r.get("case_id"), r.get("claim_path"), r.get("source_id")) for r in rows if isinstance(r, dict)}
    def walk(obj, prefix=""):
        if isinstance(obj, dict):
            if isinstance(obj.get("source_ids"), list):
                yield prefix.rstrip("."), obj.get("source_ids")
            for k, v in obj.items():
                if k != "source_ids":
                    yield from walk(v, prefix + k + ".")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                yield from walk(v, prefix + str(i) + ".")
    base_to_case_id = {}
    for p in (ROOT/"cases").glob("*scoreboard.json"):
        data = load_json(p) or {}
        cid = data.get("case_id")
        base = p.name[:-len("-scoreboard.json")]
        base_to_case_id[base] = cid
        for path, sids in walk(data):
            for sid in sids:
                if (cid, path, sid) not in ledger_keys:
                    fail(f"Scoreboard source edge missing from EVIDENCE_LEDGER: {cid} {path} {sid}")
    # rev0340: memo-level citations must also be represented as evidence edges.
    for p in (ROOT/"cases").glob("*case.md"):
        base = p.name[:-len("-case.md")]
        cid = base_to_case_id.get(base, base)
        text = p.read_text(encoding="utf-8", errors="ignore")
        for n in re.findall(r"\[S(\d{2,3})\]", text):
            sid = "S" + n
            if (cid, "case_memo", sid) not in ledger_keys:
                fail(f"Case memo source edge missing from EVIDENCE_LEDGER: {cid} case_memo {sid}")


def check_rev0320_backstop_scoreboards():
    required = {
        "ai-data-center-grid-water-public-backstop-rev0320-scoreboard.json": {"ai_data_center_grid_water_backstop", "large_load_utility_cost_shift", "data_center_water_consumption_permitting"},
        "private-equity-hospital-public-backstop-rev0320-scoreboard.json": {"healthcare_financialization_public_backstop", "hospital_sale_leaseback_asset_stripping_risk", "essential_service_closure_public_cost"},
        "critical-minerals-industrial-policy-public-upside-rev0320-scoreboard.json": {"critical_minerals_supply_chain_subsidy_capture", "industrial_policy_public_upside_recovery", "supply_chain_security_public_risk_transfer"},
    }
    for name, keys in required.items():
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0320 backstop scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        fields = set((data.get("fields") or {}).keys())
        if not (fields & keys):
            fail(f"Rev0320 backstop scoreboard lacks expected fields: cases/{name}")


def load_route_registry():
    reg = load_json(ROOT/"docs/00-meta/route-registry.json") or {}
    routes = reg.get("routes", [])
    route_ids = {r.get("route_id") for r in routes if isinstance(r, dict)}
    aliases = set()
    for r in routes:
        if isinstance(r, dict):
            for a in r.get("aliases", []) or []:
                aliases.add(a)
    accepted = route_ids | aliases | {"unrouted"}
    return reg, route_ids, accepted


def extract_frontmatter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    return text[4:end]


def route_refs_from_fm(fm):
    role = None
    refs = []
    m = re.search(r"^route_role:\s*(.+)$", fm, re.M)
    if m:
        role = m.group(1).strip().strip('"\'')
    m = re.search(r"^route_refs:\s*(.*)$", fm, re.M)
    if m:
        rest = m.group(1).strip()
        if rest == "[]":
            refs = []
        elif rest.startswith("["):
            refs = [x.strip().strip('"\'') for x in rest.strip("[]").split(",") if x.strip()]
        else:
            after = fm[m.end():].splitlines()
            for line in after:
                if re.match(r"^[A-Za-z_]+:", line):
                    break
                m2 = re.match(r"^-\s*(.+)$", line.strip())
                if m2:
                    refs.append(m2.group(1).strip().strip('"\''))
    return role, refs


def check_route_registry_sync():
    reg, route_ids, accepted = load_route_registry()
    if reg.get("revision_current") != CURRENT_REVISION:
        fail("route-registry revision_current mismatch")
    if reg.get("route_count") != len(route_ids):
        fail("route-registry route_count mismatch")
    if len(route_ids) < 20:
        fail("route-registry unexpectedly small")
    for p in list((ROOT/"docs").glob("*/*.md")) + list((ROOT/"cases").glob("*.md")) + list(ROOT.glob("*.md")):
        fm = extract_frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        if not fm:
            continue
        role, refs = route_refs_from_fm(fm)
        if role and role not in accepted:
            fail(f"Unregistered route_role {role!r}: {p.relative_to(ROOT)}")
        for r in refs:
            if r not in accepted:
                fail(f"Unregistered route_ref {r!r}: {p.relative_to(ROOT)}")
    def walk_routes(obj, prefix=""):
        if isinstance(obj, dict):
            if isinstance(obj.get("routes"), list):
                yield prefix.rstrip("."), obj.get("routes")
            for k, v in obj.items():
                if k != "routes":
                    yield from walk_routes(v, prefix + k + ".")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                yield from walk_routes(v, prefix + str(i) + ".")
    for p in (ROOT/"cases").glob("*scoreboard.json"):
        data = load_json(p) or {}
        for path, routes in walk_routes(data):
            for r in routes:
                if r not in accepted:
                    fail(f"Unregistered scoreboard route {r!r} at {p.relative_to(ROOT)}::{path}")
    ledger = load_json(ROOT/"docs/00-meta/route-ledger.json") or {}
    if ledger.get("revision_current") != CURRENT_REVISION:
        fail("route-ledger revision_current mismatch")
    summary_ids = {r.get("route_id") for r in ledger.get("route_usage_summary", []) if isinstance(r, dict)}
    missing = route_ids - summary_ids
    if missing:
        fail(f"route-ledger summary missing route ids: {sorted(missing)[:10]}")


def is_remedy_operability_scoreboard(data):
    text = " ".join([str(data.get("case_type", "")), str(data.get("calibration_class", "")), " ".join((data.get("fields") or {}).keys()), " ".join((data.get("certification_gates") or {}).keys())])
    markers = ["remedy_operability", "appeal_latency", "identity_proofing", "arbitration_class", "collective_redress", "claimant_standing", "private_enforcement"]
    return any(m in text for m in markers)


def check_remedy_operability_register_presence():
    required = {"harm_or_claim", "claimant_perimeter", "standing_path", "notice_explanation", "interim_protection", "time_to_relief", "review_body", "collective_or_representative_action", "restoration_remedy", "enforcement_actor", "evidence_quality", "source_ids"}
    for p in sorted((ROOT/"cases").glob("*scoreboard.json")):
        data = load_json(p) or {}
        if not is_remedy_operability_scoreboard(data):
            continue
        reg = data.get("remedy_operability_register")
        if not isinstance(reg, list) or not reg:
            fail(f"Remedy-operability scoreboard missing nonempty remedy_operability_register: {p.relative_to(ROOT)}")
            continue
        for i, item in enumerate(reg):
            if not isinstance(item, dict):
                fail(f"Remedy-operability register item {i} not object: {p.relative_to(ROOT)}")
                continue
            for key in required:
                if key not in item:
                    fail(f"Remedy-operability register item missing {key}: {p.relative_to(ROOT)}")


def check_rev0321_remedy_scoreboards():
    required = {
        "social-security-disability-appeal-latency-rev0321-scoreboard.json": {"remedy_operability_gate", "appeal_latency_and_time_to_relief", "interim_protection_before_irreversible_loss"},
        "unemployment-insurance-identity-proofing-lockout-rev0321-scoreboard.json": {"identity_proofing_exclusion_risk", "anti_fraud_due_process_balance", "non_digital_access_channel"},
        "forced-arbitration-collective-redress-remedy-suppression-rev0321-scoreboard.json": {"arbitration_class_waiver_remedy_suppression", "collective_redress_availability", "private_enforcement_availability"},
    }
    for name, keys in required.items():
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0321 remedy scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        fields = set((data.get("fields") or {}).keys())
        if not keys.issubset(fields):
            fail(f"Rev0321 remedy scoreboard lacks expected fields: cases/{name}")



def check_field_registry_sync():
    schema = load_json(ROOT/"docs/20-program/scoreboard-schema.json") or {}
    schema_fields = set((((schema.get("properties") or {}).get("fields") or {}).get("properties") or {}).keys())
    if ((schema.get("properties") or {}).get("fields") or {}).get("additionalProperties") is not False:
        fail("scoreboard-schema fields.additionalProperties must be false")
    registry = load_json(ROOT/"docs/00-meta/field-registry.json") or {}
    ledger = load_json(ROOT/"docs/00-meta/field-use-ledger.json") or {}
    if registry.get("revision_current") != CURRENT_REVISION:
        fail("field-registry revision_current mismatch")
    if ledger.get("revision_current") != CURRENT_REVISION:
        fail("field-use-ledger revision_current mismatch")
    reg_ids = {r.get("field_id") for r in registry.get("fields", []) if isinstance(r, dict)}
    led_ids = {r.get("field_id") for r in ledger.get("fields", []) if isinstance(r, dict)}
    if schema_fields != reg_ids:
        fail("field-registry field set does not match scoreboard schema fields")
    if schema_fields != led_ids:
        fail("field-use-ledger field set does not match scoreboard schema fields")
    usage = {fid: set() for fid in schema_fields}
    for p in (ROOT/"cases").glob("*scoreboard.json"):
        data = load_json(p) or {}
        cid = data.get("case_id")
        for fid in (data.get("fields") or {}).keys():
            if fid not in schema_fields:
                fail(f"Unregistered field key {fid}: {p.relative_to(ROOT)}")
            else:
                usage[fid].add(cid)
    led_by_id = {r.get("field_id"): r for r in ledger.get("fields", []) if isinstance(r, dict)}
    reg_by_id = {r.get("field_id"): r for r in registry.get("fields", []) if isinstance(r, dict)}
    for fid, cases in usage.items():
        row = led_by_id.get(fid, {})
        if row.get("usage_count") != len(cases):
            fail(f"field-use-ledger usage_count mismatch for {fid}")
        if sorted(row.get("used_by_cases", [])) != sorted(cases):
            fail(f"field-use-ledger used_by_cases mismatch for {fid}")
        rrow = reg_by_id.get(fid, {})
        if rrow.get("usage_count") != len(cases):
            fail(f"field-registry usage_count mismatch for {fid}")
        for key in ["family", "primary_gate", "primary_route", "lifecycle_status"]:
            if not rrow.get(key):
                fail(f"field-registry missing {key} for {fid}")


def check_rev0322_rental_market_power_scoreboards():
    required = {
        "algorithmic-rent-setting-market-coordination-rev0322-scoreboard.json": {"rental_market_power_gate", "algorithmic_rent_setting_coordination", "competitor_data_pooling_in_pricing_tools", "landlord_pricing_independence_audit"},
        "institutional-single-family-rental-fee-repair-power-rev0322-scoreboard.json": {"rental_market_power_gate", "institutional_single_family_rental_concentration", "corporate_landlord_fee_stack", "security_deposit_repair_remedy_access"},
        "manufactured-housing-land-lease-wealth-trap-rev0322-scoreboard.json": {"rental_market_power_gate", "manufactured_housing_land_lease_split", "manufactured_home_mobility_lock_in", "manufactured_lot_rent_escalation", "chattel_finance_protection_gap"},
    }
    for name, keys in required.items():
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0322 rental-market-power scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        fields = set((data.get("fields") or {}).keys())
        if not keys.issubset(fields):
            fail(f"Rev0322 rental-market-power scoreboard lacks expected fields: cases/{name}")



def check_currentness_ledger_sync():
    ledger = load_json(ROOT/"docs/00-meta/currentness-ledger.json") or {}
    if ledger.get("revision_current") != CURRENT_REVISION:
        fail("currentness-ledger revision_current mismatch")
    classes = {c.get("class") for c in ledger.get("currentness_classes", []) if isinstance(c, dict)}
    if not classes:
        fail("currentness-ledger has no currentness_classes")
    rows = ledger.get("case_rows", [])
    if not isinstance(rows, list):
        fail("currentness-ledger case_rows must be a list")
        rows = []
    score_ids = { (load_json(p) or {}).get("case_id") for p in (ROOT/"cases").glob("*scoreboard.json") }
    date_re = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for row in rows:
        cid = row.get("case_id") if isinstance(row, dict) else None
        if cid not in score_ids:
            fail(f"currentness-ledger case row does not match scoreboard: {cid}")
        for key in ["currentness_class", "snapshot_date", "refresh_due", "reopen_on"]:
            if key not in row or row.get(key) in (None, ""):
                fail(f"currentness-ledger row missing {key}: {cid}")
        if row.get("currentness_class") not in classes:
            fail(f"currentness-ledger undeclared case currentness_class {row.get('currentness_class')!r}: {cid}")
        for key in ["snapshot_date", "refresh_due"]:
            if row.get(key) and not date_re.match(str(row.get(key))):
                fail(f"currentness-ledger case row bad {key}: {cid}")
        if not isinstance(row.get("reopen_on"), list) or not row.get("reopen_on"):
            fail(f"currentness-ledger case row reopen_on must be nonempty list: {cid}")
    source_rows = ledger.get("source_rows", [])
    if not isinstance(source_rows, list) or not source_rows:
        fail("currentness-ledger source_rows must be a nonempty list")
        return
    srcs = load_json(ROOT/"SOURCES.json") or {}
    source_ids_expected = {s.get("id") for s in srcs.get("sources", []) if isinstance(s, dict)}
    by_source = {r.get("source_id"): r for r in source_rows if isinstance(r, dict)}
    if source_ids_expected != set(by_source):
        missing = sorted(source_ids_expected - set(by_source))[:10]
        extra = sorted(set(by_source) - source_ids_expected)[:10]
        fail(f"currentness-ledger source_rows source set mismatch; missing={missing}, extra={extra}")
    for sid, row in by_source.items():
        for key in ["currentness_class", "snapshot_date", "refresh_due", "reopen_on"]:
            if key not in row or row.get(key) in (None, ""):
                fail(f"currentness-ledger source row missing {key}: {sid}")
        if row.get("currentness_class") not in classes:
            fail(f"currentness-ledger undeclared source currentness_class {row.get('currentness_class')!r}: {sid}")
        for key in ["snapshot_date", "refresh_due"]:
            if row.get(key) and not date_re.match(str(row.get(key))):
                fail(f"currentness-ledger source row bad {key}: {sid}")
        if not isinstance(row.get("reopen_on"), list) or not row.get("reopen_on"):
            fail(f"currentness-ledger source row reopen_on must be nonempty list: {sid}")


def check_case_source_refresh_ordering():
    sources = load_json(ROOT/"SOURCES.json") or {}
    refresh = {s.get("id"): s.get("refresh_due") for s in sources.get("sources", []) if isinstance(s, dict)}
    date_re = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for p in sorted((ROOT/"cases").glob("*scoreboard.json")):
        data = load_json(p) or {}
        case_refresh = data.get("source_refresh_due")
        if not case_refresh or not date_re.match(str(case_refresh)):
            continue
        sids = sorted({sid for sid in iter_source_ids_in_json(data) if sid in refresh})
        if not sids:
            continue
        min_due = min(refresh[sid] for sid in sids if refresh.get(sid))
        if min_due and case_refresh > min_due:
            fail(f"{p.relative_to(ROOT)} source_refresh_due {case_refresh} later than cited source min refresh_due {min_due}")


def check_source_duplicate_audit_sync():
    audit = load_json(ROOT/"docs/00-meta/source-duplicate-audit.json") or {}
    if audit.get("revision_current") != CURRENT_REVISION:
        fail("source-duplicate-audit revision_current mismatch")
    sources = load_json(ROOT/"SOURCES.json") or {}
    by_url, by_title = {}, {}
    for s in sources.get("sources", []):
        url = (s.get("url") or "").strip()
        if url:
            by_url.setdefault(url, []).append(s.get("id"))
        title = re.sub(r"\s+", " ", (s.get("title") or "").strip().lower())
        if title:
            by_title.setdefault(title, []).append(s.get("id"))
    actual_url = sum(1 for ids in by_url.values() if len(ids) > 1)
    actual_title = sum(1 for ids in by_title.values() if len(ids) > 1)
    if audit.get("duplicate_url_group_count") != actual_url:
        fail(f"source-duplicate-audit URL count {audit.get('duplicate_url_group_count')} != {actual_url}")
    if audit.get("duplicate_title_group_count") != actual_title:
        fail(f"source-duplicate-audit title count {audit.get('duplicate_title_group_count')} != {actual_title}")
    if len(audit.get("url_groups", [])) != actual_url:
        fail("source-duplicate-audit url_groups length mismatch")
    if len(audit.get("title_groups", [])) != actual_title:
        fail("source-duplicate-audit title_groups length mismatch")


def check_current_validation_report_present():
    rel = f"reports/validation-report-{CURRENT_REVISION}.md"
    path = ROOT/rel
    if not path.exists():
        fail(f"Missing current validation report: {rel}")
        return
    if CURRENT_REVISION not in path.read_text(encoding="utf-8", errors="ignore"):
        fail(f"Current validation report does not mention {CURRENT_REVISION}: {rel}")


def check_rev0323_currentness_dynastic_scoreboards():
    required = {
        "estate-gift-gst-exemption-currentness-rev0323-scoreboard.json": {"temporal_currentness_gate", "current_law_snapshot_date", "law_effective_date_stability", "estate_tax_gift_gst_perimeter"},
        "dynasty-trust-perpetuity-gst-lock-in-rev0323-scoreboard.json": {"trust_duration_perpetuity_risk", "dynasty_trust_gst_lock_in", "dynasty_trust_rule_against_perpetuities"},
        "beneficial-ownership-trust-entity-visibility-rollback-rev0323-scoreboard.json": {"beneficial_ownership_trust_arrangement_visibility", "domestic_entity_boi_reporting_exemption", "trust_beneficial_ownership_visibility"},
        "donor-advised-fund-private-foundation-public-subsidy-rev0323-scoreboard.json": {"private_charitable_vehicle_public_subsidy", "donor_advised_fund_payout_timing", "charitable_tax_expenditure_accountability"},
    }
    for name, keys in required.items():
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0323 currentness/dynastic scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        fields = set((data.get("fields") or {}).keys())
        if not keys.issubset(fields):
            fail(f"Rev0323 currentness/dynastic scoreboard lacks expected fields: cases/{name}")


def check_rev0326_gate20_burndown():
    required_active = {
        "stablecoins-money-market-treasury-liquidity-backstop-rev0319-scoreboard.json": {"S441", "S442", "S443", "S444"},
        "private-credit-nonbank-backstop-perimeter-rev0319-scoreboard.json": {"S359", "S376"},
        "tax-expenditure-hidden-public-balance-sheet-rev0319-scoreboard.json": {"S378"},
        "federal-reserve-balance-sheet-quasi-fiscal-rev0318-scoreboard.json": set(),
    }
    for name, expected_sources in required_active.items():
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0326 Gate 20 burndown scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        if data.get("status") != "active":
            fail(f"rev0326 Gate 20 burndown scoreboard is not active: cases/{name}")
        sids = set(iter_source_ids_in_json(data))
        missing = expected_sources - sids
        if missing:
            fail(f"rev0326 Gate 20 burndown scoreboard missing expected sources {sorted(missing)}: cases/{name}")
    stable = load_json(ROOT/"cases"/"stablecoins-money-market-treasury-liquidity-backstop-rev0319-scoreboard.json") or {}
    if stable.get("source_refresh_due") != "2026-09-30":
        fail("rev0326 stablecoin case must refresh by 2026-09-30 while GENIUS Act rulemaking is live")
    # Active case/scoreboard payloads should no longer cite duplicate aliases canonicalized in rev0326.
    banned = {"S377", "S438"}
    for p in sorted((ROOT/"cases").glob("*scoreboard.json")):
        data = load_json(p) or {}
        used = set(iter_source_ids_in_json(data))
        bad = banned & used
        if bad:
            fail(f"Active scoreboard still cites canonicalized duplicate alias(es) {sorted(bad)}: {p.relative_to(ROOT)}")
    for p in sorted((ROOT/"cases").glob("*case.md")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        for sid in banned:
            if f"[{sid}]" in text:
                fail(f"Active case memo still cites canonicalized duplicate alias {sid}: {p.relative_to(ROOT)}")



def check_rev0327_backstop_status_parity():
    required = {
        "ai-data-center-grid-water-public-backstop-rev0320-scoreboard.json": {"sources": {"S445", "S446"}, "refresh_due": "2026-09-30"},
        "us-climate-residual-insurance-public-backstop-rev0319-scoreboard.json": {"sources": {"S447"}, "refresh_due": "2026-09-30"},
        "private-equity-hospital-public-backstop-rev0320-scoreboard.json": {"sources": {"S394", "S396"}, "refresh_due": "2026-12-31"},
        "critical-minerals-industrial-policy-public-upside-rev0320-scoreboard.json": {"sources": {"S448"}, "refresh_due": "2026-12-31"},
    }
    for name, spec in required.items():
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0327 backstop-status-parity scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        if data.get("status") != "active":
            fail(f"rev0327 promoted backstop scoreboard is not active: cases/{name}")
        if data.get("source_refresh_due") != spec["refresh_due"]:
            fail(f"rev0327 promoted backstop scoreboard has wrong source_refresh_due: cases/{name}")
        used = set(iter_source_ids_in_json(data))
        missing = spec["sources"] - used
        if missing:
            fail(f"rev0327 promoted backstop scoreboard missing expected currentness sources {sorted(missing)}: cases/{name}")
        if "case remains seed" in json.dumps(data).lower():
            fail(f"rev0327 promoted backstop scoreboard retains seed-only validation language: cases/{name}")
    # This audit should remain visible until the remaining active_memo/seed_scoreboard backlog is burned down.
    audit = ROOT/"reports"/"status-parity-audit-rev0327.json"
    if not audit.exists():
        fail(f"Missing rev0327 status-parity audit: {audit.relative_to(ROOT)}")
        return
    data = load_json(audit) or {}
    fixed = set(data.get("corrected_in_revision", []))
    required_ids = {name[:-len("-scoreboard.json")] for name in required}
    if not required_ids.issubset(fixed):
        fail("rev0327 status-parity audit does not list all corrected target cases")



def check_rev0328_federal_claim_security_burndown():
    required = {
        "social-security-medicare-claim-security-rev0318-scoreboard.json": {"sources": {"S449", "S450"}, "refresh_due": "2026-09-30"},
        "united-states-federal-fiscal-interest-risk-rev0318-scoreboard.json": {"sources": {"S451", "S449", "S450"}, "refresh_due": "2026-09-30"},
        "deposit-insurance-bank-backstop-rev0318-scoreboard.json": {"sources": {"S452"}, "refresh_due": "2026-09-30"},
        "housing-finance-guarantee-fha-gse-rev0318-scoreboard.json": {"sources": {"S365", "S366", "S367"}, "refresh_due": "2027-03-31"},
        "federal-student-loan-credit-program-risk-rev0319-scoreboard.json": {"sources": {"S453"}, "refresh_due": "2026-09-30"},
    }
    for name, spec in required.items():
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0328 federal claim-security burndown scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        if data.get("status") != "active":
            fail(f"rev0328 promoted federal claim-security scoreboard is not active: cases/{name}")
        if name == "social-security-medicare-claim-security-rev0318-scoreboard.json":
            # rev0378: this case now cites a source with an earlier refresh/recommendation update date.
            if data.get("source_refresh_due") > spec["refresh_due"]:
                fail(f"rev0328 promoted federal claim-security scoreboard has source_refresh_due later than legacy ceiling: cases/{name}")
        elif data.get("source_refresh_due") != spec["refresh_due"]:
            fail(f"rev0328 promoted federal claim-security scoreboard has wrong source_refresh_due: cases/{name}")
        used = set(iter_source_ids_in_json(data))
        missing = spec["sources"] - used
        if missing:
            fail(f"rev0328 promoted federal claim-security scoreboard missing expected sources {sorted(missing)}: cases/{name}")
        if "case remains seed" in json.dumps(data).lower():
            fail(f"rev0328 promoted federal claim-security scoreboard retains seed-only validation language: cases/{name}")
    audit = ROOT/"reports"/"status-parity-audit-rev0328.json"
    if not audit.exists():
        fail(f"Missing rev0328 status-parity audit: {audit.relative_to(ROOT)}")
        return
    data = load_json(audit) or {}
    fixed = set(data.get("corrected_in_revision", []))
    required_ids = {name[:-len("-scoreboard.json")] for name in required}
    if not required_ids.issubset(fixed):
        fail("rev0328 status-parity audit does not list all corrected target cases")
    if "risk_queue" not in data:
        fail("rev0328 status-parity audit must include risk_queue triage")



def check_rev0329_sovereign_public_fiscal_burndown():
    required = {
        "china-local-government-property-state-capital-risk-rev0319-scoreboard.json": {"sources": {"S383", "S384"}, "refresh_due": "2026-12-31"},
        "japan-korea-aging-pension-care-fiscal-risk-rev0319-scoreboard.json": {"sources": {"S356", "S386", "S387", "S388", "S389"}, "refresh_due": "2027-03-31"},
        "norway-gpfg-public-asset-governance-rev0318-scoreboard.json": {"sources": {"S369", "S456"}, "refresh_due": "2027-03-31"},
        "ppp-soe-legal-judgment-contingent-liability-rev0319-scoreboard.json": {"sources": {"S350", "S381", "S382", "S457"}, "refresh_due": "2027-03-31"},
        "us-state-local-public-pension-risk-rev0318-scoreboard.json": {"sources": {"S454", "S455"}, "refresh_due": "2026-12-31"},
    }
    for name, spec in required.items():
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0329 sovereign/public-fiscal burndown scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        if data.get("status") != "active":
            fail(f"rev0329 promoted sovereign/public-fiscal scoreboard is not active: cases/{name}")
        if data.get("source_refresh_due") != spec["refresh_due"]:
            fail(f"rev0329 promoted sovereign/public-fiscal scoreboard has wrong source_refresh_due: cases/{name}")
        used = set(iter_source_ids_in_json(data))
        missing = spec["sources"] - used
        if missing:
            fail(f"rev0329 promoted sovereign/public-fiscal scoreboard missing expected sources {sorted(missing)}: cases/{name}")
        if "case remains seed" in json.dumps(data).lower() or "seed/proxy stress case" in json.dumps(data).lower():
            fail(f"rev0329 promoted sovereign/public-fiscal scoreboard retains seed-only validation language: cases/{name}")
    audit = ROOT/"reports"/"status-parity-audit-rev0329.json"
    if not audit.exists():
        fail(f"Missing rev0329 status-parity audit: {audit.relative_to(ROOT)}")
        return
    data = load_json(audit) or {}
    fixed = set(data.get("corrected_in_revision", []))
    required_ids = {name[:-len("-scoreboard.json")] for name in required}
    if not required_ids.issubset(fixed):
        fail("rev0329 status-parity audit does not list all corrected target cases")
    if data.get("remaining_count") != len(data.get("remaining_active_memo_seed_scoreboard_mismatches", [])):
        fail("rev0329 status-parity audit remaining_count mismatch")



def check_rev0330_score_mediated_exclusion_burndown():
    required = {
        "united-states-credit-reporting-medical-debt-rev0315-scoreboard.json": {"sources": {"S458", "S459"}, "refresh_due": "2026-09-30"},
        "tenant-screening-eviction-records-rev0315-scoreboard.json": {"sources": {"S286", "S287"}, "refresh_due": "2026-12-31"},
        "insurance-scoring-surveillance-pricing-rev0315-scoreboard.json": {"sources": {"S290", "S291", "S292", "S293", "S294"}, "refresh_due": "2026-12-31"},
        "data-broker-fraud-identity-lockout-rev0315-scoreboard.json": {"sources": {"S459", "S461", "S283", "S289"}, "refresh_due": "2026-09-30"},
        "algorithmic-public-benefit-eligibility-rev0315-scoreboard.json": {"sources": {"S460", "S461", "S295", "S297"}, "refresh_due": "2026-12-31"},
    }
    for name, spec in required.items():
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0330 Gate 17 burndown scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        if data.get("status") != "active":
            fail(f"rev0330 promoted Gate 17 scoreboard is not active: cases/{name}")
        if data.get("source_refresh_due") != spec["refresh_due"]:
            fail(f"rev0330 promoted Gate 17 scoreboard has wrong source_refresh_due: cases/{name}")
        used = set(iter_source_ids_in_json(data))
        missing = spec["sources"] - used
        if missing:
            fail(f"rev0330 promoted Gate 17 scoreboard missing expected sources {sorted(missing)}: cases/{name}")
        body = json.dumps(data).lower()
        if "case remains seed" in body or "seed/proxy" in body or "not a certified jurisdiction report" in body:
            fail(f"rev0330 promoted Gate 17 scoreboard retains seed-only validation language: cases/{name}")
        cert = (data.get("certification_gates") or {}).get("gate_17_score_mediated_exclusion") or {}
        if cert.get("status") != "blocked":
            fail(f"rev0330 promoted Gate 17 scoreboard must keep certification blocked pending remedy proof: cases/{name}")
    audit = ROOT/"reports"/"status-parity-audit-rev0330.json"
    if not audit.exists():
        fail(f"Missing rev0330 status-parity audit: {audit.relative_to(ROOT)}")
        return
    data = load_json(audit) or {}
    fixed = set(data.get("corrected_in_revision", []))
    required_ids = {name[:-len("-scoreboard.json")] for name in required}
    if not required_ids.issubset(fixed):
        fail("rev0330 status-parity audit does not list all corrected Gate 17 target cases")
    if data.get("remaining_count") != len(data.get("remaining_active_memo_seed_scoreboard_mismatches", [])):
        fail("rev0330 status-parity audit remaining_count mismatch")
    if (data.get("risk_queue") or {}).get("remaining_gate_17_score_mediated_exclusion"):
        fail("rev0330 status-parity audit should show no remaining Gate 17 status-parity mismatches")



def check_rev0331_gate18_gate19_backlog_closure():
    required = {
        "united-states-bankruptcy-fresh-start-rev0316-scoreboard.json": {"sources": {"S301", "S302", "S304", "S319"}, "gate": "gate_18_fresh_start_capacity", "refresh_due": "2027-03-31"},
        "united-states-garnishment-bank-levy-rev0316-scoreboard.json": {"sources": {"S304", "S305", "S306", "S320"}, "gate": "gate_18_fresh_start_capacity", "refresh_due": "2027-03-31"},
        "debt-collection-default-judgment-rev0316-scoreboard.json": {"sources": {"S307", "S308", "S318", "S319"}, "gate": "gate_18_fresh_start_capacity", "refresh_due": "2027-03-31"},
        "eviction-foreclosure-record-recovery-rev0316-scoreboard.json": {"sources": {"S309", "S310", "S311", "S312", "S313"}, "gate": "gate_18_fresh_start_capacity", "refresh_due": "2027-03-31"},
        "reentry-clean-slate-collateral-consequences-rev0316-scoreboard.json": {"sources": {"S315", "S316", "S317"}, "gate": "gate_18_fresh_start_capacity", "refresh_due": "2027-03-31"},
        "united-states-inheritance-lifetime-transfer-rev0317-scoreboard.json": {"sources": {"S321", "S322", "S323", "S324"}, "gate": "gate_19_intergenerational_transfer", "refresh_due": "2027-03-31"},
        "united-states-estate-tax-trust-perimeter-rev0317-scoreboard.json": {"sources": {"S326", "S430", "S431", "S439", "S440"}, "gate": "gate_19_intergenerational_transfer", "refresh_due": "2027-03-31"},
        "heirs-property-probate-title-finality-rev0317-scoreboard.json": {"sources": {"S335", "S336", "S337"}, "gate": "gate_19_intergenerational_transfer", "refresh_due": "2027-03-31"},
        "medicaid-estate-recovery-home-equity-rev0317-scoreboard.json": {"sources": {"S332", "S333", "S334", "S462"}, "gate": "gate_19_intergenerational_transfer", "refresh_due": "2027-03-31"},
        "guardianship-elder-exploitation-fiduciary-rev0317-scoreboard.json": {"sources": {"S338", "S339", "S340", "S341", "S342", "S344"}, "gate": "gate_19_intergenerational_transfer", "refresh_due": "2027-03-31"},
        "divorce-child-support-family-wealth-rev0317-scoreboard.json": {"sources": {"S327", "S328", "S329", "S330", "S331"}, "gate": "gate_19_intergenerational_transfer", "refresh_due": "2027-03-31"},
    }
    for name, spec in required.items():
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0331 Gate 18/19 backlog closure scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        if data.get("status") != "active":
            fail(f"rev0331 promoted Gate 18/19 scoreboard is not active: cases/{name}")
        if data.get("source_refresh_due") != spec["refresh_due"]:
            fail(f"rev0331 promoted Gate 18/19 scoreboard has wrong source_refresh_due: cases/{name}")
        used = set(iter_source_ids_in_json(data))
        missing = spec["sources"] - used
        if missing:
            fail(f"rev0331 promoted Gate 18/19 scoreboard missing expected sources {sorted(missing)}: cases/{name}")
        body = json.dumps(data).lower()
        if "case remains seed" in body or "seed/proxy" in body or "not a certified jurisdiction report" in body or "not a full jurisdictional certification" in body:
            fail(f"rev0331 promoted Gate 18/19 scoreboard retains seed-only validation language: cases/{name}")
        cert = (data.get("certification_gates") or {}).get(spec["gate"]) or {}
        if cert.get("status") != "blocked":
            fail(f"rev0331 promoted Gate 18/19 scoreboard must keep certification blocked pending proof: cases/{name}")
        if not data.get("evidence_debt_register") or len(data.get("evidence_debt_register", [])) < 4:
            fail(f"rev0331 promoted Gate 18/19 scoreboard lacks enough evidence-debt rows: cases/{name}")
    audit = ROOT/"reports"/"status-parity-audit-rev0331.json"
    if not audit.exists():
        fail(f"Missing rev0331 status-parity audit: {audit.relative_to(ROOT)}")
        return
    data = load_json(audit) or {}
    fixed = set(data.get("corrected_in_revision", []))
    required_ids = {name[:-len("-scoreboard.json")] for name in required}
    if not required_ids.issubset(fixed):
        fail("rev0331 status-parity audit does not list all corrected Gate 18/19 target cases")
    if data.get("remaining_count") != 0 or data.get("remaining_active_memo_seed_scoreboard_mismatches"):
        fail("rev0331 status-parity audit must close all active-memo/seed-scoreboard mismatches")
    if (data.get("risk_queue") or {}).get("remaining_gate_18_fresh_start_recovery") or (data.get("risk_queue") or {}).get("remaining_gate_19_intergenerational_family_property_transfer"):
        fail("rev0331 status-parity audit should show no remaining Gate 18 or Gate 19 mismatches")


def check_no_active_memo_seed_scoreboard_mismatch():
    for score in sorted((ROOT/"cases").glob("*-scoreboard.json")):
        base = score.name[:-len("-scoreboard.json")]
        data = load_json(score) or {}
        memo = ROOT/"cases"/(base + "-case.md")
        if not memo.exists():
            continue
        text = memo.read_text(encoding="utf-8", errors="ignore")
        fm = extract_frontmatter(text) or ""
        m = re.search(r"^status:\s*(.+)$", fm, re.M)
        memo_status = m.group(1).strip() if m else ""
        if data.get("status") == "seed" and "active" in memo_status:
            fail(f"Active memo still paired with seed scoreboard after rev0331 closure: {base}")



def check_rev0332_seed_backlog_closure():
    required = {
        "social-security-disability-appeal-latency-rev0321-scoreboard.json": {"sources": {"S402", "S403"}, "refresh_due": "2026-12-31"},
        "unemployment-insurance-identity-proofing-lockout-rev0321-scoreboard.json": {"sources": {"S404", "S405", "S406", "S407", "S408"}, "refresh_due": "2026-12-31"},
        "forced-arbitration-collective-redress-remedy-suppression-rev0321-scoreboard.json": {"sources": {"S409", "S410", "S413", "S463"}, "refresh_due": "2027-03-31"},
        "algorithmic-rent-setting-market-coordination-rev0322-scoreboard.json": {"sources": {"S414", "S415", "S416", "S464"}, "refresh_due": "2026-09-30"},
        "institutional-single-family-rental-fee-repair-power-rev0322-scoreboard.json": {"sources": {"S417", "S418", "S419", "S420"}, "refresh_due": "2027-03-31"},
        "manufactured-housing-land-lease-wealth-trap-rev0322-scoreboard.json": {"sources": {"S421", "S422", "S423", "S425", "S465"}, "refresh_due": "2027-03-31"},
    }
    for pth in sorted((ROOT/"cases").glob("*-scoreboard.json")):
        data = load_json(pth) or {}
        if data.get("status") == "seed":
            fail(f"rev0332 should have no remaining seed scoreboards: {pth.relative_to(ROOT)}")
    for name, spec in required.items():
        pth = ROOT/"cases"/name
        if not pth.exists():
            fail(f"Missing rev0332 seed-backlog closure scoreboard: cases/{name}")
            continue
        data = load_json(pth) or {}
        if data.get("status") != "active":
            fail(f"rev0332 promoted scoreboard is not active: cases/{name}")
        if data.get("source_refresh_due") != spec["refresh_due"]:
            fail(f"rev0332 promoted scoreboard has wrong source_refresh_due: cases/{name}")
        used = set(iter_source_ids_in_json(data))
        missing = spec["sources"] - used
        if missing:
            fail(f"rev0332 promoted scoreboard missing expected sources {sorted(missing)}: cases/{name}")
        body = json.dumps(data).lower()
        if "seed/proxy" in body or "case remains seed" in body:
            fail(f"rev0332 promoted scoreboard retains seed-only validation language: cases/{name}")
        for gate, item in (data.get("gate_inventory") or {}).items():
            if isinstance(item, dict) and item.get("status") in {"blocked", "watch", "missing"} and not item.get("source_ids"):
                fail(f"rev0332 promoted scoreboard has unsourced active gate_inventory row {gate}: cases/{name}")
        memo = ROOT/"cases"/(name[:-len("-scoreboard.json")] + "-case.md")
        if memo.exists():
            fm = extract_frontmatter(memo.read_text(encoding="utf-8", errors="ignore")) or ""
            if "status: active_case" not in fm:
                fail(f"rev0332 promoted memo is not active_case: {memo.relative_to(ROOT)}")
    audit = ROOT/"reports"/"seed-backlog-audit-rev0332.json"
    if not audit.exists():
        fail(f"Missing rev0332 seed backlog audit: {audit.relative_to(ROOT)}")
        return
    data = load_json(audit) or {}
    if data.get("remaining_seed_scoreboard_count") != 0 or data.get("remaining_seed_scoreboards"):
        fail("rev0332 seed backlog audit must show zero remaining seed scoreboards")
    fixed = set(data.get("corrected_in_revision", []))
    required_ids = {name[:-len("-scoreboard.json")] for name in required}
    if not required_ids.issubset(fixed):
        fail("rev0332 seed backlog audit does not list all corrected target cases")



def check_rev0333_workplace_power_current_law_hardening():
    required = {
        "united-states-union-density-wealth-formation-rev0312-scoreboard.json": {"sources": {"S220", "S221", "S237"}, "refresh_due": "2027-03-31", "gate_status": "blocked"},
        "united-states-noncompete-worker-mobility-rev0312-scoreboard.json": {"sources": {"S225", "S226", "S232", "S233"}, "refresh_due": "2026-12-31", "gate_status": "blocked"},
        "united-states-fissured-workplace-joint-employer-rev0312-scoreboard.json": {"sources": {"S222", "S223", "S224", "S227", "S228"}, "refresh_due": "2026-12-31", "gate_status": "blocked"},
        "eu-platform-work-employment-presumption-rev0312-scoreboard.json": {"sources": {"S229"}, "refresh_due": "2026-12-31", "gate_status": "watch"},
        "employee-ownership-esop-wealth-formation-rev0312-scoreboard.json": {"sources": {"S235", "S236"}, "refresh_due": "2027-03-31", "gate_status": "watch"},
    }
    for name, spec in required.items():
        pth = ROOT/"cases"/name
        if not pth.exists():
            fail(f"Missing rev0333 workplace-power hardened scoreboard: cases/{name}")
            continue
        data = load_json(pth) or {}
        if data.get("status") != "active":
            fail(f"rev0333 workplace-power target is not active: cases/{name}")
        if "seed" in str(data.get("calibration_class", "")).lower():
            fail(f"rev0333 workplace-power target still has seed calibration class: cases/{name}")
        if data.get("source_refresh_due") != spec["refresh_due"]:
            fail(f"rev0333 workplace-power target has wrong source_refresh_due: cases/{name}")
        used = set(iter_source_ids_in_json(data))
        missing = spec["sources"] - used
        if missing:
            fail(f"rev0333 workplace-power target missing expected sources {sorted(missing)}: cases/{name}")
        cert = (data.get("certification_gates") or {}).get("gate_14_workplace_power") or {}
        if cert.get("status") != spec["gate_status"]:
            fail(f"rev0333 workplace-power target has wrong Gate 14 status: cases/{name}")
        rows = data.get("evidence_debt_register") or []
        if len(rows) < 5:
            fail(f"rev0333 workplace-power target lacks enough evidence-debt rows: cases/{name}")
        for i, row in enumerate(rows):
            if not isinstance(row, dict) or not row.get("source_ids"):
                fail(f"rev0333 workplace-power target has unsourced evidence-debt row {i}: cases/{name}")
        body = json.dumps(data).lower()
        if "workplace_power_gate_seed" in body:
            fail(f"rev0333 workplace-power target still refers to workplace_power_gate_seed: cases/{name}")
    audit = ROOT/"reports"/"seed-calibration-class-audit-rev0333.json"
    if not audit.exists():
        fail(f"Missing rev0333 seed-calibration-class audit: {audit.relative_to(ROOT)}")
        return
    data = load_json(audit) or {}
    fixed = {r.get("case_id", "").replace("-case", "") for r in data.get("corrected_this_revision", []) if isinstance(r, dict)}
    required_ids = {name[:-len("-scoreboard.json")] for name in required}
    if not required_ids.issubset(fixed):
        fail("rev0333 seed-calibration-class audit does not list all workplace-power targets")
    remaining = data.get("remaining_active_seed_calibration_scoreboards", [])
    for r in remaining:
        if isinstance(r, dict) and any(name[:-len("-scoreboard.json")] in str(r.get("scoreboard_file", "")) for name in required):
            fail("rev0333 seed-calibration-class audit still lists a target as remaining seed calibration")



def check_rev0334_household_market_extraction_hardening():
    required = {
        "bnpl-earned-wage-credit-visibility-rev0314-scoreboard.json": {"sources": {"S264", "S265", "S272"}, "refresh_due": "2026-12-31", "gate_status": "watch"},
        "united-states-auto-finance-repossession-rev0314-scoreboard.json": {"sources": {"S260", "S266", "S267", "S280"}, "refresh_due": "2027-03-31", "gate_status": "blocked"},
        "united-states-consumer-finance-fee-drain-rev0314-scoreboard.json": {"sources": {"S260", "S262", "S263", "S268", "S269", "S270", "S271", "S279"}, "refresh_due": "2026-12-31", "gate_status": "blocked"},
        "united-states-childcare-cost-time-wealth-rev0314-scoreboard.json": {"sources": {"S273", "S274", "S275", "S276"}, "refresh_due": "2027-03-31", "gate_status": "blocked"},
        "oecd-long-term-care-asset-spenddown-rev0314-scoreboard.json": {"sources": {"S277", "S278"}, "refresh_due": "2027-03-31", "gate_status": "blocked"},
    }
    for name, spec in required.items():
        pth = ROOT/"cases"/name
        if not pth.exists():
            fail(f"Missing rev0334 household-market target scoreboard: cases/{name}")
            continue
        data = load_json(pth) or {}
        if data.get("status") != "active":
            fail(f"rev0334 household-market target is not active: cases/{name}")
        if "seed" in str(data.get("calibration_class", "")).lower():
            fail(f"rev0334 household-market target still has seed calibration class: cases/{name}")
        if data.get("source_refresh_due") != spec["refresh_due"]:
            fail(f"rev0334 household-market target has wrong source_refresh_due: cases/{name}")
        used = set(iter_source_ids_in_json(data))
        missing = spec["sources"] - used
        if missing:
            fail(f"rev0334 household-market target missing expected sources {sorted(missing)}: cases/{name}")
        cert = (data.get("certification_gates") or {}).get("gate_16_household_market_extraction") or {}
        if cert.get("status") != spec["gate_status"]:
            fail(f"rev0334 household-market target has wrong Gate 16 status: cases/{name}")
        rows = data.get("evidence_debt_register") or []
        if len(rows) < 5:
            fail(f"rev0334 household-market target lacks enough evidence-debt rows: cases/{name}")
        for i, row in enumerate(rows):
            if not isinstance(row, dict) or not row.get("source_ids"):
                fail(f"rev0334 household-market target has unsourced evidence-debt row {i}: cases/{name}")
    audit = ROOT/"reports"/"seed-calibration-class-audit-rev0334.json"
    if not audit.exists():
        fail(f"Missing rev0334 seed-calibration-class audit: {audit.relative_to(ROOT)}")
        return
    data = load_json(audit) or {}
    fixed = {r.get("scoreboard_file", "") for r in data.get("corrected_this_revision", []) if isinstance(r, dict)}
    if not set(required).issubset(fixed):
        fail("rev0334 seed-calibration-class audit does not list all household-market targets")
    remaining = data.get("remaining_active_seed_calibration_scoreboards", [])
    for r in remaining:
        if isinstance(r, dict) and r.get("scoreboard_file") in required:
            fail("rev0334 seed-calibration-class audit still lists a target as remaining seed calibration")
    sources = load_json(ROOT/"SOURCES.json") or {}
    s279 = next((s for s in sources.get("sources", []) if s.get("id") == "S279"), {})
    if s279.get("source_type") == "official" or s279.get("evidence_role") == "official":
        fail("rev0334 source-fit refactor failed: S279 still labeled as official authority")
    ledger = load_json(ROOT/"docs/00-meta/currentness-ledger.json") or {}
    classes = {c.get("class") for c in ledger.get("currentness_classes", []) if isinstance(c, dict)}
    if "household_market_product_current_law" not in classes or "household_market_statistical_release" not in classes:
        fail("rev0334 currentness ledger lacks household-market currentness classes")



def check_rev0335_place_public_finance_hardening():
    required = {
        "united-states-school-finance-property-tax-rev0313-scoreboard.json": {"sources": {"S238", "S239", "S240", "S241", "S242", "S466"}, "refresh_due": "2026-12-31", "gate_status": "watch"},
        "united-states-municipal-infrastructure-fiscal-capacity-rev0313-scoreboard.json": {"sources": {"S245", "S246", "S247", "S248", "S249", "S258"}, "refresh_due": "2026-12-31", "gate_status": "watch"},
        "united-states-utility-burden-disconnection-rev0313-scoreboard.json": {"sources": {"S250", "S251", "S252", "S253"}, "refresh_due": "2026-12-31", "gate_status": "blocked"},
        "local-disaster-fiscal-capacity-rev0313-scoreboard.json": {"sources": {"S256", "S257", "S258", "S468"}, "refresh_due": "2026-12-31", "gate_status": "watch"},
        "transportation-access-and-place-affordability-rev0313-scoreboard.json": {"sources": {"S254", "S255", "S259", "S467"}, "refresh_due": "2026-12-31", "gate_status": "watch"},
    }
    for name, spec in required.items():
        pth = ROOT/"cases"/name
        if not pth.exists():
            fail(f"Missing rev0335 place-public-finance target scoreboard: cases/{name}")
            continue
        data = load_json(pth) or {}
        if data.get("status") != "active":
            fail(f"rev0335 place-public-finance target is not active: cases/{name}")
        if "seed" in str(data.get("calibration_class", "")).lower():
            fail(f"rev0335 place-public-finance target still has seed calibration class: cases/{name}")
        if data.get("source_refresh_due") != spec["refresh_due"]:
            fail(f"rev0335 place-public-finance target has wrong source_refresh_due: cases/{name}")
        used = set(iter_source_ids_in_json(data))
        missing = spec["sources"] - used
        if missing:
            fail(f"rev0335 place-public-finance target missing expected sources {sorted(missing)}: cases/{name}")
        cert = (data.get("certification_gates") or {}).get("gate_15_place_public_finance") or {}
        if cert.get("status") != spec["gate_status"]:
            fail(f"rev0335 place-public-finance target has wrong Gate 15 status: cases/{name}")
        rows = data.get("evidence_debt_register") or []
        if len(rows) < 6:
            fail(f"rev0335 place-public-finance target lacks enough evidence-debt rows: cases/{name}")
        for i, row in enumerate(rows):
            if not isinstance(row, dict) or not row.get("source_ids"):
                fail(f"rev0335 place-public-finance target has unsourced evidence-debt row {i}: cases/{name}")
        gate_inv = (data.get("gate_inventory") or {}).get("gate_15_place_public_finance_service_wealth") or {}
        if gate_inv.get("status") != spec["gate_status"] or not gate_inv.get("source_ids"):
            fail(f"rev0335 place-public-finance target has wrong or unsourced Gate 15 inventory row: cases/{name}")
    audit = ROOT/"reports"/"seed-calibration-class-audit-rev0335.json"
    if not audit.exists():
        fail(f"Missing rev0335 seed-calibration-class audit: {audit.relative_to(ROOT)}")
        return
    data = load_json(audit) or {}
    fixed = {r.get("scoreboard_file", "") for r in data.get("corrected_this_revision", []) if isinstance(r, dict)}
    if not set(required).issubset(fixed):
        fail("rev0335 seed-calibration-class audit does not list all place-public-finance targets")
    remaining = data.get("remaining_active_seed_calibration_scoreboards", [])
    for r in remaining:
        if isinstance(r, dict) and r.get("scoreboard_file") in required:
            fail("rev0335 seed-calibration-class audit still lists a target as remaining seed calibration")
    sources = load_json(ROOT/"SOURCES.json") or {}
    by = {s.get("id"): s for s in sources.get("sources", [])}
    for sid in ["S245", "S246", "S257"]:
        s = by.get(sid, {})
        if s.get("source_type") == "official" or s.get("evidence_role") == "direct":
            fail(f"rev0335 source-fit refactor failed: {sid} still labeled official/direct")
    for sid in ["S466", "S467", "S468"]:
        if sid not in by:
            fail(f"rev0335 missing new source {sid}")
    ledger = load_json(ROOT/"docs/00-meta/currentness-ledger.json") or {}
    classes = {c.get("class") for c in ledger.get("currentness_classes", []) if isinstance(c, dict)}
    if "place_public_finance_official_data_release" not in classes or "place_public_finance_service_operability" not in classes:
        fail("rev0335 currentness ledger lacks place-public-finance currentness classes")



def check_rev0336_jurisdictional_mobility_hardening():
    required = {
        "eu-investor-citizenship-residence-rev0311-scoreboard.json": {"gate_status":"blocked", "sources":{"S203","S204","S206","S470"}, "refresh":"2026-12-31"},
        "united-kingdom-non-dom-transition-rev0311-scoreboard.json": {"gate_status":"watch", "sources":{"S207","S208","S209","S469"}, "refresh":"2026-12-31"},
        "global-high-wealth-migration-exit-threat-rev0311-scoreboard.json": {"gate_status":"watch", "sources":{"S180","S181","S210","S211","S212"}, "refresh":"2026-12-31"},
        "gulf-migrant-public-wealth-perimeter-rev0311-scoreboard.json": {"gate_status":"blocked", "sources":{"S216","S217","S218","S471"}, "refresh":"2026-09-30"},
        "remittance-dependence-transnational-family-burden-rev0311-scoreboard.json": {"gate_status":"watch", "sources":{"S218","S219","S471"}, "refresh":"2026-09-30"},
    }
    for name, spec in required.items():
        p = ROOT/"cases"/name
        if not p.exists():
            fail(f"Missing rev0336 jurisdictional-mobility target scoreboard: cases/{name}")
            continue
        data = load_json(p) or {}
        if data.get("status") != "active":
            fail(f"rev0336 jurisdictional-mobility target is not active: cases/{name}")
        if "seed" in str(data.get("calibration_class", "")).lower():
            fail(f"rev0336 jurisdictional-mobility target still has seed calibration class: cases/{name}")
        if data.get("source_refresh_due") != spec["refresh"]:
            fail(f"rev0336 jurisdictional-mobility target has wrong source_refresh_due: cases/{name}")
        sids = set(iter_source_ids_in_json(data))
        missing = spec["sources"] - sids
        if missing:
            fail(f"rev0336 jurisdictional-mobility target missing expected sources {sorted(missing)}: cases/{name}")
        fields = data.get("fields") or {}
        if "jurisdictional_mobility_gate" not in fields:
            fail(f"rev0336 jurisdictional-mobility target lacks jurisdictional_mobility_gate field: cases/{name}")
        rows = data.get("evidence_debt_register") or []
        if len(rows) < 6:
            fail(f"rev0336 jurisdictional-mobility target lacks enough evidence-debt rows: cases/{name}")
        for i, row in enumerate(rows):
            if not isinstance(row, dict) or not row.get("source_ids"):
                fail(f"rev0336 jurisdictional-mobility target has unsourced evidence-debt row {i}: cases/{name}")
        gate_inv = (data.get("gate_inventory") or {}).get("gate_13_jurisdictional_mobility_claimant_perimeter") or {}
        if gate_inv.get("status") != spec["gate_status"] or not gate_inv.get("source_ids"):
            fail(f"rev0336 jurisdictional-mobility target has wrong or unsourced Gate 13 inventory row: cases/{name}")
    audit = ROOT/"reports"/"seed-calibration-class-audit-rev0336.json"
    if not audit.exists():
        fail(f"Missing rev0336 seed-calibration-class audit: {audit.relative_to(ROOT)}")
        return
    data = load_json(audit) or {}
    fixed = {str(r.get("scoreboard_file", "")) for r in data.get("corrected_this_revision", []) if isinstance(r, dict)}
    if not set(required).issubset(fixed):
        fail("rev0336 seed-calibration-class audit does not list all jurisdictional-mobility targets")
    remaining = data.get("remaining_active_seed_calibration_scoreboards", [])
    for r in remaining:
        if isinstance(r, dict) and r.get("scoreboard_file") in required:
            fail("rev0336 seed-calibration-class audit still lists a target as remaining seed calibration")
    sources = load_json(ROOT/"SOURCES.json") or {}
    by = {s.get("id"): s for s in sources.get("sources", [])}
    for sid in ["S469", "S470", "S471"]:
        if sid not in by:
            fail(f"rev0336 missing new source {sid}")
    expected_fit = {
        "S206": ("official_judicial", "direct"),
        "S208": ("official", "direct"),
        "S211": ("nonprofit_research", "context"),
        "S212": ("academic_research", "context"),
        "S216": ("multilateral_research", "context"),
        "S217": ("official_statistical_report", "direct"),
    }
    for sid, (stype, role) in expected_fit.items():
        s = by.get(sid, {})
        if s.get("source_type") != stype or s.get("evidence_role") != role:
            fail(f"rev0336 source-fit refactor failed for {sid}: expected {stype}/{role}")
    ledger = load_json(ROOT/"docs/00-meta/currentness-ledger.json") or {}
    classes = {c.get("class") for c in ledger.get("currentness_classes", []) if isinstance(c, dict)}
    if "jurisdictional_mobility_current_law_or_rule_watch" not in classes or "jurisdictional_mobility_flow_or_price_release" not in classes:
        fail("rev0336 currentness ledger lacks jurisdictional-mobility currentness classes")



def check_rev0337_seedclass_backlog_closure():
    democratic = {
        "united-states-democratic-wealth-power-rev0310-scoreboard.json": {"sources":{"S184","S185","S186","S188","S189","S473"}, "gate":"gate_12_democratic_non_domination", "gate_status":"blocked", "refresh":"2026-12-31"},
        "united-kingdom-political-finance-rev0310-scoreboard.json": {"sources":{"S192","S193","S194"}, "gate":"gate_12_democratic_non_domination", "gate_status":"watch", "refresh":"2026-12-31"},
        "eu-media-pluralism-agenda-power-rev0310-scoreboard.json": {"sources":{"S190","S191","S472"}, "gate":"gate_12_democratic_non_domination", "gate_status":"watch", "refresh":"2026-12-31"},
        "local-land-use-homeowner-veto-rev0310-scoreboard.json": {"sources":{"S195","S202","S473"}, "gate":"gate_12_democratic_non_domination", "gate_status":"blocked", "refresh":"2026-12-31"},
    }
    portfolio = {
        "united-states-rev0304-scoreboard.json": {"sources":{"S02","S55","S70","S374","S84","S184","S473"}, "refresh":"2026-09-30"},
        "alaska-permanent-fund-rev0304-scoreboard.json": {"sources":{"S81","S82","S374"}, "refresh":"2026-10-31"},
        "netherlands-rev0304-scoreboard.json": {"sources":{"S71","S72","S197"}, "refresh":"2026-11-30"},
        "singapore-rev0304-scoreboard.json": {"sources":{"S77","S79","S474"}, "refresh":"2026-12-31"},
        "south-africa-rev0304-scoreboard.json": {"sources":{"S74","S75","S76","S85","S475"}, "refresh":"2026-09-30"},
        "us-climate-insurance-rev0304-scoreboard.json": {"sources":{"S374","S84"}, "refresh":"2026-09-30"},
    }
    all_req = {**democratic, **portfolio}
    for pth in sorted((ROOT/"cases").glob("*-scoreboard.json")):
        data = load_json(pth) or {}
        if data.get("status") == "active" and "seed" in str(data.get("calibration_class", "")).lower():
            fail(f"active scoreboard retains seed calibration class after rev0337: {pth.relative_to(ROOT)}")
    for name, spec in all_req.items():
        pth = ROOT/"cases"/name
        if not pth.exists():
            fail(f"Missing rev0337 target scoreboard: cases/{name}")
            continue
        data = load_json(pth) or {}
        if data.get("status") != "active":
            fail(f"rev0337 target is not active: cases/{name}")
        if "seed" in str(data.get("calibration_class", "")).lower():
            fail(f"rev0337 target still has seed calibration class: cases/{name}")
        if data.get("source_refresh_due") != spec["refresh"]:
            fail(f"rev0337 target has wrong source_refresh_due: cases/{name}")
        used = set(iter_source_ids_in_json(data))
        missing = spec["sources"] - used
        if missing:
            fail(f"rev0337 target missing expected sources {sorted(missing)}: cases/{name}")
        rows = data.get("evidence_debt_register") or []
        if len(rows) < 6:
            fail(f"rev0337 target lacks enough evidence-debt rows: cases/{name}")
        for i, row in enumerate(rows):
            if not isinstance(row, dict) or not row.get("source_ids"):
                fail(f"rev0337 target has unsourced evidence-debt row {i}: cases/{name}")
        if name in democratic:
            cert = (data.get("certification_gates") or {}).get(spec["gate"]) or {}
            if cert.get("status") != spec["gate_status"] or not cert.get("source_ids"):
                fail(f"rev0337 democratic target has wrong or unsourced Gate 12 certification: cases/{name}")
    audit = ROOT/"reports"/"seed-calibration-class-audit-rev0337.json"
    if not audit.exists():
        fail(f"Missing rev0337 seed-calibration-class audit: {audit.relative_to(ROOT)}")
    else:
        data = load_json(audit) or {}
        if data.get("remaining_active_seed_calibration_count") != 0 or data.get("remaining_active_seed_calibration_scoreboards"):
            fail("rev0337 seed-calibration-class audit must show zero remaining active seed calibration labels")
    sources = load_json(ROOT/"SOURCES.json") or {}
    by = {s.get("id"): s for s in sources.get("sources", [])}
    for sid in ["S472","S473","S474","S475"]:
        if sid not in by:
            fail(f"rev0337 missing new source {sid}")
    expected_fit = {
        "S186": ("nonprofit_research", "context"),
        "S190": ("commission_published_research", "context"),
        "S193": ("official_parliamentary_report", "direct"),
        "S194": ("official_report", "direct"),
        "S70": ("official_statistical_release", "direct"),
        "S71": ("official_statistical_release", "direct"),
        "S72": ("official_statistical_table", "direct"),
        "S77": ("official_statistical_report", "direct"),
        "S81": ("official_report", "direct"),
        "S84": ("official_statistical_dataset", "direct"),
    }
    for sid, (stype, role) in expected_fit.items():
        s = by.get(sid, {})
        if s.get("source_type") != stype or s.get("evidence_role") != role:
            fail(f"rev0337 source-fit refactor failed for {sid}: expected {stype}/{role}")
    ledger = load_json(ROOT/"docs/00-meta/currentness-ledger.json") or {}
    classes = {c.get("class") for c in ledger.get("currentness_classes", []) if isinstance(c, dict)}
    if "democratic_power_political_finance_or_media_currentness" not in classes or "portfolio_foundation_wealth_floor_or_stress_release" not in classes:
        fail("rev0337 currentness ledger lacks democratic/portfolio currentness classes")



def check_rev0338_evidence_debt_source_anchor_refactor():
    # Global invariant: after rev0338 no active scoreboard may carry unsourced evidence-debt rows.
    for pth in sorted((ROOT/"cases").glob("*-scoreboard.json")):
        data = load_json(pth) or {}
        if data.get("status") != "active":
            continue
        for i, row in enumerate(data.get("evidence_debt_register") or []):
            if not isinstance(row, dict) or not row.get("source_ids"):
                fail(f"active scoreboard has unsourced evidence-debt row {i} after rev0338: {pth.relative_to(ROOT)}")
    targets = {
        "canada-rev0305-scoreboard.json": {"S476"},
        "india-rev0305-scoreboard.json": {"S477", "S478"},
        "united-kingdom-rev0305-scoreboard.json": {"S479", "S480", "S481"},
        "vienna-social-housing-rev0305-scoreboard.json": {"S482", "S483"},
        "federal-reserve-balance-sheet-quasi-fiscal-rev0318-scoreboard.json": {"S484", "S485", "S486"},
    }
    for name, expected in targets.items():
        pth = ROOT/"cases"/name
        if not pth.exists():
            fail(f"Missing rev0338 target scoreboard: cases/{name}")
            continue
        data = load_json(pth) or {}
        used = set(iter_source_ids_in_json(data))
        missing = expected - used
        if missing:
            fail(f"rev0338 target missing expected source anchors {sorted(missing)}: cases/{name}")
    fed = load_json(ROOT/"cases/federal-reserve-balance-sheet-quasi-fiscal-rev0318-scoreboard.json") or {}
    if fed.get("source_refresh_due") != "2026-09-30":
        fail("rev0338 Fed quasi-fiscal case must refresh by 2026-09-30")
    audit = ROOT/"reports"/"unsourced-evidence-debt-audit-rev0338.json"
    if not audit.exists():
        fail(f"Missing rev0338 unsourced evidence-debt audit: {audit.relative_to(ROOT)}")
    else:
        data = load_json(audit) or {}
        if data.get("remaining_unsourced_evidence_debt_count") != 0 or data.get("remaining_unsourced_evidence_debt_rows"):
            fail("rev0338 unsourced evidence-debt audit must show zero remaining rows")
    sources = load_json(ROOT/"SOURCES.json") or {}
    by = {s.get("id"): s for s in sources.get("sources", [])}
    for sid in ["S476","S477","S478","S479","S480","S481","S482","S483","S484","S485","S486"]:
        if sid not in by:
            fail(f"rev0338 missing new source {sid}")
    expected_fit = {
        "S87": ("official_statistics_quality_limited", "direct_with_quality_caveat"),
        "S90": ("official_parliamentary_report", "direct"),
        "S95": ("official_municipal_policy", "direct"),
        "S96": ("nonprofit_research", "context"),
    }
    for sid, (stype, role) in expected_fit.items():
        s = by.get(sid, {})
        if s.get("source_type") != stype or s.get("evidence_role") != role:
            fail(f"rev0338 source-fit refactor failed for {sid}: expected {stype}/{role}")
    ledger = load_json(ROOT/"docs/00-meta/currentness-ledger.json") or {}
    classes = {c.get("class") for c in ledger.get("currentness_classes", []) if isinstance(c, dict)}
    for klass in ["measurement_evidence_debt_anchor", "central_bank_quasi_fiscal_current_release", "housing_outcome_conversion_release"]:
        if klass not in classes:
            fail(f"rev0338 currentness ledger lacks {klass}")



def check_rev0339_currentness_coverage_and_validator_callchain():
    # Global invariant: every active scoreboard must have a currentness-ledger row with matching refresh_due.
    ledger = load_json(ROOT/"docs/00-meta/currentness-ledger.json") or {}
    rows = {r.get("case_id"): r for r in ledger.get("case_rows", []) if isinstance(r, dict)}
    missing = []
    mismatched = []
    for p in sorted((ROOT/"cases").glob("*-scoreboard.json")):
        data = load_json(p) or {}
        if data.get("status") != "active":
            continue
        cid = data.get("case_id")
        row = rows.get(cid)
        if not row:
            missing.append(cid)
            continue
        if row.get("refresh_due") != data.get("source_refresh_due"):
            mismatched.append((cid, data.get("source_refresh_due"), row.get("refresh_due")))
    if missing:
        fail(f"rev0339 currentness coverage missing active case rows: {missing[:20]}")
    if mismatched:
        fail(f"rev0339 currentness coverage refresh mismatches: {mismatched[:20]}")
    # Global invariant: any live gate row must be auditable to source ids.
    for p in sorted((ROOT/"cases").glob("*-scoreboard.json")):
        data = load_json(p) or {}
        if data.get("status") != "active":
            continue
        for gate, row in (data.get("gate_inventory") or {}).items():
            if isinstance(row, dict) and row.get("status") in {"passed", "watch", "blocked", "missing"} and not row.get("source_ids"):
                fail(f"rev0339 non-not-applicable gate inventory row lacks source_ids: {p.relative_to(ROOT)}::{gate}")
    # Self-audit the callchain so defined revision-hardening checks cannot sit idle again.
    text = (ROOT/"tools"/"validate_archive.py").read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"def main\(\):(?P<body>.*?)(?:\nif __name__ ==)", text, re.S)
    body = m.group("body") if m else ""
    expected_calls = [
        "check_rev0327_backstop_status_parity",
        "check_rev0328_federal_claim_security_burndown",
        "check_rev0329_sovereign_public_fiscal_burndown",
        "check_rev0330_score_mediated_exclusion_burndown",
        "check_rev0331_gate18_gate19_backlog_closure",
        "check_rev0332_seed_backlog_closure",
        "check_rev0333_workplace_power_current_law_hardening",
        "check_rev0334_household_market_extraction_hardening",
        "check_rev0335_place_public_finance_hardening",
        "check_rev0336_jurisdictional_mobility_hardening",
        "check_rev0337_seedclass_backlog_closure",
        "check_rev0338_evidence_debt_source_anchor_refactor",
        "check_rev0339_currentness_coverage_and_validator_callchain",
        "check_rev0340_memo_citation_lineage_and_alias_canonicalization",
        "check_rev0341_case_memo_status_language_repair",
    ]
    for call in expected_calls:
        if call + "()" not in body:
            fail(f"validator main() does not call {call}()")
    report = ROOT/"reports"/f"currentness-ledger-coverage-and-validator-callchain-repair-rev0339.json"
    if not report.exists():
        fail(f"Missing rev0339 currentness/callchain repair report: {report.relative_to(ROOT)}")
        return
    data = load_json(report) or {}
    if data.get("case_rows_added_count") != 19:
        fail("rev0339 repair report should record 19 added currentness case rows")
    if data.get("remaining_missing_currentness_case_rows"):
        fail("rev0339 repair report should show zero missing currentness rows")
    if data.get("remaining_non_na_gate_inventory_rows_without_sources"):
        fail("rev0339 repair report should show zero unsourced live gate rows")
    sources = load_json(ROOT/"SOURCES.json") or {}
    by = {s.get("id"): s for s in sources.get("sources", [])}
    for sid in ["S487", "S488", "S489"]:
        if sid not in by:
            fail(f"rev0339 missing new source {sid}")
    expected_fit = {
        "S162": ("official_statistical_release", "direct_with_quality_caveat"),
        "S169": ("official_current_status_page", "direct"),
        "S172": ("official_portal", "direct_with_access_caveat"),
        "S173": ("official_legal_text", "direct"),
        "S174": ("official_legal_text", "direct"),
        "S183": ("multilateral_research", "context"),
    }
    for sid, (stype, role) in expected_fit.items():
        s = by.get(sid, {})
        if s.get("source_type") != stype or s.get("evidence_role") != role:
            fail(f"rev0339 source-fit refactor failed for {sid}: expected {stype}/{role}")



def check_rev0340_memo_citation_lineage_and_alias_canonicalization():
    alias_to_canon = {
        "S107":"S379", "S83":"S374", "S128":"S262", "S63":"S435", "S154":"S431", "S121":"S263", "S171":"S433", "S377":"S359", "S432":"S169", "S65":"S418", "S325":"S430", "S438":"S378", "S80":"S369", "S314":"S260", "S114":"S196", "S385":"S356", "S16":"S142", "S40":"S139", "S53":"S197"
    }
    alias_ids = set(alias_to_canon)
    # No active case scoreboard or case memo may cite retained aliases.
    for p in sorted((ROOT/"cases").glob("*-scoreboard.json")):
        data = load_json(p) or {}
        used = set(iter_source_ids_in_json(data))
        bad = sorted(used & alias_ids)
        if bad:
            fail(f"rev0340 retained alias source ids still used in scoreboard {p.relative_to(ROOT)}: {bad}")
    for p in sorted((ROOT/"cases").glob("*-case.md")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        used = {"S"+n for n in re.findall(r"\[S(\d{2,3})\]", text)}
        bad = sorted(used & alias_ids)
        if bad:
            fail(f"rev0340 retained alias source ids still used in case memo {p.relative_to(ROOT)}: {bad}")
    sources = load_json(ROOT/"SOURCES.json") or {}
    by = {s.get("id"): s for s in sources.get("sources", [])}
    for alias, canon in alias_to_canon.items():
        s = by.get(alias, {})
        if s.get("alias_of") != canon or not s.get("retained_alias"):
            fail(f"rev0340 alias metadata missing for {alias}->{canon}")
        if s.get("used_by_cases") or s.get("used_by_fields"):
            fail(f"rev0340 retained alias has nonempty use metadata: {alias}")
    if by.get("S169", {}).get("refresh_due") != "2026-09-30":
        fail("rev0340 S169 BOI current-status source must refresh by 2026-09-30")
    boi = load_json(ROOT/"cases/united-states-beneficial-ownership-reversal-rev0309-scoreboard.json") or {}
    if boi.get("source_refresh_due") != "2026-09-30":
        fail("rev0340 U.S. BOI reversal case must refresh by 2026-09-30")
    ledger = load_json(ROOT/"cases/EVIDENCE_LEDGER.json") or {}
    memo_edges = [r for r in ledger.get("edge_rows", []) if isinstance(r, dict) and r.get("claim_path") == "case_memo"]
    if not memo_edges:
        fail("rev0340 EVIDENCE_LEDGER must include case_memo citation edges")
    report = ROOT/"reports"/f"source-alias-and-memo-citation-lineage-repair-rev0340.json"
    if not report.exists():
        fail(f"Missing rev0340 source-alias/memo-citation repair report: {report.relative_to(ROOT)}")
    else:
        data = load_json(report) or {}
        if data.get("active_alias_reference_remaining_count") != 0:
            fail("rev0340 report must show zero active alias references remaining")
        if data.get("case_memo_source_edges_added_to_evidence_ledger", 0) <= 0:
            fail("rev0340 report must record memo citation evidence edges")
    dup = load_json(ROOT/"docs/00-meta/source-duplicate-audit.json") or {}
    if dup.get("canonicalized_url_group_count", 0) < 10:
        fail("rev0340 duplicate audit should record canonicalized duplicate URL groups")


def check_rev0341_case_memo_status_language_repair():
    # After rev0341, active case-facing files may describe cases as bounded/proxy/stress,
    # but must not call an active case seed, seed/proxy, seed stress, or active-seed.
    stale = [
        r"active seed case",
        r"active seed\b",
        r"seed stress case",
        r"seed/proxy case",
        r"not scored in seed case",
        r"seed read",
        r"active-seed",
        r"active-seed-closure",
        r"case is a seed stress case",
    ]
    pats = [re.compile(p, re.I) for p in stale]
    # Pair active memos with active scoreboards.
    active_bases = set()
    for p in (ROOT/"cases").glob("*-scoreboard.json"):
        data = load_json(p) or {}
        if data.get("status") == "active":
            active_bases.add(p.name[:-len("-scoreboard.json")])
            text = json.dumps(data, ensure_ascii=False)
            for pat in pats:
                if pat.search(text):
                    fail(f"rev0341 stale seed-status language remains in active scoreboard {p.relative_to(ROOT)}: {pat.pattern}")
    for p in (ROOT/"cases").glob("*-case.md"):
        base = p.name[:-len("-case.md")]
        if base not in active_bases:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for pat in pats:
            if pat.search(text):
                fail(f"rev0341 stale seed-status language remains in active case memo {p.relative_to(ROOT)}: {pat.pattern}")
    report = ROOT/"reports"/"case-memo-status-drift-and-stale-seed-language-repair-rev0341.json"
    if not report.exists():
        fail(f"Missing rev0341 stale seed-language repair report: {report.relative_to(ROOT)}")
    else:
        data = load_json(report) or {}
        if data.get("post_repair_active_case_files_with_stale_seed_language_count") != 0:
            fail("rev0341 report must show zero remaining stale seed-status active files")
        if data.get("new_sources") != 0 or data.get("new_cases") != 0 or data.get("new_schema_fields") != 0:
            fail("rev0341 should not widen sources/cases/schema while repairing status-language drift")



def check_rev0342_case_identity_lineage_canonicalization():
    """Case identity fields should use canonical case slugs, not memo filenames."""
    canonical_bases = {p.name[:-len("-scoreboard.json")] for p in (ROOT/"cases").glob("*-scoreboard.json")}
    mismatch_count = 0
    for score in sorted((ROOT/"cases").glob("*-scoreboard.json")):
        base = score.name[:-len("-scoreboard.json")]
        data = load_json(score) or {}
        cid = data.get("case_id")
        if cid != base:
            mismatch_count += 1
            fail(f"rev0342 canonical case_id mismatch: {score.relative_to(ROOT)} has {cid!r}, expected {base!r}")
        if isinstance(cid, str) and cid.endswith("-case"):
            fail(f"rev0342 active scoreboard uses memo-style case_id: {score.relative_to(ROOT)}")
    # Authoritative ledgers should not use memo-style case IDs for active case identity.
    authoritative = [
        ROOT/"SOURCES.json",
        ROOT/"cases"/"CASE_LEDGER.json",
        ROOT/"cases"/"EVIDENCE_LEDGER.json",
        ROOT/"docs"/"00-meta"/"currentness-ledger.json",
        ROOT/"docs"/"00-meta"/"field-registry.json",
        ROOT/"docs"/"00-meta"/"field-use-ledger.json",
        ROOT/"docs"/"00-meta"/"source-use-register.json",
    ]
    def walk_values(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                yield from walk_values(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                yield from walk_values(v, f"{path}[{i}]")
        elif isinstance(obj, str):
            yield path, obj
    for path in authoritative:
        data = load_json(path) or {}
        for jpath, val in walk_values(data):
            # Memo file paths such as cases/foo-case.md are allowed; case identity values ending in -case are not.
            if val.endswith("-case") and val[:-5] in canonical_bases:
                fail(f"rev0342 memo-style case identity remains in {path.relative_to(ROOT)}::{jpath}: {val}")
    report = ROOT/"reports"/"case-identity-lineage-canonicalization-rev0342.json"
    if not report.exists():
        fail(f"Missing rev0342 case identity lineage report: {report.relative_to(ROOT)}")
    else:
        data = load_json(report) or {}
        if data.get("pre_repair_scoreboard_case_id_mismatch_count") != 51:
            fail("rev0342 report should record the 51 pre-repair case_id mismatches")
        if data.get("post_repair_scoreboard_case_id_mismatch_count") != 0:
            fail("rev0342 report must show zero post-repair case_id mismatches")
        if data.get("post_repair_authoritative_case_id_suffix_count") != 0:
            fail("rev0342 report must show zero remaining authoritative memo-style case IDs")
        if data.get("new_sources") != 0 or data.get("new_cases") != 0 or data.get("new_schema_fields") != 0:
            fail("rev0342 should not widen sources/cases/schema while repairing case identity lineage")


def check_rev0343_live_doc_source_alias_canonicalization():
    sources = (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])
    alias_map = {}
    for s in sources:
        if s.get("source_type") == "retained_alias" or s.get("retained_alias"):
            sid = s.get("id")
            canon = s.get("canonical_source_id") or s.get("alias_of")
            if not canon:
                fail(f"retained alias {sid} lacks canonical_source_id/alias_of")
                continue
            if s.get("canonical_source_id") != canon or s.get("alias_of") != canon:
                fail(f"retained alias {sid} has inconsistent canonical alias metadata")
            if s.get("duplicate_status") != "retired_alias":
                fail(f"retained alias {sid} must have duplicate_status retired_alias")
            if s.get("evidence_role") != "retained_alias_no_active_use":
                fail(f"retained alias {sid} must have retained_alias_no_active_use evidence_role")
            alias_map[sid] = canon
    def live_path(path):
        rel = str(path.relative_to(ROOT))
        if rel.startswith("reports/"):
            return False
        if rel in {"SOURCES.json", "SOURCES.md", "MANIFEST.json", "MANIFEST.sha256"}:
            return False
        if rel.startswith("docs/00-meta/") and re.search(r"(audit-rev\d{4}|source-duplicate-audit|source-use-register|currentness-ledger|field-registry|field-use-ledger|route-ledger)", rel):
            return False
        return path.suffix in {".md", ".json"}
    for p in ROOT.rglob("*"):
        if not p.is_file() or not live_path(p):
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for sid in alias_map:
            if re.search(rf"(?<![A-Z0-9]){re.escape(sid)}(?!\d)", text):
                fail(f"live file retains retired source alias {sid}: {p.relative_to(ROOT)}")
    report = ROOT/"reports"/"live-doc-source-alias-canonicalization-rev0343.json"
    if not report.exists():
        fail("Missing rev0343 live-doc source alias canonicalization report")
    else:
        data = load_json(report) or {}
        if data.get("post_live_alias_reference_count") != 0:
            fail("rev0343 report must show zero post-repair live alias references")
        if data.get("post_retained_alias_rows_missing_canonical_source_id") != 0:
            fail("rev0343 report must show all retained aliases have canonical_source_id")
        if data.get("new_sources") != 0 or data.get("new_cases") != 0 or data.get("new_schema_fields") != 0:
            fail("rev0343 should not widen sources/cases/schema while repairing source-alias lineage")



def check_rev0344_unused_source_burndown_and_validator_callchain():
    """rev0344: prevent high-value non-alias sources from floating unused and ensure latest invariants are called."""
    report_path = ROOT/"reports"/"unused-source-burndown-and-validator-callchain-hardening-rev0344.json"
    if not report_path.exists():
        fail("Missing rev0344 unused-source burn-down report")
        return
    report = load_json(report_path) or {}
    target_sources = set(report.get("target_source_ids", []))
    if report.get("pre_unused_non_alias_source_count") != 45:
        fail("rev0344 report should record 45 pre-repair unused non-alias sources")
    if report.get("post_target_sources_still_unused") != []:
        fail("rev0344 report must show no target sources still unused")
    if report.get("post_unused_non_alias_source_count") != 0:
        fail("rev0344 report must show zero remaining non-alias unused sources")
    if report.get("new_sources") != 0 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0344 should not widen sources/cases/schema while burning down unused-source drift")
    sources = {s.get("id"): s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", []) if isinstance(s, dict)}
    for sid in sorted(target_sources):
        row = sources.get(sid)
        if not row:
            fail(f"rev0344 target source missing from SOURCES.json: {sid}")
            continue
        if row.get("retained_alias") or row.get("source_type") == "retained_alias":
            fail(f"rev0344 target source should not be a retained alias: {sid}")
        if not row.get("used_by_cases"):
            fail(f"rev0344 target source remains unused: {sid}")
    # Make the validator callchain self-aware enough to catch the exact rev0343 omission fixed here.
    try:
        tree = ast.parse((ROOT/"tools"/"validate_archive.py").read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"Could not parse validator for callchain audit: {e}")
        return
    main = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main"), None)
    if main is None:
        fail("validator has no main() for callchain audit")
        return
    called = {n.func.id for n in ast.walk(main) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    required = {
        "check_rev0339_currentness_coverage_and_validator_callchain",
        "check_rev0340_memo_citation_lineage_and_alias_canonicalization",
        "check_rev0341_case_memo_status_language_repair",
        "check_rev0342_case_identity_lineage_canonicalization",
        "check_rev0343_live_doc_source_alias_canonicalization",
        "check_rev0344_unused_source_burndown_and_validator_callchain",
    }
    missing = required - called
    if missing:
        fail(f"validator main() is missing recent invariant call(s): {sorted(missing)}")




def check_rev0345_frontdoor_reality_audit_and_changelog_repair():
    """Historical rev0345 check: preserve the repair receipt without making it chase later counts."""
    report_path = ROOT/"reports"/"frontdoor-reality-audit-and-changelog-repair-rev0345.json"
    if not report_path.exists():
        fail("Missing rev0345 front-door reality audit report JSON")
        return
    report = load_json(report_path) or {}
    if report.get("revision") != "rev0345":
        fail("rev0345 report revision mismatch")
    if report.get("base_revision") != "rev0344":
        fail("rev0345 report base_revision mismatch")
    if report.get("codename") != "frontdoor-reality-audit-changelogrepair":
        fail("rev0345 report codename mismatch")
    if report.get("new_sources") != 0 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0345 should not add sources, cases, or schema fields")

    expected_counts = {
        "case_memo_count": 95,
        "scoreboard_count": 95,
        "case_ledger_count": 95,
        "source_count": 489,
        "schema_field_count": 367,
        "registered_unused_field_count": 50,
        "evidence_edge_count": 5407,
    }
    report_counts = report.get("current_counts") or {}
    for key, val in expected_counts.items():
        if report_counts.get(key) != val:
            fail(f"rev0345 report current_counts.{key}={report_counts.get(key)!r} does not match rev0345 receipt {val!r}")

    changelog = (ROOT/"CHANGELOG.md").read_text(encoding="utf-8", errors="ignore")
    if changelog.count("## rev0345") != 1:
        fail("CHANGELOG must contain exactly one rev0345 heading")
    if changelog.count("## rev0344") != 1:
        fail("CHANGELOG must contain exactly one rev0344 heading")
    if changelog.find("## rev0345") > changelog.find("## rev0344"):
        fail("CHANGELOG must keep rev0345 above rev0344")
    if changelog.count("# Changelog") != 1:
        fail("CHANGELOG must contain exactly one top-level # Changelog heading")
    if changelog.count("## rev0342") != 1:
        fail("CHANGELOG must contain exactly one rev0342 heading after rev0341 repair")
    if "## rev0341" not in changelog:
        fail("CHANGELOG must expose a rev0341 heading")
    if "## rev0324" not in changelog:
        fail("CHANGELOG must expose a rev0324 heading")
    for rev in ["rev0332", "rev0331", "rev0330", "rev0329", "rev0328", "rev0327"]:
        if changelog.count("## " + rev) != 1:
            fail(f"CHANGELOG must contain exactly one {rev} heading")
    first_block_end = changelog.find("\n---", 4)
    rest = changelog[first_block_end+4:] if first_block_end != -1 else changelog
    if re.search(r"(?m)^---\s*\nrevision_current:", rest):
        fail("CHANGELOG contains an embedded duplicate frontmatter block")

    # Generalize the rev0344 callchain lesson: every top-level check_* function must be called by main().
    try:
        tree = ast.parse((ROOT/"tools"/"validate_archive.py").read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"Could not parse validator for rev0345 callchain audit: {e}")
        return
    main = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main"), None)
    if main is None:
        fail("validator has no main() for rev0345 callchain audit")
        return
    defs = {n.name for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("check_")}
    called = {n.func.id for n in ast.walk(main) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id.startswith("check_")}
    missing = sorted(defs - called)
    if missing:
        fail(f"validator main() is missing check function(s): {missing}")


def check_rev0346_volatile_currentness_and_sourcefit_refactor():
    report_path = ROOT/"reports"/"volatile-currentness-and-sourcefit-refactor-rev0346.json"
    if not report_path.exists():
        fail("Missing rev0346 volatile-currentness/source-fit report JSON")
        return
    report = load_json(report_path) or {}
    if report.get("revision") != "rev0346":
        fail("rev0346 report revision mismatch")
    if report.get("base_revision") != "rev0345":
        fail("rev0346 report base_revision mismatch")
    if report.get("codename") != "volatile-currentness-and-sourcefit-refactor":
        fail("rev0346 report codename mismatch")
    if report.get("new_sources") != 3 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0346 should add exactly three sources and no cases/schema fields")
    if sorted(report.get("new_source_ids") or []) != ["S490", "S491", "S492"]:
        fail("rev0346 report new_source_ids mismatch")

    # Historical receipt check only: later releases may change front-door counts and CHANGELOG order.
    expected_counts = {
        "case_memo_count": 95,
        "scoreboard_count": 95,
        "source_count": 492,
        "schema_field_count": 367,
        "registered_unused_field_count": 50,
        "evidence_edge_count": 5435,
    }
    report_counts = report.get("current_counts") or {}
    for key, val in expected_counts.items():
        if report_counts.get(key) != val:
            fail(f"rev0346 report current_counts.{key}={report_counts.get(key)!r} does not match rev0346 receipt {val!r}")

    sources = {s.get("id"): s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    expected_sources = {
        "S490": ("official_financial_statistical_release", "direct", "2026-09-30"),
        "S491": ("official_current_status_page", "direct", "2026-09-30"),
        "S492": ("official_regulatory_proceeding", "direct", "2026-09-30"),
    }
    for sid, (stype, role, due) in expected_sources.items():
        s = sources.get(sid)
        if not s:
            fail(f"Missing rev0346 source {sid}")
            continue
        if s.get("source_type") != stype or s.get("evidence_role") != role or s.get("refresh_due") != due:
            fail(f"rev0346 source metadata mismatch for {sid}")

    expected_fit = {
        "S12": ("nonprofit_modeling", "context"),
        "S106": ("nonprofit_research", "context"),
        "S117": ("think_tank_research", "context"),
        "S131": ("nonprofit_gse_methodology", "direct_with_methodology_caveat"),
        "S283": ("official_list_with_coverage_caveat", "direct_with_coverage_caveat"),
        "S285": ("official_historical_rule_notice", "context"),
        "S310": ("nonprofit_policy_tracker", "context"),
        "S318": ("advocacy_legal_update", "context"),
        "S339": ("professional_association_reference", "context"),
        "S343": ("advocacy_research", "context"),
        "S390": ("national_lab_technical_report", "direct"),
        "S393": ("national_lab_literature_review", "context"),
        "S407": ("official_technical_standard", "direct"),
        "S424": ("community_development_research", "context"),
    }
    for sid, (stype, role) in expected_fit.items():
        s = sources.get(sid)
        if not s:
            fail(f"Missing source-fit refactor source {sid}")
            continue
        if s.get("source_type") != stype or s.get("evidence_role") != role:
            fail(f"rev0346 source-fit metadata mismatch for {sid}")

    scoreboard_requirements = {
        "cases/united-states-rev0304-scoreboard.json": "S490",
        "cases/macro-consistent-wealth-accounts-rev0308-scoreboard.json": "S490",
        "cases/ai-data-center-grid-water-public-backstop-rev0320-scoreboard.json": "S492",
        "cases/united-states-beneficial-ownership-reversal-rev0309-scoreboard.json": "S491",
    }
    for rel, sid in scoreboard_requirements.items():
        data = load_json(ROOT/rel) or {}
        found = False
        def walk(obj):
            nonlocal found
            if isinstance(obj, dict):
                if sid in (obj.get("source_ids") or []):
                    found = True
                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for v in obj:
                    walk(v)
        walk(data)
        if not found:
            fail(f"rev0346 required source {sid} missing from {rel}")
    macro = load_json(ROOT/"cases"/"macro-consistent-wealth-accounts-rev0308-scoreboard.json") or {}
    if macro.get("source_refresh_due") != "2026-09-30":
        fail("rev0346 macro measurement case must refresh by 2026-09-30")
    med = load_json(ROOT/"cases"/"united-states-credit-reporting-medical-debt-rev0315-scoreboard.json") or {}
    med_text = json.dumps(med, sort_keys=True)
    if "historical-rule context" not in med_text or "coverage-caveated" not in med_text:
        fail("rev0346 medical-debt scoreboard must document historical-rule and coverage caveats")

    currentness = load_json(ROOT/"docs"/"00-meta"/"currentness-ledger.json") or {}
    source_rows = {r.get("source_id"): r for r in currentness.get("source_rows", [])}
    for sid in ["S490", "S491", "S492"]:
        if sid not in source_rows:
            fail(f"rev0346 currentness ledger missing source row {sid}")
    macro_rows = [r for r in currentness.get("case_rows", []) if r.get("case_id") == "macro-consistent-wealth-accounts-rev0308"]
    if not macro_rows or macro_rows[0].get("refresh_due") != "2026-09-30":
        fail("rev0346 currentness ledger must shorten macro case refresh_due to 2026-09-30")



def check_rev0347_dfa_share_extraction_and_gridload_incidence():
    report_path = ROOT/"reports"/"dfa-share-extraction-and-gridload-incidence-rev0347.json"
    if not report_path.exists():
        fail("Missing rev0347 DFA share/load-incidence report JSON")
        return
    report = load_json(report_path) or {}
    if report.get("revision") != "rev0347":
        fail("rev0347 report revision mismatch")
    if report.get("base_revision") != "rev0346":
        fail("rev0347 report base_revision mismatch")
    if report.get("codename") != "dfa-share-extraction-and-gridload-incidence":
        fail("rev0347 report codename mismatch")
    if report.get("new_sources") != 3 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0347 should add exactly three sources and no cases/schema fields")
    if sorted(report.get("new_source_ids") or []) != ["S493", "S494", "S495"]:
        fail("rev0347 report new_source_ids mismatch")

    # Historical receipt check only: later releases may change front-door counts and CHANGELOG order.
    expected_counts = {
        "case_memo_count": 95,
        "scoreboard_count": 95,
        "source_count": 495,
        "schema_field_count": 367,
        "registered_unused_field_count": 50,
        "evidence_edge_count": 5478,
    }
    report_counts = report.get("current_counts") or {}
    for key, val in expected_counts.items():
        if report_counts.get(key) != val:
            fail(f"rev0347 report current_counts.{key}={report_counts.get(key)!r} does not match rev0347 receipt {val!r}")

    changelog = (ROOT/"CHANGELOG.md").read_text(encoding="utf-8", errors="ignore")
    if "## rev0347 — dfa-share-extraction-and-gridload-incidence" not in changelog:
        fail("CHANGELOG missing rev0347 historical heading")

    sources = {s.get("id"): s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    expected_sources = {
        "S493": ("official_distributional_financial_accounts_release_table", "direct", "2026-09-30"),
        "S494": ("official_grid_load_forecast", "direct_with_forecast_uncertainty", "2027-01-31"),
        "S495": ("official_energy_statistical_analysis", "direct", "2026-12-31"),
    }
    for sid, (stype, role, due) in expected_sources.items():
        s = sources.get(sid)
        if not s:
            fail(f"Missing rev0347 source {sid}")
            continue
        if s.get("source_type") != stype or s.get("evidence_role") != role or s.get("refresh_due") != due:
            fail(f"rev0347 source metadata mismatch for {sid}")

    us = load_json(ROOT/"cases"/"united-states-rev0304-scoreboard.json") or {}
    fields = us.get("fields") or {}
    expected_us_values = {
        "bottom_50_private_wealth_share": 2.5,
        "middle_40_private_wealth_share": 29.2,
        "next_9_private_wealth_share": 36.4,
        "top_1_private_wealth_share": 31.9,
        "top_0_1_private_wealth_share": 14.5,
    }
    for field, val in expected_us_values.items():
        item = fields.get(field) or {}
        if item.get("value") != val or "S493" not in (item.get("source_ids") or []):
            fail(f"rev0347 U.S. exact DFA share missing for {field}")
        if item.get("year") != "2025:Q4" or item.get("evidence_quality") != "direct":
            fail(f"rev0347 U.S. exact DFA metadata mismatch for {field}")

    macro = load_json(ROOT/"cases"/"macro-consistent-wealth-accounts-rev0308-scoreboard.json") or {}
    if "S493" not in ((macro.get("fields") or {}).get("source_family_comparability") or {}).get("source_ids", []):
        fail("rev0347 macro measurement case must cite S493 in source_family_comparability")
    ai = load_json(ROOT/"cases"/"ai-data-center-grid-water-public-backstop-rev0320-scoreboard.json") or {}
    ai_text = json.dumps(ai, sort_keys=True)
    for sid in ["S494", "S495"]:
        if sid not in ai_text:
            fail(f"rev0347 AI/data-center case must cite {sid}")
    if "Dominion" not in ai_text and "Virginia" not in ai_text:
        fail("rev0347 AI/data-center scoreboard must record localized Dominion/Virginia incidence")

    currentness = load_json(ROOT/"docs"/"00-meta"/"currentness-ledger.json") or {}
    source_rows = {r.get("source_id"): r for r in currentness.get("source_rows", []) if isinstance(r, dict)}
    for sid in ["S493", "S494", "S495"]:
        if sid not in source_rows:
            fail(f"rev0347 currentness ledger missing source row {sid}")


def check_rev0348_large_load_tariff_incidence_and_proofdebt_closeout():
    report_path = ROOT/"reports"/"large-load-tariff-incidence-and-proofdebt-closeout-rev0348.json"
    if not report_path.exists():
        fail("Missing rev0348 large-load tariff incidence report JSON")
        return
    report = load_json(report_path) or {}
    if report.get("revision") != "rev0348":
        fail("rev0348 report revision mismatch")
    if report.get("base_revision") != "rev0347":
        fail("rev0348 report base_revision mismatch")
    if report.get("codename") != "large-load-tariff-incidence-and-proofdebt-closeout":
        fail("rev0348 report codename mismatch")
    if report.get("new_sources") != 6 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0348 should add exactly six sources and no cases/schema fields")
    if sorted(report.get("new_source_ids") or []) != ["S496", "S497", "S498", "S499", "S500", "S501"]:
        fail("rev0348 report new_source_ids mismatch")

    expected_counts = {
        "case_memo_count": 95,
        "scoreboard_count": 95,
        "source_count": 501,
        "schema_field_count": 367,
        "registered_unused_field_count": 50,
        "evidence_edge_count": 5628,
    }
    report_counts = report.get("current_counts") or {}
    for key, val in expected_counts.items():
        if report_counts.get(key) != val:
            fail(f"rev0348 historical report current_counts.{key}={report_counts.get(key)!r} does not match recorded {val!r}")

    changelog = (ROOT/"CHANGELOG.md").read_text(encoding="utf-8", errors="ignore")
    headings = re.findall(r"(?m)^## rev(\d{4})\b", changelog)
    if "0348" not in headings or "0347" not in headings:
        fail("CHANGELOG must retain rev0348 and rev0347 historical entries")

    sources = {s.get("id"): s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    expected_sources = {
        "S496": ("official_regulatory_order_notice", "direct", "2026-09-30"),
        "S497": ("utility_tariff_implementation_page", "direct_with_utility_perspective", "2026-09-30"),
        "S498": ("official_regulatory_fact_sheet", "direct", "2026-09-30"),
        "S499": ("official_model_tariff_tentative_order_notice", "direct_with_pending_final_order", "2026-09-30"),
        "S500": ("official_tariff_decision_notice", "direct_open_meeting_decision_notice", "2026-09-30"),
        "S501": ("official_service_agreement_decision_notice", "direct_open_meeting_decision_notice", "2026-09-30"),
    }
    for sid, (stype, role, due) in expected_sources.items():
        s = sources.get(sid)
        if not s:
            fail(f"Missing rev0348 source {sid}")
            continue
        if s.get("source_type") != stype or s.get("evidence_role") != role or s.get("refresh_due") != due:
            fail(f"rev0348 source metadata mismatch for {sid}")

    ai = load_json(ROOT/"cases"/"ai-data-center-grid-water-public-backstop-rev0320-scoreboard.json") or {}
    ai_text = json.dumps(ai, sort_keys=True)
    for sid in ["S496", "S497", "S498", "S499", "S500", "S501"]:
        if sid not in ai_text:
            fail(f"rev0348 AI/data-center case must cite {sid}")
    required_phrases = ["50% of total minimum charges", "85% of contract capacity", "14-year contract", "CIAC", "15-year", "termination-charge"]
    for phrase in required_phrases:
        if phrase not in ai_text:
            fail(f"rev0348 AI/data-center scoreboard missing tariff-incidence phrase: {phrase}")
    if ((ai.get("fields") or {}).get("utility_affordability_burden") or {}).get("evidence_quality") != "direct":
        fail("rev0348 utility_affordability_burden must be upgraded to direct evidence")

    currentness = load_json(ROOT/"docs"/"00-meta"/"currentness-ledger.json") or {}
    source_rows = {r.get("source_id"): r for r in currentness.get("source_rows", []) if isinstance(r, dict)}
    for sid in ["S496", "S497", "S498", "S499", "S500", "S501"]:
        if sid not in source_rows:
            fail(f"rev0348 currentness ledger missing source row {sid}")
    ai_rows = [r for r in currentness.get("case_rows", []) if r.get("case_id") == "ai-data-center-grid-water-public-backstop-rev0320"]
    if not ai_rows or "state_large_load_tariff_order_or_rehearing" not in (ai_rows[0].get("reopen_on") or []):
        fail("rev0348 currentness ledger must preserve state large-load tariff reopening trigger")


def check_rev0349_project_level_water_ratepayer_incidence_and_proofdebt_refactor():
    """Historical rev0349 check: preserve project-incidence receipt without pinning current front-door counts to rev0349."""
    report_path = ROOT/"reports"/"project-level-water-ratepayer-incidence-and-proofdebt-refactor-rev0349.json"
    if not report_path.exists():
        fail("Missing rev0349 project-level incidence report JSON")
        return
    report = load_json(report_path) or {}
    if report.get("revision") != "rev0349":
        fail("rev0349 report revision mismatch")
    if report.get("base_revision") != "rev0348":
        fail("rev0349 report base_revision mismatch")
    if report.get("codename") != "project-level-water-ratepayer-incidence-and-proofdebt-refactor":
        fail("rev0349 report codename mismatch")
    if report.get("new_sources") != 4 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0349 should add exactly four sources and no cases/schema fields")
    if sorted(report.get("new_source_ids") or []) != ["S502", "S503", "S504", "S505"]:
        fail("rev0349 report new_source_ids mismatch")

    # Historical receipt counts must remain what rev0349 actually recorded, not chase later revisions.
    expected_counts = {
        "case_memo_count": 95,
        "scoreboard_count": 95,
        "source_count": 505,
        "schema_field_count": 367,
        "registered_unused_field_count": 50,
        "evidence_edge_count": 5732,
    }
    report_counts = report.get("current_counts") or {}
    for key, val in expected_counts.items():
        if report_counts.get(key) != val:
            fail(f"rev0349 report current_counts.{key}={report_counts.get(key)!r} does not match rev0349 receipt {val!r}")

    sources = {s.get("id"): s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    expected_sources = {
        "S502": ("official_rate_case_settlement_record", "direct_regulatory_details_with_advocate_statement", "2026-09-30"),
        "S503": ("official_regulatory_decision_notice", "direct_current_status", "2026-09-30"),
        "S504": ("official_state_audit_report", "direct_state_audit", "2027-03-31"),
        "S505": ("interstate_compact_water_planning_report", "direct_basin_water_modeling", "2026-09-30"),
    }
    for sid, (stype, role, due) in expected_sources.items():
        s = sources.get(sid)
        if not s:
            fail(f"Missing rev0349 source {sid}")
            continue
        if s.get("source_type") != stype or s.get("evidence_role") != role or s.get("refresh_due") != due:
            fail(f"rev0349 source metadata mismatch for {sid}")

    ai = load_json(ROOT/"cases"/"ai-data-center-grid-water-public-backstop-rev0320-scoreboard.json") or {}
    ai_text = json.dumps(ai, sort_keys=True)
    for sid in ["S502", "S503", "S504", "S505"]:
        if sid not in ai_text:
            fail(f"rev0349 AI/data-center scoreboard must cite {sid}")
    for phrase in ["LP-6", "50 MW", "75 MW", "10-year", "$11 million", "Potomac", "80 MGD", "$928 million", "90 percent"]:
        if phrase not in ai_text:
            fail(f"rev0349 AI/data-center scoreboard missing project-incidence phrase: {phrase}")
    if "signed ESAs" not in ai_text or "facility-level water" not in ai_text or "abatement" not in ai_text:
        fail("rev0349 proof debt must name signed ESAs, facility-level water, and abatement evidence")
    water_field = ((ai.get("fields") or {}).get("data_center_water_consumption_permitting") or {})
    for sid in ["S504", "S505"]:
        if sid not in (water_field.get("source_ids") or []):
            fail(f"rev0349 water field missing {sid}")

    currentness = load_json(ROOT/"docs"/"00-meta"/"currentness-ledger.json") or {}
    source_rows = {r.get("source_id"): r for r in currentness.get("source_rows", []) if isinstance(r, dict)}
    for sid in ["S502", "S503", "S504", "S505"]:
        if sid not in source_rows:
            fail(f"rev0349 currentness ledger missing source row {sid}")
    ai_rows = [r for r in currentness.get("case_rows", []) if r.get("case_id") == "ai-data-center-grid-water-public-backstop-rev0320"]
    reopen = ai_rows[0].get("reopen_on") if ai_rows else []
    for trig in ["PPL_LP6_compliance_tariff_or_ESA_update", "facility_water_reporting_or_basin_low_flow_update"]:
        if trig not in reopen:
            fail(f"rev0349 currentness ledger missing AI reopen trigger {trig}")



def check_rev0350_louisiana_meta_esa_financing_risk_and_countsurface_repair():
    """Historical rev0350 check: preserve Louisiana/Meta project-packet receipt without pinning current front-door counts to rev0350."""
    report_path = ROOT/"reports"/"louisiana-meta-esa-financing-risk-and-countsurface-repair-rev0350.json"
    if not report_path.exists():
        fail("Missing rev0350 Louisiana/Meta project-packet report JSON")
        return
    report = load_json(report_path) or {}
    if report.get("revision") != "rev0350":
        fail("rev0350 report revision mismatch")
    if report.get("base_revision") != "rev0349":
        fail("rev0350 report base_revision mismatch")
    if report.get("codename") != "louisiana-meta-esa-financing-risk-and-countsurface-repair":
        fail("rev0350 report codename mismatch")
    if report.get("new_sources") != 5 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0350 should add exactly five sources and no cases/schema fields")
    if sorted(report.get("new_source_ids") or []) != ["S506", "S507", "S508", "S509", "S510"]:
        fail("rev0350 report new_source_ids mismatch")
    expected_counts = {
        "case_memo_count": 95,
        "scoreboard_count": 95,
        "source_count": 510,
        "schema_field_count": 367,
        "registered_unused_field_count": 50,
        "evidence_edge_count": 5860,
    }
    report_counts = report.get("current_counts") or {}
    for key, val in expected_counts.items():
        if report_counts.get(key) != val:
            fail(f"rev0350 report current_counts.{key}={report_counts.get(key)!r} does not match rev0350 receipt {val!r}")

    sources = {s.get("id"): s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    expected_sources = {
        "S506": ("official_regulatory_docket_status", "direct_current_docket_status", "2026-09-30"),
        "S507": ("utility_regulatory_approval_notice", "direct_with_utility_perspective", "2026-09-30"),
        "S508": ("utility_service_agreement_update", "direct_with_utility_claim_caveat", "2026-09-30"),
        "S509": ("regulatory_intervenor_expert_testimony", "adversarial_direct_testimony", "2026-09-30"),
        "S510": ("regulatory_intervenor_motion", "adversarial_financing_risk_context", "2026-09-30"),
    }
    for sid, (stype, role, due) in expected_sources.items():
        s = sources.get(sid)
        if not s:
            fail(f"Missing rev0350 source {sid}")
            continue
        if s.get("source_type") != stype or s.get("evidence_role") != role or s.get("refresh_due") != due:
            fail(f"rev0350 source metadata mismatch for {sid}")

    ai = load_json(ROOT/"cases"/"ai-data-center-grid-water-public-backstop-rev0320-scoreboard.json") or {}
    ai_text = json.dumps(ai, sort_keys=True)
    for sid in ["S506", "S507", "S508", "S509", "S510"]:
        if sid not in ai_text:
            fail(f"rev0350 AI/data-center scoreboard must cite {sid}")
    for phrase in ["U-37425", "15-year ESA", "$2.65B", "Blue Owl/Beignet", "three CCGTs", "1,500 MW solar", "FAC", "final signed ESA/CIAC"]:
        if phrase not in ai_text:
            fail(f"rev0350 AI/data-center scoreboard missing Louisiana project phrase: {phrase}")
    debt = ai.get("evidence_debt_register") or []
    if not any(isinstance(r, dict) and "Louisiana/Meta U-37425" in (r.get("question") or "") for r in debt):
        fail("rev0350 evidence debt register missing Louisiana/Meta U-37425 item")

    currentness = load_json(ROOT/"docs"/"00-meta"/"currentness-ledger.json") or {}
    source_rows = {r.get("source_id"): r for r in currentness.get("source_rows", []) if isinstance(r, dict)}
    for sid in ["S506", "S507", "S508", "S509", "S510"]:
        if sid not in source_rows:
            fail(f"rev0350 currentness ledger missing source row {sid}")
    ai_rows = [r for r in currentness.get("case_rows", []) if r.get("case_id") == "ai-data-center-grid-water-public-backstop-rev0320"]
    reopen = ai_rows[0].get("reopen_on") if ai_rows else []
    for trig in ["Louisiana_Meta_final_ESA_or_CIAC_disclosure", "Blue_Owl_Beignet_or_Meta_sponsor_financing_change"]:
        if trig not in reopen:
            fail(f"rev0350 currentness ledger missing AI reopen trigger {trig}")



def check_rev0351_written_order_phase2_expansion_and_la_large_load_router_refactor():
    """Historical rev0351 check: preserve written-order/phase-two receipt without pinning current front-door counts to rev0351."""
    report_path = ROOT/"reports"/"written-order-phase2-expansion-and-la-large-load-router-refactor-rev0351.json"
    if not report_path.exists():
        fail("Missing rev0351 written-order/phase-two report JSON")
        return
    report = load_json(report_path) or {}
    if report.get("revision") != "rev0351":
        fail("rev0351 report revision mismatch")
    if report.get("base_revision") != "rev0350":
        fail("rev0351 report base_revision mismatch")
    if report.get("codename") != "written-order-phase2-expansion-and-la-large-load-router-refactor":
        fail("rev0351 report codename mismatch")
    if report.get("new_sources") != 5 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0351 should add exactly five sources and no cases/schema fields")
    if sorted(report.get("new_source_ids") or []) != ["S511", "S512", "S513", "S514", "S515"]:
        fail("rev0351 report new_source_ids mismatch")
    sources = {s.get("id"): s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    for sid in ["S511", "S512", "S513", "S514", "S515"]:
        if sid not in sources:
            fail(f"Missing rev0351 source {sid}")
    ai = load_json(ROOT/"cases"/"ai-data-center-grid-water-public-backstop-rev0320-scoreboard.json") or {}
    ai_text = json.dumps(ai, sort_keys=True)
    for sid in ["S511", "S512", "S513", "S514", "S515"]:
        if sid not in ai_text:
            fail(f"rev0351 AI/data-center scoreboard must cite {sid}")
    for phrase in ["Order No. U-37425", "ESA and Related Agreements", "Project Evest", "U-37882", "December 16, 2026", "X-37921"]:
        if phrase not in ai_text:
            fail(f"rev0351 AI/data-center scoreboard missing phrase: {phrase}")
    debt = ai.get("evidence_debt_register") or []
    if not any(isinstance(r, dict) and "Project Evest U-37882" in (r.get("question") or "") for r in debt):
        fail("rev0351 evidence debt register missing Project Evest/U-37882 item")
    proof = " ".join(str(x) for x in ai.get("proof_debt", []))
    if "written LPSC order" in proof:
        fail("rev0351 proof_debt still asks generically for a written LPSC order after S511")
    currentness = load_json(ROOT/"docs"/"00-meta"/"currentness-ledger.json") or {}
    source_rows = {r.get("source_id"): r for r in currentness.get("source_rows", []) if isinstance(r, dict)}
    for sid in ["S511", "S512", "S513", "S514", "S515"]:
        if sid not in source_rows:
            fail(f"rev0351 currentness ledger missing source row {sid}")


def check_rev0352_large_load_guidelines_and_evest_redaction_risk():
    report_path = ROOT/"reports"/"large-load-guidelines-and-evest-redaction-risk-rev0352.json"
    if not report_path.exists():
        fail("Missing rev0352 large-load-guidelines/redaction report JSON")
        return
    report = load_json(report_path) or {}
    if report.get("revision") != "rev0352":
        fail("rev0352 report revision mismatch")
    if report.get("base_revision") != "rev0351":
        fail("rev0352 report base_revision mismatch")
    if report.get("codename") != "large-load-guidelines-and-evest-redaction-risk":
        fail("rev0352 report codename mismatch")
    if report.get("new_sources") != 5 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0352 should add exactly five sources and no cases/schema fields")
    if sorted(report.get("new_source_ids") or []) != ["S516", "S517", "S518", "S519", "S520"]:
        fail("rev0352 report new_source_ids mismatch")

    sources = {s.get("id"): s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    expected_sources = {
        "S516": ("official_nonbinding_large_load_guidelines", "direct_policy_scoring_template_with_nonbinding_caveat", "2026-09-30"),
        "S517": ("utility_direct_testimony_public_redacted", "utility_project_cost_monitoring_and_customer_protection_claim_with_redaction_caveat", "2026-12-31"),
        "S518": ("utility_direct_testimony_public_redacted", "direct_guideline_compliance_claim_with_sealed_exhibit_caveat", "2026-12-31"),
        "S519": ("official_repository_notice", "direct_comment_deadline_and_no_intervention_process", "2026-09-30"),
        "S520": ("official_commission_minutes_directive", "direct_policy_origin_and_large_load_threshold_context", "2026-09-30"),
    }
    for sid, (stype, role, due) in expected_sources.items():
        s = sources.get(sid)
        if not s:
            fail(f"Missing rev0352 source {sid}")
            continue
        if s.get("source_type") != stype or s.get("evidence_role") != role or s.get("refresh_due") != due:
            fail(f"rev0352 source metadata mismatch for {sid}")

    ai = load_json(ROOT/"cases"/"ai-data-center-grid-water-public-backstop-rev0320-scoreboard.json") or {}
    ai_text = json.dumps(ai, sort_keys=True)
    for sid in ["S516", "S517", "S518", "S519", "S520"]:
        if sid not in ai_text:
            fail(f"rev0352 AI/data-center scoreboard must cite {sid}")
    for phrase in ["twelve guideline categories", "HSPM/AEO", "seven CCCTs", "three battery resources", "250 miles", "$13B", "June 19, 2026", "no interventions", "5% of prior peak load", "public-redaction matrix"]:
        if phrase not in ai_text:
            fail(f"rev0352 AI/data-center scoreboard missing phrase: {phrase}")
    debt = ai.get("evidence_debt_register") or []
    if not any(isinstance(r, dict) and "guideline compliance" in (r.get("question") or "") for r in debt):
        fail("rev0352 evidence debt register missing guideline-compliance/redaction item")
    proof = " ".join(str(x) for x in ai.get("proof_debt", []))
    if "guideline-compliance and redaction matrix" not in proof:
        fail("rev0352 proof_debt missing guideline-compliance and redaction matrix")

    currentness = load_json(ROOT/"docs"/"00-meta"/"currentness-ledger.json") or {}
    source_rows = {r.get("source_id"): r for r in currentness.get("source_rows", []) if isinstance(r, dict)}
    for sid in ["S516", "S517", "S518", "S519", "S520"]:
        if sid not in source_rows:
            fail(f"rev0352 currentness ledger missing source row {sid}")
    ai_rows = [r for r in currentness.get("case_rows", []) if r.get("case_id") == "ai-data-center-grid-water-public-backstop-rev0320"]
    reopen = ai_rows[0].get("reopen_on") if ai_rows else []
    for trig in ["X37921_comments_due_2026_06_19", "X37921_staff_report_back_December_2026", "U37882_HSPM_AEO_redaction_summary_or_protective_order_change"]:
        if trig not in reopen:
            fail(f"rev0352 currentness ledger missing AI reopen trigger {trig}")





def check_rev0353_resource_adequacy_riverbend_water_and_router_refactor():
    report_path = ROOT/"reports"/"resource-adequacy-riverbend-water-and-router-refactor-rev0353.json"
    if not report_path.exists():
        fail("Missing rev0353 resource-adequacy/River Bend report JSON")
        return
    report = load_json(report_path) or {}
    if report.get("revision") != "rev0353":
        fail("rev0353 report revision mismatch")
    if report.get("base_revision") != "rev0352":
        fail("rev0353 report base_revision mismatch")
    if report.get("codename") != "resource-adequacy-riverbend-water-and-router-refactor":
        fail("rev0353 report codename mismatch")
    if report.get("new_sources") != 6 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0353 should add exactly six sources and no cases/schema fields")
    if sorted(report.get("new_source_ids") or []) != ["S521", "S522", "S523", "S524", "S525", "S526"]:
        fail("rev0353 report new_source_ids mismatch")
    historical_counts = report.get("current_counts") or {}
    for key, val in {"case_memo_count": 95, "scoreboard_count": 95, "source_count": 526, "schema_field_count": 367, "registered_unused_field_count": 50, "evidence_edge_count": 6419}.items():
        if historical_counts.get(key) != val:
            fail(f"rev0353 report historical current_counts.{key}={historical_counts.get(key)!r} expected {val!r}")

    historical_sources = {s.get("id"): s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", []) if s.get("id") in ["S521", "S522", "S523", "S524", "S525", "S526"]}
    for sid in ["S521", "S522", "S523", "S524", "S525", "S526"]:
        if sid not in historical_sources:
            fail(f"Missing rev0353 source {sid}")
    ai = load_json(ROOT/"cases"/"ai-data-center-grid-water-public-backstop-rev0320-scoreboard.json") or {}
    ai_text = json.dumps(ai, sort_keys=True)
    for sid in ["S521", "S522", "S523", "S524", "S525", "S526"]:
        if sid not in ai_text:
            fail(f"rev0353 AI/data-center scoreboard must cite {sid}")
    for phrase in ["Order X-37566", "reserve-margin", "Lightning", "River Bend", "245 MW", "330 MW", "$3.25B", "$16M", "Google", "private project seniority"]:
        if phrase not in ai_text:
            fail(f"rev0353 AI/data-center scoreboard missing phrase: {phrase}")
    proof = " ".join(str(x) for x in ai.get("proof_debt", []))
    if "River Bend public/private packet" not in proof and "River Bend post-rev0354" not in proof:
        fail("rev0353/0354 proof_debt missing River Bend public/private packet lineage")


def check_rev0354_riverbend_indenture_pilot_rebate_and_local_incidence_refactor():
    report_path = ROOT/"reports"/"riverbend-indenture-pilot-rebate-and-local-incidence-refactor-rev0354.json"
    if not report_path.exists():
        fail("Missing rev0354 River Bend indenture/PILOT/local-incidence report JSON")
        return
    report = load_json(report_path) or {}
    if report.get("revision") != "rev0354":
        fail("rev0354 report revision mismatch")
    if report.get("base_revision") != "rev0353":
        fail("rev0354 report base_revision mismatch")
    if report.get("codename") != "riverbend-indenture-pilot-rebate-and-local-incidence-refactor":
        fail("rev0354 report codename mismatch")
    if report.get("new_sources") != 6 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0354 should add exactly six sources and no cases/schema fields")
    if sorted(report.get("new_source_ids") or []) != ["S527", "S528", "S529", "S530", "S531", "S532"]:
        fail("rev0354 report new_source_ids mismatch")

    schema = load_json(ROOT/"docs"/"20-program"/"scoreboard-schema.json") or {}
    schema_fields = (((schema.get("properties") or {}).get("fields") or {}).get("properties") or {})
    field_registry = load_json(ROOT/"docs"/"00-meta"/"field-registry.json") or {}
    registered_unused = [f for f in field_registry.get("fields", []) if isinstance(f, dict) and f.get("lifecycle_status") == "registered_unused"]
    expected_counts = {
        "case_memo_count": 95,
        "scoreboard_count": 95,
        "source_count": 532,
        "schema_field_count": 367,
        "registered_unused_field_count": 50,
        "evidence_edge_count": 6653,
    }
    report_counts = report.get("current_counts") or {}
    for key, val in expected_counts.items():
        if report_counts.get(key) != val:
            fail(f"rev0354 historical report current_counts.{key}={report_counts.get(key)!r} expected {val!r}")

    sources = {s.get("id"): s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    expected_sources = {
        "S527": ("sec_8k_indentured_project_financing_disclosure", "direct_project_debt_waterfall_and_lease_modification_constraints", "2026-12-31"),
        "S528": ("company_project_capacity_status_page", "direct_project_scale_status_claim_with_company_caveat", "2026-09-30"),
        "S529": ("official_state_tax_incentive_statute", "direct_data_center_sales_use_exemption_and_clawback_authority", "2026-12-31"),
        "S530": ("official_local_property_tax_rebate_authority", "direct_ad_valorem_rebate_authority_current_status", "2027-01-31"),
        "S531": ("local_report_with_official_project_incidence_claims", "project_water_pilot_and_electric_infrastructure_claims_with_verification_debt", "2026-09-30"),
        "S532": ("advocacy_modeling_public_cost_estimate", "adversarial_public_cost_estimate_with_modeling_caveat", "2026-09-30"),
    }
    for sid, (stype, role, due) in expected_sources.items():
        s = sources.get(sid)
        if not s:
            fail(f"Missing rev0354 source {sid}")
            continue
        if s.get("source_type") != stype or s.get("evidence_role") != role or s.get("refresh_due") != due:
            fail(f"rev0354 source metadata mismatch for {sid}")

    ai = load_json(ROOT/"cases"/"ai-data-center-grid-water-public-backstop-rev0320-scoreboard.json") or {}
    ai_text = json.dumps(ai, sort_keys=True)
    for sid in ["S527", "S528", "S529", "S530", "S531", "S532"]:
        if sid not in ai_text:
            fail(f"rev0354 AI/data-center scoreboard must cite {sid}")
    for phrase in ["6.192%", "2042", "330 MW", "2,361 acres", "sales/use tax exemption", "Act 434", "PILOT", "$26B", "private creditor seniority"]:
        if phrase not in ai_text:
            fail(f"rev0354 AI/data-center scoreboard missing phrase: {phrase}")
    proof = " ".join(str(x) for x in ai.get("proof_debt", []))
    if "River Bend post-rev0354 primary-instrument packet" not in proof:
        fail("rev0354 proof_debt missing River Bend primary-instrument packet")
    debt = ai.get("evidence_debt_register") or []
    if not any(isinstance(r, dict) and "indenture, water, PILOT/rebate" in (r.get("question") or "") for r in debt):
        fail("rev0354 evidence debt register missing River Bend indenture/water/PILOT proof-packet item")

    currentness = load_json(ROOT/"docs"/"00-meta"/"currentness-ledger.json") or {}
    source_rows = {r.get("source_id"): r for r in currentness.get("source_rows", []) if isinstance(r, dict)}
    for sid in ["S527", "S528", "S529", "S530", "S531", "S532"]:
        if sid not in source_rows:
            fail(f"rev0354 currentness ledger missing source row {sid}")
    ai_rows = [r for r in currentness.get("case_rows", []) if r.get("case_id") == "ai-data-center-grid-water-public-backstop-rev0320"]
    reopen = ai_rows[0].get("reopen_on") if ai_rows else []
    for trig in ["River_Bend_indentures_or_lease_guarantee_modification", "River_Bend_PILOT_or_ad_valorem_rebate_implementation", "Louisiana_data_center_sales_use_exemption_agreement_or_clawback", "River_Bend_switchyard_line_or_ratebase_treatment_update", "UCS_or_LPSC_large_load_cost_model_update"]:
        if trig not in reopen:
            fail(f"rev0354 currentness ledger missing AI reopen trigger {trig}")

    # rev0354 is now a historical snapshot; current front-door count checks move to rev0355.
    current_claims = {}
    changelog = (ROOT/"CHANGELOG.md").read_text(encoding="utf-8", errors="ignore")
    if "## rev0352" in changelog and "## rev0352 — large-load-guidelines-and-evest-redaction-risk\n\n- Added S521-S526" in changelog:
        fail("rev0354 should repair the rev0352 changelog source-range typo")



def check_rev0355_riverbend_pilot_distribution_and_public_instrument_ladder():
    report_path = ROOT/"reports"/"riverbend-pilot-distribution-and-public-instrument-ladder-rev0355.json"
    if not report_path.exists():
        fail("Missing rev0355 River Bend public-instrument report JSON")
        return
    report = load_json(report_path) or {}
    if report.get("revision") != "rev0355" or report.get("base_revision") != "rev0354":
        fail("rev0355 report revision/base_revision mismatch")
    if report.get("codename") != "riverbend-pilot-distribution-and-public-instrument-ladder":
        fail("rev0355 report codename mismatch")
    if report.get("new_sources") != 5 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0355 should add exactly five sources and no cases/schema fields")
    if sorted(report.get("new_source_ids") or []) != ['S533', 'S534', 'S535', 'S536', 'S537']:
        fail("rev0355 report new_source_ids mismatch")
    schema = load_json(ROOT/"docs"/"20-program"/"scoreboard-schema.json") or {}
    schema_fields = (((schema.get("properties") or {}).get("fields") or {}).get("properties") or {})
    field_registry = load_json(ROOT/"docs"/"00-meta"/"field-registry.json") or {}
    registered_unused = [f for f in field_registry.get("fields", []) if isinstance(f, dict) and f.get("lifecycle_status") == "registered_unused"]
    # rev0355 is now a historical receipt. Its count block reflects the last
    # audited snapshot preserved by later repairs and must not chase live sources
    # added in rev0361+.
    frozen_counts = {
        "case_memo_count": 95,
        "scoreboard_count": 95,
        "source_count": 539,
        "schema_field_count": 317,
        "registered_unused_field_count": 0,
        "evidence_edge_count": 6793,
    }
    for key, val in frozen_counts.items():
        if (report.get("current_counts") or {}).get(key) != val:
            fail(f"rev0355 report frozen current_counts.{key} mismatch: expected {val!r}")
    sources = {s.get("id"): s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    expected_sources = {
        "S533": ("utility_project_announcement", "direct_utility_capacity_incentive_and_timeline_claim_with_tariff_gap", "2026-09-30"),
        "S534": ("local_pilot_idb_reporting", "project_pilot_leaseback_and_revenue_claim_with_primary_contract_debt", "2026-09-30"),
        "S535": ("local_idb_resolution_reporting", "direct_distribution_schedule_claim_with_resolution_document_debt", "2026-09-30"),
        "S536": ("local_rebate_implementation_reporting", "public_upside_distribution_and_rebate_sequence_claim_with_implementation_debt", "2026-12-31"),
        "S537": ("official_local_public_records_and_meeting_surface", "direct_record_retrieval_route_for_missing_project_instruments", "2026-09-30"),
    }
    for sid, (stype, role, due) in expected_sources.items():
        s = sources.get(sid)
        if not s:
            fail(f"Missing rev0355 source {sid}")
            continue
        if s.get("source_type") != stype or s.get("evidence_role") != role or s.get("refresh_due") != due:
            fail(f"rev0355 source metadata mismatch for {sid}")
    ai = load_json(ROOT/"cases"/"ai-data-center-grid-water-public-backstop-rev0320-scoreboard.json") or {}
    ai_text = json.dumps(ai, sort_keys=True)
    for sid in ['S533', 'S534', 'S535', 'S536', 'S537']:
        if sid not in ai_text:
            fail(f"rev0355 AI/data-center scoreboard must cite {sid}")
    for phrase in ["330 MW", "245 MW", "PILOT", "up-to-$90M/year", "distribution schedule", "public-record", "IDB/PILOT lease"]:
        if phrase not in ai_text:
            fail(f"rev0355 AI/data-center scoreboard missing phrase: {phrase}")
    proof = " ".join(str(x) for x in ai.get("proof_debt", []))
    if "River Bend post-rev0355 public-instrument packet" not in proof:
        fail("rev0355 proof_debt missing River Bend public-instrument packet")
    debt = ai.get("evidence_debt_register") or []
    if not any(isinstance(r, dict) and "River Bend IDB/PILOT distribution" in (r.get("question") or "") for r in debt):
        fail("rev0355 evidence debt register missing River Bend IDB/PILOT distribution item")
    currentness = load_json(ROOT/"docs"/"00-meta"/"currentness-ledger.json") or {}
    source_rows = {r.get("source_id"): r for r in currentness.get("source_rows", []) if isinstance(r, dict)}
    for sid in ['S533', 'S534', 'S535', 'S536', 'S537']:
        if sid not in source_rows:
            fail(f"rev0355 currentness ledger missing source row {sid}")
    ai_rows = [r for r in currentness.get("case_rows", []) if r.get("case_id") == "ai-data-center-grid-water-public-backstop-rev0320"]
    reopen = ai_rows[0].get("reopen_on") if ai_rows else []
    for trig in ["River_Bend_IDB_PILOT_lease_or_land_transfer_disclosure", "River_Bend_IDB_distribution_resolution_or_taxing_body_allocation_update", "River_Bend_public_records_response_or_missing_primary_instrument_posted", "River_Bend_Entergy_service_tariff_or_ratebase_treatment_update"]:
        if trig not in reopen:
            fail(f"rev0355 currentness ledger missing AI reopen trigger {trig}")
    # Historical rev0355 facts are preserved in its report. Current front-door truth is
    # enforced by generic release checks rather than by an old release fixture.


def actual_cube_counts():
    schema = load_json(ROOT/"docs/20-program/scoreboard-schema.json") or {}
    schema_fields = (((schema.get("properties") or {}).get("fields") or {}).get("properties") or {})
    field_registry = load_json(ROOT/"docs/00-meta/field-registry.json") or {}
    registered_unused = [
        row for row in field_registry.get("fields", [])
        if isinstance(row, dict) and row.get("lifecycle_status") == "registered_unused"
    ]
    evidence = load_json(ROOT/"cases/EVIDENCE_LEDGER.json") or {}
    return {
        "case_memo_count": len(list((ROOT/"cases").glob("*-case.md"))),
        "scoreboard_count": len(list((ROOT/"cases").glob("*-scoreboard.json"))),
        "source_count": len((load_json(ROOT/"SOURCES.json") or {}).get("sources", [])),
        "schema_field_count": len(schema_fields),
        "registered_unused_field_count": len(registered_unused),
        "evidence_edge_count": evidence.get("evidence_edge_count"),
    }


def check_current_count_surfaces():
    counts = actual_cube_counts()
    fragments = [
        f"{counts['case_memo_count']} case memos",
        f"{counts['scoreboard_count']} scoreboards",
        f"{counts['source_count']} sources",
        f"{counts['schema_field_count']} registered field",
        f"{counts['registered_unused_field_count']} registered_unused field",
        f"{counts['evidence_edge_count']} mechanical evidence associations",
    ]
    surfaces = [
        "README.md",
        "START_HERE.md",
        "ARCHIVE_INDEX.md",
        "cases/case-portfolio-summary.md",
        "docs/20-program/case-portfolio-coverage-map.md",
        "docs/20-program/scoreboard-spec.md",
        "docs/90-open/open-questions.md",
    ]
    for rel in surfaces:
        path = ROOT/rel
        if not path.exists():
            fail(f"Missing current-count surface: {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for frag in fragments:
            if frag not in text:
                fail(f"Current-count surface {rel} missing exact fragment: {frag}")
        for stale in ["532 sources", "6653 evidence edges"]:
            if stale in text:
                fail(f"Current-count surface {rel} retains stale fragment: {stale}")
    sources_text = (ROOT/"SOURCES.md").read_text(encoding="utf-8", errors="ignore")
    src_rows = (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])
    if src_rows:
        first = src_rows[0].get("id")
        last = src_rows[-1].get("id")
        start_tail = f"S{max(1, int(last[1:]) - 4):03d}"
        source_frags = [f"{counts['source_count']} sources", f"{first}-{last}", f"{start_tail}-{last}"]
    else:
        source_frags = [f"{counts['source_count']} sources"]
    for frag in source_frags:
        if frag not in sources_text:
            fail(f"SOURCES.md missing current source fragment: {frag}")
    receipt = load_json(ROOT/"REVISION-RECEIPT.json") or {}
    for key, value in counts.items():
        if (receipt.get("current_counts") or {}).get(key) != value:
            fail(f"REVISION-RECEIPT current_counts.{key} mismatch: expected {value!r}")


def check_entrypoint_backtick_paths():
    code_path_re = re.compile(r"`([^`\n]+?\.(?:md|json))`")
    for rel in ["README.md", "START_HERE.md"]:
        path = ROOT/rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for target in code_path_re.findall(text):
            target = target.split("#", 1)[0]
            dest = (ROOT/target).resolve()
            try:
                dest.relative_to(ROOT.resolve())
            except Exception:
                fail(f"Entrypoint code path escapes archive: {rel} -> {target}")
                continue
            if not dest.exists():
                fail(f"Broken entrypoint code path: {rel} -> {target}")


def check_archive_index_sync():
    json_path = ROOT/"ARCHIVE_INDEX.json"
    md_path = ROOT/"ARCHIVE_INDEX.md"
    if not json_path.exists() or not md_path.exists():
        fail("Archive index JSON/Markdown pair is missing")
        return
    actual = sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file())
    data = load_json(json_path) or {}
    listed = data.get("files") or []
    if data.get("revision_current") != CURRENT_REVISION:
        fail("ARCHIVE_INDEX.json revision_current mismatch")
    if data.get("file_count") != len(actual):
        fail(f"ARCHIVE_INDEX.json file_count {data.get('file_count')} != actual {len(actual)}")
    if listed != actual:
        missing = sorted(set(actual) - set(listed))
        extra = sorted(set(listed) - set(actual))
        fail(f"ARCHIVE_INDEX.json file set mismatch; missing={missing[:10]} extra={extra[:10]}")
    md_text = md_path.read_text(encoding="utf-8", errors="ignore")
    md_listed = re.findall(r"(?m)^- `([^`]+)`$", md_text)
    if md_listed != actual:
        missing = sorted(set(actual) - set(md_listed))
        extra = sorted(set(md_listed) - set(actual))
        fail(f"ARCHIVE_INDEX.md file set mismatch; missing={missing[:10]} extra={extra[:10]}")


def check_rev0356_mission_heart_evidence_integrity_audit():
    codename = "mission-heart-evidence-integrity-and-cloudtainer-pruning-map"
    jpath = ROOT/"reports"/f"{codename}-rev0356.json"
    mpath = ROOT/"reports"/f"{codename}-rev0356.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0356 mission/evidence/cloudtainer audit pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0356" or report.get("base_revision") != "rev0355":
        fail("rev0356 audit revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0356 audit codename mismatch")
    if report.get("new_sources") != 0 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0356 must add no canonical sources, cases, or schema fields")
    # Historical reports must not be forced to roll forward to live current counts.
    # rev0356 froze the counts observed when that audit was written; rev0357 validates
    # those frozen values rather than rewriting history.
    frozen_counts = {
        "case_memo_count": 95,
        "scoreboard_count": 95,
        "source_count": 537,
        "schema_field_count": 367,
        "registered_unused_field_count": 50,
        "evidence_edge_count": 6793,
    }
    for key, value in frozen_counts.items():
        if (report.get("current_counts") or {}).get(key) != value:
            fail(f"rev0356 audit frozen current_counts.{key} mismatch: expected {value!r}")
    required_findings = {
        "evidence_edge_inflation",
        "front_door_and_count_drift",
        "historical_provenance_overwrite",
        "validator_append_only_release_diary",
        "no_reproducible_derived_ledger_build",
        "portfolio_maturity_overstatement",
        "schema_sprawl",
    }
    found = {row.get("id") for row in report.get("severe_findings", []) if isinstance(row, dict)}
    if not required_findings.issubset(found):
        fail(f"rev0356 audit missing finding ids: {sorted(required_findings - found)}")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in [
        "ordinary independence",
        "6,793 rows but only 670 unique case-source pairs",
        "Historical provenance was overwritten",
        "Deliberately not changed",
    ]:
        if phrase not in text:
            fail(f"rev0356 human audit missing required phrase: {phrase}")
    validator_text = (ROOT/"tools/validate_archive.py").read_text(encoding="utf-8", errors="ignore")
    if len(re.findall(r"(?m)^CURRENT_REVISION\s*=", validator_text)) != 1:
        fail("Validator must declare CURRENT_REVISION exactly once")
    for entry in [ROOT/"README.md", ROOT/"START_HERE.md"]:
        et = entry.read_text(encoding="utf-8", errors="ignore")
        if "riverbend-indenture-pilot-rebate-and-local-incidence-refactor-rev0355.md" in et:
            fail(f"Broken rev0355 report route survives in {entry.name}")
        if f"reports/{codename}-rev0356.md" not in et:
            fail(f"rev0356 audit route missing from {entry.name}")


def check_rev0357_substantive_risk_claim_migration_sprint():
    codename = "substantive-risk-claim-migration-and-field-pruning-sprint"
    jpath = ROOT/"reports"/f"{codename}-rev0357.json"
    mpath = ROOT/"reports"/f"{codename}-rev0357.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0357 substantive risk sprint report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0357" or report.get("base_revision") != "rev0356":
        fail("rev0357 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0357 report codename mismatch")
    if report.get("new_sources") != 0 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0357 must add no canonical sources, cases, or schema fields")
    # rev0357 is a historical receipt; its current_counts snapshot is intentionally
    # frozen and should not roll forward as rev0361 adds sources/verified edges.
    frozen_counts = {
        "case_memo_count": 95,
        "scoreboard_count": 95,
        "source_count": 539,
        "schema_field_count": 317,
        "registered_unused_field_count": 0,
        "evidence_edge_count": 6793,
    }
    for key, value in frozen_counts.items():
        if (report.get("current_counts") or {}).get(key) != value:
            fail(f"rev0357 report frozen current_counts.{key} mismatch: expected {value!r}")
    evidence = load_json(ROOT/"cases/EVIDENCE_LEDGER.json") or {}
    if "mechanical_evidence_associations" not in str(evidence.get("ledger_semantics", "")):
        fail("EVIDENCE_LEDGER missing mechanical association semantics")
    # rev0357 had zero verified claim edges as a historical fact. Later revisions may
    # increase the current ledger count, so validate the rev0357 report snapshot instead.
    if (report.get("priority_results") or {}).get("verified_claim_edge_count") != 0:
        fail("rev0357 report snapshot must show zero verified claim edges")
    rows = evidence.get("edge_rows") or []
    qualities = {}
    for row in rows:
        q = row.get("evidence_quality", "<missing>") if isinstance(row, dict) else "<bad>"
        qualities[q] = qualities.get(q, 0) + 1
    pairs = {(r.get("case_id"), r.get("source_id")) for r in rows if isinstance(r, dict)}
    if evidence.get("mechanical_association_count") != len(rows):
        fail("EVIDENCE_LEDGER mechanical_association_count mismatch")
    if evidence.get("unique_case_source_pair_count") != len(pairs):
        fail("EVIDENCE_LEDGER unique_case_source_pair_count mismatch")
    summary = load_json(ROOT/"cases/MECHANICAL_EVIDENCE_SUMMARY.json") or {}
    scounts = summary.get("counts") or {}
    if scounts.get("mechanical_association_count") != len(rows):
        fail("MECHANICAL_EVIDENCE_SUMMARY mechanical count mismatch")
    if scounts.get("unique_case_source_pair_count") != len(pairs):
        fail("MECHANICAL_EVIDENCE_SUMMARY unique pair count mismatch")
    if scounts.get("scoreboard_source_ids_row_count") != qualities.get("scoreboard_source_ids", 0):
        fail("MECHANICAL_EVIDENCE_SUMMARY scoreboard_source_ids count mismatch")
    claim_backlog = load_json(ROOT/"cases/CLAIM_ATOM_BACKLOG.json") or {}
    atoms = claim_backlog.get("claim_atoms") or []
    if len(atoms) < 20:
        fail("CLAIM_ATOM_BACKLOG must retain at least 20 seed atoms")
    if not any(a.get("case_id") == "ai-data-center-grid-water-public-backstop-rev0320" for a in atoms if isinstance(a, dict)):
        fail("CLAIM_ATOM_BACKLOG missing AI/data-center P0 migration target")
    case_ledger = load_json(ROOT/"cases/CASE_LEDGER.json") or {}
    case_rows = case_ledger.get("cases") or []
    for row in case_rows:
        if not isinstance(row, dict):
            continue
        for key in ["workflow_status", "evidentiary_maturity", "certification_status", "claim_lineage_status", "substantive_priority_band", "next_substantive_action"]:
            if not row.get(key):
                fail(f"CASE_LEDGER row missing rev0357 maturity key {key}: {row.get('case_id')}")
        if row.get("certification_status") == "certified_current":
            fail(f"No case may be certified_current before verified claim edges: {row.get('case_id')}")
    maturity = load_json(ROOT/"cases/CASE_MATURITY_LEDGER.json") or {}
    if maturity.get("certified_current_count") != 0 or len(maturity.get("rows") or []) != len(case_rows):
        fail("CASE_MATURITY_LEDGER mismatch with CASE_LEDGER")
    quarantine = load_json(ROOT/"docs/00-meta/report-provenance-quarantine.json") or {}
    qcounts = quarantine.get("counts") or {}
    # Recompute report revision mismatches.
    json_mis = 0; md_mis = 0
    for p in (ROOT/"reports").glob("*"):
        if p.suffix not in [".json", ".md"]:
            continue
        m = re.search(r"rev(\d{4})", p.name)
        filename_rev = "rev" + m.group(1) if m else None
        declared = None
        if p.suffix == ".json":
            d = load_json(p) or {}
            declared = d.get("revision") or d.get("revision_current") or d.get("current_revision")
            if filename_rev and declared and filename_rev != declared:
                json_mis += 1
        else:
            text = p.read_text(encoding="utf-8", errors="ignore")[:2000]
            mm = re.search(r"(?m)^revision_current:\s*(rev\d{4})", text)
            declared = mm.group(1) if mm else None
            if filename_rev and declared and filename_rev != declared:
                md_mis += 1
    if qcounts.get("json_revision_mismatch_count") != json_mis or qcounts.get("markdown_revision_mismatch_count") != md_mis:
        fail("report-provenance-quarantine mismatch counts are stale")
    field_candidates = load_json(ROOT/"docs/00-meta/field-retirement-candidate-ledger.json") or {}
    fcounts = field_candidates.get("counts") or {}
    field_reg = load_json(ROOT/"docs/00-meta/field-registry.json") or {}
    zero = [r for r in field_reg.get("fields", []) if isinstance(r, dict) and r.get("usage_count") == 0]
    if fcounts.get("zero_usage_field_count") != len(zero):
        fail("field-retirement-candidate-ledger zero-use count mismatch")
    if not all(r.get("retirement_candidate") is True for r in zero):
        fail("Not all zero-use fields are marked retirement_candidate")
    workq = load_json(ROOT/"docs/00-meta/high-risk-substantive-work-queue.json") or {}
    if len(workq.get("work_items") or []) < 10:
        fail("high-risk substantive work queue is too small")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["claim-level evidence migration", "case maturity", "report-provenance quarantine", "schema pruning"]:
        if phrase not in text:
            fail(f"rev0357 report missing required phrase: {phrase}")



def check_rev0358_claim_edge_pilot_and_validator_refactor():
    codename = "claim-edge-pilot-ai-large-load-and-validator-history-refactor"
    jpath = ROOT/"reports"/f"{codename}-rev0358.json"
    mpath = ROOT/"reports"/f"{codename}-rev0358.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0358 claim-edge pilot report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0358" or report.get("base_revision") != "rev0357":
        fail("rev0358 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0358 report codename mismatch")
    if report.get("new_sources") != 0 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0358 must add no canonical sources, cases, or schema fields")
    # Historical receipt: current_counts is a rev0358 snapshot and must not chase later live counts.
    if not isinstance(report.get("current_counts"), dict) or not report.get("current_counts"):
        fail("rev0358 report missing current_counts snapshot")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("VERIFIED_CLAIM_EDGE_LEDGER revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 6:
        fail("VERIFIED_CLAIM_EDGE_LEDGER count mismatch or too few rows")
    evidence = load_json(ROOT/"cases"/"EVIDENCE_LEDGER.json") or {}
    if evidence.get("verified_claim_edge_count") != len(vrows):
        fail("EVIDENCE_LEDGER verified_claim_edge_count does not match verified ledger")
    if evidence.get("verified_claim_edge_ledger") != "cases/VERIFIED_CLAIM_EDGE_LEDGER.json":
        fail("EVIDENCE_LEDGER missing verified edge ledger route")
    ids = source_ids()
    allowed_relationships = {"supports","qualifies","contradicts","context_only","method_only"}
    seen = set()
    required = ["verified_claim_edge_id","case_id","bounded_claim","relationship_code","source_ids","exact_locator","does_not_prove","contrary_or_qualifying_evidence_needed","reversal_rule","verification_status"]
    for row in vrows:
        if not isinstance(row, dict):
            fail("Verified claim edge row is not an object")
            continue
        edge_id = row.get("verified_claim_edge_id")
        if edge_id in seen:
            fail(f"Duplicate verified claim edge id: {edge_id}")
        seen.add(edge_id)
        for key in required:
            if not row.get(key):
                fail(f"Verified claim edge {edge_id} missing {key}")
        if row.get("relationship_code") not in allowed_relationships:
            fail(f"Verified claim edge {edge_id} has bad relationship code {row.get('relationship_code')}")
        if str(edge_id).startswith("VCEDGE-rev0358-") and row.get("case_id") != "ai-data-center-grid-water-public-backstop-rev0320":
            fail(f"rev0358 pilot edge should cover AI/data-center case: {edge_id}")
        for sid in row.get("source_ids") or []:
            if sid not in ids:
                fail(f"Verified claim edge {edge_id} uses unknown source id {sid}")
    rel_counts = collections.Counter(row.get("relationship_code") for row in vrows if isinstance(row,dict))
    if rel_counts.get("supports",0) < 3 or rel_counts.get("qualifies",0) < 2:
        fail("rev0358 verified pilot must include both support and qualification edges")
    packet = load_json(ROOT/"cases"/"ai-data-center-grid-water-public-backstop-rev0320-claim-packet.json") or {}
    if packet.get("case_id") != "ai-data-center-grid-water-public-backstop-rev0320":
        fail("AI claim packet case_id mismatch")
    ai_seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict) and r.get("case_id") == "ai-data-center-grid-water-public-backstop-rev0320"}
    if set(packet.get("verified_claim_edge_ids") or []) != ai_seen:
        fail("AI claim packet verified edge ids do not match AI verified ledger subset")
    blockers = packet.get("unverified_decisive_premises") or []
    if len(blockers) < 3:
        fail("AI claim packet must retain at least three unverified decisive premises")
    case_ledger = load_json(ROOT/"cases"/"CASE_LEDGER.json") or {}
    ai_rows = [r for r in case_ledger.get("cases",[]) if isinstance(r,dict) and r.get("case_id") == "ai-data-center-grid-water-public-backstop-rev0320"]
    if not ai_rows:
        fail("CASE_LEDGER missing AI/data-center row")
    else:
        ai = ai_rows[0]
        if ai.get("certification_status") == "certified_current":
            fail("AI/data-center case must not be certified by rev0358 pilot")
        ai_count = sum(1 for r in vrows if isinstance(r,dict) and r.get("case_id") == "ai-data-center-grid-water-public-backstop-rev0320")
        if ai.get("verified_claim_edge_count") != ai_count:
            fail("CASE_LEDGER AI verified edge count mismatch")
    maturity = load_json(ROOT/"cases"/"CASE_MATURITY_LEDGER.json") or {}
    if maturity.get("certified_current_count") != 0 or maturity.get("verified_edge_pilot_case_count", 0) < 1:
        fail("CASE_MATURITY_LEDGER rev0358 maturity counts mismatch")
    workq = load_json(ROOT/"docs"/"00-meta"/"high-risk-substantive-work-queue.json") or {}
    wanted = {"ai-up1-project-cost-assignment-verified-edge","ai-up2-water-local-incidence-verified-edge","ai-up3-public-upside-recovery-verified-edge"}
    found = {r.get("work_item_id") for r in workq.get("work_items",[]) if isinstance(r,dict)}
    if not wanted.issubset(found):
        fail(f"rev0358 high-risk queue missing next AI edge items: {sorted(wanted-found)}")
    audit = load_json(ROOT/"docs"/"00-meta"/"validator-history-refactor-audit-rev0358.json") or {}
    if audit.get("revision_current") != "rev0358" or audit.get("release_specific_check_count",0) < 1:
        fail("validator history refactor historical audit missing, misidentified, or empty")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["six locator-bounded verified claim edges", "not certify project-level cost shift", "validator-history audit"]:
        if phrase not in text:
            fail(f"rev0358 report missing required phrase: {phrase}")



def check_rev0359_project_instrument_edges_and_source_role_refactor():
    codename = "project-instrument-edges-la-large-load-and-source-role-refactor"
    jpath = ROOT/"reports"/f"{codename}-rev0359.json"
    mpath = ROOT/"reports"/f"{codename}-rev0359.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0359 project-instrument report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0359" or report.get("base_revision") != "rev0358":
        fail("rev0359 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0359 report codename mismatch")
    if report.get("new_sources") != 0 or report.get("new_cases") != 0 or report.get("new_schema_fields") != 0:
        fail("rev0359 must add no canonical sources, cases, or schema fields")
    # Historical receipt: current_counts is a rev0359 snapshot and must not chase later live counts.
    if not isinstance(report.get("current_counts"), dict) or not report.get("current_counts"):
        fail("rev0359 report missing current_counts snapshot")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0359 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 20:
        fail("rev0359 verified ledger must have at least 20 rows and correct count")
    required_rev0359 = {f"VCEDGE-rev0359-{i:04d}" for i in range(7,21)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict)}
    if not required_rev0359.issubset(seen):
        fail(f"rev0359 missing new verified edge ids: {sorted(required_rev0359-seen)}")
    sources_used = set()
    for row in vrows:
        for sid in row.get("source_ids") or []:
            sources_used.add(sid)
    for sid in {"S511","S516","S526","S527","S530","S535","S536","S537"}:
        if sid not in sources_used:
            fail(f"rev0359 verified edges missing source {sid}")
    rel_counts = collections.Counter(r.get("relationship_code") for r in vrows if isinstance(r,dict))
    if rel_counts.get("context_only",0) < 1 or rel_counts.get("qualifies",0) < 5:
        fail("rev0359 should include qualification/context edges, not only support edges")
    packet = load_json(ROOT/"cases"/"ai-data-center-grid-water-public-backstop-rev0320-claim-packet.json") or {}
    ai_seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict) and r.get("case_id") == "ai-data-center-grid-water-public-backstop-rev0320"}
    if set(packet.get("verified_claim_edge_ids") or []) != ai_seen:
        fail("rev0359 claim packet verified edge ids do not match AI verified ledger subset")
    if packet.get("case_certification_status_after") == "certified_current":
        fail("rev0359 AI claim packet must not certify the case")
    matrix = load_json(ROOT/"cases"/"ai-data-center-grid-water-public-backstop-rev0320-instrument-matrix.json") or {}
    if matrix.get("revision_current") != CURRENT_REVISION or len(matrix.get("matrix") or []) < 5:
        fail("rev0359 instrument matrix missing or too thin")
    if "not_certified" not in (matrix.get("bottom_line") or "") and "Certification" not in (matrix.get("bottom_line") or ""):
        fail("rev0359 instrument matrix must state the certification boundary")
    case_ledger = load_json(ROOT/"cases"/"CASE_LEDGER.json") or {}
    ai_rows = [r for r in case_ledger.get("cases",[]) if isinstance(r,dict) and r.get("case_id") == "ai-data-center-grid-water-public-backstop-rev0320"]
    if not ai_rows:
        fail("rev0359 CASE_LEDGER missing AI row")
    else:
        ai = ai_rows[0]
        ai_count = sum(1 for r in vrows if isinstance(r,dict) and r.get("case_id") == "ai-data-center-grid-water-public-backstop-rev0320")
        if ai.get("verified_claim_edge_count") != ai_count:
            fail("rev0359 CASE_LEDGER AI verified count mismatch")
        if ai.get("certification_status") == "certified_current":
            fail("rev0359 AI case must not be certified")
        if not ai.get("instrument_matrix"):
            fail("rev0359 AI row missing instrument matrix route")
    maturity = load_json(ROOT/"cases"/"CASE_MATURITY_LEDGER.json") or {}
    if maturity.get("certified_current_count") != 0 or maturity.get("verified_edge_pilot_case_count", 0) < 1:
        fail("rev0359 maturity counts mismatch")
    audit = load_json(ROOT/"docs"/"00-meta"/"ai-source-role-overassignment-audit-rev0359.json") or {}
    if audit.get("revision_current") != "rev0359":
        fail("rev0359 source-role overassignment historical audit missing or misidentified")
    if "noncertifying" not in (audit.get("certification_guard") or ""):
        fail("rev0359 source-role audit must state noncertifying guard")
    workq = load_json(ROOT/"docs"/"00-meta"/"high-risk-substantive-work-queue.json") or {}
    if "ai-river-bend-primary-instrument-record-retrieval" not in {r.get("work_item_id") for r in workq.get("work_items",[]) if isinstance(r,dict)}:
        fail("rev0359 work queue missing River Bend primary-record retrieval item")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["project-instrument", "20", "not certified current", "source-role audit"]:
        if phrase not in text:
            fail(f"rev0359 report missing required phrase: {phrase}")



def check_rev0360_pilot_advance_public_record_and_schema_retirement_cutover():
    codename = "pilot-advance-public-record-and-schema-retirement-cutover"
    jpath = ROOT/"reports"/f"{codename}-rev0360.json"
    mpath = ROOT/"reports"/f"{codename}-rev0360.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0360 pilot advance/schema cutover report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0360" or report.get("base_revision") != "rev0359":
        fail("rev0360 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0360 report codename mismatch")
    if report.get("new_sources") != 2 or sorted(report.get("new_source_ids") or []) != ["S538", "S539"]:
        fail("rev0360 must add exactly S538-S539")
    if report.get("new_cases") != 0 or report.get("new_schema_fields") != 0 or report.get("retired_schema_fields") != 50:
        fail("rev0360 source/case/schema delta mismatch")
    # Historical receipt: current_counts is a rev0360 snapshot and must not chase later live counts.
    counts = actual_cube_counts()
    if not isinstance(report.get("current_counts"), dict) or not report.get("current_counts"):
        fail("rev0360 report missing current_counts snapshot")
    if counts.get("schema_field_count") != 317 or counts.get("registered_unused_field_count") != 0:
        fail("rev0360 schema cutover counts must be 317 fields and 0 registered_unused fields")
    sources = {s.get("id"): s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    for sid in ["S538","S539"]:
        if sid not in sources:
            fail(f"rev0360 missing source {sid}")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0360 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 30:
        fail("rev0360 verified ledger must have at least 30 rows and correct count")
    required = {f"VCEDGE-rev0360-{i:04d}" for i in range(21,31)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict)}
    if not required.issubset(seen):
        fail(f"rev0360 missing new edge ids: {sorted(required-seen)}")
    used = set()
    for row in vrows:
        for sid in row.get("source_ids") or []:
            used.add(sid)
    for sid in ["S538","S539","S530","S526","S531"]:
        if sid not in used:
            fail(f"rev0360 verified edges missing source {sid}")
    packet = load_json(ROOT/"cases"/"ai-data-center-grid-water-public-backstop-rev0320-claim-packet.json") or {}
    ai_seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict) and r.get("case_id") == "ai-data-center-grid-water-public-backstop-rev0320"}
    if set(packet.get("verified_claim_edge_ids") or []) != ai_seen:
        fail("rev0360 claim packet verified edge ids do not match AI verified ledger subset")
    if packet.get("case_certification_status_after") == "certified_current":
        fail("rev0360 must not certify AI/data-center case")
    impl = load_json(ROOT/"cases"/"ai-data-center-grid-water-public-backstop-rev0320-river-bend-implementation-ledger.json") or {}
    if impl.get("revision_current") != CURRENT_REVISION or len(impl.get("implementation_items") or []) < 6:
        fail("rev0360 implementation ledger missing or too thin")
    if impl.get("certification_status") == "certified_current":
        fail("rev0360 implementation ledger must not certify the case")
    audit = load_json(ROOT/"docs"/"00-meta"/"field-retirement-cutover-audit-rev0360.json") or {}
    if audit.get("retired_zero_use_field_count") != 50 or audit.get("schema_field_count_after") != 317:
        fail("rev0360 field-retirement audit count mismatch")
    schema = load_json(ROOT/"docs"/"20-program"/"scoreboard-schema.json") or {}
    schema_fields = set(((((schema.get("properties") or {}).get("fields") or {}).get("properties") or {}).keys()))
    retired = set(audit.get("retired_field_ids") or [])
    if schema_fields & retired:
        fail("rev0360 retired fields remain in scoreboard schema")
    for p in (ROOT/"cases").glob("*scoreboard.json"):
        data = load_json(p) or {}
        live_fields = set((data.get("fields") or {}).keys())
        if live_fields & retired:
            fail(f"rev0360 scoreboard still uses retired fields: {p.relative_to(ROOT)}")
    workq = load_json(ROOT/"docs"/"00-meta"/"high-risk-substantive-work-queue.json") or {}
    ids = {r.get("work_item_id") for r in workq.get("work_items",[]) if isinstance(r,dict)}
    if "ai-river-bend-utility-accounting-primary-record-sprint" not in ids:
        fail("rev0360 work queue missing utility-accounting primary-record sprint")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["$10M PILOT advance", "not certified current", "50 zero-use fields", "utility accounting"]:
        if phrase not in text:
            fail(f"rev0360 report missing required phrase: {phrase}")



def check_rev0361_dual_claim_migration_us_dfa_and_ratepayer_risk_refactor():
    codename = "dual-claim-migration-us-dfa-and-ratepayer-risk-refactor"
    jpath = ROOT/"reports"/f"{codename}-rev0361.json"
    mpath = ROOT/"reports"/f"{codename}-rev0361.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0361 dual-claim migration report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0361" or report.get("base_revision") != "rev0360":
        fail("rev0361 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0361 report codename mismatch")
    if report.get("new_sources") != 2 or sorted(report.get("new_source_ids") or []) != ["S540", "S541"]:
        fail("rev0361 must add exactly S540-S541")
    # Historical receipt: rev0361 current_counts is a snapshot and must not chase rev0362 source growth.
    if not isinstance(report.get("current_counts"), dict) or not report.get("current_counts"):
        fail("rev0361 report missing current_counts snapshot")
    sources = {s.get("id"): s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    for sid in ["S540", "S541"]:
        if sid not in sources:
            fail(f"rev0361 missing source {sid}")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0361 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 41:
        fail("rev0361 verified ledger must have at least 41 rows and correct count")
    required = {f"VCEDGE-rev0361-{i:04d}" for i in range(31,42)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict)}
    if not required.issubset(seen):
        fail(f"rev0361 missing new verified edge ids: {sorted(required-seen)}")
    by_case = collections.Counter(r.get("case_id") for r in vrows if isinstance(r,dict))
    if by_case.get("ai-data-center-grid-water-public-backstop-rev0320",0) < 36 or by_case.get("united-states-rev0304",0) < 5:
        fail("rev0361 verified edge case counts too low")
    if verified.get("case_count_with_verified_edges") != len(by_case) or len(by_case) < 2:
        fail("rev0361 verified ledger should cover at least two cases")
    used = set()
    for row in vrows:
        for sid in row.get("source_ids") or []:
            used.add(sid)
    for sid in ["S540","S541","S510","S493","S70","S490"]:
        if sid not in used:
            fail(f"rev0361 verified edges missing source {sid}")
    ai_packet = load_json(ROOT/"cases"/"ai-data-center-grid-water-public-backstop-rev0320-claim-packet.json") or {}
    us_packet = load_json(ROOT/"cases"/"united-states-rev0304-claim-packet.json") or {}
    ai_seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict) and r.get("case_id") == "ai-data-center-grid-water-public-backstop-rev0320"}
    us_seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict) and r.get("case_id") == "united-states-rev0304"}
    if set(ai_packet.get("verified_claim_edge_ids") or []) != ai_seen:
        fail("rev0361 AI packet verified edge ids mismatch")
    if set(us_packet.get("verified_claim_edge_ids") or []) != us_seen:
        fail("rev0361 U.S. packet verified edge ids mismatch")
    if ai_packet.get("case_certification_status_after") == "certified_current" or us_packet.get("case_certification_status_after") == "certified_current":
        fail("rev0361 claim packets must not certify cases")
    maturity = load_json(ROOT/"cases"/"CASE_MATURITY_LEDGER.json") or {}
    if maturity.get("certified_current_count") != 0 or maturity.get("verified_edge_pilot_case_count", 0) < 2:
        fail("rev0361 maturity ledger counts mismatch")
    audit = load_json(ROOT/"docs"/"00-meta"/"verified-claim-edge-quality-audit-rev0361.json") or {}
    if audit.get("missing_required_field_rows"):
        fail("rev0361 verified claim-edge quality audit has missing fields")
    tool = ROOT/"tools"/"audit_verified_claim_edges.py"
    if not tool.exists():
        fail("rev0361 missing verified claim-edge audit tool")
    workq = load_json(ROOT/"docs"/"00-meta"/"high-risk-substantive-work-queue.json") or {}
    wids = {r.get("work_item_id") for r in workq.get("work_items", []) if isinstance(r,dict)}
    for wid in ["ai-u37425-parent-guarantee-esa-financing-followup", "us-dfa-liquid-control-crosswalk"]:
        if wid not in wids:
            fail(f"rev0361 high-risk queue missing {wid}")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["dual claim", "41", "U.S. DFA", "not certify"]:
        if phrase not in text:
            fail(f"rev0361 report missing required phrase: {phrase}")



def check_rev0362_boi_transfer_tax_current_law_and_source_edge_refactor():
    codename = "boi-transfer-tax-current-law-and-source-edge-refactor"
    jpath = ROOT/"reports"/f"{codename}-rev0362.json"
    mpath = ROOT/"reports"/f"{codename}-rev0362.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0362 BOI/transfer-tax/source-edge report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0362" or report.get("base_revision") != "rev0361":
        fail("rev0362 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0362 report codename mismatch")
    if report.get("new_sources") != 4 or sorted(report.get("new_source_ids") or []) != ["S542","S543","S544","S545"]:
        fail("rev0362 must add exactly S542-S545")
    frozen_counts = {
        "case_memo_count": 95,
        "scoreboard_count": 95,
        "source_count": 545,
        "schema_field_count": 317,
        "registered_unused_field_count": 0,
        "evidence_edge_count": 6798,
    }
    for key, value in frozen_counts.items():
        if (report.get("current_counts") or {}).get(key) != value:
            fail(f"rev0362 report frozen current_counts.{key} mismatch: expected {value!r}")
    sources = {s.get("id"):s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    for sid in ["S542","S543","S544","S545"]:
        if sid not in sources:
            fail(f"rev0362 missing source {sid}")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0362 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 53:
        fail("rev0362 verified ledger must have at least 53 rows and correct count")
    required = {f"VCEDGE-rev0362-{i:04d}" for i in range(42,54)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict)}
    if not required.issubset(seen):
        fail(f"rev0362 missing new verified edge ids: {sorted(required-seen)}")
    by_case = collections.Counter(r.get("case_id") for r in vrows if isinstance(r,dict))
    if by_case.get("estate-gift-gst-exemption-currentness-rev0323",0) < 7 or by_case.get("united-states-beneficial-ownership-reversal-rev0309",0) < 5:
        fail("rev0362 transfer-tax/BOI case edge counts too low")
    if verified.get("case_count_with_verified_edges") != len(by_case) or len(by_case) < 4:
        fail("rev0362 verified ledger should cover at least four cases")
    used = set()
    for row in vrows:
        for sid in row.get("source_ids") or []:
            used.add(sid)
    for sid in ["S542","S543","S544","S545","S169","S433","S491"]:
        if sid not in used:
            fail(f"rev0362 verified edges missing source {sid}")
    estate_packet = load_json(ROOT/"cases"/"estate-gift-gst-exemption-currentness-rev0323-claim-packet.json") or {}
    boi_packet = load_json(ROOT/"cases"/"united-states-beneficial-ownership-reversal-rev0309-claim-packet.json") or {}
    estate_seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict) and r.get("case_id") == "estate-gift-gst-exemption-currentness-rev0323"}
    boi_seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict) and r.get("case_id") == "united-states-beneficial-ownership-reversal-rev0309"}
    if set(estate_packet.get("verified_claim_edge_ids") or []) != estate_seen:
        fail("rev0362 estate claim packet verified edge ids mismatch")
    if set(boi_packet.get("verified_claim_edge_ids") or []) != boi_seen:
        fail("rev0362 BOI claim packet verified edge ids mismatch")
    if estate_packet.get("case_certification_status_after") == "certified_current" or boi_packet.get("case_certification_status_after") == "certified_current":
        fail("rev0362 claim packets must not certify cases")
    maturity = load_json(ROOT/"cases"/"CASE_MATURITY_LEDGER.json") or {}
    if maturity.get("certified_current_count") != 0 or maturity.get("verified_edge_pilot_case_count",0) < 4:
        fail("rev0362 maturity ledger counts mismatch")
    audit = load_json(ROOT/"docs"/"00-meta"/"source-edge-use-backfill-audit-rev0362.json") or {}
    if audit.get("verified_claim_edge_count", 0) < 53 or not audit.get("sources_touched_for_used_by_cases"):
        fail("rev0362 source-edge use backfill audit mismatch or empty")
    qa = load_json(ROOT/"docs"/"00-meta"/"verified-claim-edge-quality-audit-rev0362.json") or {}
    if qa.get("total_verified_claim_edges", 0) < 53 or qa.get("missing_required_field_rows"):
        fail("rev0362 verified-claim-edge audit mismatch or missing fields")
    workq = load_json(ROOT/"docs"/"00-meta"/"high-risk-substantive-work-queue.json") or {}
    wids = {r.get("work_item_id") for r in workq.get("work_items", []) if isinstance(r,dict)}
    for wid in ["boi-final-rule-litigation-and-alternative-rails-sprint", "estate-form706-form709-and-soi-incidence-sprint"]:
        if wid not in wids:
            fail(f"rev0362 high-risk queue missing {wid}")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["transfer-tax", "BOI perimeter", "source-edge use", "zero certified current cases"]:
        if phrase not in text:
            fail(f"rev0362 report missing required phrase: {phrase}")


def check_rev0363_stablecoin_law_waterfall_and_backstop_refactor():
    codename = "stablecoin-law-waterfall-and-backstop-refactor"
    jpath = ROOT/"reports"/f"{codename}-rev0363.json"
    mpath = ROOT/"reports"/f"{codename}-rev0363.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0363 stablecoin law/waterfall/backstop report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0363" or report.get("base_revision") != "rev0362":
        fail("rev0363 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0363 report codename mismatch")
    if report.get("new_sources") != 3 or sorted(report.get("new_source_ids") or []) != ["S546","S547","S548"]:
        fail("rev0363 must add exactly S546-S548")
    frozen_counts = {
        "case_memo_count": 95,
        "scoreboard_count": 95,
        "source_count": 548,
        "schema_field_count": 317,
        "registered_unused_field_count": 0,
        "evidence_edge_count": 6841,
    }
    for key, value in frozen_counts.items():
        if (report.get("current_counts") or {}).get(key) != value:
            fail(f"rev0363 report frozen current_counts.{key} mismatch: expected {value!r}")
    sources = {s.get("id"):s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    for sid in ["S546","S547","S548"]:
        if sid not in sources:
            fail(f"rev0363 missing source {sid}")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0363 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 65:
        fail("rev0363 verified ledger must have at least 65 rows and correct count")
    required = {f"VCEDGE-rev0363-{i:04d}" for i in range(54,66)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict)}
    if not required.issubset(seen):
        fail(f"rev0363 missing new verified edge ids: {sorted(required-seen)}")
    by_case = collections.Counter(r.get("case_id") for r in vrows if isinstance(r,dict))
    if by_case.get("stablecoins-money-market-treasury-liquidity-backstop-rev0319",0) < 12:
        fail("rev0363 stablecoin case edge count too low")
    if verified.get("case_count_with_verified_edges") != len(by_case) or len(by_case) < 5:
        fail("rev0363 verified ledger should cover at least five cases")
    used = set()
    for row in vrows:
        for sid in row.get("source_ids") or []:
            used.add(sid)
    for sid in ["S546","S547","S548","S441","S442","S443","S444","S375"]:
        if sid not in used:
            fail(f"rev0363 verified edges missing source {sid}")
    packet = load_json(ROOT/"cases"/"stablecoins-money-market-treasury-liquidity-backstop-rev0319-claim-packet.json") or {}
    waterfall = load_json(ROOT/"cases"/"stablecoins-money-market-treasury-liquidity-backstop-rev0319-backstop-waterfall.json") or {}
    stable_seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict) and r.get("case_id") == "stablecoins-money-market-treasury-liquidity-backstop-rev0319"}
    if set(packet.get("verified_claim_edge_ids") or []) != stable_seen:
        fail("rev0363 stablecoin claim packet verified edge ids mismatch")
    if packet.get("case_certification_status_after") == "certified_current":
        fail("rev0363 stablecoin claim packet must not certify case")
    if len(waterfall.get("waterfall_claimants") or []) < 6 or "not certify" not in waterfall.get("certification_boundary", "").lower():
        fail("rev0363 stablecoin waterfall missing claimant depth or certification boundary")
    maturity = load_json(ROOT/"cases"/"CASE_MATURITY_LEDGER.json") or {}
    if maturity.get("certified_current_count") != 0 or maturity.get("verified_edge_pilot_case_count",0) < 5:
        fail("rev0363 maturity ledger counts mismatch")
    qa = load_json(ROOT/"docs"/"00-meta"/"verified-claim-edge-quality-audit-rev0363.json") or {}
    if qa.get("total_verified_claim_edges", 0) < 65 or qa.get("missing_required_field_rows"):
        fail("rev0363 verified-claim-edge audit mismatch or missing fields")
    audit = load_json(ROOT/"docs"/"00-meta"/"stablecoin-current-law-waterfall-audit-rev0363.json") or {}
    if audit.get("certification_status") != "not_certified_current":
        fail("rev0363 stablecoin audit must preserve not_certified_current")
    workq = load_json(ROOT/"docs"/"00-meta"/"high-risk-substantive-work-queue.json") or {}
    wids = {r.get("work_item_id") for r in workq.get("work_items", []) if isinstance(r,dict)}
    if "stablecoin-final-rules-reserve-data-and-public-upside-sprint" not in wids:
        fail("rev0363 high-risk queue missing stablecoin final-rules sprint")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Public Law 119-27", "1:1 reserves", "no federal guarantee", "public-upside recovery", "zero certified current cases"]:
        if phrase not in text:
            fail(f"rev0363 report missing required phrase: {phrase}")



def check_rev0364_stablecoin_reporting_forms_and_currentness_watch_refactor():
    codename = "stablecoin-reporting-forms-and-currentness-watch-refactor"
    jpath = ROOT/"reports"/f"{codename}-rev0364.json"
    mpath = ROOT/"reports"/f"{codename}-rev0364.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0364 stablecoin reporting/currentness report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0364" or report.get("base_revision") != "rev0363":
        fail("rev0364 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0364 report codename mismatch")
    if report.get("new_sources") != 4 or sorted(report.get("new_source_ids") or []) != ["S549","S550","S551","S552"]:
        fail("rev0364 must add exactly S549-S552")
    frozen_counts = {
        "case_memo_count": 95,
        "scoreboard_count": 95,
        "source_count": 552,
        "schema_field_count": 317,
        "registered_unused_field_count": 0,
        "evidence_edge_count": 6893,
    }
    for key, value in frozen_counts.items():
        if (report.get("current_counts") or {}).get(key) != value:
            fail(f"rev0364 report frozen current_counts.{key} mismatch: expected {value!r}")
    sources = {s.get("id"):s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    for sid in ["S549","S550","S551","S552"]:
        if sid not in sources:
            fail(f"rev0364 missing source {sid}")
        if sources.get(sid, {}).get("refresh_due") != "2026-09-30":
            fail(f"rev0364 source {sid} refresh_due must be 2026-09-30")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0364 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 77:
        fail("rev0364 verified ledger must have at least 77 rows and correct count")
    required = {f"VCEDGE-rev0364-{i:04d}" for i in range(66,78)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict)}
    if not required.issubset(seen):
        fail(f"rev0364 missing new verified edge ids: {sorted(required-seen)}")
    by_case = collections.Counter(r.get("case_id") for r in vrows if isinstance(r,dict))
    if by_case.get("stablecoins-money-market-treasury-liquidity-backstop-rev0319", 0) < 24:
        fail("rev0364 stablecoin case edge count too low")
    if verified.get("case_count_with_verified_edges") != len(by_case) or len(by_case) < 5:
        fail("rev0364 verified ledger case count mismatch")
    packet = load_json(ROOT/"cases"/"stablecoins-money-market-treasury-liquidity-backstop-rev0319-claim-packet.json") or {}
    stable_seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict) and r.get("case_id") == "stablecoins-money-market-treasury-liquidity-backstop-rev0319"}
    if set(packet.get("verified_claim_edge_ids") or []) != stable_seen:
        fail("rev0364 stablecoin claim packet verified edge ids mismatch")
    if packet.get("case_certification_status_after") == "certified_current":
        fail("rev0364 stablecoin claim packet must not certify case")
    data_map = load_json(ROOT/"cases"/"stablecoins-money-market-treasury-liquidity-backstop-rev0319-issuer-reporting-data-map.json") or {}
    if data_map.get("certification_status") != "not_certified_current":
        fail("rev0364 issuer reporting map must preserve not_certified_current")
    if len(data_map.get("ps01_weekly_data_categories") or []) < 4 or len(data_map.get("ps02_quarterly_data_categories") or []) < 3:
        fail("rev0364 issuer reporting data map missing PS-01/PS-02 depth")
    watch = load_json(ROOT/"docs"/"00-meta"/"currentness-watchlist-audit-rev0364.json") or {}
    if watch.get("revision_current") != "rev0364" or watch.get("missing_or_bad_field_count") != 0:
        fail("rev0364 currentness watchlist historical audit mismatch or missing fields")
    qa = load_json(ROOT/"docs"/"00-meta"/"verified-claim-edge-quality-audit-rev0364.json") or {}
    if qa.get("total_verified_claim_edges", 0) < 77 or qa.get("missing_required_field_rows"):
        fail("rev0364 verified-edge QA mismatch or missing fields")
    audit = load_json(ROOT/"docs"/"00-meta"/"stablecoin-reporting-forms-audit-rev0364.json") or {}
    if audit.get("certification_status") != "not_certified_current" or audit.get("mechanical_lineage_rows_added") is None:
        fail("rev0364 stablecoin reporting audit mismatch")
    tool = ROOT/"tools"/"audit_currentness_watchlist.py"
    if not tool.exists() or "rev0364" not in tool.read_text(encoding="utf-8", errors="ignore"):
        fail("rev0364 currentness watchlist tool missing or stale")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["S549-S552", "PS-01", "PS-02", "0 certified current cases", "public-upside recovery"]:
        if phrase not in text:
            fail(f"rev0364 report missing required phrase: {phrase}")


def check_rev0365_private_credit_formpf_counterparty_and_redemption_risk_refactor():
    codename = "private-credit-formpf-counterparty-and-redemption-risk-refactor"
    jpath = ROOT/"reports"/f"{codename}-rev0365.json"
    mpath = ROOT/"reports"/f"{codename}-rev0365.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0365 private-credit/Form PF report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0365" or report.get("base_revision") != "rev0364":
        fail("rev0365 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0365 report codename mismatch")
    if report.get("new_sources") != 4 or sorted(report.get("new_source_ids") or []) != ["S553","S554","S555","S556"]:
        fail("rev0365 must add exactly S553-S556")
    # Historical receipt: current_counts is a snapshot and must not chase later live counts.
    if not isinstance(report.get("current_counts"), dict) or not report.get("current_counts"):
        fail("rev0365 report missing current_counts snapshot")
    sources = {s.get("id"):s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    for sid in ["S553","S554","S555","S556"]:
        if sid not in sources:
            fail(f"rev0365 missing source {sid}")
        if sources.get(sid, {}).get("used_by_cases") != ["private-credit-nonbank-backstop-perimeter-rev0319"]:
            fail(f"rev0365 source {sid} should be used only by private-credit case")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0365 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 91:
        fail("rev0365 verified ledger must have at least 91 rows and correct count")
    required = {f"VCEDGE-rev0365-{i:04d}" for i in range(78,92)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict)}
    if not required.issubset(seen):
        fail(f"rev0365 missing new verified edge ids: {sorted(required-seen)}")
    by_case = collections.Counter(r.get("case_id") for r in vrows if isinstance(r,dict))
    if by_case.get("private-credit-nonbank-backstop-perimeter-rev0319", 0) < 14:
        fail("rev0365 private-credit case edge count too low")
    if verified.get("case_count_with_verified_edges") != len(by_case) or len(by_case) < 6:
        fail("rev0365 verified ledger case count mismatch")
    packet = load_json(ROOT/"cases"/"private-credit-nonbank-backstop-perimeter-rev0319-claim-packet.json") or {}
    pc_seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict) and r.get("case_id") == "private-credit-nonbank-backstop-perimeter-rev0319"}
    if set(packet.get("verified_claim_edge_ids") or []) != pc_seen:
        fail("rev0365 private-credit claim packet verified edge ids mismatch")
    if packet.get("case_certification_status_after") == "certified_current":
        fail("rev0365 private-credit claim packet must not certify case")
    pcmap = load_json(ROOT/"cases"/"private-credit-nonbank-backstop-perimeter-rev0319-counterparty-and-disclosure-map.json") or {}
    if pcmap.get("certification_status") != "not_certified_current" or len(pcmap.get("perimeter_layers") or []) < 6:
        fail("rev0365 private-credit map must preserve noncertification and six-layer perimeter")
    audit = load_json(ROOT/"docs"/"00-meta"/"private-credit-counterparty-and-disclosure-audit-rev0365.json") or {}
    if audit.get("certification_status") != "not_certified_current" or audit.get("problem_count") != 0:
        fail("rev0365 private-credit audit mismatch")
    qa = load_json(ROOT/"docs"/"00-meta"/"verified-claim-edge-quality-audit-rev0365.json") or {}
    if qa.get("total_verified_claim_edges") != len(vrows) or qa.get("missing_required_field_rows"):
        fail("rev0365 verified-edge QA mismatch or missing fields")
    tool = ROOT/"tools"/"audit_private_credit_perimeter.py"
    if not tool.exists() or "rev0365" not in tool.read_text(encoding="utf-8", errors="ignore"):
        fail("rev0365 private credit audit tool missing or stale")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["S553-S556", "Form PF", "redemption", "0 certified current cases", "public-upside recovery"]:
        if phrase not in text:
            fail(f"rev0365 report missing required phrase: {phrase}")


def check_rev0366_treasury_basis_repo_clearing_and_public_upside_refactor():
    codename = "treasury-basis-repo-clearing-and-public-upside-refactor"
    case_id = "stablecoins-money-market-treasury-liquidity-backstop-rev0319"
    jpath = ROOT/"reports"/f"{codename}-rev0366.json"
    mpath = ROOT/"reports"/f"{codename}-rev0366.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0366 Treasury basis/repo/clearing report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0366" or report.get("base_revision") != "rev0365":
        fail("rev0366 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0366 report codename mismatch")
    if report.get("new_sources") != 6 or sorted(report.get("new_source_ids") or []) != ["S557","S558","S559","S560","S561","S562"]:
        fail("rev0366 must add exactly S557-S562")
    # Historical receipt: current_counts is a snapshot and must not chase later live counts.
    if not isinstance(report.get("current_counts"), dict) or not report.get("current_counts"):
        fail("rev0366 report missing current_counts snapshot")
    sources = {s.get("id"):s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    for sid in ["S557","S558","S559","S560","S561","S562"]:
        if sid not in sources:
            fail(f"rev0366 missing source {sid}")
        if sources.get(sid, {}).get("used_by_cases") != [case_id]:
            fail(f"rev0366 source {sid} should be used only by stablecoin/MMF/Treasury case")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0366 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 107:
        fail("rev0366 verified ledger must have at least 107 rows and correct count")
    required = {f"VCEDGE-rev0366-{i:04d}" for i in range(92,108)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict)}
    if not required.issubset(seen):
        fail(f"rev0366 missing new verified edge ids: {sorted(required-seen)}")
    by_case = collections.Counter(r.get("case_id") for r in vrows if isinstance(r,dict))
    if by_case.get(case_id, 0) < 40:
        fail("rev0366 stablecoin/MMF/Treasury case edge count too low")
    packet = load_json(ROOT/"cases"/f"{case_id}-claim-packet.json") or {}
    case_seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict) and r.get("case_id") == case_id}
    if set(packet.get("verified_claim_edge_ids") or []) != case_seen:
        fail("rev0366 claim packet verified edge ids mismatch")
    if packet.get("case_certification_status_after") == "certified_current":
        fail("rev0366 claim packet must not certify case")
    tmap = load_json(ROOT/"cases"/f"{case_id}-treasury-basis-repo-clearing-map.json") or {}
    if tmap.get("certification_status") != "not_certified_current" or len(tmap.get("perimeter_layers") or []) < 6:
        fail("rev0366 Treasury map must preserve noncertification and six-layer perimeter")
    audit = load_json(ROOT/"docs"/"00-meta"/"treasury-basis-repo-clearing-audit-rev0366.json") or {}
    if audit.get("certification_status") != "not_certified_current" or audit.get("problem_count") != 0:
        fail("rev0366 Treasury basis audit mismatch")
    qa = load_json(ROOT/"docs"/"00-meta"/"verified-claim-edge-quality-audit-rev0366.json") or {}
    if qa.get("total_verified_claim_edges") != len(vrows) or qa.get("missing_required_field_rows"):
        fail("rev0366 verified-edge QA mismatch or missing fields")
    tool = ROOT/"tools"/"audit_treasury_basis_perimeter.py"
    if not tool.exists() or "rev0366" not in tool.read_text(encoding="utf-8", errors="ignore"):
        fail("rev0366 Treasury audit tool missing or stale")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["S557-S562", "repo", "clearing", "0", "public-upside recovery"]:
        if phrase not in text:
            fail(f"rev0366 report missing required phrase: {phrase}")



def check_rev0367_residual_insurance_nfip_fairplan_assessment_and_mortgage_stress_refactor():
    codename = "residual-insurance-nfip-fairplan-assessment-and-mortgage-stress-refactor"
    case_id = "us-climate-residual-insurance-public-backstop-rev0319"
    jpath = ROOT/"reports"/f"{codename}-rev0367.json"
    mpath = ROOT/"reports"/f"{codename}-rev0367.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0367 residual-insurance/NFIP report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0367" or report.get("base_revision") != "rev0366":
        fail("rev0367 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0367 report codename mismatch")
    if report.get("new_sources") != 7 or sorted(report.get("new_source_ids") or []) != ["S563","S564","S565","S566","S567","S568","S569"]:
        fail("rev0367 must add exactly S563-S569")
    # Historical receipt: current_counts is a snapshot and must not chase later live counts.
    if not isinstance(report.get("current_counts"), dict) or not report.get("current_counts"):
        fail("rev0367 report missing current_counts snapshot")
    sources = {s.get("id"):s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    for sid in ["S563","S564","S565","S566","S567","S568","S569"]:
        if sid not in sources:
            fail(f"rev0367 missing source {sid}")
        if case_id not in sources.get(sid, {}).get("used_by_cases", []):
            fail(f"rev0367 source {sid} should be used by residual-insurance case")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0367 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 123:
        fail("rev0367 verified ledger must have at least 123 rows and correct count")
    required = {f"VCEDGE-rev0367-{i:04d}" for i in range(108,124)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict)}
    if not required.issubset(seen):
        fail(f"rev0367 missing new verified edge ids: {sorted(required-seen)}")
    by_case = collections.Counter(r.get("case_id") for r in vrows if isinstance(r,dict))
    if by_case.get(case_id, 0) < 16:
        fail("rev0367 residual-insurance case edge count too low")
    if verified.get("case_count_with_verified_edges") != len(by_case) or len(by_case) < 7:
        fail("rev0367 verified ledger case count mismatch")
    packet = load_json(ROOT/"cases"/f"{case_id}-claim-packet.json") or {}
    case_seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict) and r.get("case_id") == case_id}
    if set(packet.get("verified_claim_edge_ids") or []) != case_seen:
        fail("rev0367 claim packet verified edge ids mismatch")
    if packet.get("case_certification_status_after") == "certified_current":
        fail("rev0367 claim packet must not certify case")
    imap = load_json(ROOT/"cases"/f"{case_id}-nfip-fairplan-assessment-map.json") or {}
    if imap.get("certification_status") != "not_certified_current" or len(imap.get("perimeter_layers") or []) < 6:
        fail("rev0367 residual-insurance map must preserve noncertification and six-layer perimeter")
    audit = load_json(ROOT/"docs"/"00-meta"/"residual-insurance-backstop-audit-rev0367.json") or {}
    if audit.get("certification_status") != "not_certified_current" or audit.get("problem_count") != 0:
        fail("rev0367 residual-insurance audit mismatch")
    qa = load_json(ROOT/"docs"/"00-meta"/"verified-claim-edge-quality-audit-rev0367.json") or {}
    if qa.get("total_verified_claim_edges") != len(vrows) or qa.get("missing_required_field_rows"):
        fail("rev0367 verified-edge QA mismatch or missing fields")
    score = load_json(ROOT/"cases"/f"{case_id}-scoreboard.json") or {}
    gate20e = ((score.get("gate_20_subgates") or {}).get("20E_public_upside_recovery") or {})
    if gate20e.get("status") != "watch" or not set(["S563","S564","S566"]).issubset(set(gate20e.get("source_ids") or [])):
        fail("rev0367 must refactor residual-insurance 20E public-upside recovery to watch with sources")
    tool = ROOT/"tools"/"audit_residual_insurance_backstop.py"
    if not tool.exists() or "rev0367" not in tool.read_text(encoding="utf-8", errors="ignore"):
        fail("rev0367 residual-insurance audit tool missing or stale")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["S563-S569", "NFIP", "FAIR Plan", "mortgage", "0", "public-upside"]:
        if phrase not in text:
            fail(f"rev0367 report missing required phrase: {phrase}")




def check_rev0368_public_pension_private_markets_fees_and_liquidity_refactor():
    codename = "public-pension-private-markets-fees-and-liquidity-refactor"
    case_id = "us-state-local-public-pension-risk-rev0318"
    jpath = ROOT/"reports"/f"{codename}-rev0368.json"
    mpath = ROOT/"reports"/f"{codename}-rev0368.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0368 public-pension/private-markets report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0368" or report.get("base_revision") != "rev0367":
        fail("rev0368 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0368 report codename mismatch")
    if report.get("new_sources") != 4 or sorted(report.get("new_source_ids") or []) != ["S570","S571","S572","S573"]:
        fail("rev0368 must add exactly S570-S573")
    # Historical receipt: current_counts is a snapshot and must not chase later live counts.
    if not isinstance(report.get("current_counts"), dict) or not report.get("current_counts"):
        fail("rev0368 report missing current_counts snapshot")
    sources = {s.get("id"):s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    for sid in ["S570","S571","S572","S573"]:
        if sid not in sources:
            fail(f"rev0368 missing source {sid}")
        if case_id not in sources.get(sid, {}).get("used_by_cases", []):
            fail(f"rev0368 source {sid} should be used by public-pension case")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0368 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 139:
        fail("rev0368 verified ledger must have at least 139 rows and correct count")
    required = {f"VCEDGE-rev0368-{i:04d}" for i in range(124,140)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict)}
    if not required.issubset(seen):
        fail(f"rev0368 missing new verified edge ids: {sorted(required-seen)}")
    by_case = collections.Counter(r.get("case_id") for r in vrows if isinstance(r,dict))
    if by_case.get(case_id, 0) < 16:
        fail("rev0368 public-pension case edge count too low")
    if verified.get("case_count_with_verified_edges") != len(by_case) or len(by_case) < 8:
        fail("rev0368 verified ledger case count mismatch")
    packet = load_json(ROOT/"cases"/f"{case_id}-claim-packet.json") or {}
    case_seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict) and r.get("case_id") == case_id}
    if set(packet.get("verified_claim_edge_ids") or []) != case_seen:
        fail("rev0368 public-pension claim packet verified edge ids mismatch")
    if packet.get("case_certification_status_after") == "certified_current":
        fail("rev0368 public-pension claim packet must not certify case")
    pmap = load_json(ROOT/"cases"/f"{case_id}-private-markets-fee-liquidity-map.json") or {}
    if pmap.get("certification_status") != "not_certified_current" or len(pmap.get("perimeter_layers") or []) < 7:
        fail("rev0368 public-pension map must preserve noncertification and seven-layer perimeter")
    audit = load_json(ROOT/"docs"/"00-meta"/"public-pension-private-markets-audit-rev0368.json") or {}
    if audit.get("certification_status") != "not_certified_current" or audit.get("problem_count") != 0:
        fail("rev0368 public-pension audit mismatch")
    qa = load_json(ROOT/"docs"/"00-meta"/"verified-claim-edge-quality-audit-rev0368.json") or {}
    if qa.get("total_verified_claim_edges") != len(vrows) or qa.get("missing_required_field_rows"):
        fail("rev0368 verified-edge QA mismatch or missing fields")
    score = load_json(ROOT/"cases"/f"{case_id}-scoreboard.json") or {}
    gate20e = ((score.get("gate_20_subgates") or {}).get("20E_public_upside_recovery") or {})
    if gate20e.get("status") != "watch" or not set(["S570","S571","S573"]).issubset(set(gate20e.get("source_ids") or [])):
        fail("rev0368 must refactor public-pension 20E public-upside recovery to watch with sources")
    tool = ROOT/"tools"/"audit_public_pension_private_markets.py"
    if not tool.exists() or "rev0368" not in tool.read_text(encoding="utf-8", errors="ignore"):
        fail("rev0368 public-pension audit tool missing or stale")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["S570-S573", "private-market", "fee/carry", "0", "not certified"]:
        if phrase not in text:
            fail(f"rev0368 report missing required phrase: {phrase}")


def check_rev0369_tax_expenditure_claimant_incidence_and_current_law_refactor():
    codename = "tax-expenditure-claimant-incidence-and-current-law-refactor"
    case_id = "tax-expenditure-hidden-public-balance-sheet-rev0319"
    jpath = ROOT/"reports"/f"{codename}-rev0369.json"
    mpath = ROOT/"reports"/f"{codename}-rev0369.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0369 tax-expenditure report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0369" or report.get("base_revision") != "rev0368":
        fail("rev0369 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0369 report codename mismatch")
    if report.get("new_sources") != 4 or sorted(report.get("new_source_ids") or []) != ["S574","S575","S576","S577"]:
        fail("rev0369 must add exactly S574-S577")
    # rev0378 validator refactor: rev0369 current_counts is a historical snapshot, not a live counter.
    if not isinstance(report.get("current_counts"), dict) or not report.get("current_counts"):
        fail("rev0369 report missing current_counts snapshot")
    sources = {s.get("id"):s for s in (load_json(ROOT/"SOURCES.json") or {}).get("sources", [])}
    for sid in ["S574","S575","S576","S577"]:
        if sid not in sources:
            fail(f"rev0369 missing source {sid}")
        if case_id not in sources.get(sid, {}).get("used_by_cases", []):
            fail(f"rev0369 source {sid} should be used by tax-expenditure case")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0369 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 155:
        fail("rev0369 verified ledger must have at least 155 rows and correct count")
    required = {f"VCEDGE-rev0369-{i:04d}" for i in range(140,156)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict)}
    if not required.issubset(seen):
        fail(f"rev0369 missing new verified edge ids: {sorted(required-seen)}")
    by_case = collections.Counter(r.get("case_id") for r in vrows if isinstance(r,dict))
    if by_case.get(case_id, 0) < 16:
        fail("rev0369 tax-expenditure case edge count too low")
    if verified.get("case_count_with_verified_edges") != len(by_case) or len(by_case) < 9:
        fail("rev0369 verified ledger case count mismatch")
    packet = load_json(ROOT/"cases"/f"{case_id}-claim-packet.json") or {}
    case_seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict) and r.get("case_id") == case_id}
    if set(packet.get("verified_claim_edge_ids") or []) != case_seen:
        fail("rev0369 tax-expenditure claim packet verified edge ids mismatch")
    if packet.get("case_certification_status_after") == "certified_current":
        fail("rev0369 tax-expenditure claim packet must not certify case")
    cmap = load_json(ROOT/"cases"/f"{case_id}-claimant-incidence-map.json") or {}
    if cmap.get("certification_status") != "not_certified_current" or len(cmap.get("perimeter_layers") or []) < 7:
        fail("rev0369 tax-expenditure map must preserve noncertification and seven-layer perimeter")
    audit = load_json(ROOT/"docs"/"00-meta"/"tax-expenditure-claimant-incidence-audit-rev0369.json") or {}
    if audit.get("certification_status") != "not_certified_current" or audit.get("problem_count") != 0:
        fail("rev0369 tax-expenditure audit mismatch")
    score = load_json(ROOT/"cases"/f"{case_id}-scoreboard.json") or {}
    gate20e = ((score.get("gate_20_subgates") or {}).get("20E_public_upside_recovery") or {})
    if gate20e.get("status") != "blocked" or not set(["S574","S575"]).issubset(set(gate20e.get("source_ids") or [])):
        fail("rev0369 must block tax-expenditure 20E public-upside recovery with sources")
    if (score.get("certification_gates") or {}).get("gate_20_public_balance_sheet",{}).get("status") != "blocked":
        fail("rev0369 tax-expenditure gate_20 certification gate must remain blocked")
    tool = ROOT/"tools"/"audit_tax_expenditure_claimant_incidence.py"
    if not tool.exists() or "rev0369" not in tool.read_text(encoding="utf-8", errors="ignore"):
        fail("rev0369 tax-expenditure audit tool missing or stale")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["S574-S577", "tax expenditure", "claimant incidence", "public-upside recovery", "not certified"]:
        if phrase not in text:
            fail(f"rev0369 report missing required phrase: {phrase}")



def check_rev0370_medicare_advantage_denial_payment_integrity_refactor():
    codename = "medicare-advantage-denial-payment-integrity-and-claim-security-refactor"
    case_id = "social-security-medicare-claim-security-rev0318"
    report_json = ROOT/"reports"/f"{codename}-rev0370.json"
    report_md = ROOT/"reports"/f"{codename}-rev0370.md"
    if not report_json.exists() or not report_md.exists():
        fail("Missing rev0370 Medicare Advantage refactor report pair")
        return
    report = load_json(report_json) or {}
    if report.get("revision") != "rev0370" or report.get("base_revision") != "rev0369":
        fail("rev0370 report revision/base mismatch")
    if report.get("new_source_ids") != ["S578","S579","S580","S581","S582","S583"]:
        fail("rev0370 report new_source_ids mismatch")
    if report.get("new_verified_claim_edge_count") != 16:
        fail("rev0370 must add 16 verified claim edges")
    ledger = load_json(ROOT/"cases/VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    rows = [r for r in ledger.get("verified_claim_edges", []) if r.get("created_revision") == "rev0370"]
    if len(rows) != 16:
        fail(f"rev0370 ledger edge count mismatch: {len(rows)}")
    if {sid for r in rows for sid in r.get("source_ids", [])} != {"S578","S579","S580","S581","S582","S583"}:
        fail("rev0370 edge source set mismatch")
    if not all(r.get("case_id") == case_id for r in rows):
        fail("rev0370 edges must all bind to the Social Security/Medicare case")
    for rel in [
        f"cases/{case_id}-claim-packet.json",
        f"cases/{case_id}-claim-packet.md",
        f"cases/{case_id}-medicare-advantage-payment-denial-map.json",
        f"cases/{case_id}-medicare-advantage-payment-denial-map.md",
        "docs/00-meta/medicare-advantage-payment-denial-audit-rev0370.json",
        "docs/00-meta/medicare-advantage-payment-denial-audit-rev0370.md",
        "tools/audit_medicare_advantage_payment_denial.py",
    ]:
        if not (ROOT/rel).exists():
            fail(f"Missing rev0370 artifact: {rel}")
    packet = load_json(ROOT/f"cases/{case_id}-claim-packet.json") or {}
    if packet.get("case_certification_status_after") != "not_certified_current":
        fail("rev0370 claim packet must remain not_certified_current")
    audit = load_json(ROOT/"docs/00-meta/medicare-advantage-payment-denial-audit-rev0370.json") or {}
    if audit.get("problem_count") != 0 or audit.get("new_rev0370_edge_count") != 16:
        fail("rev0370 MA audit counts must be clean")
    score = load_json(ROOT/f"cases/{case_id}-scoreboard.json") or {}
    used = set(iter_source_ids_in_json(score))
    if not {"S578","S579","S580","S581","S582","S583"}.issubset(used):
        fail("rev0370 Social Security/Medicare scoreboard missing MA sources")
    text = report_md.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["Medicare Advantage", "prior-authorization", "payment", "0 certified current cases"]:
        if phrase not in text:
            fail(f"rev0370 report missing phrase: {phrase}")


def check_rev0377_ma_medical_necessity_criteria_and_clinical_remedy_guardrails():
    codename = "ma-medical-necessity-criteria-and-clinical-remedy-guardrails"
    report_path = ROOT/"reports"/f"{codename}-rev0377.json"
    report_md = ROOT/"reports"/f"{codename}-rev0377.md"
    if not report_path.exists() or not report_md.exists():
        fail("Missing rev0377 MA medical-necessity report pair")
        return
    report = load_json(report_path) or {}
    if report.get("revision") != "rev0377" or report.get("base_revision") != "rev0376":
        fail("rev0377 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0377 report codename mismatch")
    if report.get("new_sources") != 4 or sorted(report.get("new_source_ids") or []) != ["S605","S606","S607","S608"]:
        fail("rev0377 must add exactly S605-S608")
    verified = load_json(ROOT/"cases/VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 217:
        fail("rev0377 verified ledger must have at least 217 rows and correct count")
    required_ids = {f"VCEDGE-rev0377-{i:04d}" for i in range(210,218)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r, dict)}
    if not required_ids.issubset(seen):
        fail(f"rev0377 missing verified edge ids: {sorted(required_ids-seen)}")
    rel = collections.Counter(r.get("relationship_code") for r in vrows)
    if rel.get("contradicts", 0) < 2:
        fail("rev0377 must introduce at least two contradict records")
    bridge = load_json(ROOT/"cases/social-security-medicare-claim-security-rev0318-ma-medical-necessity-clinical-remedy-guardrails-rev0377.json") or {}
    if bridge.get("certification_status_after_rev0377") != "not_certified_current":
        fail("rev0377 bridge must remain noncertifying")
    req_sources = {"S599","S605","S606","S607","S608"}
    if not req_sources.issubset(set(bridge.get("source_ids") or [])):
        fail("rev0377 bridge missing required source ids")
    req_fields = {"medicare_coverage_authority_type","medicare_coverage_authority_locator","internal_coverage_criteria_used_flag","internal_coverage_criteria_public_url","medical_records_sufficient_flag","physician_or_clinical_reviewer_conclusion","service_would_be_covered_under_original_medicare_flag","denial_cause_taxonomy","algorithm_or_ai_tool_used","human_review_level","effectuation_deadline_date","service_authorized_or_provided_date","provider_payment_restored_date","effectuation_deadline_met_flag","beneficiary_harm_or_abandonment_signal"}
    if not req_fields.issubset(set(bridge.get("required_clinical_remedy_fields") or [])):
        fail("rev0377 bridge missing clinical-remedy required fields")
    bridge_text = (ROOT/"cases/social-security-medicare-claim-security-rev0318-ma-medical-necessity-clinical-remedy-guardrails-rev0377.json").read_text(encoding="utf-8", errors="ignore")
    for phrase in ["No denial-rate pass","No appeal-overturn pass","No internal-criteria pass","No algorithm/delegation opacity pass","No CY2026-AI-guardrail pass","No remedy pass"]:
        if phrase not in bridge_text:
            fail(f"rev0377 bridge missing false-pass phrase: {phrase}")
    audit = load_json(ROOT/"docs/00-meta/ma-medical-necessity-clinical-remedy-guardrails-audit-rev0377.json") or {}
    if audit.get("new_locator_record_count") != 8 or audit.get("new_contradict_record_count") != 2 or audit.get("certified_current_after") is not False:
        fail("rev0377 audit count/certification mismatch")
    script = ROOT/"tools/audit_ma_medical_necessity_clinical_remedy_guardrails.py"
    if not script.exists() or "REQUIRED_FIELDS" not in script.read_text(encoding="utf-8", errors="ignore"):
        fail("rev0377 audit script missing or too weak")
    backlog = load_json(ROOT/"cases/CLAIM_ATOM_BACKLOG.json") or {}
    top = (backlog.get("claim_atoms") or [{}])[0]
    if not set(["S600","S601","S602","S603","S604","S605","S606","S607","S608"]).issubset(set(top.get("source_ids") or [])):
        fail("rev0377 top claim atom must carry S600-S608")
    text = report_md.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["medical necessity", "internal criteria", "effectuation", "contradict", "not certified current"]:
        if phrase not in text:
            fail(f"rev0377 report missing required phrase: {phrase}")

def check_manifest():
    manifest_path = ROOT/"MANIFEST.json"
    checksum_path = ROOT/"MANIFEST.sha256"
    if not manifest_path.exists():
        fail("Missing MANIFEST.json")
        return
    if not checksum_path.exists():
        fail("Missing MANIFEST.sha256")
        return
    manifest = load_json(manifest_path)
    if not manifest:
        return
    if manifest.get("revision") != CURRENT_REVISION:
        fail("MANIFEST.json revision mismatch")
    # Exclude both manifest files from the hash inventory to avoid a circular hash dependency.
    expected = sorted(
        str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
        if p.is_file() and str(p.relative_to(ROOT)) not in {"MANIFEST.json", "MANIFEST.sha256"}
    )
    rows = manifest.get("files") or []
    listed = [row.get("path") for row in rows if isinstance(row, dict)]
    if manifest.get("file_count") != len(expected) or len(rows) != len(expected):
        fail(f"MANIFEST.json count mismatch: expected {len(expected)}")
    if listed != expected:
        missing = sorted(set(expected) - set(listed))
        extra = sorted(set(listed) - set(expected))
        fail(f"Manifest file set mismatch; missing={missing[:10]} extra={extra[:10]}")
    for item in rows:
        rel = item.get("path")
        if not rel:
            fail("Manifest row missing path")
            continue
        p = ROOT/rel
        if not p.exists():
            fail(f"Manifest file missing: {rel}")
            continue
        raw = p.read_bytes()
        if item.get("bytes") != len(raw):
            fail(f"Manifest byte count mismatch: {rel}")
        h = hashlib.sha256(raw).hexdigest()
        if h != item.get("sha256"):
            fail(f"Manifest hash mismatch: {rel}")
    checksum = checksum_path.read_text(encoding="utf-8", errors="ignore").strip()
    actual_manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    if checksum != f"{actual_manifest_hash}  MANIFEST.json":
        fail("MANIFEST.sha256 does not match MANIFEST.json")



def check_rev0372_ma_contract_level_claim_security_and_validator_pruning_sprint():
    codename = "ma-contract-level-claim-security-and-validator-pruning-sprint"
    jpath = ROOT/"reports"/f"{codename}-rev0372.json"
    mpath = ROOT/"reports"/f"{codename}-rev0372.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0372 MA contract-level sprint report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0372" or report.get("base_revision") != "rev0371":
        fail("rev0372 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0372 report codename mismatch")
    if report.get("new_sources") != 7 or sorted(report.get("new_source_ids") or []) != ["S584","S585","S586","S587","S588","S589","S590"]:
        fail("rev0372 must add exactly S584-S590")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0372 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 179:
        fail("rev0372 verified ledger must have at least 179 rows and correct count")
    required = {f"VCEDGE-rev0372-{i:04d}" for i in range(172,180)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r,dict)}
    if not required.issubset(seen):
        fail(f"rev0372 missing new edge ids: {sorted(required-seen)}")
    sids = set()
    for row in vrows:
        for sid in row.get("source_ids") or []:
            sids.add(sid)
    for sid in ["S584","S585","S586","S587","S588","S589","S590"]:
        if sid not in sids:
            fail(f"rev0372 verified edges missing source {sid}")
    sprint = load_json(ROOT/"cases"/"social-security-medicare-claim-security-rev0318-ma-contract-certification-sprint-rev0372.json") or {}
    if sprint.get("status") == "certified_current" or sprint.get("red_amber_green",{}).get("certified_current") != "red_zero_cases_certified_current":
        fail("rev0372 sprint must preserve noncertification boundary")
    audit = load_json(ROOT/"docs"/"00-meta"/"medicare-advantage-contract-certification-audit-rev0372.json") or {}
    if audit.get("certified_current_after") is not False or audit.get("new_locator_record_count") != 8:
        fail("rev0372 MA audit certification/count mismatch")
    # The live surface validator must be executable and no longer hardcode rev0371 semantic-audit paths.
    vls = (ROOT/"tools"/"validate_live_surfaces.py").read_text(encoding="utf-8", errors="ignore")
    if "def main(" not in vls or 'if __name__ == "__main__"' not in vls:
        fail("rev0372 validate_live_surfaces.py must expose a CLI")
    if "verified-claim-edge-semantic-boundary-audit-rev0371.json" in vls:
        fail("rev0372 validate_live_surfaces.py still hardcodes rev0371 semantic audit")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["contract-level", "LDS", "RADV", "UM", "not certified current", "validator"]:
        if phrase not in text:
            fail(f"rev0372 report missing required phrase: {phrase}")


def check_case_maturity_live_count_sync():
    evidence = load_json(ROOT/"cases/EVIDENCE_LEDGER.json") or {}
    verified = load_json(ROOT/"cases/VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    erows = evidence.get("edge_rows") or []
    vrows = verified.get("verified_claim_edges") or []
    expected = {}
    for row in erows:
        cid = row.get("case_id")
        if not cid:
            continue
        bucket = expected.setdefault(cid, {"mechanical_association_count": 0, "sources": set(), "claim_paths": set(), "verified_claim_edge_count": 0})
        bucket["mechanical_association_count"] += 1
        bucket["sources"].add(row.get("source_id"))
        bucket["claim_paths"].add(row.get("claim_path"))
    for row in vrows:
        cid = row.get("case_id")
        if cid:
            expected.setdefault(cid, {"mechanical_association_count": 0, "sources": set(), "claim_paths": set(), "verified_claim_edge_count": 0})["verified_claim_edge_count"] += 1
    normalized = {cid: {"mechanical_association_count": vals["mechanical_association_count"], "unique_source_count": len(vals["sources"]), "unique_claim_path_count": len(vals["claim_paths"]), "verified_claim_edge_count": vals["verified_claim_edge_count"]} for cid, vals in expected.items()}
    for rel, key in [("cases/CASE_MATURITY_LEDGER.json", "rows"), ("cases/CASE_LEDGER.json", "cases")]:
        data = load_json(ROOT/rel) or {}
        for row in data.get(key, []):
            cid = row.get("case_id") if isinstance(row, dict) else None
            if cid not in normalized:
                continue
            for field, value in normalized[cid].items():
                if row.get(field) != value:
                    fail(f"{rel} {cid} {field} {row.get(field)} != live {value}")


def check_rev0373_ma_row_contract_remedy_appeal_and_quality_workbench():
    codename = "ma-row-contract-remedy-appeal-and-quality-workbench"
    jpath = ROOT/"reports"/f"{codename}-rev0373.json"
    mpath = ROOT/"reports"/f"{codename}-rev0373.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0373 MA row-contract report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0373" or report.get("base_revision") != "rev0372":
        fail("rev0373 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0373 report codename mismatch")
    if report.get("new_sources") != 6 or sorted(report.get("new_source_ids") or []) != ["S591","S592","S593","S594","S595","S596"]:
        fail("rev0373 must add exactly S591-S596")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0373 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 186:
        fail("rev0373 verified ledger must have at least 186 rows and correct count")
    required = {f"VCEDGE-rev0373-{i:04d}" for i in range(180,187)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r, dict)}
    if not required.issubset(seen):
        fail(f"rev0373 missing new edge ids: {sorted(required-seen)}")
    workbench = load_json(ROOT/"cases"/"social-security-medicare-claim-security-rev0318-ma-contract-claim-security-workbench-rev0373.json") or {}
    if workbench.get("certification_status_after_rev0373") != "not_certified_current":
        fail("rev0373 workbench must remain noncertifying")
    required_cols = {"contract_id","report_year","service_category","monthly_enrollment","request_count","adverse_or_partially_adverse_count","appeal_count","overturn_count","criteria_id","delegated_entity","delay_days","beneficiary_harm_flag","beneficiary_remedy_type","star_rating_contract","radv_overpayment_amount","radv_recovery_status","integrated_denial_notice_issued","source_ids"}
    cols = set(workbench.get("required_columns") or [])
    missing = sorted(required_cols - cols)
    if missing:
        fail(f"rev0373 workbench missing required columns: {missing}")
    if len(workbench.get("false_pass_blocks") or []) < 6:
        fail("rev0373 workbench false_pass_blocks too short")
    audit = load_json(ROOT/"docs"/"00-meta"/"ma-row-contract-workbench-audit-rev0373.json") or {}
    if audit.get("certified_current_after") is not False or audit.get("new_locator_record_count") != 7:
        fail("rev0373 MA audit certification/count mismatch")
    script = ROOT/"tools"/"audit_ma_row_contract_workbench.py"
    if not script.exists() or "REQUIRED" not in script.read_text(encoding="utf-8", errors="ignore"):
        fail("rev0373 workbench audit script missing or too weak")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["row contract", "appeal", "remedy", "quality", "RADV", "not certified current"]:
        if phrase not in text:
            fail(f"rev0373 report missing required phrase: {phrase}")



def check_rev0374_ma_appeal_burden_public_pilot_and_validator_refactor():
    codename = "ma-appeal-burden-public-pilot-and-validator-refactor"
    jpath = ROOT/"reports"/f"{codename}-rev0374.json"
    mpath = ROOT/"reports"/f"{codename}-rev0374.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0374 MA appeal-burden public-pilot report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0374" or report.get("base_revision") != "rev0373":
        fail("rev0374 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0374 report codename mismatch")
    if report.get("new_sources") != 0 or report.get("new_source_ids") not in ([], None):
        fail("rev0374 must add zero new sources; this pass is a substance pilot")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0374 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 193:
        fail("rev0374 verified ledger must have at least 193 rows and correct count")
    required = {f"VCEDGE-rev0374-{i:04d}" for i in range(187,194)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r, dict)}
    if not required.issubset(seen):
        fail(f"rev0374 missing new edge ids: {sorted(required-seen)}")
    pilot = load_json(ROOT/"cases"/"social-security-medicare-claim-security-rev0318-ma-appeal-burden-public-pilot-rev0374.json") or {}
    if pilot.get("certification_status_after_rev0374") != "not_certified_current":
        fail("rev0374 public pilot must remain noncertifying")
    blob = json.dumps(pilot, sort_keys=True)
    for phrase in ["52.8", "4.1", "0.077", "0.115", "0.807", "0.95", "A high overturn rate is not a self-correction pass"]:
        if phrase not in blob:
            fail(f"rev0374 public pilot missing required public metric/inference phrase: {phrase}")
    if len(pilot.get("false_pass_blocks") or []) < 6:
        fail("rev0374 public pilot false_pass_blocks too short")
    audit = load_json(ROOT/"docs"/"00-meta"/"ma-appeal-burden-public-pilot-audit-rev0374.json") or {}
    if audit.get("certified_current_after") is not False or audit.get("new_locator_record_count") != 7:
        fail("rev0374 MA appeal-burden audit certification/count mismatch")
    script = ROOT/"tools"/"audit_ma_appeal_burden_pilot.py"
    if not script.exists() or "EXPECTED" not in script.read_text(encoding="utf-8", errors="ignore"):
        fail("rev0374 public-pilot audit script missing or too weak")
    row_script = (ROOT/"tools"/"audit_ma_row_contract_workbench.py").read_text(encoding="utf-8", errors="ignore")
    if "resolve_workbench" not in row_script or "rev0374" not in row_script:
        fail("rev0374 row-contract audit refactor is missing")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["no new source", "appeal-burden", "overturn", "not certified current", "validator"]:
        if phrase.lower() not in text.lower():
            fail(f"rev0374 report missing required phrase: {phrase}")



def check_rev0375_ma_contractor_resident_harm_and_enforcement_bridge():
    codename = "ma-contractor-resident-harm-and-enforcement-bridge"
    jpath = ROOT/"reports"/f"{codename}-rev0375.json"
    mpath = ROOT/"reports"/f"{codename}-rev0375.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0375 MA contractor/resident-harm/enforcement bridge report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0375" or report.get("base_revision") != "rev0374":
        fail("rev0375 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0375 report codename mismatch")
    if report.get("new_sources") != 3 or report.get("new_source_ids") != ["S597", "S598", "S599"]:
        fail("rev0375 must add exactly S597-S599")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0375 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 201:
        fail("rev0375 verified ledger must have at least 201 rows and correct count")
    required = {f"VCEDGE-rev0375-{i:04d}" for i in range(194,202)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r, dict)}
    if not required.issubset(seen):
        fail(f"rev0375 missing new edge ids: {sorted(required-seen)}")
    bridge = load_json(ROOT/"cases"/"social-security-medicare-claim-security-rev0318-ma-contractor-resident-harm-enforcement-bridge-rev0375.json") or {}
    if bridge.get("certification_status_after_rev0375") != "not_certified_current":
        fail("rev0375 bridge must remain noncertifying")
    blob = json.dumps(bridge, sort_keys=True)
    for phrase in ["navihealth_processed_share_of_snf_requests", "navihealth_appealed_denial_overturn_rate", "nursing_home_resident_snf_denial_rate", "program_audit_result_id", "cms_enforcement_action_id", "beneficiary_restoration_status"]:
        if phrase not in blob:
            fail(f"rev0375 bridge missing required metric/field phrase: {phrase}")
    for sid in ["S597", "S598", "S599"]:
        if sid not in blob:
            fail(f"rev0375 bridge missing source {sid}")
    if len(bridge.get("false_pass_blocks") or []) < 6:
        fail("rev0375 bridge false_pass_blocks too short")
    audit = load_json(ROOT/"docs"/"00-meta"/"ma-contractor-resident-harm-enforcement-bridge-audit-rev0375.json") or {}
    if audit.get("certified_current_after") is not False or audit.get("new_locator_record_count") != 8:
        fail("rev0375 MA bridge audit certification/count mismatch")
    script = ROOT/"tools"/"audit_ma_contractor_resident_harm_enforcement_bridge.py"
    if not script.exists() or "navihealth_processed_share_of_snf_requests" not in script.read_text(encoding="utf-8", errors="ignore"):
        fail("rev0375 bridge audit script missing or too weak")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["contractor", "resident", "enforcement", "restoration", "not certified current"]:
        if phrase.lower() not in text.lower():
            fail(f"rev0375 report missing required phrase: {phrase}")


def check_rev0376_ma_equity_disaggregation_and_beneficiary_experience_join():
    codename = "ma-equity-disaggregation-and-beneficiary-experience-join"
    jpath = ROOT/"reports"/f"{codename}-rev0376.json"
    mpath = ROOT/"reports"/f"{codename}-rev0376.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0376 MA equity-disaggregation report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0376" or report.get("base_revision") != "rev0375":
        fail("rev0376 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0376 report codename mismatch")
    if report.get("new_sources") != 5 or report.get("new_source_ids") != ["S600", "S601", "S602", "S603", "S604"]:
        fail("rev0376 must add exactly S600-S604")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0376 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 209:
        fail("rev0376 verified ledger must have at least 209 rows and correct count")
    required = {f"VCEDGE-rev0376-{i:04d}" for i in range(202,210)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r, dict)}
    if not required.issubset(seen):
        fail(f"rev0376 missing new edge ids: {sorted(required-seen)}")
    bridge = load_json(ROOT/"cases"/f"social-security-medicare-claim-security-rev0318-ma-equity-disaggregation-beneficiary-experience-bridge-rev0376.json") or {}
    if bridge.get("certification_status_after_rev0376") != "not_certified_current":
        fail("rev0376 bridge must remain noncertifying")
    blob = json.dumps(bridge, sort_keys=True)
    for phrase in ["dual_eligible_status", "lis_or_low_income_cost_sharing_status", "race_ethnicity_code_or_method", "beneficiary_reported_access_problem", "mmd_disparity_context_measure", "eho4all_or_hei_reward_active_flag", "cell_suppression_or_disclosure_limit"]:
        if phrase not in blob:
            fail(f"rev0376 bridge missing required metric/field phrase: {phrase}")
    for sid in ["S600", "S601", "S602", "S603", "S604"]:
        if sid not in blob:
            fail(f"rev0376 bridge missing source {sid}")
    if len(bridge.get("false_pass_blocks") or []) < 8:
        fail("rev0376 bridge false_pass_blocks too short")
    audit = load_json(ROOT/"docs"/"00-meta"/f"ma-equity-disaggregation-beneficiary-experience-bridge-audit-rev0376.json") or {}
    if audit.get("certified_current_after") is not False or audit.get("new_locator_record_count") != 8:
        fail("rev0376 MA equity bridge audit certification/count mismatch")
    script = ROOT/"tools"/"audit_ma_equity_disaggregation_beneficiary_experience_bridge.py"
    if not script.exists() or "dual_eligible_status" not in script.read_text(encoding="utf-8", errors="ignore"):
        fail("rev0376 bridge audit script missing or too weak")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["equity", "subgroup", "beneficiary-experience", "Star Rating", "not certified current"]:
        if phrase.lower() not in text.lower():
            fail(f"rev0376 report missing required phrase: {phrase}")


def check_rev0378_ma_access_availability_ghost_network_and_denied_claim_visibility_bridge():
    codename = "ma-access-availability-ghost-network-and-denied-claim-visibility-bridge"
    jpath = ROOT/"reports"/f"{codename}-rev0378.json"
    mpath = ROOT/"reports"/f"{codename}-rev0378.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0378 MA access availability report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0378" or report.get("base_revision") != "rev0377":
        fail("rev0378 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0378 report codename mismatch")
    if report.get("new_sources") != 6 or report.get("new_source_ids") != ["S609","S610","S611","S612","S613","S614"]:
        fail("rev0378 must add exactly S609-S614")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0378 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 225:
        fail("rev0378 verified ledger must have at least 225 rows and correct count")
    required = {f"VCEDGE-rev0378-{i:04d}" for i in range(218,226)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r, dict)}
    if not required.issubset(seen):
        fail(f"rev0378 missing new edge ids: {sorted(required-seen)}")
    bridge = load_json(ROOT/"cases/social-security-medicare-claim-security-rev0318-ma-access-availability-ghost-network-claim-visibility-bridge-rev0378.json") or {}
    if bridge.get("certification_status_after_rev0378") != "not_certified_current":
        fail("rev0378 bridge must remain noncertifying")
    blob = json.dumps(bridge, sort_keys=True)
    for phrase in ["provider_directory_api_update_timestamp", "automated_criteria_check_pass_fail", "ghost_provider_flag", "definitive_denied_claim_indicator_present_flag", "No provider-directory pass", "No encounter-adjustment pass"]:
        if phrase not in blob:
            fail(f"rev0378 bridge missing required phrase: {phrase}")
    for sid in ["S609","S610","S611","S612","S613","S614"]:
        if sid not in blob:
            fail(f"rev0378 bridge missing source {sid}")
    if len(bridge.get("false_pass_blocks") or []) < 10:
        fail("rev0378 bridge false_pass_blocks too short")
    audit = load_json(ROOT/"docs/00-meta/ma-access-availability-ghost-network-claim-visibility-audit-rev0378.json") or {}
    if audit.get("certified_current_after") is not False or audit.get("new_locator_record_count") != 8 or audit.get("new_contradict_record_count") != 2:
        fail("rev0378 MA access audit certification/count mismatch")
    script = ROOT/"tools"/"audit_ma_access_availability_ghost_network_claim_visibility.py"
    if not script.exists() or "definitive_denied_claim_indicator_present_flag" not in script.read_text(encoding="utf-8", errors="ignore"):
        fail("rev0378 bridge audit script missing or too weak")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["ghost-network", "provider-directory", "denied-claim", "behavioral-health", "not certified current"]:
        if phrase.lower() not in text.lower():
            fail(f"rev0378 report missing required phrase: {phrase}")


def check_rev0379_ma_payment_integrity_rebate_value_risk_coding_public_cost_waterfall():
    codename = "ma-payment-integrity-rebate-value-risk-coding-and-public-cost-waterfall"
    jpath = ROOT/"reports"/f"{codename}-rev0379.json"
    mpath = ROOT/"reports"/f"{codename}-rev0379.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0379 MA payment-integrity report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0379" or report.get("base_revision") != "rev0378":
        fail("rev0379 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0379 report codename mismatch")
    if report.get("new_sources") != 6 or report.get("new_source_ids") != ["S615","S616","S617","S618","S619","S620"]:
        fail("rev0379 must add exactly S615-S620")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0379 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 235:
        fail("rev0379 verified ledger must have at least 235 rows and correct count")
    required = {f"VCEDGE-rev0379-{i:04d}" for i in range(226,236)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r, dict)}
    if not required.issubset(seen):
        fail(f"rev0379 missing new edge ids: {sorted(required-seen)}")
    rel = collections.Counter(r.get("relationship_code") for r in vrows if isinstance(r, dict))
    if rel.get("contradicts",0) < 6:
        fail("rev0379 must raise contradict records to at least six")
    bridge = load_json(ROOT/"cases/social-security-medicare-claim-security-rev0318-ma-payment-integrity-rebate-value-risk-coding-waterfall-rev0379.json") or {}
    if bridge.get("certification_status_after_rev0379") != "not_certified_current" or bridge.get("certified_current_case_count_after") != 0:
        fail("rev0379 bridge must remain noncertifying")
    blob = json.dumps(bridge, sort_keys=True)
    for phrase in ["diagnosis_source_type", "service_record_linkage_flag", "rebate_amount", "supplemental_benefit_utilization_measure", "part_b_premium_effect", "taxpayer_cost_effect", "radv_recovery_amount", "No rebate-value pass", "No risk-score pass", "No RADV-existence pass"]:
        if phrase not in blob:
            fail(f"rev0379 bridge missing required phrase: {phrase}")
    for sid in ["S580","S581","S588","S589","S615","S616","S617","S618","S619","S620"]:
        if sid not in blob:
            fail(f"rev0379 bridge missing source {sid}")
    if len(bridge.get("false_pass_blocks") or []) < 10:
        fail("rev0379 bridge false_pass_blocks too short")
    audit = load_json(ROOT/"docs/00-meta/ma-payment-integrity-rebate-value-risk-coding-audit-rev0379.json") or {}
    if audit.get("certified_current_after") is not False or audit.get("new_locator_record_count") != 10 or audit.get("new_contradict_record_count") != 2:
        fail("rev0379 MA payment-integrity audit certification/count mismatch")
    script = ROOT/"tools"/"audit_ma_payment_integrity_rebate_value_risk_coding.py"
    if not script.exists() or "supplemental_benefit_utilization_measure" not in script.read_text(encoding="utf-8", errors="ignore"):
        fail("rev0379 bridge audit script missing or too weak")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["payment integrity", "rebate", "risk", "RADV", "public-cost", "not certified current"]:
        if phrase.lower() not in text.lower():
            fail(f"rev0379 report missing required phrase: {phrase}")


def check_rev0380_ma_encounter_benefit_use_minimum_certifying_row_lock():
    codename = "ma-encounter-benefit-use-and-minimum-certifying-row-lock"
    jpath = ROOT/"reports"/f"{codename}-rev0380.json"
    mpath = ROOT/"reports"/f"{codename}-rev0380.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0380 MA encounter/benefit-use report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0380" or report.get("base_revision") != "rev0379":
        fail("rev0380 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0380 report codename mismatch")
    if report.get("new_sources") != 7 or report.get("new_source_ids") != ["S621","S622","S623","S624","S625","S626","S627"]:
        fail("rev0380 must add exactly S621-S627")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0380 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 245:
        fail("rev0380 verified ledger must have at least 245 rows and correct count")
    required = {f"VCEDGE-rev0380-{i:04d}" for i in range(236,246)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r, dict)}
    if not required.issubset(seen):
        fail(f"rev0380 missing new edge ids: {sorted(required-seen)}")
    rel = collections.Counter(r.get("relationship_code") for r in vrows if isinstance(r, dict))
    if rel.get("contradicts",0) < 9:
        fail("rev0380 must raise contradict records to at least nine")
    bridge = load_json(ROOT/"cases/social-security-medicare-claim-security-rev0318-ma-encounter-benefit-use-minimum-certifying-row-lock-rev0380.json") or {}
    if bridge.get("certification_status_after_rev0380") != "not_certified_current" or bridge.get("certified_current_case_count_after") != 0:
        fail("rev0380 bridge must remain noncertifying")
    blob = json.dumps(bridge, sort_keys=True)
    for phrase in ["benefit_offered_flag", "service_request_id", "organization_determination_outcome", "encounter_join_key", "encounter_no_payment_variables_flag", "payment_source_id", "supplemental_benefit_denied_not_in_utilization_flag", "rebate_actual_use_evidence", "beneficiary_service_restoration_date", "No encounter-data pass", "No PBP/offered-benefit pass", "No rebate-allocation pass"]:
        if phrase not in blob:
            fail(f"rev0380 bridge missing required phrase: {phrase}")
    for sid in ["S585","S591","S614","S621","S622","S623","S624","S625","S626","S627"]:
        if sid not in blob:
            fail(f"rev0380 bridge missing source {sid}")
    if len(bridge.get("false_pass_blocks") or []) < 10:
        fail("rev0380 bridge false_pass_blocks too short")
    audit = load_json(ROOT/"docs/00-meta/ma-encounter-benefit-use-minimum-certifying-row-lock-audit-rev0380.json") or {}
    if audit.get("certified_current_after") is not False or audit.get("new_locator_record_count") != 10 or audit.get("new_contradict_record_count") != 3:
        fail("rev0380 MA row-lock audit certification/count mismatch")
    script = ROOT/"tools"/"audit_ma_encounter_benefit_use_minimum_certifying_row_lock.py"
    if not script.exists() or "supplemental_benefit_denied_not_in_utilization_flag" not in script.read_text(encoding="utf-8", errors="ignore"):
        fail("rev0380 row-lock audit script missing or too weak")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["encounter", "benefit", "minimum certifying row", "rebate", "not certified current"]:
        if phrase.lower() not in text.lower():
            fail(f"rev0380 report missing required phrase: {phrase}")



def check_rev0381_ma_steering_lock_in_broker_incentive_exit_rights_bridge():
    codename = "ma-steering-lock-in-broker-incentive-and-exit-rights-bridge"
    jpath = ROOT/"reports"/f"{codename}-rev0381.json"
    mpath = ROOT/"reports"/f"{codename}-rev0381.md"
    if not jpath.exists() or not mpath.exists():
        fail("Missing rev0381 MA steering/lock-in report pair")
        return
    report = load_json(jpath) or {}
    if report.get("revision") != "rev0381" or report.get("base_revision") != "rev0380":
        fail("rev0381 report revision/base_revision mismatch")
    if report.get("codename") != codename:
        fail("rev0381 report codename mismatch")
    if report.get("new_sources") != 8 or report.get("new_source_ids") != ["S628","S629","S630","S631","S632","S633","S634","S635"]:
        fail("rev0381 must add exactly S628-S635")
    verified = load_json(ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json") or {}
    vrows = verified.get("verified_claim_edges") or []
    if verified.get("revision_current") != CURRENT_REVISION:
        fail("rev0381 verified ledger revision_current mismatch")
    if verified.get("verified_claim_edge_count") != len(vrows) or len(vrows) < 255:
        fail("rev0381 verified ledger must have at least 255 rows and correct count")
    required = {f"VCEDGE-rev0381-{i:04d}" for i in range(246,256)}
    seen = {r.get("verified_claim_edge_id") for r in vrows if isinstance(r, dict)}
    if not required.issubset(seen):
        fail(f"rev0381 missing new edge ids: {sorted(required-seen)}")
    rel = collections.Counter(r.get("relationship_code") for r in vrows if isinstance(r, dict))
    if rel.get("contradicts",0) < 11:
        fail("rev0381 must raise contradict records to at least eleven")
    bridge = load_json(ROOT/"cases/social-security-medicare-claim-security-rev0318-ma-steering-lock-in-broker-incentive-exit-rights-bridge-rev0381.json") or {}
    if bridge.get("certification_status_after_rev0381") != "not_certified_current" or bridge.get("certified_current_case_count_after") != 0:
        fail("rev0381 bridge must remain noncertifying")
    blob = json.dumps(bridge, sort_keys=True)
    for phrase in ["enrollment_event_id", "broker_or_agent_npn", "tpmo_or_lead_generator_id", "compensation_amount_initial", "renewal_compensation_amount", "plan_universe_presented", "plans_not_presented_or_blocked", "financial_incentive_or_bonus_marker", "marketing_or_hcp_referral_payment_marker", "written_consent_to_share_lead_data", "beneficiary_disability_status", "dual_lis_or_complex_care_marker", "misleading_marketing_complaint_id", "cms_complaint_tracking_module_or_ctm_id", "special_enrollment_period_or_correction_right", "medigap_guaranteed_issue_status", "medigap_underwriting_barrier", "exit_to_traditional_medicare_feasibility", "post_enrollment_denial_or_access_problem", "claim_security_row_join_key", "No enrollment-neutral pass", "No broker-disclosure pass", "No compensation-cap pass", "No complaint-only pass", "No Medigap-exit pass", "No DOJ-allegation pass", "No OIG-work-plan pass"]:
        if phrase not in blob:
            fail(f"rev0381 bridge missing required phrase: {phrase}")
    for sid in ["S628","S629","S630","S631","S632","S633","S634","S635"]:
        if sid not in blob:
            fail(f"rev0381 bridge missing source {sid}")
    if len(bridge.get("false_pass_blocks") or []) < 10:
        fail("rev0381 bridge false_pass_blocks too short")
    audit = load_json(ROOT/"docs/00-meta/ma-steering-lock-in-broker-incentive-exit-rights-audit-rev0381.json") or {}
    if audit.get("certified_current_after") is not False or audit.get("new_locator_record_count") != 10 or audit.get("new_contradict_record_count") != 2:
        fail("rev0381 steering/lock-in audit certification/count mismatch")
    script = ROOT/"tools"/"audit_ma_steering_lock_in_broker_incentive_exit_rights.py"
    if not script.exists() or "medigap_underwriting_barrier" not in script.read_text(encoding="utf-8", errors="ignore"):
        fail("rev0381 steering/lock-in audit script missing or too weak")
    text = mpath.read_text(encoding="utf-8", errors="ignore")
    for phrase in ["steering", "lock-in", "broker", "Medigap", "not certified current"]:
        if phrase.lower() not in text.lower():
            fail(f"rev0381 report missing required phrase: {phrase}")


def main():
    check_json()
    check_json_source_ids()
    check_scoreboards()
    check_source_refs()
    check_links()
    check_frontmatter()
    check_duplicate_frontmatter_blocks()
    check_source_sequence()
    check_source_metadata_completeness()
    check_current_release_surfaces()
    check_current_count_surfaces()
    check_live_operator_surface_parity()
    check_entrypoint_backtick_paths()
    check_archive_index_sync()
    check_scoreboard_spec_schema_sync()
    check_gate_inventory_coverage()
    check_gate20_register_presence()
    check_case_ledger_coverage()
    check_case_maturity_live_count_sync()
    check_case_scoreboard_pairing()
    check_case_memo_scoreboard_refresh_sync()
    check_no_cache_artifacts()
    check_source_use_register_sync()
    check_evidence_ledger_sync()
    check_route_registry_sync()
    check_field_registry_sync()
    check_currentness_ledger_sync()
    check_case_source_refresh_ordering()
    check_source_duplicate_audit_sync()
    check_current_validation_report_present()
    check_remedy_operability_register_presence()
    check_gate20_generic_proof_debt_repetition()
    check_rev0308_measurement_scoreboards()
    check_rev0309_enforcement_scoreboards()
    check_rev0310_democratic_power_scoreboards()
    check_rev0311_jurisdictional_mobility_scoreboards()
    check_rev0312_workplace_power_scoreboards()
    check_rev0313_place_public_finance_scoreboards()
    check_rev0314_household_market_extraction_scoreboards()
    check_rev0315_score_mediated_exclusion_scoreboards()
    check_rev0316_fresh_start_scoreboards()
    check_rev0317_intergenerational_transfer_scoreboards()
    check_rev0318_public_balance_sheet_scoreboards()
    check_rev0320_backstop_scoreboards()
    check_rev0321_remedy_scoreboards()
    check_rev0322_rental_market_power_scoreboards()
    check_rev0323_currentness_dynastic_scoreboards()
    check_rev0326_gate20_burndown()
    check_rev0327_backstop_status_parity()
    check_rev0328_federal_claim_security_burndown()
    check_rev0329_sovereign_public_fiscal_burndown()
    check_rev0330_score_mediated_exclusion_burndown()
    check_rev0331_gate18_gate19_backlog_closure()
    check_no_active_memo_seed_scoreboard_mismatch()
    check_rev0332_seed_backlog_closure()
    check_rev0333_workplace_power_current_law_hardening()
    check_rev0334_household_market_extraction_hardening()
    check_rev0335_place_public_finance_hardening()
    check_rev0336_jurisdictional_mobility_hardening()
    check_rev0337_seedclass_backlog_closure()
    check_rev0338_evidence_debt_source_anchor_refactor()
    check_rev0339_currentness_coverage_and_validator_callchain()
    check_rev0340_memo_citation_lineage_and_alias_canonicalization()
    check_rev0341_case_memo_status_language_repair()
    check_rev0342_case_identity_lineage_canonicalization()
    check_rev0343_live_doc_source_alias_canonicalization()
    check_rev0344_unused_source_burndown_and_validator_callchain()
    check_rev0345_frontdoor_reality_audit_and_changelog_repair()
    check_rev0346_volatile_currentness_and_sourcefit_refactor()
    check_rev0347_dfa_share_extraction_and_gridload_incidence()
    check_rev0348_large_load_tariff_incidence_and_proofdebt_closeout()
    check_rev0349_project_level_water_ratepayer_incidence_and_proofdebt_refactor()
    check_rev0350_louisiana_meta_esa_financing_risk_and_countsurface_repair()
    check_rev0351_written_order_phase2_expansion_and_la_large_load_router_refactor()
    check_rev0352_large_load_guidelines_and_evest_redaction_risk()
    check_rev0353_resource_adequacy_riverbend_water_and_router_refactor()
    check_rev0354_riverbend_indenture_pilot_rebate_and_local_incidence_refactor()
    check_rev0355_riverbend_pilot_distribution_and_public_instrument_ladder()
    check_rev0356_mission_heart_evidence_integrity_audit()
    check_rev0357_substantive_risk_claim_migration_sprint()
    check_rev0358_claim_edge_pilot_and_validator_refactor()
    check_rev0359_project_instrument_edges_and_source_role_refactor()
    check_rev0360_pilot_advance_public_record_and_schema_retirement_cutover()
    check_rev0361_dual_claim_migration_us_dfa_and_ratepayer_risk_refactor()
    check_rev0362_boi_transfer_tax_current_law_and_source_edge_refactor()
    check_rev0363_stablecoin_law_waterfall_and_backstop_refactor()
    check_rev0364_stablecoin_reporting_forms_and_currentness_watch_refactor()
    check_rev0365_private_credit_formpf_counterparty_and_redemption_risk_refactor()
    check_rev0366_treasury_basis_repo_clearing_and_public_upside_refactor()
    check_rev0367_residual_insurance_nfip_fairplan_assessment_and_mortgage_stress_refactor()
    check_rev0368_public_pension_private_markets_fees_and_liquidity_refactor()
    check_rev0369_tax_expenditure_claimant_incidence_and_current_law_refactor()
    check_rev0370_medicare_advantage_denial_payment_integrity_refactor()
    check_rev0372_ma_contract_level_claim_security_and_validator_pruning_sprint()
    check_rev0373_ma_row_contract_remedy_appeal_and_quality_workbench()
    check_rev0374_ma_appeal_burden_public_pilot_and_validator_refactor()
    check_rev0375_ma_contractor_resident_harm_and_enforcement_bridge()
    check_rev0376_ma_equity_disaggregation_and_beneficiary_experience_join()
    check_rev0377_ma_medical_necessity_criteria_and_clinical_remedy_guardrails()
    check_rev0378_ma_access_availability_ghost_network_and_denied_claim_visibility_bridge()
    check_rev0379_ma_payment_integrity_rebate_value_risk_coding_public_cost_waterfall()
    check_rev0380_ma_encounter_benefit_use_minimum_certifying_row_lock()
    check_rev0381_ma_steering_lock_in_broker_incentive_exit_rights_bridge()
    check_manifest()
    for w in warnings:
        print("WARN:", w)
    if errors:
        for e in errors:
            print("ERROR:", e)
        print(f"FAILED: {len(errors)} errors, {len(warnings)} warnings")
        sys.exit(1)
    print(f"PASSED: 0 errors, {len(warnings)} warnings")

if __name__ == "__main__":
    main()
