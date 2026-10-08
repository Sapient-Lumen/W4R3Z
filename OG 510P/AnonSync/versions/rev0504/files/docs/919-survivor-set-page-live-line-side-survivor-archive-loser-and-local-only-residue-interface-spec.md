# Survivor set page: live line, side survivor, archive loser, and local-only residue interface spec

## Purpose

Contested repair is not finished when a winner is chosen.
Operators still need one ordinary page that answers:

> after this contest or repair, what material actually survives, where, and under what status?

## Core decision

Every serious contested object and every serious repair receipt must project into one first-class **Survivor set** page.

The page owns:

- current live line
- side-by-side survivors
- archived losers
- local-only unsynced residue
- no-source / missing participants
- cleanup eligibility

## Layout

1. survivor summary strip
2. survivor matrix
3. cleanup and protection card
4. receipt links

### 1) Survivor summary strip

Show:

- contested object
- total survivor classes present
- whether live line is stable, provisional, or still contested
- strongest next-safe action

### 2) Survivor matrix

Render rows for:

- live winner
- side survivor
- archive-backed loser
- exported preserve copy
- local-only unsynced residue
- deleted / missing participant

Each row shows:

- location
- status
- whether it still participates in sync
- whether deletion is safe, dangerous, or blocked pending review
- lineage reference

### 3) Cleanup and protection card

Show:

- which survivors are protected from casual delete
- which require deeper review before cleanup
- which may be safely exported or detached
- whether deleting a named side survivor would hit a remote counterpart or only local residue

### 4) Receipt links

Link to:

- repair lineage receipt
- archive restore receipt if any
- export receipt if any
- conflict / chronology evidence packet if any

## Rules

### Rule 1 — survivor presence is not failure to clean up

Parallel or archived survivors are real outcomes and must stay visible until deliberately resolved.

### Rule 2 — dangerous delete stays explicit

The page must distinguish `local cleanup only` from `could delete live remote counterpart`.

### Rule 3 — sync participation stays visible

A survivor row must say whether it still participates in live sync, remains local-only, or is archive-only.

## Acceptance criteria

A later operator can:

- tell exactly what material survived the contest
- tell where each survivor lives now
- tell which ones still participate in live sync
- tell what cleanup is safe or unsafe
- trace each survivor back to a receipt or evidence basis
