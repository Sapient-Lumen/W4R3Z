# References (tight, lockfile-first)

**Track:** Shared


This archive prioritizes **primary sources**: election authority guidance, standards/RFCs, and peer‑reviewed papers.

**Lockfile-first:** normative citations inside this archive should use `source:` / `xref:` IDs from `evidence/lock/external-sources.toml` (policy: `docs/151`).

Reading views (no URLs):
- Flat index: `docs/214-external-sources-index.md` (generated)
- Grouped by primary tag: `docs/230-external-sources-by-primary-tag.md` (generated)

This file stays small on purpose; if a new reference matters, add it to the lockfile with a short note + tags and cite by ID.

## Public guidance: election security, ballot return risk, certification
- EAC — End‑to‑End (E2E) Protocol Evaluation Process: `xref: eac_e2e_protocol_evaluation_process_page`
- EAC — VVSG 2.0 Test Assertions v1.4 (Jan 30, 2026): `source: eac_vvsg2_test_assertions_v1_4_pdf`
- CISA/EAC/FBI/NIST — Risk Management for Electronic Ballot Delivery/Return (May 8, 2020): `xref: cisa_electronic_ballot_risk_mgmt_2020_pdf`
- NIST — Voting security recommendations: `xref: nist_voting_security_recommendations_page`
- EAC — Checklist for Securing ENR: `xref: eac_enr_securing_results_checklist_pdf`
- NIST — ENR security discussion/use case: `xref: nist_enr_security_enr_use_case_page`
- IFES — Results management cybersecurity briefing: `xref: ifes_results_management_cybersecurity_briefing_pdf`
- National Academies — Securing the Vote (highlights, 2018): `source: nasem_securing_the_vote_highlights_pdf`

## Remote return case studies (cautionary)
- OmniBallot analysis (MIT, 2020): `xref: mit_omniballot_analysis_2020_pdf`
- Democracy Live analysis (USENIX Security 2021): `xref: usenix_democracylive_security_2021_pdf`
- Estonia I‑voting analysis (ACM CCS 2014): `xref: estonia_ivote_security_analysis_2014_pdf`
- Swiss Post UV flaw disclosure (2019): `xref: swiss_post_uv_flaw_disclosure_2019_page`

## E2E verifiability (on-paper preferred)
- ElectionGuard specs landing page: `xref: electionguard_spec_page`
- ElectionGuard toolkit paper (USENIX Security 2024): `xref: usenix_electionguard_toolkit_2024_pdf`

## Transparency log patterns
- Certificate Transparency v2 (RFC 9162): `source: rfc9162_txt`
- Transparent logs design notes (informative): `xref: swtch_tlog_design_notes_page`
- SCITT architecture draft (informative): `source: draft_scitt_architecture_22_txt`

## Supply-chain integrity (operator relevance)
- in-toto Attestation Statement v1 (raw spec): `source: intoto_statement_v1_md`
- DSSE envelope layer spec (raw; informative): `xref: intoto_envelope_v1_md`
- NIST SP 800-204D (CI/CD supply-chain): `source: nist_sp800_204d_pdf`
- SSDF (NIST SP 800-218 landing page): `xref: nist_sp800_218_final_html`
- C-SCRM (NIST SP 800-161r1 landing page): `xref: nist_sp800_161r1_final_html`
- SLSA v1.1 (landing page): `xref: slsa_spec_v1_1_html`
- TUF specification (latest): `xref: tuf_spec_latest_html`

