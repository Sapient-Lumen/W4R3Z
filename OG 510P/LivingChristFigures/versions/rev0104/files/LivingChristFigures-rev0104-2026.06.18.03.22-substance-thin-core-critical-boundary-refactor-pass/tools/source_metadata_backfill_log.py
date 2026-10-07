#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['backfill_id', 'batch_revision', 'source_id', 'domain', 'candidate_ids', 'verification_mode', 'backfill_status', 'fields_updated', 'date_checked', 'maintenance_priority_after', 'public_exposure_effect', 'evidence_note', 'status', 'note']

# Cumulative source-health backfill ledger. This is metadata/safety maintenance,
# not source promotion, URL publication, referral advice, route extraction, family-story reuse,
# or service-capacity validation.
BATCHES={'rev0077': [('src_justice_gov_za_456a06b5',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'South Africa MPTT/Gallows exhumation public speech verified as dated 2025-05-03.')),
             ('src_justice_gov_za_f622e04c',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'South Africa MPTT/TRC reburial public speech verified as dated 2025-05-31.')),
             ('src_npa_gov_za_4340f7aa',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'NPA MPTT release verified with page date 2025-05-05 and release date 2025-05-02.')),
             ('src_bakerinstitute_org_d6c4f9b3',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Baker Institute Sudan mutual-aid research page verified as 2025-03-12.')),
             ('src_museumofhomelessness_org_49005fec',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Museum of Homelessness 2024 homeless-death investigation page verified as public context, not case list.')),
             ('src_nationalhomeless_org_26783ea2',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'National Homeless Persons Memorial Day public explainer verified; annual observance boundary retained.')),
             ('src_homelessdeathscount_org_d62ff6e0',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Homeless Deaths Count homepage verified as aggregate US death-monitoring context.')),
             ('src_homelessdeathscount_org_60b79db6',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Homeless Deaths Count methods/help page verified; individual death submissions remain outside cube use.')),
             ('src_afn_ca_f8bc2116',
              ('web_search_result_after_direct_open_error',
               'completed_partial_direct_error_visible',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'AFN MMIWG progress-report press release metadata was search-result-confirmed after direct-open error; no public URL expansion.')),
             ('src_academic_oup_com_82f20685',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'OUP Hearing Voices Movement article verified as published 2014-06-13.')),
             ('src_amnesty_org_aafa173a',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Amnesty El Salvador gang/human-rights context page verified as 2022-08-31.')),
             ('src_c_r_org_6558084e',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Conciliation Resources El Salvador gangs/peace-process context verified as Accord Issue 25, April 2014.')),
             ('src_care_org_60880b7a',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'CARE Yemen displacement/COVID public context page verified as 2021-03-18.')),
             ('src_cpr_org_272fb267',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Colorado Public Radio/NPR El Salvador evangelical exit context verified from URL-date/live text.')),
             ('src_duihua_org_df8296a4',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Dui Hua Dialogue Issue 46 page verified; undated source remains marked as such.')),
             ('src_humanium_org_57edc0f1',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Humanium China children-of-convicted-parents article verified with original/update dates.')),
             ('src_quno_org_070c6f64',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'QUNO children of prisoners program page verified; undated program page remains marked undated.')),
             ('src_hearing_voices_org_8dccf83c',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'UK National Hearing Voices Network homepage verified; no crisis/referral capacity claim added.')),
             ('src_hearingvoicesusa_org_f42484ca',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Hearing Voices Network USA about page verified; no clinical/referral capacity claim added.')),
             ('src_nida_nih_gov_fdbcc7a5',
              ('direct_open_js_challenge',
               'blocked_visible_recheck_needed',
               'date_last_checked|last_http_status|language|jurisdiction',
               'NIDA registry URL returned a JS challenge; row is intentionally left P1-visible rather than falsely complete.'))],
 'rev0078': [('src_abc_net_au_0e55f232',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'ABC public report metadata verified as 2025-11-24; no shelter/contact/service extraction.')),
             ('src_abuelas_org_ar_525b65f9',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Abuelas public science/history explainer verified as live; undated source remains marked undated.')),
             ('src_argentina_gob_ar_966addf8',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Argentina BNDG public history page verified as live; undated source remains marked undated.')),
             ('src_agenciabrasil_ebc_com_br_a53ee049',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Agência Brasil Mães de Maio public-context article verified as dated 2026-05-11.')),
             ('src_brasildefato_com_br_b727e80a',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Brasil de Fato Mães de Maio public-context article verified as dated 2026-05-13.')),
             ('src_chinadaily_com_cn_2ebe3f96',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'China Daily Red Apple/Fujian article verified as dated 2018-08-20.')),
             ('src_chinadaily_com_cn_3346de22',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'China Daily Red Apple/Fujian article verified as dated 2019-02-20.')),
             ('src_cupe_ca_e2ba4114',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'CUPE MMIWG/Bridget Tolley advocacy context verified as dated 2024-11-13; public layer remains closed.')),
             ('src_hepvu_org_126a4b1f',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'HepVu International Overdose Awareness Day context verified as dated 2022-08-31.')),
             ('src_inccip_org_b5729944',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'INCCIP about/charity context verified with 2025 accounts marker; no referral capacity added.')),
             ('src_intervoiceonline_org_85e7034d',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Intervoice homepage verified with latest update dated 2026-06-09; no crisis/referral capacity added.')),
             ('src_transcend_org_au_3489c875',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Transcend organization-history page verified; support/service pages handled separately as internal-only.')),
             ('src_mmiwg_ffada_ca_52aa4644',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'National Inquiry MMIWG final-report home page verified as final-report context; no aftercare/story extraction.')),
             ('src_caminandofronteras_org_efdba0c5',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Caminando Fronteras monitoring page contains route details and a missing-relative contact path; reclassified to internal route/contact-near.')),
             ('src_childfund_org_au_4965cce6',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'ChildFund 1-Tok page contains live helpline/service/referral details; reclassified to internal contact-rich.')),
             ('src_pflagcanada_ca_1680e546',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'pflag Canada homepage contains support/chapter/contact pathways; reclassified to internal contact-rich.')),
             ('src_pflagcanada_ca_44e27c6e',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'pflag Parents & Support Circle page contains support/resource/chapter pathways; reclassified to internal contact-rich.')),
             ('src_transcend_org_au_6ef1a2d9',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Transcend homepage contains quick-exit, contact, services, and care-pathway surfaces; reclassified to internal contact-rich.')),
             ('src_transcend_org_au_44c11205',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Transcend family-members page contains service/enquiry pathways; reclassified to internal contact-rich.')),
             ('src_humanrights_ca_39c3eea5',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'CMHR MMIWG resource guide contains support line/aftercare/story-resource surfaces; reclassified to internal contact-rich.')),
             ('src_africas_com_br_a7e4f577',
              ('direct_open_verification_challenge',
               'blocked_visible_recheck_needed',
               'date_last_checked|last_http_status|language|jurisdiction',
               'Africas.com.br direct open produced verification/loader challenge; row stays P1-visible until manual source-date verification.'))],
 'rev0079': [('src_greaterfortwayneinc_com_85187939',
              ('web_open_or_blocked_direct_check',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Greater Fort Wayne project.ME opening article exposes service location, hours, recovery support and harm-reduction context; reclassified to internal-only '
               'route/support-near.')),
             ('src_journalgazette_net_c2891b82',
              ('web_open_or_blocked_direct_check',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Journal Gazette project.ME opening source is recovery drop-in/service-location adjacent and robots-blocked for direct verification; reclassified internal-only '
               'with metadata debt visible.')),
             ('src_wane_com_b1478e44',
              ('web_open_or_blocked_direct_check',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'WANE project.ME recovery-center support source could expose support/capacity pathways; reclassified internal-only with manual verification posture.')),
             ('src_wfft_com_bde9f5d0',
              ('web_open_or_blocked_direct_check',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'WFFT recovery drop-in center opening source is service-location/support adjacent and robots-blocked; reclassified internal-only with manual verification '
               'posture.')),
             ('src_wfyi_org_64392b9d',
              ('web_open_or_blocked_direct_check',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'WFYI Narcan/harm-reduction profile includes recovery-support and access context; reclassified internal-only; no public service availability or referral use.')),
             ('src_understandingvoices_com_327bab21',
              ('web_open_or_blocked_direct_check',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Understanding Voices hearing-voices groups page describes peer-support groups, crisis navigation, confidentiality and group continuity; reclassified internal-only '
               'support-path surface.')),
             ('src_transcend_org_au_a2da7245',
              ('web_open_or_blocked_direct_check',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Transcend father-figures program page has support-program, services, helplines/contact navigation, and future participation opportunities; reclassified '
               'internal-only.')),
             ('src_transformandofamilias_com_ar_d4d207ce',
              ('web_open_or_blocked_direct_check',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Transformando Familias homepage exposes accompaniment, workshops/courses, contact/email and participation paths; reclassified internal-only support/contact '
               'surface.')),
             ('src_omct_org_57fea8b0',
              ('web_open_or_blocked_direct_check',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'OMCT EAAF network-member profile exposes phone/email/address and forensic/missing-persons context; reclassified internal-only contact/intake-adjacent source.')),
             ('src_missingpersons_icrc_org_5bea203b',
              ('web_open_or_blocked_direct_check',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'ICRC missing-persons EAAF directory page was direct-open 403 and directory/contact-adjacent; reclassified internal-only pending manual review.')),
             ('src_missingpersons_icrc_org_24ae247f',
              ('web_open_or_blocked_direct_check',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'ICRC missing-persons Mothers of Srebrenica and Žepa directory page was direct-open 403 and directory/contact-adjacent; reclassified internal-only pending manual '
               'review.'))],
 'rev0080': [('src_adobomagazine_com_a04398ff',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Adobo Magazine Tan Swee Ban/RHB article verified as dated 2025-01-22; public context only.')),
             ('src_brandinginasia_com_c973941c',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Branding in Asia Tan Swee Ban/RHB article verified as dated 2025-01-21; public context only.')),
             ('src_americamagazine_org_72ae6cc1',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'America Magazine El Salvador gang-violence/church context verified as dated 2022-04-13.')),
             ('src_reuters_com_e7f0a6d4',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Reuters South Africa apartheid-era crimes inquiry article verified as dated 2025-04-30.')),
             ('src_nippon_com_01107706',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Nippon.com kodokushi/trauma-cleaning public context verified as dated 2021-10-15.')),
             ('src_tif_ssrc_org_375b4b74',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'The Immanent Frame/SSRC mortuary prospects essay verified as dated 2021-09-23.')),
             ('src_muse_jhu_edu_66553766',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Project MUSE article metadata verified; launch date 2013-05-22 and archive status archived 2020 recorded from publisher page.')),
             ('src_sahistory_org_za_a5bce2fd',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'South African History Online MPTT page verified as published 2020-05-31 and updated 2020-06-03.')),
             ('src_museumofhomelessness_org_6edac4c7',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Museum of Homelessness 2020 homeless-deaths article verified as dated 2021-02-22.')),
             ('src_osvnews_com_692524b9',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'OSV homeless memorial services article verified as dated 2023-12-27.')),
             ('src_sandas_org_au_709497e1',
              ('web_open_primary',
               'completed_verified_metadata',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'SANDAS International Overdose Awareness Day page verified with 2024-08-31 event context.')),
             ('src_alleganycouncil_wordpress_com_7023f40f',
              ('web_search_result_metadata_check',
               'completed_partial_direct_error_visible',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Allegany Council IOAD/Sally Finn page verified through indexed search result dated 2021-08-30.')),
             ('src_freemalaysiatoday_com_1e938970',
              ('web_search_result_metadata_check',
               'completed_partial_direct_error_visible',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Free Malaysia Today Tan Swee Ban profile metadata verified through indexed search result dated 2025-03-10.')),
             ('src_freemalaysiatoday_com_54e280c7',
              ('web_search_result_metadata_check',
               'completed_partial_direct_error_visible',
               'source_date|date_last_checked|last_http_status|language|jurisdiction',
               'Free Malaysia Today Tan Swee Ban refresh source metadata verified through indexed search result dated 2025-03-10.')),
             ('src_coloradocoalition_org_db167abc',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Colorado Coalition homeless memorial advisory contains media contact plus service/referral navigation; reclassified internal-only contact/service-near.')),
             ('src_projectme_fw_org_18cb8156',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'project.ME homepage exposes request-support/Naloxone, recovery drop-in, peer-support and contact paths; reclassified internal-only.')),
             ('src_monarelief_ngo_b5511624',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Mona Relief about page exposes humanitarian field/service/shelter/logistics context; reclassified internal-only.')),
             ('src_monarelief_ngo_5ad67832',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Mona Relief media page is humanitarian operational support-adjacent; reclassified internal-only pending manual preservation review.')),
             ('src_monareliefye_org_ac108c94',
              ('web_open_or_blocked_direct_check',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Legacy Mona Relief about URL remains operational-humanitarian/contact-adjacent; reclassified internal-only with direct-check caveat.')),
             ('src_humanitariancorridor_org_87783b45',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Humanitarian Corridors page describes selection/transfer/accommodation pipeline; reclassified internal-only operational-route/service path.')),
             ('src_fondazionecarpinetum_org_b54a601e',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Fondazione Carpinetum request-housing page exposes housing request process and contact/location details; reclassified internal-only.')),
             ('src_fondazionecarpinetum_org_b3ab1d75',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Fondazione Carpinetum homepage lists protected-housing centers and contact/service paths; reclassified internal-only.')),
             ('src_fondazionecarpinetum_org_166c31cf',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Fondazione Carpinetum housing-center page exposes shelter/housing location context; reclassified internal-only.')),
             ('src_fondazionecarpinetum_org_9b5e0269',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Fondazione Carpinetum housing-center page exposes shelter/housing location context; reclassified internal-only.')),
             ('src_santegidio_org_cc618bd7',
              ('web_open_primary',
               'safety_reclassified_no_public_url',
               'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically',
               'Sant’Egidio co-housing page is housing/support-service adjacent; reclassified internal-only.'))]}
BATCH_DATES={'rev0077':'2026-06-12','rev0078':'2026-06-12','rev0079':'2026-06-12','rev0080':'2026-06-13','rev0081':'2026-06-13'}
COMPLETED={'completed_verified_metadata','completed_partial_direct_error_visible','coverage_reconciled_existing_verified_metadata'}

# rev0081 full remaining public-context queue pass: metadata repair plus safety reclassification.
BATCHES['rev0081'] = [('src_asiapacific_unwomen_org_4fc5fc2b', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_asiapacific_unwomen_org_4fc5fc2b metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_en_wikipedia_org_63e05ab7', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_en_wikipedia_org_63e05ab7 metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_frontiersin_org_0adf8f6e', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_frontiersin_org_0adf8f6e metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_fsmlaw_org_c997931a', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_fsmlaw_org_c997931a metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_fsmlaw_org_e255111c', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_fsmlaw_org_e255111c metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_islandtimes_org_a3a84c3a', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_islandtimes_org_a3a84c3a metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_journals_sagepub_com_7bce719c', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_journals_sagepub_com_7bce719c metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_link_springer_com_7297e8ba', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_link_springer_com_7297e8ba metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_nida_nih_gov_fdbcc7a5', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_nida_nih_gov_fdbcc7a5 metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_ohchr_org_dd8b579e', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_ohchr_org_dd8b579e metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_pacificdata_org_04a16ba6', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_pacificdata_org_04a16ba6 metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_pacificdata_org_671b1237', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_pacificdata_org_671b1237 metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_pacificdata_org_b0a0e5ad', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_pacificdata_org_b0a0e5ad metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_pjsp_govt_nz_63a82b31', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_pjsp_govt_nz_63a82b31 metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_platform_who_int_61dd0742', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_platform_who_int_61dd0742 metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_ronlaw_gov_nr_02ff88fc', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_ronlaw_gov_nr_02ff88fc metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_sinembargo_mx_922b657e', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_sinembargo_mx_922b657e metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_spc_int_235d26c6', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_spc_int_235d26c6 metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_state_gov_8d35873f', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_state_gov_8d35873f metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_tandfonline_com_021ff445', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_tandfonline_com_021ff445 metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_thelancet_com_74257e1f', ('web_search_result_after_direct_open_error', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'Lancet Hearing Voices URL was structurally repaired from indexed fulltext/DOI result; direct publisher open returned access challenge; metadata only.')), ('src_undp_org_dba2eee0', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_undp_org_dba2eee0 metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_ungeneva_org_8a872e57', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_ungeneva_org_8a872e57 metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_unwomen_org_e6904897', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_unwomen_org_e6904897 metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_upr_info_org_fed03bd1', ('web_search_result_metadata_check', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'src_upr_info_org_fed03bd1 metadata repaired during rev0081 URL/source-health batch; no public URL/contact/referral/route/service/case expansion.')), ('src_africas_com_br_a7e4f577', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Mães de Maio article is family/case-detail adjacent; keep internal-only and do not extract names, incident histories, or vigil details.')), ('src_alistairreignblog_com_e225d676', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Mona Relief volunteer-targeting/aid-delivery context is operational-humanitarian near; no route/logistics/contact extraction.')), ('src_beijing_kids_com_3b58b53c', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Sun Village child residential/service context is location/access-path sensitive; no service referral or living-site amplification.')), ('src_csmonitor_com_9f397ae4', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Gang-exit ministry context can become live referral/support-path exposure; keep internal-only.')), ('src_en_wikipedia_org_28c85673', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'MMIWG encyclopedia page is case/family-search adjacent; no public URL/case extraction.')), ('src_en_wikipedia_org_2f2c8928', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Emergency Response Rooms page describes live humanitarian coordination/operations; keep route/support details internal.')), ('src_en_wikipedia_org_5e827adc', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Madres buscadoras page is missing-persons/family-search adjacent; no case/location extraction.')), ('src_en_wikipedia_org_d8c8ae26', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Hospice/support-care context can become referral/service-path exposure; keep internal-only.')), ('src_en_wikipedia_org_d9632dc3', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Greg Boyle/Homeboy context is service/support-path adjacent; no referral/capacity rendering.')), ('src_en_wikipedia_org_f51daac2', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Hearing Voices support-network context can become group/referral exposure; keep public URL blocked.')), ('src_en_wikipedia_org_faf56040', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Homeboy Industries page is service/support-path adjacent; no referral/capacity rendering.')), ('src_esango_un_org_42aab1bc', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'UN NGO profile/directory context is contact/organization-address adjacent; no public URL exposure.')), ('src_facebook_com_8a49ab3a', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Mona Relief social video is operational/field-context adjacent; no public link or logistics extraction.')), ('src_facinghistory_org_ea5fb90d', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Las Patronas article is migrant-route/accompaniment adjacent; no route/contact/timing extraction.')), ('src_fiertemontreal_com_60581942', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Gender Creative Kids/Fierté page is event/support-path adjacent; no contact/attendance/support referral use.')), ('src_fwbusiness_com_f9f62ac3', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'project.ME local profile is recovery/support-path adjacent; no contact or service-capacity use.')), ('src_gcsynod_org_b17ba88f', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Former-gang-member ministry context can become live referral/support exposure; keep internal-only.')), ('src_jornaldebrasilia_com_br_c6491ea7', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Mães de Maio public article is family/case-detail adjacent; no case/name extraction.')), ('src_journalgazette_net_5d1fc94e', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Aisha Diss/project.ME profile is recovery-support adjacent; no public service referral/capacity claim.')), ('src_legistar_council_nyc_gov_d3310fee', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Public meeting/vigil/media surface may carry images, names, or event logistics; keep internal-only unless reviewed.')), ('src_medium_com_beaae411', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Sun Village article is child residential/service-location adjacent; no access/location/referral amplification.')), ('src_middleeastmonitor_com_e3a4f479', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Mona Relief leadership/operations context is humanitarian-route/logistics adjacent; keep internal-only.')), ('src_museumofhomelessness_org_ec0747bd', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Dying Homeless Project accepts death reports and handles death-record/memorial context; no individual-death extraction or submission-path reuse.')), ('src_newsweek_com_19713173', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Gang-exit church context is support/referral adjacent; keep internal-only.')), ('src_piauihoje_com_e5228d9a', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Mães de Maio article is case/family profile adjacent; no names/incidents extraction.')), ('src_racismoambiental_net_br_72416998', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Mães de Maio/A Pública public article is case/family-profile adjacent; no case-story extraction.')), ('src_scmp_com_1a5d3e1f', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Last-living-amah profile is person/family-care-story adjacent; keep internal-only to avoid extraction of identity/story details.')), ('src_tatlerasia_com_5752a534', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Peace Harmony Home profile is residential/support-location adjacent; no referral/location/capacity use.')), ('src_thedial_world_a77ce6db', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Migrant-bodies identification article is case/family/route adjacent; no route, CATE, ante-mortem, or family-detail extraction.')), ('src_thestar_com_my_698a39b9', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Peace Harmony Home article is residential/support-location adjacent; no referral/location/capacity use.')), ('src_thestar_com_my_c3afce4c', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Peace Harmony Home article is residential/support-location adjacent; no referral/location/capacity use.')), ('src_theworld_org_c6a23d14', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Mona Relief famine/aid article is field-operations/logistics adjacent; no route/contact/capacity extraction.')), ('src_thrivefuture_org_37aff843', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Thrive Future / support-program context can become service/contact path; keep internal-only pending manual review.')), ('src_tour_beijing_com_7b576e3d', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Sun Village travel/blog context is child residential/location adjacent; no visit/access/location amplification.')), ('src_umnews_org_5fc6fcc6', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Gang-neighborhood church article is support/referral adjacent; keep internal-only.')), ('src_uncannyjapan_com_649bf1c4', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'source_date|date_last_checked|last_http_status|language|jurisdiction|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Muenbotoke/death-memorial podcast source is death-record/narrative adjacent; no individual-story extraction.'))]


# rev0081 late near-miss containment rows discovered by the narrowed source-safety audit.
BATCHES['rev0081'] += [('src_duihua_org_df8296a4', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'date_last_checked|last_http_status|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Dui Hua children-of-incarcerated-mothers context is child/residential-family-service adjacent; keep internal-only and do not amplify family/location/support paths.')), ('src_humanium_org_57edc0f1', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'date_last_checked|last_http_status|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'Humanium Sun Village/orphanage article is child residential/service-context adjacent; keep internal-only and do not amplify location/access/support paths.')), ('src_inccip_org_b5729944', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'date_last_checked|last_http_status|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'INCCIP children-of-incarcerated-parents about page is organization/service context adjacent; keep internal-only and no referral/capacity use.')), ('src_quno_org_070c6f64', ('web_search_result_sensitive_reclass', 'safety_reclassified_no_public_url', 'date_last_checked|last_http_status|harm_proximity|public_link_policy|safe_to_recheck_automatically', 'QUNO children-of-prisoners program page is policy/program context near vulnerable children; keep internal-only for source maintenance.'))]


