# 214. External sources index (lockfile IDs, no URLs)

**Track:** Shared


Generated from `evidence/lock/external-sources.toml`. This index is intentionally **no‑URL** to reduce link rot and avoid bundling third‑party artifacts.

How to cite in docs: `source: <id>`. For pinning policy and precedence, see `docs/151` and `docs/161` (pin exemptions: `docs/228`).

## Summary

- Total sources: 87 (pinned: 49; unpinned: 38).
- Unpinned entries carry an explicit `pin_exemption` + `review_by` triage marker; treat as informative until sha256 is pinned (see docs/151 and docs/228).
- Maintainer queue (generated): see `docs/EXTERNAL_SOURCE_REVIEW_QUEUE.md`.
- Pin-first candidates (highest leverage unpinned IDs):
  - `eac_e2e_protocol_evaluation_process_page` (refs: 3; tags: eac,vvsg,e2e)
  - `nist_sp800_161r1_final_html` (refs: 4; tags: nist,c_scrm,supply_chain)
  - `nist_sp800_218_final_html` (refs: 4; tags: nist,ssdf,secure_development,supply_chain)
  - `slsa_provenance_v1_html` (refs: 3; tags: slsa,provenance,supply_chain)
  - `arxiv_more_style_less_work_2012_03371_pdf` (refs: 1; tags: audit,rla,card_style_data)
  - `arxiv_stylish_rla_in_practice_2309_09081_pdf` (refs: 1; tags: audit,rla,card_style_data)
  - `cisa_tactics_of_disinformation_508_pdf` (refs: 2; tags: cisa,disinformation,comms)
  - `nist_irb_overview_html` (refs: 2; tags: nist,randomness,beacon)

