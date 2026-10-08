# Lock contention watch page: blocked object list, unknown locker, and recheck cadence interface spec

## Purpose

When synchronization is blocked by another application or stranded network-share locks, the operator needs one ordinary watch surface that answers:

> which objects are blocked, how fresh is this blockage, do we know who holds the lock, what retry posture is active, and what safe next step exists?

This page exists so `locked files` do not remain a terse status badge plus troubleshooting article.

## Core decision

Lock contention is a first-class blockage object.
The watch page owns:

- blocked object set
- scope and freshness
- lock-holder knowledge class
- automatic recheck cadence
- current sync consequence
- safe next actions

## Fixed page order

1. blockage summary header
2. blocked object table
3. lock knowledge card
4. retry / recheck card
5. safe next step rail

### 1) Blockage summary header

Show:

- number of blocked objects
- earliest / latest observation time
- affected scope
- current consequence (`transfer-blocked`, `indexing-blocked`, `mixed`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

Example safe sentence:

- `Four files are currently blocked by lock contention; Sync can name the objects but cannot identify the locking process.`

### 2) Blocked object table

Each row shows:

- object path
- object class
- first seen blocked
- last checked
- current state (`still-locked`, `cleared`, `stale`, `unknown`)
- path jump affordance

### 3) Lock knowledge card

Show:

- whether locker identity is known, inferred, or unknown
- whether the lock likely came from local app, network-share residue, or mixed topology suspicion
- what evidence exists
- what stronger diagnosis remains forbidden

Do not imply a lock owner if the runtime only knows the file is inaccessible.

### 4) Retry / recheck card

Show:

- automatic recheck interval
- last retry outcome
- whether restart is recommended, optional, or not relevant
- whether retries are suppressed to avoid high CPU cost

Possible cadence states:

- `continuous event retry`
- `scheduled recheck`
- `manual retry only`
- `restart-gated`

### 5) Safe next step rail

Only show actions that preserve meaning, such as:

- `Reveal blocked paths`
- `Retry now`
- `Open topology review`
- `Mark as external-writer suspicion`
- `Emit lock receipt`

## Rules

### Rule 1 — unknown locker identity stays explicit

The page must never pretend to know which process owns the lock unless there is real evidence.

### Rule 2 — blockage freshness matters

Old unresolved locks and newly observed locks are not the same risk sentence.

### Rule 3 — lock watch and topology watch stay connected

If the blockage plausibly comes from a degraded substrate or mixed-writer topology, the page must surface that link.

### Rule 4 — retry posture is part of the contract

Operators need to know whether the product will recheck later, needs manual retry, or still depends on restart.

## Acceptance criteria

A later operator can:

- tell which objects are blocked
- tell how fresh the blockage is
- tell whether locker identity is actually known
- tell what retry cadence is active
- tell whether topology suspicion is involved
- tell what stronger diagnosis remained forbidden