# rev0083 Pacific crisis/GBV/support cohort: metadata/freshness repaired and explicit
# no-public-archive/no-auto-crawl preservation decisions recorded. These are not
# public-source releases and do not authorize contact/referral/route/service extraction.
BATCHES['rev0083'] = [('src_acom_org_sb_08b47827',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'acom.org.sb Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Solomon Islands.')),
 ('src_devpolicy_org_c268901f',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'devpolicy.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Papua New Guinea.')),
 ('src_dfat_gov_au_8a71acdb',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'dfat.gov.au Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Nauru.')),
 ('src_docs_un_org_3a479271',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'docs.un.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Tuvalu.')),
 ('src_fbcnews_com_fj_adab8c69',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'fbcnews.com.fj Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pacific regional / Vanuatu / Tonga / Kiribati / '
   'Papua New Guinea.')),
 ('src_femilipng_org_9056a4ee',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'femilipng.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Papua New Guinea.')),
 ('src_femilipngaus_org_d3ddb654',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'femilipngaus.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Papua New Guinea.')),
 ('src_fijiwomen_com_2b876272',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'fijiwomen.com Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Fiji.')),
 ('src_fijiwomen_com_57718d07',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'fijiwomen.com Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pacific regional / Fiji / Tuvalu.')),
 ('src_fijiwomen_com_b642dedd',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'fijiwomen.com Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pacific regional / Fiji / Cook Islands.')),
 ('src_fijiwomen_com_cccf1022',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'fijiwomen.com Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Fiji.')),
 ('src_fijiwomen_com_d94329cc',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'fijiwomen.com Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pacific regional / Fiji / Tuvalu.')),
 ('src_findahelpline_com_ad966042',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'findahelpline.com Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Kiribati.')),
 ('src_foreignminister_gov_au_eb92da86',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'foreignminister.gov.au Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pacific regional / Vanuatu / Tonga / '
   'Kiribati / Papua New Guinea.')),
 ('src_fscsi_org_sb_6c0b4c65',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'fscsi.org.sb Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Solomon Islands.')),
 ('src_iwda_org_au_afb0bcde',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'iwda.org.au Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Solomon Islands.')),
 ('src_kit_edu_ki_bd8021d9',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'kit.edu.ki Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Kiribati.')),
 ('src_kwcsc_ki_58ad1de9',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'kwcsc.ki Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Kiribati.')),
 ('src_lifeline_international_com_cacae671',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'lifeline-international.com Pacific crisis/GBV/support source reviewed as sensitive '
   'contact/referral/service-adjacent metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Papua '
   'New Guinea.')),
 ('src_lifelinefiji_com_01f25fc5',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'lifelinefiji.com Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Fiji.')),
 ('src_lifelinefiji_com_4945cc73',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'lifelinefiji.com Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Fiji.')),
 ('src_lifelinefiji_com_9e7fc891',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'lifelinefiji.com Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Fiji.')),
 ('src_micronesia_un_org_5e7e058c',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'micronesia.un.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Kiribati.')),
 ('src_moh_gov_vu_c60cb0ea',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'moh.gov.vu Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Vanuatu.')),
 ('src_naurujudiciary_gov_nr_09f265eb',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'naurujudiciary.gov.nr Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Nauru.')),
 ('src_ombudsman_gov_ws_50f37d16',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'ombudsman.gov.ws Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Samoa.')),
 ('src_openresearch_repository_anu_edu_au_5e0fbcc6',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'openresearch-repository.anu.edu.au Pacific crisis/GBV/support source reviewed as sensitive '
   'contact/referral/service-adjacent metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Papua '
   'New Guinea.')),
 ('src_pacific_unfpa_org_4cd6d3e0',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacific.unfpa.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Palau.')),
 ('src_pacificdata_org_09ad25d9',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacificdata.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Marshall Islands.')),
 ('src_pacificdata_org_19bc3167',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacificdata.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Marshall Islands.')),
 ('src_pacificdata_org_489e7207',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacificdata.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Federated States of Micronesia.')),
 ('src_pacificdata_org_57924b72',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacificdata.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Niue.')),
 ('src_pacificdata_org_61658d14',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacificdata.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Federated States of Micronesia.')),
 ('src_pacificdata_org_98d28246',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacificdata.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Cook Islands.')),
 ('src_pacificdata_org_c4845950',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacificdata.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Federated States of Micronesia.')),
 ('src_pacificdata_org_c6f8acbc',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacificdata.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Nauru.')),
 ('src_pacificdata_org_f19685fd',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacificdata.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Nauru.')),
 ('src_pacificdata_org_f47dbf11',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacificdata.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Federated States of Micronesia.')),
 ('src_pacifichealthdialog_nz_24dc1084',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacifichealthdialog.nz Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Niue.')),
 ('src_pacificwomen_org_2c76d28d',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacificwomen.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pacific regional / Federated States of '
   'Micronesia / Marshall Islands.')),
 ('src_pacificwomen_org_435ae489',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacificwomen.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pacific regional / multi-country.')),
 ('src_pacificwomen_org_7bb97d9b',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacificwomen.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pacific regional / multi-country.')),
 ('src_pacificwomen_org_cc86299f',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pacificwomen.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Federated States of Micronesia.')),
 ('src_pina_com_fj_c1eba419',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pina.com.fj Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pacific regional / Vanuatu / Tonga / Kiribati / '
   'Papua New Guinea.')),
 ('src_png_embassy_gov_au_f23cb6b3',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'png.embassy.gov.au Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Papua New Guinea.')),
 ('src_png_highcommission_gov_au_b73a1da2',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'png.highcommission.gov.au Pacific crisis/GBV/support source reviewed as sensitive '
   'contact/referral/service-adjacent metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Papua '
   'New Guinea.')),
 ('src_samoaobserver_ws_5c8ee258',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'samoaobserver.ws Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Samoa.')),
 ('src_sista_com_vu_45c5a136',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'sista.com.vu Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Vanuatu.')),
 ('src_solomonislands_embassy_gov_au_3f78d506',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'solomonislands.embassy.gov.au Pacific crisis/GBV/support source reviewed as sensitive '
   'contact/referral/service-adjacent metadata; no-public-archive/no-auto-crawl decision recorded; '
   'jurisdiction=Solomon Islands.')),
 ('src_spc_int_9b68d458',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'spc.int Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pacific regional / multi-country.')),
 ('src_spccfpstore1_blob_core_windows_net_289aa4f9',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'spccfpstore1.blob.core.windows.net Pacific crisis/GBV/support source reviewed as sensitive '
   'contact/referral/service-adjacent metadata; no-public-archive/no-auto-crawl decision recorded; '
   'jurisdiction=Pacific regional / multi-country.')),
 ('src_spotlightinitiative_org_1c534a69',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'spotlightinitiative.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Palau.')),
 ('src_spotlightinitiative_org_53c68837',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'spotlightinitiative.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Samoa.')),
 ('src_svsg_org_ws_0b3fa712',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'svsg.org.ws Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Samoa.')),
 ('src_svsg_org_ws_6f45d73d',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'svsg.org.ws Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Samoa.')),
 ('src_therapyroute_com_e2878237',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'therapyroute.com Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Samoa.')),
 ('src_undp_org_9524a55d',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'undp.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pacific regional / Palau / Nauru / Federated '
   'States of Micronesia / Marshall Islands.')),
 ('src_undp_org_e067e85a',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'undp.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pacific regional / Palau / Federated States of '
   'Micronesia / Marshall Islands.')),
 ('src_undp_org_e9f45a1c',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'undp.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pacific regional / Palau / Federated States of '
   'Micronesia / Marshall Islands.')),
 ('src_unicef_org_6b60eb6b',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'unicef.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Papua New Guinea.')),
 ('src_vanuatuwomenscentre_org_30d819c2',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'vanuatuwomenscentre.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Vanuatu.')),
 ('src_vanuatuwomenscentre_org_36e931e9',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'vanuatuwomenscentre.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Vanuatu.')),
 ('src_vanuatuwomenscentre_org_4a728277',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'vanuatuwomenscentre.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Vanuatu.')),
 ('src_vanuatuwomenscentre_org_652f712d',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'vanuatuwomenscentre.org Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent '
   'metadata; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Vanuatu.')),
 ('src_wccctonga_com_0991ba1a',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'wccctonga.com Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Tonga.')),
 ('src_wccctonga_com_3eff8ccc',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'wccctonga.com Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Tonga.')),
 ('src_wccctonga_com_9c3bafe0',
  ('web_search_result_and_source_index_sensitive_cohort',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'wccctonga.com Pacific crisis/GBV/support source reviewed as sensitive contact/referral/service-adjacent metadata; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Tonga.'))]

