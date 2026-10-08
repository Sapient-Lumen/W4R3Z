# Convergence timeline page: wave entry, reconciliation, settlement, and straggler events interface spec

## Purpose

The archive already had subject timelines.
Once settlement becomes a campaign, it also needs one timeline that shows how the wave evolved, when its claim ceiling changed, and which stragglers kept the broader sentence blocked.

## Timeline promise

This page must answer:

> how did this settlement wave evolve over time, when did subjects enter or fall out, when did the claim narrow or upgrade, and what events kept full success blocked?

## Event families

### 1) Campaign-shape events

Supported values:

- `campaign-created`
- `cohort-expanded`
- `cohort-trimmed`
- `route-changed`
- `safety-fence-armed`

### 2) Subject-settlement events

Supported values:

- `subject-routed-to-restore`
- `subject-routed-to-successor`
- `subject-routed-to-reopen`
- `subject-restored-exactly`
- `subject-promoted-to-successor`
- `subject-kept-temporary`
- `subject-dropped-from-wave`

### 3) Risk and claim events

Supported values:

- `merge-risk-discovered`
- `overwrite-risk-blocked`
- `claim-frozen`
- `bounded-claim-published`
- `broader-claim-unblocked`
- `campaign-aborted`

### 4) Straggler events

Supported values:

- `straggler-created`
- `straggler-expiry-near`
- `straggler-reassigned`
- `straggler-reopened`
- `straggler-settled`

## Required timeline controls

The page must let operators filter by:

- subject
- route
- settlement class
- claim effect
- straggler state
- time window

## Required summary rail

Pinned above the timeline:

- current strongest safe sentence
- broader blocked sentence
- number of uncovered subjects
- next campaign gate
- whether the campaign is still safe to widen

## Explicit anti-goals

Do not:

- show only task completion events
- hide claim-freeze or claim-upgrade moments
- collapse subject settlement and cohort settlement into one timestamp
- let straggler creation disappear after a later bounded win

## Why this page exists

Because settlement campaigns are as much about preserving truthful claim evolution as they are about recording the mechanical fixes.
