# Settlement authority proof page — valid releasor, waiver scope, and reopen risk

## Purpose

This page is the durable proof object for the strongest true sentence available when a representative has been reviewed.
It exists so the archive can say exactly who may accept which settlement actions, which stronger powers remain blocked, and whether a future authority challenge can reopen the case.

## Sentences this page may support

- `principal accepted partial reserve repair; named residue not waived`
- `delegate may receive payment acknowledgment but may not close the case`
- `role-based representative may sign capped settlement with countersign still required for waiver`
- `full release validly signed by authorized principal or valid full-scope delegate`
- `prior release withdrawn because authority had expired`

## Mandatory proof blocks

### A. Principal-and-representative block

- source creditor authority contract sheet
- acting speaker for the current action
- representative class
- verified principal behind that speaker
- whether the speaker is self-acting or delegated

### B. Scope block

- settlement actions allowed now
- settlement actions blocked now
- waiver scope now (`none`, `partial`, `full`, `countersigned-only`)
- probation-lift authority now (`none`, `limited`, `full`)
- reopen power now (`none`, `new-evidence-only`, `full-challenge-right`)
- strongest sentence the proof may currently support

### C. Freshness-and-challenge block

- oldest load-bearing authority evidence still relied on
- earliest expiry or rereview deadline
- revocation risk now
- role-continuity risk now
- whether clean release is frozen by authority risk

### D. Consequence block

- what settlement credit may be booked now
- what weaker sentence still survives
- what stronger sentence remains blocked
- whether restoration, probation lift, or future-burst release remains frozen by authority gap
- exact fact needed to improve the sentence

### E. Reopenability block

- reopen allowed now
- reopen trigger threshold
- exact event that would invalidate the current proof
- exact event that would make this closure final

## Required badges

- `self-authorized`
- `delegate-limited`
- `countersign-required`
- `waiver-not-proven`
- `probation-lift-not-proven`
- `authority-challenge-open`
- `release-freeze-active`
- `full-releasor-verified`
- `reopened-for-authority-defect`
- `final-closure-eligible`

Badges must stack instead of erasing lineage.
For example, `delegate-limited` may coexist with `release-freeze-active` and `waiver-not-proven`.

## Proof obligations

- prove representative scope separately from creditor existence
- prove waiver authority separately from payment-receipt authority
- preserve weaker surviving sentences when only part of authority is proven
- preserve reopen risk when authority freshness is near expiry or contested
- preserve history when a prior stronger sentence is later withdrawn

## Stronger-sentence guard

This page may say `delegate accepted settlement slice; residue and reopen rights survive`.
It may not say `creditor fully released` until the acting speaker is proven to hold that stronger scope.
