# Non-authority local-change review page — suspend, auto-heal, or preserve elsewhere interface spec

## Purpose

This page answers one ordinary question:

> I am about to make a local change on a non-authority copy, or enable a policy that will police such changes, so what exactly will freeze, revert, survive locally, or need to be preserved elsewhere first?

The page exists because the danger is not the local edit alone.
The danger is hidden future-update loss or silent destructive reversion.

## Core decision

Before either of these commits, the product must open one first-class **Non-authority local-change review** page:

- a local edit that touches managed bytes on a non-authority seat
- a policy mutation that changes local-edit fate for such bytes

The page owns:

- intended local action
- current posture and continuity rule
- predicted path-class outcome
- preserve / divert options
- post-commit claim ceiling

## Fixed review order

1. intended action strip
2. current posture card
3. predicted-outcome matrix
4. preserve-or-divert card
5. commit review
6. receipt

### 1) Intended action strip

Show:

- subject and seat
- intended local action
- relevant path set
- current local-edit mode
- top-level risk class: `safe`, `guarded`, `destructive`, `blocked`

### 2) Current posture card

This card publishes:

- authority grade
- current continuity mode
- whether auto-heal is disabled, optional, or forced
- whether selective materialization or other posture constraints narrow options

### 3) Predicted-outcome matrix

Rows should cover the affected path classes.
Columns should include:

- intended change class
- upstream propagation
- future update continuity
- auto-heal / revert behavior
- local residue fate
- proof lost if committed

The operator must be able to answer: **what exactly happens to these paths if I continue?**

### 4) Preserve-or-divert card

Offer typed alternatives such as:

- preserve copy outside managed lane
- convert to explicit fork / branch / exported work area
- keep change but accept frozen continuity
- enable auto-heal and treat local edits as disposable
- cancel and edit on an authority-bearing seat instead

This card must state which alternative is the least destructive.

### 5) Commit review

This section publishes:

- actual commit being approved
- strongest safe sentence afterward
- stronger unsupported sentence
- required repair if continuity will freeze

### 6) Receipt

The receipt preserves:

- intended action
- posture in force
- predicted path-class outcome
- preserve/divert option shown
- actual committed choice
- claim ceiling

## Public object

### `non_authority_local_change_review`

Fields:

- `non_authority_local_change_review_id`
- `subject_ref`
- `seat_ref`
- `intended_action`
- `affected_paths[]`
- `authority_grade`
- `continuity_mode`
- `auto_heal_mode`
- `predicted_outcomes[]`
- `preserve_or_divert_options[]`
- `committed_choice`
- `claim_ceiling`
- `generated_at`

## Review rules

### Rule 1 — destructive auto-heal must be reviewed as destruction

If enabling or relying on auto-heal can overwrite local edits, the page must present that as destructive, not routine synchronization hygiene.

### Rule 2 — frozen continuity must be reviewed as future loss, not just current success

A local save that looks successful now may still suspend future remote updates for that path.
The page must publish that future cost.

### Rule 3 — preserve elsewhere must be first-class

When the safest route is to move work outside the managed lane or to a writable seat, the page must show that route before commit.

## Honest outputs

The page may conclude:

- `Continuing here will keep the local rename, but future remote continuity for the managed path will stop until repaired.`
- `With auto-heal enabled, this edited file is expected to revert to upstream state. Preserve a copy elsewhere first if the local version matters.`
- `This posture cannot offer the safer selective materialization route on this seat.`

It may not flatten those outcomes into `changes may be lost`.
