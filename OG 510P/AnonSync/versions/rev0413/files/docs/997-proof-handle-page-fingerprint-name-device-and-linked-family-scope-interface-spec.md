# Proof handle page — fingerprint, names, device labels, and linked-family scope

## Purpose

Present the operator with the exact proof bundle behind a requester or remembered approval without flattening it into a single label.

This page exists so the operator can inspect:

- what handle was actually reviewed
- what labels were merely informative
- whether the handle belongs to one seat or to a linked family scope
- whether reuse of trust is exact, weakened, or unavailable

## Required sections

### 1. Handle summary

Must show:

- canonical proof handle
- associated human label
- associated device label
- handle class (`seat`, `family`, `unknown`)
- source (`live request`, `stored memory`, `linked-family derivation`, `receipt replay`)

### 2. Evidence composition

List the components that make up the proof bundle:

- cryptographic handle / fingerprint
- lineage or family association
- stored trust-memory key
- any operator-authored alias

Each component must publish whether it is:

- authoritative
- corroborating only
- descriptive only
- stale or superseded

### 3. Reuse verdict

Possible verdicts:

- `exact match`
- `label match only`
- `proof mismatch`
- `family match but seat not exact`
- `insufficient for reuse`

### 4. Scope boundary

Must clearly state:

- what the handle proves about this requester
- what it does **not** prove about siblings / linked devices / renamed seats
- whether family-widening would require another review

### 5. Strongest safe sentence

Examples:

- `This stored proof bundle matches the requester exactly.`
- `This requester belongs to a reviewed family, but the seat-specific handle was not previously approved.`
- `Only the descriptive labels match; proof reuse is unavailable.`

### 6. Blocked stronger sentence

Examples:

- `A family match proves this exact device.`
- `Any matching label is sufficient to reuse approval.`

## Interaction rules

- export/copy actions must include scope boundary text
- alias editing must never mutate the canonical proof handle
- family and seat handles must never render as the same visual token

## Receipt obligations

Any receipt derived from this page must preserve:

- canonical proof handle
- handle class
- reuse verdict
- scope boundary
- blocked stronger sentence