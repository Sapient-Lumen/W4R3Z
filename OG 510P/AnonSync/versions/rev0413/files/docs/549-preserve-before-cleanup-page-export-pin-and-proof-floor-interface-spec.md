# Preserve-before-cleanup page: export, pin, and proof-floor interface spec

## Purpose

This page answers:

> before I clean this up, what should I preserve so I do not accidentally narrow later recovery, audit, or explanation truth?

The page exists because preservation is not merely the opposite of deletion.
It is a reviewed choice about which proof floor should remain afterward.

## Core decision

Whenever cleanup would weaken any meaningful witness class, the product must offer one first-class **Preserve-before-cleanup** page.
That page owns:

- candidate witnesses worth preserving
- preservation goals
- concrete preservation actions
- cost and residue of preservation itself
- resulting proof floor after cleanup

## Primary layout

The page always renders the same regions in the same order:

1. preservation goal strip
2. candidate-witness table
3. preservation actions card
4. cost and residue card
5. resulting proof-floor card
6. proceed / decline decision card
7. preservation receipt target

### 1) Preservation goal strip

Show:

- requested cleanup action waiting downstream
- current at-risk witness summary
- recommended preservation goal (`retain-rollback`, `retain-audit`, `retain-discoverability`, `retain-minimum-proof`, `no-preservation-needed`)

### 2) Candidate-witness table

Each row should show:

- witness class
- current host / surface
- why it matters
- preservation suitability (`best`, `acceptable`, `poor`, `not-worth-preserving`)
- whether preserving it changes local residue or disk cost

### 3) Preservation actions card

Offer explicit actions such as:

- `export prior-version bundle`
- `pin hidden witness / suspend pruning`
- `switch recovery locus to another seat`
- `keep placeholders / names visible`
- `keep app installed; use local reclaim only`
- `extend retention window`
- `accept minimum-proof cleanup with no extra preservation`

The product must choose one strongest recommended action whenever the witness floor would otherwise fall materially.

### 4) Cost and residue card

Show:

- bytes added or retained by preservation
- whether new hidden residue is intentionally kept
- whether preservation creates a new receipt, bundle, or manual export obligation
- whether the preservation is temporary or durable

### 5) Resulting proof-floor card

Show the proof floor *after* preservation and *after later cleanup*:

- `rollback-bytes preserved`
- `event-only preserved`
- `discoverability only preserved`
- `manual export only preserved`
- `no meaningful proof preserved`

### 6) Proceed / decline decision card

Show two paths side by side:

- `Preserve then continue cleanup`
- `Continue cleanup without preservation`

If the operator declines preservation, the page must show the stronger sentence they are giving up.

### 7) Preservation receipt target

Link to the receipt that will later prove exactly what was preserved before cleanup.

## Rules

### Rule 1 — preservation must be typed by witness class

`Save backup` is not enough.
The page must say whether it preserved rollback bytes, event history, hidden archive residue, or only ordinary files.

### Rule 2 — preservation may not hide its own residue

If preservation keeps hidden or local-only material around, the page must name that residue directly.

### Rule 3 — decline path must stay honest

If the operator chooses not to preserve, the product must show the narrower proof floor without editorial softening.

## Honest outputs

The page may conclude:

- `Export one prior-version witness before local cleanup.`
- `Keep placeholders visible; do not prune hidden archive yet.`
- `Switch to remote desktop host if you need later rollback after uninstall.`
- `Proceed without preservation; later proof floor becomes names/history only.`
