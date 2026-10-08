# Creditor representation review page — verify, delegate, split scope, and freeze routes

## Purpose

This page is the operator review for deciding what to do when a person, role, device, or policy actor claims the right to speak for a creditor.
It must answer:

> do we verify the principal, verify a limited delegate, split acceptable powers from blocked ones, freeze release, escalate for countersign, or reopen because the speaker was never truly authorized?

## Mandatory review inputs

- source creditor authority contract sheet
- source creditor verification state and any dispute residue
- proposed settlement, waiver, absorber, probation, or reopen action
- authority proof materials and freshness horizons
- role-directory, delegation instrument, or principal confirmation if one exists
- current release freeze and future-burst posture

## Required review routes

### Route 1 — verify self-acting principal

Allowed only when:

- principal identity is sufficiently matched to the creditor record
- no material impersonation or successor challenge remains
- requested action stays inside the creditor's own power under policy

### Route 2 — verify limited delegate

Default route when:

- delegation basis is real
- some powers are clearly granted
- stronger powers such as waiver, probation lift, or final closure are not clearly granted

This route must preserve:

- the powers clearly granted now
- the stronger sentences still blocked
- the exact countersign or rereview needed to expand scope

### Route 3 — split settlement authority from waiver authority

Required when:

- the representative may accept money or service credit
- but the representative may not waive residue or reopen rights
- or the representative may negotiate but not sign final closure

### Route 4 — freeze release and keep weaker consequences alive

Required when:

- authority proof is stale, expired, revoked, or challenged
- role occupancy changed
- linked-identity, certificate, or operator continuity is in doubt
- a proposed release exceeds the verified scope

### Route 5 — require countersign or named absorber

Allowed only when:

- a limited representative can move the case forward
- but final waiver or absorption needs an additional authority layer
- the product can render the remaining weaker sentence explicitly

### Route 6 — deny or revoke claimed authority

Allowed only when:

- the speaker cannot prove principal or delegated status strongly enough
- no narrower safe scope remains
- denial explains which actions remain blocked and who may still act

### Route 7 — reopen because prior speaker was stale or over-scoped

Required when:

- new evidence shows prior authority had expired or been revoked
- the speaker was a device, operator, or role-holder without actual release power
- a prior closure exceeded the earlier verified scope

Reopen must be able to:

- withdraw a prior stronger sentence
- re-freeze release
- re-open probation or future-burst constraints
- preserve already accepted narrower actions that remain valid

## Required outputs

- chosen authority verdict
- verified representative set after review
- blocked powers after review
- whether partial settlement may proceed now
- whether waiver or probation lift remains frozen
- next countersign, proof, or ruling required
- strongest sentence still blocked

## Required comparisons

The page must keep these comparisons explicit:

- `authorized to receive settlement` vs `authorized to grant release`
- `authorized to negotiate` vs `authorized to sign`
- `role holder today` vs `delegation still current`
- `device owner` vs `creditor representative`
- `administrative convenience` vs `truthful authority`

## Failure modes the page must prevent

- clearing a case because the easiest reachable operator said it was fine
- converting device or Owner status into silent waiver authority
- using a stale delegation instrument after role exit or identity takeover
- forgetting that a narrower valid act can coexist with blocked stronger acts
- preserving a bad release simply because rollback is awkward

## Stronger-sentence guard

The review may say `manager may accept capped repayment; principal or countersigner still required for full waiver`.
It may not say `case finally closed` until verified authority actually reaches that stronger sentence.
