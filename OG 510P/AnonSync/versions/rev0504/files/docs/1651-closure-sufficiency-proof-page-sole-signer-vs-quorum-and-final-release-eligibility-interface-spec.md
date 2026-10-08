# Closure sufficiency proof page — sole signer vs quorum and final-release eligibility

## Purpose

This page is the durable proof object for the strongest true closure sentence after coalition review.
It exists so the archive can preserve whether finality was earned by one signer, countersign path, quorum, unanimity, or adjudication, and reopen that statement if the sufficiency basis later fails.

## Sentences this page may support

- `single authorized principal was sufficient and signed final release`
- `delegate signature valid, but countersign still required for waiver`
- `quorum reached for capped settlement; unanimity still required for final residue waiver`
- `vacant required seat leaves probation lift frozen`
- `prior closure withdrawn because successor ratification never occurred`

## Mandatory proof blocks

### A. Action-and-rule block

- source coalition review
- attempted action
- coalition model for this action
- strongest sentence actually earned
- stronger sentence still blocked

### B. Satisfaction block

- required seats for the earned sentence
- seats actually counted
- count method used (`single`, `countersign`, `quorum`, `unanimous`, `adjudicated`)
- whether silence or timeout contributed and under which rule
- whether successor ratification was required and satisfied

### C. Residue-and-fallback block

- weaker truths that still survive
- open residue that was not waived
- whether restoration remains partial
- whether probation remains active
- whether future-burst release remains blocked

### D. Fragility-and-reopen block

- earliest event that would reopen this proof
- seat-turnover risk now
- revocation or challenge risk now
- whether current proof depends on temporary vacancy assumptions
- exact event that would make closure more final

### E. Audit block

- decisive signers or seats
- decisive timestamps
- decisive objections or abstentions preserved
- dominance or adjudication reference if used
- strongest withdrawn sentence, if any

## Required badges

- `sole-signer-sufficient`
- `countersigned`
- `quorum-satisfied`
- `unanimity-satisfied`
- `successor-ratified`
- `vacancy-assumption-active`
- `final-release-eligible`
- `final-release-not-eligible`
- `reopened-for-sufficiency-defect`
- `adjudicated-finality`

Badges must stack instead of erasing lineage.
For example, `quorum-satisfied` may coexist with `final-release-not-eligible` when unanimity is still required for full waiver.

## Proof obligations

- prove sufficiency separately from signer validity
- prove final-waiver threshold separately from partial-settlement threshold
- preserve open residue when only a narrower coalition threshold was met
- preserve reopen risk when vacancy, succession, or challenge assumptions remain load-bearing
- preserve withdrawn stronger sentences when later sufficiency review fails

## Stronger-sentence guard

This page may say `three-seat quorum satisfied for staged settlement; final release still requires absent principal countersign`.
It may not say `all creditor rights extinguished` until the stronger threshold is actually met.
