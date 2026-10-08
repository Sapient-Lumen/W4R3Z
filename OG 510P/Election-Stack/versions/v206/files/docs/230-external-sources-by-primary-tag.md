# 230. External sources by primary tag (lockfile IDs, no URLs)

**Track:** Shared


Generated from `evidence/lock/external-sources.toml`. Primary tag = the first element of each entry's `tags[]` list.

Purpose: a reading/triage view that avoids duplicate listings (each source appears once). For the flat table, see `docs/214`.

## audit (total=3; pinned=1; unpinned=2)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `arxiv_more_style_less_work_2012_03371_pdf` | no | 2026-02-22 | temporary | 2026-05-15 | Glazer, Spertus, Stark (2020): 'More style, less work' (card-style data for RLAs). PDF cited (not bundled); pin sha256 once fetched. |
| `arxiv_stylish_rla_in_practice_2309_09081_pdf` | no | 2026-02-22 | temporary | 2026-05-15 | Glazer, Spertus, Stark (2023): Stylish Risk-Limiting Audits in Practice. PDF cited (not bundled); pin sha256 once fetched. |
| `stark_gentle_introduction_rla_2012_pdf` | yes | 2026-02-24 |  |  | Lindeman & Stark (2012): A Gentle Introduction to Risk-Limiting Audits. PDF cited (not bundled); sha256 pinned. |

## c2pa (total=1; pinned=0; unpinned=1)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `c2pa_content_credentials_spec_2_2_pdf` | no | 2026-02-22 | temporary | 2026-05-15 | C2PA Content Credentials technical specification (v2.2 PDF). Used as an informative reference for optional provenance of official media artifacts; do not bundle bytes. sha256 pending; treat as informative until pinned. |

## case_study (total=1; pinned=0; unpinned=1)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `swiss_post_uv_flaw_disclosure_2019_page` | no | 2026-02-26 | mutable | 2026-05-31 | Swiss Federal Chancellery (2019): Swiss Post universal-verifiability flaw disclosure. HTML is mutable; treat as informative; cite without bundling. |

## cdf (total=6; pinned=6; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `nist_gcr_24_058_cdf_implementation_guidance_pdf` | yes | 2026-02-26 |  |  | NIST GCR 24-058 (2024): Implementation Guidance for Common Data Formats. Practical cross-CDF mapping, identifiers, and processing guidance. |
| `nist_sp1500_100r2_err_pdf` | yes | 2026-02-26 |  |  | NIST SP 1500-100r2: Election Results Reporting (ERR) Common Data Format specification (rev 2.0). Reference for structured results reporting + disclosure policy. |
| `nist_sp1500_101_eel_pdf` | yes | 2026-02-26 |  |  | NIST SP 1500-101 (Apr 2020): Election Event Logging (EEL) Common Data Format specification. Reference for publishable log commitments + incident forensics. |
| `nist_sp1500_102_vri_pdf` | yes | 2026-02-26 |  |  | NIST SP 1500-102 (Nov 2019): Voter Records Interchange (VRI) Common Data Format specification. Reference for registration/eligibility interchange. |
| `nist_sp1500_103_cvr_pdf` | yes | 2026-02-26 |  |  | NIST SP 1500-103 (Nov 2019): Cast Vote Records (CVR) Common Data Format specification. Load-bearing for reproducible tabulation + audit bridging. |
| `nist_sp1500_20_bd_pdf` | yes | 2026-02-26 |  |  | NIST SP 1500-20 (Jan 2023): Ballot Definition (BD) Common Data Format specification. Core reference for BD hashing + interoperability in Track A. |

