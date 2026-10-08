# State adoption review page — cold successor, stale backup, concurrent duplicate, and clean seat

## Purpose

Review any attempt to open copied state, restored backup state, or reviewed successor artifacts before the runtime is allowed to rely on them.

This page exists to answer:

- `what kind of state source is this really?`
- `is live activation admissible, inspection-only, or blocked?`
- `what continuity would survive if I proceed?`
- `what safer alternative exists if this is a bad clone story?`

## Classification classes

The page must classify the candidate as exactly one of:

1. `same-world reopen`
2. `cold successor import`
3. `stale backup / snapshot restore`
4. `concurrent duplicate risk`
5. `foreign / unknown state`
6. `clean seat`
7. `proof insufficient`

## Required sections

### 1. Candidate source summary

Must show:

- source kind (`successor capsule`, `raw storage copy`, `disk image`, `backup restore`, `manual folder pick`, `detected prior world`, `other`)
- how it was discovered
- source freshness
- whether another runtime may still exist using the same source lineage

### 2. Evidence comparison

Must compare current seat and candidate across:

- world id
- state-root origin
- seat handle / certificate family
- subject roster lineage
- last known receipts
- export/import provenance if present

### 3. Continuity verdict

Must publish:

- whether live activation is allowed, inspection-only, or blocked
- whether seat identity is continuous, reborn, unknown, or duplicate-risk
- whether subject state is reusable, narrowed, stale, or foreign

### 4. Consequence ladder

For each admissible path, preview:

- `activate as cold successor`
- `open inspect-only`
- `start clean seat and reconnect separately`
- `export reviewed successor from original seat first`
- `block until predecessor is retired`

### 5. Strongest safe sentence

Examples:

- `This looks like a reviewed successor artifact for replacement of a stopped predecessor seat.`
- `This is a raw storage copy with duplicate-seat risk; live activation is blocked.`
- `This is an older backup that may be inspected or selectively recovered, but not claimed as present continuity.`

### 6. Receipt linkout

The review must end with either:

- an activation-proof link
- an inspect-only receipt
- a blocked-adoption receipt
