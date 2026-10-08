# Remedy-hardening-attestation successor beneficiary-custody timeline page — hydrate, retain, export, evict, withdraw, and narrow events

## Purpose

This page records the life of one beneficiary-facing result from first usable appearance through hydration, export, local retention, placeholder reversion, source withdrawal, storage cleanup, contradiction, supersession, or final narrowing.
It exists so the product can tell whether a result that was usable also became durably custodied, stayed source-fragile, or later lost custody again.

## Required event families

The timeline must support at least these events:

- beneficiary-usable state bound
- local bytes first materialized
- retention anchor selected
- export or handoff completed
- placeholder reversion requested
- placeholder reversion applied
- source peer lost
- source share disconnected or removed
- local share source removed
- license or topology fragility triggered
- app-storage cleanup or device-local removal observed
- durable custody sentence upgraded
- custody sentence narrowed
- receipt superseded

## Event fields

Each event must preserve:

- timestamp
- actor or system source
- source world
- event family
- touched subject identifier if applicable
- before state
- after state
- whether custody confidence widened or narrowed
- whether a stronger sentence became safe, stayed blocked, or became newly blocked
- linked evidence identifiers

## Timeline views

### Compact rail

Show only:

- beneficiary-usable state bound
- first local-byte event
- first retention-anchor or fragility event
- first custody upgrade
- first later narrowing or supersession

### Full audit view

Show:

- every hydration, export, remove-from-device, placeholder, and cleanup event
- every source-withdrawal, mode-change, and topology-fragility event
- every sentence upgrade or downgrade

## Mandatory badges

The timeline must surface badges for:

- usable only
- source-dependent
- local bytes present
- app-sandbox only
- export completed
- placeholder reverted
- upstream withdrawn
- local copy evicted
- topology fragile
- custody sentence blocked
- receipt superseded

## Hard rules

The timeline must never allow:

- `usable` to silently become `durably custodied`
- `bytes local once` to silently become `retained independently`
- `downloaded into app storage` to silently become `portable custody`
- `recipient got it` to silently become `upstream-independent possession`
