# Linked family page: future subject scope, default arrival, and owner-domain boundary interface spec

## Purpose

The archive already had strong constellation, linking, and per-seat exception doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> what does this linked-seat family actually mean for future arrivals, default modes, and owner-domain breadth?

## Core decision

Every product that supports `my seats are related` must own one first-class **Linked family** page.
That page is the semantic home of:

- linked-family membership
- future-subject scope
- default arrival policy
- owner-domain breadth
- per-seat exception boundaries
- recent family-change receipts

The product must not let `linked` or `My devices` act as a magical umbrella without this page.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. family snapshot strip
2. scope-of-relationship card
3. future-arrival card
4. default-arrival-mode card
5. owner-domain card
6. seat-exception card
7. recent family receipts
8. expert details drawer

### 1) Family snapshot strip

Show:

- linked-family name or label
- seats currently in the family
- whether the family is healthy, partial, or drifting
- strongest next-safe action

The strip should answer `what family am I looking at right now?`

### 2) Scope-of-relationship card

Show one explicit scope verdict:

- `relationship affects future subjects in this namespace`
- `relationship affects only reviewed selected subjects`
- `relationship is suspended for future arrivals`
- `relationship is being narrowed per seat`

Also show:

- whether the family is broad by design or intentionally narrow
- whether this page is describing current behavior or a proposed change

This card should answer `does this family relationship reach beyond the current subject?`

### 3) Future-arrival card

Show:

- whether newly created or newly shared subjects will appear automatically on descendant seats
- which subset of subjects are in scope
- whether arrival is immediate, review-gated, or announcement-only
- whether removal from the family stops only future arrivals or also current subjects

This card should answer `what will appear later because this relationship exists?`

### 4) Default-arrival-mode card

Show:

- default mode for arriving subjects (`disconnected`, `announce-only`, `placeholder`, `full`, etc.)
- whether the mode is family-wide, seat-specific, or subject-specific
- whether later local overrides are allowed
- whether choosing a broad relationship silently widens storage or write posture

This card should answer `how will future arrivals land by default?`

### 5) Owner-domain card

Show:

- whether descendant seats act as owners, broad writers, or narrower managed seats
- whether onward-share is inherited broadly, narrowed, or disallowed
- whether the family shares one owner domain or only one trust relationship
- whether rights mutation from one seat affects siblings automatically or only by reviewed policy

This card should answer `how merged or separate is authority inside this linked family?`

### 6) Seat-exception card

Show:

- any seats with narrower write, narrower arrival, or narrower onward-share posture
- whether those exceptions are true in-place exceptions or breakout subjects
- whether the current design can honestly support that narrowing without class escape

This card should answer `where does the family stop being uniform?`

### 7) Recent family receipts

Show recent receipts with:

- seat added or removed
- future-scope verdict at the time
- default-arrival mode at the time
- owner-domain breadth at the time
- exceptions created or removed

### 8) Expert details drawer

Hide lineage identifiers, certificate details, seat-state drift diagnostics, and low-level reconciliation traces behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. family phrase
2. future-scope phrase
3. default-arrival phrase
4. owner-domain phrase
5. strongest next action

Example:

```text
Household laptops family   future subjects in Personal mesh arrive automatically   default arrival: placeholder on portable seats, full on archive seat   owner-domain breadth: broad write across family, onward-share separately policy-bounded   Inspect exceptions
```

## Acceptance criteria

This spec is satisfied when:

- linked relationship and per-subject grant are visibly different answers
- future scope is shown separately from current-subject rights
- broad owner-domain and narrow managed-family designs are visibly different answers
- exceptions are shown as true in-place exceptions or breakout subjects rather than hidden rituals
- the product emits receipts for meaningful family-scope changes rather than outsourcing memory to later surprise arrivals
