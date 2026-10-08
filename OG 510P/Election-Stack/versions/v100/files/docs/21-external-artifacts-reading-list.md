# External artifacts: curated reading list (with why it matters)

**Track:** A (Deployable core)


This is the “minimum credible bibliography” for design reviews. Links are in `references.md`.

## Transparency / append-only logs
- RFC 9162 (Certificate Transparency v2): baseline model for Merkle logs, inclusion/consistency proofs, and equivocation evidence.
- CT-style “transparency log” design notes (tlog): pragmatic patterns for skeptical clients.

## E2E verifiability in practice
- ElectionGuard official specs: concrete, implementable E2E toolkit designed to layer onto traditional elections.
- USENIX Security 2024 (Benaloh et al.): peer-reviewed overview of ElectionGuard and verifier goals.
- “Verifying ElectionGuard” (Jensen et al., 2024): focuses on *auditor usability* and real verification friction.

## Remote voting risk reality checks
- CISA/EAC/FBI/NSA Risk Management for Electronic Ballot Delivery/Marking/Return (2020): joint federal guidance emphasizing risk and mitigations. (`source: cisa_electronic_ballot_risk_mgmt_2020_pdf`).
- OmniBallot / Democracy Live analyses: concrete examples of how client + workflow + server risks surface in the real world.
- Estonian i-voting analysis (CCS 2014): operational + technical lessons, including software supply-chain and procedural concerns.
- Swiss Post 2019 disclosure: universal-verifiability is fragile; implementation details matter.

## Coercion resistance research
- VoteAgain (USENIX Security 2020): coercion-resistant revoting paradigm; very explicit about assumptions.

## Paper audits (recovery anchor)
- National Academies “Securing the Vote”: paper ballots + RLAs as bedrock.
- RLAs (Stark & community): how to make outcomes evidence-based.

## Supply chain / secure development
- NIST SSDF (SP 800-218) and NIST C-SCRM (SP 800-161r1): governance + engineering controls.
- TUF + in-toto + SLSA: practical secure-update and provenance patterns.


## Submission privacy / metadata reduction
- RFC 9458 (OHTTP) and RFC 9230 (ODoH): privacy partitioning to reduce IP→ballot linkage at the PBB front-end.
- RFC 9577 (Privacy Pass): anonymous anti-abuse tokens; useful for rate-limiting without IP-based discrimination.
