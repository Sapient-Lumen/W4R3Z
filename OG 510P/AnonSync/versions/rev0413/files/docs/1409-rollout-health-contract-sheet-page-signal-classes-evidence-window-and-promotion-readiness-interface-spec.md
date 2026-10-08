# Rollout-health contract sheet page: signal classes, evidence window, and promotion readiness interface spec

## Purpose

The archive already has pages for rollout structure, readiness gates, stop conditions, and rollback class.
What it still lacked was one ordinary page for the narrower question:

> given the evidence we have right now, is this rollout actually healthy enough to widen, and what exactly is that judgment based on?

Current official Resilio docs make this seam concrete.
They separately describe real-time performance graphs, peer-table details, Status warnings, Sync History checks, warning KB pages, hidden background work, debug-log collection, profiler capture, and changelog-known issues.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Rollout-health contract sheet** whenever a rollout has moved beyond purely planned state or when any promotion, freeze, hold, or rollback decision depends on observed health evidence.

The sheet exists to answer nine things in one place:

1. which rollout and ring boundary this health judgment belongs to
2. which evidence window is in scope
3. which signal classes are present
4. which symptoms are adjudicated as real, transient, structural, or unknown
5. which likely-cause classes are in play
6. what freshness grade the evidence deserves
7. what promotion-confidence grade currently applies
8. what action is allowed now
9. what stronger sentence remains blocked

## Fixed page order

1. **Health header**
2. **Evidence-window card**
3. **Signal inventory card**
4. **Adjudication card**
5. **Promotion-confidence card**
6. **Blocked stronger sentence**

### 1) Health header

Show at minimum:

- `rollout_health_id`
- rollout id
- policy family / successor revision
- focused ring boundary
- strongest safe sentence
- blocked stronger sentence
- current promotion-confidence grade
- last adjudicated time

Supported headline states must include:

- `green-promotable`
- `guarded-promotable`
- `hold-pending-more-evidence`
- `freeze-now`
- `rollback-now`
- `unknown`

Example safe sentence:

- `Canary health is currently green-promotable for pilot expansion, but broad promotion remains blocked because signal coverage is fresh only for desktop lanes and host-load attribution remains unresolved on one service cohort.`

### 2) Evidence-window card

Show explicit rows for at least:

- observation start time
- observation end time
- ring / cohort covered
- product version window
- host/platform window
- freshness grade
- missing windows if any

Supported freshness grades must include:

- `live-current`
- `recent-enough`
- `stale-but-still-informative`
- `too-stale-for-promotion`
- `unknown`

The operator must be able to answer:

> how recent is this judgment, and which cohort/time window does it really cover?

### 3) Signal inventory card

Supported signal classes must include:

- `live-metric`
- `warning-or-status`
- `history-event`
- `queue-observation`
- `support-artifact`
- `known-issue-prior`
- `operator-note`
- `unknown`

Each signal row must show:

- signal class
- source surface
- freshness
- affected cohort
- whether it is adjudicated yet
- whether it raises, lowers, or leaves unchanged promotion confidence

The operator must be able to answer:

> what evidence types are we actually relying on right now?

### 4) Adjudication card

Separate these verdict classes explicitly:

- `transient-symptom`
- `structural-symptom`
- `host-load-only`
- `product-regression-likely`
- `mixed-causality`
- `insufficient-evidence`
- `recovered-but-unexplained`
- `unknown`

Every adjudication row must show:

- verdict
- supporting signals
- opposing signals
- likely-cause class
- affected rings
- promotion consequence

Likely-cause classes must include:

- `product-change`
- `host-environment`
- `network-path`
- `storage-pressure`
- `version-known-issue`
- `operator-action`
- `mixed`
- `unknown`

The operator must be able to answer:

> what do we think is happening, how sure are we, and what rollout action follows from that?

### 5) Promotion-confidence card

Supported confidence outcomes must include:

- `green-promotable`
- `guarded-promotable`
- `hold-pending-more-evidence`
- `freeze-now`
- `rollback-now`
- `unknown`

Each row must show:

- confidence outcome
- covered rings
- required next action
- missing evidence still needed
- stronger sentence blocked by current uncertainty

The operator must be able to answer:

> can we widen, must we hold, or do we need to freeze or roll back?

### 6) Blocked stronger sentence

Examples:

- `Pilot expansion is broadly safe` blocked because the evidence window covers only 10 minutes and lacks fresh service-cohort logs.
- `No meaningful regression remains` blocked because symptoms recovered but root cause is still unproven.
- `Observed degradation is product-caused` blocked because host-load evidence remains stronger than product-only evidence.

## Hard rules

- graphs alone must never determine promotion confidence
- one warning article must never stand in for adjudicated root-cause truth
- support artifacts must never bypass adjudication
- stale evidence must never authorize broader promotion without explicit exception handling
- recovered symptoms must never overclaim resolved root cause
- confidence grade must never sound stronger than the evidence window actually supports
