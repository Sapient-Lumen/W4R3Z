# Source health

Generated for `rev0799` from `metadata/source_health.json`, `metadata/source_health_taxonomy.json`, and `sources/source_keys.json`.

This is an offline dependency and currentness surface. It does not prove a URL is live; it shows which source keys are checked, unchecked, volatile, supersession-prone, and depended on by notes, claims, and case packets.

## Summary

| Metric | Count |
| --- | ---: |
| Source keys | 750 |
| Manual health entries | 750 |
| Manual health coverage | 100.00% |
| Direct-review entries | 750 |
| Direct-review coverage | 100.00% |
| Clean direct-review entries | 735 |
| Clean direct-review coverage | 98.00% |
| Limited-reliance direct-review entries | 13 |
| Limited-reliance share | 1.73% |
| Follow-up capture entries | 2 |
| Follow-up capture share | 0.27% |
| Catalog-triage entries awaiting direct refresh | 0 |
| Catalog-triage share | 0.00% |
| Unclassified / unchecked keys | 0 |
| Review-due checked keys | 0 |

## Health status counts

| Status | Count |
| --- | ---: |
| `checked` | 68 |
| `checked_active_incident_anchor` | 2 |
| `checked_active_lessons_anchor` | 1 |
| `checked_active_policy_anchor` | 1 |
| `checked_active_standard_anchor` | 1 |
| `checked_current_as_live_register` | 2 |
| `checked_current_as_live_register_record` | 7 |
| `checked_current_as_of_review` | 208 |
| `current_as_of_review` | 24 |
| `current_direct_review_reliance_limited` | 4 |
| `current_limited_reliance_locator_only` | 9 |
| `current_official_data_surface` | 3 |
| `current_official_living_source` | 161 |
| `current_official_periodic_summary` | 3 |
| `current_search_resolved_reliance_limited` | 1 |
| `current_secondary_risk_signal_limited_reliance` | 1 |
| `direct_review_current_official_locator` | 10 |
| `direct_review_stable_or_historical_anchor` | 23 |
| `external_analysis_current_as_of_review` | 1 |
| `external_research_current_as_of_review` | 1 |
| `historical_case_anchor_not_continuing_authority` | 1 |
| `historical_news_anchor_not_continuing_authority` | 4 |
| `needs_frequent_direct_check_for_live_use` | 10 |
| `needs_periodic_direct_check` | 63 |
| `official_enforcement_action_surface` | 2 |
| `official_living_rule_text` | 2 |
| `official_proposed_rule_surface` | 1 |
| `official_search_resolved_page_blocked_reliance_limited` | 2 |
| `reliance_limited_direct_review` | 7 |
| `retired_or_ended_surface_checked` | 1 |
| `stable_guidance_or_historical_anchor` | 1 |
| `stable_historical_anchor_reliance_limited` | 1 |
| `stable_historical_or_supersession_prone_anchor` | 7 |
| `stable_historical_primary_source` | 6 |
| `stable_legal_or_soft_law_anchor` | 2 |
| `stable_legal_text_checked` | 13 |
| `stable_official_guidance_anchor` | 4 |
| `stable_official_report_anchor` | 1 |
| `stable_reference_or_historical_anchor` | 58 |
| `stable_report_or_guidance_anchor` | 1 |
| `stable_report_or_historical_anchor` | 25 |
| `stable_report_with_followup_clock` | 7 |

## Taxonomy-pressure audit

| Field | Raw unique labels | Normalized labels |
| --- | ---: | ---: |
| `health_status` | 42 | 5 |
| `expected_volatility` | 60 | 6 |

### Normalized volatility counts

| Normalized volatility | Count |
| --- | ---: |
| `implementation_or_event_clock` | 221 |
| `live_or_current_surface` | 84 |
| `periodic_refresh` | 101 |
| `stable_or_historical_anchor` | 176 |
| `supersession_or_policy_clock` | 99 |
| `unclassified_or_other` | 69 |

### Normalized health-status counts

| Normalized status | Count |
| --- | ---: |
| `checked_or_current` | 554 |
| `limited_reliance` | 1 |
| `needs_followup_or_check` | 80 |
| `stable_or_historical_anchor` | 110 |
| `unclassified_or_other` | 5 |

## Largest dependent surfaces

| Source key | Dependents | Volatility | Status | Risk flags |
| --- | ---: | --- | --- | --- |
| `nyc_comptroller_mycity_audit_2025` | 17 | `stable_with_order_followup` | `stable_report_or_historical_anchor` | `audit-followup`, `cost-overrun`, `local-digital-government`, `municipal-ai`, `rev0783`, `service-home`, `transition-receipt` |
| `uk_ai_playbook_2025` | 17 | `current` | `checked_current_as_of_review` | `AI-governance`, `staff-copilot`, `public-service-guidance`, `source-boundary` |
| `nyc_algorithmic_tools_report_2025` | 16 | `annual` | `checked` | `annual-report-cycle`, `local-digital-government`, `municipal-algorithmic-tools`, `pdf-source`, `rev0783`, `service-home` |
| `interoperable_europe_assessment_guidelines` | 15 | `supersession_risk` | `checked_current_as_of_review` | `interoperability`, `cross-border-services`, `guidance-revision`, `source-boundary` |
| `uk_algorithmic_transparency_records_hub` | 14 | `live_dashboard` | `checked_current_as_live_register` | `AI-register`, `live-register`, `phase-drift`, `source-boundary` |
| `nyc_chatbot_beta_ended` | 13 | `event_triggered` | `retired_or_ended_surface_checked` | `chatbot`, `local-digital-government`, `retired-surface`, `rev0783`, `service-home`, `source-boundary`, `transition-receipt` |
| `nyc_comptroller_evictions_representation_2025` | 12 | `periodic` | `current_as_of_review` | `eviction`, `right-to-counsel`, `representation`, `rental-assistance-delay` |
| `oecd_governing_city` | 12 | `stable` | `stable_reference_or_historical_anchor` | `metropolitan-governance`, `cross-boundary-authority`, `case-packet-dependency` |
| `world_bank_metropolitan_governance` | 12 | `stable` | `stable_reference_or_historical_anchor` | `metropolitan-governance`, `cross-boundary-authority`, `case-packet-dependency` |
| `cfpb_consumer_complaint_database_2026` | 11 | `agency_webpage_and_rule_guidance_clock` | `current_official_living_source` | `consumer-finance-continuity`, `bank-accounts`, `credit-reporting`, `debt-collection`, `Reg-E`, `complaints`, `source-boundary`, `no-financial-access-by-account-row` |
| `cfpb_reg_e_1005_2026` | 11 | `agency_webpage_and_rule_guidance_clock` | `current_official_living_source` | `consumer-finance-continuity`, `bank-accounts`, `credit-reporting`, `debt-collection`, `Reg-E`, `complaints`, `source-boundary`, `no-financial-access-by-account-row` |
| `cfpb_submit_complaint_2026` | 11 | `agency_webpage_and_rule_guidance_clock` | `current_official_living_source` | `consumer-finance-continuity`, `bank-accounts`, `credit-reporting`, `debt-collection`, `Reg-E`, `complaints`, `source-boundary`, `no-financial-access-by-account-row` |
| `coe_local_self_government` | 11 | `periodic` | `checked_current_as_of_review` | `local-self-government`, `cross-boundary-authority`, `treaty-reference` |
| `la_county_lahsa_jpa_presentation` | 11 | `stable_historical_anchor` | `stable_report_or_historical_anchor` | `LAHSA`, `joint-powers-authority`, `homelessness-governance`, `transition`, `source-boundary` |
| `nist_ai_rmf` | 11 | `supersession_risk` | `checked_current_as_of_review` | `AI-risk`, `standards`, `critical-infrastructure`, `source-boundary` |
| `ap_lahsa_restructure_2025` | 10 | `stable` | `historical_news_anchor_not_continuing_authority` | `case-packet-dependency`, `audit-trigger`, `not-continuing-authority` |
| `cfpb_bank_accounts_services_2025` | 10 | `agency_webpage_and_rule_guidance_clock` | `current_official_living_source` | `consumer-finance-continuity`, `bank-accounts`, `credit-reporting`, `debt-collection`, `Reg-E`, `complaints`, `source-boundary`, `no-financial-access-by-account-row` |
| `cfpb_prepaid_accounts_1005_18_2026` | 10 | `agency_webpage_and_rule_guidance_clock` | `current_official_living_source` | `consumer-finance-continuity`, `bank-accounts`, `credit-reporting`, `debt-collection`, `Reg-E`, `complaints`, `source-boundary`, `no-financial-access-by-account-row` |
| `eviction_lab_2025_filing_patterns_2026` | 10 | `periodic` | `current_as_of_review` | `eviction-filings`, `renter-households`, `racial-disparity`, `data-infrastructure` |
| `helpwithmybank_file_complaint_2026` | 10 | `agency_webpage_and_rule_guidance_clock` | `current_official_living_source` | `consumer-finance-continuity`, `bank-accounts`, `credit-reporting`, `debt-collection`, `Reg-E`, `complaints`, `source-boundary`, `no-financial-access-by-account-row` |
| `la_county_auditor_lahsa_finance_contracts_2024` | 10 | `periodic` | `reliance_limited_direct_review` | `AI-governance`, `municipal-handback`, `source-health`, `supplier-dependency`, `direct-refresh-rev0772`, `direct-refresh-rev0775`, `reliance-limited` |
| `la_county_dh_page` | 10 | `implementation_clock` | `current_official_living_source` | `LA-homelessness`, `symbolic-authority`, `implementation`, `department-transition`, `source-boundary` |
| `markup_nyc_chatbot_illegal_advice_2024` | 10 | `stable` | `historical_news_anchor_not_continuing_authority` | `audit-trigger`, `case-packet-dependency`, `local-digital-government`, `not-continuing-authority`, `rev0783`, `service-home` |
| `omb_2025_federal_ai_inventory` | 10 | `volatile` | `checked` | `inventory-update-risk`, `machine-readable-public-register` |
| `ap_nyc_chatbot_false_advice_2024` | 9 | `stable` | `historical_news_anchor_not_continuing_authority` | `AI-governance`, `direct-refresh-rev0770`, `local-digital-government`, `rev0783`, `service-home`, `source-boundary`, `source-health` |
| `govuk_chat_pilot_findings_2026` | 9 | `implementation_clock` | `checked_current_as_of_review` | `public-service-chatbot`, `pilot-to-scale`, `AI-governance`, `source-boundary` |
| `govuk_onelogin_technical_how_it_works` | 9 | `supersession_risk` | `needs_periodic_direct_check` | `credential-access`, `identity-proofing`, `technical-docs` |
| `la_city_controller_interim_housing_audit` | 9 | `stable` | `checked_current_as_of_review` | `homelessness-governance`, `budget-accountability`, `service-continuity` |
| `la_city_controller_pathways_audit` | 9 | `stable` | `checked_current_as_of_review` | `homelessness-governance`, `budget-accountability`, `service-continuity` |
| `la_county_hsh_director_2025` | 9 | `implementation_clock` | `checked_current_as_of_review` | `homelessness-governance`, `budget-accountability`, `service-continuity` |

## Catalog-triage direct-refresh priority sources

These source keys have a manual catalog posture but were not directly network-checked in the offline build. They are sorted by dependency and volatility so future refresh passes start where stale evidence would be most consequential.

| Source key | Score | Dependents | Volatility | Status | Publisher | Title |
| --- | ---: | ---: | --- | --- | --- | --- |
| — | 0 | 0 | — | — | — | — |

## Limited-reliance direct-review sources

These source keys have an official or primary route identified, but the route is intentionally limited: legal section-level, quote-level, supersession, page/PDF, or outcome reliance still needs extra evidence. They are no longer capture-required rows, but they are not clean outcome proof.

| Source key | Score | Dependents | Volatility | Status | Reliance tier | Result | Publisher | Title |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| — | 0 | 0 | — | — | — | — | — | — |

## Follow-up capture priority sources

These source keys have been moved out of catalog-only posture but still require a page-level, PDF, blocked-route, or direct-capture follow-up before quote-level or legal reliance. They are direct-refresh attempts, not clean reliance-ready checks.

| Source key | Score | Dependents | Volatility | Status | Result | Publisher | Title |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| `cisa_bod_20_01_vulnerability_disclosure_policy` | 8 | 0 | `cybersecurity_policy_clock` | `official_search_resolved_page_blocked_reliance_limited` | `official_result_resolved_but_direct_open_blocked_403_during_rev0799` | Cybersecurity and Infrastructure Security Agency | BOD 20-01: Develop and Publish a Vulnerability Disclosure Policy |
| `cisa_vulnerability_disclosure_policy_template` | 8 | 0 | `cybersecurity_guidance_clock` | `official_search_resolved_page_blocked_reliance_limited` | `official_result_resolved_but_direct_open_blocked_403_during_rev0799` | Cybersecurity and Infrastructure Security Agency | Vulnerability Disclosure Policy Template |

## Unchecked priority sources

These unchecked keys are sorted by source-health triage score, which prioritizes current notes, case packets, claims, dependency count, and volatility before routine source-health expansion.

| Source key | Score | Dependents | Reason | Publisher | Title |
| --- | ---: | ---: | --- | --- | --- |
| — | 0 | 0 | — | — | — |

## Manual health entries

