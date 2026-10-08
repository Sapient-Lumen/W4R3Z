# Control attestation lineage receipt page: latest proof, mechanism, and blocked stronger sentences interface spec

## Purpose

The attestation contract, review, rehearsal proof, and decay timeline carry detail.
What the archive still needs at handoff time is one compact receipt answering:

> why do we still trust this control, what was the last real proof, and what stronger sentence is still blocked right now?

## Core decision

AnonSync must emit one **Control attestation lineage receipt** whenever a control gains trust, loses trust, misses freshness, passes rehearsal, or has trust withdrawn.

## Required receipt fields

### Identity block

- `control_id`
- control revision
- source case ids
- owner
- current mechanism family
- current trust state

### Proof block

- latest accepted witness class
- latest proof time
- freshness deadline
- rehearsal required or not
- proof scope
- excluded scope

### Truth block

- strongest safe sentence
- blocked stronger sentence
- anti-claim
- surviving weaker sentence if stale
- latest decay pressure

### Failure block

- latest trust-withdrawal trigger
- latest same-cause escape if any
- next required review page
- next acceptable witness
- successor control if any

## Supported compact verdict language

The receipt must support compact phrases such as:

- `attested by paired-surface check; trusted within desktop worlds only`
- `configured and active, but stale after version-floor change`
- `rehearsed in isolated world; still blocked from fleet-preventive claim`
- `trust withdrawn after service-world fork`
- `passive window renewed; stronger claim still blocked without drill`

## Hard rules

### 1) Latest accepted proof stays visible

A receipt is incomplete if it tells the reader only the current setting state but not the last accepted witness.

### 2) Freshness is mandatory

A receipt must always tell the next operator when this trust expires or what event already withdrew it.

### 3) Weaker surviving sentence is mandatory on downgrade

When trust falls, the receipt must preserve the weaker sentence that is still safe, if any.

### 4) Proof scope may not round up

A rehearsal or live check that covered only one world or lane may not silently become a fleet-wide trust receipt.

### 5) Handoff must preserve the next overclaim to avoid

The receipt is not complete unless it says what sentence would currently be too strong.
