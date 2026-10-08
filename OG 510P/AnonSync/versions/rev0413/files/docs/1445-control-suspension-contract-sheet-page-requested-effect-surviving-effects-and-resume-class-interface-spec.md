# Control suspension contract sheet page: requested effect, surviving effects, and resume class interface spec

## Purpose

After the archive learned to trust or distrust a control, it still needed one ordinary page for the next operator question:

> if we suspend or bypass this control temporarily, what exactly is supposed to stop, what is explicitly allowed to keep happening, and how does normal trust come back later?

## Core decision

AnonSync must expose one first-class **Control suspension contract sheet** whenever an operator pauses, narrows, bypasses, detaches, or otherwise weakens a live control.

## Fixed page order

1. **Suspension header**
2. **Requested-effect card**
3. **Surviving-effects card**
4. **Scope and resume card**
5. **Trust-downgrade card**
6. **Decision sentence**

### 1) Suspension header

Show:

- suspension id
- affected control id
- source case / rollout / maintenance window id
- current suspension class
- current status
- start time
- expiry or rereview time
- owner
- current strongest safe sentence

Supported `current_status` values:

- `requested-not-yet-armed`
- `armed-active`
- `armed-with-drift`
- `expired-but-still-active`
- `manual-resume-requested`
- `rearm-proof-pending`
- `closed`

Hard rule:

A suspension may not inherit `trusted` language from the underlying control while active.

### 2) Requested-effect card

This card states what the operator intends to suppress.
Required rows:

- requested stop effect
- reason class
- triggering condition
- whether the stop is preventive, bandwidth, safety, maintenance, or break-glass
- desired end state
- allowed override scope

Supported `requested_stop_effect` values:

- `pause-transfers`
- `download-stop-upload-allowed`
- `network-gated-stop`
- `background-activity-suppressed`
- `local-detach-reconnectable`
- `peer-revocation`
- `global-wide-pause`
- `destructive-detach-and-recreate`

Supported `reason_class` values:

- `maintenance-window`
- `safety-break-glass`
- `bandwidth-or-cost-control`
- `partial-outage-containment`
- `debug-or-observation`
- `operator-convenience`
- `policy-exception`

Hard rule:

Requested effect must describe the stop in operator language, not just the button name.

### 3) Surviving-effects card

This card is mandatory and records what still happens during suspension.
Required rows:

- effects explicitly stopped
- effects still allowed
- effects deferred until resume
- effects that continue elsewhere
- data-loss or topology risk
- visible UI badge class

Supported `surviving_effect` values:

- `deletions-still-propagate`
- `indexing-or-detection-continues`
- `uploads-may-continue`
- `placeholders-remain-visible`
- `peer-relationship-persists`
- `peer-relationship-revoked`
- `new-updates-not-detected`
- `new-path-may-be-created-on-resume`
- `bytes-remain-present-but-future-updates-stop`

Hard rule:

A suspension is invalid unless at least one `still allowed` or `nothing survives` statement is explicit.

### 4) Scope and resume card

Required rows:

- subject scope
- world / lane scope
- whether auto-resume exists
- resume class
- proof needed to re-arm
- whether original topology/path is preserved

Supported `resume_class` values:

- `manual-resume-same-surface`
- `scheduled-auto-resume`
- `environment-return-based`
- `reconnect-required`
- `readd-required`
- `new-attestation-required-before-trust-restores`

Hard rule:

`resume available` and `trust restored` may never be treated as the same answer.

### 5) Trust-downgrade card

Required rows:

- sentence withdrawn at arm time
- weaker surviving sentence while active
- overclaim currently blocked
- whether recurrence watch changes while suspended
- who must approve extension past expiry

Supported `downgrade_class` values:

- `trusted-control-now-bypassed`
- `coverage-narrowed`
- `detection-only-during-suspension`
- `manual-rearm-required`
- `topology-detached`

### 6) Decision sentence

The page ends with one sentence in this shape:

> `Suspension <id> requests <requested stop effect> for <scope>; while active, <surviving effect summary> remains true and the strongest safe sentence drops to <weaker sentence>.`
