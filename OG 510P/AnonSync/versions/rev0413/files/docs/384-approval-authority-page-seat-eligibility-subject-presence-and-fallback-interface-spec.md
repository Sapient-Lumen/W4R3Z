# Approval authority page: seat eligibility, subject presence, and fallback interface spec

## Purpose

The archive already has strong linked-seat and surface-capability doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> which current seat may approve this claim, why is that true here, and what is the safest fallback if this seat cannot decide it?

## Core decision

Every serious approval flow must own one first-class **Approval authority** page.
That page is the semantic home of:

- candidate deciding seats
- eligibility verdict per seat
- subject-presence floor
- operator-role ceiling
- fallback / handoff plan
- approval-authority receipts

The product must not let `linked device` or `issuer device` stand in for this page.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. approval-target strip
2. candidate-seat matrix
3. subject-presence card
4. deciding-authority card
5. fallback-and-handoff card
6. recent authority receipts
7. expert details drawer

### 1) Approval-target strip

Show:

- claimant
- subject
- requested right
- current seat from which the page is being viewed
- strongest next-safe action

The strip should answer `approval for whom, on what, from where?`

### 2) Candidate-seat matrix

For each candidate seat show:

- seat name
- linked-family relation
- current online / reachable state
- whether subject is `absent`, `disconnected`, `selective`, `full`, `historical-only`, or `unknown`
- eligibility verdict (`may approve now`, `may approve after subject reconnect`, `cannot approve from this seat`, `insufficient evidence`)
- why

This matrix should answer `which seats can actually decide this claim?`

### 3) Subject-presence card

Show:

- minimum subject presence required for approval on a seat
- whether current seat satisfies that requirement
- whether mere linked relationship is insufficient here
- whether the claim can be observed but not decided from some seats

This card should answer `what must be true about the subject on a seat before that seat can approve?`

### 4) Deciding-authority card

Show:

- whether the current operator on the current seat has authority to approve, narrow, or deny
- whether another seat has stronger or weaker decision scope
- whether the lane or subject class narrows what the deciding seat may grant even if it can approve the claim
- whether the deciding act would create remembered trust or only one-time authorization

This card should answer `if this seat is eligible, what can it actually decide?`

### 5) Fallback-and-handoff card

Show the strongest safe fallback ladder, for example:

1. `Approve here now`
2. `Reconnect subject on Seat-B and approve there`
3. `Open review handoff to eligible seat`
4. `Wait for online eligible seat; no current seat can decide`
5. `Deny here not possible; open claimant notice instead`

This card must preserve the review basis when handing off.

### 6) Recent authority receipts

Show recent receipts with:

- deciding seat
- subject-presence verdict
- authority verdict
- action taken
- whether handoff was required

### 7) Expert details drawer

Hide raw linkage IDs, sync-mode witnesses, ACL role proofs, and route traces behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. seat phrase
2. subject-presence phrase
3. eligibility phrase
4. authority-scope phrase
5. fallback phrase

Example:

```text
Laptop-02 · subject present selective · may approve now · may grant RO/RW but not broader than lane ceiling · Approve here or hand off reviewed denial to Desktop-01
```

## Mandatory fields

- `claim_ref`
- `subject_ref`
- `current_viewing_seat_ref`
- `candidate_seat_rows[]`
- `minimum_subject_presence_required`
- `current_seat_subject_presence`
- `current_seat_eligibility_verdict`
- `current_seat_authority_scope`
- `fallback_plan[]`
- `strongest_next_action`

## Review guarantees

This page must let the operator:

- distinguish linked seats from currently eligible approver seats
- see why a seat is or is not eligible right now
- preserve review context when approval must move to another seat
- understand the deciding ceiling of the chosen seat before committing
