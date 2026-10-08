# Case studies & lessons (for paranoia)

**Track:** A (Deployable core)


This document distills practical lessons from public analyses and real deployments. It is **not** an endorsement of any specific product.

## 1) Democracy Live / OmniBallot (web-based ballot delivery/marking/return)
Key lesson: *web-based ballot workflows inherit the full browser + supply-chain attack surface*; sophisticated attackers can target voters at scale.  
Suggested use constraint: if used at all, prefer modes where the **ballot of record is paper** returned via mail/in-person, and treat online components as *convenience* layers.

Artifacts:
- MIT analysis (2020): xref: mit_omniballot_analysis_2020_pdf
- USENIX paper (2021): xref: usenix_democracylive_security_2021_pdf

## 2) Estonia Internet voting (I-voting)
Key lesson: operational security, client security, and end-to-end transparency are perennial weak points; server trust and client compromise remain central concerns.  
Design implication: do not assume “national ID cards” magically solve remote voting—client malware and insider threats persist.

Artifact:
- Security Analysis (ACM CCS 2014): xref: estonia_ivote_security_analysis_2014_pdf

## 3) Swiss Post e-voting (universal verifiability flaw disclosure)
Key lesson: even systems designed for universal verifiability can harbor subtle proof/verification flaws; *verification code is security‑critical code.*  
Design implication: require multiple independent implementations of verifiers, formal test vectors, and public reproducibility.

Artifact:
- Official disclosure (2019): xref: swiss_post_uv_flaw_disclosure_2019_page

## 4) ElectionGuard (E2E toolkit integrated with traditional processes)
Key lesson: the strongest path tends to be **E2E on top of paper** — add cryptographic verifiability while keeping a paper ballot of record and audits.

Artifacts:
- Specs: xref: electionguard_spec_page
- USENIX Security 2024 paper: xref: usenix_electionguard_toolkit_2024_pdf

## 5) Transparency logs in the wild (Certificate Transparency)
Key lesson: append-only Merkle logs with inclusion/consistency proofs are a proven pattern for making tampering **detectable**, but operationalizing witness diversity and gossip is crucial.

Artifacts:
- RFC 9162: source: rfc9162_txt
- Design notes: xref: swtch_tlog_design_notes_page