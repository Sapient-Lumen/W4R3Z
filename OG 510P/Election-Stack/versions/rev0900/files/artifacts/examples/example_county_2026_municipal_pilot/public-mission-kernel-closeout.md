# Example County mission-kernel closeout

**Synthetic example only. This is not live election evidence.**

Scenario: `EXAMPLE-COUNTY-2026-MUNI-v900`  
Archive version: `v900`  
Verdict: `SYNTHETIC_REPLAY_PASS_LIVE_NO_GO`

This file names the seven mission-kernel elements, the synthetic evidence currently wired to each one, and the live blockers that must close before any pilot, public-release, production-authority, or voter-instruction claim.

## Kernel status

- `K01_AUTHORIZED_ELECTION_DEFINITION` — `SYNTHETIC_REPLAY_PASS`; owner role: jurisdiction authority liaison; evidence refs: 3; live blockers: 3.
- `K02_BALLOT_ACCOUNTING_AND_CUSTODY` — `SYNTHETIC_PARTIAL`; owner role: custody and ballot accounting lead; evidence refs: 8; live blockers: 5.
- `K03_STANDARDIZED_RESULTS_EXPORTS` — `SYNTHETIC_REPLAY_PASS`; owner role: results export and verifier lead; evidence refs: 11; live blockers: 4.
- `K04_AUDIT_RECOUNT_ADJUDICATION` — `LIVE_BLOCKED_MISSING_EVIDENCE`; owner role: audit adjudication and dispute lead; evidence refs: 3; live blockers: 4.
- `K05_AUTHENTICATED_OFFICIAL_NOTICES` — `SYNTHETIC_REPLAY_PASS`; owner role: public notice and accessibility lead; evidence refs: 8; live blockers: 3.
- `K06_INDEPENDENT_VERIFIER_DISAGREEMENT_FAILURE` — `SYNTHETIC_REPLAY_PASS`; owner role: independent verification coordinator; evidence refs: 7; live blockers: 3.
- `K07_INCIDENT_DISPUTE_REMEDY_CLOSEOUT` — `SYNTHETIC_PARTIAL`; owner role: incident remedy and records lead; evidence refs: 5; live blockers: 3.

## Highest-risk next work

- `MKB-001` (critical): local authority adoption packet — local election official approves scope, election id, channels, and source precedence by digest
- `MKB-002` (critical): ballot accounting and custody evidence packet — every reporting unit has ballot counts, custody anchors, exceptions, and disposition records
- `MKB-003` (critical): standards-based export replay and event-chain packet — independent verifier recomputes closeout outputs from jurisdiction export bytes and digest-bound event rows
- `MKB-004` (critical): audit adjudication remedy packet — at least one observed drill closes from issue through remedy and reviewer signoff
- `MKB-005` (critical): independent review transcript packet — two independent reviewers reproduce packet verdicts and publish bounded summaries
- `MKB-006` (high): public release approval packet — local approval records exist before any voter-facing publication claim
- `MKB-007` (high): incident remedy closeout packet — dispute or incident record carries trigger, owner, remedy, dissent, and disposition

## Boundary

This closeout does not prove that an election outcome is correct. It does not replace canvass, audit, certification, recount, statutory retention, public-records, or court process. It is live no-go until local authority, custody, export, audit/adjudication, independent-review, public-release, and remedy/retention evidence exists.