## cisa (total=8; pinned=0; unpinned=8)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `cisa_best_practices_securing_election_systems_page` | no | 2026-02-22 | mutable | 2026-05-31 | CISA best practices for securing election systems (includes guidance relevant to public-facing sites and comms operations). HTML is mutable; treat as informative until pinned. |
| `cisa_bod_18_01_page` | no | 2026-02-22 | mutable | 2026-05-31 | CISA BOD 18-01 (Enhance Email and Web Security). Useful baseline controls for official comms channels (HTTPS, email authentication). HTML is mutable; treat as informative until pinned. |
| `cisa_election_ir_comms_guide_page` | no | 2026-02-21 | mutable | 2026-05-31 | Landing page for the joint EAC/CISA incident response communications guide; automated retrieval may be blocked. Pin sha256 once fetched via a permitted channel. |
| `cisa_electronic_ballot_risk_mgmt_2020_pdf` | no | 2026-02-21 | blocked | 2026-05-31 | Authoritative joint CISA/EAC/FBI/NIST risk assessment; automated retrieval may be blocked (403). Pin sha256 once fetched via a permitted channel. |
| `cisa_rumorcontrol_page` | no | 2026-02-22 | mutable | 2026-05-31 | CISA Election Security Rumor vs. Reality landing page ('rumorcontrol'). Mutable HTML; treat as informative until pinned. |
| `cisa_tactics_of_disinformation_508_pdf` | no | 2026-02-22 | blocked | 2026-05-31 | CISA: 'Tactics of Disinformation' (PDF). Automated retrieval may be blocked (403); cite without bundling bytes. |
| `cisa_time_guidance_network_operators_2023_pdf` | no | 2026-02-22 | blocked | 2026-05-31 | CISA time guidance for network operators (PDF). Access may be restricted (403) in some environments; record as best-effort citation without bundling bytes. |
| `cisa_voluntary_incident_reporting_guidance_2024_pdf` | no | 2026-02-22 | temporary | 2026-05-15 | CISA: Voluntary Incident Reporting Guidance for Election Infrastructure stakeholders (June 2024). PDF is cited (not bundled); pin sha256 once fetched via a permitted channel. |

## coercion (total=1; pinned=1; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `voteagain_revoting_usenix_2020_pdf` | yes | 2026-02-26 |  |  | Lueks et al. (USENIX Security 2020): VoteAgain (revoting paradigm). Reference for revoting assumptions and coercion-mitigation limits; sha256 pinned; PDF not bundled. |

## ct (total=3; pinned=2; unpinned=1)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `ndss_2024_public_inspections_monitors_pdf` | yes | 2026-02-24 |  |  | NDSS 2024 paper: 'Certificate Transparency Revisited: The Public Inspections on Third-party Monitors' (Sun et al.). Used as a CT monitor/watchers reference for monitor reliability gaps. |
| `rfc9162_txt` | yes | 2026-02-21 |  |  | Certificate Transparency v2 (RFC 9162). |
| `swtch_tlog_design_notes_page` | no | 2026-02-26 | mutable | 2026-05-31 | Snyder (research.swtch.com) design notes on transparent logs (tlog). Mutable blog content; cite as informative. |

## dkim (total=1; pinned=1; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `rfc6376_txt` | yes | 2026-02-22 |  |  | DomainKeys Identified Mail (DKIM) Signatures (RFC 6376). |

## dmarc (total=1; pinned=1; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `rfc7489_txt` | yes | 2026-02-22 |  |  | Domain-based Message Authentication, Reporting, and Conformance (DMARC) (RFC 7489). |

## dns (total=3; pinned=3; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `rfc2606_txt` | yes | 2026-02-26 |  |  | Reserved Top Level DNS Names (RFC 2606). Reference for non-identifying example domains used in publishable artifacts (docs/189). |
| `rfc4033_txt` | yes | 2026-02-22 |  |  | DNS Security Introduction and Requirements (RFC 4033). Baseline reference for enabling DNSSEC on official election domains. |
| `rfc8659_txt` | yes | 2026-02-22 |  |  | DNS Certification Authority Authorization (CAA) Resource Record (RFC 8659). Useful to constrain certificate issuance for official election domains. |

## e2e (total=3; pinned=1; unpinned=2)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `eac_e2e_protocols_draft_tgdc_2023_pdf` | yes | 2026-02-21 |  |  | EAC/NIST E2E verifiable protocol draft for TGDC (Jan 2023). |
| `electionguard_spec_page` | no | 2026-02-26 | mutable | 2026-05-31 | ElectionGuard specifications landing page. Mutable HTML; treat as informative unless a pinned snapshot/spec artifact is added. |
| `usenix_electionguard_toolkit_2024_pdf` | no | 2026-02-26 | temporary | 2026-05-15 | Benaloh et al. (USENIX Security 2024): ElectionGuard toolkit paper. Background reference for E2E-on-paper deployment patterns; cite without bundling. sha256 pending; treat as informative until pinned. |