| Source key | Publisher | Last checked | Result | Next review | Dependents |
| --- | --- | --- | --- | --- | ---: |
| `acf_afcars_dashboard_2024` | Administration for Children and Families, Children's Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0750_child_welfare_continuity_pass` | 2026-09-11 | 5 |
| `acf_afcars_data_statistics_2025` | Administration for Children and Families, Children's Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0750_child_welfare_continuity_pass` | 2026-09-11 | 5 |
| `acf_child_maltreatment_2024` | Administration for Children and Families, Children's Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0750_child_welfare_continuity_pass` | 2026-09-11 | 5 |
| `acf_child_welfare_cfsr_round4` | Administration for Children and Families, Children's Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0750_child_welfare_continuity_pass` | 2026-09-11 | 5 |
| `acf_nytd_data_statistics` | Administration for Children and Families, Children's Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0750_child_welfare_continuity_pass` | 2026-09-11 | 5 |
| `acf_title_iv_e_prevention_program_2026` | Administration for Children and Families, Children's Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0750_child_welfare_continuity_pass` | 2026-09-11 | 5 |
| `acl_aps_final_rule_2024` | Administration for Community Living | 2026-06-13 | `resolved_or_indexed_during_rev0752_long_term_care_continuity_pass` | 2026-12-10 | 5 |
| `acl_ltc_ombudsman_program_2024` | Administration for Community Living | 2026-06-13 | `resolved_or_indexed_during_rev0752_long_term_care_continuity_pass` | 2026-12-10 | 5 |
| `acl_namrs_home_2026` | Administration for Community Living / National Adult Maltreatment Reporting System | 2026-06-13 | `resolved_or_indexed_during_rev0752_long_term_care_continuity_pass` | 2026-12-10 | 5 |
| `ada_voting_polling_places_2026` | ADA.gov / U.S. Department of Justice | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-09-11 | 5 |
| `ap_haiti_chad_gsf_arrival_2026` | Associated Press | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2027-06-17 | 5 |
| `ap_lahsa_restructure_2025` | Associated Press | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2027-06-17 | 10 |
| `ap_nyc_chatbot_false_advice_2024` | Associated Press | 2026-06-17 | `ap_news_article_resolved_during_rev0770` | 2027-06-17 | 9 |
| `binuh_haiti_q1_2026_human_rights` | United Nations Integrated Office in Haiti (BINUH) | 2026-06-17 | `official_route_identified_but_current_context_limited` | 2026-10-15 | 6 |
| `bja_dcra_reported_data_2025` | Bureau of Justice Assistance | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-09-11 | 5 |
| `bja_dcra_state_implementation_plans_2024` | Bureau of Justice Assistance | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-09-11 | 5 |
| `bjs_correctional_populations_2022` | Bureau of Justice Statistics | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-12-10 | 5 |
| `bjs_first_step_act_2025` | Bureau of Justice Statistics | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-12-10 | 5 |
| `bjs_jail_inmates_2023` | Bureau of Justice Statistics | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-12-10 | 5 |
| `bjs_mci_data_collection` | Bureau of Justice Statistics | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-12-10 | 5 |
| `bjs_mortality_local_jails_2000_2019` | Bureau of Justice Statistics | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-12-10 | 5 |
| `bjs_prisoners_2023` | Bureau of Justice Statistics | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-12-10 | 5 |
| `bma_fdp_palantir_resolution_2025` | British Medical Association | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-10-15 | 5 |
| `bop_first_step_act_annual_report_2024` | Federal Bureau of Prisons | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-12-10 | 5 |
| `brazil_ai_bill_pl2338_camara` | Câmara dos Deputados | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-08-09 | 4 |
| `brazil_ai_bill_pl2338_senate` | Senado Federal | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-08-09 | 3 |
| `brazil_anpd_ai_automated_decisions_2025` | Autoridade Nacional de Proteção de Dados | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-12-07 | 3 |
| `brazil_bolsa_familia_decree_12064` | Presidência da República / Planalto | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2027-06-10 | 4 |
| `brazil_bolsa_familia_law_14601` | Presidência da República / Planalto | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2027-06-10 | 4 |
| `brazil_cadunico_block_schedule_2026` | Ministério do Desenvolvimento e Assistência Social, Família e Combate à Fome | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-09-08 | 4 |
| `brazil_cadunico_decree_11016` | Presidência da República / Planalto | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-09-08 | 4 |
| `brazil_cadunico_mds_home_2026` | Ministério do Desenvolvimento e Assistência Social, Família e Combate à Fome | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-09-08 | 5 |
| `brazil_cadunico_new_system_2025` | Ministério do Desenvolvimento e Assistência Social, Família e Combate à Fome | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-09-08 | 3 |
| `brazil_cadunico_qualification_2026` | Ministério do Desenvolvimento e Assistência Social, Família e Combate à Fome | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-09-08 | 5 |
| `brazil_digital_government_law_14129` | Presidência da República / Planalto | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2027-06-10 | 5 |
| `brazil_federal_digital_strategy_ind_decree_12198` | Presidência da República / Planalto | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2027-06-10 | 4 |
| `brazil_govbr_account_levels` | Governo Digital / gov.br | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-09-08 | 5 |
| `brazil_lgpd_law_13709` | Presidência da República / Planalto | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2027-06-10 | 4 |
| `brazil_national_digital_gov_strategy_decree_12069` | Presidência da República / Planalto | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2027-06-10 | 4 |
| `brazil_pbia_2024_2028` | Ministério da Ciência, Tecnologia e Inovação | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-12-07 | 4 |
| `brazil_pbia_final_pdf_2025` | Ministério da Ciência, Tecnologia e Inovação | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-12-07 | 3 |
| `british_library_cyber_attack_lessons_2024` | British Library | 2026-06-13 | `direct_page_opened` | 2026-12-10 | 6 |
| `bts_national_transit_map_2025` | Bureau of Transportation Statistics | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `bts_public_transit_ridership_2024` | Bureau of Transportation Statistics | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `california_cde_ai_public_schools_2026` | California Department of Education | 2026-06-10 | `resolved` | 2026-10-08 | 4 |
| `california_cde_ai_working_group_2026` | California Department of Education | 2026-06-10 | `resolved` | 2026-09-08 | 4 |
| `california_cdt_high_risk_ads_report_2025` | California Department of Technology | 2026-06-10 | `resolved` | 2026-10-08 | 5 |
| `california_cdt_hrads_faq` | California Department of Technology | 2026-06-10 | `resolved` | 2026-09-08 | 6 |
| `california_courts_generative_ai_policy_preview_2025` | California Courts Newsroom | 2026-06-10 | `resolved` | 2026-12-07 | 4 |
| `caloes_ng911_project_page_2026` | California Governor's Office of Emergency Services | 2026-06-18 | `official_Cal_OES_NG911_page_resolved_during_rev0781` | 2026-07-18 | 3 |
| `canada_algorithmic_impact_assessment` | Government of Canada | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 6 |
| `canada_automated_decision_directive` | Treasury Board of Canada Secretariat | 2026-06-17 | `canada_tbs_automated_decision_directive_search_result_resolved_request_rejected_on_open` | 2026-09-15 | 7 |
| `canada_hcm_feasibility_report_2025` | Public Services and Procurement Canada | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-09-15 | 6 |
| `canada_hr_pay_transformation_dayforce_2026` | Public Services and Procurement Canada | 2026-06-17 | `canada_hr_pay_dayforce_transformation_page_resolved` | 2026-08-16 | 5 |
| `canada_international_bridges_tunnels_act` | Justice Laws Website, Government of Canada | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 3 |
| `canada_oag_modernizing_pay_system_2026` | Office of the Auditor General of Canada | 2026-06-17 | `auditor_general_modernizing_pay_system_report_page_resolved` | 2026-10-15 | 8 |
| `canada_pay_centre_dashboard_2026` | Public Services and Procurement Canada | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-09-15 | 5 |
| `canada_phoenix_damages_compensation_2026` | Treasury Board of Canada Secretariat | 2026-06-17 | `resolved_official_canada_phoenix_damages_compensation_page_during_rev0769_web_review` | 2026-08-01 | 5 |
| `cbp_ai_use_cases` | U.S. Department of Homeland Security | 2026-06-10 | `official page indexed; direct fetch may block automated access` | 2026-09-08 | 4 |
| `cbsa_arrivecan_advance_declaration` | Canada Border Services Agency | 2026-06-17 | `cbsa_arrivecan_advance_declaration_page_resolved` | 2026-08-16 | 4 |
| `cbsa_arrivecan_main_advance_declaration` | Canada Border Services Agency | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-07-17 | 3 |
| `cbsa_arrivecan_pacp_issue_notes_2024` | Canada Border Services Agency | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 4 |
| `cbsa_arrivecan_platform_pia_summary_2025` | Canada Border Services Agency | 2026-06-17 | `cbsa_arrivecan_privacy_impact_assessment_summary_resolved` | 2026-12-14 | 8 |
| `cbsa_border_reminder_checklist_2026` | Canada Border Services Agency | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-07-17 | 2 |
| `cdc_cerc_2025` | Centers for Disease Control and Prevention | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 5 |
| `cdc_disability_emergency_preparedness_2025` | Centers for Disease Control and Prevention | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 5 |
| `cdc_drinking_water_advisories_overview_2024` | Centers for Disease Control and Prevention | 2026-06-13 | `resolved_or_indexed_during_rev0754_water_sanitation_continuity_pass` | 2026-10-11 | 5 |
| `cdc_heat_power_outage_medical_devices_2025` | Centers for Disease Control and Prevention | 2026-06-10 | `official or authoritative source indexed / opened during rev0745 climate-utility continuity pass` | 2026-12-07 | 4 |
| `census_disclosure_avoidance_methods` | U.S. Census Bureau | 2026-06-18 | `locator_level_public_source_resolved_for_release_controls; no snapshot or private data captured` | 2026-12-15 | 1 |
| `cer_amp_process_guide` | Canada Energy Regulator | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-07-17 | 0 |
| `cer_compliance_enforcement` | Canada Energy Regulator | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 1 |
| `cer_enforcement_policy` | Canada Energy Regulator | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-09-15 | 0 |
| `cer_enforcing_rules` | Canada Energy Regulator | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 0 |
| `cer_international_power_lines_dashboard` | Canada Energy Regulator | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-07-17 | 1 |
| `cer_mandate_roles_responsibilities` | Canada Energy Regulator | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 0 |
| `cer_pipeline_power_responsibilities` | Canada Energy Regulator | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 0 |
| `cer_what_we_regulate` | Canada Energy Regulator | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 0 |
| `cfpb_bank_accounts_services_2025` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 10 |
| `cfpb_chex_systems_company_list_2025` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0764_deposit_account_access_continuity_pass` | 2026-07-13 | 5 |
| `cfpb_closed_account_reopening_circular_2023` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0764_deposit_account_access_continuity_pass` | 2026-12-10 | 5 |
| `cfpb_consumer_complaint_database_2026` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 11 |
| `cfpb_consumer_reporting_companies_2025` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 5 |
| `cfpb_credit_report_dispute_2024` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 5 |
| `cfpb_credit_reports_scores_2025` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 5 |
| `cfpb_debt_collection_model_forms_2025` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 5 |
| `cfpb_debt_collection_rule_1006_34_2026` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 5 |
| `cfpb_debt_collection_validation_info_2024` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 5 |
| `cfpb_denied_checking_accounts_2016` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0764_deposit_account_access_continuity_pass` | 2026-12-10 | 5 |
| `cfpb_direct_disputes_reg_v_1022_43_2026` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 5 |
| `cfpb_early_warning_services_company_list_2025` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0764_deposit_account_access_continuity_pass` | 2026-07-13 | 5 |
| `cfpb_ftc_transunion_tenant_screening_2023` | Consumer Financial Protection Bureau | 2026-06-12 | `opened during rev0747 housing-continuity case pass` | 2027-06-12 | 5 |
| `cfpb_overdraft_options_2025` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 5 |
| `cfpb_prepaid_accounts_1005_18_2026` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 10 |
| `cfpb_reg_e_1005_2026` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 11 |
| `cfpb_submit_complaint_2026` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 11 |
| `cfpb_synapse_enforcement_action_2025` | Consumer Financial Protection Bureau | 2026-06-13 | `resolved_or_indexed_during_rev0764_deposit_account_access_continuity_pass` | 2026-08-12 | 6 |
| `cfpb_tenant_background_checks_2024` | Consumer Financial Protection Bureau | 2026-06-12 | `rechecked during rev0747 housing-continuity case pass` | 2026-12-09 | 8 |
| `childwelfare_responding_youth_missing_foster_care` | Child Welfare Information Gateway | 2026-06-13 | `resolved_or_indexed_during_rev0750_child_welfare_continuity_pass` | 2026-09-11 | 5 |
| `cisa_ai` | Cybersecurity and Infrastructure Security Agency | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `cisa_bod_20_01_vulnerability_disclosure_policy` | Cybersecurity and Infrastructure Security Agency | 2026-06-18 | `official_result_resolved_but_direct_open_blocked_403_during_rev0799` | 2026-09-16 | 0 |
| `cisa_circia_reporting_2026` | Cybersecurity and Infrastructure Security Agency | 2026-06-13 | `search_result_verified_official_source` | 2026-07-13 | 5 |
| `cisa_cross_sector_cpg_2_0` | Cybersecurity and Infrastructure Security Agency | 2026-06-13 | `search_result_verified_official_source` | 2026-09-11 | 6 |
| `cisa_election_security` | Cybersecurity and Infrastructure Security Agency | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-09-11 | 5 |
| `cisa_election_security_services` | Cybersecurity and Infrastructure Security Agency | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-09-11 | 5 |
| `cisa_known_exploited_vulnerabilities_catalog` | Cybersecurity and Infrastructure Security Agency | 2026-06-13 | `search_result_verified_official_source` | 2026-06-27 | 6 |
| `cisa_secure_software_attestation_form` | Cybersecurity and Infrastructure Security Agency | 2026-06-13 | `search_result_verified_official_source` | 2026-09-11 | 6 |
| `cisa_stopransomware_guide` | Cybersecurity and Infrastructure Security Agency | 2026-06-13 | `search_result_verified_official_source` | 2026-09-11 | 6 |
| `cisa_vulnerability_disclosure_policy_template` | Cybersecurity and Infrastructure Security Agency | 2026-06-18 | `official_result_resolved_but_direct_open_blocked_403_during_rev0799` | 2026-09-16 | 0 |
| `cms_appointment_representative_1696` | Centers for Medicare & Medicaid Services | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2027-06-17 | 4 |
| `cms_facility_initiated_discharge_2017` | Centers for Medicare & Medicaid Services | 2026-06-13 | `resolved_or_indexed_during_rev0752_long_term_care_continuity_pass` | 2026-12-10 | 5 |
| `cms_hhs_reentry_1115_guidance_2023` | Centers for Medicare & Medicaid Services | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-09-11 | 5 |
| `cms_ltc_minimum_staffing_final_rule_2024` | Centers for Medicare & Medicaid Services | 2026-06-13 | `resolved_or_indexed_during_rev0752_long_term_care_continuity_pass` | 2026-08-12 | 5 |
| `cms_medicaid_access_final_rule_2024` | Centers for Medicare & Medicaid Services | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2026-12-07 | 3 |
| `cms_medicaid_chip_streamlining_final_rule_2024` | Centers for Medicare & Medicaid Services | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2026-12-07 | 4 |
| `cms_medicaid_managed_care_access_finance_quality_final_rule_2024` | Centers for Medicare & Medicaid Services | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2026-12-07 | 3 |
| `cms_medicaid_reentry_1115_demonstrations` | Centers for Medicare & Medicaid Services / Medicaid.gov | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-09-11 | 5 |
| `cms_medicaid_renewals_transitions_coverage_webinar_2024` | Centers for Medicare & Medicaid Services | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2026-12-07 | 4 |
| `cms_medicare_prescription_payment_plan` | Centers for Medicare & Medicaid Services | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2026-10-08 | 5 |
| `cms_nursing_home_provider_data_2026` | Centers for Medicare & Medicaid Services | 2026-06-13 | `resolved_or_indexed_during_rev0752_long_term_care_continuity_pass` | 2026-08-12 | 5 |
| `cms_nursing_home_provider_info_dataset` | Centers for Medicare & Medicaid Services | 2026-06-13 | `resolved_or_indexed_during_rev0752_long_term_care_continuity_pass` | 2026-08-12 | 5 |
| `cms_part_d_model_materials_2026` | Centers for Medicare & Medicaid Services | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2026-08-09 | 5 |
| `cms_part_d_redesign_2026_instructions` | Centers for Medicare & Medicaid Services | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2026-12-07 | 5 |
| `cms_part_d_reporting_requirements_2026` | Centers for Medicare & Medicaid Services | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2026-09-08 | 5 |
| `cms_sff_candidate_list_jan_2026` | Centers for Medicare & Medicaid Services | 2026-06-13 | `resolved_or_indexed_during_rev0752_long_term_care_continuity_pass` | 2026-08-12 | 5 |
| `coe_charter_monitoring` | Council of Europe / Congress of Local and Regional Authorities | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `coe_democratic_accountability_local` | Council of Europe | 2026-06-17 | `council_of_europe_recommendation_pdf_opened_and_text_extracted_during_rev0774` | 2026-09-15 | 3 |
| `coe_local_self_government` | Council of Europe | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2027-06-17 | 11 |
| `colombia_atrato_elaw_t622` | Environmental Law Alliance Worldwide | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-12-14 | 4 |
| `colombia_atrato_minambiente_advances` | Ministerio de Ambiente y Desarrollo Sostenible / Cuenca del río Atrato | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2027-06-17 | 4 |
| `colombia_atrato_minambiente_compliance` | Ministerio de Ambiente y Desarrollo Sostenible / Cuenca del río Atrato | 2026-06-17 | `official_minambiente_page_indexed_during_rev0772_direct_refresh` | 2027-06-17 | 4 |
| `colombia_atrato_minambiente_home` | Ministerio de Ambiente y Desarrollo Sostenible | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 6 |
| `colombia_atrato_minambiente_orders` | Ministerio de Ambiente y Desarrollo Sostenible / Cuenca del río Atrato | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 6 |
| `colombia_atrato_minambiente_sentence` | Ministerio de Ambiente y Desarrollo Sostenible / Cuenca del río Atrato | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 6 |
| `colorado_sb24_205_ai_act` | Colorado General Assembly | 2026-06-10 | `resolved` | 2026-10-08 | 5 |
| `commonwealth_ombudsman_centrelink_automated_debt_2017` | Commonwealth Ombudsman | 2026-06-17 | `official_ombudsman_pdf_opened_and_screenshot_captured_during_rev0774` | 2026-07-17 | 4 |
| `contracts_finder_fdpas_award_2024` | Contracts Finder / GOV.UK | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-10-15 | 6 |
| `council_europe_local_self_government_status_2025` | Council of Europe / Venice Commission | 2026-06-17 | `council_of_europe_local_self_government_report_pdf_opened_during_rev0774` | 2026-09-15 | 3 |
| `cpuc_medical_baseline` | California Public Utilities Commission | 2026-06-10 | `official or authoritative source indexed / opened during rev0745 climate-utility continuity pass` | 2026-10-08 | 5 |
| `cpuc_psps_2026` | California Public Utilities Commission | 2026-06-12 | `opened during rev0746 cloudtainer deep-read audit` | 2026-09-10 | 6 |
| `creative_commons_license_considerations_v4` | Creative Commons | 2026-06-18 | `resolved_during_rev0799` | 2027-06-18 | 0 |
| `crs_fema_sba_disaster_assistance_r45238_2024` | Congressional Research Service | 2026-06-10 | `available as CRS report` | 2027-06-10 | 3 |
| `ct_auditors_dcf_missing_from_care_2025` | Connecticut Auditors of Public Accounts | 2026-06-13 | `resolved_or_indexed_during_rev0750_child_welfare_continuity_pass` | 2026-12-10 | 5 |
| `ct_pura_payment_assistance_programs` | Connecticut Public Utilities Regulatory Authority | 2026-06-10 | `official or authoritative source indexed / opened during rev0745 climate-utility continuity pass` | 2026-10-08 | 6 |
| `ct_winter_protection_program_2026` | State of Connecticut | 2026-06-12 | `opened during rev0746 cloudtainer deep-read audit` | 2026-10-10 | 7 |
| `dbt_ai_governance_framework_redbox_2024` | Digital Trade Blog / Department for Business and Trade | 2026-06-17 | `dbt_ai_governance_redbox_blog_resolved` | 2026-12-14 | 4 |
| `dbt_redbox_atrs` | Cabinet Office / Department for Science, Innovation and Technology / Government Digital Service | 2026-06-17 | `govuk_atrs_dbt_redbox_record_resolved` | 2026-08-16 | 4 |
| `defra_catchment_based_approach` | Defra / GOV.UK | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `detroit_city_council_fy2026_closing_resolution` | Detroit City Council | 2026-06-17 | `official_pdf_opened_and_screenshot_during_rev0772_direct_refresh` | 2026-10-15 | 5 |
| `detroit_financial_reports` | City of Detroit | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-10-15 | 5 |
| `dfe_correspondence_drafter_atrs` | Cabinet Office / Department for Science, Innovation and Technology / Government Digital Service | 2026-06-17 | `govuk_atrs_record_resolved` | 2026-08-16 | 7 |
| `dhs_2025_ai_use_case_inventory` | U.S. Department of Homeland Security | 2026-06-10 | `official page indexed; direct fetch may block automated access` | 2026-09-08 | 4 |
| `dhs_trip_2025` | U.S. Department of Homeland Security | 2026-06-10 | `official page indexed; direct fetch may block automated access` | 2026-10-08 | 4 |
| `digital_govhub_ui_cx_integrity_2025` | Digital Government Hub | 2026-06-18 | `opened_or_passage_located_during_rev0788; supports source-boundary receipt only, not field validation` | 2026-09-16 | 1 |
| `digitalgov_adm_better_practice_guide` | Australian Government Architecture / digital.gov.au | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 4 |
| `digitalgov_ai_government_policy_v2` | Australian Government / digital.gov.au | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-07-17 | 3 |
| `digitalgov_federal_source_code_policy_resource` | Digital.gov / General Services Administration | 2026-06-18 | `resolved_during_rev0799` | 2026-12-15 | 0 |
| `digitalgov_omb_a130_appendix_i_privacy_act` | Digital.gov / Office of Management and Budget | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0791; locator-level reliance only, not source-preservation closure` | 2026-12-15 | 2 |
| `disasterassistance_gov` | Federal Emergency Management Agency / DisasterAssistance.gov | 2026-06-10 | `resolved via search/open surface` | 2026-09-08 | 5 |
| `docs_un_res_2793_2025` | United Nations Digital Library / Documents | 2026-06-17 | `un_digital_library_resolution_record_resolved_during_rev0774` | 2026-10-15 | 4 |
| `doj_elder_guardian_abuse` | U.S. Department of Justice Elder Justice Initiative | 2026-06-13 | `resolved_or_indexed_during_rev0752_long_term_care_continuity_pass` | 2026-12-10 | 5 |
| `dol_information_quality_guidelines` | U.S. Department of Labor | 2026-06-18 | `resolved_during_rev0795_correction_control_pass` | 2026-12-15 | 1 |
| `dol_oig_ui_oversight_2025` | U.S. Department of Labor Office of Inspector General | 2026-06-10 | `resolved` | 2026-12-07 | 8 |
| `dol_strudl_statistical_disclosure_control` | U.S. Department of Labor Chief Evaluation Office | 2026-06-18 | `locator_level_public_source_resolved_for_release_controls; no snapshot or private data captured` | 2026-12-15 | 1 |
| `dol_ten_18_24_customer_experience` | U.S. Department of Labor Employment and Training Administration | 2026-06-10 | `resolved` | 2026-12-07 | 5 |
| `dol_ui_claims_status_claimant_communication` | U.S. Department of Labor Employment and Training Administration | 2026-06-18 | `resolved_to_official_html_page` | 2026-09-16 | 2 |
| `dol_ui_claims_status_implement` | U.S. Department of Labor Employment and Training Administration | 2026-06-18 | `resolved_to_official_html_page` | 2026-09-16 | 2 |
| `dol_ui_claims_status_notifications` | U.S. Department of Labor Employment and Training Administration | 2026-06-18 | `resolved_to_official_html_page` | 2026-09-16 | 2 |
| `dol_ui_cx_improve_applications` | U.S. Department of Labor Employment and Training Administration | 2026-06-10 | `resolved` | 2026-09-08 | 4 |
| `dol_ui_direct_observation_illinois` | U.S. Department of Labor Employment and Training Administration | 2026-06-18 | `opened_or_passage_located_during_rev0788; supports source-boundary receipt only, not field validation` | 2026-09-16 | 4 |
| `dol_ui_modernization` | U.S. Department of Labor Employment and Training Administration | 2026-06-10 | `resolved` | 2026-09-08 | 4 |
| `dol_ui_modernization_arpa_investments_2023` | U.S. Department of Labor Employment and Training Administration | 2026-06-18 | `resolved_to_official_pdf_and_relevant_page_screenshot` | 2026-09-16 | 2 |
| `dol_ui_survey_design_ides` | U.S. Department of Labor Employment and Training Administration | 2026-06-18 | `opened_or_passage_located_during_rev0788; supports source-boundary receipt only, not field validation` | 2026-09-16 | 4 |
| `dol_ui_transformation_plan_2024` | U.S. Department of Labor Employment and Training Administration | 2026-06-10 | `official page visible; plan content may move` | 2026-12-07 | 4 |
| `dol_uipl_10_26_identity_verification` | U.S. Department of Labor Employment and Training Administration | 2026-06-10 | `resolved` | 2026-09-08 | 6 |
| `dol_uipl_11_23_identity_verification` | U.S. Department of Labor Employment and Training Administration | 2026-06-10 | `resolved` | 2026-12-07 | 3 |
| `dsit_consult_atrs` | Cabinet Office / Department for Science, Innovation and Technology / Government Digital Service | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-07-17 | 1 |
| `dsit_onelogin_supplementary_estimates_2026` | Department for Science, Innovation and Technology / GOV.UK | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-10-15 | 7 |
| `dsit_redbox_atrs` | Cabinet Office / Department for Science, Innovation and Technology / Government Digital Service | 2026-06-17 | `govuk_atrs_record_resolved` | 2026-08-16 | 7 |
| `dwp_move_uc_legacy_customers_qualitative_2025` | Department for Work and Pensions / GOV.UK | 2026-06-17 | `govuk_move_to_uc_legacy_customers_research_resolved` | 2026-12-14 | 5 |
| `dwp_move_uc_migration_notice_guidance_2026` | Department for Work and Pensions / GOV.UK | 2026-06-17 | `govuk_migration_notice_guidance_page_resolved` | 2026-08-16 | 7 |
| `dwp_move_uc_nonclaimants_research_2025` | Department for Work and Pensions / GOV.UK | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-08-01 | 4 |
| `dwp_move_uc_stats_march_2026` | Department for Work and Pensions / GOV.UK | 2026-06-17 | `govuk_official_statistics_page_resolved_data_to_end_march_2026` | 2026-08-16 | 8 |
| `dwp_uc_quarterly_stats_feb2026` | Department for Work and Pensions / GOV.UK | 2026-06-17 | `official_govuk_collection_opened_during_rev0772_direct_refresh` | 2026-07-17 | 3 |
| `dwp_whitemail_vulnerability_scanner_atrs` | Cabinet Office / Department for Science, Innovation and Technology / Government Digital Service | 2026-06-17 | `govuk_atrs_record_resolved` | 2026-08-16 | 7 |
| `ea_about_responsibilities` | Environment Agency / GOV.UK | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `ea_fcerm_strategy` | Environment Agency / GOV.UK | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `ea_frmp_2021_2027` | Environment Agency / GOV.UK | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `ea_frmp_responsibilities` | Environment Agency / GOV.UK | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-09-15 | 3 |
| `ea_rbmp_2022` | Environment Agency / GOV.UK | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-09-15 | 3 |
| `ea_rbmp_interim_progress_2025` | Environment Agency / GOV.UK | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-10-15 | 3 |
| `ea_rfccs` | Environment Agency / GOV.UK | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `eac_2024_eavs_release_2025` | U.S. Election Assistance Commission | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-12-10 | 5 |
| `eac_2024_eavs_report_2025` | U.S. Election Assistance Commission | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-12-10 | 5 |
| `eac_election_audits_across_us_2025` | U.S. Election Assistance Commission | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-09-11 | 5 |
| `eac_election_results_canvass_certification_2025` | U.S. Election Assistance Commission | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-09-11 | 5 |
| `eac_managing_election_technology` | U.S. Election Assistance Commission | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-12-10 | 5 |
| `eac_voting_accessibility` | U.S. Election Assistance Commission | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-09-11 | 5 |
| `eac_vvsg_2_0` | U.S. Election Assistance Commission | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-12-10 | 5 |
| `ec_sis` | European Commission / Migration and Home Affairs | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-10-15 | 6 |
| `ec_sis_access_rights_data_protection` | European Commission / Migration and Home Affairs | 2026-06-17 | `ec_sis_access_rights_page_resolved` | 2026-09-15 | 5 |
| `ec_sis_alerts_data` | European Commission / Migration and Home Affairs | 2026-06-17 | `ec_sis_alerts_and_data_page_resolved` | 2026-09-15 | 5 |
| `ec_sis_what` | European Commission / Migration and Home Affairs | 2026-06-17 | `ec_sis_overview_page_resolved` | 2026-09-15 | 5 |
| `ecfr_45_cfr_46_102_definitions` | Electronic Code of Federal Regulations | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0791; locator-level reliance only, not source-preservation closure` | 2026-12-15 | 1 |
| `ecfr_45_cfr_46_104_exempt_research` | Electronic Code of Federal Regulations | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0791; locator-level reliance only, not source-preservation closure` | 2026-12-15 | 1 |
| `ecfr_45_cfr_46_109_irb_review` | Electronic Code of Federal Regulations | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0793; locator-level reliance only, not fieldwork authorization, collection, source preservation, or closure` | 2026-12-15 | 1 |
| `ecfr_45_cfr_46_116_informed_consent` | Electronic Code of Federal Regulations | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0791; locator-level reliance only, not source-preservation closure` | 2026-12-15 | 1 |
| `ecfr_garnishment_federal_benefits_31_cfr_212_2026` | Electronic Code of Federal Regulations | 2026-06-13 | `resolved_or_indexed_during_rev0764_deposit_account_access_continuity_pass` | 2026-07-13 | 5 |
| `ecfr_icwa_25_cfr_part_23` | Electronic Code of Federal Regulations | 2026-06-13 | `resolved_or_indexed_during_rev0750_child_welfare_continuity_pass` | 2026-09-11 | 5 |
| `ecfr_reg_cc_12_cfr_229_2026` | Electronic Code of Federal Regulations | 2026-06-13 | `resolved_or_indexed_during_rev0764_deposit_account_access_continuity_pass` | 2026-07-13 | 5 |
| `ed_crdc_2021_22_page_2025` | U.S. Department of Education / Office for Civil Rights | 2026-06-13 | `resolved_or_indexed_during_rev0753_special_education_continuity_pass` | 2026-09-11 | 5 |
| `ed_crdc_first_look_2025` | U.S. Department of Education / Office for Civil Rights | 2026-06-13 | `resolved_or_indexed_during_rev0753_special_education_continuity_pass` | 2026-09-11 | 5 |
| `ed_idea_discipline_provisions_dcl_2022` | U.S. Department of Education / OSERS / OSEP | 2026-06-13 | `resolved_or_indexed_during_rev0753_special_education_continuity_pass` | 2026-09-11 | 5 |
| `ed_idea_fast_facts_sld_2026` | U.S. Department of Education / OSEP | 2026-06-13 | `resolved_or_indexed_during_rev0753_special_education_continuity_pass` | 2026-09-11 | 5 |
| `ed_idea_section_618_data_2026` | U.S. Department of Education | 2026-06-13 | `resolved_or_indexed_during_rev0753_special_education_continuity_pass` | 2026-09-11 | 5 |
| `ed_osep_determination_letters_2025` | U.S. Department of Education / OSEP | 2026-06-13 | `resolved_or_indexed_during_rev0753_special_education_continuity_pass` | 2026-09-11 | 5 |
| `ed_osep_inclusive_practices_dcl_2025` | U.S. Department of Education / OSERS / OSEP | 2026-06-13 | `resolved_or_indexed_during_rev0753_special_education_continuity_pass` | 2026-09-11 | 5 |
| `ed_osep_spp_apr_2026` | U.S. Department of Education / OSEP | 2026-06-13 | `resolved_or_indexed_during_rev0753_special_education_continuity_pass` | 2026-09-11 | 5 |
| `ed_section_504_fape_faq_2025` | U.S. Department of Education / Office for Civil Rights | 2026-06-13 | `resolved_or_indexed_during_rev0753_special_education_continuity_pass` | 2026-09-11 | 5 |
| `ed_section_504_overview_2025` | U.S. Department of Education | 2026-06-13 | `resolved_or_indexed_during_rev0753_special_education_continuity_pass` | 2026-09-11 | 5 |
| `edps_sis` | European Data Protection Supervisor | 2026-06-17 | `edps_sis_page_resolved` | 2026-09-15 | 5 |
| `eia_2024_residential_utility_disconnections_report` | U.S. Energy Information Administration | 2026-06-12 | `opened during rev0746 cloudtainer deep-read audit` | 2027-06-12 | 6 |
| `ems_gov_nationwide_ems_incident_data_2025` | NHTSA Office of EMS / EMS.gov | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 5 |
| `ems_gov_using_ems_data_2025` | NHTSA Office of EMS / EMS.gov | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 5 |
| `emsa_thetis` | European Maritime Safety Agency | 2026-06-17 | `emsa_thetis_page_and_public_inspection_surface_resolved` | 2026-09-15 | 4 |
| `eoir_automated_case_information_2026` | U.S. Department of Justice / Executive Office for Immigration Review | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `eoir_ecas_online_filing_2025` | U.S. Department of Justice / Executive Office for Immigration Review | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `eoir_eoir33ic_change_address_2026` | U.S. Department of Justice / Executive Office for Immigration Review | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `eoir_respondent_access_faq_2026` | U.S. Department of Justice / Executive Office for Immigration Review | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `eoir_workload_adjudication_statistics_2026` | U.S. Department of Justice / Executive Office for Immigration Review | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `epa_awia_rra_erp_2026` | U.S. Environmental Protection Agency | 2026-06-13 | `resolved_or_indexed_during_rev0754_water_sanitation_continuity_pass` | 2026-08-12 | 5 |
| `epa_ccr_consumers_2025` | U.S. Environmental Protection Agency | 2026-06-13 | `resolved_or_indexed_during_rev0754_water_sanitation_continuity_pass` | 2026-10-11 | 5 |
| `epa_clean_water_act` | U.S. Environmental Protection Agency | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `epa_cwns_2022_report_2024` | U.S. Environmental Protection Agency | 2026-06-13 | `resolved_or_indexed_during_rev0754_water_sanitation_continuity_pass` | 2026-10-11 | 5 |
| `epa_dwinrsa_7th_2023` | U.S. Environmental Protection Agency | 2026-06-13 | `resolved_or_indexed_during_rev0754_water_sanitation_continuity_pass` | 2026-10-11 | 5 |
| `epa_echo_sdwa_download_summary_2025` | U.S. Environmental Protection Agency / ECHO | 2026-06-13 | `resolved_or_indexed_during_rev0754_water_sanitation_continuity_pass` | 2026-08-12 | 5 |
| `epa_fbi_cisa_nsa_water_cyber_advisory_2026` | U.S. Environmental Protection Agency / FBI / CISA / NSA | 2026-06-13 | `resolved_or_indexed_during_rev0754_water_sanitation_continuity_pass` | 2026-08-12 | 5 |
| `epa_lcri_final_rule_2024` | U.S. Environmental Protection Agency | 2026-06-13 | `resolved_or_indexed_during_rev0754_water_sanitation_continuity_pass` | 2026-08-12 | 5 |
| `epa_lead_service_line_funding_2026` | U.S. Environmental Protection Agency | 2026-06-13 | `resolved_or_indexed_during_rev0754_water_sanitation_continuity_pass` | 2026-08-12 | 5 |
| `epa_pfas_drinking_water_rule_2026` | U.S. Environmental Protection Agency | 2026-06-13 | `resolved_or_indexed_during_rev0754_water_sanitation_continuity_pass` | 2026-08-12 | 5 |
| `epa_safe_drinking_water_act` | U.S. Environmental Protection Agency | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `epa_sdwa_cyber_enforcement_alert_2024` | U.S. Environmental Protection Agency | 2026-06-13 | `resolved_or_indexed_during_rev0754_water_sanitation_continuity_pass` | 2026-08-12 | 5 |
| `epa_sdwis_federal_reporting_2026` | U.S. Environmental Protection Agency | 2026-06-13 | `resolved_or_indexed_during_rev0754_water_sanitation_continuity_pass` | 2026-08-12 | 5 |
| `epa_sdwis_waterdata_2025` | U.S. Environmental Protection Agency | 2026-06-13 | `resolved_or_indexed_during_rev0754_water_sanitation_continuity_pass` | 2026-08-12 | 5 |
| `epa_water_sector_cybersecurity_2025` | U.S. Environmental Protection Agency | 2026-06-13 | `resolved_or_indexed_during_rev0754_water_sanitation_continuity_pass` | 2026-08-12 | 5 |
| `eu_ai_act_commission` | European Commission / Shaping Europe’s digital future | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 5 |
| `eu_ai_act_eurlex_2024` | EUR-Lex | 2026-06-10 | `resolved` | 2027-06-10 | 6 |
| `eu_ai_act_service_desk_article_71` | European Commission AI Act Service Desk | 2026-06-10 | `resolved` | 2026-12-07 | 6 |
| `eu_data_act_commission` | European Commission / Shaping Europe’s digital future | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 6 |
| `eu_data_act_eurlex` | EUR-Lex / European Union | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-07-17 | 4 |
| `eu_data_act_explained_switching_2025` | European Commission | 2026-06-10 | `resolved` | 2026-12-07 | 1 |
| `eu_gpai_code_practice` | European Commission / Shaping Europe’s digital future | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-07-17 | 4 |
| `eu_gpai_guidelines` | European Commission / Shaping Europe’s digital future | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 5 |
| `eulisa_sis` | eu-LISA | 2026-06-17 | `eulisa_sis_page_resolved` | 2026-09-15 | 4 |
| `eurlex_directive_2009_16_port_state_control` | EUR-Lex / European Union | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-12-14 | 4 |
| `eurlex_reg_2018_1860_sis_return` | EUR-Lex / European Union | 2026-06-17 | `eurlex_reg_2018_1860_resolved` | 2027-06-17 | 4 |
| `eurlex_reg_2018_1861_sis_border` | EUR-Lex / European Union | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 4 |
| `eurlex_reg_2018_1862_sis_police_judicial` | EUR-Lex / European Union | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 4 |
| `eurlex_reg_2022_1190_sis_europol_alerts` | EUR-Lex / European Union | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 4 |
| `eviction_lab_2025_filing_patterns_2026` | Eviction Lab | 2026-06-12 | `rechecked during rev0747 housing-continuity case pass` | 2026-12-09 | 10 |
| `eviction_lab_rtc_2025` | Eviction Lab | 2026-06-18 | `opened_or_passage_located_during_rev0788; supports source-boundary receipt only, not field validation` | 2026-09-16 | 1 |
| `eviction_lab_tracking_system_2026` | Eviction Lab | 2026-06-12 | `rechecked during rev0747 housing-continuity case pass` | 2026-08-11 | 8 |
| `fatf_black_grey_lists` | Financial Action Task Force | 2026-06-17 | `resolved_official_current_fatf_listing_page_during_rev0769_web_review` | 2026-08-01 | 5 |
| `fatf_countries` | Financial Action Task Force | 2026-06-17 | `official_fatf_country_route_indexed_during_rev0772_direct_refresh` | 2026-12-14 | 4 |
| `fatf_fifth_round_procedures` | Financial Action Task Force | 2026-06-17 | `official_fatf_page_indexed_during_rev0772_direct_refresh` | 2026-12-14 | 4 |
| `fatf_global_network` | Financial Action Task Force | 2026-06-17 | `official_fatf_global_network_route_indexed_during_rev0772_direct_refresh` | 2026-12-14 | 4 |
| `fatf_high_risk_monitored` | Financial Action Task Force | 2026-06-17 | `resolved_official_fatf_february_2026_increased_monitoring_page_during_rev0769_web_review` | 2026-08-01 | 5 |
| `fatf_increased_monitoring_2026_02` | Financial Action Task Force | 2026-06-17 | `official_fatf_increased_monitoring_page_opened_during_rev0774` | 2026-10-15 | 5 |
| `fatf_mutual_evaluations_topic` | Financial Action Task Force | 2026-06-17 | `fatf_mutual_evaluations_page_resolved` | 2026-12-14 | 5 |
| `fatf_recommendations` | Financial Action Task Force | 2026-06-17 | `fatf_recommendations_page_resolved` | 2026-12-14 | 7 |
| `fbi_2024_watchlisting_transparency` | Federal Bureau of Investigation | 2026-06-10 | `resolved` | 2026-12-07 | 4 |
| `fbi_threat_screening_center` | Federal Bureau of Investigation | 2026-06-10 | `resolved` | 2026-12-07 | 3 |
| `fcc_911_outages_reporting_2022` | Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 8 |
| `fcc_affordable_connectivity_program_2024` | Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0758_broadband_connectivity_continuity_pass` | 2026-08-12 | 5 |
| `fcc_bdc_availability_challenge_2025` | Federal Communications Commission Broadband Data Collection Help Center | 2026-06-13 | `resolved_or_indexed_during_rev0758_broadband_connectivity_continuity_pass` | 2026-07-13 | 5 |
| `fcc_broadband_consumer_labels_2026` | Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0758_broadband_connectivity_continuity_pass` | 2026-07-13 | 5 |
| `fcc_broadband_data_collection_2026` | Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0758_broadband_connectivity_continuity_pass` | 2026-07-13 | 5 |
| `fcc_broadband_labels_glossary_2024` | Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0758_broadband_connectivity_continuity_pass` | 2026-08-12 | 5 |
| `fcc_lifeline_consumers_2026` | Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0758_broadband_connectivity_continuity_pass` | 2026-07-13 | 5 |
| `fcc_location_based_routing_911_2024` | Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 8 |
| `fcc_multilingual_wea_2026` | Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 5 |
| `fcc_national_broadband_map_2026` | Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0758_broadband_connectivity_continuity_pass` | 2026-07-13 | 5 |
| `fcc_network_outage_reporting_system_2026` | Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0758_broadband_connectivity_continuity_pass` | 2026-07-13 | 5 |
| `fcc_ng911_reliability_fnprm_2025` | Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 8 |
| `fcc_ng911_reliability_order_2026` | Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 8 |
| `fcc_outage_information_sharing_2025` | Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0758_broadband_connectivity_continuity_pass` | 2026-07-13 | 5 |
| `fcc_wireless_911_location_accuracy_2025` | Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 5 |
| `fcc_wireless_emergency_alerts_2026` | Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 5 |
| `fcdo_correspondence_triage_atrs` | Cabinet Office / Department for Science, Innovation and Technology / Government Digital Service | 2026-06-17 | `govuk_atrs_fcdo_correspondence_triage_record_resolved` | 2026-08-16 | 5 |
| `fcsm_nonresponse_bias_reporting_2023` | Federal Committee on Statistical Methodology | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0790_sampling_gate_pass; locator-level reliance only` | 2027-06-18 | 2 |
| `fcsm_spwp22_statistical_disclosure_limitation` | Federal Committee on Statistical Methodology / National Transportation Library | 2026-06-18 | `locator_level_public_source_resolved_for_release_controls; no snapshot or private data captured` | 2026-12-15 | 1 |
| `fdic_custodial_deposit_accounts_transactional_features_2024` | Federal Deposit Insurance Corporation | 2026-06-13 | `resolved_or_indexed_during_rev0764_deposit_account_access_continuity_pass` | 2026-08-12 | 5 |
| `fdic_household_survey_2023` | Federal Deposit Insurance Corporation | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 7 |
| `fdic_unbanked_underbanked_press_2024` | Federal Deposit Insurance Corporation | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 5 |
| `fed_consumer_compliance_outlook_2024_complaints_2026` | Federal Reserve System / Consumer Compliance Outlook | 2026-06-13 | `resolved_or_indexed_during_rev0764_deposit_account_access_continuity_pass` | 2027-06-13 | 5 |
| `federal_register_cbp_biometric_entry_exit_2025` | Federal Register | 2026-06-10 | `resolved` | 2027-06-10 | 6 |
| `federal_register_digital_discrimination_2024` | Federal Register / Federal Communications Commission | 2026-06-13 | `resolved_or_indexed_during_rev0758_broadband_connectivity_continuity_pass` | 2026-08-12 | 5 |
| `federal_register_fema_ia_program_equity_2024` | Federal Register / FEMA | 2026-06-10 | `resolved` | 2027-06-10 | 6 |
| `federal_register_medicaid_chip_streamlining_rule_2024` | Federal Register / Centers for Medicare & Medicaid Services | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2027-06-10 | 4 |
| `federal_register_transit_asset_management_2025` | Federal Register / Federal Transit Administration | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `federal_register_usps_postmarks_postal_possession_2025` | Federal Register / United States Postal Service | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-12-10 | 5 |
| `federal_reserve_evolve_enforcement_2024` | Board of Governors of the Federal Reserve System | 2026-06-13 | `resolved_or_indexed_during_rev0764_deposit_account_access_continuity_pass` | 2026-09-11 | 5 |
| `fedramp_marketplace` | FedRAMP.gov | 2026-06-17 | `official_fedramp_marketplace_route_resolved_during_rev0774` | 2026-09-15 | 5 |
| `fema_individual_assistance_appeals` | Federal Emergency Management Agency | 2026-06-10 | `search-visible; direct fetch may require browser access` | 2026-09-08 | 5 |
| `fema_individual_assistance_library` | Federal Emergency Management Agency | 2026-06-10 | `search-visible; direct fetch may require browser access` | 2026-09-08 | 2 |
| `fema_individual_assistance_program` | Federal Emergency Management Agency | 2026-06-10 | `search-visible; direct fetch may require browser access` | 2026-09-08 | 5 |
| `fema_ipaws_2026` | Federal Emergency Management Agency | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 8 |
| `fema_ipaws_public_alerts_2026` | Federal Emergency Management Agency | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 5 |
| `fhwa_gordie_howe_profile` | Federal Highway Administration | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-07-17 | 3 |
| `flood_risk_regulations_2009` | UK legislation.gov.uk | 2026-06-17 | `legal_text_route_identified_but_status_limited` | 2026-09-15 | 5 |
| `flood_water_management_act_2010` | UK legislation.gov.uk | 2026-06-17 | `legal_text_route_identified_but_outcome_limited` | 2026-09-15 | 5 |
| `fna_child_nutrition_tables_2026` | USDA Food and Nutrition Administration | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `fna_disaster_assistance_2026` | USDA Food and Nutrition Administration | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `fna_dsnap_income_eligibility_fy26` | USDA Food and Nutrition Administration | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `fna_snap_application_timeliness_2026` | USDA Food and Nutrition Administration | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `fna_snap_data_tables_2026` | USDA Food and Nutrition Administration | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `fna_snap_ebt_modernization_2026` | USDA Food and Nutrition Administration | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `fna_snap_recertification_timeliness_fy2024_2026` | USDA Food and Nutrition Administration | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `fna_snap_retailer_locator_data_2026` | USDA Food and Nutrition Administration | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `fna_snap_stolen_benefits_2026` | USDA Food and Nutrition Administration | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `fna_snap_stolen_benefits_dashboard_2026` | USDA Food and Nutrition Administration | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `fna_summer_ebt_2026` | USDA Food and Nutrition Administration | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `fna_summer_ebt_toolkit_2026` | USDA Food and Nutrition Administration | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `fna_wic_data_tables_2026` | USDA Food and Nutrition Administration | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `fna_wic_modernization_2025` | USDA Food and Nutrition Administration | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `fta_ada_complaint_process_2025` | Federal Transit Administration | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `fta_ada_faq_paratransit_2025` | Federal Transit Administration | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `fta_ada_guidance_2020` | Federal Transit Administration | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `fta_ntd_2024_annual_service_database` | Federal Transit Administration | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `fta_ntd_data_page_2026` | Federal Transit Administration | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `fta_ntd_home_2025` | Federal Transit Administration | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `fta_ptasp_2025` | Federal Transit Administration | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `fta_ptasp_final_rule_2025` | Federal Transit Administration | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `fta_tam_performance_management_2026` | Federal Transit Administration | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `fta_title_vi_circular_4702_1b_2012` | Federal Transit Administration | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `fta_title_vi_guidance_2025` | Federal Transit Administration | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `fta_transit_asset_management_2026` | Federal Transit Administration | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `ftc_fair_credit_reporting_act_2026` | Federal Trade Commission | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 5 |
| `ftc_fair_debt_collection_practices_act_2026` | Federal Trade Commission | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 5 |
| `ftc_transunion_tenant_screening_settlement_2023` | Federal Trade Commission | 2026-06-12 | `opened during rev0747 housing-continuity case pass` | 2027-06-12 | 5 |
| `fvap_june_2026_voter_alert` | Federal Voting Assistance Program | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-09-11 | 5 |
| `fvap_uocava_law` | Federal Voting Assistance Program | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-12-10 | 5 |
| `gao_2022_disaster_recovery_federal_approach` | U.S. Government Accountability Office | 2026-06-10 | `resolved` | 2027-06-10 | 5 |
| `gao_2022_pua_racial_disparities` | U.S. Government Accountability Office | 2026-06-10 | `resolved` | 2027-06-10 | 4 |
| `gao_2023_facial_recognition_law_enforcement` | U.S. Government Accountability Office | 2026-06-10 | `resolved` | 2026-12-07 | 6 |
| `gao_2023_ui_fraud_estimate` | U.S. Government Accountability Office | 2026-06-10 | `resolved` | 2027-06-10 | 8 |
| `gao_2023_ui_it_modernization` | U.S. Government Accountability Office | 2026-06-10 | `resolved` | 2027-06-10 | 4 |
| `gao_2024_pua_fraud_controls` | U.S. Government Accountability Office | 2026-06-10 | `resolved` | 2027-06-10 | 4 |
| `gao_2024_residential_facilities_abuse` | U.S. Government Accountability Office | 2026-06-13 | `resolved_or_indexed_during_rev0750_child_welfare_continuity_pass` | 2026-12-10 | 5 |
| `gao_2025_disaster_assistance_federal_approach` | U.S. Government Accountability Office | 2026-06-10 | `resolved` | 2027-06-10 | 5 |
| `gao_2025_generative_ai_use_management` | U.S. Government Accountability Office | 2026-06-10 | `resolved` | 2027-06-10 | 6 |
| `gao_2025_high_risk_series` | U.S. Government Accountability Office | 2026-06-10 | `resolved` | 2027-06-10 | 7 |
| `gao_2025_legacy_it_modernization` | U.S. Government Accountability Office | 2026-06-17 | `resolved` | 2027-06-17 | 1 |
| `gao_2025_sba_dol_overpayment_recovery` | U.S. Government Accountability Office | 2026-06-10 | `resolved` | 2027-06-10 | 5 |
| `gao_2025_watchlist_nomination_redress` | U.S. Government Accountability Office | 2026-06-10 | `resolved` | 2027-06-10 | 6 |
| `gao_2026_congregate_care_family_first` | U.S. Government Accountability Office | 2026-06-13 | `resolved_or_indexed_during_rev0750_child_welfare_continuity_pass` | 2026-12-10 | 5 |
| `gao_2026_irs_ai_inventory_supplement` | U.S. Government Accountability Office | 2026-06-10 | `resolved` | 2027-06-10 | 5 |
| `gao_2026_irs_ai_management` | U.S. Government Accountability Office | 2026-06-10 | `resolved` | 2027-06-10 | 6 |
| `gao_2026_sba_ai_reporting` | U.S. Government Accountability Office | 2026-06-10 | `resolved` | 2027-06-10 | 6 |
| `gao_2026_watchlist_nonfederal_law_enforcement` | U.S. Government Accountability Office | 2026-06-10 | `resolved` | 2027-06-10 | 6 |
| `gao_bop_health_care_reentry_2023` | U.S. Government Accountability Office | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-12-10 | 5 |
| `gao_bop_id_documents_2022` | U.S. Government Accountability Office | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-12-10 | 5 |
| `gao_bop_rrc_2026` | U.S. Government Accountability Office | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-09-11 | 5 |
| `gao_erc_lessons_2026` | U.S. Government Accountability Office | 2026-06-17 | `gao_erc_lessons_report_page_resolved` | 2026-12-14 | 7 |
| `gao_evictions_data_limited_2024` | U.S. Government Accountability Office | 2026-06-12 | `opened during rev0747 housing-continuity case pass` | 2027-06-12 | 8 |
| `gao_evidence_based_policymaking_practices_2023` | U.S. Government Accountability Office | 2026-06-18 | `official_gao_product_page_resolved; no private data captured` | 2027-06-18 | 2 |
| `gao_green_book_2025` | U.S. Government Accountability Office | 2026-06-18 | `locator_level_public_source_resolved_for_redress_verification_controls; no snapshot or private data captured` | 2027-06-18 | 3 |
| `gao_guardianship_abuse_unknown_2016` | U.S. Government Accountability Office | 2026-06-13 | `resolved_or_indexed_during_rev0752_long_term_care_continuity_pass` | 2026-12-10 | 5 |
| `gao_idea_dispute_resolution_2019` | U.S. Government Accountability Office | 2026-06-13 | `resolved_or_indexed_during_rev0753_special_education_continuity_pass` | 2026-09-11 | 5 |
| `gao_program_evaluation_key_terms_2021` | U.S. Government Accountability Office | 2026-06-18 | `official_gao_product_locator_resolved; no private data captured` | 2027-06-18 | 1 |
| `gao_rural_tribal_transit_2025` | U.S. Government Accountability Office | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `gao_transit_asset_management_2020` | U.S. Government Accountability Office | 2026-06-13 | `resolved_or_indexed_during_rev0757_transportation_mobility_continuity_pass` | 2026-07-28 | 5 |
| `gao_va_disability_program_management_2025` | U.S. Government Accountability Office | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-09-11 | 5 |
| `gao_va_disability_rating_schedule_2026` | U.S. Government Accountability Office | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-09-11 | 5 |
| `gao_va_ehrm_deployments_2025` | U.S. Government Accountability Office | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-09-11 | 5 |
| `gds_dwp_onelogin_kbv_2026` | Government Digital Service blog | 2026-06-18 | `official_or_primary_route_resolved_during_rev0782_service_home_packet` | 2026-10-16 | 3 |
| `gds_hmrc_onelogin_rollout_2026` | Government Digital Service blog | 2026-06-18 | `official_or_primary_route_resolved_during_rev0782_service_home_packet` | 2026-10-16 | 3 |
| `gla_decision_making` | London City Hall / Greater London Authority | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `gla_governance` | London City Hall / Greater London Authority | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 7 |
| `govuk_atrs_public_sector_guidance_2025` | GOV.UK | 2026-06-10 | `resolved` | 2026-12-07 | 7 |
| `govuk_benefit_appointee` | GOV.UK | 2026-06-17 | `govuk_benefit_appointee_guidance_resolved` | 2026-09-15 | 7 |
| `govuk_chat_algorithmic_transparency_record` | Government Digital Service / Department for Science, Innovation and Technology | 2026-06-17 | `govuk_chat_atrs_record_resolved` | 2026-08-16 | 7 |
| `govuk_chat_engineering_journey_2026` | Inside GOV.UK | 2026-06-17 | `inside_govuk_chat_engineering_journey_resolved` | 2026-10-15 | 4 |
| `govuk_chat_jailbreaking_2024` | Inside GOV.UK | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-10-15 | 6 |
| `govuk_chat_pilot_findings_2026` | Inside GOV.UK | 2026-06-17 | `inside_govuk_chat_pilot_findings_page_resolved` | 2026-08-16 | 9 |
| `govuk_chat_privacy_notice` | Government Digital Service | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-09-15 | 3 |
| `govuk_help_someone_benefit_claim` | GOV.UK | 2026-06-17 | `official_govuk_page_indexed_during_rev0772_direct_refresh` | 2027-06-17 | 4 |
| `govuk_onelogin_about_service_2026` | GOV.UK One Login / Government Digital Service | 2026-06-18 | `official_or_primary_route_resolved_during_rev0782_service_home_packet` | 2026-08-17 | 3 |
| `govuk_onelogin_privacy_notice_2026` | GOV.UK / Government Digital Service | 2026-06-17 | `govuk_onelogin_privacy_notice_page_resolved` | 2026-08-16 | 8 |
| `govuk_onelogin_services_list_2026` | GOV.UK One Login | 2026-06-18 | `official_or_primary_route_resolved_during_rev0782_service_home_packet` | 2026-08-17 | 3 |
| `govuk_onelogin_status_2026` | GOV.UK One Login status page | 2026-06-17 | `live_status_page_opened_during_rev0772_direct_refresh` | 2027-06-17 | 7 |
| `govuk_onelogin_technical_how_it_works` | GOV.UK One Login technical documentation | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-09-15 | 9 |
| `govuk_service_standard_reliable_service_2026` | Government Digital Service / GOV.UK | 2026-06-18 | `resolved` | 2026-12-15 | 2 |
| `govuk_service_standard_whole_problem_2026` | Government Digital Service / GOV.UK | 2026-06-18 | `resolved` | 2026-12-15 | 2 |
| `govuk_state_of_digital_government_review_2025` | Department for Science, Innovation and Technology / GOV.UK | 2026-06-18 | `official_or_primary_route_resolved_during_rev0782_service_home_packet` | 2026-10-16 | 3 |
| `govuk_using_one_login_2026` | GOV.UK | 2026-06-18 | `official_or_primary_route_resolved_during_rev0782_service_home_packet` | 2026-08-17 | 3 |
| `gsa_fedramp` | U.S. General Services Administration | 2026-06-17 | `gsa_fedramp_page_resolved_by_search_and_fedramp_home_opened` | 2026-08-16 | 6 |
| `gsa_oes_evidence_act_toolkits` | GSA Office of Evaluation Sciences | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0790_sampling_gate_pass; locator-level reliance only` | 2026-12-15 | 1 |
| `gsa_open_source_software_policy` | General Services Administration | 2026-06-18 | `resolved_during_rev0799` | 2026-12-15 | 0 |
| `gsaig_logingov_ial2_evaluation_2023` | GSA Office of Inspector General | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-10-15 | 4 |
| `harvard_medicaid_unwinding_prescription_access_2026` | Harvard T.H. Chan School of Public Health | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2027-06-10 | 5 |
| `healthcaregov_marketplace_appeal_representative` | HealthCare.gov | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2027-06-17 | 4 |
| `healthcaregov_medicaid_chip_transfer_marketplace` | HealthCare.gov | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2026-09-08 | 5 |
| `healthcaregov_sep_confirm_loss_medicaid_chip_documents` | HealthCare.gov | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2026-09-08 | 5 |
| `helpwithmybank_file_complaint_2026` | Office of the Comptroller of the Currency | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 10 |
| `hhs_change_healthcare_cyber_incident_faq_2025` | U.S. Department of Health and Human Services | 2026-06-13 | `direct_page_opened` | 2026-08-12 | 6 |
| `hhs_empower_map_monthly` | U.S. Department of Health and Human Services | 2026-06-12 | `opened during rev0746 cloudtainer deep-read audit` | 2026-08-11 | 5 |
| `hhs_empower_program_home` | U.S. Department of Health and Human Services | 2026-06-12 | `opened during rev0746 cloudtainer deep-read audit` | 2026-12-09 | 5 |
| `hhs_guidance_hcbs_qms_2024` | U.S. Department of Health and Human Services | 2026-06-13 | `resolved_or_indexed_during_rev0752_long_term_care_continuity_pass` | 2026-08-12 | 5 |
| `hhs_liheap_program_2025` | Administration for Children and Families / U.S. Department of Health and Human Services | 2026-06-12 | `opened during rev0746 cloudtainer deep-read audit` | 2026-10-10 | 6 |
| `hhs_ltc_staffing_repeal_2025` | U.S. Department of Health and Human Services | 2026-06-13 | `resolved_or_indexed_during_rev0752_long_term_care_continuity_pass` | 2026-08-12 | 5 |
| `hhs_medicare_right_to_representation` | U.S. Department of Health and Human Services | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 6 |
| `hhs_ohrp_45_cfr_46_overview` | U.S. Department of Health and Human Services, Office for Human Research Protections | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0791; locator-level reliance only, not source-preservation closure` | 2026-12-15 | 1 |
| `hhs_ohrp_coded_private_information_guidance_2018` | U.S. Department of Health and Human Services, Office for Human Research Protections | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0791; locator-level reliance only, not source-preservation closure` | 2026-12-15 | 1 |
| `hhs_ohrp_continuing_review_guidance_2010` | U.S. Department of Health and Human Services, Office for Human Research Protections | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0793; locator-level reliance only, not fieldwork authorization, collection, source preservation, or closure` | 2026-12-15 | 1 |
| `hhs_ohrp_incident_reporting_guidance_2022` | U.S. Department of Health and Human Services, Office for Human Research Protections | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0793; locator-level reliance only, not fieldwork authorization, collection, source preservation, or closure` | 2026-12-15 | 1 |
| `hhs_ohrp_unanticipated_problems_guidance_2007` | U.S. Department of Health and Human Services, Office for Human Research Protections | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0793; locator-level reliance only, not fieldwork authorization, collection, source preservation, or closure` | 2026-12-15 | 1 |
| `hhs_oig_missing_foster_care_ncic_2023` | HHS Office of Inspector General | 2026-06-13 | `resolved_or_indexed_during_rev0750_child_welfare_continuity_pass` | 2026-12-10 | 5 |
| `hhs_oig_nursing_home_emergency_preparedness_2023` | HHS Office of Inspector General | 2026-06-13 | `resolved_or_indexed_during_rev0752_long_term_care_continuity_pass` | 2026-12-10 | 5 |
| `hhs_oig_nursing_home_sff_2025` | HHS Office of Inspector General | 2026-06-13 | `resolved_or_indexed_during_rev0752_long_term_care_continuity_pass` | 2026-08-12 | 5 |
| `hhs_oig_psychotropic_medication_foster_care_2026` | HHS Office of Inspector General | 2026-06-13 | `resolved_or_indexed_during_rev0750_child_welfare_continuity_pass` | 2026-12-10 | 5 |
| `hmrc_annual_report_onelogin_2025` | HM Revenue & Customs / GOV.UK | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-10-15 | 6 |
| `hrlc_prygodicz_fca_2021` | Human Rights Law Centre | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-12-14 | 4 |
| `hrw_world_report_2026_haiti` | Human Rights Watch | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-10-15 | 5 |
| `hsgac_2023_mislabeled_as_threat` | U.S. Senate Committee on Homeland Security & Governmental Affairs | 2026-06-10 | `resolved` | 2027-06-10 | 3 |
| `hud_ahar_2025_pit_homelessness` | U.S. Department of Housing and Urban Development / HUD USER | 2026-06-12 | `opened during rev0747 housing-continuity case pass` | 2027-06-12 | 5 |
| `hud_ahar_data_reports_2026` | U.S. Department of Housing and Urban Development / HUD USER | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-09-11 | 5 |
| `ico_dhsc_fdp_foi_2026` | Information Commissioner's Office | 2026-06-17 | `official_ico_decision_notice_page_opened_during_rev0774` | 2026-10-15 | 4 |
| `ico_ice360_case_creation_atrs` | Cabinet Office / Department for Science, Innovation and Technology / Government Digital Service | 2026-06-17 | `govuk_atrs_record_resolved` | 2026-08-16 | 7 |
| `illinois_court_based_rental_assistance_2026` | Illinois Housing Development Authority | 2026-06-12 | `rechecked during rev0747 housing-continuity case pass` | 2026-09-10 | 6 |
| `imo_port_state_control` | International Maritime Organization | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2027-06-17 | 4 |
| `india_aadhaar_authentication_offline_verification_2025` | Unique Identification Authority of India | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-12-07 | 4 |
| `india_aadhaar_good_governance_rules_2025` | Unique Identification Authority of India | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-12-07 | 4 |
| `india_digilocker_faq` | DigiLocker / Ministry of Electronics & IT | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-09-08 | 5 |
| `india_digilocker_home` | DigiLocker / Ministry of Electronics & IT | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-09-08 | 5 |
| `india_digilocker_requesters` | DigiLocker / Ministry of Electronics & IT | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-09-08 | 4 |
| `india_dpdp_act_2023` | Ministry of Electronics and Information Technology | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-12-07 | 4 |
| `india_ganga_yamuna_downtoearth_stay_2017` | Down To Earth | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2027-06-17 | 4 |
| `india_ganga_yamuna_ecojurisprudence` | Eco Jurisprudence Monitor | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-12-14 | 4 |
| `india_ganga_yamuna_elaw_salim` | Environmental Law Alliance Worldwide | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2027-06-17 | 6 |
| `india_uidai_regulations_2026` | Unique Identification Authority of India | 2026-06-10 | `official source indexed / opened during rev0743 source-language pass` | 2026-09-08 | 5 |
| `interoperable_europe_act_eurlex` | EUR-Lex / European Union | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 8 |
| `interoperable_europe_assessment_guidelines` | Interoperable Europe Portal / European Commission | 2026-06-17 | `interoperable_europe_guidelines_page_resolved_multilingual_download_routes_present` | 2026-09-15 | 15 |
| `interoperable_europe_assessments_mandatory` | Interoperable Europe Portal / European Commission | 2026-06-17 | `resolved_official_interoperable_europe_mandatory_assessments_page_during_rev0769_web_review` | 2026-08-01 | 7 |
| `interoperable_europe_guidelines_chapter1` | Interoperable Europe Portal / European Commission | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 8 |
| `interoperable_europe_guidelines_chapter2` | Interoperable Europe Portal / European Commission | 2026-06-17 | `interoperable_europe_chapter2_page_resolved` | 2026-09-15 | 7 |
| `interoperable_europe_two_years` | Interoperable Europe Portal / European Commission | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 6 |
| `irs_child_tax_credit_2026` | Internal Revenue Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `irs_create_account_idme` | Internal Revenue Service | 2026-06-17 | `irs_account_creation_guidance_resolved_with_idme_and_alternative_access_notes` | 2026-08-16 | 7 |
| `irs_eitc_2026` | Internal Revenue Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `irs_eitc_tables_2025` | Internal Revenue Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `irs_erc_faq_2026` | Internal Revenue Service | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-09-15 | 6 |
| `irs_erc_main_page` | Internal Revenue Service | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 3 |
| `irs_filing_season_statistics_2026` | Internal Revenue Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `irs_filing_season_week_april_17_2026` | Internal Revenue Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 6 |
| `irs_free_file_options_2026` | Internal Revenue Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `irs_free_file_program_2026` | Internal Revenue Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `irs_id_theft_victim_assistance_2026` | Internal Revenue Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `irs_ip_pin_2026` | Internal Revenue Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `irs_itin_apply_2026` | Internal Revenue Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `irs_itin_renew_2025` | Internal Revenue Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `irs_online_account_individuals` | Internal Revenue Service | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-08-01 | 4 |
| `irs_power_of_attorney_authorizations` | Internal Revenue Service | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-09-15 | 6 |
| `irs_refundable_tax_credits_2026` | Internal Revenue Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `irs_refunds_wheres_my_refund_2026` | Internal Revenue Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 6 |
| `irs_submit_poa_tia_authorizations` | Internal Revenue Service | 2026-06-17 | `official_irs_page_opened_during_rev0772_direct_refresh` | 2027-06-17 | 4 |
| `irs_tax_pro_account_2026` | Internal Revenue Service | 2026-06-17 | `official_irs_page_indexed_during_rev0772_direct_refresh` | 2027-06-17 | 4 |
| `irs_vita_tce_free_tax_prep_2026` | Internal Revenue Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `justice_fulton_jail_findings_2024` | U.S. Department of Justice | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-12-10 | 5 |
| `justice_georgia_prisons_findings_2024` | U.S. Department of Justice, U.S. Attorney’s Office for the Northern District of Georgia | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-12-10 | 5 |
| `kff_medicaid_unwinding_tracker_2026` | KFF | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2026-08-09 | 7 |
| `la_city_controller_interim_housing_audit` | Los Angeles City Controller | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 9 |
| `la_city_controller_pathways_audit` | Los Angeles City Controller | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 9 |
| `la_county_auditor_lahsa_finance_contracts_2024` | County of Los Angeles Department of Auditor-Controller | 2026-06-17 | `official_pdf_route_identified_but_quote_limited` | 2026-10-15 | 10 |
| `la_county_dh_page` | Los Angeles County Chief Executive Office | 2026-06-17 | `la_county_department_on_homelessness_page_resolved` | 2026-09-15 | 10 |
| `la_county_hsh_director_2025` | LA County Homeless Services & Housing | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-09-15 | 9 |
| `la_county_lahsa_jpa_presentation` | County and City of Los Angeles / Office of the County Counsel | 2026-06-17 | `la_county_lahsa_jpa_presentation_indexed_after_direct_open_limit` | 2026-12-14 | 11 |
| `lahsa_about` | Los Angeles Homeless Services Authority | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-09-15 | 9 |
| `lahsa_audit_response_2024` | Los Angeles Homeless Services Authority | 2026-06-17 | `lahsa_audit_response_page_resolved` | 2026-10-15 | 8 |
| `lahsa_budget` | Los Angeles Homeless Services Authority | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-09-15 | 9 |
| `lifeline_988_state_monthly_reports_2026` | 988 Suicide & Crisis Lifeline | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 5 |
| `lifeline_support_recertify_2026` | Lifeline Support / Universal Service Administrative Company | 2026-06-13 | `resolved_or_indexed_during_rev0758_broadband_connectivity_continuity_pass` | 2026-07-13 | 5 |
| `linz_taranaki_maunga_registration_guideline` | Land Information New Zealand | 2026-06-17 | `official_linz_registration_guideline_route_resolved_during_rev0774` | 2026-08-01 | 5 |
| `loc_web_archiving_overview` | Library of Congress | 2026-06-18 | `current_direct_review_section_locator_no_snapshot` | 2027-06-18 | 2 |
| `logingov_ial2_compliant_service_2024` | Login.gov | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 4 |
| `logingov_ial2_right_for_you_2025` | Login.gov | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 4 |
| `logingov_roadmap_update_2024` | Login.gov | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 4 |
| `logingov_rules_of_use_identity_proofing` | Login.gov | 2026-06-17 | `logingov_rules_of_use_page_resolved` | 2026-09-15 | 5 |
| `london_assembly_scrutiny` | London City Hall / London Assembly | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 6 |
| `london_travelwatch_complaints` | London TravelWatch | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 8 |
| `markup_nyc_chatbot_illegal_advice_2024` | The Markup | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2027-06-17 | 10 |
| `mayor_transport_strategy` | London City Hall / Greater London Authority | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 3 |
| `medicaid_dec2025_eligibility_snapshot` | Centers for Medicare & Medicaid Services / Medicaid.gov | 2026-06-17 | `cms_pdf_resolved_title_date_and_key_findings` | 2026-08-16 | 9 |
| `medicaid_exparte_renewal_cib_2024` | Centers for Medicare & Medicaid Services / Medicaid.gov | 2026-06-17 | `cms_informational_bulletin_pdf_resolved` | 2026-12-14 | 7 |
| `medicaid_hcbs_quality_measure_set_2026` | Centers for Medicare & Medicaid Services / Medicaid.gov | 2026-06-13 | `resolved_or_indexed_during_rev0752_long_term_care_continuity_pass` | 2026-08-12 | 5 |
| `medicaid_unwinding_archived_operations_2024` | Centers for Medicare & Medicaid Services / Medicaid.gov | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2027-06-17 | 4 |
| `medicaid_unwinding_data_definitions_2024` | Centers for Medicare & Medicaid Services / Medicaid.gov | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 6 |
| `medicaid_unwinding_longterm_strategies_cib_2024` | Centers for Medicare & Medicaid Services / Medicaid.gov | 2026-06-17 | `official_pdf_opened_and_screenshot_during_rev0772_direct_refresh` | 2026-09-15 | 5 |
| `medicaidgov_renewal_strategies_tools` | Medicaid.gov | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2026-09-08 | 3 |
| `medicare_appeals_forms` | Medicare.gov | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2027-06-17 | 4 |
| `medicare_extra_help_drug_costs` | Medicare.gov | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2026-09-08 | 5 |
| `medicare_part_d_appeals_drug_plans` | Medicare.gov | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2026-09-08 | 5 |
| `michigan_detroit_frc` | Michigan Department of Treasury | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 7 |
| `michigan_detroit_frc_2025_city_resolutions` | Michigan Department of Treasury | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-09-15 | 0 |
| `michigan_detroit_frc_2026_city_resolutions` | Michigan Department of Treasury | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-10-15 | 4 |
| `michigan_detroit_frc_minutes_2026_04_27` | Michigan Department of Treasury | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 7 |
| `michigan_frc_city_meeting_packet_2024_06_24` | Detroit Financial Review Commission / Michigan Department of Treasury | 2026-06-17 | `official_michigan_frc_meeting_page_and_packet_opened_during_rev0774` | 2026-09-15 | 3 |
| `michigan_frc_resolution_2025_01` | Detroit Financial Review Commission / Michigan Department of Treasury | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 6 |
| `michigan_frc_resolution_2025_02` | Detroit Financial Review Commission / Michigan Department of Treasury | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 7 |
| `mrsc_local_government_ai_resources_2026` | Municipal Research and Services Center | 2026-06-10 | `resolved` | 2026-10-08 | 6 |
| `mwra_board_documents` | Massachusetts Water Resources Authority | 2026-06-17 | `official_mwra_board_documents_page_opened_with_2026_meeting_materials_during_rev0774` | 2026-09-15 | 8 |
| `mwra_business_plan` | Massachusetts Water Resources Authority | 2026-06-17 | `official_mwra_business_plan_page_opened_and_board_route_captured_during_rev0774` | 2026-09-15 | 8 |
| `mwra_customer_communities` | Massachusetts Water Resources Authority | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 6 |
| `mwra_governance_management` | Massachusetts Water Resources Authority | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 6 |
| `mwra_investor_info` | Massachusetts Water Resources Authority | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `mwra_public_records` | Massachusetts Water Resources Authority | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-09-15 | 2 |
| `mwra_rates_finances` | Massachusetts Water Resources Authority | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `mwra_transparency` | Massachusetts Water Resources Authority | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `nao_progress_implementing_universal_credit_2024` | National Audit Office | 2026-06-17 | `official_nao_report_page_and_pdf_opened_with_key_facts_captured_during_rev0774` | 2026-10-15 | 5 |
| `nara_managing_web_records_background` | National Archives and Records Administration | 2026-06-18 | `current_direct_review_section_locator_no_snapshot` | 2027-06-18 | 2 |
| `nara_records_scheduling_guidance` | National Archives and Records Administration | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0793; locator-level reliance only, not fieldwork authorization, collection, source preservation, or closure` | 2026-12-15 | 1 |
| `national_911_annual_report_2023` | National 911 Program / 911.gov | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 8 |
| `national_911_ng911_progress_2025` | National 911 Program / 911.gov | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 8 |
| `national_911_profile_database_2025` | National 911 Program / 911.gov | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 8 |
| `nbc_california_ng911_records_2026` | NBC Bay Area | 2026-06-18 | `NBC_Bay_Area_project_records_story_resolved_during_rev0781` | 2026-07-18 | 3 |
| `nces_students_with_disabilities_2024` | National Center for Education Statistics | 2026-06-13 | `resolved_or_indexed_during_rev0753_special_education_continuity_pass` | 2026-09-11 | 5 |
| `nclc_utility_service_extreme_heat_report_2024` | National Consumer Law Center | 2026-06-12 | `opened during rev0746 cloudtainer deep-read audit` | 2027-06-12 | 4 |
| `ncsc_ai_state_courts_resources` | National Center for State Courts | 2026-06-10 | `resolved` | 2026-10-08 | 5 |
| `ncsl_2025_ai_legislation` | National Conference of State Legislatures | 2026-06-10 | `resolved` | 2026-09-08 | 5 |
| `nemsis_research_dataset_2026` | NEMSIS Technical Assistance Center | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 5 |
| `nhs_england_synnovis_cyber_incident_2025` | NHS England | 2026-06-13 | `direct_page_opened` | 2026-09-11 | 6 |
| `nhs_fdp_centre_excellence` | NHS England | 2026-06-17 | `official_nhs_england_page_indexed_during_rev0772_direct_refresh` | 2026-07-17 | 3 |
| `nhs_fdp_contract_explainer` | NHS England | 2026-06-17 | `nhs_england_fdp_contract_explainer_resolved` | 2026-09-15 | 7 |
| `nhs_fdp_ig_framework` | NHS England | 2026-06-17 | `nhs_fdp_information_governance_framework_page_resolved` | 2026-09-15 | 5 |
| `nhs_fdp_privacy_notice` | NHS England | 2026-06-17 | `nhs_england_fdp_privacy_notice_resolved` | 2026-09-15 | 7 |
| `nhs_fdp_uptake_benefits` | NHS England | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-10-15 | 6 |
| `nist_ai_rmf` | National Institute of Standards and Technology | 2026-06-17 | `nist_ai_rmf_page_resolved_with_2026_profile_update_signal` | 2026-09-15 | 11 |
| `nist_ir_8053_deidentification` | National Institute of Standards and Technology | 2026-06-18 | `locator_level_public_source_resolved_for_release_controls; no snapshot or private data captured` | 2026-12-15 | 1 |
| `nist_privacy_framework` | National Institute of Standards and Technology | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0790_sampling_gate_pass; locator-level reliance only` | 2026-12-15 | 1 |
| `nist_sp800_63_4_digital_identity` | National Institute of Standards and Technology | 2026-06-10 | `resolved` | 2027-06-10 | 9 |
| `nist_sp_800_122_pii_confidentiality` | National Institute of Standards and Technology | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0791; locator-level reliance only, not source-preservation closure` | 2026-12-15 | 2 |
| `nist_sp_800_188_deidentifying_government_datasets` | National Institute of Standards and Technology | 2026-06-18 | `locator_level_public_source_resolved_for_release_controls; no snapshot or private data captured` | 2026-12-15 | 1 |
| `nist_sp_800_53r5_security_privacy_controls` | National Institute of Standards and Technology | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0792; locator-level reliance only, not collection authorization or source-preservation closure` | 2026-12-15 | 2 |
| `nist_ssdf_sp_800_218` | National Institute of Standards and Technology | 2026-06-13 | `direct_page_opened` | 2026-12-10 | 6 |
| `nlihc_rental_assistance_dashboard` | National Low Income Housing Coalition | 2026-06-12 | `rechecked during rev0747 housing-continuity case pass` | 2026-08-11 | 6 |
| `nta_erc_claim_period_closed_2025` | Taxpayer Advocate Service | 2026-06-17 | `tas_erc_claim_period_closed_page_resolved` | 2026-10-15 | 4 |
| `nta_erc_form907_streamlined_process_2026` | Taxpayer Advocate Service | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-09-15 | 6 |
| `ntia_bead_program_2026` | National Telecommunications and Information Administration | 2026-06-13 | `resolved_or_indexed_during_rev0758_broadband_connectivity_continuity_pass` | 2026-07-13 | 5 |
| `ntia_bead_progress_dashboard_2026` | National Telecommunications and Information Administration | 2026-06-13 | `resolved_or_indexed_during_rev0758_broadband_connectivity_continuity_pass` | 2026-07-13 | 5 |
| `ny_psc_extreme_heat_protections_2026` | New York State Department of Public Service | 2026-06-12 | `opened during rev0746 cloudtainer deep-read audit` | 2026-12-09 | 1 |
| `nyc_algorithmic_tools_open_data` | NYC Open Data | 2026-06-10 | `resolved` | 2026-09-08 | 7 |
| `nyc_algorithmic_tools_report_2025` | New York City Office of Technology and Innovation | 2026-06-10 | `resolved` | 2026-10-08 | 16 |
| `nyc_board_elections_home_2026` | New York City Board of Elections | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-09-11 | 5 |
| `nyc_chatbot_beta_ended` | City of New York | 2026-06-17 | `nyc_beta_ended_page_resolved_and_points_users_to_primary_nyc_gov_portal` | 2026-08-16 | 13 |
| `nyc_comptroller_evictions_representation_2025` | Office of the New York City Comptroller | 2026-06-12 | `rechecked during rev0747 housing-continuity case pass` | 2026-12-09 | 12 |
| `nyc_comptroller_mycity_audit_2025` | New York City Comptroller | 2026-06-17 | `nyc_comptroller_audit_page_resolved` | 2026-12-14 | 17 |
| `nyc_mayor_ai_action_plan_2023` | City of New York Mayor’s Office | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-10-15 | 9 |
| `nyc_mycity_business_faq_2026` | NYC Business / City of New York | 2026-06-18 | `primary_or_official_page_resolved_during_rev0783_web_review` | 2026-09-16 | 3 |
| `nyc_mycity_landing_2026` | City of New York | 2026-06-18 | `primary_or_official_page_resolved_during_rev0783_web_review` | 2026-09-16 | 3 |
| `nyc_ocj_annual_report_2025` | New York City Office of Civil Justice | 2026-06-18 | `opened_or_passage_located_during_rev0788; supports source-boundary receipt only, not field validation` | 2026-09-16 | 1 |
| `nyc_office_algorithmic_accountability_charter` | American Legal Publishing / New York City Charter | 2026-06-10 | `resolved` | 2026-12-07 | 5 |
| `nyc_oti_mycity_progress_2025` | New York City Office of Technology and Innovation | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-10-15 | 9 |
| `nyc_oti_mycity_progress_updates_2025` | New York City Office of Technology and Innovation | 2026-06-18 | `primary_or_official_page_resolved_during_rev0783_web_review` | 2026-09-16 | 3 |
| `nyc_right_to_counsel_mayors_peu` | NYC Mayor's Public Engagement Unit | 2026-06-12 | `identified during rev0747 housing-continuity case pass` | 2026-10-10 | 5 |
| `nyc_votes_2026_election_calendar` | NYC Votes | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-09-11 | 5 |
| `nz_taranaki_maunga_act_2025` | New Zealand Legislation | 2026-06-17 | `legal_text_route_identified_but_quote_limited` | 2026-08-01 | 7 |
| `nz_taranaki_maunga_settlement` | Te Tari Whakatau / Office for Māori Crown Relations | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 6 |
| `nz_te_awa_tupua_act_2017` | New Zealand Legislation | 2026-06-17 | `legal_text_route_identified_but_quote_limited` | 2026-08-01 | 7 |
| `oag_canada_arrivecan_media_2024` | Office of the Auditor General of Canada | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-09-15 | 3 |
| `oag_canada_arrivecan_report_2024` | Office of the Auditor General of Canada | 2026-06-17 | `auditor_general_arrivecan_report_page_resolved` | 2026-12-14 | 9 |
| `oaic_adm_foi_report_2026` | Office of the Australian Information Commissioner | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 6 |
| `occ_consumer_complaints_2026` | Office of the Comptroller of the Currency | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 6 |
| `occ_consumer_protection_2026` | Office of the Comptroller of the Currency | 2026-06-13 | `resolved_or_indexed_during_rev0762_consumer_finance_continuity_pass` | 2026-07-13 | 5 |
| `oecd_digital_government_outlook_2026_services` | OECD | 2026-06-18 | `resolved` | 2027-06-18 | 2 |
| `oecd_fiscal_federalism_2022` | OECD | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2027-06-17 | 5 |
| `oecd_governing_city` | OECD | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2027-06-17 | 12 |
| `oecd_government_at_a_glance_2025_services` | OECD | 2026-06-17 | `resolved` | 2027-06-17 | 1 |
| `oecd_hdp_nexus_recommendation` | OECD Legal Instruments | 2026-06-17 | `official_oecd_legal_instrument_route_resolved_during_rev0774` | 2026-09-15 | 3 |
| `oecd_human_centred_services_recommendation_2024` | OECD | 2026-06-18 | `resolved` | 2027-06-18 | 2 |
| `oecd_intermunicipal_shared_services_lithuania` | OECD | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2027-06-17 | 9 |
| `oecd_multilevel_governance` | OECD | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2027-06-17 | 7 |
| `oecd_responsibility_assignment` | OECD | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2027-06-17 | 7 |
| `oecd_states_fragility_2025` | OECD | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-09-15 | 2 |
| `oecd_subnational_fiscal_rules` | OECD | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `oecd_water_governance_principles` | OECD | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-08-01 | 3 |
| `ofsted_ai_writing_assistant_social_care_atrs` | Cabinet Office / Department for Science, Innovation and Technology / Government Digital Service | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-07-17 | 2 |
| `ogp_australia_adm_transparency` | Open Government Partnership | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 5 |
| `ohchr_fpic_indigenous_peoples` | Office of the United Nations High Commissioner for Human Rights | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2027-06-17 | 6 |
| `ohchr_haiti_gang_violence_2026` | UN Human Rights Office (OHCHR) | 2026-06-17 | `official_route_identified_but_current_context_limited` | 2026-07-17 | 6 |
| `ohchr_ilo_convention_169` | Office of the United Nations High Commissioner for Human Rights | 2026-06-17 | `official_ohchr_ilo_169_instrument_route_resolved_during_rev0774` | 2026-09-15 | 3 |
| `omb_2023_iqa_faq` | Office of Management and Budget | 2026-06-18 | `resolved_during_rev0795_correction_control_pass` | 2026-12-15 | 1 |
| `omb_2025_federal_ai_inventory` | Office of Management and Budget / GitHub | 2026-06-10 | `resolved` | 2026-09-08 | 10 |
| `omb_a11_section_280_2025` | Office of Management and Budget | 2026-06-18 | `resolved_to_official_pdf_and_relevant_page_screenshot` | 2026-09-16 | 4 |
| `omb_a11_section_290_2025` | Office of Management and Budget | 2026-06-18 | `locator_level_public_source_resolved_for_closure_dossier_controls; no snapshot or private data captured` | 2026-12-15 | 2 |
| `omb_circular_a123_2026` | Office of Management and Budget | 2026-06-18 | `locator_level_public_source_resolved_for_redress_verification_controls; no snapshot or private data captured` | 2026-12-15 | 3 |
| `omb_circular_a_108_privacy_act` | Office of Management and Budget | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0792; locator-level reliance only, not collection authorization or source-preservation closure` | 2026-12-15 | 1 |
| `omb_information_quality_guidelines_2002` | Office of Management and Budget / Federal Register | 2026-06-18 | `resolved_during_rev0795_correction_control_pass` | 2026-12-15 | 2 |
| `omb_m_01_05_interagency_personal_data_sharing` | Office of Management and Budget | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0792; locator-level reliance only, not collection authorization or source-preservation closure` | 2026-12-15 | 1 |
| `omb_m_14_06_administrative_data_statistical_purposes` | Office of Management and Budget | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0792; locator-level reliance only, not collection authorization or source-preservation closure` | 2026-12-15 | 1 |
| `omb_m_16_21_federal_source_code_policy` | Office of Management and Budget / White House Archives | 2026-06-18 | `official_pdf_opened_and_pages_screenshotted_during_rev0799` | 2027-06-18 | 0 |
| `omb_m_17_12_pii_breach_response` | Office of Management and Budget | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0793; locator-level reliance only, not fieldwork authorization, collection, source preservation, or closure` | 2026-12-15 | 1 |
| `omb_m_19_15_information_quality` | Office of Management and Budget | 2026-06-18 | `resolved_during_rev0795_correction_control_pass` | 2026-12-15 | 2 |
| `omb_m_19_23_evidence_act` | Office of Management and Budget | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0790_sampling_gate_pass; locator-level reliance only` | 2027-06-18 | 2 |
| `omb_m_20_12_program_evaluation_standards` | Office of Management and Budget | 2026-06-18 | `locator_level_public_source_resolved; no snapshot or private data captured` | 2027-06-18 | 1 |
| `omb_m_21_27_learning_agendas_evaluation_plans` | Office of Management and Budget | 2026-06-18 | `locator_level_public_source_resolved; no snapshot or private data captured` | 2027-06-18 | 1 |
| `omb_m_22_10_public_benefits_pra` | Office of Management and Budget | 2026-06-18 | `resolved_to_official_pdf_and_relevant_page_screenshot` | 2026-09-16 | 2 |
| `omb_m_25_21_ai_use` | Office of Management and Budget | 2026-06-10 | `resolved` | 2026-12-07 | 8 |
| `omb_m_25_22_ai_acquisition` | Office of Management and Budget | 2026-06-17 | `official_white_house_pdf_opened_and_screenshot_captured_during_rev0774` | 2026-09-15 | 4 |
| `omb_m_26_04_llm_transparency` | Office of Management and Budget | 2026-06-17 | `official_white_house_pdf_opened_and_screenshot_captured_during_rev0774` | 2026-07-17 | 3 |
| `omb_m_26_05_software_hardware_security` | Office of Management and Budget | 2026-06-13 | `direct_pdf_opened` | 2026-08-12 | 6 |
| `omb_statistical_policy_directive_4` | Office of Management and Budget / Federal Register | 2026-06-18 | `locator_level_public_source_resolved_for_release_controls; no snapshot or private data captured` | 2026-12-15 | 1 |
| `omb_statistical_policy_directive_4_addendum_2016` | Office of Management and Budget / Federal Register | 2026-06-18 | `resolved_during_rev0795_correction_control_pass` | 2026-12-15 | 1 |
| `omb_statistical_surveys_2006` | Office of Management and Budget / Federal Committee on Statistical Methodology | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0790_sampling_gate_pass; locator-level reliance only` | 2027-06-18 | 2 |
| `opensource_guide_leadership_and_governance` | Open Source Guides | 2026-06-18 | `resolved_during_rev0799` | 2026-12-15 | 0 |
| `opo_arrivecan_procurement_review_2024` | Office of the Procurement Ombud | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-10-15 | 4 |
| `parismou_banning` | Paris Memorandum of Understanding on Port State Control | 2026-06-17 | `official_parismou_procedure_page_indexed_during_rev0772_direct_refresh` | 2027-06-17 | 4 |
| `parismou_current_bannings` | Paris Memorandum of Understanding on Port State Control | 2026-06-17 | `official_parismou_current_list_indexed_during_rev0772_direct_refresh` | 2026-07-17 | 3 |
| `parismou_current_detentions` | Paris Memorandum of Understanding on Port State Control | 2026-06-17 | `official_parismou_current_list_indexed_during_rev0772_direct_refresh` | 2026-07-17 | 3 |
| `parismou_memorandum` | Paris Memorandum of Understanding on Port State Control | 2026-06-17 | `official_parismou_procedure_page_indexed_during_rev0772_direct_refresh` | 2027-06-17 | 4 |
| `parismou_psc_inspections` | Paris Memorandum of Understanding on Port State Control | 2026-06-17 | `paris_mou_inspection_page_indexed_primary_pdf_route_available` | 2026-12-14 | 8 |
| `pclob_2025_terrorist_watchlist_report` | Privacy and Civil Liberties Oversight Board | 2026-06-10 | `resolved` | 2027-06-10 | 4 |
| `pge_self_identified_vulnerable_customer_program` | Pacific Gas & Electric | 2026-06-10 | `official or authoritative source indexed / opened during rev0745 climate-utility continuity pass` | 2026-10-08 | 4 |
| `plos_medicine_power_outages_hospitalizations_2026` | PLOS Medicine | 2026-06-12 | `opened during rev0746 cloudtainer deep-read audit` | 2027-06-12 | 6 |
| `psac_phoenix_decade_2026` | Public Service Alliance of Canada | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-08-01 | 4 |
| `psfa_fraud_risk_assessment_accelerator_atrs` | Cabinet Office / Department for Science, Innovation and Technology / Government Digital Service | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-07-17 | 2 |
| `rand_medicaid_unwinding_buprenorphine_2025` | RAND | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2027-06-10 | 4 |
| `readygov_power_outages_medical_devices` | Ready.gov | 2026-06-10 | `official or authoritative source indexed / opened during rev0745 climate-utility continuity pass` | 2026-12-07 | 4 |
| `reliefweb_hct_haiti_gsf_key_messages_2025` | ReliefWeb / Humanitarian Country Team | 2026-06-17 | `reliefweb_hct_gsf_key_messages_route_resolved_during_rev0774` | 2026-09-15 | 4 |
| `reproducible_builds_source_date_epoch` | Reproducible Builds project | 2026-06-18 | `resolved` | 2027-06-18 | 2 |
| `reuse_specification_3_3` | REUSE / Free Software Foundation Europe | 2026-06-18 | `resolved_during_rev0799` | 2026-12-15 | 0 |
| `robodebt_pmc_government_response` | Department of the Prime Minister and Cabinet | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2027-06-17 | 5 |
| `robodebt_royal_commission_report` | Royal Commission into the Robodebt Scheme | 2026-06-17 | `royal_commission_report_page_resolved` | 2027-06-17 | 7 |
| `samhsa_988_fact_sheet_2026` | Substance Abuse and Mental Health Services Administration | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 5 |
| `samhsa_988_performance_metrics_2026` | Substance Abuse and Mental Health Services Administration | 2026-06-13 | `resolved_or_indexed_during_rev0756_emergency_response_continuity_pass` | 2026-07-28 | 5 |
| `samhsa_state_prisons_moud_guidelines_2025` | Substance Abuse and Mental Health Services Administration | 2026-06-13 | `resolved_or_indexed_during_rev0751_custody_reentry_pass` | 2026-12-10 | 5 |
| `sba_2026_ai_inventory` | U.S. Small Business Administration | 2026-06-10 | `resolved` | 2026-09-08 | 4 |
| `sce_medical_baseline_allowance` | Southern California Edison / Prepare for Power Down | 2026-06-10 | `official or authoritative source indexed / opened during rev0745 climate-utility continuity pass` | 2026-10-08 | 4 |
| `security_council_report_haiti_apr_2026` | Security Council Report | 2026-06-17 | `security_council_report_haiti_april_2026_route_resolved_during_rev0774` | 2026-09-15 | 4 |
| `services_australia_new_robodebt_settlement_2026` | Services Australia | 2026-06-17 | `official_services_australia_page_opened_during_rev0772_direct_refresh` | 2026-12-14 | 4 |
| `services_australia_robodebt_refunds` | Services Australia | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-08-01 | 4 |
| `shadac_insurance_coverage_transitions_medicaid_unwinding_2025` | SHADAC | 2026-06-10 | `official or authoritative source indexed / opened during rev0744 health-coverage transition pass` | 2027-06-10 | 4 |
| `sites_idea_annual_reports_2025` | U.S. Department of Education / IDEA | 2026-06-13 | `resolved_or_indexed_during_rev0753_special_education_continuity_pass` | 2026-09-11 | 5 |
| `sites_idea_data_page_2026` | U.S. Department of Education / IDEA | 2026-06-13 | `resolved_or_indexed_during_rev0753_special_education_continuity_pass` | 2026-09-11 | 5 |
| `social_security_scotland_acting_on_behalf` | mygov.scot / Social Security Scotland | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-10-15 | 6 |
| `spain_mar_menor_ecojurisprudence_2026` | Eco Jurisprudence Monitor | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-12-14 | 4 |
| `spain_mar_menor_law_19_2022_boe` | Agencia Estatal Boletín Oficial del Estado | 2026-06-17 | `boe_html_law_19_2022_resolved` | 2027-06-17 | 8 |
| `spain_mar_menor_rd_90_2025_boe` | Agencia Estatal Boletín Oficial del Estado | 2026-06-17 | `boe_html_royal_decree_90_2025_resolved` | 2027-06-17 | 7 |
| `spain_mar_menor_tc_142_2024_boe` | Agencia Estatal Boletín Oficial del Estado | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-10-15 | 5 |
| `ssa_representative_payee_guide` | Social Security Administration | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 6 |
| `ssa_representative_payee_misuse_liability_cfr` | Social Security Administration | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 6 |
| `ssa_representative_payee_pa_reviews` | Social Security Administration | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-12-14 | 6 |
| `ssa_representative_payee_program` | Social Security Administration | 2026-06-17 | `ssa_representative_payee_program_page_resolved` | 2026-09-15 | 7 |
| `statspolicy_cipsea_data_access_sharing` | U.S. Statistical Policy / Office of Management and Budget | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0792; locator-level reliance only, not collection authorization or source-preservation closure` | 2026-12-15 | 1 |
| `statspolicy_standard_application_process_resources` | U.S. Statistical Policy / Office of Management and Budget | 2026-06-18 | `public source opened_or_lines_reviewed_during_rev0792; locator-level reliance only, not collection authorization or source-preservation closure` | 2026-12-15 | 1 |
| `tas_2025_annual_report_press_2026` | Taxpayer Advocate Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `tas_bfs_offsets_non_tax_debts_2026` | Taxpayer Advocate Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `tas_direct_deposit_changes_2026` | Taxpayer Advocate Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `tas_held_stopped_refunds_2026` | Taxpayer Advocate Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `tas_identity_verification_tax_return_2026` | Taxpayer Advocate Service | 2026-06-17 | `tas_identity_verification_tax_return_page_resolved` | 2026-09-15 | 4 |
| `te_kopuka_te_awa_tupua` | Te Kōpuka | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 4 |
| `te_pou_tupua_te_awa_tupua` | Te Pou Tupua | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2027-06-17 | 5 |
| `tfl_annual_report` | Transport for London | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-09-15 | 2 |
| `tfl_audit_assurance` | Transport for London | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-09-15 | 2 |
| `tfl_business_plan_budget` | Transport for London | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-09-15 | 3 |
| `tfl_complaint_further` | Transport for London | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `tfl_governance` | Transport for London | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 8 |
| `treasury_emergency_rental_assistance_program_2026` | U.S. Department of the Treasury | 2026-06-12 | `rechecked during rev0747 housing-continuity case pass` | 2026-12-09 | 7 |
| `treasury_offset_faqs_public_2026` | Bureau of the Fiscal Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 5 |
| `treasury_offset_program_2026` | Bureau of the Fiscal Service | 2026-06-13 | `resolved_or_indexed_during_rev0761_tax_refund_continuity_pass` | 2026-06-27 | 6 |
| `tsa_dhs_trip_redress_program` | Transportation Security Administration | 2026-06-10 | `resolved` | 2026-10-08 | 2 |
| `uk_ai_civil_service_productivity_trial_2025` | Department for Science, Innovation and Technology | 2026-06-17 | `govuk_ai_civil_service_productivity_trial_resolved` | 2026-12-14 | 4 |
| `uk_ai_playbook_2025` | Government Digital Service | 2026-06-17 | `govuk_publication_resolved_with_html_and_pdf_routes` | 2026-09-15 | 17 |
| `uk_algorithmic_transparency_records_hub` | Cabinet Office / Department for Science, Innovation and Technology / Government Digital Service | 2026-06-17 | `govuk_algorithmic_transparency_records_hub_resolved_with_live_record_count_and_filters` | 2026-07-17 | 14 |
| `uk_evisa_account_creation_data_2026` | UK Home Office / GOV.UK | 2026-06-17 | `govuk_evisa_account_creation_data_resolved` | 2026-08-16 | 4 |
| `uk_evisa_commons_library_2025` | House of Commons Library | 2026-06-17 | `commons_library_evisa_briefing_resolved` | 2026-09-15 | 5 |
| `uk_evisa_home_office_factsheet_2024` | Home Office in the media | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 4 |
| `uk_evisa_parliament_written_evidence_the3million_2025` | UK Parliament Committees | 2026-06-17 | `parliament_written_evidence_evisa_resolved` | 2026-12-14 | 5 |
| `uk_evisa_remaining_account_methodology_2026` | UK Home Office / GOV.UK | 2026-06-17 | `govuk_evisa_remaining_account_methodology_resolved` | 2026-09-15 | 4 |
| `uk_evisa_updates_2026` | UK Home Office / GOV.UK | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-08-16 | 7 |
| `uk_evisa_view_prove_guidance_2026` | UK Home Office / GOV.UK | 2026-06-17 | `govuk_evisa_view_prove_guidance_resolved_with_share_code_and_error_routes` | 2026-07-17 | 8 |
| `uk_hansard_fdp_contract_award_2023` | UK Parliament Hansard | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 4 |
| `uk_hansard_fdp_debate_2026` | UK Parliament Hansard | 2026-06-17 | `hansard_nhs_fdp_debate_resolved` | 2026-12-14 | 5 |
| `uk_ibca_community_feedback_jan_mar_2026` | Infected Blood Compensation Authority | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-08-01 | 4 |
| `uk_ibca_stats_may21_2026` | Infected Blood Compensation Authority | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-08-16 | 6 |
| `uk_ibca_support_scheme_transition` | Infected Blood Compensation Authority | 2026-06-17 | `ibca_current_support_payments_page_resolved` | 2026-08-16 | 5 |
| `uk_infected_blood_scheme_design_response_apr2026` | Cabinet Office / GOV.UK | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-08-01 | 4 |
| `uk_infected_blood_scheme_update_2025` | Cabinet Office / GOV.UK | 2026-06-17 | `govuk_infected_blood_compensation_update_resolved` | 2026-09-15 | 5 |
| `uk_postoffice_glo_closure_2026` | Department for Business and Trade / GOV.UK | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 4 |
| `uk_postoffice_horizon_family_redress_2026` | Department for Business and Trade / GOV.UK | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 4 |
| `uk_postoffice_horizon_legal_costs_mar2026` | Department for Business and Trade / GOV.UK | 2026-06-17 | `govuk_postoffice_horizon_legal_costs_mar2026_resolved` | 2026-09-15 | 4 |
| `uk_postoffice_horizon_redress_2026_collection` | Department for Business and Trade / GOV.UK | 2026-06-17 | `official_govuk_collection_opened_during_rev0772_direct_refresh` | 2026-07-17 | 3 |
| `uk_postoffice_horizon_redress_apr2026` | Department for Business and Trade / GOV.UK | 2026-06-17 | `govuk_post_office_horizon_redress_2026_statistics_indexed` | 2026-07-17 | 7 |
| `un_undrip` | United Nations | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2027-06-17 | 6 |
| `undp_universal_dpi_safeguards_framework_v2` | United Nations Development Programme / DPI Safeguards Initiative | 2026-06-18 | `resolved` | 2026-12-15 | 2 |
| `unfpa_haiti_sitrep_jan_mar_2026` | UNFPA Haiti | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 4 |
| `unhabitat_decentralization_services` | UN-Habitat | 2026-06-17 | `official_unhabitat_decentralization_services_route_resolved_during_rev0774` | 2026-09-15 | 8 |
| `unsc_res_2793_2025_unscr` | UNSCR / United Nations Security Council resolution reference | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-10-15 | 6 |
| `unsoh_mandate` | United Nations Support Office in Haiti / UN Mine Action Service portal | 2026-06-17 | `source_key_registry_url_and_official_or_primary_route_reviewed_during_rev0772_direct_refresh` | 2026-12-14 | 4 |
| `us_treasury_fatf` | U.S. Department of the Treasury | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-09-15 | 4 |
| `usac_lifeline_national_verifier_2026` | Universal Service Administrative Company | 2026-06-13 | `resolved_or_indexed_during_rev0758_broadband_connectivity_continuity_pass` | 2026-07-13 | 5 |
| `usac_lifeline_recertification_2026` | Universal Service Administrative Company | 2026-06-13 | `resolved_or_indexed_during_rev0758_broadband_connectivity_continuity_pass` | 2026-07-13 | 5 |
| `usagov_help_with_utility_bills_2026` | USAGov | 2026-06-12 | `opened during rev0746 cloudtainer deep-read audit` | 2026-09-10 | 1 |
| `uscis_address_change_2025` | U.S. Citizenship and Immigration Services | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `uscis_ar11_change_address_2026` | U.S. Citizenship and Immigration Services | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `uscis_asylum_ead_clock_notice_2026` | U.S. Citizenship and Immigration Services | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `uscis_asylum_page_2026` | U.S. Citizenship and Immigration Services | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `uscis_case_status_online_2026` | U.S. Citizenship and Immigration Services | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `uscis_check_case_processing_2026` | U.S. Citizenship and Immigration Services | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `uscis_historic_processing_times_2026` | U.S. Citizenship and Immigration Services | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `uscis_i589_asylum_2026` | U.S. Citizenship and Immigration Services | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `uscis_i765_employment_authorization_2026` | U.S. Citizenship and Immigration Services | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `uscis_save_casecheck_2025` | U.S. Citizenship and Immigration Services | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `uscis_save_program_2026` | U.S. Citizenship and Immigration Services | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `uscis_save_verification_response_time_2026` | U.S. Citizenship and Immigration Services | 2026-06-13 | `resolved_or_indexed_during_rev0760_immigration_status_continuity_pass` | 2026-06-27 | 5 |
| `usda_ers_food_security_key_stats_2026` | USDA Economic Research Service | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `usda_ers_snap_participation_fy2024_2025` | USDA Economic Research Service | 2026-06-13 | `resolved_or_indexed_during_rev0755_food_nutrition_continuity_pass` | 2026-08-12 | 5 |
| `usps_election_mail_2026` | United States Postal Service | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-09-11 | 5 |
| `usps_kit600_2026_2027` | United States Postal Service | 2026-06-13 | `resolved_or_indexed_during_rev0749_election_continuity_pass` | 2026-09-11 | 5 |
| `va_board_veterans_appeals_2026` | Department of Veterans Affairs / Board of Veterans’ Appeals | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-07-13 | 5 |
| `va_community_care_eligibility_2025` | Department of Veterans Affairs | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-07-13 | 5 |
| `va_family_caregiver_assistance_2026` | Department of Veterans Affairs | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-07-13 | 5 |
| `va_gibill_home_2026` | Department of Veterans Affairs / Veterans Benefits Administration | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-07-13 | 5 |
| `va_gibill_rudisill_perkins_2026` | Department of Veterans Affairs / Veterans Benefits Administration | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-07-13 | 5 |
| `va_health_care_about_benefits_2025` | Department of Veterans Affairs | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-07-13 | 5 |
| `va_health_care_eligibility_2026` | Department of Veterans Affairs | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-07-13 | 5 |
| `va_hud_vash_2026` | Department of Veterans Affairs / VA Homeless Programs | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-07-13 | 5 |
| `va_mental_health_get_help_2026` | Department of Veterans Affairs / Mental Health | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-07-13 | 5 |
| `va_pact_act_performance_dashboard_2026` | Department of Veterans Affairs | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-07-13 | 5 |
| `va_vba_claims_backlog_2026` | Department of Veterans Affairs / Veterans Benefits Administration | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-07-13 | 5 |
| `va_vba_detailed_claims_data_2026` | Department of Veterans Affairs / Veterans Benefits Administration | 2026-06-13 | `resolved_or_indexed_during_rev0759_veterans_continuity_pass` | 2026-07-13 | 5 |
| `wdba_atip` | Windsor-Detroit Bridge Authority | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `wdba_bridging_north_america` | Gordie Howe International Bridge / Windsor-Detroit Bridge Authority | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `wdba_corporate_reports` | Windsor-Detroit Bridge Authority | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-09-15 | 2 |
| `wdba_governance` | Windsor-Detroit Bridge Authority | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 3 |
| `wdba_hicc_overview` | Housing, Infrastructure and Communities Canada | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `wdba_mandate_legislation` | Windsor-Detroit Bridge Authority | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 3 |
| `wdba_p3_procurement` | Gordie Howe International Bridge / Windsor-Detroit Bridge Authority | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 3 |
| `who_ihr_amendments_qa` | World Health Organization | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 4 |
| `who_ihr_current_text_2014_2022_2024` | World Health Organization | 2026-06-17 | `official_who_topic_page_opened_during_rev0772_direct_refresh` | 2026-10-15 | 4 |
| `who_ihr_emergency_committees` | World Health Organization | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2026-09-15 | 6 |
| `who_ihr_emergency_committees_qa` | World Health Organization | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-07-17 | 1 |
| `who_ihr_entry_force_2025` | World Health Organization | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-07-17 | 4 |
| `who_ihr_joint_external_evaluation` | World Health Organization | 2026-06-17 | `official_who_jmef_page_indexed_during_rev0772_direct_refresh` | 2026-12-14 | 4 |
| `who_ihr_mef` | World Health Organization | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 0 |
| `who_ihr_national_focal_points` | World Health Organization | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 1 |
| `who_ihr_national_implementation` | World Health Organization | 2026-06-17 | `resolved_or_indexed_during_rev0771_direct_refresh` | 2026-08-01 | 4 |
| `who_ihr_spar` | World Health Organization | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-09-15 | 0 |
| `who_ihr_topic` | World Health Organization | 2026-06-17 | `who_ihr_topic_page_resolved` | 2026-12-14 | 8 |
| `world_bank_decentralization` | World Bank | 2026-06-17 | `source_key_registry_url_or_official_search_result_resolved_during_rev0773_direct_refresh` | 2026-12-14 | 2 |
| `world_bank_fcv_strategy_2020_2025` | World Bank | 2026-06-17 | `world_bank_fcv_strategy_route_resolved_during_rev0774` | 2026-09-15 | 4 |
| `world_bank_metropolitan_governance` | World Bank | 2026-06-17 | `triaged_from_high_dependency_unchecked_queue_during_rev0768; primary/official/reputable source URL or search-result evidence resolved where available; no offline build fetch assumed` | 2027-06-17 | 12 |

## Unclassified source keys

- None.
