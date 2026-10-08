# Removal contract sheet page: verb, plane, scope, residue, and reversibility interface spec

## Purpose

Before an operator disconnects, hides, evicts, unlinks, removes, deletes, or uninstalls, they need one ordinary page that answers:

> what kind of removal is this, which plane does it mutate, who loses visibility or bytes, what residue survives, and what is the strongest honest sentence the product can still say?

## Core decision

Every serious remove-like action must open one first-class **Removal contract sheet**.

The sheet owns:

- requested verb family
- mutation plane
- audience and scope
- surviving residue
- reversibility class
- comeback / reconnect path
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. removal claim header
2. verb family matrix
3. residue and survivor card
4. reversibility and comeback card
5. claim ceiling and next-safe action rail

### 1) Removal claim header

Show at minimum:

- target subject or seat
- requested verb (`disconnect`, `evict-local-material`, `remove-from-linked-set`, `delete-global-material`, `hide-roster-entry`, `unlink-seat`, `uninstall-runtime`, `unknown`)
- overall verdict (`local-only`, `linked-set-wide`, `global-delete-risk`, `residue-survives`, `reappears-later`, `unknown`)
- strongest safe sentence
- stronger rejected sentence
- evidence freshness

### 2) Verb family matrix

Columns:

- verb family
- mutated plane
- who is affected
- what remains untouched
- default comeback path

Rows must include at least:

- seat roster visibility
- seat linkage / authority
- subject registration in this runtime
- local bytes / placeholders
- remote linked seats
- remote non-linked seats
- archived / hidden service material

### 3) Residue and survivor card

Show:

- local disk residue
- placeholder residue
- archive / hidden service residue
- remote survivors outside the current scope
- latent members that can return later
- path/name residue that could mislead later operators

### 4) Reversibility and comeback card

Render at minimum:

- reconnect possible?
- path reselection required?
- duplicate-branch risk on reconnect?
- can a hidden or dormant member reappear later?
- does reinstall or re-add revive ordinary continuity?

### 5) Claim ceiling and next-safe action rail

Only show actions that preserve meaning, such as:

- `Open removal intent disambiguation`
- `Open device-local eviction boundary`
- `Open identity-wide removal review`
- `Emit removal receipt`

## Rules

### Rule 1 — remove-like verbs never collapse into one red button

The operator must not have to infer whether the action is local detachment, global deletion, seat cleanup, or software removal.

### Rule 2 — residue is part of the contract

The page must show what survives, not only what disappears.

### Rule 3 — reversibility must be typed

`Can reconnect later` is different from `bytes gone but path survives` and different again from `seat may silently reappear`.
