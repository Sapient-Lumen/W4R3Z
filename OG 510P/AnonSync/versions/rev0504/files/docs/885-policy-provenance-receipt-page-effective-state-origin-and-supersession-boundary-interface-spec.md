# Policy provenance receipt page: effective state, origin lineage, and supersession boundary interface spec

## Purpose

This receipt answers one ordinary question:

> after a policy change, reset, or drift review, what value is in force now, which plane owns it, and what older assumption did this receipt supersede?

The receipt exists because later operators should not have to reconstruct policy origin from memory.

## Core decision

Every serious policy mutation, inheritance rejoin, or drift classification emits a first-class **Policy provenance receipt**.

## Receipt body

The receipt must preserve at minimum:

- subject or cohort scope
- field family changed or reviewed
- resulting effective value
- winning source plane
- losing competing plane if relevant
- blast radius
- exception status after action
- future-arrivals effect if any
- superseded receipt or assumption
- reopen triggers

## Receipt sections

### 1) Result sentence

One durable sentence such as:

- `This subject now inherits residency policy from cohort default.`
- `This share now carries a reviewed local override for relay posture.`
- `This cohort default changed, but listed exceptions remain pinned.`
- `This subject is config-owned; UI-local edits do not own its truth.`

### 2) Provenance block

Show:

- winning plane
- previous plane
- precedence reason
- whether the outcome was mutation, rejoin, classification, or lock acknowledgment

### 3) Scope block

Show:

- touched current subjects
- untouched exceptions
- future subjects affected or unaffected

### 4) Supersession block

Publish what older assumption is no longer safe to reuse.
Examples:

- `previous local override receipt superseded`
- `cohort-default assumption invalidated for listed exceptions`
- `config-plane lock replaced earlier UI-owned assumption`

### 5) Reopen block

Publish triggers such as:

- parent default changes again
- config plane changes
- subject leaves cohort
- exception ages out
- drift appears elsewhere in the cohort

## Rules

### Rule 1 — receipts preserve origin, not just value

`Relay disabled` or `Selective Sync on` is insufficient.
The receipt must say who now owns that truth.

### Rule 2 — supersession must be explicit

A newer provenance receipt must name the older receipt or assumption it weakened or replaced.

### Rule 3 — future-only effects stay distinct from current-subject effects

The receipt must separate `what changed here now` from `what later arrivals will inherit`.

## Acceptance criteria

A later operator can:

- tell the current effective value
- tell which plane owns it
- tell what older policy belief is no longer safe
- know exactly when to reopen the policy question
