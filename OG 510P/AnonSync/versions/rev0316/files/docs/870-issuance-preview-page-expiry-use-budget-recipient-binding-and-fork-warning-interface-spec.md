# Issuance preview page: expiry, use budget, recipient binding, and fork warning interface spec

## Purpose

This page exists because `copy link`, `show QR`, and `rotate key` are not small UI actions.
They create authority objects with scope, lifetime, and continuity consequences.

The operator question is:

> if I issue this artifact now, what exact authority object will exist, who is it for, how long will it work, and what continuity damage or fork could this create later?

## Core decision

Every serious invite, link, key, QR, or successor artifact issuance must render one first-class **Issuance preview** page before export.

## Fixed page order

1. issuance strip
2. resulting artifact card
3. recipient binding card
4. expiry and use-budget card
5. continuity and fork-warning card
6. safe export options
7. pending receipt summary

### 1) Issuance strip

Show:

- artifact family to be issued
- source seat / subject
- intended audience
- strongest next-safe action

### 2) Resulting artifact card

Publish:

- resulting family
- resulting authority ceiling
- approval requirement if any
- onward-share ceiling
- whether this issuance preserves current artifact epoch or creates a successor artifact

### 3) Recipient binding card

Show how tightly issuance is bound:

- unbound / bearer-style
- expected claimant identity
- reviewed recipient fingerprint or identity
- lane-restricted recipient set
- one-time claim only

If recipient binding is weak, the page must say so bluntly.

### 4) Expiry and use-budget card

Show:

- no expiry / fixed expiry / claim-once / use-limited / freshness-limited
- use budget remaining at issuance
- whether the budget is global or recipient-bound
- what happens after expiry or budget exhaustion

### 5) Continuity and fork-warning card

This card is mandatory whenever issuance replaces or rotates another live artifact.
Show:

- whether old artifacts remain valid
- whether old cohorts continue syncing together
- whether this is a narrowing, widening, or successor epoch
- retirement order required to avoid accidental parallel continuity
- strongest safe sentence and stronger forbidden sentence

### 6) Safe export options

Offer export carriers, but preserve semantics:

- copy text
- QR display
- local handoff
- reviewed send path
- hold without export

The page must make clear that changing carrier does not change authority semantics.

### 7) Pending receipt summary

Preview the issuance receipt fields that will be frozen on commit.

## Rules

### Rule 1 — issuance must preview the artifact, not just the carrier

`Copy link` is not a sufficient pre-commit explanation.

### Rule 2 — rotation must preview fork risk

If old and new artifacts can coexist, the page must warn that continuity may fork.

### Rule 3 — recipient binding truth must be explicit

A bearer-style artifact must not sound recipient-bound just because the operator intends one recipient.

### Rule 4 — expiry must be semantically visible

Expiry and click/use budgets belong to authority review, not hidden advanced options.

## Acceptance criteria

A later operator can:

- reconstruct what artifact was issued and why
- see how tightly the recipient was bound
- see expiry and use budget clearly
- understand whether this issuance risks parallel epochs
- tell which export carriers were available without confusing carrier for meaning