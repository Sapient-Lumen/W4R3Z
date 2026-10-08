# Retention/replay dependence page — archive policy, remote rename-copy, and recovery scope interface spec

## Purpose

This page owns the next question after an operator inspects or is about to touch Archive policy:

> what does Archive currently do for this subject besides keeping old bytes, and what would become weaker if I narrowed or disabled it here?

This page exists so `Use Archive` never substitutes for a real contract.

## Core decision

Any share, subject, or seat where archive-bearing policy materially affects rollback, rename/copy replay, or local access must create one first-class **Retention/replay dependence** page.

The page is required whenever Archive policy might otherwise be mistaken for retention-only behavior.

## Fixed page order

1. **Dependence verdict strip**
2. **Current archive-bearing benefits**
3. **Seat-local access ceiling**
4. **Replay dependence map**
5. **Mutation sensitivity**
6. **Receipt promise**

### 1) Dependence verdict strip

Show:

- reviewed subject or share
- current archive policy state
- dependence verdict
- strongest safe sentence

Example verdicts:

- `Archive currently supports rollback and rename replay on this seat`
- `Archive narrows recovery locally; replay help still comes from another seat`
- `Archive is enabled but locally inaccessible on this surface`
- `Archive disabled; remote rename/copy will re-download here`

### 2) Current archive-bearing benefits

Always distinguish at least these benefit classes:

- `retained-prior-version`
- `local-delete-undo-witness`
- `rename-replay-assistance`
- `copy-replay-assistance`
- `none-proved`

For each class, show:

- whether it is active now
- which policy enables it
- whether the benefit is local to this seat or depends on some other witness seat
- strongest known limit

### 3) Seat-local access ceiling

Show:

- whether Archive can be opened locally from this surface
- whether the current platform/path class limits Archive operation
- whether retention exists but access is indirect, hidden-path only, or unavailable
- whether this seat is a true recovery witness or only a participant that might consume another witness later

The operator should be able to answer: **what can I actually recover from here without moving to another seat or surface?**

### 4) Replay dependence map

Show whether remote rename/copy behavior currently depends on Archive-backed local reuse.

Required rows:

- `remote rename → local rename replay or re-download`
- `remote copy → local copy replay or re-download`
- `restore candidate → local replay or guarded/none`

For each row show:

- current expected result
- current evidence basis
- what policy/state would weaken it

### 5) Mutation sensitivity

Show what changes if Archive policy is shortened, disabled, or moved to a weaker surface/path class.

Minimum deltas:

- retained-byte horizon change
- local access change
- remote replay-cost change
- stronger forbidden sentence after change

### 6) Receipt promise

The page must say which receipt will preserve:

- reviewed policy state
- replay dependence rows
- local access ceiling
- stronger rejected sentence

## Public object

### `retention_replay_dependence_page`

Fields:

- `retention_replay_dependence_page_id`
- `subject_ref`
- `archive_policy_state`
- `dependence_verdict`
- `benefit_rows[]`
- `access_ceiling_rows[]`
- `replay_rows[]`
- `mutation_sensitivity_rows[]`
- `generated_at`

## Result

A good retention/replay dependence page prevents five failures:

- `Use Archive` masquerading as retention-only
- local access limits being rediscovered only during recovery
- rename/copy replay degradation being learned after traffic spikes
- another seat silently holding the only useful witness
- later operators losing proof of what the toggle actually changed
