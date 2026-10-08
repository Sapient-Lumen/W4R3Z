# Warning history page: acknowledgment, residue, evidence, and recurrence interface spec

## Purpose

Answer the later question:

> this warning is gone or quieter now, but what exactly happened, what was merely acknowledged, what residue remains, and how often has this class come back?

This page exists because operators often remember only that a banner disappeared, not whether the system self-recovered, an operator acknowledged it, or a strong repair rebuilt continuity.

## Core rule

Every durable warning must have a **warning history** timeline.
The timeline must distinguish four different outcomes:

1. `self-cleared`
2. `acknowledged-no-repair`
3. `repair-applied`
4. `muted-but-recurrent`

The product must never flatten those into one `resolved` badge.

## Required sections

### 1) Warning lifecycle timeline

Show:

- first seen
- severity changes
- evidence changes
- acknowledgements
- applied repair rungs
- self-clear / recurrence events
- current residue state

### 2) Acknowledgment semantics

Whenever the user acknowledged the warning, preserve:

- who acknowledged it
- scope of acknowledgment
- whether visibility changed only locally or across collaborators
- what acknowledgment explicitly did **not** repair

### 3) Residue after clear

Even if the banner is gone, show whether residue remains:

- chronology repaired but loser fate still unknown
- continuity rebuilt but old local state discarded
- source absence cleared after a peer returned
- transient load self-cleared without structural mutation
- warning suppressed while detector remains degraded

### 4) Recurrence pattern

Show:

- recurrence count
- recurring class/fingerprint
- last interval between occurrences
- whether the same repair rung has failed repeatedly
- whether escalation is now recommended by history, not just current state

### 5) Exportable statement

The page must be able to emit one honest sentence such as:

- `Acknowledged locally; no repair was applied.`
- `Self-cleared after transient load; no continuity damage proved.`
- `Cleared after reconnect to same path; chronology remains valid.`
- `Recurred three times after the same local storage-floor condition.`

## Data model

- `warning_history_id`
- `warning_code`
- `scope_ref`
- `events[]`
- `ack_events[]`
- `repair_receipts[]`
- `self_clear_events[]`
- `recurrence_count`
- `residue_state`
- `exportable_statement`

## Failure this page prevents

Without this page, operators confuse silence with repair, forget recurrence, and lose the evidence trail needed to choose a stronger rung next time.

AnonSync should instead preserve warning memory as a first-class history object.
