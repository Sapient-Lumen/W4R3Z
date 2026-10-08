# Work progress lineage receipt page: progress basis, churn status, and blocked stronger sentences interface spec

## Purpose

Later operators need one small durable artifact that answers:

> what was the last trusted progress state of this claimed work, what proved real advance if anything did, how much churn was present, and what stronger progress sentence remained blocked?

## Receipt fields

The **Work progress lineage receipt** must contain exactly these fields in this order:

1. progress id
2. linked heartbeat id
3. linked claim id
4. linked work id
5. final progress status
6. strongest advance basis
7. last observed motion time
8. last confirmed net-advance time
9. churn status
10. no-net-gain status
11. reroute owner
12. surviving weaker sentence
13. blocked stronger sentence

## Supported `final_progress_status` values

- `motion-seen-net-advance-unproven`
- `net-progress-proved`
- `partial-net-progress`
- `churn-present-but-advancing`
- `churn-dominant`
- `new-debt-created`
- `no-net-gain`
- `reroute-live`
- `requalified`
- `closed-without-net-gain`

## Supported `churn_status` values

- `none-visible`
- `within-budget`
- `budget-aging`
- `budget-exceeded`
- `created-new-debt`
- `resolved-after-reroute`

## Supported `no_net_gain_status` values

- `not-open`
- `watch-open`
- `watch-aging`
- `boundary-crossed`
- `reroute-live`
- `requalified`

## Receipt rules

### Rule 1: motion status may not stand in for progress status

`motion observed` belongs in the timeline.
This receipt starts at progress truth.

### Rule 2: the strongest advance basis must be reviewable later

Examples:

- direct reduction of bytes or open set
- verified closure of a named substep
- accepted evidence return that closes a decision gap
- explicit reroute requalification after a no-net-gain period

`The system looked busy` is never enough.

### Rule 3: surviving weaker sentence is mandatory

Examples:

- `Motion was observed, but no fresh proof of net obligation reduction was accepted.`
- `The work advanced partially while consuming visible churn budget.`
- `The work remained alive but crossed the no-net-gain boundary and required reroute.`

### Rule 4: blocked stronger sentence is mandatory

Examples:

- `All visible activity was meaningful progress.`
- `No reroute or rescue was warranted.`
- `The current route remained efficient throughout.`
- `The obligation was steadily shrinking.`

### Rule 5: reroute ownership must survive no-net-gain states

A receipt may show `no-net-gain` or `reroute-live` and must still preserve who owned the route change burden at that moment.

## Display note

This receipt should be short enough to travel with heartbeat, portfolio, claim, mandate, fulfillment, and dispute receipts without losing the progress-quality story.
