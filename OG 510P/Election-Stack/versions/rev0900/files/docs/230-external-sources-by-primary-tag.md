# 230. External sources by primary tag (lockfile IDs, no URLs)

**Track:** Shared


Generated from `evidence/lock/external-sources.toml`. Primary tag = the first element of each entry's `tags[]` list.

Purpose: bounded tag-grouped triage without duplicating the full lockfile. Exhaustive per-ID lookup lives in `evidence/lock/external-sources.toml`; the compact flat view lives in `docs/214`.

| primary tag | total | pinned | unpinned | next review_by | example ids |
|---|---:|---:|---:|---|---|
| ada | 2 | 0 | 2 | 2026-08-09 | `ada_gov_web_mobile_apps_fact_sheet_page`, `ada_voting_and_polling_places_page` |
| adobe | 35 | 0 | 35 | 2026-09-08 | `adobe_acrobat_add_links_pdfs_help_page`, `adobe_acrobat_add_manage_comments_help_page`, `adobe_acrobat_automatically_open_pdfs_help_page`; (+32 more) |
| android | 3 | 0 | 3 | 2026-09-08 | `android_build_web_apps_in_webview_page`, `android_in_app_browsing_embedded_web_page`, `android_use_web_content_within_app_page` |
| apple | 40 | 0 | 40 | 2026-09-08 | `apple_app_store_connect_accessibility_nutrition_labels_page`, `apple_app_store_connect_manage_app_privacy_page`, `apple_app_store_connect_set_developer_name_page`; (+37 more) |
| arizona | 2 | 1 | 1 | 2026-07-25 | `arizona_registering_to_vote_page`, `arizona_tribal_id_document_pdf` |
| audit | 4 | 2 | 2 | 2026-09-08 | `arxiv_more_style_less_work_2012_03371_pdf`, `arxiv_stylish_rla_in_practice_2309_09081_pdf`, `nist_gentle_intro_rla_pdf`; (+1 more) |
| c2pa | 3 | 1 | 2 | 2026-09-08 | `c2pa_content_credentials_spec_2_2_pdf`, `c2pa_content_credentials_spec_2_4_html`, `c2pa_faq_page` |
| california | 7 | 2 | 5 | 2026-07-25 | `california_conservatorship_voting_rights_page`, `california_preregister_16_vote_18_page`, `california_registering_to_vote_new_citizen_page`; (+4 more) |
| case_study | 1 | 0 | 1 | 2026-09-08 | `swiss_post_uv_flaw_disclosure_2019_page` |
| cdf | 6 | 6 | 0 |  | `nist_gcr_24_058_cdf_implementation_guidance_pdf`, `nist_sp1500_100r2_err_pdf`, `nist_sp1500_101_eel_pdf`; (+3 more) |
| chrome | 1 | 0 | 1 | 2026-09-08 | `developer_chrome_implementing_speculation_rules_page` |
| cis | 1 | 0 | 1 | 2026-11-17 | `cis_rabet_v_page` |
| cisa | 13 | 0 | 13 | 2026-08-09 | `cisa_best_practices_securing_election_systems_page`, `cisa_bod_18_01_page`, `cisa_cpg_2_0_pdf`; (+10 more) |
| citation_backfill | 177 | 23 | 154 | 2026-07-25 | `asa_post_election_audit_best_practices_2018_pdf`, `bpc_content_uploads_2022_03_bpc_electronicballottransmission_revised_411`, `bpc_making_ballot_images_and_cast_vote_records_public`; (+174 more) |
| coercion | 1 | 1 | 0 |  | `voteagain_revoting_usenix_2020_pdf` |
| colorado | 1 | 0 | 1 | 2026-07-25 | `colorado_current_election_rules_page` |
| ct | 4 | 2 | 2 | 2026-09-08 | `ndss_2024_public_inspections_monitors_pdf`, `rfc6962_html`, `rfc9162_txt`; (+1 more) |
| delaware | 1 | 0 | 1 | 2026-07-25 | `delaware_guardianship_voter_eligibility_page` |
| digital_gov | 1 | 0 | 1 | 2026-09-08 | `digital_gov_mobile_principles_page` |
| dkim | 1 | 1 | 0 |  | `rfc6376_txt` |
| dmarc | 1 | 1 | 0 |  | `rfc7489_txt` |
| dns | 3 | 3 | 0 |  | `rfc2606_txt`, `rfc4033_txt`, `rfc8659_txt` |
| doj | 4 | 1 | 3 | 2026-08-09 | `ada_polling_places_checklist_page`, `ada_protecting_voter_rights_page`, `justice_language_minority_citizens_page`; (+1 more) |
| e2e | 3 | 2 | 1 | 2026-09-08 | `eac_e2e_protocols_draft_tgdc_2023_pdf`, `electionguard_spec_page`, `usenix_electionguard_toolkit_2024_pdf` |
| eac | 47 | 24 | 23 | 2026-08-09 | `eac_accessibility_checklist_accessible_communications_2024_pdf`, `eac_accessibility_for_voting_by_mail_checklist_pdf`, `eac_ai_and_election_administration_page`; (+44 more) |
| eat | 1 | 1 | 0 |  | `rfc9711_txt` |
| ed25519 | 1 | 1 | 0 |  | `rfc8032_txt` |
| email | 2 | 2 | 0 |  | `rfc8460_txt`, `rfc8461_txt` |
| evoting | 1 | 0 | 1 | 2026-09-08 | `schneier_swiss_evoting_vulnerability_2023_post` |
| georgia | 1 | 0 | 1 | 2026-07-25 | `georgia_register_to_vote_mental_incompetence_page` |
| google | 193 | 0 | 193 | 2026-09-08 | `chrome_lighthouse_notification_on_start_doc`, `chrome_web_push_rate_limits_blog_page`, `chrome_workbox_handling_service_worker_updates_page`; (+190 more) |
| gsa | 31 | 0 | 31 | 2026-08-09 | `api_data_gov_agency_manual_page`, `digital_gov_accessibility_for_ux_design_page`, `digital_gov_accessibility_social_media_in_government_page`; (+28 more) |
| http | 3 | 3 | 0 |  | `rfc9110_txt`, `rfc9111_txt`, `rfc9421_txt` |
| ietf | 1 | 0 | 1 | 2026-09-08 | `draft_scitt_refusal_events_02_html` |
| ifes | 1 | 1 | 0 |  | `ifes_results_management_cybersecurity_briefing_pdf` |
| in_toto | 5 | 4 | 1 | 2026-09-08 | `intoto_envelope_v1_md`, `intoto_slsa_provenance_predicate_md`, `intoto_specs_html`; (+2 more) |
| indiana | 1 | 0 | 1 | 2026-07-25 | `indiana_provisional_ballots_page` |
| ip | 3 | 3 | 0 |  | `rfc3849_txt`, `rfc5737_txt`, `rfc9637_txt` |
| iso | 1 | 0 | 1 | 2026-09-08 | `iso_iec_27037_iso_page` |
| jcs | 1 | 1 | 0 |  | `rfc8785_txt` |
| law | 1 | 0 | 1 | 2026-09-08 | `frcp_rule_37_lii_html` |
| maryland | 3 | 1 | 2 | 2026-07-25 | `maryland_designation_of_agent_form_mail_in_ballot_pdf`, `maryland_guardianship_voting_eligibility_page`, `maryland_mail_in_voting_page` |
| mdn | 123 | 0 | 123 | 2026-09-08 | `mdn_accept_attribute_page`, `mdn_alert_role_page`, `mdn_aria_busy_attribute_page`; (+120 more) |
| michigan | 1 | 0 | 1 | 2026-07-25 | `michigan_accessibility_and_accommodations_page` |
| microsoft | 100 | 0 | 100 | 2026-09-08 | `microsoft_365_copilot_privacy_learn_page`, `microsoft_365_copilot_public_web_access_page`, `microsoft_365_copilot_voice_features_page`; (+97 more) |
| minnesota | 1 | 1 | 0 |  | `minnesota_guardianship_voting_rights_page` |
| montana | 1 | 1 | 0 |  | `montana_satellite_election_offices_directive_pdf` |
| mozilla | 8 | 0 | 8 | 2026-09-08 | `firefox_print_simplified_pages_help_page`, `firefox_reader_view_help_page`, `mozilla_firefox_picture_in_picture_help_page`; (+5 more) |
| nasem | 1 | 1 | 0 |  | `nasem_securing_the_vote_highlights_pdf` |
| nass | 2 | 0 | 2 | 2026-12-01 | `nass_can_i_vote_page`, `nass_trustedinfo_2026_page` |
| new_hampshire | 1 | 0 | 1 | 2026-07-25 | `new_hampshire_how_are_votes_challenged_2025_pdf` |
| new_mexico | 1 | 0 | 1 | 2026-07-25 | `new_mexico_native_american_voting_rights_act_page` |
| nist | 19 | 12 | 7 | 2026-07-31 | `nist_ai_600_1_genai_profile_pdf`, `nist_ai_rmf_100_1_pdf`, `nist_csf2_0_pdf`; (+16 more) |
| north_carolina | 1 | 0 | 1 | 2026-07-25 | `north_carolina_accessible_absentee_voting_page` |
| north_dakota | 2 | 0 | 2 | 2026-07-25 | `north_dakota_tribal_member_voting_flyer_pdf`, `north_dakota_voter_id_requirements_page` |
| official_websites | 74 | 0 | 74 | 2026-07-25 | `arizona_jail_voting_guide_pdf`, `arizona_protected_voter_registration_page`, `arlington_lost_damaged_ballots_page`; (+71 more) |
| open_graph | 1 | 0 | 1 | 2026-09-08 | `open_graph_protocol_page` |
| oregon | 1 | 0 | 1 | 2026-07-25 | `oregon_voters_with_disabilities_assistance_page` |
| owasp | 1 | 0 | 1 | 2027-03-18 | `owasp_information_exposure_query_strings_page` |
| randomness | 1 | 0 | 1 | 2026-09-08 | `drand_docs_overview_html` |
| rats | 1 | 1 | 0 |  | `rfc9334_txt` |
| remote_return | 3 | 3 | 0 |  | `estonia_ivote_security_analysis_2014_pdf`, `mit_omniballot_analysis_2020_pdf`, `usenix_democracylive_security_2021_pdf` |
| scitt | 4 | 3 | 1 | 2026-09-08 | `draft_scitt_architecture_22_txt`, `draft_scitt_receipts_ccf_profile_00_txt`, `draft_scitt_scrapi_07_txt`; (+1 more) |
| section508 | 3 | 0 | 3 | 2026-08-09 | `section508_accessible_fonts_typography_page`, `section508_authoring_meaningful_alternative_text_page`, `section508_guide_accessible_web_design_development_page` |
| security | 1 | 1 | 0 |  | `rfc9116_txt` |
| slack | 1 | 0 | 1 | 2026-09-08 | `slack_unfurling_links_in_messages_page` |
| slsa | 1 | 0 | 1 | 2026-09-08 | `slsa_provenance_v1_2_html` |
| spf | 1 | 1 | 0 |  | `rfc7208_txt` |
| texas | 2 | 0 | 2 | 2026-07-25 | `texas_information_about_returning_your_carrier_envelope_pdf`, `texas_voter_assistance_and_interpreter_advisory_page` |
| tiktok | 1 | 0 | 1 | 2026-09-08 | `tiktok_live_events_help_page` |
| time | 4 | 4 | 0 |  | `draft_ietf_ntp_roughtime_17_txt`, `rfc3161_txt`, `rfc5905_txt`; (+1 more) |
| transparency | 2 | 0 | 2 | 2026-09-08 | `sigstore_rekor_overview`, `trillian_transparent_logging` |
| tuf | 1 | 0 | 1 | 2026-09-08 | `tuf_spec_latest_html` |
| uscis | 1 | 0 | 1 | 2026-08-09 | `uscis_administrative_naturalization_ceremony_voter_registration_page` |
| uswds | 67 | 0 | 67 | 2026-09-08 | `uswds_404_page_template_page`, `uswds_accessibility_page`, `uswds_accordion_accessibility_tests_page`; (+64 more) |
| vimeo | 74 | 0 | 74 | 2026-09-08 | `vimeo_about_end_screens_help_page`, `vimeo_about_on_site_notifications_help_page`, `vimeo_about_simulcasting_help_page`; (+71 more) |
| vote_gov | 5 | 0 | 5 | 2026-08-09 | `vote_gov_about_us_page`, `vote_gov_age_18_and_under_page`, `vote_gov_home_page`; (+2 more) |
| vvsg | 1 | 1 | 0 |  | `eac_vvsg2_test_assertions_v1_4_pdf` |
| w3c | 82 | 0 | 82 | 2026-09-08 | `w3c_personal_names_around_world_page`, `w3c_remote_playback_api_candidate_recommendation`, `w3c_uievents_algorithms_composition_section`; (+79 more) |
| washington | 2 | 1 | 1 | 2026-07-25 | `washington_future_voter_program_page`, `washington_signature_update_form_pdf` |
| web_dev | 2 | 0 | 2 | 2026-09-08 | `web_dev_network_reliability_page`, `web_dev_pwa_installation_page` |
| webkit | 1 | 0 | 1 | 2027-03-18 | `webkit_safari_18_reader_semantic_html_page` |
| well_known | 1 | 1 | 0 |  | `rfc8615_txt` |
| whatwg | 1 | 0 | 1 | 2026-09-08 | `whatwg_html_autocapitalize_autocorrect_section` |
| wicg | 1 | 0 | 1 | 2026-09-08 | `wicg_url_fragment_text_directives_spec_page` |
| youtube | 2 | 0 | 2 | 2026-09-08 | `youtube_in_app_browser_ios_help_page`, `youtube_universal_links_help_page` |
