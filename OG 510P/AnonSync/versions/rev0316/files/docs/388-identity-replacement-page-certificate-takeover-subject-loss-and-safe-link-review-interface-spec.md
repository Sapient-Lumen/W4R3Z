# Identity replacement page: certificate takeover, subject loss, and safe-link review interface spec

## Purpose

The archive already has strong linking and replacement doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> if I continue this link / repair / import action, am I merely relating seats, or am I about to replace a seat identity and drop subjects out of the app?

## Core decision

Every serious linking and recovery system must own one first-class **Identity replacement** page.
That page is the semantic home of:

- candidate replacement operation
- certificate-takeover verdict
- subject-loss preview
- resulting roster change
- preservation guarantees and non-guarantees
- final apply gate

The product must not let an ordinary `Link device`, `Import`, or `Reset` verb silently cross into destructive identity replacement.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. replacement-intent strip
2. takeover verdict card
3. subject-loss preview card
4. preservation / non-preservation card
5. safe alternatives card
6. final apply gate
7. recent replacement receipts
8. expert details drawer

### 1) Replacement-intent strip

Show:

- current seat
- candidate donor / target identity
- operation being attempted
- strongest next-safe action

The strip should answer `who would replace whom, through what action?`

### 2) Takeover verdict card

Show one explicit verdict:

- `no identity replacement`
- `reviewed successor bind only`
- `certificate takeover will occur`
- `replacement impossible without prior cleanup`
- `insufficient evidence`

Also show the precise sentence explaining why.

### 3) Subject-loss preview card

Show:

- which subjects would remain
- which subjects would be removed from the app
- whether local bytes remain on disk
- whether any platform-specific delete hazard exists
- what new subjects would appear from the donor side

This card should answer `what subject world changes if I continue?`

### 4) Preservation / non-preservation card

Show separately:

- what continuity is preserved
- what continuity is not preserved
- which rights / remembered approvals would need fresh review
- which changes are reversible only by later recovery work

This card should answer `what do I actually keep, and what do I lose?`

### 5) Safe alternatives card

Offer safer branches, for example:

- `Relate seats without replacement`
- `Declare successor after fresh export/import review`
- `Unlink locally and recreate identity first`
- `Keep identities separate and share by grant lane`
- `Abort; destructive replacement not desired`

### 6) Final apply gate

The final gate must require the operator to acknowledge:

- the replacement verdict
- the expected subject-loss class
- the non-preserved continuity items
- the exact seat that will remain after apply

### 7) Recent replacement receipts

Show recent receipts with:

- source seat
- target seat
- takeover verdict
- subject-loss summary
- final action

### 8) Expert details drawer

Hide raw donor-token material, certificate lineage internals, and per-subject migration witnesses behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. operation phrase
2. takeover verdict phrase
3. subject-loss phrase
4. preservation phrase
5. strongest next action

Example:

```text
Link running Tablet-A into Desktop family · certificate takeover will occur · 3 advanced subjects leave app view though local bytes remain · Abort and use reviewed successor flow instead
```

## Mandatory fields

- `operation_ref`
- `current_seat_ref`
- `candidate_identity_ref`
- `takeover_verdict`
- `subject_loss_summary`
- `preserved_continuity_items[]`
- `non_preserved_continuity_items[]`
- `safe_alternatives[]`
- `apply_gate_requirements[]`
- `strongest_next_action`

## Review guarantees

This page must let the operator:

- know before apply whether identity replacement is happening at all
- see which subjects leave app governance even if bytes remain on disk
- choose a safer non-replacement path when desired
- prevent `link` from silently meaning `replace`
