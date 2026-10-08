# Return-to-protection contract sheet page: intended restoration, structural delta, and return class interface spec

## Purpose

After the archive learned how to suspend a control truthfully, it still needed one ordinary page for the next operator question:

> now that we want protection back, what exact state are we trying to restore, what changed while the bypass was active, and what kind of return are we actually performing?

## Core decision

AnonSync must expose one first-class **Return-to-protection contract sheet** whenever an operator ends, narrows, or reverses a bypass and wants a control, path, permission, or policy effect back.

## Fixed page order

1. **Return header**
2. **Target-restoration card**
3. **Structural-delta card**
4. **Return-class card**
5. **Requalification card**
6. **Decision sentence**

### 1) Return header

Show:

- return id
- affected suspension id
- affected control id
- source case / rollout / maintenance window id
- current return status
- owner
- requested return time
- current strongest safe sentence

Supported `current_return_status` values:

- `requested-not-yet-started`
- `blocked-by-prerequisite`
- `ready-for-reconciliation-review`
- `return-in-progress`
- `motion-restored-awaiting-requalification`
- `partially-restored`
- `fully-restored`
- `closed-with-intentional-delta`

Hard rule:

A return object may not inherit `fully restored` language just because the underlying transport is moving again.

### 2) Target-restoration card

This card states what protected state is being sought.
Required rows:

- target protected sentence
- target path / topology / permission posture
- target coverage scope
- target byte/materialization posture
- target policy/profile posture
- whether exact parity or acceptable-delta return is intended

Supported `target_restoration_intent` values:

- `exact-pre-bypass-return`
- `same-protection-new-path-accepted`
- `same-protection-new-mode-accepted`
- `permission-only-restoration`
- `transport-only-restoration`
- `intentional-weaker-successor-return`

Hard rule:

The target must be stated in operator language, not implied from the last button used.

### 3) Structural-delta card

This card records what is different between pre-bypass state and the proposed return.
Required rows:

- path delta
- topology delta
- permission delta
- placeholder / full-byte delta
- policy/profile delta
- observer/witness delta

Supported `structural_delta_flag` values:

- `same-path`
- `new-default-path-proposed`
- `new-directory-created`
- `existing-directory-merge-return`
- `placeholder-state-changed`
- `peer-rights-not-yet-restored`
- `scope-narrower-than-before`
- `world-or-lane-changed`

Hard rule:

A return is incomplete unless every material delta is either reconciled, accepted, or blocked.

### 4) Return-class card

Required rows:

- return class
- initiating surface
- prerequisite class
- reconciliation depth
- whether same-path continuity exists
- whether manual attestation is required after motion returns

Supported `return_class` values:

- `same-surface-resume`
- `scheduled-window-exit`
- `environment-gate-clear`
- `reconnect-same-path`
- `reconnect-new-path`
- `connect-existing-directory-merge`
- `permission-restoration`
- `recreate-and-requalify`
- `partial-scope-return`

Hard rule:

`same-surface-resume` may not be used if the return changes path, topology, permission, or byte posture.

### 5) Requalification card

Required rows:

- first point at which motion may return
- first point at which structure matches target
- first point at which trust may return
- proof needed to close remaining delta
- stronger sentence still blocked
- linked case / control / rollout reopened if return fails

Supported `requalification_class` values:

- `none-motion-equals-claim`
- `path-parity-check-required`
- `merge-result-check-required`
- `peer-rights-check-required`
- `attestation-required`
- `new-baseline-required`

Hard rule:

`resumed` and `requalified` may never be treated as the same answer unless the target restoration intent explicitly allows that weaker claim.

### 6) Decision sentence

The page ends with one sentence in this shape:

> `Return <id> seeks <target restoration intent> for <scope>; compared with the pre-bypass state, <structural delta summary> is still relevant, so the current safe sentence is <current sentence> until <requalification requirement>.`
