# 245 — External standards and alignment map (anchors, not requirements)

**Track:** Shared

This document is a **compact index of external election standards and guidance** that this archive frequently intersects with.
It exists for two reasons:

1. **Navigation:** help readers quickly locate the “real-world” anchors election officials, labs, and vendors already use.
2. **Discipline:** make it explicit what we **do** and **do not** claim to align with, so the stack does not drift into unreviewed “compliance theater.”

## 245.1 Normativity rule

- **External documents are not normative for this archive** unless a specific numbered spec explicitly says so.
- When we borrow a concept, we prefer to restate it as a **project-local requirement** and cite the external source as an *anchor*, not as a substitute for reasoning.

## 245.2 Voting system standards (US)

### EAC VVSG 2.0

- The U.S. Election Assistance Commission (EAC) **adopted VVSG 2.0** on **February 10, 2021**. (EAC adoption announcement (xref: eac_commission_adopts_new_voluntary_voting_system_guidelines_20)).  
- VVSG 2.0 is published as a requirements document (PDF). (VVSG 2.0 Requirements PDF (xref: eac_testingcertification_voluntary_voting_system_guidelines_version_2_0)).
- EAC certification to VVSG 2.0 is now operational; EAC has announced at least one **VVSG 2.0–certified system** (example: Hart InterCivic Verity Vanguard 1.0, announced July 10, 2025). (EAC July 10, 2025 certification announcement (xref: eac_certified_voting_system_voluntary_voting_system_guidelines_vvsg)).

**Stack relevance (high-level):**
- Track A evidence patterns are intended to be **compatible with** VVSG-era operations (paper audit trails, accessibility, security process), but this archive **does not claim VVSG conformance** without a jurisdiction-specific engineering + test campaign.
- When we discuss “voting system” properties, default to **VVSG language** unless a numbered spec defines a different term.

## 245.3 Cyber risk management for election infrastructure

### NIST Cybersecurity Framework Election Infrastructure Profile (2024)

NIST publishes a CSF “profile” tailored to election infrastructure as a voluntary, risk-based approach for managing cyber risk. (NIST VTS 200-1 PDF (xref: nist_nistpubs_vts_nist_vts_200_1)).

**Stack relevance (high-level):**
- Use the Profile as an **overlay** when building Track A operational checklists (e.g., incident response, supplier controls, resilience).
- Treat the Profile as a **coverage check** for omissions, not as a “checkbox compliance” destination.

## 245.4 Common Data Formats (CDFs) and interoperability

### NIST implementation guidance for election Common Data Formats (2024)

NIST provides implementation guidance spanning multiple election CDFs (Ballot Definition, Cast Vote Records, Voter Records Interchange, Election Results Reporting). (NIST GCR 24-058 (xref: nist_gcr_2024_24_058_nist_gcr_24_058)).

**Stack relevance (high-level):**
- Where this archive defines evidence objects for ballot definitions, CVRs, or results reporting, prefer:
  - **Explicit transforms** between local schemas and the relevant CDF; and
  - **Hash-linked evidence** of each transform step (so disputes can reason about exact bytes, not “what the system meant”).
- Avoid hand-waving “we output CDF” claims: always specify the **version**, **profile**, and any **extensions**.

## 245.5 Audits and outcome verification

### Risk-limiting audits (RLA)

- NIST’s introduction explains RLAs as statistical checks of outcomes via partial manual examination of the audit trail. (NIST “A Gentle Introduction to Risk-Limiting Audits” (xref: nist_gentle_intro_rla_pdf)).  
- A practical field guide exists (Jennifer Morrell, 2019). (Jennifer Morrell, “Knowing It’s Right” (2019) (xref: democracy_fund_content_uploads_2020_06_2019_df_knowingitsright_part1)).

**Stack relevance (high-level):**
- Track A is designed so the public record can support (at minimum) **credible escalation paths** into audits and recounts by ensuring:
  - published artifacts are **complete, time-stamped, and hash-addressable**; and
  - disputes can be scoped to **specific precinct/batch/ballot-style objects**, not vibes.

## 245.6 Remote ballot delivery / return risk guidance

- CISA maintains “Best Practices for Securing Election Systems.” (CISA Best Practices for Securing Election Systems (xref: cisa_best_practices_securing_election_systems_page)).
- CISA/EAC/FBI/NSA publish risk management guidance for electronic ballot delivery/marking/return (2020). (CISA et al., Risk Management for Electronic Ballot Delivery, Marking, and Return (2020) (xref: cisa_electronic_ballot_risk_mgmt_2020_pdf)).

**Stack relevance (high-level):**
- This archive’s Track B/C remote-return work should stay **tethered** to published risk language:
  - articulate *which risks remain* even after mitigation;
  - define what “acceptable residual risk” would mean; and
  - maintain an auditable record of why a jurisdiction did or did not adopt a given mechanism.

## 245.7 What this doc does not do

- It does **not** attempt an exhaustive bibliography.
- It does **not** certify safety, legality, or compliance.
- It does **not** substitute for local law, accreditation rules, or testing lab requirements.

## 245.8 Open questions (for future bounded expansion)

- How to publish **machine-checkable conformance claims** (“this evidence packet covers these VVSG-adjacent requirements”) without turning the archive into a compliance framework.
- How to define **jurisdictional profiles** (state/country variants) while keeping Track A artifacts interoperable.
