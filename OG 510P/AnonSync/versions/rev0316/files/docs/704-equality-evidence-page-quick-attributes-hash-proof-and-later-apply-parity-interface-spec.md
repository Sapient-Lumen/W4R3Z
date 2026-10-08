# Equality evidence page: quick attributes, hash proof, and later-apply parity interface spec

## Purpose

This page exists because equality claims come from different evidence classes and those classes are not interchangeable.

The page must answer:

> did the product infer quietness from quick attributes, prove content equality by hash, prove optional planes natively, or only preserve them for later compatible application?

## Core decision

Every serious sync product must own one first-class **Equality evidence** page.
That page publishes the evidence ladder behind every non-trivial sameness claim.

## Fixed page order

1. evidence strip
2. quick-attribute evidence
3. content-proof evidence
4. optional-plane evidence
5. later-apply evidence
6. residual uncertainty and receipts

### 1) Evidence strip

Show:

- compared subject/candidate scope
- current strongest evidence class
- claim ceiling
- whether the record is live, replayed, or incomplete

### 2) Quick-attribute evidence

Show:

- which fast attributes were checked
- whether they matched
- whether any were removed from the equation by policy
- whether this class alone can justify quietness or only provisional calm

### 3) Content-proof evidence

Show:

- whether hashing has begun, completed, or is still deferred
- proof class: `none`, `partial hash`, `full content hash`, `piece-map proven`, `unknown`
- whether interrupted transfer or lazy hashing still weakens the claim

### 4) Optional-plane evidence

Show separately for each optional plane:

- permissions
- xattrs / streams
- platform-local decorations
- any subject-specific plane

For each, show:

- `native parity proven`, `carried only`, `later apply only`, `disabled`, `not representable`, `unknown`

### 5) Later-apply evidence

Show:

- whether parity depends on later landing on a compatible substrate
- what plane will apply later
- what substrate or runtime condition is required
- whether the current seat can only act as carrier/courier

### 6) Residual uncertainty and receipts

Show:

- unresolved mismatches
- missing proofs
- receipt refs
- one next honest action

## Rules

### Rule 1 — quick-attribute quiet is not full equality

The page must explicitly distinguish provisional quiet from stronger proof.

### Rule 2 — optional planes must stay separate

Permission parity, xattr parity, and content proof may not be collapsed into one badge.

### Rule 3 — later-apply parity must be named as such

The page may not imply that preserved-for-later means applied-now.

## Success criteria

The page is successful only when a later operator can answer:

1. what evidence class the product actually reached
2. whether content equality was fully proven
3. which optional planes were proven, deferred, or disabled
4. whether this seat only preserves later parity
5. what uncertainty still remains