# rev0084 non-Pacific/manual-sensitive legacy cohort: metadata reviewed without direct crawl and explicit
# no-public-archive/no-auto-crawl decisions recorded for internal-only P1 rows.
BATCHES['rev0084'] = [('src_abuelas_org_ar_2543f5c7',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'abuelas.org.ar legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Argentina.')),
 ('src_abuelas_org_ar_31c08cd1',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'abuelas.org.ar legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Argentina.')),
 ('src_abuelas_org_ar_70fd4749',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'abuelas.org.ar legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Argentina.')),
 ('src_agenciapresentes_org_11d35221',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'agenciapresentes.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico — Casa '
   'Hogar Paola Buenrostro in CDMX (opened January 2020); second house Catherinne Danielle Márquez '
   'in Cuernavaca, Morelos (opened February 2022); third house Kaory Catarero Regalado in Apaxco, '
   'Estado de México .')),
 ('src_alarmphone_org_501cbdd9',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'alarmphone.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Italy / Mediterranean '
   'routes.')),
 ('src_aljazeera_com_e7707fdc',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'aljazeera.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Italy / Mediterranean '
   'routes.')),
 ('src_americamagazine_org_fecedb62',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'americamagazine.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Riohacha, La Guajira, '
   'Colombia.')),
 ('src_amnesty_org_c3d47c42',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'amnesty.org legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico - translocal (Sonora, '
   'Veracruz, Puebla, Tamaulipas, Chiapas, Baja California and other states).')),
 ('src_archives_nyc_cae7953e',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'archives.nyc legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=New York City, New York, USA; '
   'Hart Island / Bronx / public cemetery system.')),
 ('src_axios_com_540481fb',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'axios.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States origin; '
   'online/translocal networks.')),
 ('src_bangkokpost_com_1565c1c3',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'bangkokpost.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Chiang Rai Province, '
   'northern Thailand.')),
 ('src_bangkokpost_com_5422484c',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'bangkokpost.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Chiang Rai Province, '
   'northern Thailand.')),
 ('src_batimes_com_ar_9b57d8d0',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'batimes.com.ar legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Argentina.')),
 ('src_blogs_lse_ac_uk_8ce8ece5',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'blogs.lse.ac.uk legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Lalish temple, Sheikhan '
   'district, Duhok Governorate, Kurdistan Region of Iraq; office serves Yazidi survivors of the '
   '2014 ISIS Sinjar genocide and continuing crisis.')),
 ('src_buenosairesherald_com_09275290',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'buenosairesherald.com legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Argentina.')),
 ('src_calmatters_org_2424892a',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'calmatters.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pittsburgh, '
   'Pennsylvania, USA; translocal through the Street Medicine Institute field network.')),
 ('src_caminandofronteras_org_2bff210c',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'caminandofronteras.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Morocco / '
   'Spain / Western Euro-African border.')),
 ('src_caminandofronteras_org_642712fa',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'caminandofronteras.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Morocco / '
   'Spain / Western Euro-African border.')),
 ('src_caminandofronteras_org_aded1537',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'caminandofronteras.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Morocco / '
   'Spain / Western Euro-African border.')),
 ('src_caminandofronteras_org_d3e5d75d',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'caminandofronteras.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Morocco / '
   'Spain / Western Euro-African border.')),
 ('src_canada_ca_9095f6f5',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'canada.ca legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Canada / sponsored refugees '
   'overseas.')),
 ('src_catalog_data_gov_7faaa634',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'catalog.data.gov legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=New York City, New '
   'York, USA; Hart Island / Bronx / public cemetery system.')),
 ('src_catholicworker_org_c3c2b69d',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'catholicworker.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Manila / Meycauayan, '
   'Philippines.')),
 ('src_catholicworker_org_f2cc681c',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'catholicworker.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Manila / Meycauayan, '
   'Philippines.')),
 ('src_causeiq_com_3eeb58f3',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'causeiq.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Worcester, Massachusetts, '
   'USA.')),
 ('src_cbsnews_com_066ae688',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'cbsnews.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pittsburgh, Pennsylvania, USA; '
   'translocal through the Street Medicine Institute field network.')),
 ('src_chathamhouse_org_524f89f0',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'chathamhouse.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Sudan — decentralized '
   'conflict-zone mutual-aid networks; public cube must not map base rooms, kitchens, routes, '
   'transfer paths, local contacts, or volunteer identities.')),
 ('src_cnn_com_d009192c',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'cnn.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Goyang, Seoul, and other South '
   'Korean cities; Nanum and Nanum operates the Seoul Public Funeral consultation hotline ([public '
   'consultation hotline number redacted — non-referral cube]).')),
 ('src_cnn_com_fc6a5310',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'cnn.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Goyang, Seoul, and other South '
   'Korean cities; Nanum and Nanum operates the Seoul Public Funeral consultation hotline ([public '
   'consultation hotline number redacted — non-referral cube]).')),
 ('src_council_nyc_gov_4ac8bb71',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'council.nyc.gov legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=New York City, New '
   'York, USA; Hart Island / Bronx / public cemetery system.')),
 ('src_crcc_usc_edu_e6af180a',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'crcc.usc.edu legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Chiang Rai Province, northern '
   'Thailand.')),
 ('src_doctorswithoutborders_org_a2f603ba',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'doctorswithoutborders.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Lebanon — '
   'Beirut-based, helpline serving the country and parts of the wider Arabic-speaking Middle '
   'East.')),
 ('src_eaaf_org_3b4b4c3c',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'eaaf.org legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Argentina / international.')),
 ('src_ehospice_com_fd0c8d16',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'ehospice.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Moscow and other Russian '
   "regions; First Moscow Hospice (1994), Lighthouse children's hospice (opened October 2019).")),
 ('src_eldiario_es_3a46630e',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'eldiario.es legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico — Casa Hogar Paola '
   'Buenrostro in CDMX (opened January 2020); second house Catherinne Danielle Márquez in '
   'Cuernavaca, Morelos (opened February 2022); third house Kaory Catarero Regalado in Apaxco, '
   'Estado de México .')),
 ('src_elpais_com_25ccd42e',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'elpais.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Argentina.')),
 ('src_elpais_com_385ceec1',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'elpais.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico / Spain.')),
 ('src_elpais_com_89c9c27a',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'elpais.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Argentina.')),
 ('src_elpais_com_b1f7ec24',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'elpais.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico.')),
 ('src_elpais_com_e1fbf5e9',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'elpais.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Argentina.')),
 ('src_embracelebanon_org_19e52581',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'embracelebanon.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Lebanon — Beirut-based, '
   'helpline serving the country and parts of the wider Arabic-speaking Middle East.')),
 ('src_endhomelessness_org_ea3bd781',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'endhomelessness.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pittsburgh, '
   'Pennsylvania, USA; translocal through the Street Medicine Institute field network.')),
 ('src_endhomelessness_org_f50581e4',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'endhomelessness.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pittsburgh, '
   'Pennsylvania, USA; translocal through the Street Medicine Institute field network.')),
 ('src_enklave_srebrenica_zepa_org_6df8f0e6',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'enklave-srebrenica-zepa.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Bosnia and '
   'Herzegovina.')),
 ('src_fairplanet_org_fa21271f',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'fairplanet.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico.')),
 ('src_fflag_org_uk_004e8537',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'fflag.org.uk legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=United Kingdom / Great '
   'Britain.')),
 ('src_fflag_org_uk_35e943d8',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'fflag.org.uk legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=United Kingdom / Great '
   'Britain.')),
 ('src_fflag_org_uk_402f82f3',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'fflag.org.uk legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=United Kingdom / Great '
   'Britain.')),
 ('src_fhr_org_za_44a20109',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'fhr.org.za legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=South Africa.')),
 ('src_foreignpolicy_com_9da2242d',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'foreignpolicy.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Lalish temple, Sheikhan '
   'district, Duhok Governorate, Kurdistan Region of Iraq; office serves Yazidi survivors of the '
   '2014 ISIS Sinjar genocide and continuing crisis.')),
 ('src_foundationforlebanon_org_452511ec',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'foundationforlebanon.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Lebanon — '
   'Beirut-based, helpline serving the country and parts of the wider Arabic-speaking Middle '
   'East.')),
 ('src_gardenofinnocence_org_09316abc',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'gardenofinnocence.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States; '
   'originated in San Diego, California; affiliated/local garden network.')),
 ('src_gardenofinnocence_org_2f3d4f22',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'gardenofinnocence.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States; '
   'originated in San Diego, California; affiliated/local garden network.')),
 ('src_gardenofinnocents_org_0b5fc46c',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'gardenofinnocents.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States; '
   'originated in San Diego, California; affiliated/local garden network.')),
 ('src_gire_org_mx_cf381d69',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'gire.org.mx legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico — Casa Hogar Paola '
   'Buenrostro in CDMX (opened January 2020); second house Catherinne Danielle Márquez in '
   'Cuernavaca, Morelos (opened February 2022); third house Kaory Catarero Regalado in Apaxco, '
   'Estado de México .')),
 ('src_gothamist_com_bd80299e',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'gothamist.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=New York City, New '
   'York, USA; Hart Island / Bronx / public cemetery system.')),
 ('src_hartisland_net_5d46d16c',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'hartisland.net legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=New York City, New '
   'York, USA; Hart Island / Bronx / public cemetery system.')),
 ('src_hartisland_net_94ac9345',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'hartisland.net legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=New York City, New '
   'York, USA; Hart Island / Bronx / public cemetery system.')),
 ('src_hartisland_net_cee83a15',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'hartisland.net legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=New York City, New '
   'York, USA; Hart Island / Bronx / public cemetery system.')),
 ('src_herwayhomeworcester_org_4d6a41c4',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'herwayhomeworcester.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Worcester, '
   'Massachusetts, USA.')),
 ('src_homeshare_org_7a795931',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'homeshare.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United Kingdom; '
   'international programme network.')),
 ('src_homeshareuk_org_45d7926c',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'homeshareuk.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United Kingdom; '
   'international programme network.')),
 ('src_homosensual_com_b4f12db7',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'homosensual.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico — Casa Hogar '
   'Paola Buenrostro in CDMX (opened January 2020); second house Catherinne Danielle Márquez in '
   'Cuernavaca, Morelos (opened February 2022); third house Kaory Catarero Regalado in Apaxco, '
   'Estado de México .')),
 ('src_hqsc_govt_nz_b4de0756',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'hqsc.govt.nz legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Te Tai Tokerau / Northland, '
   'Aotearoa New Zealand; serving a population of about 179,000.')),
 ('src_hrc_govt_nz_dc88173c',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'hrc.govt.nz legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Te Tai Tokerau / Northland, '
   'Aotearoa New Zealand; serving a population of about 179,000.')),
 ('src_hrw_org_ff6af737',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'hrw.org legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Italy / Mediterranean '
   'routes.')),
 ('src_humanrightsobservers_org_13a2f5c3',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'humanrightsobservers.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Calais, '
   'Grande-Synthe, Dunkirk, northern France / UK-France border.')),
 ('src_humanrightsobservers_org_9d32f01c',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'humanrightsobservers.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Calais, '
   'Grande-Synthe, Dunkirk, northern France / UK-France border.')),
 ('src_humanrightsobservers_org_d24bd142',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'humanrightsobservers.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Calais, '
   'Grande-Synthe, Dunkirk, northern France / UK-France border.')),
 ('src_iasp_info_8ace6ee0',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'iasp.info legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Aotearoa New Zealand / '
   'Pasifika communities nationally.')),
 ('src_innovation_go_kr_3adead05',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'innovation.go.kr legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Goyang, Seoul, and '
   'other South Korean cities; Nanum and Nanum operates the Seoul Public Funeral consultation '
   'hotline ([public consultation hotline number redacted — non-referral cube]).')),
 ('src_inputfortwayne_com_5a1bbbff',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'inputfortwayne.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Fort Wayne, Indiana, '
   'USA.')),
 ('src_insightcrime_org_4ce4a84d',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'insightcrime.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico - translocal '
   '(Sonora, Veracruz, Puebla, Tamaulipas, Chiapas, Baja California and other states).')),
 ('src_iom_int_c6fc06e0',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'iom.int legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Morocco / Spain / Western '
   'Euro-African border.')),
 ('src_ipsnews_net_43c5dc87',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'ipsnews.net legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Lebanon — Beirut-based, '
   'helpline serving the country and parts of the wider Arabic-speaking Middle East.')),
 ('src_journals_sagepub_com_246a4219',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'journals.sagepub.com legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Italy and '
   'wider Europe; multiple origin/transit contexts depending on protocol.')),
 ('src_journals_sagepub_com_80918845',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'journals.sagepub.com legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Riohacha, La '
   'Guajira, Colombia.')),
 ('src_khartoumerr_org_57060286',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'khartoumerr.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Sudan — decentralized '
   'conflict-zone mutual-aid networks; public cube must not map base rooms, kitchens, routes, '
   'transfer paths, local contacts, or volunteer identities.')),
 ('src_khulumani_net_6c88b73d',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'khulumani.net legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=South Africa.')),
 ('src_khulumani_net_90f528fc',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'khulumani.net legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=South Africa.')),
 ('src_lab_org_uk_05ff7504',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'lab.org.uk legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico - translocal (Sonora, '
   'Veracruz, Puebla, Tamaulipas, Chiapas, Baja California and other states).')),
 ('src_lacounty_gov_92bc5752',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'lacounty.gov legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=UK / US examples; translocal '
   'office.')),
 ('src_latina_com_0249a505',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'latina.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico / United States media '
   'source.')),
 ('src_laubergedesmigrants_fr_23a60148',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'laubergedesmigrants.fr legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Calais, '
   'Grande-Synthe, Dunkirk, northern France / UK-France border.')),
 ('src_laubergedesmigrants_fr_5544f413',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'laubergedesmigrants.fr legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Calais, '
   'Grande-Synthe, Dunkirk, northern France / UK-France border.')),
 ('src_leva_co_nz_b91e16ef',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'leva.co.nz legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Aotearoa New Zealand / '
   'Pasifika communities nationally.')),
 ('src_mamadragons_org_1e9c6b73',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'mamadragons.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States origin; '
   'online/translocal networks.')),
 ('src_mamadragons_org_60cc63be',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'mamadragons.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States origin; '
   'online/translocal networks.')),
 ('src_mamadragons_org_626c3ba6',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'mamadragons.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States origin; '
   'online/translocal networks.')),
 ('src_mamadragons_org_99684702',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'mamadragons.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States origin; '
   'online/translocal networks.')),
 ('src_manaramagazine_org_a22783e8',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'manaramagazine.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Lalish temple, Sheikhan '
   'district, Duhok Governorate, Kurdistan Region of Iraq; office serves Yazidi survivors of the '
   '2014 ISIS Sinjar genocide and continuing crisis.')),
 ('src_mentalhealth_org_nz_097bc682',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'mentalhealth.org.nz legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Aotearoa New Zealand / '
   'Pasifika communities nationally.')),
 ('src_missingmigrants_iom_int_5a231c6f',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'missingmigrants.iom.int legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Morocco / '
   'Spain / Western Euro-African border.')),
 ('src_multco_us_8ee528cf',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'multco.us legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=UK / US examples; translocal '
   'office.')),
 ('src_mutualaidsudan_org_2e48a97f',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'mutualaidsudan.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Sudan — decentralized '
   'conflict-zone mutual-aid networks; public cube must not map base rooms, kitchens, routes, '
   'transfer paths, local contacts, or volunteer identities.')),
 ('src_newsreview_com_b03945c0',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'newsreview.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States; '
   'originated in San Diego, California; affiliated/local garden network.')),
 ('src_newyorker_com_74fef11c',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'newyorker.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Riohacha, La Guajira, '
   'Colombia.')),
 ('src_nhchc_org_1adcdc50',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'nhchc.org legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pittsburgh, Pennsylvania, USA; '
   'translocal through the Street Medicine Institute field network.')),
 ('src_nyc_gov_536afbc8',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'nyc.gov legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=New York City, New York, USA; '
   'Hart Island / Bronx / public cemetery system.')),
 ('src_nyc_gov_70bee52c',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'nyc.gov legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=New York City, New York, USA; '
   'Hart Island / Bronx / public cemetery system.')),
 ('src_nyc_gov_dfd338af',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'nyc.gov legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=New York City, New York, USA; '
   'Hart Island / Bronx / public cemetery system.')),
 ('src_nyc_gov_e1b0ecf7',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'nyc.gov legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=New York City, New York, USA; '
   'Hart Island / Bronx / public cemetery system.')),
 ('src_nycgovparks_org_37df22d7',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'nycgovparks.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=New York City, New '
   'York, USA; Hart Island / Bronx / public cemetery system.')),
 ('src_nzherald_co_nz_973ee422',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'nzherald.co.nz legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Te Tai Tokerau / '
   'Northland, Aotearoa New Zealand; serving a population of about 179,000.')),
 ('src_oas_org_d12a4efb',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'oas.org legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico - translocal (Sonora, '
   'Veracruz, Puebla, Tamaulipas, Chiapas, Baja California and other states).')),
 ('src_occemeterydistrict_com_ba5d890a',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'occemeterydistrict.com legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States; '
   'originated in San Diego, California; affiliated/local garden network.')),
 ('src_overdoseday_com_f8344cf8',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'overdoseday.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=St Kilda, Melbourne, '
   'Australia (founding 2001); since 2012 coordinated by Penington Institute, Melbourne; now '
   'observed in 40+ countries on 31 August.')),
 ('src_participedia_net_432d442d',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'participedia.net legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=South Africa.')),
 ('src_penington_org_au_6f0a781e',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'penington.org.au legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=St Kilda, Melbourne, '
   'Australia (founding 2001); since 2012 coordinated by Penington Institute, Melbourne; now '
   'observed in 40+ countries on 31 August.')),
 ('src_pittsburghmercy_org_30734742',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pittsburghmercy.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pittsburgh, '
   'Pennsylvania, USA; translocal through the Street Medicine Institute field network.')),
 ('src_pittsburghmercy_org_c4d7b73c',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pittsburghmercy.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pittsburgh, '
   'Pennsylvania, USA; translocal through the Street Medicine Institute field network.')),
 ('src_pmc_ncbi_nlm_nih_gov_ae40a4dd',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pmc.ncbi.nlm.nih.gov legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pittsburgh, '
   'Pennsylvania, USA; translocal through the Street Medicine Institute field network.')),
 ('src_pointsoflight_org_b78d9f08',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pointsoflight.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States; '
   'originated in San Diego, California; affiliated/local garden network.')),
 ('src_pomeps_org_59ccfc2f',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pomeps.org legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Lalish temple, Sheikhan '
   'district, Duhok Governorate, Kurdistan Region of Iraq; office serves Yazidi survivors of the '
   '2014 ISIS Sinjar genocide and continuing crisis.')),
 ('src_pri_org_a90cb5c0',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'pri.org legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Lalish temple, Sheikhan '
   'district, Duhok Governorate, Kurdistan Region of Iraq; office serves Yazidi survivors of the '
   '2014 ISIS Sinjar genocide and continuing crisis.')),
 ('src_qz_com_32311929',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'qz.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Goyang, Seoul, and other South '
   'Korean cities; Nanum and Nanum operates the Seoul Public Funeral consultation hotline ([public '
   'consultation hotline number redacted — non-referral cube]).')),
 ('src_realmamabears_org_39f4dd11',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'realmamabears.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States origin; '
   'online/translocal networks.')),
 ('src_realmamabears_org_9f9a19f9',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'realmamabears.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States origin; '
   'online/translocal networks.')),
 ('src_realmamabears_org_cdd09bb2',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'realmamabears.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States origin; '
   'online/translocal networks.')),
 ('src_reed_edu_8d9fde37',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'reed.edu legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=New York City, New York, USA; '
   'Hart Island / Bronx / public cemetery system.')),
 ('src_refugeecommunitykitchen_org_98f12257',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'refugeecommunitykitchen.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Calais, '
   'Grande-Synthe, Dunkirk, northern France / UK-France border.')),
 ('src_refugeecommunitykitchen_org_ab705a15',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'refugeecommunitykitchen.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Calais, '
   'Grande-Synthe, Dunkirk, northern France / UK-France border.')),
 ('src_refugeesinternational_org_72dbfd68',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'refugeesinternational.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Sudan — '
   'decentralized conflict-zone mutual-aid networks; public cube must not map base rooms, '
   'kitchens, routes, transfer paths, local contacts, or volunteer identities.')),
 ('src_refugiolgbt_org_5dfde4da',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'refugiolgbt.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico — Casa Hogar '
   'Paola Buenrostro in CDMX (opened January 2020); second house Catherinne Danielle Márquez in '
   'Cuernavaca, Morelos (opened February 2022); third house Kaory Catarero Regalado in Apaxco, '
   'Estado de México .')),
 ('src_reliefweb_int_2c41770a',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'reliefweb.int legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Lebanon — Beirut-based, '
   'helpline serving the country and parts of the wider Arabic-speaking Middle East.')),
 ('src_reliefweb_int_aa046293',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'reliefweb.int legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Lalish temple, Sheikhan '
   'district, Duhok Governorate, Kurdistan Region of Iraq; office serves Yazidi survivors of the '
   '2014 ISIS Sinjar genocide and continuing crisis.')),
 ('src_repository_usfca_edu_a287ae1a',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'repository.usfca.edu legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico — Casa '
   'Hogar Paola Buenrostro in CDMX (opened January 2020); second house Catherinne Danielle Márquez '
   'in Cuernavaca, Morelos (opened February 2022); third house Kaory Catarero Regalado in Apaxco, '
   'Estado de México .')),
 ('src_reuters_com_b7abea3d',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'reuters.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico - translocal (Sonora, '
   'Veracruz, Puebla, Tamaulipas, Chiapas, Baja California and other states).')),
 ('src_reuters_com_bc05c81e',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'reuters.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Morocco / Spain / Western '
   'Euro-African border.')),
 ('src_reuters_com_fc8316de',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'reuters.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=South Africa.')),
 ('src_rightlivelihood_org_8c3f8284',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'rightlivelihood.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Sudan — decentralized '
   'conflict-zone mutual-aid networks; public cube must not map base rooms, kitchens, routes, '
   'transfer paths, local contacts, or volunteer identities.')),
 ('src_rsnz_onlinelibrary_wiley_com_5d94adfa',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'rsnz.onlinelibrary.wiley.com legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Te Tai Tokerau '
   '/ Northland, Aotearoa New Zealand; serving a population of about 179,000.')),
 ('src_rstp_ca_117ffbe1',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'rstp.ca legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Canada / sponsored refugees '
   'overseas.')),
 ('src_rstp_ca_a7706af1',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'rstp.ca legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Canada / sponsored refugees '
   'overseas.')),
 ('src_rstp_ca_f64dcffc',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'rstp.ca legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Canada / sponsored refugees '
   'overseas.')),
 ('src_santegidio_org_02b4f7f8',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'santegidio.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Italy and wider Europe; '
   'multiple origin/transit contexts depending on protocol.')),
 ('src_santegidio_org_09740e12',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'santegidio.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Italy and wider Europe; '
   'multiple origin/transit contexts depending on protocol.')),
 ('src_santegidio_org_220296bc',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'santegidio.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Italy and wider Europe; '
   'multiple origin/transit contexts depending on protocol.')),
 ('src_santegidio_org_842032cf',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'santegidio.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Italy and wider Europe; '
   'multiple origin/transit contexts depending on protocol.')),
 ('src_santegidio_org_847d03ec',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'santegidio.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Italy and wider Europe; '
   'multiple origin/transit contexts depending on protocol.')),
 ('src_sarde_podbean_com_4042fb4a',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'sarde.podbean.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Lebanon — Beirut-based, '
   'helpline serving the country and parts of the wider Arabic-speaking Middle East.')),
 ('src_scu_edu_a9ac5560',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'scu.edu legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pittsburgh, Pennsylvania, USA; '
   'translocal through the Street Medicine Institute field network.')),
 ('src_socialscienceinaction_org_a044de78',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'socialscienceinaction.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Sudan — '
   'decentralized conflict-zone mutual-aid networks; public cube must not map base rooms, '
   'kitchens, routes, transfer paths, local contacts, or volunteer identities.')),
 ('src_southeastasiaglobe_com_9c9d3cc6',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'southeastasiaglobe.com legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Chiang Rai '
   'Province, northern Thailand.')),
 ('src_spectrumnews1_com_e082e8f4',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'spectrumnews1.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Worcester, '
   'Massachusetts, USA.')),
 ('src_spid_center_e0a71c4e',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'spid.center legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Moscow and other Russian '
   "regions; First Moscow Hospice (1994), Lighthouse children's hospice (opened October 2019).")),
 ('src_srebrenica_org_uk_31119c18',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'srebrenica.org.uk legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United Kingdom / '
   'Netherlands / Bosnia and Herzegovina.')),
 ('src_stlouisreview_com_92401eb9',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'stlouisreview.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States; '
   'originated in San Diego, California; affiliated/local garden network.')),
 ('src_streetmedicine_org_1f929407',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'streetmedicine.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pittsburgh, '
   'Pennsylvania, USA; translocal through the Street Medicine Institute field network.')),
 ('src_streetmedicine_org_20f00ffe',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'streetmedicine.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pittsburgh, '
   'Pennsylvania, USA; translocal through the Street Medicine Institute field network.')),
 ('src_streetmedicine_org_5af129e1',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'streetmedicine.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pittsburgh, '
   'Pennsylvania, USA; translocal through the Street Medicine Institute field network.')),
 ('src_streetmedicine_org_ec1f95f4',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'streetmedicine.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pittsburgh, '
   'Pennsylvania, USA; translocal through the Street Medicine Institute field network.')),
 ('src_tewhatuora_govt_nz_a480be30',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'tewhatuora.govt.nz legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Te Tai Tokerau / '
   'Northland, Aotearoa New Zealand; serving a population of about 179,000.')),
 ('src_theguardian_com_693f2605',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'theguardian.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Calais, Grande-Synthe, '
   'Dunkirk, northern France / UK-France border.')),
 ('src_theguardian_com_93820ccb',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'theguardian.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pittsburgh, '
   'Pennsylvania, USA; translocal through the Street Medicine Institute field network.')),
 ('src_theguardian_com_b28c1553',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'theguardian.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Morocco / Spain / '
   'Western Euro-African border.')),
 ('src_theguardian_com_fb8f4d98',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'theguardian.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico - translocal '
   '(Sonora, Veracruz, Puebla, Tamaulipas, Chiapas, Baja California and other states).')),
 ('src_thenewhumanitarian_org_246d090e',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'thenewhumanitarian.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Sudan — '
   'decentralized conflict-zone mutual-aid networks; public cube must not map base rooms, '
   'kitchens, routes, transfer paths, local contacts, or volunteer identities.')),
 ('src_thesoutherncross_org_ea897b96',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'thesoutherncross.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=United States; '
   'originated in San Diego, California; affiliated/local garden network.')),
 ('src_theworcesterguardian_org_e63baaf1',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'theworcesterguardian.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Worcester, '
   'Massachusetts, USA.')),
 ('src_time_com_25794036',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'time.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Goyang, Seoul, and other South '
   'Korean cities; Nanum and Nanum operates the Seoul Public Funeral consultation hotline ([public '
   'consultation hotline number redacted — non-referral cube]).')),
 ('src_timep_org_ee7796cb',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'timep.org legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Lebanon — Beirut-based, '
   'helpline serving the country and parts of the wider Arabic-speaking Middle East.')),
 ('src_trc_inquiry_org_za_ce7c2584',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'trc-inquiry.org.za legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=South Africa.')),
 ('src_unfinishedtrc_co_za_195bae0b',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'unfinishedtrc.co.za legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=South Africa.')),
 ('src_unfinishedtrc_co_za_1ecbe232',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'unfinishedtrc.co.za legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=South Africa.')),
 ('src_unfinishedtrc_co_za_98bf2ba9',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'unfinishedtrc.co.za legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=South Africa.')),
 ('src_unfinishedtrc_co_za_b31464aa',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'unfinishedtrc.co.za legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=South Africa.')),
 ('src_unhcr_org_8498a254',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'unhcr.org legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Canada / sponsored refugees '
   'overseas.')),
 ('src_unhcr_org_a58857b2',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'unhcr.org legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Lalish temple, Sheikhan '
   'district, Duhok Governorate, Kurdistan Region of Iraq; office serves Yazidi survivors of the '
   '2014 ISIS Sinjar genocide and continuing crisis.')),
 ('src_unhcr_org_a6077c01',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'unhcr.org legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Chiang Rai Province, northern '
   'Thailand.')),
 ('src_unhcr_org_e4da4d3f',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'unhcr.org legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Riohacha, La Guajira, '
   'Colombia.')),
 ('src_upmc_com_8177da0e',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'upmc.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Pittsburgh, Pennsylvania, USA; '
   'translocal through the Street Medicine Institute field network.')),
 ('src_upstreamjournal_org_f2071384',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'upstreamjournal.org legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Sudan — decentralized '
   'conflict-zone mutual-aid networks; public cube must not map base rooms, kitchens, routes, '
   'transfer paths, local contacts, or volunteer identities.')),
 ('src_utopia56_org_c3cc0534',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'utopia56.org legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Calais, Grande-Synthe, '
   'Dunkirk, northern France / UK-France border.')),
 ('src_vice_com_2f7c3028',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'vice.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Moscow and other Russian '
   "regions; First Moscow Hospice (1994), Lighthouse children's hospice (opened October 2019).")),
 ('src_vice_com_5a8807cb',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'vice.com legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Lalish temple, Sheikhan '
   'district, Duhok Governorate, Kurdistan Region of Iraq; office serves Yazidi survivors of the '
   '2014 ISIS Sinjar genocide and continuing crisis.')),
 ('src_washingtonblade_com_6cddab3f',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'washingtonblade.com legacy internal-only sensitive source reviewed by source-registry metadata '
   'sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Mexico — Casa Hogar '
   'Paola Buenrostro in CDMX (opened January 2020); second house Catherinne Danielle Márquez in '
   'Cuernavaca, Morelos (opened February 2022); third house Kaory Catarero Regalado in Apaxco, '
   'Estado de México .')),
 ('src_wboi_org_29463df8',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'wboi.org legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Fort Wayne, Indiana, USA.')),
 ('src_worldwithoutexploitation_org_e3c015a1',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'worldwithoutexploitation.org legacy internal-only sensitive source reviewed by source-registry '
   'metadata sweep; no-public-archive/no-auto-crawl decision recorded; jurisdiction=Worcester, '
   'Massachusetts, USA.')),
 ('src_wwohp_org_ad66cc90',
  ('manual_registry_metadata_review_no_direct_crawl',
   'manual_sensitive_metadata_completed_no_public_archive',
   'source_date|date_last_checked|last_http_status|language|jurisdiction|archived_copy_status',
   'wwohp.org legacy internal-only sensitive source reviewed by source-registry metadata sweep; '
   'no-public-archive/no-auto-crawl decision recorded; jurisdiction=Worcester, Massachusetts, '
   'USA.'))]
