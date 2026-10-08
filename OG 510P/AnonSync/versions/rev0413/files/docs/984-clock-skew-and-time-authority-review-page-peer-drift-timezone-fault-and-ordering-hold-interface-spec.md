# Clock-skew and time-authority review page — peer drift, timezone fault, and ordering hold

## Purpose

Make chronology degradation reviewable before operators act on overwrite, replay, or freshness claims.

This page answers:

> which peers or seats are making time-based ordering unsafe, what kind of fault is it, and what chronology-dependent actions are now being held or downgraded?

## Primary layout

1. current chronology posture
2. drift roster
3. fault classifier
4. held decisions
5. repair ladder
6. pending receipt

### 1) Current chronology posture

Show:

- `trusted`, `guarded`, `quarantined`, or `clock-blind`
- active skew budget
- whether timezone or raw clock skew is the main failure class
- whether automatic ordering is still allowed

### 2) Drift roster

For each relevant peer/seat show:

- seat name
- observed drift from quorum
- timezone confidence
- last sampled at
- participation verdict: `full`, `guarded`, `excluded`

### 3) Fault classifier

Classify the issue as one or more of:

- timezone mismatch
- raw wall-clock skew
- unknown clock source
- stale validation sample
- ledger-vs-disk mismatch only

### 4) Held decisions

Show which actions are currently degraded or blocked:

- latest-wins overwrite
- completion/freshness claims
- replay from retention
- conflict auto-pick
- rename chronology inference

### 5) Repair ladder

Offer only typed next actions:

- `Repair time settings on peer`
- `Repair timezone labeling`
- `Exclude peer from chronology decisions temporarily`
- `Hold restore / overwrite until revalidated`
- `Revalidate now`

### 6) Pending receipt

Preview what the later receipt will preserve:

- pre-review confidence class
- affected peers
- held actions
- stronger rejected sentence

## Mandatory fields

- review identifier
- drift roster
- skew budget
- fault classes
- held actions
- requested repair action
- stronger rejected sentence

## Interaction rules

- The page must differentiate `peer is offline` from `peer is unsafe for chronology`.
- `Empty folder` or `no files shown` must never be the only indication of a time-authority fault.
- Any approval to continue in guarded mode must carry a short expiry and produce a receipt.
