# Execution heartbeat proof page: motion basis, silence window, and rescue route interface spec

## Purpose

After heartbeat review, the product needs one durable proof page that answers:

> what is the strongest liveness claim we can still make about this claimed work, what motion or waiting basis supports it, how much silence remains acceptable, and who rescues it if that silence outlives the contract?

## Core decision

AnonSync must expose one first-class **Execution heartbeat proof** page for every claimed item that has entered accepted, healthy-motion, healthy-wait, blocked-wait, overdue, stalled, or rescue-active state.

## Fixed page order

1. **Heartbeat verdict banner**
2. **Liveness basis card**
3. **Quiet-window card**
4. **Stall-boundary card**
5. **Rescue consequence card**
6. **Blocked stronger claim card**

### 1) Heartbeat verdict banner

Show:

- current heartbeat verdict
- current custodian
- current rescue owner
- strongest allowed liveness sentence
- last observed motion time
- next required heartbeat time
- current stall risk grade

Supported `heartbeat_verdict` values:

- `custody-only-no-motion-proof`
- `motion-proved`
- `healthy-wait-proved`
- `blocked-wait-proved`
- `heartbeat-overdue`
- `stall-proved`
- `rescue-live`
- `requalified-after-rescue`

Hard rule:

A verdict may not say `motion-proved` unless there is at least one fresh evidence basis that matches the expected motion class.

### 2) Liveness basis card

Required rows:

- strongest current basis
- secondary bases if any
- freshness of the strongest basis
- whether the basis proves motion or only healthy wait
- whether the basis comes from direct output or proxy signal
- last reviewer who accepted the basis

Supported `liveness_basis_class` values:

- `direct-output-change`
- `explicit-custodian-check-in`
- `queue-or-transfer-progress`
- `performance-signal-only`
- `healthy-background-processing`
- `confirmed-external-blocker`
- `no-fresh-basis`

Hard rule:

Proxy signal may support a weaker sentence than direct output.
The proof page must preserve that difference.

### 3) Quiet-window card

Required rows:

- current quiet-window class
- time remaining in the quiet window
- whether the window is renewable
- who may renew it
- evidence needed for renewal
- what sentence survives if the window expires silently

Supported `quiet_window_status` values:

- `none`
- `open-and-healthy`
- `open-but-aging`
- `renewed`
- `expired`
- `expired-with-rescue-live`

Hard rule:

A renewed quiet window must show a new boundary.
Passive passage of time can never count as renewal.

### 4) Stall-boundary card

Required rows:

- overdue threshold
- stall threshold
- current distance to each threshold
- whether a blocker explains the current quiet
- whether the blocker itself is overdue
- what stronger sentence became blocked at each threshold

Supported `stall_boundary_posture` values:

- `far-from-overdue`
- `near-overdue`
- `overdue-not-stalled`
- `stalled`
- `stalled-and-reclaim-risk`

Hard rule:

The proof page must keep overdue and stalled separate even when both imply concern.

### 5) Rescue consequence card

Required rows:

- rescue owner
- first rescue action
- fallback rescue action
- latest safe completion of first rescue action
- whether custody remains with the same person during rescue
- what weaker sentence survives if rescue also fails

Supported `rescue_consequence_class` values:

- `nudge-with-same-custody`
- `proof-request-with-same-custody`
- `backup-custody-activation`
- `reclaim-to-portfolio`
- `reopen-underlying-case`
- `external-escalation`

Hard rule:

Rescue may not appear ownerless.
The proof page must always name who has the next burden.

### 6) Blocked stronger claim card

Render exactly one line beginning:

**Blocked stronger claim:**

Examples:

- `This work is definitely progressing.`
- `Quiet means healthy.`
- `The current custodian still has this under control.`
- `No rescue path remains necessary.`

Hard rule:

Every heartbeat proof must preserve one blocked stronger claim.
