# Temporal authority contract sheet page — ordering basis, disk-vs-ledger time, and proof ceiling

## Purpose

Give the operator one canonical answer to:

> which timestamps are actually governing chronology for this subject right now, how trustworthy are they, and what stronger time-based claim is still forbidden?

This page exists so the product never lets `modified at`, `current timestamp`, `latest`, or `restored` pretend to mean the same thing.

## Core objects shown

### 1. Claim sentence

A single human sentence at the top, for example:

- `Chronology is currently ordered by trusted peer mtime with a 600-second skew budget.`
- `Ledger mtime is authoritative for ordering; disk-visible timestamp on this seat is not trustworthy.`
- `Replay chronology is guarded because one peer is outside drift budget and one restored candidate carries older mtime.`

### 2. Ordering-basis panel

Show:

- active ordering basis: `peer mtime`, `ledger mtime`, `manual override`, `insufficient confidence`
- whether wall clock, timezone correctness, or both are part of current trust
- active skew budget
- current confidence class: `trusted`, `guarded`, `quarantined`, `clock-blind`

This panel answers `what clock/timestamp basis is actually being trusted?`

### 3. Timestamp-provenance panel

Show separate rows for:

- disk-visible timestamp
- ledger / database timestamp
- peer-published timestamp
- restored-candidate timestamp
- operator-entered or manual override timestamp if present

Each row publishes:

- source plane
- last observed value
- current trust grade
- whether it participates in ordering
- stronger blocked sentence

### 4. Divergence matrix

Columns:

- value visible on disk
- value held in ledger
- ordering relevance
- confidence
- operator consequence

Cells show one of:

- `matches`
- `diverges but ledger authoritative`
- `diverges and ordering unsafe`
- `unknown`

### 5. Chronology consequence panel

Show:

- whether `latest` claims are safe
- whether replay/restore claims are safe
- whether freshness claims are weakened
- which recent decisions are now suspect

### 6. Strongest-safe-sentence panel

Show:

- strongest safe sentence
- stronger rejected sentence
- invalidators that would weaken the claim

## Required fields

- subject identifier
- active ordering basis
- skew budget
- confidence class
- disk timestamp value and trust grade
- ledger timestamp value and trust grade
- divergence verdict
- strongest safe sentence
- stronger rejected sentence
- invalidator list

## Interaction rules

- Never collapse disk time and ledger time into one displayed `modified` field.
- If disk time is visible but not authoritative, badge it as `visible only`.
- If ledger time is authoritative but not filesystem-visible, say so in the main page body, not only in expert details.
- Any `latest`, `fresh`, or `restored` badge must link back to this sheet.
- The page must remain readable without opening logs or power-user settings.

## Empty / degraded states

The page must say so plainly when time truth is weak:

- `Filesystem timestamp is current-time residue; ordering uses ledger mtime only.`
- `Peer time is outside drift budget; automatic chronology is held.`
- `Restore candidate carries older mtime and will likely lose without guarded replay.`
