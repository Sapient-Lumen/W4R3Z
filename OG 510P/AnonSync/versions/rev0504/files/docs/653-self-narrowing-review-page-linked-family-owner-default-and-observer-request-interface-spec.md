# Self-narrowing review page — linked-family owner default and observer request interface spec

## Purpose

This page answers one ordinary question before commit:

> I want one of my own seats to be narrower than the rest of my personal constellation, so what is the least-distorting way to do that and what truth will the product be allowed to claim afterward?

The page exists because `make this device read only` is not a harmless toggle when owner-default, artifact family, bind path, and subject continuity can all change.

## Core decision

Whenever an operator asks to narrow one of their own seats beneath the linked-family default, the product must render one first-class **Self-narrowing review** page.

The page owns:

- requested target role
- current family basis
- native versus detour implementation options
- continuity and path consequences
- claim ceiling before commit

## Fixed page order

1. request strip
2. current family basis card
3. implementation options compare
4. continuity and bind consequences
5. commit review
6. receipt preview

### 1) Request strip

Show:

- subject
- source seat if relevant
- target seat
- requested narrower role: `observer`, `receive-only`, `opaque-custody`, `names-only`, `unknown`
- one honest next action

### 2) Current family basis card

This card publishes:

- whether the target seat is currently powerful because it is linked under the same identity
- current role on the target seat
- whether auto-approval or shared visibility also rides on that linked-family basis
- what exactly must change to make the seat narrower

### 3) Implementation options compare

Render one row for each available approach:

- native same-subject seat-role narrowing
- native derived observer seat
- separate detour artifact / alternate subject family
- bounded opaque replica
- blocked / unavailable

Columns:

- `same subject lineage?`
- `same path continuity?`
- `manual bind required?`
- `approval/share powers afterward`
- `future repair burden`
- `strongest safe sentence`

The safest same-subject option must sort first.

### 4) Continuity and bind consequences

This card publishes:

- whether bytes remain in one subject or become a detour copy
- whether a different key, artifact family, or subject class is required
- whether disconnect/manual connect/manual path selection will happen
- whether non-empty-target review is still required
- what later operators must not assume

### 5) Commit review

This section must state:

- requested role
- option chosen
- actual role that will exist afterward
- strongest safe sentence afterward
- stronger unsupported sentence afterward

### 6) Receipt preview

The receipt must preserve:

- requested narrower role
- chosen implementation
- continuity class
- bind/path consequence
- claim ceiling

## Public object

### `self_narrowing_review`

Fields:

- `self_narrowing_review_id`
- `subject_ref`
- `target_seat_ref`
- `requested_role`
- `current_role`
- `family_basis`
- `implementation_options[]`
- `chosen_option`
- `continuity_consequences[]`
- `claim_ceiling`
- `generated_at`

## Review rules

### Rule 1 — `share another key` is not a role sentence

If a workaround needs a different artifact family, that is an implementation detail, not the operator's requested role.
The page must keep the requested role visible.

### Rule 2 — same-subject option must outrank detour convenience

If a native same-subject narrower seat exists, it must appear ahead of any workaround that changes lineage or artifact family.

### Rule 3 — detour artifacts must publish lineage cost

If the chosen option produces a workaround copy rather than a native narrowed seat, the page must say so before commit.

## Honest outputs

The page may conclude:

- `Native same-subject observer posture is available. This keeps subject lineage intact and removes onward-share authority on the target seat.`
- `Requested observer posture cannot be expressed natively in the interoperating system. Available fallback uses a detour artifact and separate manual bind.`
- `Strongest safe sentence after commit: this target seat is intentionally narrower for this material purpose. Stronger unsupported sentence: this target seat remains an Owner inside the same role system.`

It may not flatten those outcomes into `linked`, `read only`, or `standard/advanced` jargon alone.