BATCH_DATES['rev0084']='2026-06-13'
BATCH_DATES['rev0083']='2026-06-13'
# rev0086 closes the last three manual-sensitive Srebrenica/Žepa official-source rows
# and records coverage-only dispositions for source ids that already had coherent
# Source Registry metadata but were absent from the cumulative backfill ledger.
BATCHES['rev0086']=[
 ('src_bosniaherzegovina_un_org_0bc4afdb',
  ('official_manual_review_no_public_archive',
   'manual_context_sensitive_verified_no_public_archive',
   'date_last_checked|last_http_status|archived_copy_status|risk_notes|data_governance_notes',
   'UN Bosnia and Herzegovina official-context page manually verified for Srebrenica/Žepa remembrance/justice context; no case, testimony, image, contact, event, route, or archive URL extraction.')),
 ('src_hudoc_echr_coe_int_2c941c2c',
  ('official_hudoc_record_verified_dynamic_no_public_archive',
   'manual_context_sensitive_verified_no_public_archive',
   'date_last_checked|last_http_status|archived_copy_status|risk_notes|data_governance_notes',
   'HUDOC/ECHR official record manually verified as legal-context support for Stichting Mothers of Srebrenica boundary; dynamic HUDOC surface is not mirrored or republished.')),
 ('src_ungeneva_org_1e73a63b',
  ('official_manual_review_no_public_archive',
   'manual_context_sensitive_verified_no_public_archive',
   'date_last_checked|last_http_status|archived_copy_status|risk_notes|data_governance_notes',
   'UN Geneva official-context page manually verified for 30-year Srebrenica remembrance/truth/justice framing; no family testimony, image, vigil, contact, or archive URL extraction.')),
 ('src_afn_ca_0741c255',
  ('ledger_coverage_reconciliation_existing_checked_metadata',
   'coverage_reconciled_existing_verified_metadata',
   'source_metadata_backfill_coverage_only',
   'Existing AFN source metadata/freshness state reconciled into cumulative backfill coverage ledger; no new public expansion.')),
 ('src_amnesty_ca_58860a31',
  ('ledger_coverage_reconciliation_existing_checked_metadata',
   'coverage_reconciled_existing_verified_metadata',
   'source_metadata_backfill_coverage_only',
   'Existing Amnesty Canada source metadata/freshness state reconciled into cumulative backfill coverage ledger; no family-story/name/image/contact expansion.')),
 ('src_mmiwg_ffada_ca_3fd59200',
  ('ledger_coverage_reconciliation_existing_checked_metadata',
   'coverage_reconciled_existing_verified_metadata',
   'source_metadata_backfill_coverage_only',
   'Existing National Inquiry source metadata/freshness state reconciled into cumulative backfill coverage ledger; no archive or public-surface expansion.')),
 ('src_rcaanc_cirnac_gc_ca_6dbf4fc4',
  ('ledger_coverage_reconciliation_existing_checked_metadata',
   'coverage_reconciled_existing_verified_metadata',
   'source_metadata_backfill_coverage_only',
   'Existing Crown-Indigenous Relations source metadata/freshness state reconciled into cumulative backfill coverage ledger; no public expansion.')),
]
BATCH_DATES['rev0086']='2026-06-13'
DECISION_RECORDED={'manual_sensitive_metadata_completed_no_public_archive'}
CONTEXT_DECISION_RECORDED={'manual_context_sensitive_verified_no_public_archive'}
COVERAGE_ONLY={'coverage_reconciled_existing_verified_metadata'}

