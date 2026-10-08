# Subject architecture lineage receipt page: governance domain, authority lane, and blocked stronger sentences interface spec

## Purpose

Every architecture-affecting action needs one durable receipt.
The receipt answers:

> what governance family did we actually choose, what authority and re-share lane did that imply, what exception or migration path did we take, and what stronger sentence did we explicitly refuse to claim?

## Receipt payload

The receipt must preserve:

- subject identifier and display name
- chosen architecture family
- governance primitive (`key`, `certificate`, `encrypted derivative`, `unknown`)
- authority lane
- onward re-share lane
- linked-device compatibility class
- manual exception class if any
- migration verdict
- config / automation support verdict
- survivor map
- strongest safe sentence
- stronger rejected sentence
- evidence freshness

## Required sections

### 1) Architecture verdict block

Show:

- `Chosen family: …`
- `Governance primitive: …`
- `Why this family: …`

### 2) Authority and delegation block

Show:

- `May write shared truth: yes/no/limited/unknown`
- `May delegate onward: yes/no/owners-only/encrypted-only/unknown`
- `May mutate permissions later: yes/no/remove-and-readd/unknown`

### 3) Linked-lane / exception block

Show:

- whether linked auto-arrival was used
- default authority lane if linked
- whether a manual Standard RO exception was required
- whether an encrypted derivative branch was used instead of normal readable participation

### 4) Migration / ceiling block

Show:

- whether the action was in-place or remove-and-readd
- whether config/automation support exists
- whether any stronger upgrade / conversion promise was rejected

### 5) Blocked stronger sentence block

Examples:

- `Rejected: this can later be upgraded in place without subject replacement.`
- `Rejected: linked-device arrival can natively produce read-only Advanced behavior.`
- `Rejected: encrypted derivative is interchangeable with a readable writable participant.`

## Rules

### Rule 1 — the receipt must preserve architecture, not just permissions

`RO/RW/Owner` without family and governance primitive is not sufficient.

### Rule 2 — exception branches must survive the log

If the operator had to leave the linked lane or manual-connect an encrypted derivative, the receipt must say so.

### Rule 3 — stronger rejected claims are mandatory

Architecture mistakes often happen when the product implies later convertibility or equivalence that it cannot actually guarantee.
