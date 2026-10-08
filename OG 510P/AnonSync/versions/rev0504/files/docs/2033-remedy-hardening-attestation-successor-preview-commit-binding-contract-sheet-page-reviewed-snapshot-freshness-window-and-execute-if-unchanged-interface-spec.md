# Remedy-hardening-attestation successor preview/commit binding contract sheet page — reviewed snapshot, freshness window, and execute-if-unchanged gate

## Purpose

This page is the operator-facing contract sheet for one reviewed action run.
It exists to answer a narrow but decisive question:

**what exact reviewed snapshot is this run allowed to execute against, for how long, and what kinds of drift force re-review instead of reuse?**

## Core decision this page must support

The page must let the product distinguish at least these states:

- plan exists, no reviewed snapshot
- reviewed snapshot exists, not yet bound to commit
- reviewed snapshot bound, freshness window still open
- reviewed snapshot bound, drift check pending
- reviewed snapshot invalidated by material drift
- commit token issued, execute-if-unchanged still true
- commit blocked because same-run proof failed
- commit expired, re-review required

## Minimum fields

### Identity and scope

- action identifier
- successor world identifier
- chosen actuator
- beneficiary slice
- reviewed envelope identifier
- reviewed snapshot identifier
- snapshot creation time
- snapshot scope summary

### Freshness discipline

- freshness window length
- freshness window close time
- allowed same-run reuse count
- whether replay is forbidden
- whether pause/resume preserves or destroys freshness

### Drift invalidators

- approval-state change invalidator
- participant-set change invalidator
- linked-device auto-arrival invalidator
- pending-folder auto-connect invalidator
- permission-state change invalidator
- path or target change invalidator
- rescan-driven content delta invalidator
- settings-save or config-refresh invalidator if relevant
- service-world or runtime-profile change invalidator

### Commit binding

- commit token identifier
- commit token issue time
- commit actor set
- execute-if-unchanged condition set
- mandatory pre-commit checks
- required second look if any
- strongest safe sentence now
- strongest blocked stronger sentence now

## Required layout

### Header

Show:

- action name
- reviewed snapshot identifier
- freshness state
- time remaining
- commit eligibility state

### Left column — what this snapshot covers

Show:

- touched-set summary
- admission and approval summary
- known automatic side-effects summary
- excluded objects or lanes
- runtime world assumptions

### Right column — what would invalidate it

Show:

- drift invalidators
- window expiry rules
- replay rules
- mandatory re-review triggers
- why `same action` can still be a different run

### Footer decision rail

The footer must expose:

- can issue commit token / cannot issue commit token
- execute now / refresh preview / full re-review
- strongest honest sentence now
- strongest blocked stronger no-surprise sentence now

## Hard rules

This page must never collapse:

- `same operator intention` into `same reviewed run`
- `same plan id` into `same snapshot`
- `same snapshot id` into `snapshot still fresh`
- `no alert fired` into `no material drift`
- `commit token exists` into `execute-if-unchanged still true`