## eac (total=6; pinned=3; unpinned=3)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `eac_ai_toolkit_2023_pdf` | yes | 2026-02-22 |  |  | EAC: AI Toolkit for Election Officials (Aug 2023). Hash pinned; PDF not bundled. |
| `eac_communicating_election_post_election_toolkit_2026_page` | no | 2026-02-22 | mutable | 2026-05-31 | EAC web toolkit (Feb 2026): Communicating election and post-election processes. SHA blank (HTML; pin when fetched via permitted channel). |
| `eac_e2e_protocol_evaluation_process_page` | no | 2026-02-22 | mutable | 2026-05-31 | EAC page describing the public E2E protocol evaluation/approval process intended to support VVSG 2.0 certification. HTML is mutable; treat as informative until pinned. |
| `eac_enhancing_election_security_public_comms_2024_pdf` | yes | 2026-02-22 |  |  | EAC/CISA guidance: Enhancing Election Security Through Public Communications (PDF). Hash pinned; PDF not bundled. |
| `eac_enr_securing_results_checklist_pdf` | no | 2026-02-26 | temporary | 2026-05-15 | EAC checklist for securing election-night results reporting (ENR). PDF is not yet sha256-pinned; treat as informative until pinned. |
| `eac_incident_response_comms_guide_pdf` | yes | 2026-02-21 |  |  | Pinned hash only (PDF not bundled). Used for incident communications process references (docs/186). |

## eat (total=1; pinned=1; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `rfc9711_txt` | yes | 2026-02-21 |  |  | Entity Attestation Token (EAT) (RFC 9711). |

## email (total=2; pinned=2; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `rfc8460_txt` | yes | 2026-02-22 |  |  | SMTP TLS Reporting (RFC 8460). |
| `rfc8461_txt` | yes | 2026-02-22 |  |  | SMTP MTA Strict Transport Security (MTA-STS) (RFC 8461). |

## evoting (total=1; pinned=0; unpinned=1)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `schneier_swiss_evoting_vulnerability_2023_post` | no | 2026-02-26 | mutable | 2026-05-31 | Schneier on Security (Oct 2023): discussion of a Swiss e-voting vulnerability. Informative commentary pointer; do not treat as normative. |

## http (total=3; pinned=3; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `rfc9110_txt` | yes | 2026-02-26 |  |  | HTTP Semantics (RFC 9110). Reference for Vary / content negotiation in split-view investigations (docs/224). |
| `rfc9111_txt` | yes | 2026-02-24 |  |  | HTTP Caching (RFC 9111). Pinned reference for cache/freshness guidance in Track A public surfaces. |
| `rfc9421_txt` | yes | 2026-02-22 |  |  | HTTP Message Signatures (RFC 9421). |

## ietf (total=1; pinned=0; unpinned=1)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `draft_scitt_refusal_events_02_html` | no | 2026-02-22 | mutable | 2026-05-31 | IETF individual draft (Kamimura et al., 2026): Verifiable AI Refusal Events using SCITT Transparency Logs. Drafts change; treat as informative until pinned. |

## ifes (total=1; pinned=0; unpinned=1)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `ifes_results_management_cybersecurity_briefing_pdf` | no | 2026-02-26 | temporary | 2026-05-15 | IFES briefing paper on cybersecurity of election results management systems. PDF is not yet sha256-pinned; treat as informative until pinned. |

## in_toto (total=4; pinned=2; unpinned=2)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `intoto_slsa_provenance_predicate_md` | yes | 2026-02-21 |  |  | in-toto predicate: SLSA Provenance (Type URI and migration notes). |
| `intoto_specs_html` | no | 2026-02-21 | blocked | 2026-05-31 | in-toto specs index page; sha256 intentionally blank because automated fetch of HTML may be blocked in some environments. |
| `intoto_statement_v1_md` | yes | 2026-02-21 |  |  | in-toto Attestation: Statement v1 (raw markdown). |
| `usenix_intoto_pipeline_integrity_pdf` | no | 2026-02-22 | temporary | 2026-05-15 | Torres-Arias et al. (USENIX Security 2019): in-toto pipeline integrity paper (PDF). Pin sha256 once fetched via a stable channel. |

