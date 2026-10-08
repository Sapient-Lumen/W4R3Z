# Protection change review page — Recents visibility, external-edit consequences, and lost-secret risk interface spec

## Purpose

This page answers one ordinary question:

> if I enable, disable, or rotate local protection here, what changes in OS visibility, outside-app editing behavior, and local recovery risk?

The page exists because a local-protection change is not only an auth change.
It can also change what the operating system surfaces, what outside apps can do conveniently, and how much local-only data would be at risk if the secret is later forgotten.

## Core decision

Every non-trivial change to local protection must render one first-class **Protection change review** page before commit.
The page owns:

- requested protection delta
- OS-surface visibility delta
- edit-lane delta
- local-only data / reinstall risk delta
- strongest safe sentence after commit

## Primary layout

The page always renders the same regions in the same order:

1. requested protection delta
2. OS visibility delta
3. external-edit delta
4. recovery and lockout delta
5. decision and receipt preview

### 1) Requested protection delta

Show:

- current protection class/state
- requested class/state
- scope affected
- strongest honest summary

The operator must be able to answer: **what protection posture is changing?**

### 2) OS visibility delta

Show:

- whether Files/Recents or equivalent OS recency surfaces will still show these items
- whether provider-backed browsing remains available
- whether app-local visibility is the only remaining route
- whether any existing recency hints may persist transiently after the change

This section must answer: **what OS-level discoverability do I lose or regain?**

### 3) External-edit delta

Show:

- current lane vs resulting lane (`live-provider`, `copy-return`, `copy-branch`, `blocked`, `unknown`)
- whether outside apps continue editing the authoritative bytes or only a copy
- whether duplicate old/new versions may result
- whether return-to-share requires stronger permission than before

This section must answer: **what changes for real editing work, not just viewing?**

### 4) Recovery and lockout delta

Show:

- forgotten-secret consequence before/after
- whether reinstall becomes part of the recovery ladder
- whether local-only bytes are newly at risk
- whether replicated bytes remain safe elsewhere
- whether the product should require a replication check before allowing the change

This section must answer: **what do I risk later if I cannot unlock this seat?**

### 5) Decision and receipt preview

Possible verdicts:

- `apply protection change`
- `apply after replicate local-only bytes`
- `apply with copy-return warning`
- `defer; recovery cliff too high`
- `reject; requested sentence would overclaim privacy or recoverability`

Each verdict must preview the exact receipt sentence.

## Public object

### `protection_change_review`

Fields:

- `protection_change_review_id`
- `seat_ref`
- `subject_scope`
- `current_protection`
- `requested_protection`
- `os_visibility_delta_rows[]`
- `external_edit_delta_rows[]`
- `recovery_delta_rows[]`
- `decision_verdict`
- `receipt_preview`
- `generated_at`

## Non-negotiable rules

### Rule 1 — protection review must not hide productivity consequences

If enabling protection changes Recents visibility or turns a convenient edit path into copy-return ritual, the page must say so.

### Rule 2 — protection review must not hide the lockout cliff

If forgetting the secret can force reinstall or local-only data loss, that must appear before commit rather than only in help text later.

### Rule 3 — recovery safety must be checked, not assumed

If the seat currently holds local-only bytes or unreplicated edits, the product should block or warn before allowing a change that raises recovery risk.

## Honest outputs

The page may conclude:

- `Enabling protection will hide these files from OS Recents on this seat.`
- `Outside-app editing remains possible, but as copy-return rather than guaranteed live-provider editing.`
- `If the local secret is later lost, recovery may require reinstall; replicate local-only bytes first.`

It may not flatten those truths into `enable passcode` or `protect app` alone.
