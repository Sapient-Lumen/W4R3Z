# Return-to-protection proof page: resume, reconnect, rebind, and requalification interface spec

## Purpose

Once a return route is approved, the archive needs one explicit page for the next question:

> what exactly came back, what proof shows the system is moving again, what structural deltas were actually resolved, and what still has to be requalified before the stronger protection sentence returns?

## Core decision

AnonSync must expose one first-class **Return-to-protection proof** whenever a control bypass, detachment, permission revoke, or path/mode divergence is ended.

## Fixed page order

1. **Proof header**
2. **Motion-restoration card**
3. **Structural-reconciliation card**
4. **Residual-delta card**
5. **Requalification verdict card**
6. **Proof sentence**

### 1) Proof header

Show:

- return id
- proof time
- proof owner
- active scope
- return verdict
- chosen return class
- current protection state
- resulting trust state

Supported `return_verdict` values:

- `motion-restored-as-intended`
- `motion-restored-with-structural-delta`
- `reconnected-but-new-path-created`
- `merge-return-completed-awaiting-review`
- `permission-restored-awaiting-attestation`
- `inconclusive-return-state`
- `fully-requalified`

### 2) Motion-restoration card

Required rows:

- surface or mechanism used to restore motion
- direct evidence that motion or eligibility returned
- evidence that the chosen route matches the approved candidate
- missing evidence if any
- observers and timestamps

Supported `motion_restoration_evidence_class` values:

- `ui-resume-state`
- `scheduled-window-ended`
- `environment-gate-cleared`
- `reconnect-completed`
- `permission-restored`
- `directory-merge-begun`
- `new-baseline-accepted`

Hard rule:

A badge or button flip alone cannot prove path parity, permission parity, or return-to-same-protection unless the product says that is all it is claiming.

### 3) Structural-reconciliation card

Required rows:

- path parity result
- placeholder/full-byte posture result
- peer/topology result
- merge or overwrite result
- lane/world result
- observer/witness restoration result

Supported `structural_reconciliation_verdict` values:

- `same-path-confirmed`
- `new-path-accepted`
- `index-suffixed-path-created`
- `existing-directory-merge-under-review`
- `placeholder-posture-changed`
- `future-updates-restored`
- `relationship-restored-but-not-baselined`
- `world-lane-delta-remains`

### 4) Residual-delta card

Required rows:

- delta still present
- delta accepted intentionally or not
- risk if delta persists
- linked object impacted
- whether rollback or re-detach remains allowed
- earliest next review

Supported `residual_delta_class` values:

- `none`
- `accepted-new-path`
- `accepted-weaker-mode`
- `merge-review-pending`
- `permission-asymmetry-pending`
- `attestation-pending`
- `rebaseline-pending`

### 5) Requalification verdict card

Required rows:

- strongest sentence now safe
- stronger sentence still blocked
- next proof needed
- whether old baseline was restored or replaced
- case / control / rollout reopened if proof later fails

Hard rule:

`activity restored` may not imply `same protection restored` unless the structural-reconciliation card proves parity or the target restoration intent explicitly accepted the delta.

### 6) Proof sentence

The page must end with one sentence in this shape:

> `Return <id> is <return verdict> across <scope>; motion has returned by <evidence>, but <residual delta or none> means the strongest safe sentence is <current sentence> until <next proof>.`
