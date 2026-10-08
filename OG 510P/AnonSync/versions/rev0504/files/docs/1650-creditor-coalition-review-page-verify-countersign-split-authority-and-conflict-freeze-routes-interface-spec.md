# Creditor coalition review page — verify countersign, split authority, and conflict-freeze routes

## Purpose

This page is the operator workspace for deciding whether the current signer set is sufficient for the action being attempted.
It exists so the archive can review coalition truth directly instead of over-reading one seemingly valid signature.

## Main questions the review must answer

1. What action is being attempted right now?
2. Which seats are required for that action?
3. Which required seats are validly occupied and currently consenting?
4. Is conflict present among valid seats?
5. What weaker route is still allowed if the stronger route is blocked?

## Mandatory review blocks

### A. Attempted-action block

- attempted action (`receipt`, `partial-settlement`, `capped-settlement`, `waiver`, `probation-lift`, `final-release`, `reopen`, `other`)
- source coalition contract sheet
- strongest sentence the operator is trying to earn
- weaker fallback sentence if sufficiency fails

### B. Required-seat evaluation block

For each seat the page must show:

- seat label
- required for this action (`yes`, `no`, `fallback-only`)
- occupant validity now
- consent state (`consents`, `objects`, `silent`, `unreachable`, `vacant`, `challenged`)
- whether this seat's absence blocks only stronger acts or all acts
- whether substitute seat is allowed and proven

### C. Sufficiency verdict block

- current sufficiency class (`met`, `partially-met`, `not-met`, `frozen-by-conflict`, `pending-successor`, `pending-adjudication`)
- exact missing seat or consent
- whether quorum math is satisfied
- whether unanimity is satisfied
- whether countersign path is satisfied
- whether silent members count under this rule
- strongest sentence currently supportable

### D. Narrower-route block

- partial action that may proceed now
- accounting credit that may be booked now
- residue that must remain open
- whether probation remains frozen
- whether future-burst posture remains tightened
- exact stronger statement that remains blocked

### E. Conflict-resolution block

- conflict source
- rule that governs the conflict
- next dominance proof, adjudication, or ratification needed
- whether earlier partial acts stay valid if conflict persists
- whether earlier stronger acts must be withdrawn

## Required comparisons

The review must keep these comparisons explicit:

- `one valid signer` vs `enough valid signers`
- `consent absent` vs `consent refused`
- `vacancy` vs `temporary unreachable occupant`
- `narrower act may proceed` vs `stronger closure frozen`
- `successor present` vs `successor ratified for this action`

## Failure modes the page must prevent

- treating a prestigious signer as sufficient when the rule requires more seats
- letting silence do the work of explicit consent without rule support
- collapsing seat vacancy and active objection into the same state
- allowing final release to survive after required-seat turnover invalidated sufficiency
- forgetting that partial settlement can remain true while final closure is false

## Stronger-sentence guard

The review may say `reserve guardian and principal delegate agreed, finance seat still vacant; capped settlement may proceed, final waiver blocked`.
It may not say `case fully closed` until the exact coalition rule for that stronger sentence is satisfied.
