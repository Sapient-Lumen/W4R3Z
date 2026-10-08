# Observation coverage review page — notification capability, blind window, and evidence grade interface spec

## Purpose

The archive already had presence review, topology review, and route evidence.
What it still lacked was the comparison page for this narrower question:

> how much of the subject was actually under timely observation, and what evidence grade supports that claim?

AnonSync should therefore issue a dedicated **observation coverage review** whenever delay, absence, or stale-view language depends on how changes are discovered.

## Review fields

The review must preserve:

- review id
- incident id
- linked detection-posture version
- subject scope
- storage / mount / platform notes
- notification-coverage verdict
- rescan-coverage verdict
- manual-probe availability
- blind-window basis
- observation evidence grade
- strongest allowed sentence
- stronger rejected sentence

## Required sections

### 1) Coverage map

Publish the effective observation map in ordinary language, for example:

- `root tree is notification-backed, but nested network mount falls back to rescans`
- `notification coverage is degraded due to watcher exhaustion`
- `storage class does not support timely notifications; only scheduled/manual discovery is credible`

### 2) Evidence basis

State why the coverage verdict was chosen:

- known platform limitation
- current warning present
- explicit power-user setting
- recent healthy notification witness
- lack of any stronger basis

### 3) Blind-window statement

State the current blind-window shape, for example:

- `up to next scheduled rescan`
- `indefinite until manual rescan or restart`
- `blind window narrowed by healthy notifications`
- `coverage uncertain because posture changed during the incident`

### 4) Stronger rejected claim

State the stronger sentence the review refuses to make.
This is mandatory.

### 5) Cheap next rung

Show the least-strong honest next move:

- wait within declared latency
- run manual rescan as probe
- restore watcher capacity
- revert widened rescan interval
- leave posture as-is but lower freshness claims

## Compact rendering obligations

Any compact rendering must still preserve:

- coverage verdict
- evidence grade
- blind-window label
- strongest allowed sentence
- cheap next rung

## Anti-clone rule

Do not clone views where notification health, rescan fallback, and blind windows remain implicit while the UI still talks as if absence or delay were decisive.
