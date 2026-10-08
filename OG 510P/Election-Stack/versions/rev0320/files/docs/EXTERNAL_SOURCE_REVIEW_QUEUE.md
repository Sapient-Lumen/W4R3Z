# External source review queue (generated; no URLs)

**Track:** Shared


Generated from `evidence/lock/external-sources.toml`.

Purpose: keep unpinned-source drift risk **visible and bounded** without expanding the archive.

Notes:
- Sorted by `review_by` (earliest first), then by a small heuristic priority score.
- `refs` counts total `source:` + `xref:` occurrences across in-repo markdown.
- `docs` shows up to 6 numbered docs that reference the ID (as `DOC:docs/<file>.md`).

Unpinned entries: 38

| review_by | id | exemption | retrieved | refs | tags | docs (top) |
|---|---|---|---|---:|---|---|
| 2026-05-15 | `arxiv_more_style_less_work_2012_03371_pdf` | temporary | 2026-02-22 | 1 | audit,rla,card_style_data | `DOC:docs/36-risk-limiting-audits-integration.md` |
| 2026-05-15 | `arxiv_stylish_rla_in_practice_2309_09081_pdf` | temporary | 2026-02-22 | 1 | audit,rla,card_style_data | `DOC:docs/36-risk-limiting-audits-integration.md` |
| 2026-05-15 | `eac_enr_securing_results_checklist_pdf` | temporary | 2026-02-26 | 2 | eac,enr,results_reporting,checklist | `DOC:docs/63-election-night-reporting-and-public-results-security.md`; (+1 other) |
| 2026-05-15 | `rfc9116_txt` | temporary | 2026-02-27 | 1 | security,http,rfc,comms | `DOC:docs/199-official-surface-security-snapshots.md` |
| 2026-05-15 | `cisa_voluntary_incident_reporting_guidance_2024_pdf` | temporary | 2026-02-22 | 2 | cisa,incident_reporting,election_security | `DOC:docs/186-incident-communications-as-evidence.md`, `DOC:docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md` |
| 2026-05-15 | `usenix_intoto_pipeline_integrity_pdf` | temporary | 2026-02-22 | 3 | in_toto,supply_chain,pipeline_integrity,paper | `DOC:docs/08-operations.md`, `DOC:docs/10-assurance-plan.md`, `DOC:docs/17-supply-chain-and-build-integrity.md` |
| 2026-05-15 | `c2pa_content_credentials_spec_2_2_pdf` | temporary | 2026-02-22 | 4 | c2pa,content_credentials,synthetic_media,provenance | `DOC:docs/37-public-evidence-and-disinformation-resilience.md`, `DOC:docs/172-open-research-questions-and-experiment-backlog.md`, `DOC:docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`, `DOC:docs/207-research-agenda-and-revision-ledger.md` |
| 2026-05-15 | `mit_omniballot_analysis_2020_pdf` | temporary | 2026-02-26 | 3 | remote_return,case_study,client_security,paper | `DOC:docs/06-client-security.md`, `DOC:docs/11-case-studies.md`; (+1 other) |
| 2026-05-15 | `estonia_ivote_security_analysis_2014_pdf` | temporary | 2026-02-26 | 2 | remote_return,case_study,operational_security,paper | `DOC:docs/11-case-studies.md`; (+1 other) |
| 2026-05-15 | `ifes_results_management_cybersecurity_briefing_pdf` | temporary | 2026-02-26 | 2 | ifes,enr,results_management,cybersecurity | `DOC:docs/63-election-night-reporting-and-public-results-security.md`; (+1 other) |
| 2026-05-15 | `usenix_democracylive_security_2021_pdf` | temporary | 2026-02-26 | 2 | remote_return,case_study,client_security,paper | `DOC:docs/11-case-studies.md`; (+1 other) |
| 2026-05-15 | `usenix_electionguard_toolkit_2024_pdf` | temporary | 2026-02-26 | 2 | e2e,electionguard,paper | `DOC:docs/11-case-studies.md`; (+1 other) |
| 2026-05-31 | `eac_e2e_protocol_evaluation_process_page` | mutable | 2026-02-22 | 3 | eac,vvsg,e2e | `DOC:docs/10-assurance-plan.md`, `DOC:docs/19-certification-and-standards-alignment.md`; (+1 other) |
| 2026-05-31 | `nist_sp800_161r1_final_html` | mutable | 2026-02-22 | 4 | nist,c_scrm,supply_chain | `DOC:docs/08-operations.md`, `DOC:docs/10-assurance-plan.md`, `DOC:docs/17-supply-chain-and-build-integrity.md`; (+1 other) |
| 2026-05-31 | `nist_sp800_218_final_html` | mutable | 2026-02-22 | 4 | nist,ssdf,secure_development,supply_chain | `DOC:docs/08-operations.md`, `DOC:docs/10-assurance-plan.md`, `DOC:docs/17-supply-chain-and-build-integrity.md`; (+1 other) |
| 2026-05-31 | `slsa_provenance_v1_html` | blocked | 2026-02-21 | 3 | slsa,provenance,supply_chain | `DOC:docs/97-supply-chain-attestations-for-verifiers.md`, `DOC:docs/170-slsa-and-intoto-provenance-profile.md` |
| 2026-05-31 | `cisa_tactics_of_disinformation_508_pdf` | blocked | 2026-02-22 | 2 | cisa,disinformation,comms | `DOC:docs/37-public-evidence-and-disinformation-resilience.md`, `DOC:docs/207-research-agenda-and-revision-ledger.md` |
| 2026-05-31 | `nist_irb_overview_html` | blocked | 2026-02-21 | 2 | nist,randomness,beacon | `DOC:docs/168-public-randomness-beacons-and-seeded-sampling.md` |
| 2026-05-31 | `nist_sp800_218_r1_ipd_html` | mutable | 2026-02-22 | 2 | nist,ssdf,draft | `DOC:docs/08-operations.md`, `DOC:docs/10-assurance-plan.md` |
| 2026-05-31 | `cisa_rumorcontrol_page` | mutable | 2026-02-22 | 6 | cisa,rumor_control,disinformation,election_security | `DOC:docs/37-public-evidence-and-disinformation-resilience.md`, `DOC:docs/186-incident-communications-as-evidence.md`, `DOC:docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`, `DOC:docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`, `DOC:docs/197-precinct-closeout-evidence-capture-and-publication.md`, `DOC:docs/198-precinct-closeout-index-and-omission-detection.md` |
| 2026-05-31 | `slsa_spec_v1_1_html` | blocked | 2026-02-21 | 6 | slsa,supply_chain | `DOC:docs/08-operations.md`, `DOC:docs/17-supply-chain-and-build-integrity.md`, `DOC:docs/97-supply-chain-attestations-for-verifiers.md`, `DOC:docs/170-slsa-and-intoto-provenance-profile.md`; (+1 other) |
| 2026-05-31 | `cisa_electronic_ballot_risk_mgmt_2020_pdf` | blocked | 2026-02-21 | 3 | cisa,electronic_ballot,risk | `DOC:docs/21-external-artifacts-reading-list.md`, `DOC:docs/207-research-agenda-and-revision-ledger.md`; (+1 other) |
| 2026-05-31 | `eac_communicating_election_post_election_toolkit_2026_page` | mutable | 2026-02-22 | 3 | eac,public_comms,toolkit | `DOC:docs/186-incident-communications-as-evidence.md`, `DOC:docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`, `DOC:docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md` |
| 2026-05-31 | `nist_voting_security_recommendations_page` | mutable | 2026-02-22 | 2 | nist,election_security,operations | `DOC:docs/08-operations.md`; (+1 other) |
| 2026-05-31 | `cisa_bod_18_01_page` | mutable | 2026-02-22 | 5 | cisa,comms,email,web,baseline_controls | `DOC:docs/37-public-evidence-and-disinformation-resilience.md`, `DOC:docs/45-routing-dns-availability-attacks.md`, `DOC:docs/186-incident-communications-as-evidence.md`, `DOC:docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`, `DOC:docs/207-research-agenda-and-revision-ledger.md` |
| 2026-05-31 | `tuf_spec_latest_html` | mutable | 2026-02-22 | 4 | tuf,secure_updates,supply_chain | `DOC:docs/08-operations.md`, `DOC:docs/10-assurance-plan.md`, `DOC:docs/17-supply-chain-and-build-integrity.md`; (+1 other) |
| 2026-05-31 | `cisa_best_practices_securing_election_systems_page` | mutable | 2026-02-22 | 3 | cisa,election_security,operations,best_practices | `DOC:docs/19-certification-and-standards-alignment.md`, `DOC:docs/68-results-pipeline-end-to-end.md`, `DOC:docs/186-incident-communications-as-evidence.md` |
| 2026-05-31 | `nist_enr_security_enr_use_case_page` | mutable | 2026-02-26 | 2 | nist,enr,results_reporting,security | `DOC:docs/63-election-night-reporting-and-public-results-security.md`; (+1 other) |
| 2026-05-31 | `cisa_time_guidance_network_operators_2023_pdf` | blocked | 2026-02-22 | 1 | cisa,time,operations | `DOC:docs/192-time-attestation-and-timestamping-as-evidence.md` |
| 2026-05-31 | `cisa_election_ir_comms_guide_page` | mutable | 2026-02-21 | 1 | cisa,incident_comms | `DOC:docs/186-incident-communications-as-evidence.md` |
| 2026-05-31 | `intoto_specs_html` | blocked | 2026-02-21 | 1 | in_toto,supply_chain,attestation | `DOC:docs/170-slsa-and-intoto-provenance-profile.md` |
| 2026-05-31 | `drand_docs_overview_html` | blocked | 2026-02-21 | 2 | randomness,beacon,drand | `DOC:docs/168-public-randomness-beacons-and-seeded-sampling.md` |
| 2026-05-31 | `schneier_swiss_evoting_vulnerability_2023_post` | mutable | 2026-02-26 | 1 | evoting,case_study,vulnerability,blog | `DOC:docs/06-client-security.md` |
| 2026-05-31 | `intoto_envelope_v1_md` | blocked | 2026-02-27 | 4 | in_toto,dsse,attestation | `DOC:docs/97-supply-chain-attestations-for-verifiers.md`, `DOC:docs/238-results-release-packages-as-evidence-envelopes.md`; (+2 other) |
| 2026-05-31 | `electionguard_spec_page` | mutable | 2026-02-26 | 2 | e2e,electionguard,spec,toolkit | `DOC:docs/11-case-studies.md`; (+1 other) |
| 2026-05-31 | `swiss_post_uv_flaw_disclosure_2019_page` | mutable | 2026-02-26 | 2 | case_study,universal_verifiability,disclosure,evoting | `DOC:docs/11-case-studies.md`; (+1 other) |
| 2026-05-31 | `swtch_tlog_design_notes_page` | mutable | 2026-02-26 | 2 | ct,transparency,design_notes | `DOC:docs/11-case-studies.md`; (+1 other) |
| 2026-05-31 | `draft_scitt_refusal_events_02_html` | mutable | 2026-02-22 | 1 | ietf,scitt,transparency_log,refusal | `DOC:docs/167-non-claims-and-boundaries.md` |
