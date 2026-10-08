# Artifact rotation / fork warning page: old cohort survival, successor issuance, and retirement order interface spec

## Purpose

This page exists because rotating a live invite, key, or linked-seat artifact can create multiple concurrently valid continuity islands.
That is not a cosmetic warning.
It is a governance event.

The operator question is:

> if I rotate this artifact, who keeps talking on the old epoch, what new epoch am I creating, and what retirement order avoids accidental split continuity?

## Core decision

Every live artifact rotation must render one first-class **Artifact rotation / fork warning** page.

## Fixed page order

1. rotation strip
2. old-epoch map
3. successor artifact card
4. fork-risk card
5. retirement-order plan
6. continuity receipt summary

### 1) Rotation strip

Show:

- current artifact family
- target successor family
- subject or seat family affected
- strongest next-safe action

### 2) Old-epoch map

Publish:

- known members of the old cohort
- who can still communicate on the old artifact
- whether old access survives until explicit retirement
- evidence freshness of this map

### 3) Successor artifact card

Show:

- new artifact family
- new ceiling
- new approval / binding / expiry choices
- whether the successor is narrower, wider, or same ceiling but new epoch

### 4) Fork-risk card

Show one verdict:

- `no fork risk; old artifact already dead`
- `limited fork risk; successor created but old cohort empty`
- `live parallel continuity likely`
- `high fork risk; old cohort active and retirement incomplete`

Also show strongest safe sentence and stronger forbidden sentence.

### 5) Retirement-order plan

Show the safest order among:

- issue successor first
- notify cohort
- wait for acknowledgements
- retire old artifact
- reread roster and confirm old-epoch silence

If safe retirement is impossible, say so.

### 6) Continuity receipt summary

Preview what the rotation receipt will preserve:

- old epoch reference
- successor epoch reference
- fork-risk verdict
- retirement order chosen
- unresolved survivors

## Rules

### Rule 1 — rotation is not framed as mere refresh

If old peers can continue on the old artifact, the page must name this as epoch split risk.

### Rule 2 — survivor maps must be freshness-bound

Retirement claims must preserve how fresh the survivor evidence was.

### Rule 3 — successor issuance and old retirement stay on one page

Operators must not be forced to open separate pages to understand the fork.

### Rule 4 — no false clean-cut language

The page may not say `rotated` as if all peers automatically moved.

## Acceptance criteria

A later operator can:

- tell whether old cohorts survive
- see what successor artifact was created
- understand the risk of parallel continuity
- follow a safe retirement order
- preserve honest continuity language in the final receipt