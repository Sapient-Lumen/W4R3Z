# Storage-only arrival posture page — connected appearance, writeback ceiling, and remedy interface spec

## Purpose

This page answers one ordinary question after arrival:

> this subject looks connected on this seat, but is it really collaborative sync, or is it a storage-only arrival with a narrower writeback contract and a separate repair/remedy path?

The page exists because a storage sink should not need support-article archaeology to remain honest.

## Core decision

Any subject that is present on a seat while lacking ordinary collaborative powers must render one first-class **Storage-only arrival posture** page.

The page owns:

- current presence/connected appearance
- actual writeback ceiling
- destination-side mutation fate
- retention/disconnect meaning
- least-strong remedy if a different posture is wanted

## Fixed page order

1. posture strip
2. presence-versus-collaboration card
3. destination-mutation matrix
4. retention and disconnect card
5. remedy ladder
6. receipts

### 1) Posture strip

Show:

- subject
- seat
- current visible posture: `connected`, `present`, `materialized`, `storage-only`, `read-only-sink`, `unknown`
- writeback ceiling: `none`, `local-only`, `review-required`, `full`, `unknown`
- one honest next action

### 2) Presence-versus-collaboration card

This card publishes:

- whether the subject is present only for storage or backup
- whether destination edits can ever become authoritative
- whether destination deletes can affect the source
- whether `connected` is merely presence language here

The operator must be able to answer: **what kind of connection is this actually?**

### 3) Destination-mutation matrix

Rows:

- edit existing destination file
- add new destination file
- rename destination file
- delete destination file
- disconnect subject
- reconnect subject under new reviewed posture

Columns:

- `current fate`
- `publishes upstream?`
- `retained locally?`
- `needs repair/review?`
- `receipt language`

### 4) Retention and disconnect card

Show:

- what already-landed bytes survive after disconnect
- whether disconnect removes local bytes or only future arrival continuity
- whether disconnect is a posture repair or lineage break
- what other seats still hold the storage copy or authoritative source

### 5) Remedy ladder

This section must sort options from least to most disruptive:

- keep storage-only posture and do nothing
- disconnect and reconnect under reviewed posture
- migrate sink/bind without changing subject purpose
- replace with a collaborative subject if the operator truly wants collaboration

The safest same-subject remedy must sort first.

### 6) Receipts

Receipts must preserve:

- current storage-only posture
- visible connectedness versus actual writeback ceiling
- destination mutation contract
- latest reviewed remedy

## Public object

### `storage_only_arrival_posture`

Fields:

- `storage_only_arrival_posture_id`
- `subject_ref`
- `seat_ref`
- `visible_posture`
- `writeback_ceiling`
- `mutation_rows[]`
- `disconnect_effects[]`
- `remedy_options[]`
- `claim_ceiling`
- `generated_at`

## Non-negotiable rules

### Rule 1 — presence is not collaboration

The page must never let list presence or connected appearance imply bidirectional authority by default.

### Rule 2 — writeback truth must be explicit per mutation class

If some destination-side changes remain local, are reverted, or never publish, the page must state that directly.

### Rule 3 — remedy must not erase why the posture exists

If disconnect/reconnect is offered, the page must still preserve why the current storage-only posture existed in the first place.

## Honest outputs

The page may conclude:

- `Visible posture: connected. Actual contract: storage-only sink with no upstream writeback.`
- `Disconnecting this subject preserves already-landed bytes and only removes future storage continuity on this seat.`
- `Least-strong remedy: reconnect under reviewed posture if collaboration is desired later.`

It may not flatten those truths into `backup folder`, `read only`, or `connected` alone.
