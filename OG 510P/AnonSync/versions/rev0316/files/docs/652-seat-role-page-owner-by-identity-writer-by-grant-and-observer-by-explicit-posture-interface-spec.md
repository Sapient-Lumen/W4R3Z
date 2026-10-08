# Seat role page — owner by identity, writer by grant, and observer by explicit posture interface spec

## Purpose

This page answers one ordinary question:

> what role does this seat actually have for this subject right now, and is that because of linked identity, explicit grant, derived ceiling, or a deliberate self-narrowing choice?

The page exists because `owner`, `writer`, `read only`, and `my device` are not interchangeable.
The operator needs one direct statement of seat role and role basis.

## Core decision

Every subject-seat pair must render one first-class **Seat role** page.
The page owns:

- current seat role
- role basis
- authority and onward-share powers
- whether narrower self-posture was requested or adopted
- strongest safe sentence for this seat

## Primary layout

The page always renders the same regions in the same order:

1. role strip
2. role-basis card
3. capability lattice
4. self-narrowing card
5. contradiction and detour card
6. receipts

### 1) Role strip

Show:

- subject label
- seat label
- current role: `owner`, `writer`, `observer`, `opaque-custody`, `derived-narrow`, `unknown`
- role basis: `linked-identity`, `explicit-grant`, `derived-ceiling`, `native-self-narrowing`, `detour-artifact`, `unknown`
- one honest next action

### 2) Role-basis card

This card publishes:

- whether the seat is powerful because it belongs to the same linked family
- whether the seat received an explicit remote grant
- whether the seat is narrower because of a derived or custody ceiling
- whether the current role came from one native role change or from a workaround artifact family

The operator must be able to answer: **why does this seat have this role at all?**

### 3) Capability lattice

Render rows for these capability families:

- read current bytes
- publish upstream edits
- approve or invite peers
- widen rights for others
- receive future arrivals automatically
- hold only constrained/opaque custody

Columns:

- `current yes/no`
- `basis`
- `native change available?`
- `least-strong narrower alternative`
- `receipt language`

The product must not compress these rows into one generic badge.

### 4) Self-narrowing card

This card publishes:

- whether the operator requested a narrower role for this seat
- whether the current system supports that natively
- whether the narrowing is same-subject or detour-derived
- what continuity, path, or artifact changes were required
- whether stronger convenience still remains unavailable

The operator must be able to answer: **is this seat truly a narrower role in the same subject, or only a workaround copy?**

### 5) Contradiction and detour card

This card must surface any tension such as:

- linked family says `owner` while the operator wanted `observer`
- native self-narrowing unavailable, so detour artifact used
- subject class changed to express a seat-role request
- manual bind / separate key / separate lineage now affects truth

This section must publish the strongest safe sentence and the stronger unsupported sentence.

### 6) Receipts

Receipts must preserve:

- current role
- role basis
- whether self-narrowing was requested
- whether native or detour route won
- claim ceiling

## Public object

### `seat_role_snapshot`

Fields:

- `seat_role_snapshot_id`
- `subject_ref`
- `seat_ref`
- `current_role`
- `role_basis`
- `capability_rows[]`
- `self_narrowing_status`
- `detour_or_contradiction_rows[]`
- `claim_ceiling`
- `generated_at`

## Non-negotiable rules

### Rule 1 — linked identity must not silently erase seat-role explanation

If the seat is powerful because of linked-family membership, the page must say so directly.
`Owner` alone is not enough.

### Rule 2 — requested narrower posture must remain visible even when unavailable

If the operator asked for `observer`, `receive-only`, or another narrow role and the product compiled that through a workaround, the requested role must stay visible.

### Rule 3 — subject-class substitution must be named as substitution

If the current posture exists only because a different artifact family or subject class was created, the page must publish that explicitly.

## Honest outputs

The page may conclude:

- `This seat is Owner because it participates through the linked identity family, not because a separate explicit Owner grant was issued.`
- `Requested narrower role: observer. Native self-narrowing unavailable in the interoperating system, so a detour artifact currently carries the receive-only posture.`
- `Strongest safe sentence: this seat is intentionally narrower for the same material purpose. Stronger unsupported sentence: this is a native same-subject observer role.`

It may not flatten those outcomes into `my device`, `owner`, or `read only`.
