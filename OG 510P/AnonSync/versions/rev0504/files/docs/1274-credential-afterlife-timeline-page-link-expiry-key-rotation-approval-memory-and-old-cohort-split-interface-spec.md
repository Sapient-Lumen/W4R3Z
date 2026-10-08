# Credential-afterlife timeline page: link expiry, key rotation, approval memory, and old-cohort split interface spec

## Purpose

The admission sheet answers *what is true now*.
This page answers the operator's follow-on question:

> how did this access path evolve over time, when did the invite stop being reusable, what trust memory still applied, and did later key change split the lineage?

## Core decision

AnonSync must require a **Credential-afterlife timeline** whenever current admission truth depends on time-varying invitation state, remembered approvals, or local credential rotation.

## Timeline layout

1. **Current admission banner**
2. **Admission-event sequence**
3. **Reuse / expiry forecast rail**
4. **Lineage-split intervals**
5. **Blocked stronger sentence**

### 1) Current admission banner

Show:

- current admission label
- entered-at time
- strongest safe sentence
- next expected expiry or review event if known
- blocked stronger sentence

### 2) Admission-event sequence

Supported events:

- `identity-link-created`
- `manual-key-shared`
- `manual-link-generated`
- `qr-rendered`
- `approval-request-sent`
- `approval-granted`
- `certificate-issued`
- `acl-installed`
- `link-expired-by-time`
- `link-expired-by-use-count`
- `approval-memory-reused`
- `approval-memory-not-reused`
- `local-key-rotated`
- `old-key-cohort-continued`
- `new-key-redistributed-manually`
- `access-revoked`
- `unknown-transition`

Each event must show:

- timestamp
- cause class
- changed truths
- source evidence
- resulting strongest safe sentence

### 3) Reuse / expiry forecast rail

This rail must answer:

- can new peers still join through this instrument?
- if not, is the block caused by time expiry, use exhaustion, or revocation?
- does remembered approval still apply for any class of rejoin?
- is manual redistribution required after rotation?

Supported forecast states:

- `new-joins-still-allowed`
- `new-joins-blocked-by-time-expiry`
- `new-joins-blocked-by-use-exhaustion`
- `rejoin-may-use-remembered-approval`
- `new-manual-distribution-required`
- `unknown`

### 4) Lineage-split intervals

This section preserves periods where one optimistic sentence would be dangerously wrong, including:

- expired invitation while existing grants may still persist
- approval memory applying only to some peer/folder combinations
- one peer rotating key while old-key peers continue syncing together
- manual redistribution not yet performed after rotation

The operator must be able to answer:

> when did this stop being one admission lineage and become two?

### 5) Blocked stronger sentence

Examples:

- `The expired link closed the whole share` blocked because only future joins were blocked
- `Trust was remembered everywhere` blocked because remembered approval is scoped
- `The key change migrated the cohort` blocked because old-key peers continued without automatic redistribution

## Hard rules

- expiry, revocation, and lineage split must stay distinguishable
- the timeline must never collapse local key change into a cohort-wide credential update
- remembered approval must identify its exact scope
- forecast confidence must be explicit
