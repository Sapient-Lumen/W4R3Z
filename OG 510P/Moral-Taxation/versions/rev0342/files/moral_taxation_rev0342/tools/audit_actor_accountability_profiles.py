#!/usr/bin/env python3
import json, pathlib, sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors = []
version = (root / "VERSION").read_text(encoding="utf-8").strip()

cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
schema = json.loads((root / "docs/00-meta/actor-accountability-schema.json").read_text(encoding="utf-8"))
profiles_doc = json.loads((root / "docs/00-meta/actor-accountability-profiles.json").read_text(encoding="utf-8"))

if schema.get("revision") != version:
    errors.append("actor-accountability-schema.json revision must match VERSION")
if profiles_doc.get("revision") != version:
    errors.append("actor-accountability-profiles.json revision must match VERSION")
if profiles_doc.get("case_count") != len(profiles_doc.get("profiles", [])):
    errors.append("actor-accountability-profiles.json case_count must match profiles length")

route_by_id = {rec["id"]: rec for rec in cube.get("route_records", [])}
required = set(schema.get("required_profile_fields", []))
profile_by_id = {}

private_channels = {"private_mandatory_rail", "bank_required", "tax_software", "digital_only", "vendor_mediated", "platform_account"}
penalty_instruments = {"penalty", "fine", "preparer_penalty", "forfeiture"}

