# Seat loan and reclaim review page — unique identity budget, approval, and owner-expiry cascade

## Purpose

This page exists because a borrowed seat is not just `one more licensed device`.
The real question is:

> which unique identity is consuming budget here, who approved it, who can reclaim it, and what happens to this borrower if the owner expires or retreats?

## Core decision

Borrowing, approving, reclaiming, or reclassifying a seat must pass through one dedicated **Seat loan and reclaim review** page.

## Fixed page order

1. borrower summary
2. counted-identity card
3. approval and management card
4. reclaim and expiry cascade card
5. safer alternatives card

### 1) Borrower summary

Show:

- borrower identity
- current seat class
- owner identity
- current entitlement verdict
- strongest next-safe action

### 2) Counted-identity card

Publish:

- unique identity consuming budget
- whether linked devices under that identity collapse into one counted unit
- current remaining budget after approval
- whether this borrower could be served by link-under-owner instead of borrowed seat, or vice versa

### 3) Approval and management card

Show:

- who must approve the seat
- whether borrower can manage any further seats
- whether borrower may merely consume
- whether approval creates any standing rights beyond current entitlement

### 4) Reclaim and expiry cascade card

Publish:

- who can reclaim the seat
- what reclaim removes immediately vs what bytes remain local
- whether owner expiry propagates here
- whether owner license removal leaves this borrower intact, reduced, or future-unstable
- strongest blocked sentence about independence

### 5) Safer alternatives card

Offer reviewed alternatives such as:

- `link these devices under one identity instead`
- `split this borrower into a separate line family`
- `delay reclaim until export / continuity receipt`
- `replace borrowed seat with self-owned entitlement`

## Public object

### Seat loan and reclaim review

Fields:

- `seat_loan_review_id`
- `owner_identity_ref`
- `borrower_identity_ref`
- `counted_unit_basis`
- `approval_required`
- `borrower_management_scope`
- `reclaim_effects[]`
- `expiry_cascade_effects[]`
- `safer_alternatives[]`
- `generated_at`

## Rules

### Rule 1 — borrowed is not self-owned

The page must keep dependency language explicit.

### Rule 2 — reclaim is not erasure

Any reclaim preview must separate entitlement loss from byte survival and later reconnect possibilities.

### Rule 3 — budget unit must be identity-true

If the real unit is unique identity rather than device count, the page must say so plainly.

## Acceptance criteria

A later operator can:

- tell which unique identity consumes budget
- tell who must approve and who may reclaim
- tell whether owner expiry cascades here
- tell whether a safer topology exists before borrowing another seat