# License owner transfer review page — direct apply, linked owner, and seat survivor

## Purpose

This page exists for the mutation that many products would dangerously flatten into `Apply key`.
The real question is:

> if this key application can move owner status from one identity to another, what exactly survives, what becomes borrowed, and what new blast radius am I accepting?

## Core decision

Any action that can change license-owner identity must open a dedicated **License owner transfer review** page before commit.

## Fixed page order

1. mutation summary
2. current owner vs target owner card
3. affected borrowers card
4. linked-family fallout card
5. survivor map
6. commit barrier

### 1) Mutation summary

Show:

- current owner identity
- proposed target owner identity
- whether this is direct apply, re-apply, migration, or recovery
- strongest safe summary

### 2) Current owner vs target owner card

Publish:

- current owner privileges
- target owner privileges after commit
- what owner-specific controls move
- what owner-specific receipts remain historical only

### 3) Affected borrowers card

For each dependent seat or borrower show:

- current basis
- post-transfer basis
- whether the seat keeps capability, loses capability, or becomes unknown until reapproval
- whether the seat remains attached to the same governance graph

### 4) Linked-family fallout card

Show:

- which linked devices inherit from the owner today
- whether any linked devices are on a conflicting line family
- whether this mutation would create mixed-version or mixed-line hazards
- whether UI/share configuration continuity is at risk

### 5) Survivor map

Separate:

- bytes already on disk
- live capability
- share configuration visibility
- owner controls
- borrower seats
- audit / receipt continuity

### 6) Commit barrier

Require one explicit statement:

- `Transfer owner now`
- `Do not transfer; open safer recovery`
- `Stop and split cohort first`

## Rules

### Rule 1 — owner transfer is never silent

Any direct key apply that can move owner status must preview that movement.

### Rule 2 — survivor classes stay split

Byte survival, UI/config survival, and entitlement survival may not collapse into one sentence.

### Rule 3 — mixed-version linked cohorts are loud blockers

If the transfer would deepen a known v2/v3 linked-cohort conflict, the page must block generic safe language.

## Acceptance criteria

A later operator can:

- tell who owned the entitlement graph before and after
- see which borrowers were affected
- separate disk-byte survival from governance survival
- reopen the exact receipt proving why transfer was or was not allowed