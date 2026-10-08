# Archive-policy change review page — retained-byte loss, replay cost, and surface parity interface spec

## Purpose

This review exists so an operator can change Archive policy without guessing whether the impact is just `keep fewer old files` or something stronger.

It answers:

> if I disable, shorten, or relocate Archive policy here, what recovery bytes disappear, what rename/copy replay degrades, and which surfaces or seats remain stronger than this one afterward?

## Core decision

Every non-trivial Archive mutation must emit one first-class **Archive-policy change review** before apply.

This review is separate from generic preferences because Archive policy can change retention, replay cost, and access parity at once.

## Fixed review order

1. **Change verdict**
2. **Current-vs-proposed policy**
3. **Retained-byte delta**
4. **Replay-cost delta**
5. **Surface and seat parity**
6. **Admissible outcomes**
7. **Receipt promise**

### 1) Change verdict

Show:

- requested change
- strongest honest summary
- whether this is retention-only, replay-affecting, access-affecting, or mixed

Example verdicts:

- `Shortens local retention only; replay basis unchanged`
- `Disables local Archive and weakens remote rename/copy replay on this seat`
- `No practical local delta; this surface never had local Archive access`
- `Android path class blocks Archive here; change is moot locally but still worth recording`

### 2) Current-vs-proposed policy

Show side-by-side rows for:

- current policy state
- proposed policy state
- retention horizon
- local access posture
- replay assistance posture
- strongest safe sentence before and after

### 3) Retained-byte delta

Show:

- bytes or candidate classes expected to stop being retained locally
- whether other seats still retain equivalent witness classes
- whether recovery becomes impossible, indirect, or merely shorter-lived
- whether cleanup is immediate, deferred, or policy-only for future events

### 4) Replay-cost delta

Show:

- current rename/copy replay expectation
- proposed expectation after apply
- whether more fresh transfer becomes likely
- whether the effect is local-only, seat-family-wide, or subject-wide

The operator should be able to answer: **what traffic or latency penalty am I choosing by narrowing Archive here?**

### 5) Surface and seat parity

Show:

- which seats/surfaces can still access Archive directly
- which can only use hidden-path or indirect recovery
- which lose parity after the change
- whether this mutation widens a cross-surface explanation gap

### 6) Admissible outcomes

Good actions include:

- `Keep current policy`
- `Shorten horizon only`
- `Disable locally with replay warning`
- `Move recovery responsibility to named witness seat`
- `Stop — no equivalent witness remains`

Poor actions include:

- `Save`
- `Disable Archive`

when they hide replay and locality consequences.

### 7) Receipt promise

The page must say which receipt will preserve:

- current and proposed policy
- retained-byte delta
- replay-cost delta
- surviving witness seats
- stronger rejected sentence

## Public object

### `archive_policy_change_review`

Fields:

- `archive_policy_change_review_id`
- `subject_ref`
- `requested_change`
- `change_class`
- `current_policy`
- `proposed_policy`
- `retained_byte_delta_rows[]`
- `replay_cost_delta_rows[]`
- `surface_parity_rows[]`
- `recommended_outcomes[]`
- `generated_at`

## Result

A good archive-policy change review prevents five failures:

- shrinking recovery while thinking only about storage
- disabling Archive on the only useful witness seat by accident
- learning rename/copy replay degradation only after re-download begins
- mobile/path-class limits being mistaken for ordinary parity
- later audit losing proof of what the operator consented to
