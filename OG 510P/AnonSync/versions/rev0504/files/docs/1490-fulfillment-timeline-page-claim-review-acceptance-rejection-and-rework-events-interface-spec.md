# Fulfillment timeline page: claim, review, acceptance, rejection, and rework events interface spec

## Purpose

The timeline preserves the history of completion truth so later operators can answer:

- what was claimed when
- what evidence appeared when
- when review happened
- when acceptance narrowed or widened
- when the return was rejected, superseded, or reopened

## Event model

Supported event classes:

- `mandate-issued`
- `work-started`
- `return-submitted`
- `evidence-attached`
- `review-requested`
- `review-completed`
- `accepted-exact`
- `accepted-partial`
- `disputed`
- `returned-for-rework`
- `superseded-by-newer-return`
- `reopened`
- `residual-duty-cleared`

Hard rule:

A timeline may not skip directly from `mandate-issued` to `closed`.
At least one return or explicit no-return cancellation event must exist.

## Required cards per event

Each event card shows:

- event class
- actor
- source object id
- before sentence
- after sentence
- scope widened or narrowed
- residual duty changed or unchanged

## Timeline summaries

Top summaries must show:

- latest accepted scope
- outstanding residual duties
- number of disputed returns
- whether a stronger completion sentence was ever retracted

## Failure states

If two returns claim the same scope incompatibly, show:

- `Conflicting returns exist; no single completion sentence is currently safe.`
