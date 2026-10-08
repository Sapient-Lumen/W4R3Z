# Mobile reacquire page: local clear, download history, backup redownload, and byte-return truth interface spec

## Purpose

This page answers:

> if I clear local bytes on this mobile seat, what exact path exists to get them back later?

The page exists because `remove`, `clear`, `delete from Downloads`, `remove from Shared links`, and `clear local synced files` are not the same recovery contract.

## Core rule

Every mobile seat that allows local byte removal must expose one first-class **Mobile reacquire** page.
That page owns:

- local-removal action class
- surviving history / receipt classes
- reacquire path
- prerequisites and failure modes for reacquire

## Primary layout

The page always renders the same regions:

1. reacquire verdict
2. removal-action matrix
3. surviving receipts card
4. reacquire path card
5. receipts

### 1) Reacquire verdict

Show:

- seat / subject / item context
- strongest reacquire verdict: `reacquirable-from-live-source`, `reacquirable-from-backup`, `history-only`, `receipt-only`, `not-currently-reacquirable`, `unknown`
- one next honest action

### 2) Removal-action matrix

Rows should include, when relevant:

- clear local synced files
- remove from device
- remove downloaded file
- remove shared-link row only
- clear storage bucket
- remove backup-local copy

Columns should include:

- removes bytes
- removes history row
- requires Selective Sync
- affects remote peers
- expected placeholder or residue state

The operator must be able to answer: **what exactly disappears under each action?**

### 3) Surviving receipts card

Show:

- download history rows
- shared-link history
- backup membership / sink presence
- sync-subject presence with placeholders or disconnected residue
- storage-accounting residue

The operator must be able to answer: **what proof or history survives after the bytes are gone?**

### 4) Reacquire path card

Show:

- whether reacquire requires a live full source
- whether backup-specific redownload is available
- whether the seat must stay open / foregrounded for bytes to return
- whether manual save-back or replacement is needed instead of simple fetch
- why reacquire may currently fail

The operator must be able to answer: **how do I honestly get the bytes back, and what prerequisites still matter?**

### 5) Receipts

After any clear/remove action, emit a receipt that preserves:

- action class
- surviving receipt classes
- current reacquire verdict
- strongest prerequisite or blocker

## Honest outputs

This page may conclude:

- `reacquirable if a live source peer stays online`
- `backup photo can be re-downloaded locally`
- `download removed but history still visible`
- `shared-links row removed from UI only; system file remains`
- `clearing requires Selective Sync and leaves placeholders`
- `copy-edit-return workflow does not support in-place reacquire`

It may not compress these into one generic `available later` promise.

## Rules

### Rule 1 — history and bytes must never be conflated

The page must distinguish bytes, history rows, and proof receipts.

### Rule 2 — reacquire prerequisites must stay adjacent to removal

Operators should not clear bytes first and only then discover that a live source, Selective Sync, or foreground runtime was required.

### Rule 3 — backup redownload and ordinary sync fetch are different paths

If a recovery path exists only for certain backup material or only from specific history, the page must name that path directly.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- what exact removal action they are about to use
- what history or proof survives afterward
- whether the bytes can come back at all
- whether reacquire needs live source, backup redownload, or manual save-back
- what current blocker or prerequisite still stands
