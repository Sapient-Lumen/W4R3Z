# Work heartbeat lineage receipt page: heartbeat status, stall boundary, and rescue owner interface spec

## Purpose

Later operators need one small durable artifact that answers:

> what was the last trusted liveness state of this claimed work, what supported it, when would silence stop being acceptable, and who owned rescue when the boundary was crossed?

## Receipt fields

The **Work heartbeat lineage receipt** must contain exactly these fields in this order:

1. heartbeat id
2. linked claim id
3. linked work id
4. final heartbeat status
5. strongest liveness basis
6. last observed motion time
7. next required heartbeat time
8. quiet-window status
9. stall-boundary status
10. rescue owner
11. surviving weaker sentence
12. blocked stronger sentence

## Supported `final_heartbeat_status` values

- `accepted-no-motion-proof`
- `motion-verified`
- `healthy-wait`
- `blocked-wait`
- `overdue`
- `stalled`
- `rescue-active`
- `requalified`
- `reclaimed-after-stall`
- `closed-without-recovery`

## Supported `stall_boundary_status` values

- `not-near`
- `near-overdue`
- `overdue`
- `stalled`
- `stalled-and-reclaim-risk`
- `resolved-after-rescue`

## Receipt rules

### Rule 1: custody status may not stand in for heartbeat status

`accepted` belongs to the claim receipt.
This receipt starts at liveness truth.

### Rule 2: the strongest liveness basis must be reviewable later

Examples:

- explicit custodian heartbeat
- direct output change
- queue-progress observation
- confirmed blocker proof
- explicit rescue activation

`No complaint arrived` is never enough.

### Rule 3: surviving weaker sentence is mandatory

Examples:

- `The work is still claimed but no fresh motion proof is present.`
- `The work is quietly waiting on a confirmed blocker until the next heartbeat boundary.`
- `The work stalled and rescue ownership is now live.`

### Rule 4: blocked stronger sentence is mandatory

Examples:

- `This work is definitely progressing.`
- `Quiet time is harmless.`
- `The accepted custodian still has this fully under control.`
- `No rescue path remains necessary.`

### Rule 5: rescue ownership must survive failure-looking states

A receipt may show `stalled` or `reclaimed-after-stall` and must still preserve who owned the rescue or reclaim burden at that moment.

## Display note

This receipt should be short enough to travel with portfolio, claim, mandate, and fulfillment receipts without losing the liveness story.
