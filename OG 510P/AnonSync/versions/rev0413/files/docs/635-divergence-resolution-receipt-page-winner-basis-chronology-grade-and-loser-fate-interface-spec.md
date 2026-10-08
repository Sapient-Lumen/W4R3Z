# Divergence-resolution receipt page — winner basis, chronology grade, and loser fate interface spec

## Purpose

This receipt exists so later operators do not have to reconstruct meaning from a live file, a hidden Archive entry, or memory of one `latest` label.

It answers:

> what divergence was resolved here, why did this candidate win, how trustworthy was the chronology, and what happened to the loser?

## Core decision

Every reviewed same-path winner flow must emit one first-class **Divergence-resolution receipt**.

This receipt is separate from generic bind or restore receipts because it preserves the exact claim ceiling for the overloaded `latest` / `winner` seam.

## Receipt fields

### Required top-level fields

- `divergence_resolution_receipt_id`
- `subject_ref`
- `canonical_path`
- `winner_candidate_ref`
- `winner_basis`
- `chronology_grade`
- `timestamp_source_status`
- `loser_candidate_refs[]`
- `loser_fate`
- `commit_outcome`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `completed_at`
- `acted_by`

### Allowed `winner_basis` values

- `strong-authority-proof`
- `guarded-timestamp-order`
- `offline-return-rule`
- `manual-settlement`
- `blocked-no-winner`
- `abandoned-before-apply`

### Allowed `chronology_grade` values

- `high`
- `guarded`
- `low`
- `blocked`

### Allowed `loser_fate` values

- `preserved-in-archive`
- `branched-before-apply`
- `detached-export-created`
- `quarantined-from-live-path`
- `no-extra-preservation`
- `not-reached`

## Fixed receipt order

1. **Outcome strip**
2. **Candidates reviewed**
3. **Chronology evidence used**
4. **Winner basis**
5. **Loser fate**
6. **Safe language**
7. **Next handoff**

### 1) Outcome strip

Show:

- winner basis
- canonical path
- commit outcome (`applied`, `applied-guarded`, `blocked`, `stopped`)
- strongest warning that remained true afterward

### 2) Candidates reviewed

Show:

- candidate labels
- strongest relevant time rows
- whether any candidate arrived through offline return, restore replay, or pre-populated merge

### 3) Chronology evidence used

Show:

- chronology grade
- clock-window posture
- timestamp-source status
- strongest contradiction or invalidator if any

### 4) Winner basis

Show:

- why the winner was allowed to win
- what weaker basis it still relied on
- whether stronger proof was missing

### 5) Loser fate

Show:

- what happened to the loser
- where it can later be found
- whether later replay remains guarded

### 6) Safe language

Always show both:

- strongest safe sentence
- stronger rejected sentence

Example:

- `A guarded timestamp-ranked winner was applied and the losing version was preserved in reviewed Archive scope.`
- `This receipt does not prove that chronology authority was strong enough to call the winner definitively newest.`

### 7) Next handoff

Show:

- later restore/branch review if any
- later chronology retest if any
- later cleanup obligation if any

## Result

A good divergence-resolution receipt prevents five failures:

- `winner applied` becoming the only remembered fact
- guarded timestamp winners looking identical to strong-authority winners later
- loser survival being lost from audit history
- restore/Archive risk being rediscovered only during recovery
- support and future operators having to infer meaning from filesystem fallout and vague history rows