| id | pinned | retrieved | exemption | review_by | tags | note |
|---|---|---|---|---|---|---|
| `arxiv_more_style_less_work_2012_03371_pdf` | no | 2026-02-22 | temporary | 2026-05-15 | audit,rla,card_style_data | Glazer, Spertus, Stark (2020): 'More style, less work' (card-style data for RLAs). PDF cited (not bundled); pin sha256 once fetched. |
| `arxiv_stylish_rla_in_practice_2309_09081_pdf` | no | 2026-02-22 | temporary | 2026-05-15 | audit,rla,card_style_data | Glazer, Spertus, Stark (2023): Stylish Risk-Limiting Audits in Practice. PDF cited (not bundled); pin sha256 once fetched. |
| `c2pa_content_credentials_spec_2_2_pdf` | no | 2026-02-22 | temporary | 2026-05-15 | c2pa,content_credentials,synthetic_media,provenance | C2PA Content Credentials technical specification (v2.2 PDF). Used as an informative reference for optional provenance of official media artifacts; do not bundle bytes. sha256 pending; treat as informative until pinned. |
| `cisa_best_practices_securing_election_systems_page` | no | 2026-02-22 | mutable | 2026-05-31 | cisa,election_security,operations,best_practices | CISA best practices for securing election systems (includes guidance relevant to public-facing sites and comms operations). HTML is mutable; treat as informative until pinned. |
| `cisa_bod_18_01_page` | no | 2026-02-22 | mutable | 2026-05-31 | cisa,comms,email,web,baseline_controls | CISA BOD 18-01 (Enhance Email and Web Security). Useful baseline controls for official comms channels (HTTPS, email authentication). HTML is mutable; treat as informative until pinned. |
| `cisa_election_ir_comms_guide_page` | no | 2026-02-21 | mutable | 2026-05-31 | cisa,incident_comms | Landing page for the joint EAC/CISA incident response communications guide; automated retrieval may be blocked. Pin sha256 once fetched via a permitted channel. |
| `cisa_electronic_ballot_risk_mgmt_2020_pdf` | no | 2026-02-21 | blocked | 2026-05-31 | cisa,electronic_ballot,risk | Authoritative joint CISA/EAC/FBI/NIST risk assessment; automated retrieval may be blocked (403). Pin sha256 once fetched via a permitted channel. |
| `cisa_rumorcontrol_page` | no | 2026-02-22 | mutable | 2026-05-31 | cisa,rumor_control,disinformation,election_security | CISA Election Security Rumor vs. Reality landing page ('rumorcontrol'). Mutable HTML; treat as informative until pinned. |
| `cisa_tactics_of_disinformation_508_pdf` | no | 2026-02-22 | blocked | 2026-05-31 | cisa,disinformation,comms | CISA: 'Tactics of Disinformation' (PDF). Automated retrieval may be blocked (403); cite without bundling bytes. |
| `cisa_time_guidance_network_operators_2023_pdf` | no | 2026-02-22 | blocked | 2026-05-31 | cisa,time,operations | CISA time guidance for network operators (PDF). Access may be restricted (403) in some environments; record as best-effort citation without bundling bytes. |
| `cisa_voluntary_incident_reporting_guidance_2024_pdf` | no | 2026-02-22 | temporary | 2026-05-15 | cisa,incident_reporting,election_security | CISA: Voluntary Incident Reporting Guidance for Election Infrastructure stakeholders (June 2024). PDF is cited (not bundled); pin sha256 once fetched via a permitted channel. |
| `draft_ietf_ntp_roughtime_17_txt` | yes | 2026-02-22 |  |  | time,roughtime,ietf_draft | Roughtime (IETF NTP WG) draft-ietf-ntp-roughtime-17 (Feb 21 2026). |
| `draft_scitt_architecture_22_txt` | yes | 2026-02-21 |  |  | scitt,transparency,supply_chain | SCITT architecture draft (version -22, Oct 10 2025). |
| `draft_scitt_receipts_ccf_profile_00_txt` | yes | 2026-02-21 |  |  | scitt,receipts | SCITT receipts CCF profile Internet-Draft (version -00). |
| `draft_scitt_refusal_events_02_html` | no | 2026-02-22 | mutable | 2026-05-31 | ietf,scitt,transparency_log,refusal | IETF individual draft (Kamimura et al., 2026): Verifiable AI Refusal Events using SCITT Transparency Logs. Drafts change; treat as informative until pinned. |
| `draft_scitt_scrapi_07_txt` | yes | 2026-02-21 |  |  | scitt,api | SCITT Reference APIs (SCRAPI) Internet-Draft (version -07, Feb 2026). |
| `drand_docs_overview_html` | no | 2026-02-21 | blocked | 2026-05-31 | randomness,beacon,drand | drand distributed randomness beacon docs; sha256 intentionally blank because automated fetch of HTML may be blocked in some environments. |
| `eac_ai_toolkit_2023_pdf` | yes | 2026-02-22 |  |  | eac,ai,synthetic_media,comms | EAC: AI Toolkit for Election Officials (Aug 2023). Hash pinned; PDF not bundled. |
| `eac_communicating_election_post_election_toolkit_2026_page` | no | 2026-02-22 | mutable | 2026-05-31 | eac,public_comms,toolkit | EAC web toolkit (Feb 2026): Communicating election and post-election processes. SHA blank (HTML; pin when fetched via permitted channel). |
| `eac_e2e_protocol_evaluation_process_page` | no | 2026-02-22 | mutable | 2026-05-31 | eac,vvsg,e2e | EAC page describing the public E2E protocol evaluation/approval process intended to support VVSG 2.0 certification. HTML is mutable; treat as informative until pinned. |
| `eac_e2e_protocols_draft_tgdc_2023_pdf` | yes | 2026-02-21 |  |  | e2e,vvsg | EAC/NIST E2E verifiable protocol draft for TGDC (Jan 2023). |
| `eac_enhancing_election_security_public_comms_2024_pdf` | yes | 2026-02-22 |  |  | eac,cisa,public_comms,election_security | EAC/CISA guidance: Enhancing Election Security Through Public Communications (PDF). Hash pinned; PDF not bundled. |
| `eac_enr_securing_results_checklist_pdf` | no | 2026-02-26 | temporary | 2026-05-15 | eac,enr,results_reporting,checklist | EAC checklist for securing election-night results reporting (ENR). PDF is not yet sha256-pinned; treat as informative until pinned. |
| `eac_incident_response_comms_guide_pdf` | yes | 2026-02-21 |  |  | eac,cisa,incident_comms,public_comms | Pinned hash only (PDF not bundled). Used for incident communications process references (docs/186). |
| `eac_vvsg2_test_assertions_v1_4_pdf` | yes | 2026-02-21 |  |  | vvsg,certification | VVSG 2.0 Test Assertions v1.4 (published Jan 30, 2026). |
| `electionguard_spec_page` | no | 2026-02-26 | mutable | 2026-05-31 | e2e,electionguard,spec,toolkit | ElectionGuard specifications landing page. Mutable HTML; treat as informative unless a pinned snapshot/spec artifact is added. |
| `estonia_ivote_security_analysis_2014_pdf` | no | 2026-02-26 | temporary | 2026-05-15 | remote_return,case_study,operational_security,paper | Springall et al. (ACM CCS 2014): Estonia I-voting security analysis. Used as a cautionary case study on operational/client trust and verification complexity; cite without bundling. sha256 pending; treat as informative until pinned. |
| `ifes_results_management_cybersecurity_briefing_pdf` | no | 2026-02-26 | temporary | 2026-05-15 | ifes,enr,results_management,cybersecurity | IFES briefing paper on cybersecurity of election results management systems. PDF is not yet sha256-pinned; treat as informative until pinned. |
| `intoto_envelope_v1_md` | no | 2026-02-27 | blocked | 2026-05-31 | in_toto,dsse,attestation | in-toto Attestation Framework envelope layer (DSSE v1.0) spec (raw markdown). Used as an informative reference for DSSE-wrapped attestations interoperability (docs/238). |
| `intoto_slsa_provenance_predicate_md` | yes | 2026-02-21 |  |  | in_toto,slsa,provenance | in-toto predicate: SLSA Provenance (Type URI and migration notes). |
| `intoto_specs_html` | no | 2026-02-21 | blocked | 2026-05-31 | in_toto,supply_chain,attestation | in-toto specs index page; sha256 intentionally blank because automated fetch of HTML may be blocked in some environments. |
| `intoto_statement_v1_md` | yes | 2026-02-21 |  |  | in_toto,attestation | in-toto Attestation: Statement v1 (raw markdown). |
| `mit_omniballot_analysis_2020_pdf` | no | 2026-02-26 | temporary | 2026-05-15 | remote_return,case_study,client_security,paper | Specter & Halderman (MIT, 2020): OmniBallot security analysis. Cited for browser/client attack surface risks in remote ballot workflows; do not bundle bytes. sha256 pending; treat as informative until pinned. |
| `nasem_securing_the_vote_highlights_pdf` | yes | 2026-02-21 |  |  | nasem,paper,audit | National Academies highlights for 'Securing the Vote' (2018). |
| `ndss_2024_public_inspections_monitors_pdf` | yes | 2026-02-24 |  |  | ct,monitoring,ndss,research | NDSS 2024 paper: 'Certificate Transparency Revisited: The Public Inspections on Third-party Monitors' (Sun et al.). Used as a CT monitor/watchers reference for monitor reliability gaps. |
| `nist_ai_rmf_100_1_pdf` | yes | 2026-02-22 |  |  | nist,ai,risk,rmf | NIST AI 100-1: Artificial Intelligence Risk Management Framework (AI RMF) 1.0 (PDF). |
| `nist_csf2_0_pdf` | yes | 2026-02-22 |  |  | nist,csf,risk_management | NIST Cybersecurity Framework (CSF) 2.0 (CSWP 29, Feb 26 2024). |
| `nist_enr_security_enr_use_case_page` | no | 2026-02-26 | mutable | 2026-05-31 | nist,enr,results_reporting,security | NIST election night reporting (ENR) security discussion/use case. HTML is mutable; treat as informative until pinned. |
| `nist_gcr_24_058_cdf_implementation_guidance_pdf` | yes | 2026-02-26 |  |  | cdf,nist,interoperability,implementation_guidance | NIST GCR 24-058 (2024): Implementation Guidance for Common Data Formats. Practical cross-CDF mapping, identifiers, and processing guidance. |
| `nist_irb_overview_html` | no | 2026-02-21 | blocked | 2026-05-31 | nist,randomness,beacon | NIST Interoperable Randomness Beacons overview page; sha256 intentionally blank because automated fetch of HTML may be blocked in some environments. |
| `nist_sp1500_100r2_err_pdf` | yes | 2026-02-26 |  |  | cdf,nist,err,results_reporting,enr | NIST SP 1500-100r2: Election Results Reporting (ERR) Common Data Format specification (rev 2.0). Reference for structured results reporting + disclosure policy. |
| `nist_sp1500_101_eel_pdf` | yes | 2026-02-26 |  |  | cdf,nist,eel,event_logging,logging | NIST SP 1500-101 (Apr 2020): Election Event Logging (EEL) Common Data Format specification. Reference for publishable log commitments + incident forensics. |
| `nist_sp1500_102_vri_pdf` | yes | 2026-02-26 |  |  | cdf,nist,vri,voter_registration,registration | NIST SP 1500-102 (Nov 2019): Voter Records Interchange (VRI) Common Data Format specification. Reference for registration/eligibility interchange. |
| `nist_sp1500_103_cvr_pdf` | yes | 2026-02-26 |  |  | cdf,nist,cvr,cast_vote_records,audit | NIST SP 1500-103 (Nov 2019): Cast Vote Records (CVR) Common Data Format specification. Load-bearing for reproducible tabulation + audit bridging. |
| `nist_sp1500_20_bd_pdf` | yes | 2026-02-26 |  |  | cdf,nist,bd,ballot_definition | NIST SP 1500-20 (Jan 2023): Ballot Definition (BD) Common Data Format specification. Core reference for BD hashing + interoperability in Track A. |
| `nist_sp800_122_pdf` | yes | 2026-02-26 |  |  | nist,pii,privacy,incident | NIST SP 800-122: Guide to Protecting the Confidentiality of PII. Reference for PII minimization and handling in publishable artifacts (docs/189). |
| `nist_sp800_161r1_final_html` | no | 2026-02-22 | mutable | 2026-05-31 | nist,c_scrm,supply_chain | NIST SP 800-161r1 Cybersecurity Supply Chain Risk Management Practices (C-SCRM) final landing page. Pin sha256 once fetched via a stable channel. |
| `nist_sp800_204d_pdf` | yes | 2026-02-21 |  |  | nist,supply_chain,cicd,attestation | NIST SP 800-204D (2024): strategies for integrating software supply-chain security into CI/CD pipelines. |
| `nist_sp800_218_final_html` | no | 2026-02-22 | mutable | 2026-05-31 | nist,ssdf,secure_development,supply_chain | NIST SP 800-218 Secure Software Development Framework (SSDF) final landing page. Pin sha256 once fetched via a stable channel. |
| `nist_sp800_218_r1_ipd_html` | no | 2026-02-22 | mutable | 2026-05-31 | nist,ssdf,draft | NIST SP 800-218 Revision 1 initial public draft (SSDF v1.2 draft). Draft is mutable; do not treat as binding until finalized; cite as informative. |
| `nist_sp800_61r3_pdf` | yes | 2026-02-22 |  |  | nist,incident_response,csf2_0_profile | NIST SP 800-61r3 (Apr 2025): Incident Response Recommendations and Considerations for Cyber Risk Management (CSF 2.0 community profile). |
| `nist_sp800_92r1_ipd_pdf` | yes | 2026-02-22 |  |  | nist,logging,time,draft | NIST SP 800-92 Revision 1 initial public draft: Guide to Computer Security Log Management (time sync assumptions are operationally critical). |
| `nist_voting_security_recommendations_page` | no | 2026-02-22 | mutable | 2026-05-31 | nist,election_security,operations | NIST voting security recommendations page; cited for EMS network isolation and related operational guidance. HTML is mutable; treat as informative until pinned. |
| `rfc2606_txt` | yes | 2026-02-26 |  |  | dns,examples,rfc | Reserved Top Level DNS Names (RFC 2606). Reference for non-identifying example domains used in publishable artifacts (docs/189). |
| `rfc3161_txt` | yes | 2026-02-22 |  |  | time,timestamping,rfc | Internet X.509 Public Key Infrastructure Time-Stamp Protocol (TSP) (RFC 3161). |
| `rfc3849_txt` | yes | 2026-02-26 |  |  | ip,ipv6,examples,rfc | IPv6 Address Prefix Reserved for Documentation (RFC 3849): 2001:db8::/32. Reference for non-identifying example IPv6 (docs/189). |
| `rfc4033_txt` | yes | 2026-02-22 |  |  | dns,dnssec,rfc | DNS Security Introduction and Requirements (RFC 4033). Baseline reference for enabling DNSSEC on official election domains. |
| `rfc5737_txt` | yes | 2026-02-26 |  |  | ip,examples,rfc | IPv4 Address Blocks Reserved for Documentation (RFC 5737). Reference for non-identifying example IPv4s (docs/189). |
| `rfc5905_txt` | yes | 2026-02-22 |  |  | time,ntp,rfc | Network Time Protocol Version 4: Protocol and Algorithms Specification (RFC 5905). |
| `rfc6376_txt` | yes | 2026-02-22 |  |  | dkim,email,auth | DomainKeys Identified Mail (DKIM) Signatures (RFC 6376). |
| `rfc7208_txt` | yes | 2026-02-22 |  |  | spf,email,auth | Sender Policy Framework (SPF) for Authorizing Use of Domains in Email (RFC 7208). |
| `rfc7489_txt` | yes | 2026-02-22 |  |  | dmarc,email,auth | Domain-based Message Authentication, Reporting, and Conformance (DMARC) (RFC 7489). |
| `rfc8460_txt` | yes | 2026-02-22 |  |  | email,tls,reporting | SMTP TLS Reporting (RFC 8460). |
| `rfc8461_txt` | yes | 2026-02-22 |  |  | email,tls,mta_sts | SMTP MTA Strict Transport Security (MTA-STS) (RFC 8461). |
| `rfc8615_txt` | yes | 2026-02-24 |  |  | well_known,http,rfc | ‘Well-Known Uniform Resource Identifiers (URIs)’ (RFC 8615). sha256 pinned. |
| `rfc8659_txt` | yes | 2026-02-22 |  |  | dns,caa,tls,rfc | DNS Certification Authority Authorization (CAA) Resource Record (RFC 8659). Useful to constrain certificate issuance for official election domains. |
| `rfc8785_txt` | yes | 2026-02-22 |  |  | jcs,canonicalization,json | JSON Canonicalization Scheme (JCS) (RFC 8785). |
| `rfc8915_txt` | yes | 2026-02-22 |  |  | time,nts,rfc | Network Time Security for the Network Time Protocol (NTS) (RFC 8915). |
| `rfc9110_txt` | yes | 2026-02-26 |  |  | http,semantics,rfc | HTTP Semantics (RFC 9110). Reference for Vary / content negotiation in split-view investigations (docs/224). |
| `rfc9111_txt` | yes | 2026-02-24 |  |  | http,caching,rfc | HTTP Caching (RFC 9111). Pinned reference for cache/freshness guidance in Track A public surfaces. |
| `rfc9116_txt` | no | 2026-02-27 | temporary | 2026-05-15 | security,http,rfc,comms | RFC 9116: security.txt. Standardized vulnerability disclosure contact surface; useful for making incident/reporting contact auditable without relying on screenshots. |
| `rfc9162_txt` | yes | 2026-02-21 |  |  | ct,transparency | Certificate Transparency v2 (RFC 9162). |
| `rfc9334_txt` | yes | 2026-02-21 |  |  | rats,attestation | RATS Architecture (RFC 9334). |
| `rfc9421_txt` | yes | 2026-02-22 |  |  | http,signatures,evidence | HTTP Message Signatures (RFC 9421). |
| `rfc9637_txt` | yes | 2026-02-26 |  |  | ip,ipv6,examples,rfc | Expanding the IPv6 Documentation Space (RFC 9637): adds 3fff::/20 for documentation examples. Used by publishable lint safe-placeholder heuristics (docs/189). |
| `rfc9711_txt` | yes | 2026-02-21 |  |  | eat,attestation | Entity Attestation Token (EAT) (RFC 9711). |
| `schneier_swiss_evoting_vulnerability_2023_post` | no | 2026-02-26 | mutable | 2026-05-31 | evoting,case_study,vulnerability,blog | Schneier on Security (Oct 2023): discussion of a Swiss e-voting vulnerability. Informative commentary pointer; do not treat as normative. |
| `slsa_provenance_v1_html` | no | 2026-02-21 | blocked | 2026-05-31 | slsa,provenance,supply_chain | SLSA Provenance v1 spec page; sha256 intentionally blank because automated fetch of HTML may be blocked in some environments. |
| `slsa_spec_v1_1_html` | no | 2026-02-21 | blocked | 2026-05-31 | slsa,supply_chain | SLSA specification v1.1 (Approved Apr 2025). sha256 intentionally blank because automated fetch of HTML may be blocked in some environments. |
| `stark_gentle_introduction_rla_2012_pdf` | yes | 2026-02-24 |  |  | audit,rla,paper | Lindeman & Stark (2012): A Gentle Introduction to Risk-Limiting Audits. PDF cited (not bundled); sha256 pinned. |
| `swiss_post_uv_flaw_disclosure_2019_page` | no | 2026-02-26 | mutable | 2026-05-31 | case_study,universal_verifiability,disclosure,evoting | Swiss Federal Chancellery (2019): Swiss Post universal-verifiability flaw disclosure. HTML is mutable; treat as informative; cite without bundling. |
| `swtch_tlog_design_notes_page` | no | 2026-02-26 | mutable | 2026-05-31 | ct,transparency,design_notes | Snyder (research.swtch.com) design notes on transparent logs (tlog). Mutable blog content; cite as informative. |
| `tuf_spec_latest_html` | no | 2026-02-22 | mutable | 2026-05-31 | tuf,secure_updates,supply_chain | The Update Framework (TUF) specification (latest). HTML is mutable; treat as informative; prefer versioned spec snapshots for normative claims. |
| `usenix_democracylive_security_2021_pdf` | no | 2026-02-26 | temporary | 2026-05-15 | remote_return,case_study,client_security,paper | Specter et al. (USENIX Security 2021): Democracy Live online voting system analysis. Used as a public case study of remote voting risk surfaces; cite without bundling. sha256 pending; treat as informative until pinned. |
| `usenix_electionguard_toolkit_2024_pdf` | no | 2026-02-26 | temporary | 2026-05-15 | e2e,electionguard,paper | Benaloh et al. (USENIX Security 2024): ElectionGuard toolkit paper. Background reference for E2E-on-paper deployment patterns; cite without bundling. sha256 pending; treat as informative until pinned. |
| `usenix_intoto_pipeline_integrity_pdf` | no | 2026-02-22 | temporary | 2026-05-15 | in_toto,supply_chain,pipeline_integrity,paper | Torres-Arias et al. (USENIX Security 2019): in-toto pipeline integrity paper (PDF). Pin sha256 once fetched via a stable channel. |
| `voteagain_revoting_usenix_2020_pdf` | yes | 2026-02-26 |  |  | coercion,revoting,remote_return,paper | Lueks et al. (USENIX Security 2020): VoteAgain (revoting paradigm). Reference for revoting assumptions and coercion-mitigation limits; sha256 pinned; PDF not bundled. |
