# Decision chronology evidence page — clock window, mtime source, and ranking strength interface spec

## Purpose

General clock health is not enough for a concrete overwrite or restore decision.
This page owns the narrower question:

> for this exact winner/restore/merge decision, what chronology evidence is actually being used, how strong is it, and what would invalidate it?

This page exists because `clock warning`, `mtime`, `database timestamp`, and `latest file that came online` are not the same evidence class.

## Core decision

Whenever a current ranking or restore claim depends materially on chronology, the product must provide one first-class **Decision chronology evidence** page.

This page may be linked from the general clock-authority page and mtime-integrity page, but it must stay decision-local.

## Fixed page order

1. **Decision scope strip**
2. **Clock window card**
3. **Timestamp source card**
4. **Candidate timeline card**
5. **Ranking strength card**
6. **Invalidators and retest card**

### 1) Decision scope strip

Show:

- reviewed path or restore candidate
- reviewed action (`merge`, `overwrite`, `replay`, `restore`, `branch`, `block`)
- current chronology verdict
- one next honest action

### 2) Clock window card

Show:

- relevant peers/seats
- observed skew or time-zone concerns
- policy window in force
- whether the window is satisfied, guarded, or failed
- whether chronology-sensitive actions remain admissible

The operator should be able to answer: **are the clocks trustworthy enough for this decision?**

### 3) Timestamp source card

Show:

- which timestamp source is currently authoritative for each candidate: `disk`, `database`, `mixed`, `unknown`
- whether assignment fidelity is known to be degraded
- whether Archive placement time is being shown instead of original authored time
- which surfaces may still show weaker timestamp truth than the decision engine

The operator should be able to answer: **which timestamp source is this ranking actually trusting?**

### 4) Candidate timeline card

Show:

- authored time
- last observed time
- return/rediscovery time if relevant
- archive-placement time if relevant
- gaps or contradictions between those times

The operator should be able to answer: **which timeline is actually in play here?**

### 5) Ranking strength card

Show:

- current ranking strength (`strong`, `guarded`, `weak`, `blocked`)
- strongest rule being used (`content-authority`, `timestamp-order`, `offline-return-order`, `manual`, `none`)
- whether another equally plausible ranking exists
- whether the product recommends settlement instead of automatic apply

The operator should be able to answer: **how defensible is the current ranking?**

### 6) Invalidators and retest card

Show:

- what would invalidate the ranking now (clock repair failure, fresh scan, new source peer, mtime integrity repair)
- minimum retest proving stronger chronology confidence
- whether apply should be delayed until retest

The operator should be able to answer: **what smallest new evidence would change this decision?**

## Public object

### `decision_chronology_evidence`

Fields:

- `decision_chronology_evidence_id`
- `subject_ref`
- `action_kind`
- `peer_time_window_status`
- `peer_skew_rows[]`
- `timestamp_source_rows[]`
- `candidate_timelines[]`
- `ranking_strength`
- `ranking_rule`
- `invalidators[]`
- `retest_requirements[]`
- `generated_at`

## Result

A good decision chronology page prevents five failures:

- global clock health being mistaken for decision-local chronology proof
- database-versus-disk timestamp splits staying invisible at overwrite time
- archive-placement time being mistaken for original authored time
- offline-return order being mistaken for ordinary chronology order
- later operators losing the exact evidence strength behind a guarded winner
