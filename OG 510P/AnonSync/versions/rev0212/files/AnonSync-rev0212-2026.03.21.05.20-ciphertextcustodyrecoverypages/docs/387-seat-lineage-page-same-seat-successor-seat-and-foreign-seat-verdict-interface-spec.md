# Seat lineage page: same seat, successor seat, and foreign seat verdict interface spec

## Purpose

The archive already has strong identity, replacement, and retirement doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> is this still the same seat I trusted before, a reviewed successor to it, a foreign seat with a confusingly similar label, or merely stale roster residue?

## Core decision

Every serious seat-continuity system must own one first-class **Seat lineage** page.
That page is the semantic home of:

- current seat identity proof
- compared prior seat record
- lineage verdict
- continuity-survival summary
- strongest next-safe action
- lineage receipts

The product must not let seat name, hostname, or local path reuse stand in for this page.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. seat-comparison strip
2. lineage verdict card
3. proof comparison card
4. continuity-survival card
5. action ladder card
6. recent lineage receipts
7. expert details drawer

### 1) Seat-comparison strip

Show:

- current seat
- compared prior seat
- strongest next-safe action
- whether the comparison is live, historical, or only partially evidenced

The strip should answer `which two seat stories am I comparing?`

### 2) Lineage verdict card

Show one explicit verdict:

- `same seat`
- `reviewed successor seat`
- `foreign seat`
- `replaced by certificate takeover`
- `insufficient evidence`
- `stale roster residue only`

Also show the strongest sentence explaining why.

### 3) Proof comparison card

Show:

- current certificate / fingerprint handle
- prior certificate / fingerprint handle
- stable evidence that matches or mismatches
- what evidence is label-only and therefore weak
- which facts were learned locally versus from another peer's memory

This card should answer `what makes this lineage verdict trustworthy?`

### 4) Continuity-survival card

Show what continuity truly survived:

- local bytes
- subject bindings
- linked-family membership
- remembered approvals
- preferences / policy
- operator history / receipts

This card should answer `what actually carried forward?`

### 5) Action ladder card

Offer only deliberate actions, for example:

1. `Keep as same seat`
2. `Declare successor to prior seat`
3. `Retire stale old row`
4. `Treat as foreign seat and require fresh trust`
5. `Escalate because lineage evidence is weak`

Every action must preview what continuity interpretation will change.

### 6) Recent lineage receipts

Show recent receipts with:

- compared seats
- lineage verdict
- deciding operator / seat
- continuity-survival summary
- action taken

### 7) Expert details drawer

Hide raw certificate blobs, peer-introduced aliases, storage-root hashes, and route witnesses behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. current seat phrase
2. compared-prior phrase
3. lineage verdict phrase
4. continuity-survival phrase
5. strongest next action

Example:

```text
Laptop-02 vs archived Laptop-02 row · successor seat, not same certificate · local bytes preserved but remembered trust not inherited · Declare successor and require fresh grant review
```

## Mandatory fields

- `current_seat_ref`
- `compared_prior_seat_ref` nullable
- `lineage_verdict`
- `current_identity_proof_ref`
- `prior_identity_proof_ref` nullable
- `proof_match_summary`
- `continuity_survival_summary`
- `available_lineage_actions[]`
- `strongest_next_action`

## Review guarantees

This page must let the operator:

- tell seat identity from seat label
- distinguish same-seat continuity from successor continuity
- spot when continuity is only local-byte preservation rather than trust continuity
- act on stale or duplicate rows without pretending they were the same seat all along
