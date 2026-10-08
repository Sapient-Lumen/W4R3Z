# Evidence receipts pilot

Generated for `rev0799` from `metadata/evidence_receipts.json`.

This surface records what a source can prove, what proof floor it reaches, and which live gaps it blocks. It deliberately does not store private records or claim field validation.

## Closure policy

No receipt below field-validated person or household outcome proof can close a live gap; aggregate feedback, observation, counsel, filing, or report surfaces must remain blockers unless they join to completed person/household outcomes.

## Proof-floor counts

| Proof floor | Count |
| --- | ---: |
| `aggregate_claimant_feedback_or_observation` | 1 |
| `aggregate_household_outcome_surface` | 1 |
| `dataset_or_docket_boundary` | 1 |
| `official_policy_or_guidance` | 2 |
| `partial_oversight_or_outcome_surface` | 3 |
| `program_playbook_or_report` | 3 |

## Material-outcome dimension counts

| Dimension | Count |
| --- | ---: |
| `appeal_or_waiver_outcome` | 1 |
| `application_completion` | 3 |
| `claimant_feedback` | 1 |
| `counsel_access` | 2 |
| `debt_after_waiver` | 1 |
| `direct_feedback` | 1 |
| `displacement` | 1 |
| `durable_stability` | 4 |
| `filing_exposure` | 1 |
| `housing_possession` | 3 |
| `identity_proofing` | 1 |
| `informal_eviction_denominator` | 1 |
| `issue_resolution` | 1 |
| `lease_access` | 1 |
| `money_or_debt_after_cure` | 1 |
| `non_user_denominator` | 1 |
| `notice_understanding` | 1 |
| `overpayment_debt` | 1 |
| `payment_after_cure` | 2 |
| `payment_or_debt_after_cure` | 1 |
| `physical_displacement` | 2 |
| `rental_assistance` | 1 |
| `representation_denominator` | 1 |
| `shelter_or_rehousing` | 2 |
| `stable_housing` | 1 |
| `staff_assistance` | 2 |
| `subgroup_burden` | 1 |
| `tenant_screening` | 1 |
| `time_burden` | 4 |
| `waiver` | 1 |

## Source-receipt levels

| Level | Count |
| --- | ---: |
| `public_page_heading_and_line_locator_no_private_records` | 1 |
| `public_report_page_or_section_locator_no_private_records` | 1 |
| `source_key_plus_section_locator_no_passage_snapshot` | 9 |

## Closure blockers

| Gap | Blocking receipts |
| --- | --- |
| `GAP-029-affected-person-outcome-validation` | `ER-AP-001`, `ER-HC-001`, `ER-HC-002`, `ER-HC-003`, `ER-HC-004`, `ER-HC-005`, `ER-UI-001`, `ER-UI-002`, `ER-UI-003`, `ER-UI-004`, `ER-UI-005` |
| `GAP-031-source-evidence-preservation-and-claim-capture` | `ER-AP-001`, `ER-HC-001`, `ER-HC-002`, `ER-HC-003`, `ER-HC-004`, `ER-HC-005`, `ER-UI-001`, `ER-UI-002`, `ER-UI-003`, `ER-UI-004`, `ER-UI-005` |
| `GAP-033-power-distribution-and-material-outcome-theory` | `ER-HC-001`, `ER-HC-002`, `ER-HC-003`, `ER-HC-004`, `ER-HC-005`, `ER-UI-001`, `ER-UI-002`, `ER-UI-003`, `ER-UI-004`, `ER-UI-005` |

## Receipts

