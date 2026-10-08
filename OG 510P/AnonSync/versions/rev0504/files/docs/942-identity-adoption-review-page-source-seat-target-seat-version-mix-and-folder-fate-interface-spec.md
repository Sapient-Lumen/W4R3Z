# Identity adoption review page: source seat, target seat, version mix, and folder fate interface spec

## Purpose

This review appears whenever an operator proposes a seat-link action that imports identity from one seat into another.
It exists to answer one ordinary question before commit:

> which seat is adopting which lineage, what incompatibilities or risks exist, and what subject/folder consequences follow from that direction?

## When this review must appear

Trigger this review for changes such as:

- scan or paste seat-link artifact
- replace this seat with another seat's identity lineage
- join two already-configured seats
- adopt into a seat that already has local subject history
- attempt version-mixed identity linking

## Fixed page order

1. change summary header
2. direction and lineage matrix
3. compatibility and risk examples
4. subject/folder fate forecast
5. approval footer

### 1) Change summary header

Show:

- source seat
- target/adopting seat
- current lineage on each side
- proposed winning lineage
- strongest safe sentence after apply
- stronger rejected sentence after apply

### 2) Direction and lineage matrix

Columns:

- seat
- current certificate lineage
- post-apply certificate lineage
- identity name/fingerprint effect
- subject set inherited
- subject set displaced

### 3) Compatibility and risk examples

Provide concrete examples in plain language:

- `This action would place the laptop under the desktop's identity lineage.`
- `This is a version-mixed adoption and is blocked by default.`
- `The adopting seat already has local-only history that will become detached residue.`

### 4) Subject/folder fate forecast

Show:

- subjects that become visible under the new seat lineage
- subjects removed from ordinary control surfaces
- subjects left on disk only
- any stronger platform-specific deletion risk
- whether recovery requires later manual re-add, reconnect, or export

### 5) Approval footer

Require acknowledgement whenever the change creates a non-obvious state such as:

- certificate takeover
- local subject eviction
- version-mix escalation
- adopting seat becomes derivative of another seat

## Rules

### Rule 1 — direction is the first fact, not a footnote

`Link these seats` is too vague by itself.

### Rule 2 — version-mix risk must appear before commit

The operator should not learn about broken control-plane expectations afterward.

### Rule 3 — folder fate must preview separately from identity fate

A clean identity sentence can still hide ugly subject consequences.
