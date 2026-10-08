# Pending claim page: request visibility, approval locus, and route gap interface spec

## Purpose

The archive already has strong offer, claim-lane, and pending-state doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> why is this claimant still pending, which exact seat may approve it, and is the blocker human decision, remembered-trust policy, or request visibility / route reachability?

## Core decision

Every serious incoming claim must own one first-class **Pending claim** page.
That page is the semantic home of:

- claimant and subject
- current pending-state verdict
- approver-locus truth
- request-visibility truth
- remembered-trust applicability
- strongest next-safe action

The product must not let a pending badge stand in for this page.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. claimant-and-subject strip
2. pending-state card
3. approver-locus card
4. request-visibility / route-gap card
5. remembered-trust card
6. strongest-next-action card
7. recent pending-state receipts
8. expert details drawer

### 1) Claimant-and-subject strip

Show:

- claimant identity / seat
- subject
- entry lane
- requested right if approved
- strongest next-safe action
- whether the page is live, reviewing a stale request, or reviewing a request that already resolved

The strip should answer `who is waiting for what?`

### 2) Pending-state card

Show one explicit verdict:

- `awaiting human decision`
- `awaiting request visibility on eligible seat`
- `eligible for remembered auto-approval when qualifying seat is online`
- `reprompt forced by current policy`
- `blocked because no current seat is eligible to approve`
- `historical pending state; claim already resolved elsewhere`

Also show:

- when the claim was first emitted
- whether the claimant retried or only emitted once
- whether the claimant sees `pending`, `retrying`, `approved`, or `denied`

This card should answer `what kind of pending is this really?`

### 3) Approver-locus card

Show:

- the original issuing seat if any
- all currently eligible linked seats
- why each seat is eligible or ineligible
- required subject-presence floor on each seat
- whether the eligible seat is currently online / reachable enough to receive the request

This card should answer `which seat may approve this claim right now?`

### 4) Request-visibility / route-gap card

Show:

- whether the request reached any current eligible seat
- last observed request receipt time on each candidate seat
- whether the claimant can reach the issuer / approver directly, via relay, or not at all
- whether the current pending state is actually route failure masquerading as missing approval
- evidence ceiling: what the product can prove locally versus infer from absence

This card should answer `did the approver really see this request?`

### 5) Remembered-trust card

Show:

- whether claimant identity matches a remembered trust record
- whether current lane / subject policy allows remembered auto-approval
- whether a prior approval exists only for a narrower scope
- what exact rule forced a fresh prompt if reprompt happened

This card should answer `should this have auto-approved?`

### 6) Strongest-next-action card

Show the strongest honest next action, for example:

1. `Approve from this seat`
2. `Open claim inspection first`
3. `Open approval authority page on another eligible seat`
4. `Wait for eligible seat to come online for remembered auto-approval`
5. `Open route diagnosis because no eligible seat has received the request`
6. `Deny and issue narrower successor lane`

This card should answer `what is the safest next move?`

### 7) Recent pending-state receipts

Show recent receipts with:

- claimant
- subject
- pending-state verdict
- eligible-approver set
- request-visibility verdict
- action taken

### 8) Expert details drawer

Hide raw request IDs, transport traces, retry windows, relay / direct route candidates, and certificate digests behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. claimant phrase
2. subject / lane phrase
3. pending-state phrase
4. approver-locus phrase
5. strongest next action

Example:

```text
Alex requesting RW on Project Atlas · pending because no eligible seat has seen request yet · approvable from Laptop-02 once subject reconnected · Open route diagnosis
```

## Mandatory fields

- `claim_ref`
- `claimant_ref`
- `subject_ref`
- `entry_lane`
- `requested_right`
- `pending_state_verdict`
- `pending_state_reason`
- `eligible_approver_seat_refs[]`
- `ineligible_approver_seat_refs[]`
- `request_visibility_verdict`
- `request_first_emitted_at`
- `request_last_seen_by_any_eligible_seat_at` nullable
- `remembered_trust_applicability`
- `strongest_next_action`

## Review guarantees

This page must let the operator:

- tell whether `pending` means waiting on a human or waiting on request visibility
- tell which seat may approve and why
- tell whether remembered trust should have applied
- move directly into inspection, approval, denial, or route diagnosis without reopening the world