| Receipt | Case family | Proof floor | Can close gap? | Claim | Remaining affected-person gap |
| --- | --- | --- | --- | --- | --- |
| `ER-AP-001` | `cross_public_benefits_affected_person_burden` | `official_policy_or_guidance` | `False` | Public-benefit access proof must include beginning-to-end burden and direct feedback, not only form or portal completion. | No direct claimant, applicant, or non-user outcome evidence has been collected in this cube row. |
| `ER-HC-001` | `housing_eviction_data_limits` | `dataset_or_docket_boundary` | `False` | Eviction filing data are exposure evidence, not physical eviction, informal eviction, shelter, or re-housing proof. | No household follow-up connects filing, judgment, lockout, informal move-out, shelter, or re-housing outcome. |
| `ER-HC-002` | `housing_right_to_counsel_implementation` | `partial_oversight_or_outcome_surface` | `False` | Right-to-counsel evidence must distinguish legal entitlement, representation rate, counsel at the operative event, and stable housing result. | No household-level receipt yet proves outreach, intake, counsel at hearing, settlement quality, possession, and durable housing tail. |
| `ER-HC-003` | `housing_screening_assistance_tail` | `partial_oversight_or_outcome_surface` | `False` | Tenant-screening and rental-assistance remedies must be followed through application, ledger, court, and housing-search tails. | No receipt yet proves that a corrected screening record or assistance award led to a successful application, posted payment, protected possession, or re-housing. |
| `ER-HC-004` | `housing_continuity_closure_gate` | `partial_oversight_or_outcome_surface` | `False` | A housing-continuity packet cannot be closed as repaired until household tails show possession, displacement, shelter, re-housing, screening/application effect, and durable stability. | No concrete household-level durable-stability evidence is stored or referenced by the cube. |
| `ER-HC-005` | `housing_right_to_counsel_household_outcome_aggregate` | `aggregate_household_outcome_surface` | `False` | NYC right-to-counsel evidence provides aggregate household representation and housing-outcome signals, but it still does not close the household-tail gap for unrepresented, informal, or post-case stability outcomes. | The sources report households served, representation rates, and aggregate remain/leave outcomes, but do not provide a privacy-bounded tail for households that never reached counsel, moved informally, were locked out, entered shelter, or lost stability after case closure. |
| `ER-UI-001` | `unemployment_insurance_claim_status` | `program_playbook_or_report` | `False` | A UI claim-status surface should expose actionable issue state and next steps, but status clarity is not payment proof. | No held-claim sample connects status message, burden, cure, appeal/waiver, and payment after cure. |
| `ER-UI-002` | `unemployment_insurance_customer_experience` | `program_playbook_or_report` | `False` | UI claimant-experience surveys and user testing can identify pain points, but they do not alone validate all claimant outcomes or non-users. | Survey respondents and potential users are not the same as every valid claimant delayed, denied, abandoned, or paid late. |
| `ER-UI-003` | `unemployment_insurance_integrity_remedy` | `official_policy_or_guidance` | `False` | UI identity, overpayment, waiver, and recovery controls need claimant-level remedy receipts after false positive, agency error, identity theft, or waiver eligibility. | No receipt yet shows recovery paused, debt removed, waiver granted, identity theft corrected, or money released after cure for a concrete claimant. |
| `ER-UI-004` | `unemployment_insurance_closure_gate` | `program_playbook_or_report` | `False` | A UI integrity/access packet cannot be closed as repaired until claimant-level outcomes show payment, debt, waiver, appeal, or identity-theft remedy after cure. | No concrete claimant-level post-cure outcome evidence is stored or referenced by the cube. |
| `ER-UI-005` | `unemployment_insurance_claimant_observation_and_feedback` | `aggregate_claimant_feedback_or_observation` | `False` | Direct observation and improved claimant surveys can expose UI filing burden and staff-intervention points, but they still do not prove that a claimant was paid or repaired. | The public pages show that some claimants were surveyed or observed; they do not join each participant to eligibility, payment, debt, waiver, appeal, or hardship outcome after the filing interaction. |

## Source-key recurrence

| Source key | Count |
| --- | ---: |
| `cfpb_tenant_background_checks_2024` | 2 |
| `digital_govhub_ui_cx_integrity_2025` | 1 |
| `dol_ui_claims_status_claimant_communication` | 3 |
| `dol_ui_claims_status_implement` | 3 |
| `dol_ui_claims_status_notifications` | 2 |
| `dol_ui_direct_observation_illinois` | 1 |
| `dol_ui_modernization_arpa_investments_2023` | 3 |
| `dol_ui_survey_design_ides` | 1 |
| `eviction_lab_rtc_2025` | 1 |
| `eviction_lab_tracking_system_2026` | 2 |
| `gao_evictions_data_limited_2024` | 4 |
| `nyc_comptroller_evictions_representation_2025` | 4 |
| `nyc_ocj_annual_report_2025` | 1 |
| `omb_a11_section_280_2025` | 3 |
| `omb_m_22_10_public_benefits_pra` | 1 |

## Note recurrence

| Note | Count |
| --- | ---: |
| `404` | 6 |
| `425` | 5 |
| `426` | 4 |
| `505` | 1 |
| `719` | 2 |
| `720` | 1 |
| `821` | 1 |
| `857` | 11 |
| `894` | 2 |
| `913` | 5 |
| `914` | 5 |
| `927` | 3 |
| `928` | 5 |
| `929` | 5 |
| `983` | 4 |
| `984` | 11 |
| `985` | 4 |
| `986` | 2 |

## Privacy posture

Do not store names, addresses, claim numbers, case numbers, screenshots of private accounts, or private records. Store claim class, source posture, locator, limitations, and minimum next receipt only.