for prof in profiles_doc.get("profiles", []):
    rid = prof.get("route_id")
    if rid in profile_by_id:
        errors.append(f"duplicate actor-accountability profile for route {rid}")
    profile_by_id[rid] = prof
    missing = sorted(required - set(prof))
    if missing:
        errors.append(f"actor-accountability profile {rid} missing fields {missing}")
    rec = route_by_id.get(rid)
    if not rec:
        errors.append(f"actor-accountability profile {rid} has no cube route record")
        continue
    if prof.get("family") != rec.get("family"):
        errors.append(f"actor-accountability profile {rid} family does not match cube record")
    if set(prof.get("source_currentness_refs", [])) != set(rec.get("source_currentness_refs", [])):
        errors.append(f"actor-accountability profile {rid} source_currentness_refs must mirror cube record")
    for field in ["secondary_accountable_actors", "burden_bearers", "bottleneck_or_channel_actor", "responsibility_basis", "non_responsible_actors", "evidence_required", "review_trigger"]:
        if not isinstance(prof.get(field), list) or not prof.get(field):
            errors.append(f"actor-accountability profile {rid} needs non-empty list field {field}")

    generic_beneficiary_markers = {"beneficiary_or_rent_recipient_to_trace", "named_beneficiary_or_rent_recipient", "rent_recipient_or_backstop_beneficiary"}
    if prof.get("beneficiary_or_rent_recipient") in generic_beneficiary_markers:
        errors.append(f"actor-accountability profile {rid} must name a concrete beneficiary/rent recipient after rev0301")
    if "benefit_or_rent_trace" in prof.get("evidence_required", []):
        errors.append(f"actor-accountability profile {rid} must replace generic benefit_or_rent_trace after rev0301")
    if "new_calibration_file" in prof.get("review_trigger", []):
        errors.append(f"actor-accountability profile {rid} must replace profile-level new_calibration_file review trigger after rev0308")

    if len(prof.get("evidence_required", [])) < 3:
        errors.append(f"actor-accountability profile {rid} must require at least three evidence types")
    if "title" not in prof.get("anti_misattribution_rule", "") and "proximity" not in prof.get("anti_misattribution_rule", ""):
        errors.append(f"actor-accountability profile {rid} anti_misattribution_rule must block title/proximity shortcuts")
    axes = rec.get("axes", {})
    channel = set(axes.get("delivery_channel", []))
    incidence = set(axes.get("incidence", []))
    floor = set(axes.get("floor_risk", []))
    if (channel & private_channels or "protected_floor" in incidence or floor & {"low_income_taxpayer", "public_service_access", "bankless"}) and "fallback" not in prof.get("fallback_public_duty", ""):
        errors.append(f"actor-accountability profile {rid} must name fallback public duty for private/floor channel")
    instr = set(axes.get("instrument", []))
    if instr & penalty_instruments:
        txt = " ".join(prof.get("responsibility_basis", []) + prof.get("evidence_required", []))
        for word in ["control", "notice"]:
            if word not in txt:
                errors.append(f"actor-accountability penalty-like profile {rid} must require {word} evidence")

    if prof.get("family") == "tax_administration_access":
        if prof.get("beneficiary_or_rent_recipient") == "beneficiary_or_rent_recipient_to_trace":
            errors.append(f"tax-administration actor profile {rid} must name the concrete beneficiary/rent recipient, not the placeholder")
        if "benefit_or_rent_trace" in prof.get("evidence_required", []):
            errors.append(f"tax-administration actor profile {rid} must replace generic benefit_or_rent_trace with route-specific evidence")
        if len(prof.get("responsibility_basis", [])) < 2:
            errors.append(f"tax-administration actor profile {rid} needs at least two route-specific responsibility bases")
        if "fallback" not in prof.get("fallback_public_duty", ""):
            errors.append(f"tax-administration actor profile {rid} must preserve a public fallback duty")

    if prof.get("family") == "controller_ai":
        if prof.get("beneficiary_or_rent_recipient") == "beneficiary_or_rent_recipient_to_trace":
            errors.append(f"controller-AI actor profile {rid} must name the concrete beneficiary/rent recipient, not the placeholder")
        if "benefit_or_rent_trace" in prof.get("evidence_required", []):
            errors.append(f"controller-AI actor profile {rid} must replace generic benefit_or_rent_trace with route-specific evidence")
        if len(prof.get("responsibility_basis", [])) < 2:
            errors.append(f"controller-AI actor profile {rid} needs at least two route-specific responsibility bases")
        joined = " ".join(str(x) for x in (prof.get("responsibility_basis", []) + prof.get("evidence_required", []) + prof.get("review_trigger", [])))
        if rid.startswith("controller_map_") and "controller_map" not in joined:
            errors.append(f"controller-map actor profile {rid} must require controller_map-specific evidence or responsibility")
        if rid.startswith("model_assisted"):
            for word in ["model", "review", "notice"]:
                if word not in joined:
                    errors.append(f"model-assisted actor profile {rid} must require {word} accountability evidence")
        if rid == "taxpayer_side_ai_preparer_agent_reliance_and_liability":
            for word in ["preparer", "refund", "notice", "control"]:
                if word not in joined:
                    errors.append(f"taxpayer-side AI actor profile must require {word} accountability evidence")
            if "fallback" not in prof.get("fallback_public_duty", ""):
                errors.append("taxpayer-side AI actor profile must preserve a public fallback duty")


    if prof.get("family") == "public_finance_core":
        if prof.get("beneficiary_or_rent_recipient") in {"beneficiary_or_rent_recipient_to_trace", "named_beneficiary_or_rent_recipient"}:
            errors.append(f"public-finance-core actor profile {rid} must name the concrete beneficiary/rent recipient, not a placeholder")
        if "benefit_or_rent_trace" in prof.get("evidence_required", []):
            errors.append(f"public-finance-core actor profile {rid} must replace generic benefit_or_rent_trace with route-specific evidence")
        if "no_distinct_bottleneck_identified" in prof.get("bottleneck_or_channel_actor", []):
            errors.append(f"public-finance-core actor profile {rid} must identify the real bottleneck, channel, model, or legal gate")
        if len(prof.get("responsibility_basis", [])) < 2:
            errors.append(f"public-finance-core actor profile {rid} needs at least two route-specific responsibility bases")
        joined = " ".join(str(x) for x in (prof.get("responsibility_basis", []) + prof.get("evidence_required", []) + prof.get("review_trigger", [])))
        if rid == "instrument_choice_tax_fee_mandate_ban_public_option_compensation":
            for word in ["instrument", "category", "incidence", "benefit"]:
                if word not in joined:
                    errors.append(f"instrument-choice actor profile must require {word} accountability evidence")
        if rid == "incidence_evidence_and_protected_burden":
            for word in ["incidence", "pass", "protected", "repair"]:
                if word not in joined:
                    errors.append(f"incidence-evidence actor profile must require {word} accountability evidence")
        if rid == "proceeds_visibility_local_share_and_earmarking":
            for word in ["proceeds", "local", "repair", "ledger"]:
                if word not in joined:
                    errors.append(f"proceeds-visibility actor profile must require {word} accountability evidence")



    if prof.get("family") == "legal_enforcement_penalty":
        if prof.get("beneficiary_or_rent_recipient") == "beneficiary_or_rent_recipient_to_trace":
            errors.append(f"legal-enforcement actor profile {rid} must name the concrete beneficiary/rent recipient, not the placeholder")
        if "benefit_or_rent_trace" in prof.get("evidence_required", []):
            errors.append(f"legal-enforcement actor profile {rid} must replace generic benefit_or_rent_trace with route-specific evidence")
        if len(prof.get("responsibility_basis", [])) < 2:
            errors.append(f"legal-enforcement actor profile {rid} needs at least two route-specific responsibility bases")
        if prof.get("bottleneck_or_channel_actor") == ["public_channel_owner"]:
            errors.append(f"legal-enforcement actor profile {rid} must name the coercive bottleneck, record channel, property channel, or contest channel")
        joined = " ".join(str(x) for x in (prof.get("responsibility_basis", []) + prof.get("evidence_required", []) + prof.get("review_trigger", []) + prof.get("bottleneck_or_channel_actor", [])))
        for word in ["notice", "record"]:
            if word not in joined:
                errors.append(f"legal-enforcement actor profile {rid} must require {word} accountability evidence")
        if rid == "community_supervision_private_probation_monitoring_fees":
            for word in ["ability", "willfulness", "vendor", "revocation"]:
                if word not in joined:
                    errors.append(f"community-supervision actor profile must require {word} evidence")
        if rid == "civil_asset_forfeiture_equitable_sharing_owner_remedy":
            for word in ["owner", "proceeds", "forfeiture", "return"]:
                if word not in joined:
                    errors.append(f"civil-asset-forfeiture actor profile must require {word} evidence")
        if rid == "summons_third_party_contact_john_doe_and_privilege":
            for word in ["third_party", "privilege", "scope", "notice"]:
                if word not in joined:
                    errors.append(f"summons/third-party-contact actor profile must require {word} evidence")
        if rid == "trust_fund_recovery_responsible_person_and_willfulness":
            for word in ["responsible", "willfulness", "Form_4180", "Letter_1153"]:
                if word not in joined:
                    errors.append(f"trust-fund-recovery actor profile must require {word} evidence")
        if "fallback" not in prof.get("fallback_public_duty", ""):
            errors.append(f"legal-enforcement actor profile {rid} must preserve a public fallback duty")


    if prof.get("family") == "labor_care_benefits":
        if prof.get("beneficiary_or_rent_recipient") == "beneficiary_or_rent_recipient_to_trace":
            errors.append(f"labor-care-benefits actor profile {rid} must name the concrete beneficiary/rent recipient, not the placeholder")
        if "benefit_or_rent_trace" in prof.get("evidence_required", []):
            errors.append(f"labor-care-benefits actor profile {rid} must replace generic benefit_or_rent_trace with route-specific evidence")
        if prof.get("bottleneck_or_channel_actor") in (["public_channel_owner"], ["channel_or_bottleneck_operator"]):
            errors.append(f"labor-care-benefits actor profile {rid} must name the real labor, care, credential, data, pension, or benefit bottleneck")
        if len(prof.get("responsibility_basis", [])) < 2:
            errors.append(f"labor-care-benefits actor profile {rid} needs at least two route-specific responsibility bases")
        joined = " ".join(str(x) for x in (prof.get("responsibility_basis", []) + prof.get("evidence_required", []) + prof.get("review_trigger", []) + prof.get("bottleneck_or_channel_actor", [])))
        route_terms = {
            "labor_tax_wedge_classification_social_insurance": ["classification", "wage", "contribution"],
            "education_finance_student_debt_credential_rent": ["credential", "loan", "outcome"],
            "care_economy_second_earner_household_floor": ["care", "second_earner", "benefit"],
            "retirement_tax_preference_pension_adequacy_leakage": ["retirement", "fee", "account"],
            "child_family_benefit_childcare_fertility_support": ["child", "provider", "takeup"],
            "long_term_care_aging_disability_caregiver_finance": ["care", "asset", "provider"],
            "platform_worker_portable_benefits_classification_fringe": ["platform", "classification", "benefit"],
            "assessment_unit_and_care_load": ["household", "care", "notice"],
            "data_minimization_credential_reuse_and_sensitive_attribute_firewall": ["data", "credential", "sensitive"],
            "pension_pass_through_incidence_and_proceeds": ["pension", "pass", "proceeds"],
            "worker_benefit_pay_hours_member_share_and_local_repair": ["pay", "hours", "local"],
        }
        for word in route_terms.get(rid, []):
            if word not in joined:
                errors.append(f"labor-care-benefits actor profile {rid} must require {word} accountability evidence")
        if any(token in rid for token in ["care", "child", "assessment", "data_minimization", "platform_worker", "labor_tax_wedge"]) and "fallback" not in prof.get("fallback_public_duty", ""):
            errors.append(f"labor-care-benefits actor profile {rid} must preserve a public fallback duty for care, data, worker, or floor-access channels")



    if prof.get("family") == "environment_climate_commons":
        if prof.get("beneficiary_or_rent_recipient") == "beneficiary_or_rent_recipient_to_trace":
            errors.append(f"environment-climate-commons actor profile {rid} must name the concrete beneficiary/rent recipient, not the placeholder")
        if "benefit_or_rent_trace" in prof.get("evidence_required", []):
            errors.append(f"environment-climate-commons actor profile {rid} must replace generic benefit_or_rent_trace with route-specific evidence")
        if prof.get("bottleneck_or_channel_actor") in (["public_channel_owner"], ["channel_or_bottleneck_operator"], ["no_distinct_bottleneck_identified"]):
            errors.append(f"environment-climate-commons actor profile {rid} must name the real permit, utility, registry, bond, insurance, toll, offset, or prefunding bottleneck")
        if len(prof.get("responsibility_basis", [])) < 2:
            errors.append(f"environment-climate-commons actor profile {rid} needs at least two route-specific responsibility bases")
        if "fallback" not in prof.get("fallback_public_duty", ""):
            errors.append(f"environment-climate-commons actor profile {rid} must preserve a public fallback, repair, or no-go duty")
        joined = " ".join(str(x) for x in (prof.get("responsibility_basis", []) + prof.get("evidence_required", []) + prof.get("review_trigger", []) + prof.get("bottleneck_or_channel_actor", []))).lower()
        route_terms = {
            "data_center_local_burden": ["load", "water", "ratepayer"],
            "ecological_resource_biodiversity_material_footprint": ["reclamation", "biodiversity", "offset"],
            "disaster_insurance_climate_backstop": ["hazard", "premium", "relocation"],
            "water_rights_scarcity_pricing_irrigation_subsidy": ["basin", "lifeline", "right"],
            "transport_congestion_road_pricing_mobility_access": ["toll", "transit", "location"],
            "ocean_fisheries_subsidies_marine_commons_blue_food": ["stock", "iuu", "subsidy"],
            "critical_minerals_extraction_processing_stockpile_recycling": ["criticality", "reclamation", "stockpile"],
            "hard_to_abate_transport_aviation_shipping_offset_integrity": ["offset", "fuel", "port"],
            "cumulative_burden_environmental_justice_siting_tax": ["cumulative", "siting", "monitoring"],
            "failure_waterfall_and_ex_ante_security": ["bond", "reserve", "insolvency"],
        }
        for word in route_terms.get(rid, []):
            if word not in joined:
                errors.append(f"environment-climate-commons actor profile {rid} must require {word} accountability evidence")



    if prof.get("family") == "social_floor_public_services":
        if prof.get("beneficiary_or_rent_recipient") == "beneficiary_or_rent_recipient_to_trace":
            errors.append(f"social-floor-public-services actor profile {rid} must name the concrete beneficiary/rent recipient, not the placeholder")
        if "benefit_or_rent_trace" in prof.get("evidence_required", []):
            errors.append(f"social-floor-public-services actor profile {rid} must replace generic benefit_or_rent_trace with route-specific evidence")
        if prof.get("bottleneck_or_channel_actor") in (["public_channel_owner"], ["channel_or_bottleneck_operator"], ["no_distinct_bottleneck_identified"]):
            errors.append(f"social-floor-public-services actor profile {rid} must name the real fee, exemption, service, benefit, bond, consultation, transfer, or member-relief bottleneck")
        if len(prof.get("responsibility_basis", [])) < 2:
            errors.append(f"social-floor-public-services actor profile {rid} needs at least two route-specific responsibility bases")
        if "fallback" not in prof.get("fallback_public_duty", ""):
            errors.append(f"social-floor-public-services actor profile {rid} must preserve a public fallback, access, repair, or non-substitution duty")
        joined = " ".join(str(x) for x in (prof.get("responsibility_basis", []) + prof.get("evidence_required", []) + prof.get("review_trigger", []) + prof.get("bottleneck_or_channel_actor", []))).lower()
        route_terms = {
            "health_addiction_harmful_consumption_tax": ["addiction", "treatment", "targeting"],
            "nonprofit_exemption_public_benefit": ["exemption", "community", "donor"],
            "user_fee_service_charge_utility_public_access_toll": ["fee", "disconnection", "affordability"],
            "agriculture_food_support_nutrition_rural_floor": ["nutrition", "subsidy", "food"],
            "municipal_bond_tax_exemption_public_infrastructure_finance": ["bond", "private", "arbitrage"],
            "tribal_indigenous_fiscal_sovereignty_tax_parity_consultation": ["tribal", "consultation", "parity"],
            "charitable_public_benefit_transfer_and_retained_surplus": ["irrevocable", "retained", "surplus"],
            "public_service_member_relief_and_local_repair": ["service", "member", "local"],
        }
        for word in route_terms.get(rid, []):
            if word not in joined:
                errors.append(f"social-floor-public-services actor profile {rid} must require {word} accountability evidence")


    if prof.get("family") == "cross_border_reporting":
        if prof.get("beneficiary_or_rent_recipient") == "beneficiary_or_rent_recipient_to_trace":
            errors.append(f"cross-border-reporting actor profile {rid} must name the concrete beneficiary/rent recipient, not the placeholder")
        if "benefit_or_rent_trace" in prof.get("evidence_required", []):
            errors.append(f"cross-border-reporting actor profile {rid} must replace generic benefit_or_rent_trace with route-specific evidence")
        if prof.get("bottleneck_or_channel_actor") in (["public_channel_owner"], ["channel_or_bottleneck_operator"], ["no_distinct_bottleneck_identified"]):
            errors.append(f"cross-border-reporting actor profile {rid} must name the real treaty, customs, remittance, immigration, exchange, reclaim, or claim-split bottleneck")
        if len(prof.get("responsibility_basis", [])) < 2:
            errors.append(f"cross-border-reporting actor profile {rid} needs at least two route-specific responsibility bases")
        if "fallback" not in prof.get("fallback_public_duty", ""):
            errors.append(f"cross-border-reporting actor profile {rid} must preserve a public fallback, dispute, capacity, or nonforfeiture duty")
        joined = " ".join(str(x) for x in (prof.get("responsibility_basis", []) + prof.get("evidence_required", []) + prof.get("review_trigger", []) + prof.get("bottleneck_or_channel_actor", []))).lower()
        route_terms = {
            "un_inclusive_international_tax": ["source", "participation", "capacity"],
            "customs_tariff_carbon_border": ["customs", "emissions", "pass"],
            "migration_remittance_transfer_tax_diaspora_family": ["remittance", "kyc", "corridor"],
            "immigration_status_asylum_benefit_fee_floor": ["fee", "waiver", "status"],
            "withholding_treaty_relief_map_double_tax_protection": ["withholding", "treaty", "map"],
            "international_coordination_claim_split": ["gir", "claim", "source"],
        }
        for word in route_terms.get(rid, []):
            if word not in joined:
                errors.append(f"cross-border-reporting actor profile {rid} must require {word} accountability evidence")



    if prof.get("family") == "regulated_networks_platforms":
        if prof.get("bottleneck_or_channel_actor") in (["channel_or_bottleneck_operator"], ["no_distinct_bottleneck_identified"]):
            errors.append(f"regulated-networks actor profile {rid} must name the real spectrum, standards, telecom, or ad-platform bottleneck")
        joined = " ".join(str(x) for x in (prof.get("responsibility_basis", []) + prof.get("evidence_required", []) + prof.get("review_trigger", []) + prof.get("bottleneck_or_channel_actor", []))).lower()
        route_terms = {
            "spectrum_orbital_commons_auction_interference_sustainability": ["spectrum", "interference", "debris"],
            "standards_certification_accreditation_audit_gatekeeping": ["standard", "certification", "accreditation"],
            "telecom_universal_service_broadband_affordability_surcharge": ["contribution", "bill", "affordability"],
            "media_attention_digital_advertising_tax_speech_transparency": ["ad", "speech", "pass"],
        }
        for word in route_terms.get(rid, []):
            if word not in joined:
                errors.append(f"regulated-networks actor profile {rid} must require {word} accountability evidence")

    if prof.get("family") == "release_integrity_currentness":
        if prof.get("bottleneck_or_channel_actor") in (["no_distinct_bottleneck_identified"], ["channel_or_bottleneck_operator"]):
            errors.append(f"release-integrity actor profile {rid} must name the actual registry, manifest, source, or contract bottleneck")
        joined = " ".join(str(x) for x in (prof.get("responsibility_basis", []) + prof.get("evidence_required", []) + prof.get("review_trigger", []) + prof.get("bottleneck_or_channel_actor", []))).lower()
        route_terms = {
            "cube_lifecycle_pruning_route_retirement_evidence_refresh": ["route", "retirement", "source"],
            "source_hierarchy_conflict_refresh_current_law": ["source", "conflict", "currentness"],
            "release_integrity_source_bijection_regression_harness": ["manifest", "source", "regression"],
            "case_contract_route_coverage_answer_regression": ["case", "contract", "answer"],
        }
        for word in route_terms.get(rid, []):
            if word not in joined:
                errors.append(f"release-integrity actor profile {rid} must require {word} accountability evidence")

    if prof.get("family") == "financial_system_risk":
        if prof.get("bottleneck_or_channel_actor") in (["no_distinct_bottleneck_identified"], ["channel_or_bottleneck_operator"]):
            errors.append(f"financial-system-risk actor profile {rid} must name the real backstop, custody, screening, budget, insurance, platform, creditor, or policyholder bottleneck")
        joined = " ".join(str(x) for x in (prof.get("responsibility_basis", []) + prof.get("evidence_required", []) + prof.get("review_trigger", []) + prof.get("bottleneck_or_channel_actor", []))).lower()
        route_terms = {
            "systemic_finance_backstop": ["backstop", "resolution", "clawback"],
            "digital_asset_crypto_reporting_stablecoin": ["basis", "custody", "reserve"],
            "sanctions_aml_cft_derisking_financial_access": ["sanctions", "blocked", "humanitarian"],
            "fiscal_transparency_budget_debt_tax_expenditure_legibility": ["budget", "debt", "expenditure"],
            "insurance_reinsurance_protection_gap_public_backstop": ["reinsurance", "coverage", "backstop"],
            "gambling_prediction_markets_event_contracts_addiction": ["listing", "addiction", "integrity"],
            "creditor_distress_netting_and_retained_surplus": ["creditor", "priority", "surplus"],
            "insurance_policyholder_benefit_and_retained_surplus": ["policyholder", "claim", "surplus"],
        }
        for word in route_terms.get(rid, []):
            if word not in joined:
                errors.append(f"financial-system-risk actor profile {rid} must require {word} accountability evidence")

    if prof.get("family") == "wealth_property_rent":
        if prof.get("bottleneck_or_channel_actor") in (["no_distinct_bottleneck_identified"], ["channel_or_bottleneck_operator"]):
            errors.append(f"wealth-property-rent actor profile {rid} must name the real property, transfer, public asset, wealth register, site rent, or indexation bottleneck")
        joined = " ".join(str(x) for x in (prof.get("responsibility_basis", []) + prof.get("evidence_required", []) + prof.get("review_trigger", []) + prof.get("bottleneck_or_channel_actor", []))).lower()
        route_terms = {
            "land_housing_location_rent": ["site", "zoning", "housing"],
            "wealth_transfer_dynastic_concentration_liquidity": ["trust", "valuation", "liquidity"],
            "public_wealth_sovereign_fund_soe_social_dividend_governance": ["asset", "fund", "dividend"],
            "annual_wealth_backstop_visibility_grouping_and_liquidity": ["wealth", "grouping", "liquidity"],
            "land_site_rent_netting_and_retained_surplus": ["site", "netting", "surplus"],
            "real_value_indexation_and_reset_cadence": ["index", "reset", "hardship"],
        }
        for word in route_terms.get(rid, []):
            if word not in joined:
                errors.append(f"wealth-property-rent actor profile {rid} must require {word} accountability evidence")

    if prof.get("family") == "public_procurement_industrial_policy":
        if prof.get("bottleneck_or_channel_actor") in (["channel_or_bottleneck_operator"], ["no_distinct_bottleneck_identified"]):
            errors.append(f"public-procurement actor profile {rid} must name the real contract, relief, stockpile, patent, or classified procurement bottleneck")
        joined = " ".join(str(x) for x in (prof.get("responsibility_basis", []) + prof.get("evidence_required", []) + prof.get("review_trigger", []) + prof.get("bottleneck_or_channel_actor", []))).lower()
        route_terms = {
            "procurement_subsidy_industrial_policy_public_upside": ["contract", "subsidy", "clawback"],
            "emergency_relief_speed_integrity_clawback": ["identity", "overpayment", "safe"],
            "public_health_emergency_stockpiles_procurement_allocation": ["stockpile", "allocation", "expiration"],
            "publicly_funded_research_patents_open_access_march_in": ["patent", "access", "pricing"],
            "defense_security_procurement_secrecy_industrial_base": ["classified", "cost", "test"],
        }
        for word in route_terms.get(rid, []):
            if word not in joined:
                errors.append(f"public-procurement actor profile {rid} must require {word} accountability evidence")

    if rid == "actor_accountability_responsibility_chain" and prof.get("primary_accountable_actor") != "actor_with_power_duty_benefit_or_fallback_responsibility":
        errors.append("actor accountability route must name the responsibility-chain primary actor")

