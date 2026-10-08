# Affected-path continuity page — suspended updates, auto-heal basis, and path-class verdict interface spec

## Purpose

This page answers one ordinary question after the fact:

> which exact paths are still receiving updates, which are frozen or being auto-healed, and why?

The page exists because divergence under non-authority posture is often path-local.
Operators should not have to infer the affected set from missed updates or surprise reversions.

## Core decision

Whenever a non-authority local edit or policy change creates mixed continuity outcomes, the product must render one first-class **Affected-path continuity** page.

The page owns:

- affected path inventory
- continuity verdict per path class
- auto-heal basis
- repair routes
- strongest safe sentence for the subject as a whole

## Fixed page order

1. continuity summary strip
2. path verdict table
3. auto-heal and freeze basis card
4. repair routes card
5. subject-level claim ceiling
6. receipts

### 1) Continuity summary strip

Show:

- subject and seat
- counts for `continuing`, `frozen`, `auto-heal`, `local-only`, `unknown`
- whether the issue is path-local or subject-wide
- one honest next action

### 2) Path verdict table

Each row should show:

- path or path-group label
- triggering local change class
- current verdict (`continuing`, `frozen`, `auto-heal`, `local-only residue`, `blocked`, `unknown`)
- upstream status
- future remote update fate
- data-loss risk
- repair action

Rows may be grouped by pattern if the proof is exact enough, but grouping must never hide a stronger risk class.

### 3) Auto-heal and freeze basis card

This card publishes:

- the rule or posture that caused each verdict
- whether overwrite was optional, enabled by policy, or forced by posture
- whether selective materialization or peer type removed safer alternatives
- whether the verdict is proven or inferred

### 4) Repair routes card

For each affected class, show the least-strong repair route such as:

- preserve local version and reopen on writable seat
- discard local edits and resume upstream continuity
- export local-only additions into explicit unmanaged area
- rebind / reset / rescan after proof-preserving action

### 5) Subject-level claim ceiling

This section must state:

- the strongest safe sentence for the subject overall
- any stronger sentence still unsupported
- whether the subject may still be described as `mirroring`, `protected backup`, `fully current`, or only a narrower statement

### 6) Receipts

Receipts preserve:

- affected set
- verdict classes
- policy basis
- repair route chosen or deferred
- subject-level claim ceiling

## Public object

### `affected_path_continuity`

Fields:

- `affected_path_continuity_id`
- `subject_ref`
- `seat_ref`
- `path_verdicts[]`
- `path_local_or_subject_wide`
- `policy_basis[]`
- `repair_routes[]`
- `subject_claim_ceiling`
- `generated_at`

## Non-negotiable rules

### Rule 1 — path-local freeze must not masquerade as whole-subject health

A subject may still have many healthy paths while some paths are frozen or auto-healed.
The page must show that mixed truth directly.

### Rule 2 — auto-heal must name its basis

If a path reverted, the page must state whether that came from explicit policy, forced posture, or another narrower rule.

### Rule 3 — local-only residue must stay visible

Unsynced additions or preserved local forks must not disappear just because they are outside future upstream continuity.

## Honest outputs

The page may conclude:

- `12 paths continue normally, 3 paths are frozen after local edits, and 2 local additions remain outside upstream continuity.`
- `This seat is currently auto-healing edited managed files because the active posture forces overwrite.`
- `The subject is still receiving upstream changes, but not all managed paths are continuity-clean.`

It may not flatten those outcomes into `share is out of sync`.
