# Work heartbeat timeline page: claim, start, progress, nudge, stall, and rescue events interface spec

## Purpose

Liveness truth changes over time.
The timeline page must answer:

> when was the claim accepted, when was motion last observed, when did quiet become overdue, and when did nudge, rescue, or reclaim change the status of the work?

## Core timeline rule

AnonSync must treat heartbeat changes as first-class events, not as comments hiding inside the custody record.

## Fixed event order

1. **Claim-entered event**
2. **Start or first-heartbeat event**
3. **Healthy-wait or blocker event**
4. **Heartbeat-renewal or fresh-motion event**
5. **Overdue event**
6. **Nudge / rescue / reclaim event**
7. **Aftermath event**

## Supported event types

- `claim-accepted`
- `started`
- `first-motion-observed`
- `heartbeat-observed`
- `healthy-wait-opened`
- `blocker-declared`
- `blocker-confirmed`
- `quiet-window-renewed`
- `heartbeat-overdue`
- `nudge-sent`
- `proof-request-sent`
- `stall-confirmed`
- `backup-custody-activated`
- `rescued`
- `requalified`
- `reclaimed-after-stall`
- `closed-without-recovery`

## Required fields per event

- timestamp
- acting party
- evidence basis
- resulting heartbeat state
- next required heartbeat time if any
- what stronger sentence became allowed or blocked

## Timeline obligations

### A) Claim acceptance must stay visible even after rescue

The page may not hide the original acceptance once heartbeat rescue begins.
Later readers must still see who first held the work.

### B) Quiet windows must be explicit events, not inferred from missing data

If the system allows quiet, the timeline must show when the quiet window opened and when it renewed or expired.
Missing motion alone may not silently double as a healthy wait state.

### C) Overdue and stall must be separate events

`heartbeat-overdue` means the expected heartbeat did not arrive on time.
`stall-confirmed` means the item has crossed the stronger boundary that activates rescue or reclaim.
The timeline must not collapse those two.

### D) Rescue must preserve what happened before it

If motion resumed only after rescue, the timeline must show the stale period, the rescue trigger, and the requalification event.
Rescue is not allowed to rewrite the old record into uninterrupted progress.

### E) Partial motion must survive later stall

If some progress happened before silence, the timeline must preserve the last-motion event even after the item later stalls or is reclaimed.

## Footer sentence

Render exactly one line:

**Current liveness consequence:** followed by the next required heartbeat or next rescue duty.

Hard rule:

A timeline ending in overdue, stalled, or reclaimed posture must still state the live consequence now.
