#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from test_matrix_registry import COMMON_TEST_MATRICES
from archive_meta import GENERATED, METADATA_DIR, ROOT, current_notes_from_index, current_revision, generated_at_utc

CURRENT_REV = current_revision()


def load_metadata() -> dict:
    path = METADATA_DIR / "note_metadata.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    metadata = load_metadata()
    index_path = GENERATED / "ARCHIVE_INDEX.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {"notes": []}
    by_file = {entry["file"]: entry for entry in index.get("notes", [])}
    notes: dict[str, dict] = {}
    status_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()

    for file, meta in sorted(metadata.get("notes", {}).items(), key=lambda item: item[1].get("number", 0)):
        idx = by_file.get(file, {})
        number = meta.get("number") or idx.get("number")
        status = meta.get("status", "active")
        note_class = meta.get("note_class", "archive_note")
        status_counts[status] += 1
        class_counts[note_class] += 1
        notes[file] = {
            "number": number,
            "title": idx.get("title"),
            "status": status,
            "note_class": note_class,
            "canon_role": meta.get("canon_role", "supporting_pattern"),
            "first_citation": bool(meta.get("first_citation", False)),
            "dispatcher": meta.get("dispatcher"),
            "depends_on": meta.get("depends_on", []),
            "reserved_notes": meta.get("reserved_notes", []),
            "source_keys": meta.get("source_keys", []),
            "tags": meta.get("tags", idx.get("tags", [])),
        }

    front_door = {
        "pocket_answer": "archive/841-scope-answer-cards-for-ideal-governments-of-each-scope-steward-cells-municipal-full-kits-connector-backbones-metro-authorities-regional-platforms-national-guarantors-and-global-narrow-waists.md",
        "long_answer": "archive/790-ideal-governments-of-each-scope-answer-key-micro-local-voice-municipal-full-kit-metropolitan-democracy-regional-platforms-national-guarantees-continental-compacts-and-global-narrow-waists.md",
        "operating_canon": "archive/843-reconstructed-operating-canon-for-radical-governance-scope-doctrine-opposition-briefs-case-packets-source-waists-deletion-rules-and-no-thesis-echo.md",
        "cross_boundary_dispatcher": "archive/848-cross-boundary-form-dispatcher-for-radical-governance-trigger-first-ladder-second-chain-only-as-needed-one-holding-per-case-and-no-institutional-form-by-spillover-drama.md",
        "applied_thick_case": "archive/849-applied-cross-boundary-case-packet-for-london-metropolitan-transport-authority-bounded-functional-authority-mayoral-shell-fiscal-risk-scrutiny-paths-and-no-transit-government-by-board-alone.md",
        "applied_thin_case": "archive/850-applied-cross-boundary-case-packet-for-intermunicipal-shared-service-consortium-thin-backbone-municipal-ownership-service-level-compact-fiscal-queue-and-no-county-government-by-admin-hub.md",
        "applied_middle_case": "archive/851-applied-cross-boundary-case-packet-for-river-basin-flood-risk-platform-statutory-floor-catchment-board-local-duty-and-no-watershed-government-by-hydrology-alone.md",
        "applied_asset_case": "archive/852-applied-cross-boundary-case-packet-for-regional-water-wastewater-utility-authority-asset-liability-ledger-community-assessments-ratepayer-route-and-no-utility-government-by-bond-covenant.md",
        "applied_contract_case": "archive/853-applied-cross-boundary-case-packet-for-binational-bridge-p3-delivery-authority-contract-change-control-toll-oversight-handback-and-no-border-government-by-concession.md",
        "applied_regulatory_case": "archive/854-applied-cross-boundary-case-packet-for-regional-port-state-control-inspection-regime-risk-based-inspections-detention-and-banning-route-flag-state-safety-net-and-no-maritime-government-by-shared-badge.md",
        "applied_treaty_global_case": "archive/855-applied-cross-boundary-case-packet-for-international-health-regulations-global-alert-waist-national-focal-points-pheic-and-pandemic-emergency-recommendations-core-capacity-review-and-no-world-health-government-by-outbreak-notice.md",
        "waist_capture_lens": "archive/856-waist-capture-and-chokepoint-governance-standards-databases-inspection-scores-alerts-procurement-rails-and-no-public-power-by-hidden-waist.md",
        "claim_ledger_policy": "archive/857-claim-ledgers-evidence-lanes-source-currentness-and-no-archive-authority-by-unnamed-proof.md",
        "applied_procedural_digital_case": "archive/858-applied-cross-boundary-case-packet-for-interoperable-europe-act-interoperability-assessments-procedural-digital-waist-public-sector-bodies-cross-border-services-and-no-eu-digital-government-by-assessment-form.md",
        "supplier_dependency_lens": "archive/859-cloud-and-model-provider-dependency-in-public-administration-exit-rights-assurance-boundaries-vendor-admin-records-and-no-government-by-infrastructure-dashboard.md",
        "cross_boundary_manual": "archive/860-cross-boundary-authority-manual-dispatcher-fields-defeat-tests-claim-ledgers-and-no-chain-by-recitation.md",
        "negative_control_policy": "archive/861-negative-control-handback-sunset-and-downshift-tests-for-cross-boundary-authority-no-institution-by-success-case-only.md",
        "applied_soft_law_case": "archive/862-applied-fatf-soft-law-waist-recommendations-mutual-evaluations-greylisting-and-no-global-financial-police-by-recommendation.md",
        "applied_database_alert_case": "archive/863-applied-schengen-information-system-alert-database-waist-national-issuer-responsibility-data-rights-and-no-european-police-by-alert.md",
        "plural_order_lens": "archive/864-plural-order-authority-and-indigenous-co-governance-legal-personality-consent-settlement-mandate-relational-jurisdiction-and-no-sovereignty-by-consultation-theater.md",
        "applied_plural_order_case": "archive/865-applied-plural-order-case-packet-for-taranaki-maunga-te-kahui-tupua-legal-person-mountain-iwi-crown-conservation-waist-and-no-park-government-by-ownership-fiction.md",
        "applied_supplier_dependency_case": "archive/866-applied-supplier-dependency-case-packet-for-nhs-federated-data-platform-palantir-led-saas-pet-instances-exit-proof-and-no-health-service-by-data-console.md",
        "supplier_dependency_review_policy": "archive/867-supplier-dependency-review-dockets-admin-privileges-exit-rehearsals-benefit-claims-and-no-contract-confidence-by-assertion.md",
        "municipal_distress_handback_policy": "archive/868-municipal-distress-intervention-and-handback-dockets-waivers-transition-control-local-capacity-and-no-democracy-by-permanent-receivership.md",
        "applied_municipal_handback_case": "archive/869-applied-municipal-handback-case-packet-for-detroit-financial-review-commission-post-bankruptcy-waiver-reactivation-clock-and-no-local-democracy-by-dormant-receivership.md",
        "symbolic_authority_policy": "archive/870-symbolic-authority-and-mandate-capacity-mismatch-dockets-formal-bodies-real-levers-transition-receipts-and-no-accountability-by-mission-statement.md",
        "applied_symbolic_authority_case": "archive/871-applied-symbolic-authority-case-packet-for-lahsa-joint-powers-homelessness-waist-audit-triggered-transition-city-county-split-and-no-homelessness-government-by-grant-administrator.md",
        "capacity_floor_policy": "archive/872-capacity-floor-and-fragile-jurisdiction-implementation-dockets-security-administration-donor-dependence-records-and-no-authority-by-mandate-print.md",
        "applied_fragile_capacity_case": "archive/873-applied-fragile-jurisdiction-case-packet-for-haiti-gang-suppression-force-un-support-office-hnp-capacity-floor-and-no-security-state-by-external-logistics.md",
        "model_decision_policy": "archive/874-model-mediated-public-decisions-and-evidentiary-debt-dockets-proof-hierarchy-burden-notice-review-and-no-public-debt-by-statistical-proxy.md",
        "applied_model_decision_case": "archive/875-applied-model-decision-case-packet-for-robodebt-income-averaging-welfare-debts-appeal-friction-and-no-social-security-debt-by-automated-proxy.md",
        "generative_assistant_policy": "archive/876-generative-public-service-assistants-and-guidance-liability-dockets-source-bounded-answers-reliance-boundaries-and-no-law-by-chatbot.md",
        "applied_generative_assistant_mycity_case": "archive/877-applied-generative-assistant-case-packet-for-nyc-mycity-chatbot-business-guidance-hallucination-beta-withdrawal-and-no-municipal-law-by-chatbot-answer.md",
        "applied_generative_assistant_govuk_chat_case": "archive/878-applied-generative-assistant-case-packet-for-govuk-chat-rag-guidance-assistant-source-links-limited-pilot-and-no-benefit-tax-or-visa-decision-by-summary.md",
        "staff_copilot_policy": "archive/879-staff-facing-ai-copilots-casework-triage-draft-records-and-no-public-action-by-invisible-autocomplete.md",
        "applied_staff_copilot_redbox_case": "archive/880-applied-staff-copilot-case-packet-for-redbox-general-purpose-civil-service-llm-official-sensitive-documents-use-case-gates-and-no-policy-by-prompt.md",
        "applied_staff_copilot_dfe_correspondence_case": "archive/881-applied-staff-copilot-case-packet-for-dfe-correspondence-drafter-rag-standard-lines-human-review-and-no-public-reply-by-autocomplete.md",
        "applied_staff_copilot_ico_ice360_case": "archive/882-applied-staff-copilot-case-packet-for-ico-ice360-case-creation-automation-llm-intake-fields-contact-matching-and-no-regulatory-case-by-parser.md",
        "applied_staff_triage_dwp_whitemail_case": "archive/883-applied-staff-triage-case-packet-for-dwp-whitemail-insights-and-vulnerability-scanner-letter-classification-vulnerability-shortlist-and-no-benefit-decision-by-flag.md",
        "transition_receipt_policy": "archive/884-transition-receipts-and-decommissioning-dockets-rollback-replacement-migration-sunset-and-no-governance-repair-by-disappearance.md",
        "applied_transition_receipt_arrivecan_case": "archive/885-applied-transition-receipt-case-packet-for-arrivecan-emergency-border-app-advance-declaration-conversion-procurement-failures-and-no-modernization-by-survivorship.md",
        "applied_transition_receipt_mycity_case": "archive/886-applied-transition-receipt-case-packet-for-nyc-mycity-chatbot-beta-closure-successor-gates-and-no-public-ai-repair-by-maintenance-page.md",
        "platform_migration_policy": "archive/887-platform-migration-and-reprocurement-dockets-parallel-runs-data-cutover-residual-dependency-and-no-replacement-by-award-notice.md",
        "applied_platform_migration_phoenix_dayforce_case": "archive/888-applied-platform-migration-case-packet-for-canada-phoenix-to-dayforce-payroll-transition-backlog-parallel-runs-data-hub-and-no-pay-repair-by-new-saas.md",
        "applied_platform_migration_evisa_case": "archive/889-applied-platform-migration-case-packet-for-uk-evisa-view-and-prove-digital-status-migration-share-codes-legacy-documents-and-no-right-by-portal-uptime.md",
        "ecological_personhood_policy": "archive/890-ecological-legal-personhood-and-rights-of-nature-implementation-dockets-guardian-spines-remedy-budgets-monitoring-and-no-ecological-repair-by-personhood-declaration.md",
        "applied_ecological_personhood_atrato_case": "archive/891-applied-ecological-personhood-case-packet-for-colombia-atrato-river-biocultural-rights-guardian-commission-illegal-mining-plans-and-no-river-governance-by-court-declaration.md",
        "applied_ecological_personhood_mar_menor_case": "archive/892-applied-ecological-personhood-case-packet-for-spain-mar-menor-legal-person-lagoon-tutoria-constitutional-review-guardian-committees-and-no-lagoon-repair-by-tax-number.md",
        "applied_ecological_personhood_ganga_yamuna_case": "archive/893-applied-ecological-personhood-negative-control-for-ganga-yamuna-stayed-juristic-personhood-guardian-liability-and-no-river-repair-by-impracticable-personhood.md",
        "entitlement_continuity_policy": "archive/894-entitlement-continuity-and-procedural-churn-dockets-renewals-migration-notices-ex-parte-proof-and-no-benefit-loss-by-process-failure.md",
        "applied_entitlement_continuity_medicaid_case": "archive/895-applied-entitlement-continuity-case-packet-for-medicaid-chip-renewals-continuous-enrollment-unwinding-ex-parte-renewals-procedural-disenrollment-and-no-coverage-loss-by-paperwork-failure.md",
        "applied_entitlement_continuity_universal_credit_case": "archive/896-applied-entitlement-continuity-case-packet-for-uk-universal-credit-managed-migration-migration-notices-transitional-protection-legacy-closures-and-no-income-support-by-deadline-letter.md",
        "payment_redress_policy": "archive/897-payment-entitlement-redress-and-refund-dockets-claimant-proof-calculation-payment-tail-dispute-routes-and-no-repair-by-payable-label.md",
        "applied_payment_redress_postoffice_horizon_case": "archive/898-applied-payment-redress-case-packet-for-post-office-horizon-multipath-redress-schemes-family-tail-legal-costs-and-no-scandal-repair-by-total-paid.md",
        "applied_payment_redress_infected_blood_case": "archive/899-applied-payment-redress-case-packet-for-infected-blood-compensation-authority-core-adjusted-routes-support-scheme-transition-community-feedback-and-no-redress-by-offer-count.md",
        "applied_payment_refund_erc_case": "archive/900-applied-payment-refund-case-packet-for-irs-employee-retention-credit-backlog-fraud-screening-disallowance-clock-and-no-tax-relief-by-claim-form-or-indefinite-review.md",
        "credential_access_policy": "archive/901-identity-credential-access-and-delegated-authority-dockets-assurance-levels-recovery-relying-party-boundaries-and-no-public-service-by-login.md",
        "applied_credential_access_logingov_case": "archive/902-applied-credential-access-case-packet-for-logingov-ial2-assurance-repair-federal-identity-provider-standards-reliance-and-no-trust-by-assertion.md",
        "applied_credential_access_irs_idme_case": "archive/903-applied-credential-access-case-packet-for-irs-online-account-idme-tax-records-payments-authorizations-and-no-tax-right-by-private-credential.md",
        "applied_credential_access_onelogin_case": "archive/904-applied-credential-access-case-packet-for-govuk-one-login-central-government-front-door-identity-proofing-incidents-and-no-service-by-single-sign-on.md",
        "representative_access_policy": "archive/905-representative-access-proxy-authority-and-fiduciary-dockets-scope-consent-revocation-payment-control-and-no-public-action-by-password-sharing.md",
        "applied_representative_access_ssa_payee_case": "archive/906-applied-representative-access-case-packet-for-social-security-representative-payee-benefit-management-misuse-restitution-and-no-welfare-by-informal-fiduciary.md",
        "applied_representative_access_uk_appointee_case": "archive/907-applied-representative-access-case-packet-for-uk-benefit-appointees-and-third-party-representatives-capacity-wishes-migration-and-no-support-by-account-holder-alone.md",
        "applied_representative_access_irs_taxpro_case": "archive/908-applied-representative-access-case-packet-for-irs-tax-pro-account-caf-poa-tia-authorizations-scope-revocation-and-no-tax-practice-by-checkbox.md",
        "applied_representative_access_health_appeal_case": "archive/909-applied-representative-access-case-packet-for-marketplace-and-medicare-appeal-representation-scope-health-info-notices-and-no-appeal-right-by-form-friction.md",
        "cloudtainer_source_health_policy": "archive/910-cloudtainer-maintenance-source-health-gap-ledgers-generated-surface-budgets-and-no-datacube-by-self-consistency.md",
        "disaster_assistance_policy": "archive/911-disaster-assistance-survivor-proof-program-fragmentation-appeals-and-recovery-delivery-dockets-no-relief-by-denial-letter.md",
        "applied_disaster_assistance_fema_ia_case": "archive/912-applied-disaster-assistance-case-packet-for-fema-individual-assistance-identity-ownership-occupancy-damage-appeals-sba-sequence-and-no-recovery-by-status-letter.md",
        "unemployment_insurance_integrity_access_policy": "archive/913-unemployment-insurance-integrity-claimant-access-identity-payment-hold-overpayment-waiver-and-no-benefit-by-fraud-flag.md",
        "applied_unemployment_insurance_pandemic_ui_case": "archive/914-applied-unemployment-insurance-case-packet-for-pandemic-ui-pua-identity-proofing-payment-holds-overpayments-waivers-appeals-and-no-integrity-by-payment-block.md",
        "watchlist_border_automation_policy": "archive/915-watchlist-border-law-enforcement-automation-biometric-screening-redress-and-no-enforcement-by-match.md",
        "applied_watchlist_border_us_case": "archive/916-applied-watchlist-and-border-automation-case-packet-for-us-terrorist-screening-dhs-trip-cbp-biometrics-ncic-encounters-and-no-liberty-by-alert.md",
        "public_ai_register_policy": "archive/917-public-ai-register-maintenance-inventory-drift-risk-state-and-no-governance-by-listing.md",
        "applied_public_ai_register_case": "archive/918-applied-public-ai-register-case-packet-for-federal-ai-use-case-inventories-sba-irs-atrs-eu-database-and-no-use-by-inventory-row.md",
        "subnational_ai_policy": "archive/919-subnational-digital-government-and-local-ai-implementation-procurement-benefits-schools-courts-policing-permitting-and-no-accountability-by-local-pilot.md",
        "applied_subnational_ai_case": "archive/920-applied-subnational-ai-case-packet-for-nyc-algorithmic-tools-california-ads-inventory-colorado-ai-act-courts-schools-local-records-and-no-public-service-by-local-pilot.md",
        "global_south_source_policy": "archive/921-non-english-global-south-official-source-governance-language-version-drift-translation-currentness-and-no-rule-by-english-summary.md",
        "applied_global_south_source_case": "archive/922-applied-non-english-global-south-source-case-packet-for-brazil-cadunico-govbr-bolsa-familia-ai-plan-lgpd-india-aadhaar-digilocker-and-no-benefit-by-translated-summary.md",
        "health_benefit_treatment_continuity_policy": "archive/923-health-benefit-and-prescription-drug-coverage-transition-dockets-payer-handoff-formulary-clocks-prior-authorization-and-no-treatment-continuity-by-enrollment-row.md",
        "applied_health_coverage_prescription_transition_case": "archive/924-applied-health-coverage-and-prescription-transition-case-packet-for-medicaid-chip-marketplace-and-medicare-part-d-renewals-seps-formulary-exceptions-and-no-medication-continuity-by-plan-card.md",
        "climate_utility_continuity_policy": "archive/925-utility-shutoff-medical-baseline-and-climate-continuity-dockets-arrears-outage-cooling-electricity-dependent-equipment-and-no-life-safety-by-account-code.md",
        "applied_climate_utility_medical_baseline_case": "archive/926-applied-utility-shutoff-and-medical-baseline-case-packet-for-eia-disconnection-data-liheap-hhs-empower-connecticut-winter-protection-california-psps-and-no-safety-by-medical-certificate.md",
        "housing_continuity_policy": "archive/928-housing-stability-eviction-rental-assistance-tenant-screening-and-possession-continuity-dockets-no-housing-stability-by-portal-status.md",
        "applied_housing_continuity_eviction_case": "archive/929-applied-housing-continuity-case-packet-for-eviction-lab-era-closeout-cfpb-tenant-screening-nyc-right-to-counsel-illinois-cbrap-and-no-stability-by-portal-status.md",
        "software_cyber_continuity_policy": "archive/930-cyber-incident-software-provenance-and-public-service-continuity-dockets-runtime-sbom-supplier-access-recovery-and-no-resilience-by-attestation.md",
        "applied_software_cyber_continuity_case": "archive/931-applied-cyber-software-continuity-case-packet-for-change-healthcare-synnovis-british-library-omb-nist-cisa-and-no-resilience-by-attestation.md",
        "election_continuity_policy": "archive/932-election-administration-continuity-dockets-registration-ballot-mail-accessibility-canvass-audit-certification-and-no-suffrage-by-status-row.md",
        "applied_election_continuity_case": "archive/933-applied-election-continuity-case-packet-for-eac-eavs-cisa-election-security-usps-postmarks-fvap-uocava-ada-accessibility-nyc-calendar-and-no-election-by-certified-total.md",
        "child_welfare_continuity_policy": "archive/934-child-protection-foster-care-placement-and-family-continuity-dockets-safety-permanency-health-education-missing-from-care-and-no-child-safety-by-placement-row.md",
        "applied_child_welfare_continuity_case": "archive/935-applied-child-welfare-continuity-case-packet-for-acf-afcars-ncands-family-first-gao-congregate-care-oig-missing-care-ct-dcf-and-no-safety-by-placement-row.md",
        "custody_reentry_continuity_policy": "archive/936-detention-corrections-health-release-and-reentry-continuity-dockets-booking-custody-medication-deaths-ids-housing-and-no-liberty-by-custody-row.md",
        "applied_custody_reentry_continuity_case": "archive/937-applied-custody-and-reentry-continuity-case-packet-for-bjs-jails-prisons-cms-reentry-1115-dcra-gao-bop-samhsa-moud-fulton-jail-and-no-liberty-by-custody-row.md",
        "long_term_care_continuity_policy": "archive/938-long-term-services-supports-nursing-home-hcbs-aps-guardianship-and-care-continuity-dockets-no-care-by-facility-row.md",
        "applied_long_term_care_continuity_case": "archive/939-applied-long-term-care-continuity-case-packet-for-cms-care-compare-hcbs-qms-namrs-aps-ombudsman-sff-staffing-guardianship-and-no-care-by-facility-row.md",
        "transition_receipt_tests": "generated/TRANSITION_RECEIPT_TESTS.json",
        "platform_migration_tests": "generated/PLATFORM_MIGRATION_TESTS.json",
        "ecological_personhood_tests": "generated/ECOLOGICAL_PERSONHOOD_TESTS.json",
        "entitlement_continuity_tests": "generated/ENTITLEMENT_CONTINUITY_TESTS.json",
        "payment_redress_tests": "generated/PAYMENT_REDRESS_TESTS.json",
        "credential_access_tests": "generated/CREDENTIAL_ACCESS_TESTS.json",
        "representative_access_tests": "generated/REPRESENTATIVE_ACCESS_TESTS.json",
        "disaster_assistance_tests": "generated/DISASTER_ASSISTANCE_TESTS.json",
        "unemployment_insurance_tests": "generated/UNEMPLOYMENT_INSURANCE_TESTS.json",
        "watchlist_border_tests": "generated/WATCHLIST_BORDER_TESTS.json",
        "public_ai_register_tests": "generated/PUBLIC_AI_REGISTER_TESTS.json",
        "subnational_ai_tests": "generated/SUBNATIONAL_AI_TESTS.json",
        "global_south_source_tests": "generated/GLOBAL_SOUTH_SOURCE_TESTS.json",
        "source_health": "generated/SOURCE_HEALTH.json",
        "gap_ledger": "generated/GAP_LEDGER.json",
        "generated_surface_audit": "generated/GENERATED_SURFACE_AUDIT.json",
        "symbolic_authority_tests": "generated/SYMBOLIC_AUTHORITY_TESTS.json",
        "capacity_tests": "generated/CAPACITY_TESTS.json",
        "model_decision_tests": "generated/MODEL_DECISION_TESTS.json",
        "generative_assistant_tests": "generated/GENERATIVE_ASSISTANT_TESTS.json",
        "staff_copilot_tests": "generated/STAFF_COPILOT_TESTS.json",
        "handback_tests": "generated/HANDBACK_TESTS.json",
        "supplier_dependency_tests": "generated/SUPPLIER_DEPENDENCY_TESTS.json",
        "case_packet_matrix": "generated/CASE_PACKET_MATRIX.json",
        "retirement_candidates": "generated/RETIREMENT_CANDIDATES.json",
        "claim_ledger": "generated/CLAIMS.json",
        "defeat_tests": "generated/DEFEAT_TESTS.json",
        "cross_boundary_consolidation_audit": "generated/CROSS_BOUNDARY_CONSOLIDATION_AUDIT.json",
    }

    for spec in COMMON_TEST_MATRICES:
        front_door.setdefault(spec["front_door_key"], f"generated/{spec['output_stem']}.json")

    # metadata-driven current canon roles: new substantive packets no longer need
    # a hand-written front-door entry merely to be routable in the current revision.
    # Static aliases above remain for legacy vocabulary and stable reader links.
    for current_file in current_notes_from_index():
        role = notes.get(current_file, {}).get("canon_role")
        if isinstance(role, str) and role.strip() and role != "supporting_pattern":
            front_door[role] = current_file

    payload = {
        "revision": CURRENT_REV,
        "generated_at_utc": generated_at_utc(),
        "metadata_source": "metadata/note_metadata.json",
        "front_door": front_door,
        "status_labels": metadata.get("status_labels", {}),
        "status_counts": dict(sorted(status_counts.items())),
        "class_counts": dict(sorted(class_counts.items())),
        "notes": notes,
    }
    (GENERATED / "NOTE_STATUS.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("OK: wrote generated/NOTE_STATUS.json")


if __name__ == "__main__":
    main()
