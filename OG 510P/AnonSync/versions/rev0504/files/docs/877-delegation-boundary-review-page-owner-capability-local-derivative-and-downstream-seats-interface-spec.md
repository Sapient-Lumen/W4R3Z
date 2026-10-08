# Delegation boundary review page: owner capability, local derivative narrowing, and downstream seat limits interface spec

## Purpose

This page answers one ordinary question:

> who may grant onward authority from here, how far may that authority travel, and which seats are structurally prevented from widening the line?

The page exists because delegation is not the same thing as write access and because derivatives should never silently look owner-like.

## Core decision

Every place where onward sharing, downstream seat creation, or derivative-local expansion is possible must render a **Delegation boundary review** page.

## Fixed page order

1. delegation strip
2. issuer qualification card
3. downstream ceiling card
4. derivative narrowing card
5. prohibited widening card
6. receipt / challenge rail

### 1) Delegation strip

Show:

- issuing seat
- source subject
- current delegation grade
- requested downstream action
- strongest next-safe action

### 2) Issuer qualification card

Publish whether the current seat is:

- not allowed to delegate
- allowed to delegate within fixed limits
- owner-like for this subject only
- linked-own-seat rather than external issuer
- derivative and therefore narrowing-only

### 3) Downstream ceiling card

Show the highest authority the issuer may create downstream.
Examples:

- may create observer only
- may create writer but not admin
- may create sibling derivative only
- may create no downstream seats

### 4) Derivative narrowing card

If a downstream seat is derivative or local, publish:

- source ceiling
- derivative floor
- auto-lowering triggers
- source-removal consequence
- whether the derivative survives only as residue after source loss

### 5) Prohibited widening card

List stronger forbidden moves explicitly.
Examples:

- derivative cannot become owner-like
- non-admin writer cannot mint delegate-capable seats
- linked own seats cannot be confused with third-party grants

### 6) Receipt / challenge rail

Link to existing delegation receipt, challenge, revocation impact, or successor warning.

## Rules

### Rule 1 — write is not delegate

The review must separate mutation of subject bytes from authority to invite or widen.

### Rule 2 — derivatives can only narrow

A derivative-local seat must never appear to widen or equal the source unless that is actually true and explicitly published.

### Rule 3 — own-seat linkage is not third-party delegation

The grammar for `add my own seat` must remain distinct from the grammar for `grant another principal authority`.

## Acceptance criteria

A later operator can:

- tell whether the current seat may grant anything downstream
- tell the maximum downstream authority it may create
- tell why a derivative cannot widen beyond its source
- distinguish own-seat expansion from external delegation
