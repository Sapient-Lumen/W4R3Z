# Remedy-hardening-attestation-finality contract sheet page — ruling class, reopen horizon, and supersession owner

## Purpose

This page is the operator's compact contract for a case whose challenge already received a ruling and now needs an explicit answer to whether that ruling is merely adjudicated, temporarily relied on, fully final, later superseded, or still reopenable.
It exists so the product can distinguish `we ruled once` from `we know exactly how durable that ruling is, who may rely on it, and what later evidence can still displace it`.

## Core fields

- case identifier
- source challenge receipt identifier
- source ruling identifier
- source pre-challenge sentence identifier
- current surviving sentence
- current finality class
- current reliance audience class
- ruling issue time
- reopen horizon type
- reopen horizon end time
- same-world continuity flag
- successor-world supersession flag
- superseding receipt identifier
- predecessor receipt identifier
- appeal lane status
- later-contradiction watch status
- decisive witness durability grade
- rotated-or-decayed evidence flag
- support-lane dependency flag
- restart-gated evidence dependency flag
- world-changing-repair flag
- strongest blocked permanence sentence
- strongest blocked stronger sentence
- next evidence that upgrades finality
- next evidence that reopens finality

## Finality classes

The page must model at least these distinct classes:

- provisional after ruling
- adjudicated but reopenable
- final on current record
- final for named consumer class only
- final for predecessor world only
- superseded by successor receipt
- reopened after later contradiction
- non-reopenable for the named sentence floor

## Reopen trigger classes

The page must model at least these distinct reopen triggers:

- appeal window still active
- later contradiction from a higher-priority witness
- evidence durability decay or rotation
- support-only witness later withdrawn or disputed
- world continuity break discovered after ruling
- successor-world repair that invalidates retroactive sameness
- UI or export surface proved stale or misleading
- identity or clone/fork ambiguity discovered later

## Required distinctions

The page must keep these truths separate:

- adjudicated versus final
- final on current record versus non-reopenable
- historical receipt preserved versus current receipt relied upon
- predecessor-world finality versus successor-world supersession
- calmer surface now versus evidence durable enough later
- one consumer allowed to rely versus all consumers allowed to rely
- superseded because improved versus superseded because the old ruling was too strong

## Layout

The page should be organized into five zones:

### 1) Sentence rail

Always print:

- the current surviving sentence
- the strongest blocked permanence sentence
- the strongest blocked stronger sentence
- the precise reason each stronger sentence is blocked

### 2) Finality rail

Show the current class as a ladder, not a single badge:

- provisional
- adjudicated
- final on current record
- audience-qualified final
- non-reopenable

The active rung must be highlighted and all blocked rungs must show their exact blockers.

### 3) Reopen rail

Show every live reopen trigger with status:

- armed
- expired
- tripped
- disproved
- inherited from predecessor receipt

### 4) Supersession rail

Show whether the receipt:

- still owns precedence
- shares precedence with lane restrictions
- has been superseded by a successor receipt
- survives only as historical lineage

### 5) Reliance rail

Show who may currently rely on the sentence:

- internal reviewer only
- named downstream automation only
- named human consumer classes only
- all current consumers for the sentence floor
- historical reader only

## Operator promises

The contract sheet must let the operator say things like:

- `this case is adjudicated, but the ruling is still reopenable because the decisive evidence can still be displaced by a higher-priority witness`
- `this receipt is final for historical lineage but not final for live automation`
- `this ruling is final only for the predecessor world because the successful successor-world rebuild cannot retroactively validate the earlier world`
- `this case is superseded by a new receipt, so the older receipt remains visible but loses precedence`
- `this sentence is non-reopenable only at the narrower floor, not at the original stronger claim`

## UI behavior

The page must visibly scar any permanence-like language with the exact blocker class:

- appeal still open
- evidence decay horizon not yet passed
- same-world continuity not preserved
- successor receipt already outranks this one
- support-lane witness not durable enough
- restart or rebuild changed observed world
- higher-priority contradiction lane still armed
