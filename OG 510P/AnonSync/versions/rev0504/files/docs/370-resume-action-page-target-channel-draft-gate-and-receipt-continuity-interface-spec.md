# Resume action page: target-channel draft, gate, and receipt continuity interface spec

## Purpose

The archive already had handoff doctrine.
This document makes the target-side continuation page concrete.

The page exists to answer one ordinary operator question:

> after switching channels, did I really resume the same reviewed action, what changed on arrival, and what receipt chain now proves continuity or reopen?

## Core decision

Every consumed review handoff must land on one first-class **Resume action** page.
That page is the semantic home of:

- inherited action identity
- target-channel capability state
- drift and reopen checks
- resumed action lane
- receipt chain
- fallback back-out or re-handoff options

The product must not leave the operator guessing whether the target channel continued the same work or silently started over.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. resume strip
2. inherited-context card
3. target-channel capability card
4. drift-and-reopen card
5. resumed action lane
6. receipt-chain card
7. fallback and back-out tools

### 1) Resume strip

Show:

- resumed action family
- subject
- source → target channel pair
- resume verdict
- strongest next-safe action

Allowed resume verdicts:

- `same reviewed action resumed`
- `same review resumed after revalidation`
- `broader review reopened`
- `resume blocked by new drift`
- `handoff expired before resume`

### 2) Inherited-context card

Show:

- preserved subject reference
- preserved review family
- inherited draft or plan handle
- inherited gate or capability reference
- source-channel blocker context carried forward
- which sections arrived already complete

This card should answer `what exactly made it across the channel boundary?`

### 3) Target-channel capability card

Show:

- target channel kind
- current trust/session posture
- current support state for the action
- whether apply is possible now
- any narrower limits specific to this target

This card should answer `what can this target channel honestly do with the inherited review?`

### 4) Drift-and-reopen card

Show:

- state that was revalidated on arrival
- new drift found, if any
- whether drift only required revalidation or forced broader review
- which old assumptions are still safe and which are no longer trusted

Examples of reopen causes:

- target seat differs from the one originally intended
- trust/session posture changed materially
- subject or policy revision drifted
- capability/gate changed or expired
- runtime/root identity changed

### 5) Resumed action lane

This section should preserve the honest next action, such as:

- `Continue inspection`
- `Resume guarded apply`
- `Reopen broader review`
- `Repair target-channel trust`
- `Abandon this handoff and return`

The page must not reduce a reopened review to a cosmetic warning.

### 6) Receipt-chain card

Show the linked receipts and objects in order:

- source availability or mismatch receipt when relevant
- handoff receipt
- resume receipt
- eventual apply or refusal receipt

The operator should be able to answer `what later proves that this was the same action, or proves exactly where it stopped being the same action?`

### 7) Fallback and back-out tools

Show:

- return to source-channel explanation
- create a second reviewed handoff if this target is still insufficient
- abandon the inherited draft safely
- export continuity proof before broader reopen

## Acceptance criteria

This spec is satisfied when:

- the target channel proves whether it resumed the same review or reopened broader work
- revalidation and reopen are visibly different outcomes
- receipt continuity survives source-channel failure, target-channel repair, and eventual apply or refusal
- switching channels never forces the operator to rely on memory alone for continuity claims
