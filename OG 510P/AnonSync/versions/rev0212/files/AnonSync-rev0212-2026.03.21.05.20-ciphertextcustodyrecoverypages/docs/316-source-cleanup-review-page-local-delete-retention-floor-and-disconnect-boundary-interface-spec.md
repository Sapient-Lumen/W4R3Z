# Source cleanup review page: local delete, retention floor, and disconnect boundary interface spec

## Purpose

This page answers one ordinary question:

> if I delete from the source, pause the ingest relationship, or disconnect it entirely, what exactly survives, what future ingest stops, and what retention promise remains true?

The page exists because `delete from source`, `clear local bytes`, `pause`, and `disconnect` are materially different actions.

## Core decision

Every capture-only ingest relationship must render one first-class **Source cleanup review** page.
That page owns:

- current source-cleanup action under review
- earned retention floor for already-landed items
- distinction between future ingest and already-landed copies
- disconnect boundary and residue
- cleanup receipt

The workbench must not force the operator to remember backup folklore when they are deciding whether to free space on the source.

## Primary layout

The page always renders the same regions in the same order:

1. cleanup action strip
2. current consequence card
3. retention floor card
4. pause versus disconnect boundary card
5. cleanup receipts

### 1) Cleanup action strip

Show:

- relationship label
- action under review: `delete source items`, `evict local preview`, `pause ingest`, `disconnect ingest`
- current verdict: `safe`, `safe-with-scope-limit`, `not-safe-yet`, `review-required`
- strongest next honest action

### 2) Current consequence card

This card publishes:

- which bytes are affected immediately
- whether the action changes only source bytes or also relationship state
- whether already-landed sink copies remain protected
- whether future source discoveries stop, slow, or continue

The operator must be able to answer: **what exactly changes the moment I do this?**

### 3) Retention floor card

This card publishes:

- what retention promise has already been earned for landed items
- whether the promise is sink-specific, policy-specific, or unconditional
- whether sink-side edits or deletes can propagate back in this relationship
- what warning applies if the landed-proof threshold is not yet met

The operator must be able to answer: **what durable promise survives after source cleanup?**

### 4) Pause versus disconnect boundary card

This card publishes:

- what pause means for existing bytes and future captures
- what disconnect means for existing bytes and future captures
- whether disconnect removes only relationship state or also local placeholders/previews on any participating seat
- whether later reconnection preserves continuity or starts a new review boundary

The operator must be able to answer: **what future ingest stops, and what already-landed copies remain?**

### 5) Cleanup receipts

Receipts show:

- safe-delete guidance granted
- source cleanup performed
- ingest paused or resumed
- ingest disconnected
- retention promise acknowledged
- relationship later reattached or replaced

## Non-negotiable rules

### Rule 1 — source cleanup and relationship teardown are separate

Deleting source bytes is not the same thing as pausing or disconnecting the ingest relationship.

### Rule 2 — retention floor must stay adjacent to cleanup guidance

The page must show what promise has already been earned before presenting a destructive source action as safe.

### Rule 3 — future ingest stop must be explicit

Pause and disconnect must say whether they stop discovery, transfer, or only one path class.

## Honest outputs

The page may conclude:

- `Delete from source is safe for landed items only; three newer items remain below threshold.`
- `Pause keeps all landed sink copies intact but halts further ingest until resumed.`
- `Disconnect preserves already-landed copies on admitted sinks and ends future capture from this source.`
- `Current retention floor is not yet earned; cleanup guidance downgraded to review-required.`

It may not collapse those outcomes into one generic `stop backup` or `remove from phone` label.
