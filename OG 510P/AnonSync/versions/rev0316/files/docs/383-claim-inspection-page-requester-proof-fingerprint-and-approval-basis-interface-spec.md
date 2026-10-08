# Claim inspection page: requester proof, fingerprint, and approval basis interface spec

## Purpose

The archive already has strong claimant, authority, and review-receipt doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> who exactly is asking for access here, what proof do I have about that requester, and what exact authority will I create if I approve?

## Core decision

Every serious incoming claim that can be approved by a human must own one first-class **Claim inspection** page.
That page is the semantic home of:

- claimant identity proof
- receipt evidence
- lane and artifact basis
- resulting authority if approved
- remembered-trust history
- approval / deny / narrow options

The product must not collapse approval into a one-line popup.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. claimant strip
2. proof card
3. receipt-and-lane card
4. resulting-authority card
5. remembered-history card
6. decision card
7. recent decision receipts
8. expert details drawer

### 1) Claimant strip

Show:

- claimant name / seat alias
- claimant identity family if known
- subject
- current requested right
- strongest next-safe action

The strip should answer `who is asking for what?`

### 2) Proof card

Show:

- claimant fingerprint or canonical identity proof
- whether it matches a previously seen identity exactly, approximately, or not at all
- claimant-reported IP / route witness if available
- proof freshness and receipt time
- whether the operator has enough proof to compare out-of-band if desired

This card should answer `what proof am I actually using to recognize the requester?`

### 3) Receipt-and-lane card

Show:

- entry lane used (`link`, `key`, `QR`, `linked-family arrival`, imported artifact, etc.)
- artifact or request family that produced the claim
- whether the request carries approval, expiry, or use-budget semantics
- whether approval here is creating a certificate-backed right, a narrower one-shot access, or some other governed result

This card should answer `what exact claim path produced this request?`

### 4) Resulting-authority card

Show:

- resulting right if approved
- onward-share ceiling if approved
- future-scope consequence
- whether approval also creates remembered trust for later claims
- whether approval here is broader or narrower than current policy intent

This card should answer `what authority will I create if I approve?`

### 5) Remembered-history card

Show:

- prior approvals for the same claimant identity
- whether any of them came from another linked seat
- prior denials or supersessions
- current remembered-trust scope for this claimant
- whether current policy requires reprompt despite remembered history

This card should answer `how does past trust matter right now?`

### 6) Decision card

Offer only honest choices, for example:

- `Approve as requested`
- `Approve narrower`
- `Deny`
- `Require fresh out-of-band verification`
- `Open approval memory first`
- `Open reissue plan because requested right is too broad for this lane`

The decision card must show a plain-language consequence summary before commitment.

### 7) Recent decision receipts

Show recent receipts with:

- claimant
- proof verdict
- lane
- resulting right approved / denied
- remembered-trust consequence
- deciding seat

### 8) Expert details drawer

Hide raw certificate material, ACL serials, protocol traces, and route-level metadata behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. claimant phrase
2. proof-match phrase
3. lane phrase
4. resulting-authority phrase
5. decision availability phrase

Example:

```text
Alex / fp 9C:7A… exact prior match · link claim with per-peer approval · would create RW without onward share · Approve narrower or approve as requested
```

## Mandatory fields

- `claim_ref`
- `claimant_ref`
- `claimant_display_name`
- `identity_proof_ref`
- `identity_match_verdict`
- `proof_received_at`
- `subject_ref`
- `entry_lane`
- `requested_right`
- `resulting_right_if_approved`
- `onward_share_ceiling_if_approved`
- `remembered_history_summary`
- `decision_options[]`
- `strongest_next_action`

## Review guarantees

This page must let the operator:

- identify the requester by stable proof rather than by name alone
- understand what exact lane and artifact produced the claim
- understand what authority approval would create
- choose approve, narrow, deny, or escalated verification without leaving the review basis behind
