# Archive restore review page: manual resurrection, runtime witness, and source authority interface spec

## Purpose

This page exists for the moment an operator tries to resurrect a file from hidden historical bytes.
It answers one ordinary question:

> if I pull this version out of Archive now, what exactly happens next, what runtime conditions must already hold, and does this seat have authority to make the restored version matter beyond local disk?

## When this page must appear

Trigger this page for:

- any explicit `restore from archive` action
- any attempt to use archived bytes to recover a deleted file
- any restore attempt from a seat that is read-only, encrypted, or otherwise authority-limited
- any action that would otherwise let a copied-out archive file masquerade as restored shared truth

## Fixed page order

1. restore intent header
2. source-authority and runtime card
3. resurrection path card
4. risk and ceiling card
5. receipt/export rail

### 1) Restore intent header

Show:

- subject / seat / archived object version
- seat authority class
- current runtime status
- restore verdict (`publish-capable restore`, `local-only salvage`, `other-rw-seat required`, `unsafe-to-claim`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

### 2) Source-authority and runtime card

Render rows for:

- Sync currently running / not running / unknown
- seat may publish restored bytes outward / may not / unknown
- encrypted custody rules apply / do not apply / unknown
- manual copy/move required / no automatic restore action
- local file path that will receive the restored version

### 3) Resurrection path card

Show the exact reviewed sequence:

1. identify target archived version
2. copy or move it out of `.sync/Archive`
3. place it in reviewed destination path
4. keep runtime live so newer/older comparison happens immediately
5. observe whether publication outward is expected, blocked, or requires another seat

### 4) Risk and ceiling card

Possible warnings:

- `restored version may be re-archived as older if runtime is not live`
- `this seat has archived bytes but cannot republish them`
- `restoration is manual and version selection is operator-authored`
- `retention or size ceilings may already have removed other versions`
- `Archive is historical witness, not a complete history promise`

### 5) Receipt/export rail

Offer:

- `Emit archive lineage receipt`
- `Open archive salvage proof`
- `Open archive contract sheet`

## Rules

### Rule 1 — manual restore must stay visibly manual

The page must not imply a one-click authoritative undo if the system really depends on manual copy/move.

### Rule 2 — runtime witness belongs on the restore page

If success depends on Sync already running, that condition must be visible before commit.

### Rule 3 — local salvage and authoritative restore are different verbs

A local readable copy is weaker than swarm-visible restoration.