SAFETY={'safety_reclassified_no_public_url'}
BLOCKED={'blocked_visible_recheck_needed'}
REQUIRED_METADATA=['source_date','date_last_checked','last_http_status','language','jurisdiction']

def read_csv(path: Path):
    if not path.exists(): return []
    with path.open(encoding='utf-8', newline='') as f: return list(csv.DictReader(f))

BATCHES['rev0087'] = [
    ('src_leginfo_legislature_ca_gov_80dc2002', ('web_open_official_context', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'California HSC fetal-death registration provisions verified as official context for Garden category-boundary audit; no legal advice or case extraction.')),
    ('src_leginfo_legislature_ca_gov_e150740a', ('web_open_official_context', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'California HSC 7100 disposition-control statute verified as official context for family-authority boundary; no legal advice or case extraction.')),
    ('src_information_auditor_ca_gov_83183292', ('web_open_official_context', 'completed_verified_metadata', 'source_date|date_last_checked|last_http_status|language|jurisdiction', 'California State Auditor fetal-death registration audit verified as official context for delay/process risk; no case extraction.')),
]
BATCH_DATES['rev0087'] = '2026-06-13'

def missing_metadata(src: dict) -> list[str]:
    out=[]
    for f in REQUIRED_METADATA:
        v=(src.get(f,'') or '').strip()
        if v in {'', 'unknown'} or (f=='last_http_status' and v.startswith('not_checked_by_')):
            out.append(f)
    return out

