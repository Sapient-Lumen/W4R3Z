# Entitlement topology contract sheet page — owner, user, linked identity, and line compatibility

## Purpose

This page answers the ordinary operator question:

> what exact entitlement graph is this seat living inside right now, who owns it, who is merely borrowing from it, and which product line family is it allowed to inhabit safely?

It exists because `licensed`, `trial`, `borrowed seat`, `linked owner`, and `v3-ready` are not interchangeable truths.

## Core decision

Every seat whose capability posture depends on owner identity, borrowed seats, linked identity grouping, or product-line family must render one first-class **Entitlement topology contract sheet** before serious license, link, upgrade, or reclaim actions.

## Fixed page order

1. topology strip
2. owner graph card
3. seat budget and collapse card
4. line family card
5. dependency and revocation card
6. strongest blocked sentence

### 1) Topology strip

Show:

- current seat
- topology verdict
- current owner class
- line family
- strongest next-safe action

### 2) Owner graph card

Publish:

- direct owner identity if any
- whether this seat is owner, linked-under-owner, borrowed-seat user, family-personal self-use, non-commercial self-activation, or unknown
- whether authority is direct or inherited
- whether approval from another identity is part of the basis

### 3) Seat budget and collapse card

Show:

- counted unit basis (`per seat`, `per identity`, `per linked family`, `not this lane`)
- current seat budget effect
- whether linked devices collapse into one counted identity or not
- whether this seat can lend onward or only consume

### 4) Line family card

Show:

- current product line / version family
- allowed migration family
- blocked migration families
- whether byte compatibility is stronger than entitlement compatibility
- whether mixed-version linked cohorts are supported, discouraged, or blocked

### 5) Dependency and revocation card

Show:

- what could revoke this seat next
- whether owner expiry propagates here
- whether direct key apply elsewhere could transfer ownership
- whether this seat survives owner-license removal, and at what ceiling
- whether capability presence here is independent or borrowed

### 6) Strongest blocked sentence

Examples:

- `This seat is licensed.`
- `This seat currently borrows one seat from owner identity atlas-admin.`
- `This seat can sync bytes with v3 peers but must not join a mixed-version linked cohort.`
- `This identity may not be upgraded to v3 without abandoning current Business entitlement topology.`

## Public object

### Entitlement topology contract sheet

Fields:

- `entitlement_topology_sheet_id`
- `seat_ref`
- `topology_verdict`
- `owner_identity_ref`
- `seat_class`
- `counting_basis`
- `line_family`
- `migration_verdict`
- `dependency_edges[]`
- `blocked_stronger_sentence`
- `generated_at`

## Rules

### Rule 1 — `licensed` is not enough

The page must publish direct vs inherited vs borrowed basis.

### Rule 2 — byte compatibility and entitlement compatibility stay separate

The page may never imply that protocol compatibility makes linked-cohort migration safe.

### Rule 3 — counting basis must stay visible

A seat budget based on unique identities must not be described as a per-device budget.

### Rule 4 — borrowed seats publish dependency edges

A borrowed seat may not pretend to be self-owned when owner expiry or reclaim still governs it.

## Acceptance criteria

A later operator can:

- name the current owner topology
- tell whether this seat is independent or borrowed
- tell what counting unit is actually consumed
- tell whether current line family is upgrade-safe
- reopen the right transfer / reclaim / migration page without licensing folklore