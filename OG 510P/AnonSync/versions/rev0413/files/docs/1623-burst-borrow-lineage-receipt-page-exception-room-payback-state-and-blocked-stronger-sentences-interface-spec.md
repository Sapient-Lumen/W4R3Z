# Burst borrow lineage receipt page — exception room, payback state, and blocked stronger sentences

## Purpose

This receipt is the stable handoff object for the truth about temporary borrowed room.
It preserves not just that the claimant was active and out of ordinary envelope, but whether extra room was lawfully borrowed, from where, until when, with what harm, and whether reserve and claimants were later repaid or restored.

## Required fields

### Identity

- contention case id
- winning claimant id
- receipt issue time
- ordinary award amount
- borrowed extra-room amount if any
- current exception class

### Current strongest true sentence

One of:

- `ordinary-envelope-only`
- `active-with-valid-burst-borrow`
- `active-with-valid-protected-reserve-borrow`
- `active-beyond-exception-limit`
- `exception-expired-payback-open`
- `exception-withdrawn-throttle-back-applied`
- `payback-complete-ordinary-entitlement-restored`
- `exception-failed-contention-reopened`

### Basis block

- authority basis
- borrowed-room source
- expiry or renewal state
- harmed-claimant set
- reserve impact yes/no
- payback due time
- next forced review

### Consequence block

- strongest blocked claimant sentence
- strongest blocked harmed-neighbor sentence
- unpaid payback yes/no
- future exception authority narrowed yes/no
- stronger sentence unavailable and why

## Receipt obligations

- keep ordinary entitlement, temporary exception, and payback truth separate
- preserve protected-reserve borrow as public truth rather than private operator commentary
- show expiry, renewal, withdrawal, and payback completion as typed outcomes
- preserve blocked stronger sentences for both claimant and harmed neighbors
- remain readable without the full timeline open

## Stronger-sentence guard

The receipt may say `this claimant borrowed extra room under typed temporary authority`.
It may not say `this claimant now owns the extra room` or `all harm is cleared` unless the current basis supports that stronger sentence.