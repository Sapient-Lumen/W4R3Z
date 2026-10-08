# Contested object contract sheet page: contest class, repair ladder, and claim ceiling interface spec

## Purpose

Before an operator repairs any contested file, folder, or subtree, they need one ordinary page that answers:

> what exactly is contested, which bytes are still live, what survivor classes exist, and what are the honest repair paths from here?

This page exists so named conflicts, blocked read-only edits, returning offline winners, archive-backed losers, and local-only extras do not remain separate folklore families.

## Core decision

Every serious sync repair surface must open one first-class **Contested object contract sheet**.

The sheet owns:

- contest class
- participant set
- current live winner or blockage verdict
- survivor classes already present
- repair ladder
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. contest claim header
2. contest basis card
3. participant and survivor card
4. repair ladder card
5. claim ceiling and next-safe action rail

### 1) Contest claim header

Show at minimum:

- subject / path / subtree
- contest class (`named-conflict`, `blocked-ro-edit`, `offline-returning-winner`, `archive-replay-candidate`, `local-only-residue`, `mixed`, `unknown`)
- current live-line verdict (`clean-live`, `blocked`, `parallel-live`, `candidate-only`, `unsafe-to-claim`)
- strongest safe sentence
- stronger rejected sentence

Example safe sentence:

- `This path is contested because a read-only local edit is blocking ordinary intake; the live remote line still exists separately.`

### 2) Contest basis card

Render rows for each serious basis family:

- local edit divergence
- rename / name collision
- offline chronology return
- archive-backed older version
- permission / posture blockage
- invalid-path / platform collision
- unknown diagnostic residue

Each row shows:

- whether it is active now
- evidence freshness
- affected scope
- whether it blocks intake, blocks apply, or only narrows claims

### 3) Participant and survivor card

Show the current known participants:

- current live winner candidate
- blocked local survivor
- parallel named survivor
- archive-backed loser
- local-only unsynced residue
- missing / no-source participant

Each row shows:

- location
- authority basis
- chronology grade if relevant
- expected future fate without intervention

### 4) Repair ladder card

This card is mandatory.
Show ordered repair paths such as:

- `inspect only`
- `export preserved copy`
- `keep side-by-side survivor`
- `resume remote winner`
- `restore archived candidate into live line`
- `enable overwrite / revert local edits`
- `promote local survivor`

Each path shows:

- prerequisites
- live mutation scope
- loser fate
- runtime dependence
- receipt it will emit

### 5) Claim ceiling and next-safe action rail

Only show actions that preserve meaning, such as:

- `Open repair review`
- `Export survivor first`
- `Clear blockage without touching live line`
- `Approve live repair`
- `Emit receipt without overclaim`

## Rules

### Rule 1 — contest class is public, not diagnostic trivia

The operator must never have to infer from naming conventions or stalled rows what sort of contest this is.

### Rule 2 — survivor classes stay visible before any repair

The page must not collapse parallel survivors, archived losers, and local-only extras into one generic bucket.

### Rule 3 — claim ceiling is mandatory

The page must say the strongest honest sentence now and keep a stronger tempting sentence visibly rejected.

Example rejected sentence:

- `This item has already been safely reconciled and only one authoritative version remains.`

## Acceptance criteria

A later operator can:

- tell why this object is contested
- tell which participants and survivor classes exist
- tell what repair paths are actually available
- tell which move mutates the live line and which does not
- tell what stronger reading is still forbidden
