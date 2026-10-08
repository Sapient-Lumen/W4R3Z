# Remedy-hardening-attestation successor beneficiary-adoption timeline page — correction seen, acknowledged, opened, switched, retired, and relapsed events

## Purpose

This page records the life of one beneficiary-facing correction from notice through acknowledgement, fetch, open, working-state switch, stale-state retirement, relapse, or supersession.
It exists so the product can tell not just whether a correction was observed, but how far it actually traveled into the beneficiary's real working behavior.

## Required event families

The timeline must support at least these events:

- correction published
- correction surfaced
- beneficiary likely saw correction
- acknowledgement requested
- acknowledgement completed
- corrected artifact fetched or hydrated
- corrected artifact opened
- working pointer switched to corrected artifact
- stale artifact marked risky
- stale artifact retired
- downstream pointer switched
- stale artifact reopened or reused
- relapse detected
- compliance attested for named slice
- correction superseded
- receipt superseded

## Event fields

Each event must preserve:

- timestamp
- actor or system source
- source world
- event family
- touched beneficiary / correction / artifact / slice identifier
- before state
- after state
- whether uptake confidence widened or narrowed
- whether a stronger sentence became safe, stayed blocked, or became newly blocked
- linked evidence identifiers

## Timeline views

### Compact rail

Show only:

- correction surfaced
- acknowledgement completion if any
- first fetch/open event
- first working-pointer switch event
- first stale-retirement or relapse event
- current strongest sentence

### Full audit view

Show:

- every notice, acknowledgement, fetch, open, switch, stale-risk, retirement, relapse, supersession, and sentence-upgrade or downgrade event

## Mandatory badges

The timeline must surface badges for:

- correction seen
- acknowledged
- opened only
- working switch likely
- stale reliance open
- stale reliance retired
- relapse detected
- compliance narrow
- stronger compliance blocked
- receipt superseded

## Hard rules

The timeline must never allow:

- `acknowledged` to silently become `adopted`
- `opened corrected artifact` to silently become `working pointer switched`
- `one stale artifact retired` to silently become `all stale reliance ended`
- `compliance attested for one slice` to silently become `global compliance achieved`
