# Archive contract sheet page: version witness, restore authority, and retention class interface spec

## Purpose

Before an operator treats Archive like safety, recovers a file, disables versioning, or clears hidden sidecar state, they need one ordinary page that answers:

> what do archived bytes on this seat actually witness, who is allowed to restore them, how long are they expected to survive, and what stronger recovery sentence is still blocked?

This page exists so `Archive` does not remain an over-compressed comfort word.

## Core decision

Every serious archive-bearing subject / seat pair must open one first-class **Archive contract sheet**.

The sheet owns:

- archived-byte witness class
- restore-authority class
- retention class
- size/versioning ceiling
- platform visibility class
- runtime restore requirement
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. archive claim header
2. witness and authority card
3. retention and visibility card
4. restore conditions card
5. proof card
6. claim ceiling and next-safe action rail

### 1) Archive claim header

Show at minimum:

- subject / seat / runtime name
- archive witness verdict (`none seen`, `historical-remote-change witness`, `local-trash-only expected`, `unknown`)
- restore authority verdict (`this-seat may republish`, `this-seat may only salvage locally`, `other-rw-seat required`, `unknown`)
- retention class (`ttl-bound`, `never-auto-delete`, `size-excluded`, `unknown`)
- strongest safe sentence
- stronger rejected sentence
- evidence freshness

Example safe sentence:

- `This seat contains archived historical bytes produced by remote change, but restore authority may still require a different RW seat.`

### 2) Witness and authority card

Render rows for:

- archive enabled / disabled / unknown
- archive provenance (`remote modify`, `remote delete`, `mixed`, `unknown`)
- local-delete expectation (`trash/recycle`, `archive not expected`, `unknown`)
- seat authority class (`rw`, `ro`, `encrypted-ro`, `unknown`)
- restore publication class (`can republish`, `local salvage only`, `cannot republish`, `unknown`)

### 3) Retention and visibility card

Separate these truths explicitly:

- retention TTL
- never-delete override
- versioned file-size ceiling
- desktop/mobile class
- iOS visibility absence
- Android SD-card limitation
- uninstall survivor risk

### 4) Restore conditions card

Show required conditions such as:

- `manual restore only`
- `Sync must be running while restoring`
- `timestamp older-than-mesh risk exists`
- `restored file must be moved/copied out of Archive`
- `seat cannot publish restore because authority is read-only`

### 5) Proof card

Show the current proof rung:

- `documented behavior only`
- `saved subject/archive setting visible`
- `retention defaults known`
- `seat-class authority known`
- `runtime restore behavior witnessed`

### 6) Claim ceiling and next-safe action rail

Only show actions that preserve meaning, such as:

- `Open archive restore review`
- `Open archive retention and platform visibility page`
- `Open archive salvage proof`
- `Emit archive lineage receipt`

## Rules

### Rule 1 — archive is not backup language

The page must not imply independent full-history or guaranteed recoverability.

### Rule 2 — witness and restore authority must remain separate

Holding old bytes and being allowed to republish them are different truths.

### Rule 3 — retention is part of the contract, not a preference afterthought

TTL, file-size ceiling, and platform access limits must appear on the main page.

### Rule 4 — the page must refuse stronger language it cannot prove

Blocked examples:

- `this file is safely backed up here`
- `this seat can restore everything`
- `history is preserved indefinitely`