## ip (total=3; pinned=3; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `rfc3849_txt` | yes | 2026-02-26 |  |  | IPv6 Address Prefix Reserved for Documentation (RFC 3849): 2001:db8::/32. Reference for non-identifying example IPv6 (docs/189). |
| `rfc5737_txt` | yes | 2026-02-26 |  |  | IPv4 Address Blocks Reserved for Documentation (RFC 5737). Reference for non-identifying example IPv4s (docs/189). |
| `rfc9637_txt` | yes | 2026-02-26 |  |  | Expanding the IPv6 Documentation Space (RFC 9637): adds 3fff::/20 for documentation examples. Used by publishable lint safe-placeholder heuristics (docs/189). |

## jcs (total=1; pinned=1; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `rfc8785_txt` | yes | 2026-02-22 |  |  | JSON Canonicalization Scheme (JCS) (RFC 8785). |

## nasem (total=1; pinned=1; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `nasem_securing_the_vote_highlights_pdf` | yes | 2026-02-21 |  |  | National Academies highlights for 'Securing the Vote' (2018). |

## nist (total=12; pinned=6; unpinned=6)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `nist_ai_rmf_100_1_pdf` | yes | 2026-02-22 |  |  | NIST AI 100-1: Artificial Intelligence Risk Management Framework (AI RMF) 1.0 (PDF). |
| `nist_csf2_0_pdf` | yes | 2026-02-22 |  |  | NIST Cybersecurity Framework (CSF) 2.0 (CSWP 29, Feb 26 2024). |
| `nist_enr_security_enr_use_case_page` | no | 2026-02-26 | mutable | 2026-05-31 | NIST election night reporting (ENR) security discussion/use case. HTML is mutable; treat as informative until pinned. |
| `nist_irb_overview_html` | no | 2026-02-21 | blocked | 2026-05-31 | NIST Interoperable Randomness Beacons overview page; sha256 intentionally blank because automated fetch of HTML may be blocked in some environments. |
| `nist_sp800_122_pdf` | yes | 2026-02-26 |  |  | NIST SP 800-122: Guide to Protecting the Confidentiality of PII. Reference for PII minimization and handling in publishable artifacts (docs/189). |
| `nist_sp800_161r1_final_html` | no | 2026-02-22 | mutable | 2026-05-31 | NIST SP 800-161r1 Cybersecurity Supply Chain Risk Management Practices (C-SCRM) final landing page. Pin sha256 once fetched via a stable channel. |
| `nist_sp800_204d_pdf` | yes | 2026-02-21 |  |  | NIST SP 800-204D (2024): strategies for integrating software supply-chain security into CI/CD pipelines. |
| `nist_sp800_218_final_html` | no | 2026-02-22 | mutable | 2026-05-31 | NIST SP 800-218 Secure Software Development Framework (SSDF) final landing page. Pin sha256 once fetched via a stable channel. |
| `nist_sp800_218_r1_ipd_html` | no | 2026-02-22 | mutable | 2026-05-31 | NIST SP 800-218 Revision 1 initial public draft (SSDF v1.2 draft). Draft is mutable; do not treat as binding until finalized; cite as informative. |
| `nist_sp800_61r3_pdf` | yes | 2026-02-22 |  |  | NIST SP 800-61r3 (Apr 2025): Incident Response Recommendations and Considerations for Cyber Risk Management (CSF 2.0 community profile). |
| `nist_sp800_92r1_ipd_pdf` | yes | 2026-02-22 |  |  | NIST SP 800-92 Revision 1 initial public draft: Guide to Computer Security Log Management (time sync assumptions are operationally critical). |
| `nist_voting_security_recommendations_page` | no | 2026-02-22 | mutable | 2026-05-31 | NIST voting security recommendations page; cited for EMS network isolation and related operational guidance. HTML is mutable; treat as informative until pinned. |