def run(root: Path):
    source_by={r.get('source_id',''):r for r in read_csv(root/'Source-Registry-current.csv')}
    maint_by={r.get('source_id',''):r for r in read_csv(root/'META/Source-Maintenance-Priority-current.csv')}
    latest_status_by_source={}
    for batch_revision, entries in BATCHES.items():
        for sid,(_mode,bstatus,_fields,_note) in entries:
            latest_status_by_source[sid]=bstatus
    rows=[]
    idx=0
    for batch_revision, entries in BATCHES.items():
        for sid,(mode,bstatus,fields,note) in entries:
            idx+=1
            src=source_by.get(sid,{})
            maint=maint_by.get(sid,{})
            priority=maint.get('maintenance_priority','missing_maintenance_row')
            problems=[]
            if not src: problems.append('missing source row')
            if not maint: problems.append('missing maintenance priority row')
            if bstatus in COMPLETED:
                if priority.startswith('p1_public_context_metadata_repair'):
                    problems.append('completed row still classified P1 metadata repair')
                mm=missing_metadata(src)
                if mm: problems.append('completed row still has missing metadata field(s): '+','.join(mm))
            if bstatus in BLOCKED:
                if latest_status_by_source.get(sid)==bstatus:
                    if not priority.startswith('p1_public_context_metadata_repair'):
                        problems.append('blocked-visible row should remain P1-visible')
                else:
                    # A later batch completed or safety-reclassified this source. Keep the historical
                    # blocked-visible row for audit trail, but do not require the current queue to stay blocked.
                    pass
            if bstatus in SAFETY:
                policy=(src.get('public_link_policy','') or '')
                decision=(maint.get('public_url_release_decision','') or '')
                safe=(src.get('safe_to_recheck_automatically','') or '')
                if not (priority.startswith('p1_manual_sensitive_preservation') or priority.startswith('p2_sensitive_preservation_decision_recorded')):
                    problems.append('safety row should remain manual-sensitive P1 or recorded-decision P2')
                if not policy.startswith('internal_only'):
                    problems.append('safety row public_link_policy is not internal_only')
                if decision != 'block_public_url':
                    problems.append('safety row public URL decision is not blocked')
                if safe not in {'do_not_auto_recheck','manual_review_required'}:
                    problems.append('safety row recheck posture is not manual/blocked')
                mm=missing_metadata(src)
                if mm: problems.append('safety row still has missing metadata field(s): '+','.join(mm))
            if 'DECISION_RECORDED' in globals() and bstatus in DECISION_RECORDED:
                policy=(src.get('public_link_policy','') or '')
                decision=(maint.get('public_url_release_decision','') or '')
                safe=(src.get('safe_to_recheck_automatically','') or '')
                arch=(src.get('archived_copy_status','') or '')
                archive_url=(src.get('archive_url_or_archive_id','') or '')
                if priority != 'p2_sensitive_preservation_decision_recorded':
                    problems.append('decision-recorded batch row should be p2_sensitive_preservation_decision_recorded')
                if not policy.startswith('internal_only'):
                    problems.append('decision-recorded batch public_link_policy is not internal_only')
                if decision != 'block_public_url':
                    problems.append('decision-recorded batch public URL decision is not blocked')
                if safe != 'do_not_auto_recheck':
                    problems.append('decision-recorded batch recheck posture is not do_not_auto_recheck')
                if arch != 'manual_preservation_decision_recorded_no_public_archive':
                    problems.append('decision-recorded batch archived_copy_status is not no-public-archive decision')
                if archive_url:
                    problems.append('decision-recorded batch must not carry an archive URL/id')
                mm=missing_metadata(src)
                if mm: problems.append('decision-recorded batch still has missing metadata field(s): '+','.join(mm))
            if 'CONTEXT_DECISION_RECORDED' in globals() and bstatus in CONTEXT_DECISION_RECORDED:
                policy=(src.get('public_link_policy','') or '')
                decision=(maint.get('public_url_release_decision','') or '')
                safe=(src.get('safe_to_recheck_automatically','') or '')
                arch=(src.get('archived_copy_status','') or '')
                archive_url=(src.get('archive_url_or_archive_id','') or '')
                if priority != 'p2_sensitive_preservation_decision_recorded':
                    problems.append('context decision-recorded row should be p2_sensitive_preservation_decision_recorded')
                if policy not in {'public_link_allowed_with_boundary_note','boundary_note_required'}:
                    problems.append('context decision-recorded row must remain boundary-note/manual-review only')
                if decision not in {'allow_only_with_boundary_note_after_manual_review','allow_after_context_review'}:
                    problems.append('context decision-recorded row public URL decision is not manual boundary-note limited')
                if safe != 'manual_review_required':
                    problems.append('context decision-recorded row recheck posture is not manual_review_required')
                if arch != 'manual_preservation_decision_recorded_no_public_archive':
                    problems.append('context decision-recorded row archived_copy_status is not no-public-archive decision')
                if archive_url:
                    problems.append('context decision-recorded row must not carry an archive URL/id')
                mm=missing_metadata(src)
                if mm: problems.append('context decision-recorded row still has missing metadata field(s): '+','.join(mm))
            if 'COVERAGE_ONLY' in globals() and bstatus in COVERAGE_ONLY:
                mm=missing_metadata(src)
                if mm: problems.append('coverage-only row still has missing metadata field(s): '+','.join(mm))
            exposure='no public URL/prose/contact/referral/route/case expansion; metadata repair only'
            if bstatus in SAFETY:
                exposure='public URL blocked; no contact/referral/route/service/case/story expansion; internal source context only'
            elif 'DECISION_RECORDED' in globals() and bstatus in DECISION_RECORDED:
                exposure='metadata/freshness repaired and no-public-archive/no-auto-crawl decision recorded; no public URL/contact/referral/route/support/shelter/service expansion'
            elif 'CONTEXT_DECISION_RECORDED' in globals() and bstatus in CONTEXT_DECISION_RECORDED:
                exposure='official/context source manually verified; no public archive URL, no automatic crawl, and no case/testimony/image/contact/event/legal-advice extraction'
            elif 'COVERAGE_ONLY' in globals() and bstatus in COVERAGE_ONLY:
                exposure='coverage reconciliation only; existing metadata state counted without public URL/prose/contact/referral/route/case expansion'
            elif bstatus in BLOCKED:
                if latest_status_by_source.get(sid)==bstatus:
                    exposure='blocked case remains visible; no completion claim and no public expansion'
                else:
                    exposure='historical blocked case superseded by later verified metadata or safety reclassification; no public expansion'
            rows.append({
                'backfill_id':f'smb_{idx:04d}',
                'batch_revision':batch_revision,
                'source_id':sid,
                'domain':src.get('domain',''),
                'candidate_ids':src.get('candidate_ids',''),
                'verification_mode':mode,
                'backfill_status':bstatus,
                'fields_updated':fields,
                'date_checked':BATCH_DATES.get(batch_revision,'2026-06-13'),
                'maintenance_priority_after':priority,
                'public_exposure_effect':exposure,
                'evidence_note':note,
                'status':'fail' if problems else 'pass',
                'note':'; '.join(problems) if problems else 'cumulative source-health backfill outcome is coherent with source-maintenance queue',
            })
    return rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-fail', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report:
        write_csv_json_md_report(root,'META/Source-Metadata-Backfill-current.csv',FIELDS,rows,'Source Metadata Backfill','tools/source_metadata_backfill_log.py',columns=['backfill_id','batch_revision','source_id','domain','backfill_status','maintenance_priority_after','status','note'],intro_lines=['Cumulative rev0077–rev0087 source-health ledger. It records metadata repair, safety reclassification, context-sensitive manual verification, coverage reconciliation, and blocked-visible cases without authorizing public-source expansion.','Safety reclassification rows intentionally move contact, route, support, service, housing, shelter, aftercare, child/residential-care, death-record, or case-detail surfaces into internal-only/manual preservation posture; metadata-ready rows may move to P2 recorded-decision watch without public expansion; rev0083 adds a Pacific crisis/GBV/support cohort validation path; rev0084 adds a non-Pacific/internal-only legacy manual-sensitive sweep with no direct crawl and no public archive decisions; rev0086 closes the remaining Srebrenica/Žepa official-context source debt and adds seven coverage rows; rev0087 adds Garden of Innocence legal/auditor context sources for category/family-consent boundary audit without case, service, or legal-advice expansion.'],max_md_rows=160)
    bad=[r for r in rows if r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} source metadata backfill rows={len(rows)} fail={len(bad)}")
    if args.fail_on_fail and bad: sys.exit(1)
if __name__=='__main__': main()
