# Identity-wide removal and remote remainder review page: linked-set scope, non-linked survivors, and delete authority interface spec

## Purpose

This review appears when the chosen removal family reaches beyond the current seat.
It exists to answer one ordinary question before commit:

> who exactly loses this subject, who can still retain it, and am I removing registration, deleting bytes, or both?

## When this review must appear

Trigger it for actions such as:

- remove subject from linked devices under this identity
- remove disconnected subject from all linked seats
- delete placeholder or file for all reachable peers
- attempt runtime uninstall while expecting shared cleanup everywhere

## Fixed page order

1. scope summary header
2. affected-audience matrix
3. non-linked survivor boundary
4. authority and delete-ceiling section
5. approval footer

### 1) Scope summary header

Show:

- target subject
- requested verb family
- seat scope (`this-seat-only`, `linked-identity-set`, `reachable-share-peers`, `runtime-local`, `unknown`)
- strongest safe sentence after apply
- stronger rejected sentence after apply

### 2) Affected-audience matrix

Columns:

- audience class
- registration after apply
- byte/material effect after apply
- can continuity survive?
- evidence freshness

Rows should include at least:

- current seat
- linked seats under same identity
- other approved peers outside that identity
- read-only peers
- encrypted / derivative custody peers if present

### 3) Non-linked survivor boundary

Provide explicit sentences such as:

- `This removes the subject from linked seats under this identity only.`
- `Other remote peers outside this identity may still retain the subject.`
- `Global sounding language would be false here.`

### 4) Authority and delete-ceiling section

Show:

- whether the action removes registration only, shared continuity only, or actual material
- whether delete authority depends on placeholder semantics or write permission
- whether a power-user or platform exception hides or narrows the available destructive path
- whether Linux WebUI or another projection ignores a safety preference that exists elsewhere

### 5) Approval footer

Require acknowledgement whenever the action creates a state such as:

- linked seats cleaned up while external peers survive
- placeholder deletion propagates actual data deletion
- runtime removal was mistaken for subject deletion
- safety preference is unavailable or ignored on this projection

## Rules

### Rule 1 — identity scope and share scope remain separate truths

Removing from linked seats is not the same thing as deleting from all reachable peers.

### Rule 2 — remote remainder stays visible in global-sounding flows

The product must say when other peers can still keep the subject.

### Rule 3 — authority ceiling must survive the happy-path wording

`Removed everywhere` is disallowed unless the product can actually prove the audience and byte effect.
