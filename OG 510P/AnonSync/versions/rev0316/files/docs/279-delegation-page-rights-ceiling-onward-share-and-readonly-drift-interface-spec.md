# Delegation page: rights ceiling, onward-share truth, and read-only drift interface spec

## Purpose

`170` established topology-aware rights editing.
This document makes it concrete as one ordinary page.

The page exists to answer one ordinary operator question:

> what right does this member really have here, what stronger right could they honestly receive, what onward power comes with it, and what happened if their local copy drifted anyway?

## Core decision

Every share/member relationship that supports non-trivial rights must render one first-class **Delegation** page.
That page is the semantic home of:

- current effective right
- admissible rights ceiling and the reason for it
- onward share / revoke / mutation powers
- read-only or narrowed-seat divergence truth
- rights-mutation receipts

The page must not let a disabled dropdown entry stand in for the explanation.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. member and relationship strip
2. effective-right card
3. rights-ceiling card
4. onward-power card
5. local-drift / read-only behavior card
6. mutation review and receipts
7. blocked actions drawer

### 1) Member and relationship strip

The strip shows:

- member name / seat or family
- subject name
- relationship class
- current effective right
- next-honest-action button

Allowed relationship classes include:

- `linked own seat`
- `reviewed external member`
- `local child lineage member`
- `historical / retired member`

### 2) Effective-right card

Show:

- current right (`read only`, `read & write`, `delegate / owner-like`, or narrower product terms)
- source of that right
- whether it is inherited, pinned, or temporarily narrowed
- current mutation ability
- current revoke ability

This card answers `what can they actually do right now?`

### 3) Rights-ceiling card

Show:

- strongest admissible right for this member here
- exact reason for the ceiling
- whether the ceiling comes from subject class, topology, peer class, or current source right
- what stronger proof or topology change would raise the ceiling, if any

Typical reasons include:

- `subject class does not support owner-like delegation here`
- `same-host child cannot receive onward-share power`
- `linked own seats already resolve at the family level`
- `current grant chain cannot pass stronger rights than the source owns`

### 4) Onward-power card

Show separately whether the member may:

- mutate bytes
- invite new members
- narrow or widen rights for descendants
- revoke other members
- only propagate local drift that later gets overwritten

The page must keep mutation power and onward delegation power separate.

### 5) Local-drift / read-only behavior card

This card is mandatory whenever the current or previous right is narrower than local write ability at the filesystem level.
Show:

- whether local edits can occur physically
- whether those edits propagate back
- whether sync of changed files is suspended for this member
- whether a stronger local overwrite/repair policy is enabled
- safest next action

This keeps `read only` from pretending that nothing can drift locally.

### 6) Mutation review and receipts

Before any rights change, show:

- old effective right
- proposed new right
- changed onward powers
- descendants or local children affected
- resulting rights ceiling after apply
- emitted receipt class

Show recent receipts with:

- actor
- member
- old right
- new right
- ceiling reason if blocked or narrowed
- affected descendants count

### 7) Blocked actions drawer

Blocked or harsher actions may live behind a clearly named drawer such as `Unavailable or topology-blocked actions`.
That drawer may contain:

- why `delegate / owner-like` is unavailable
- why remove-and-recreate would be required instead of in-place mutation
- why a local child must be recreated rather than promoted

## Narrow-width behavior

In narrow width the page may stack cards, but it may not hide:

- current effective right
- strongest admissible ceiling
- onward-share power truth
- local-drift behavior if relevant

## Acceptance criteria

This spec is satisfied when:

- an operator can answer current right and strongest admissible right from one page
- `read only` does not hide what happens after a local edit anyway
- topology ceilings are explained in product language rather than by grayed-out controls alone
- onward delegation is public rather than bundled into one generic right name
- every rights mutation leaves a receipt naming the resulting right and any remaining ceiling
