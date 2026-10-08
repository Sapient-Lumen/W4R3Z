# Capability-owner transfer and seat-starvation boundary interface spec

## Purpose

The archive already has subject authority, compromise response, and owner-domain language.
What it still lacked was one explicit contract for a different ownership seam:

> when a feature-capability or entitlement owner moves from one seat to another, what page proves that only capability ownership moved, who loses access if seat budget is exhausted, and what did **not** change about subject/data authority?

Current official Resilio docs make this seam vivid.
They still say applying the license key on a new device transfers license ownership to that device, that the older owner becomes a user if spare seats exist, and that if all seats are already shared one user may lose access.
A current stolen-device page still says the owner is the peer that activated the license most recently, that re-adding the license overrides the previous activation, and that the thief's instance will later revert to Free if it comes online.

That is not just billing trivia.
It means capability ownership can jump seats as a side effect of activation, while data/trust recovery is handled elsewhere.

AnonSync should therefore keep capability-envelope ownership separate from subject/data authority and render transfer/starvation explicitly.

## Core decision

Any capability-envelope transfer must be reviewed as its own mutation class.
The product must separate three questions that weaker products blur together:

1. **who owns the capability envelope now**
2. **which seats currently consume limited seats within that envelope**
3. **what subject/data/control authority is entirely unaffected by this transfer**

The product must never let `apply capability on another seat` silently mean `some other seat lost power`.

## Fixed review order

Every capability-owner transfer should render the same sections in the same order:

1. **Current capability graph**
2. **Requested owner transfer**
3. **Seat-budget impact and starvation simulation**
4. **Receipt and unaffected authority statement**

### 1) Current capability graph

This section should show:

- current capability owner seat
- all seats currently consuming the capability envelope
- total seat budget and free headroom
- any seats already in grace, degraded, or pending removal state

The operator must be able to answer: **who owns this capability envelope now, and how full is it?**

### 2) Requested owner transfer

This section should show:

- proposed new owner seat
- whether the transfer is routine, incident-driven, or stolen-seat containment
- whether the old owner remains a user, becomes unentitled, or enters grace
- whether the transfer implies any credential/token retirement

The operator must be able to answer: **what changes hands, and is this a normal move or an emergency override?**

### 3) Seat-budget impact and starvation simulation

This section should show:

- resulting seat allocation if the transfer succeeds
- which seat(s), if any, would lose capability because the budget is exhausted
- whether those seats lose premium capability immediately, after grace, or only on next contact
- alternative transfers that avoid starvation

The operator must be able to answer: **who loses access if I do this, and can I avoid that?**

### 4) Receipt and unaffected authority statement

This section should show:

- capability owner before/after
- seat-budget before/after
- seats downgraded or spared
- explicit statement of what subject/data/control authority did **not** change
- follow-up actions still needed for incident containment or subject trust repair

The operator must be able to answer: **what later proves this was a capability move, not a hidden subject-authority rewrite?**

## Public objects

### `capability_owner_transfer_review`

Fields:

- `capability_owner_transfer_review_id`
- `capability_envelope_ref`
- `current_owner_seat_ref`
- `requested_owner_seat_ref`
- `transfer_reason`
- `current_consumer_seat_refs[]`
- `seat_budget_summary`
- `starvation_findings[]`
- `unaffected_authority_statement`
- `generated_at`

### `capability_owner_transfer_receipt`

Fields:

- `capability_owner_transfer_receipt_id`
- `review_ref`
- `capability_envelope_ref`
- `before_summary`
- `after_summary`
- `downgraded_seat_refs[]`
- `retired_token_refs[]`
- `followup_refs[]`
- `created_at`

## Main surface

A compact row should read like one of these:

- `capability owner moved · no seat starvation`
- `incident override applied · old owner downgraded on next contact`
- `blocked · transfer would starve 1 seat`
- `owner moved · subject authority unchanged`

## CLI shape

```text
anonsync capability owner show --envelope family-pro
anonsync capability owner review --envelope family-pro --to seat:laptop-ember
anonsync capability owner apply <review>
anonsync capability owner receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- reapplying capability on a new seat can silently demote another seat
- incident-driven owner override still requires the operator to infer which other seats will lose access
- capability transfer is mistaken for subject-authority repair
- the operator cannot later prove whether an access loss came from budget starvation or deliberate subject revocation

## Non-clone reason

Current Resilio docs still let capability ownership jump to the most recently activated seat and explicitly warn that another seat may lose access if the budget is full.
AnonSync should instead review capability-owner transfer, starvation risk, and unaffected subject authority as one explicit receipt-bearing action.
