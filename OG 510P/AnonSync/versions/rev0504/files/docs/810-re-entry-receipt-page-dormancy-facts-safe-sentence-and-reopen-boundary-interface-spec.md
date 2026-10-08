# Re-entry receipt page — dormancy facts, safe sentence, and reopen boundary interface spec

## Purpose

The archive already had freshness receipts, opportunity receipts, and route receipts.
What it still lacked was the durable receipt for the question:

> after this dormancy interval, what exact return class was accepted, what sentence was judged safe, and what would reopen that judgment?

AnonSync should therefore issue a dedicated **re-entry receipt** whenever it resolves a stale-return question.

## Receipt fields

The receipt must preserve:

- receipt id
- incident id
- seat / subject scope
- dormancy interval
- last good witness
- current return witness
- re-entry class
- roster visibility state
- chronology confidence
- source-reality verdict
- strongest allowed sentence
- stronger rejected sentence
- supporting page ids (`807`, `808`, `809`)
- issued-at timestamp
- reopen conditions

## Required sections

### 1) Dormancy facts

State the durable dormancy basis, for example:

- `Hidden roster entry reappeared after 12 days; linkage continuity visible again, chronology still guarded.`
- `Peer returned after aging out of the roster; full source proof not yet restored.`
- `Seat resumed after offline editing period; clock validity blocks ordinary ordering claims.`

### 2) Safe current sentence

Publish one durable sentence, for example:

- `The seat returned, but should still be treated as a guarded re-entry.`
- `Visibility continuity returned; source continuity is not yet fully proved.`
- `The announcement remains visible, but no full source peer is currently proved.`
- `Ordinary participation was restored for this scope.`

### 3) Stronger rejected sentence

This is mandatory.
Examples:

- `Everything is normal again.`
- `This returning copy is definitely newest.`
- `The file is now fetchable.`

### 4) Reopen conditions

The receipt must say the judgment reopens if any of these happen:

- clocks or timezone drift reappear
- source-reality evidence changes materially
- dormancy class is revised by stronger witnesses
- local offline edits or divergence evidence newly appear
- freshness invalidation or later re-entry supersedes the basis

## Compact rendering obligations

Any compact receipt chip must still preserve:

- re-entry class
- chronology confidence
- safe current sentence
- reopen trigger summary

## Anti-clone rule

Do not clone receipts that merely say `back online`, `returned`, or `looks good now` without preserving dormancy facts, safe language, and reopen boundaries.
