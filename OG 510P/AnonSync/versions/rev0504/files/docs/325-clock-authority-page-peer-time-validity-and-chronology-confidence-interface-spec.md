# Clock authority page: peer time validity and chronology confidence interface spec

## Purpose

This page answers one ordinary question:

> are the clocks and time-zone claims in this cohort trustworthy enough for chronology-sensitive decisions, and if not, what exactly is blocked or degraded right now?

The page exists because `time warning`, `invalid timezone`, and `clock difference exceeds policy` are not the same truth.

## Core decision

Every seat must render one first-class **Clock authority** page.
That page owns:

- local clock and time-zone posture
- peer skew verdicts
- chronology-confidence grade
- consequences of invalid time
- least-destructive repair order

The workbench must not force the operator to infer chronology safety from an empty list, a stalled transfer, or a tiny warning row.

## Primary layout

The page always renders the same regions in the same order:

1. cohort strip
2. local time basis card
3. peer skew card
4. chronology-confidence card
5. consequence and repair card
6. clock receipts

### 1) Cohort strip

Show:

- seat label
- affected share or peer cohort
- current verdict: `clock-safe`, `timezone-suspect`, `skewed`, `blocked-by-time`, `ambiguous-time-authority`
- one next honest action

### 2) Local time basis card

This card publishes:

- local wall clock
- local UTC value
- time-zone identity
- whether time and time zone are automatic, manual, or unknown
- last trusted observation time

The operator must be able to answer: **what time basis is this seat actually using?**

### 3) Peer skew card

This card publishes:

- each relevant peer
- observed UTC delta
- whether the problem appears to be raw clock skew, time-zone error, or unknown
- policy window in force
- whether the peer is still chronology-admissible

The operator must be able to answer: **which peer is outside the trusted window, and by how much?**

### 4) Chronology-confidence card

This card publishes:

- current chronology-confidence grade: `high`, `guarded`, `low`, `blocked`
- what decisions are degraded: transfer, listing, replay ranking, restore confidence, merge ranking
- whether any mobile or narrow surface is falling back to empty-list behavior
- what evidence still remains trustworthy despite the skew

The operator must be able to answer: **what can I still trust while time authority is weak?**

### 5) Consequence and repair card

This card publishes:

- direct consequences now in force
- the least-destructive repair ladder
- whether fixing local zone/clock is sufficient or all peers require correction
- the minimum retest that proves chronology safety is restored

The operator must be able to answer: **what exactly breaks, and what is the smallest fix that proves the cohort is safe again?**

### 6) Clock receipts

Receipts show:

- chronology warnings issued
- clock/time-zone changes acknowledged
- retests performed
- restored chronology-confidence verdicts

## Non-negotiable rules

### Rule 1 — skew must not hide behind generic sync failure

Time authority failure is its own family and must stay named.

### Rule 2 — chronology confidence must be explicit

The page must say whether chronology-sensitive actions are trusted, guarded, or blocked.

### Rule 3 — repair must start with time basis, not with byte repair

The product must not jump straight to re-sync, restore, or overwrite actions before the time basis is trustworthy.

## Honest outputs

The page may conclude:

- `Peer clock skew exceeds the allowed window; transfer and chronology ranking are blocked until UTC/time-zone posture is repaired.`
- `Observed problem looks like time-zone mismatch rather than raw clock drift; repair the peer's zone setting before retrying sync.`
- `Transfers are paused for chronology safety; empty mobile listing is a consequence of the same time-authority failure.`

It may not collapse those outcomes into one generic `sync issue` badge.
