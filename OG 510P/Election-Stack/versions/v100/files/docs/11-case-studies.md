# Case studies & lessons (for paranoia)

**Track:** A (Deployable core)


This document distills practical lessons from public analyses and real deployments. It is **not** an endorsement of any specific product.

## 1) Democracy Live / OmniBallot (web-based ballot delivery/marking/return)
Key lesson: *web-based ballot workflows inherit the full browser + supply-chain attack surface*; sophisticated attackers can target voters at scale.  
Suggested use constraint: if used at all, prefer modes where the **ballot of record is paper** returned via mail/in-person, and treat online components as *convenience* layers.

Artifacts:
- MIT analysis (2020): https://internetpolicy.mit.edu/wp-content/uploads/2020/06/OmniBallot.pdf
- USENIX paper (2021): https://www.usenix.org/system/files/sec21-specter-security.pdf

## 2) Estonia Internet voting (I-voting)
Key lesson: operational security, client security, and end-to-end transparency are perennial weak points; server trust and client compromise remain central concerns.  
Design implication: do not assume “national ID cards” magically solve remote voting—client malware and insider threats persist.

Artifact:
- Security Analysis (ACM CCS 2014): https://jhalderm.com/pub/papers/ivoting-ccs14.pdf

## 3) Swiss Post e-voting (universal verifiability flaw disclosure)
Key lesson: even systems designed for universal verifiability can harbor subtle proof/verification flaws; *verification code is security‑critical code.*  
Design implication: require multiple independent implementations of verifiers, formal test vectors, and public reproducibility.

Artifact:
- Official disclosure (2019): https://www.news.admin.ch/en/nsb?id=74307

## 4) ElectionGuard (E2E toolkit integrated with traditional processes)
Key lesson: the strongest path tends to be **E2E on top of paper** — add cryptographic verifiability while keeping a paper ballot of record and audits.

Artifacts:
- Specs: https://electionguard.vote/spec/
- USENIX Security 2024 paper: https://www.usenix.org/system/files/usenixsecurity24-benaloh.pdf

## 5) Transparency logs in the wild (Certificate Transparency)
Key lesson: append-only Merkle logs with inclusion/consistency proofs are a proven pattern for making tampering **detectable**, but operationalizing witness diversity and gossip is crucial.

Artifacts:
- RFC 9162: https://www.rfc-editor.org/rfc/rfc9162.html
- Design notes: https://research.swtch.com/tlog