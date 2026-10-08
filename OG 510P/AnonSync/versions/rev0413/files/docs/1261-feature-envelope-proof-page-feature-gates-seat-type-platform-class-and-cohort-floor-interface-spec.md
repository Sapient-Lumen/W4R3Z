# Feature envelope proof page: feature gates, seat type, platform class, and cohort floor interface spec

## Purpose

The capability-floor sheet says what the group can safely claim.
This page proves *why* a given feature claim is allowed, degraded, or blocked.

## Core decision

AnonSync must require a **Feature envelope proof** whenever a feature claim could be misunderstood because of:

- version mismatch
- platform mismatch
- personal vs business lane split
- paid / entitled vs general availability split
- linked-family mixed-major risk

## Proof layout

1. **Feature headline**
2. **Gate stack**
3. **Per-member satisfaction table**
4. **Cohort claim verdict**
5. **Blocked stronger sentence**

### 1) Feature headline

Show:

- feature name
- current claim verdict
- strongest safe sentence
- blocked stronger sentence
- proof freshness

### 2) Gate stack

Supported gate classes:

- `version-gate`
- `license-or-entitlement-gate`
- `platform-gate`
- `product-lane-gate`
- `linked-family-safety-gate`
- `unknown-gate`

The operator must be able to answer:

> what kinds of conditions stand between this feature and a truthful cohort-wide claim?

### 3) Per-member satisfaction table

Each row must show:

- member ref
- version satisfaction
- platform satisfaction
- seat/lane satisfaction
- safety satisfaction
- final contribution (`supports`, `degrades`, `blocks`, `unknown`)

### 4) Cohort claim verdict

Supported verdicts:

- `claim-safe-cohort-wide`
- `claim-safe-only-on-subset`
- `blocked-by-one-governing-member`
- `blocked-by-lane-split`
- `blocked-by-platform-floor`
- `blocked-by-admin-safety-floor`

Each verdict must print one exact sentence suitable for UI reuse.

### 5) Blocked stronger sentence

Examples:

- `Selective Sync is safe to claim cohort-wide` blocked because one v2 member lacks the required entitlement
- `v3 management features are safe cohort-wide` blocked because one Business/NAS member must stay on v2
- `all linked devices are safely on one major` blocked because mixed-major linking risk remains

## Hard rules

- feature availability on one member may never silently imply cohort availability
- the proof must name the governing blocker, not just mark the feature unavailable
- entitlement and platform blockers must stay distinct
- the interface must preserve the difference between `bytes still sync` and `this feature is safe to roll out`
