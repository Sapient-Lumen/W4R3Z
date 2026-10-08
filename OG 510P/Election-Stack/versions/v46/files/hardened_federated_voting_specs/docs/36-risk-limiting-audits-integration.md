# Risk-limiting audits (RLA) integration with E2E verification

**Track:** A (Deployable core)


This document extends `24-software-independence-paper-and-audits.md` with a concrete integration approach.

## Why RLAs are still the recovery anchor
Cryptographic evidence can detect many failures, but RLAs provide a **procedurally familiar** and **court-defensible** path to validate outcomes using voter-verifiable paper records.

## Two integration modes

### A) Parallel evidence (simplest)
- Paper ballots are the ballot of record.
- The E2E system publishes cryptographic evidence and an independently verifiable tally.
- RLAs operate purely on paper.

**Benefit:** minimal coupling.
**Risk:** if paper and crypto disagree, you need a pre-agreed adjudication rule.

### B) Ballot-level comparison audits (stronger, but tricky)
- For each paper ballot, the tabulation system produces a cast vote record (CVR).
- The E2E system provides a way to verify that the CVR corresponds to a committed/encrypted representation.

**Privacy warning:** ballot-level mapping can increase privacy risk; you must ensure the mapping does not enable identity inference.

## Spec requirements
- The system MUST publish an **Audit Plan** before the election:
  - the audit type,
  - sampling rules,
  - escalation triggers,
  - adjudication rules for discrepancies.
- The system MUST define which evidence is authoritative in a mismatch:
  - for most real elections, the paper trail should dominate.
- The system SHOULD publish machine-readable audit artifacts:
  - audit logs,
  - sample selection proofs,
  - discrepancy reports.

## Recommended reading
- NIST “A Gentle Introduction to Risk-Limiting Audits” (Lindeman & Stark)
- National Academies “Securing the Vote” (highlights)