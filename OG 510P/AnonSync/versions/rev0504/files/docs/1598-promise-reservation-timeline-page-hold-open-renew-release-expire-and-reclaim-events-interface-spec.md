# Promise reservation timeline page: hold open, renew, release, expire, and reclaim events interface spec

## Purpose

The operator needs one durable timeline that shows how future room changed hands over time and when reservation debt accumulated or cleared.

## Core decision

AnonSync must expose one **Promise reservation timeline** page whenever holds, renewals, releases, or reclaims materially affect what promises could honestly be issued.

## Event families

Supported reservation timeline events:

- `hold-opened`
- `hold-upgraded`
- `hold-downgraded`
- `hold-renewed`
- `release-trigger-fired`
- `hold-released`
- `expiry-crossed`
- `ghost-risk-opened`
- `reclaim-started`
- `reclaimed`
- `override-used`
- `blocked-promise-attempt`

## Required columns

- event time
- reservation id
- actor or system source
- prior hold class
- new hold class
- scope changed or not
- expiry changed or not
- blocked stronger sentence changed or not
- reclaim risk changed or not
- note on why this event mattered

## Timeline behaviors

### A) Upgrade and downgrade must both stay visible

A soft hold turning into a hard reservation is not cosmetic.
Neither is a hard reservation degrading to option-only or expired-risk status.

### B) Expiry without reclaim is its own event

The page must not silently mutate `active` into forgotten absence.
Crossing the expiry boundary is a first-class change in truth.

### C) Reclaim must preserve the reason

When a ghost or stale hold is reclaimed, the operator must still be able to see whether it expired, was duplicated, lost ownership, or was released because the future need vanished.

### D) Blocked promise attempts belong on the timeline

If a stronger promise could not be issued because future room was already held, the blocked attempt is part of lineage.
Otherwise the opportunity cost of the hold disappears.

## Timeline summary footer

The page must end with:

- current live hold count
- current ghost-hold count
- most recent reclaim event
- strongest currently blocked promise due to reservations
- next expiry or review event
