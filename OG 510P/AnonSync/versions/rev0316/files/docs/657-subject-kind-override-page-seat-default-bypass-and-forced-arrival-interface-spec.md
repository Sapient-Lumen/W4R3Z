# Subject-kind override page — seat-default bypass and forced-arrival interface spec

## Purpose

This page answers one ordinary question:

> does this subject obey the seat's standing arrival default, or is the subject kind itself overriding that default with a different arrival, role, and writeback contract?

The page exists because `connected`, `backup`, `capture`, `storage-only`, and `seat default` are not interchangeable.
The operator needs one direct statement of whether a subject-kind carve-out is in force.

## Core decision

Every subject-seat pair whose effective posture differs from the seat's standing arrival default must render one first-class **Subject-kind override** page.
The page owns:

- standing seat default in scope
- subject kind and its override basis
- effective arrival/materialization posture now
- effective writeback and role ceiling
- strongest safe sentence for this subject on this seat

## Primary layout

The page always renders the same regions in the same order:

1. override strip
2. standing-default card
3. subject-kind contract card
4. effective-posture matrix
5. remedy and containment card
6. receipts

### 1) Override strip

Show:

- subject label
- seat label
- standing seat default: `disconnected`, `announced-only`, `selective`, `materialized`, `unknown`
- effective subject posture now: `disconnected`, `placeholder`, `materialized-storage-only`, `materialized-collaborative`, `opaque-custody`, `unknown`
- override status: `none`, `subject-kind-bypass`, `policy-exception`, `manual-repair`, `unknown`
- one honest next action

### 2) Standing-default card

This card publishes:

- the seat's current future-arrival default
- what that default ordinarily means for new subjects
- whether the default was advisory, strict, or already exception-bearing
- what stronger sentence the operator might otherwise have assumed

The operator must be able to answer: **what would have happened here without a subject-kind carve-out?**

### 3) Subject-kind contract card

This card publishes:

- subject kind: `collaborative-sync`, `capture-ingest`, `storage-only-backup`, `opaque-custody`, `other`
- why this subject kind is permitted to override the standing default
- whether the subject is intended for collaboration, storage, custody, or one-way ingest
- whether destination-side edits can publish back at all
- whether `connected`/`present`/`active` language would overstate the contract

The operator must be able to answer: **what contract is stronger than the seat default here?**

### 4) Effective-posture matrix

Render rows for these capability families:

- appears in folder list
- auto-arrives despite seat default
- materializes bytes automatically
- accepts local destination edits as authoritative
- publishes destination edits upstream
- requires disconnect/reconnect to reassert an alternate posture

Columns:

- `current yes/no`
- `basis`
- `subject-kind dependent?`
- `least-strong remedy`
- `receipt language`

The product must not compress these rows into one `connected` badge.

### 5) Remedy and containment card

This card publishes:

- whether the subject kind may be narrowed back toward the seat default
- whether that requires disconnect/reconnect/manual bind/manual review
- whether any remedy changes lineage or only posture
- whether the exception should stay subject-local or teach a broader policy

The operator must be able to answer: **how do I contain or repair this override without lying about the subject?**

### 6) Receipts

Show the latest override receipt, reviewed remedies, and whether the current contract is native or workaround-shaped.

## Public object

### `subject_kind_override_explainer`

Fields:

- `subject_kind_override_explainer_id`
- `subject_ref`
- `seat_ref`
- `standing_default`
- `subject_kind`
- `effective_posture`
- `override_status`
- `basis_rows[]`
- `remedy_options[]`
- `claim_ceiling`
- `generated_at`

## Non-negotiable rules

### Rule 1 — standing default remains visible even when it loses

If the subject kind bypasses the seat default, the page must still show the default that was outridden.

### Rule 2 — connected appearance must never outrun writeback truth

If the subject appears present or connected but is storage-only or non-collaborative, the page must publish that directly.

### Rule 3 — repair ritual must remain second-order

If the only way to restore the intended posture is disconnect/reconnect or another ritual, that is a remedy, not the contract itself.

## Honest outputs

The page may conclude:

- `Standing default: disconnected. Effective posture: materialized storage-only. Override basis: subject kind requires backup storage arrival on this seat.`
- `This subject appears connected on the seat, but destination edits are non-authoritative and do not publish upstream.`
- `Least-strong remedy: disconnect this subject and reconnect under reviewed posture without changing subject lineage.`

It may not flatten those truths into `connected`, `backup on`, or `mode mismatch` alone.
