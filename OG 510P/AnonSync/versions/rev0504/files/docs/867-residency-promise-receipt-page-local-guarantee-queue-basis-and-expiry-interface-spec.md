# Residency promise receipt page: local guarantee, queue basis, and expiry interface spec

## Purpose

This receipt exists because `I clicked keep local`, `I prioritized this`, and `it looked available` are not durable evidence.
Later operators need one object that says what the product actually promised at the moment of review.

## Core decision

Every residency-affecting review must emit a **residency promise receipt**.
The receipt must preserve:

- what promise class was approved
- whether inheritance changed
- what witness basis supported the promise
- what budget basis supported the promise
- when the promise or its review freshness expires
- what stronger claims remain forbidden

## Required receipt fields

### A. Promise identity

- receipt id
- subject / selection reference
- acting seat
- issued time
- reviewing surface

### B. Promise class

Exactly one:

- `preview-only`
- `queued-best-effort`
- `guaranteed-local-now`
- `guaranteed-local-for-future-descendants`
- `release-local`
- `blocked-no-source`
- `blocked-over-budget`

### C. Inheritance result

- prior policy source
- resulting policy source
- inheritance restored? (`yes`, `no`)
- future descendants affected? (`yes`, `no`, `conditional`)

### D. Source basis

- full-copy witness count at issuance
- witness fragility class
- route basis class
- ghost-risk class

### E. Budget basis

- guaranteed-local bytes approved
- elastic bytes implicated
- future-expansion class
- budget freshness timestamp

### F. Expiry / rereview

- promise freshness deadline
- rereview required on witness drift? (`yes` / `no`)
- rereview required on budget drift? (`yes` / `no`)
- nearest page to reopen

### G. Language guard

Store together:

- strongest safe sentence
- stronger forbidden sentence

## Example safe sentences

- `As of issuance, this subtree was approved as queued-best-effort only; no guaranteed-local claim was made.`
- `As of issuance, this subtree was approved as guaranteed local and future descendants beneath it were included.`
- `As of issuance, no strong local promise could be made because surviving full-copy witness proof was insufficient.`

## Anti-confusion rules

### Rule 1 — receipts preserve promise ceilings

A receipt may not let later operators confuse `queued-best-effort` with `guaranteed local`.

### Rule 2 — receipts preserve inheritance truth

If the operator restored inheritance, the receipt must say so.
If the operator froze a local override, the receipt must say so.

### Rule 3 — receipts preserve expiry

A stale receipt is still evidence of the old review, but it may not be reused as proof that the promise remains valid now.

### Rule 4 — receipts preserve block reasons

If admission was blocked by no-source or over-budget conditions, the receipt must keep that block visible instead of disappearing into history.

## Compact row contract

A compact receipt row should preserve:

1. subject phrase
2. promise class
3. inheritance result
4. witness fragility
5. expiry
6. strongest safe sentence fragment

Example:

```text
mockups subtree · guaranteed-local-for-future-descendants · inheritance restored · 3 healthy witnesses · rereview after budget drift or 24h · safe to say this subtree was guaranteed local at issuance
```

## Acceptance criteria

A later operator can:

- reconstruct the exact promise that was and was not made
- tell whether inheritance was restored or frozen
- tell whether source or budget freshness limits later reuse
- reopen the right review surface without relying on browser or memory folklore
