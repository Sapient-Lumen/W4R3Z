# LAN-scope review page: observer delta, helper cutoff, and proof floor interface spec

## Purpose

When an operator asks for a true `LAN-only` posture, the product must review more than toggle state.
It must review proof.
This page exists to answer:

> after this change, what internet-capable helpers are cut off, what residue still survives, and what minimum proof is required before the product may say `LAN-only`?

## Core decision

Every attempt to narrow a subject, seat, or cohort to `LAN-only` must compile into one first-class **LAN-scope review**.

The review owns:

- requested local-only scope
- helper cutoff set
- observer delta
- public-route residue
- proof floor
- apply verdict

## Fixed page order

1. requested local-only claim
2. helper cutoff review
3. observer delta map
4. proof floor card
5. apply verdict

### 1) Requested local-only claim

Show:

- target scope
- requested sentence (`LAN-only`, `same-subnet only`, `bound-interface only`, `offline except predefined peers`, `other`)
- strongest safe pre-apply sentence
- stronger rejected sentence

### 2) Helper cutoff review

Render one row per internet-capable or widening helper with columns:

- helper family
- state before
- state after
- cutoff confidence (`proven`, `requested`, `residue remains`, `unknown`)
- proof gap if any

Minimum rows:

- tracker discovery
- relay transfer
- proxy-assisted outside-LAN egress
- UPnP / public listener widening
- predefined hosts with public addresses
- remembered public peer addresses / caches

### 3) Observer delta map

This section names who can still plausibly observe or reach the subject after apply.
Show:

- same LAN observers
- configured predefined peers
- previously known public peers
- relay/tracker operator dependence
- broader internet observer delta (`reduced`, `unchanged`, `uncertain`)

### 4) Proof floor card

This card is mandatory.
Show:

- minimum evidence required for strong `LAN-only` language
- missing evidence right now
- whether restart, cache clearance, or fresh route witness is still required
- strongest safe sentence until that proof exists

### 5) Apply verdict

Possible outcomes:

- `apply LAN-only contract`
- `apply narrowed helper budget only`
- `clear residue before strong local-only claim`
- `switch to explicit wider route policy`
- `cancel; proof floor too weak`

## Rules

### Rule 1 — `LAN-only` is a claim family, not a switch label

The review must distinguish requested local-only posture from proven local-only posture.

### Rule 2 — residue is ordinary, not exceptional

Prior public-address memory or lingering helper dependence must render weaker language instead of being hidden in diagnostics.

### Rule 3 — observer delta is first-class

The product must show who stops being able to discover or reach the subject, not only which checkbox changed.

## Acceptance criteria

A later operator can:

- tell whether the local-only claim is proven or still provisional
- tell which helpers were actually cut off
- tell whether cache or remembered route residue still weakens the claim
- tell what evidence is still missing
- tell why the final verdict was apply, narrow-only, or cancel