missing_profiles = sorted(set(route_by_id) - set(profile_by_id))
extra_profiles = sorted(set(profile_by_id) - set(route_by_id))
if missing_profiles:
    errors.append(f"missing actor-accountability profiles for cube route records: {missing_profiles}")
if extra_profiles:
    errors.append(f"extra actor-accountability profiles without cube records: {extra_profiles}")

summary = cube.get("audit_summary", {})
if summary.get("actor_accountability_profiles_required") is not True:
    errors.append("cube audit_summary must mark actor_accountability_profiles_required=True")
if summary.get("actor_accountability_profile_count") != len(route_by_id):
    errors.append("cube audit_summary actor_accountability_profile_count is stale")
counts = {}
for p in profiles_doc.get("profiles", []):
    counts[p.get("primary_accountable_actor")] = counts.get(p.get("primary_accountable_actor"), 0) + 1
if summary.get("actor_accountability_primary_actor_counts") != {k: counts[k] for k in sorted(counts)}:
    errors.append("cube audit_summary actor_accountability_primary_actor_counts is stale")
report_rel = cube.get("actor_accountability_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json actor_accountability_audit_report_path must point to an existing report")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    if f"Actor-accountability profiles: {len(route_by_id)}" not in report:
        errors.append("actor-accountability audit report is stale")

if errors:
    raise SystemExit("\n".join(errors))
print("actor-accountability profile audit ok")
