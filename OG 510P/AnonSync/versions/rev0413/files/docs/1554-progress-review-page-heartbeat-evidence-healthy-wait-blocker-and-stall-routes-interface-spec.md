# Progress review page: heartbeat evidence, healthy wait, blocker, and stall routes interface spec

## Purpose

The contract sheet defines what motion should look like.
The review page must decide:

> based on current evidence, is this claimed work moving, waiting healthily, blocked, overdue, stalled, or already in rescue?

## Core review rule

AnonSync must separate **accepted custody**, **motion evidence**, and **stall consequence**.
No review may collapse those into one status.

## Fixed page order

1. **Review banner**
2. **Heartbeat-evidence review**
3. **Healthy-wait review**
4. **Blocker review**
5. **Overdue-versus-stall review**
6. **Rescue-route review**
7. **Blocked stronger sentence**

### 1) Review banner

Show:

- current review verdict
- current custodian
- rescue owner
- last observed motion
- next required heartbeat
- current risk grade

Supported `review_verdict` values:

- `motion-verified`
- `motion-partially-verified`
- `healthy-wait-verified`
- `blocked-wait-verified`
- `heartbeat-overdue`
- `stall-confirmed`
- `rescue-activated`
- `insufficient-basis`

Hard rule:

`motion-verified` requires actual heartbeat evidence, not just absence of bad news.

### 2) Heartbeat-evidence review

Required rows:

- evidence types observed
- freshness of each type
- whether evidence is direct or proxy
- whether the evidence matches the expected motion class
- whether it proves continued motion or only one recent burst
- claim ceiling supported by the evidence

Supported `heartbeat_evidence_type` values:

- `explicit-check-in`
- `observable-output-change`
- `queue-progress`
- `history-activity`
- `performance-activity`
- `status-light-only`
- `operator-note`

Hard rule:

`status-light-only` and `operator-note` may support weaker sentences, but they may not by themselves produce a strongest `motion-verified` verdict.

### 3) Healthy-wait review

Required rows:

- why quiet is acceptable
- what independent sign keeps it healthy
- whether the quiet window is still open
- whether waiting depends on a named blocker
- whether the waiting story is aging toward implausibility
- what sentence stays allowed while quiet continues

Supported `healthy_wait_basis` values:

- `background-processing`
- `external-response-pending`
- `scheduled-checkback`
- `known-long-operation`
- `batched-human-coordination`
- `none`

Hard rule:

Healthy wait must have a named basis.
`Nothing seems wrong yet` is not enough.

### 4) Blocker review

Required rows:

- blocker name
- blocker owner
- whether blocker proof is strong or inferred
- whether the blocker spawned a sibling work item
- whether the current custodian still owes heartbeat updates while blocked
- what would disprove the blocker story

Supported `blocker_strength` values:

- `confirmed-blocker`
- `probable-blocker`
- `claimed-blocker-unproven`
- `no-blocker`

Hard rule:

A claimed blocker without proof may soften the sentence, but it may not protect the work from overdue status indefinitely.

### 5) Overdue-versus-stall review

Required rows:

- overdue threshold reached yes or no
- stall threshold reached yes or no
- whether the current quiet is still reversible by a simple nudge
- whether rescue must activate now
- whether the work should return to the portfolio if rescue fails
- what stronger sentence is now blocked

Supported `stall_route` values:

- `still-within-quiet-window`
- `overdue-awaiting-nudge`
- `overdue-awaiting-proof`
- `stalled-requires-rescue`
- `stalled-reclaim-recommended`
- `stalled-reopen-case`

Hard rule:

The product must name the transition point.
It may not leave the operator to wonder whether the item is late or truly stalled.

### 6) Rescue-route review

Required rows:

- first rescue action
- rescue owner
- latest safe rescue-start time
- whether backup custody should activate
- whether the work becomes a portfolio item again
- what weaker sentence survives until rescue completes

Supported `rescue_start_posture` values:

- `not-needed`
- `nudge-now`
- `ask-for-proof-now`
- `activate-backup-now`
- `reclaim-now`
- `external-escalation-now`

Hard rule:

If rescue is live, the page must name the owner and clock.
A generic `follow up` label is forbidden.

### 7) Blocked stronger sentence

Render one sentence beginning:

**Still not allowed to say:**

Examples:

- `This work is actively progressing.`
- `The accepted custodian still has this under control.`
- `The quiet period is harmless.`
- `No rescue path is needed.`

Hard rule:

Every review must block one stronger sentence explicitly.
