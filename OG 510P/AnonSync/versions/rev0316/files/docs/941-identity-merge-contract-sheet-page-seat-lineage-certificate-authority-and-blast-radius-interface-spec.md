# Identity merge contract sheet page: seat lineage, certificate authority, and blast radius interface spec

## Purpose

Before an operator links two seats, replaces a certificate lineage, or tries to detach a dormant member, they need one ordinary page that answers:

> what kind of seat-adoption operation is this, which lineage wins, what subject set moves with it, what can be lost locally, and what is the strongest honest sentence the product can still say?

## Core decision

Every serious seat-link operation must open one first-class **Identity merge contract sheet**.

The sheet owns:

- source seat lineage
- target seat lineage
- adoption direction
- certificate fate
- inherited subject set
- evicted subject set
- detach / residue boundary
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. identity claim header
2. seat lineage card
3. subject blast-radius card
4. detach / residue boundary card
5. claim ceiling and next-safe action rail

### 1) Identity claim header

Show at minimum:

- source seat name / fingerprint
- target seat name / fingerprint
- overall verdict (`fresh-link`, `adoption`, `certificate-takeover`, `version-mix-risk`, `detach-local-only`, `hidden-latent-member`, `unknown`)
- strongest safe sentence
- stronger rejected sentence
- evidence freshness

### 2) Seat lineage card

Render rows for at least these truths:

- source certificate lineage
- target certificate lineage
- winning lineage after apply
- whether the target becomes a derivative of the source or vice versa
- whether seat names/fingerprints change
- whether version compatibility blocks or narrows the action

### 3) Subject blast-radius card

Render rows for at least these subject classes:

- subjects inherited onto the adopting seat
- subjects evicted from the adopting seat's control surface
- subjects left on disk only
- platform-specific stronger filesystem risk
- subjects untouched by the operation

### 4) Detach / residue boundary card

Show:

- whether the action is local-only or remote-capable
- whether hidden seats remain latent members
- whether a dormant seat can reappear later
- whether later unlink/revoke/forget actions are still needed

### 5) Claim ceiling and next-safe action rail

Only show actions that preserve meaning, such as:

- `Open identity adoption review`
- `Open certificate takeover impact`
- `Open unlink and hidden-device boundary`
- `Emit identity merge receipt`

## Rules

### Rule 1 — linking must never read like generic pairing

The operator must never have to infer certificate or subject consequences from a QR or key affordance.

### Rule 2 — seat lineage and subject fate remain distinct

Adopting an identity is not the same thing as safely adopting every subject.

### Rule 3 — local-only detach must stay explicit

The page must say when other seats remain untouched.
