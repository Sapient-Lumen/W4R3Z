# Remedy-hardening-attestation successor preview/commit binding timeline page — preview, refresh, bind, expire, invalidate, and run events

## Purpose

This page records the life of one reviewed snapshot from first preview through binding, refresh, expiry, invalidation, commit, or contradiction.
It exists so the product can tell whether execution relied on a fresh bound preview, a stale preview, a refreshed preview, or a preview that had already been invalidated.

## Required event families

The timeline must support at least these events:

- preview generated
- preview refreshed
- snapshot diff recomputed
- commit candidate marked
- commit token issued
- drift invalidator armed
- drift invalidator fired
- freshness window extended
- freshness window expired
- replay attempted
- second review required
- execute-if-unchanged checks passed
- execute-if-unchanged checks failed
- commit blocked
- execution started against bound snapshot
- post-commit contradiction discovered
- receipt superseded

## Event fields

Each event must preserve:

- timestamp
- actor or system source
- affected invalidator family if any
- before state
- after state
- whether sameness confidence widened or narrowed
- whether a stronger sentence became safe, stayed blocked, or became newly blocked
- linked evidence identifiers

## Timeline views

### Compact rail

Show only:

- preview
- bind
- refresh or expiry
- commit or block
- contradiction or supersession

### Full audit view

Show:

- every refresh
- every invalidator fire
- every token issue or expiry
- every replay attempt
- every sentence upgrade or downgrade

## Mandatory badges

The timeline must surface badges for:

- stale preview risk
- background rescan risk
- remembered-approval drift risk
- linked-device auto-arrival risk
- pending-folder auto-connect risk
- replay blocked
- commit token expired
- no-surprise sentence blocked

## Hard rules

The timeline must never flatten:

- `previewed` into `bound`
- `bound` into `fresh`
- `fresh` into `execute-if-unchanged passed`
- `committed` into `same run proved`
- `no contradiction yet` into `no pre-commit drift occurred`
