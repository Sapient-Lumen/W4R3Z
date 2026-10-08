# Mobile path class page: sandbox, fixed default, SD-root grant, and source-only path truth interface spec

## Purpose

This page answers:

> what kind of path is this on this mobile seat, and what exact authority do I have over it right now?

The page exists because `folder picker` is not one honest concept on mobile.
Sometimes the product is choosing a destination.
Sometimes it is only gaining authority to use a storage class later.

## Core rule

Every mobile destination or source path review must expose one first-class **Mobile path class** page.
That page owns:

- path class
- current writability
- admission prerequisites
- fixed-default versus explicit-choice truth
- source-only versus destination-capable truth

## Primary layout

The page always renders the same regions:

1. path-class verdict
2. path capability matrix
3. admission steps card
4. consequence card
5. receipt

### 1) Path-class verdict

Show:

- seat / platform
- path class verdict: `app-sandbox`, `internal-default`, `explicit-internal`, `sd-granted`, `external-source-only`, `downloads-fixed`, `unknown`
- strongest honest writability verdict
- one next honest action

### 2) Path capability matrix

Show rows for the relevant classes on this seat:

- app sandbox
- fixed internal default
- explicit internal chooser
- SD / removable card with provider grant
- external source-only path
- one-off download store

Columns should include:

- readable
- writable
- usable as live sync destination
- usable as backup source
- chooser visibility
- prerequisite state

The operator must be able to answer: **which path classes are real options here, and what can each one honestly do?**

### 3) Admission steps card

Show:

- whether Simple Mode or similar simplification is currently hiding choices
- whether the operator must first grant root-level storage authority
- whether the current step is choosing a location or granting future access
- the exact failure mode if the wrong picker path is used

The operator must be able to answer: **what must I do before this class becomes writable or choosable?**

### 4) Consequence card

Show:

- default naming / placement behavior
- whether collisions create suffixed paths
- whether some classes are invisible in the ordinary picker
- archive / storage / background caveats that materially differ by class

The operator must be able to answer: **what long-lived behavior comes with choosing this path class?**

### 5) Receipt

After apply, emit a receipt that preserves:

- chosen path class
- authority-grant witness if any
- whether the act was `grant`, `choose`, or `grant-then-choose`
- strongest remaining restriction

## Honest outputs

This page may conclude:

- `simple-mode fixed internal destination`
- `explicit internal path selected`
- `SD card writable after root grant`
- `external card readable as backup source only`
- `sandbox-only seat`
- `download store is fixed and non-relocatable`

It may not compress these into one generic `chosen folder` row.

## Rules

### Rule 1 — writability must be class-based, not assumed

The page must not infer that a visible folder is writable as a live destination without class-specific proof.

### Rule 2 — grant and choose must stay separate

If the operator is really granting access to a storage class rather than selecting the final share directory, that distinction must stay visible.

### Rule 3 — simplification modes must be public state

If a simplified mode hides root, SD, or custom placement choices, that fact must render as a first-class cause.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- what path class they are acting on
- whether it is writable, source-only, sandbox-only, or fixed-default
- whether a mode switch or storage grant is still required
- whether the current chooser is granting authority, choosing location, or both
- what long-lived restrictions come with the selected class
