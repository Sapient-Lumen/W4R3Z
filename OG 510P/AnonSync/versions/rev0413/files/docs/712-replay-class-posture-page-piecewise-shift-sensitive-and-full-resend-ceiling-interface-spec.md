# Replay class posture page: piecewise, shift-sensitive fallback, and resend ceiling interface spec

## Purpose

Give one ordinary page that answers:

> when this subject changes, what replay class is actually active right now, what stronger class is unavailable, and what edit shapes can still force a whole resend?

This page exists because `incremental`, `delta`, `sync changed parts`, and `efficient` are not one honest truth.

## Core rule

Every subject whose future changes may replay over a network must publish a **replay class posture**.
The posture must distinguish at least these classes:

- `full-file replay`
- `piecewise replay`
- `piecewise replay with shift-sensitive fallback`
- `diff-delta replay`
- `local-copy replay`
- `mixed / class may vary by seat`
- `unknown`

A UI may use friendlier labels, but the underlying class must still be inspectable.

## Required sections

### 1) Current replay class

Show:

- current replay class
- strongest class this subject can honestly claim now
- whether the current class is stable or workload-dependent
- strongest safe sentence

Example sentences:

- `Changed content usually replays as changed pieces.`
- `Some edits can still force a whole-file resend because block boundaries shift.`
- `This job currently prefers full resend over local recheck.`
- `A stronger diff-delta class exists elsewhere, but not for this seat/tier.`

### 2) Basis for the class

Show the current reasons:

- edition / runtime capability
- policy flags in force
- hash availability
- rolling-checksum / diff lane availability
- storage / CPU posture if it materially narrows the class
- whether the claim is per-subject, per-seat, or per-job

### 3) Edit-shape ceiling

The operator must see which edits are known to narrow replay quality:

- append-only likely safe for piecewise replay
- in-place change likely safe for piecewise replay
- prefix insert / structural shift may force whole resend
- rename/move may reuse local bytes without network replay
- unclear edit shape means ceiling remains uncertain

### 4) Stronger unavailable class

Show the best counterfactual class that is not available now, and why:

- edition unavailable
- policy disabled
- hashes absent
- rolling/diff lane unavailable
- substrate too slow / too expensive for local recheck
- unknown

### 5) Cost posture

Present a three-axis expectation row:

- network cost tendency (`low`, `mixed`, `high`)
- local CPU/disk cost tendency (`low`, `mixed`, `high`)
- interruption penalty (`resume by pieces`, `whole-file restart risk`, `unknown`)

## Required actions

- `Review replay cost change`
- `Inspect replay evidence`
- `Prefer lower network cost`
- `Prefer lower local recheck cost`
- `Keep current posture`

Never present a toggle like `Use differential replay` without showing the replay class it produces and the whole-resend counterfactual.

## Data model

- `replay_posture_id`
- `subject_id`
- `scope_kind` (`subject`, `job`, `seat`, `pair`)
- `current_replay_class`
- `best_available_replay_class`
- `fallback_replay_class`
- `edit_shape_ceiling[]`
- `basis[]`
- `hash_availability`
- `edition_gate`
- `network_cost_tendency`
- `local_cost_tendency`
- `interruption_penalty`
- `safe_sentence`
- `evidence_ref`
- `last_computed_at`

## Failure this page prevents

Without this page, operators learn too late that `changed parts only` was only true until a piece-shifting edit, a missing-hash seat, or a disabled differential policy turned the next save into a full resend.

AnonSync should instead keep replay class, narrowing basis, and cost posture adjacent before work begins.