## randomness (total=1; pinned=0; unpinned=1)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `drand_docs_overview_html` | no | 2026-02-21 | blocked | 2026-05-31 | drand distributed randomness beacon docs; sha256 intentionally blank because automated fetch of HTML may be blocked in some environments. |

## rats (total=1; pinned=1; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `rfc9334_txt` | yes | 2026-02-21 |  |  | RATS Architecture (RFC 9334). |

## remote_return (total=3; pinned=0; unpinned=3)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `estonia_ivote_security_analysis_2014_pdf` | no | 2026-02-26 | temporary | 2026-05-15 | Springall et al. (ACM CCS 2014): Estonia I-voting security analysis. Used as a cautionary case study on operational/client trust and verification complexity; cite without bundling. sha256 pending; treat as informative until pinned. |
| `mit_omniballot_analysis_2020_pdf` | no | 2026-02-26 | temporary | 2026-05-15 | Specter & Halderman (MIT, 2020): OmniBallot security analysis. Cited for browser/client attack surface risks in remote ballot workflows; do not bundle bytes. sha256 pending; treat as informative until pinned. |
| `usenix_democracylive_security_2021_pdf` | no | 2026-02-26 | temporary | 2026-05-15 | Specter et al. (USENIX Security 2021): Democracy Live online voting system analysis. Used as a public case study of remote voting risk surfaces; cite without bundling. sha256 pending; treat as informative until pinned. |

## scitt (total=3; pinned=3; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `draft_scitt_architecture_22_txt` | yes | 2026-02-21 |  |  | SCITT architecture draft (version -22, Oct 10 2025). |
| `draft_scitt_receipts_ccf_profile_00_txt` | yes | 2026-02-21 |  |  | SCITT receipts CCF profile Internet-Draft (version -00). |
| `draft_scitt_scrapi_07_txt` | yes | 2026-02-21 |  |  | SCITT Reference APIs (SCRAPI) Internet-Draft (version -07, Feb 2026). |

## slsa (total=2; pinned=0; unpinned=2)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `slsa_provenance_v1_html` | no | 2026-02-21 | blocked | 2026-05-31 | SLSA Provenance v1 spec page; sha256 intentionally blank because automated fetch of HTML may be blocked in some environments. |
| `slsa_spec_v1_1_html` | no | 2026-02-21 | blocked | 2026-05-31 | SLSA specification v1.1 (Approved Apr 2025). sha256 intentionally blank because automated fetch of HTML may be blocked in some environments. |

## spf (total=1; pinned=1; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `rfc7208_txt` | yes | 2026-02-22 |  |  | Sender Policy Framework (SPF) for Authorizing Use of Domains in Email (RFC 7208). |

## time (total=4; pinned=4; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `draft_ietf_ntp_roughtime_17_txt` | yes | 2026-02-22 |  |  | Roughtime (IETF NTP WG) draft-ietf-ntp-roughtime-17 (Feb 21 2026). |
| `rfc3161_txt` | yes | 2026-02-22 |  |  | Internet X.509 Public Key Infrastructure Time-Stamp Protocol (TSP) (RFC 3161). |
| `rfc5905_txt` | yes | 2026-02-22 |  |  | Network Time Protocol Version 4: Protocol and Algorithms Specification (RFC 5905). |
| `rfc8915_txt` | yes | 2026-02-22 |  |  | Network Time Security for the Network Time Protocol (NTS) (RFC 8915). |

## tuf (total=1; pinned=0; unpinned=1)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `tuf_spec_latest_html` | no | 2026-02-22 | mutable | 2026-05-31 | The Update Framework (TUF) specification (latest). HTML is mutable; treat as informative; prefer versioned spec snapshots for normative claims. |

## vvsg (total=1; pinned=1; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `eac_vvsg2_test_assertions_v1_4_pdf` | yes | 2026-02-21 |  |  | VVSG 2.0 Test Assertions v1.4 (published Jan 30, 2026). |

## well_known (total=1; pinned=1; unpinned=0)

| id | pinned | retrieved | exemption | review_by | note |
|---|---|---|---|---|---|
| `rfc8615_txt` | yes | 2026-02-24 |  |  | ‘Well-Known Uniform Resource Identifiers (URIs)’ (RFC 8615). sha256 pinned. |
