# Progress quality review page: meaningful advance, retry churn, and no-net-gain routes interface spec

## Purpose

The contract sheet defines what real progress should look like.
The review page must decide:

> based on current evidence, is this work actually advancing, only moving noisily, creating new debt, or spending effort without net gain?

## Core review rule

AnonSync must separate **motion evidence**, **advance evidence**, **churn evidence**, and **reroute consequence**.
No review may collapse those into one status.

## Fixed page order

1. **Review banner**
2. **Motion-versus-advance review**
3. **Churn review**
4. **No-net-gain review**
5. **Reroute / rescue review**
6. **Blocked stronger sentence**

### 1) Review banner

Show:

- current review verdict
- current custodian
- last observed motion
- last confirmed net advance
- current churn grade
- current no-net-gain posture
- reroute owner if active

Supported `review_verdict` values:

- `advance-proved`
- `advance-probable`
- `motion-only`
- `churn-heavy-but-advancing`
- `churn-dominant`
- `new-debt-created`
- `no-net-gain`
- `reroute-needed`
- `rescued-and-requalifying`

Hard rule:

`motion-only` must stay available as a stable verdict.
The review may not force every observed activity into an advance claim.

### 2) Motion-versus-advance review

Required rows:

- strongest fresh motion evidence
- strongest fresh advance evidence
- whether motion and advance come from the same event
- whether the evidence is direct or proxy
- whether the evidence reduces the named obligation or only prepares for reduction
- current claim ceiling supported by the evidence

Supported `motion_evidence_type` values:

- `transfer-progress`
- `queue-drain`
- `history-activity`
- `hashing-or-scan`
- `metadata-merge`
- `retry-loop`
- `conflict-creation`
- `blocked-transfer`
- `operator-note`

Hard rule:

`hashing-or-scan`, `metadata-merge`, `retry-loop`, and `operator-note` may support weaker sentences, but they may not by themselves produce the strongest `advance-proved` verdict.

### 3) Churn review

Required rows:

- churn class
- whether the churn was expected here
- current churn cost
- whether churn exceeded budget
- whether churn created new debt
- what sentence survives if churn continues unchanged

Supported `churn_class` values:

- `none`
- `rescan-churn`
- `rehash-churn`
- `retry-churn`
- `merge-churn`
- `conflict-churn`
- `blocked-transfer-churn`
- `mixed`

Hard rule:

Churn that creates new work must be treated more harshly than churn that only delays reduction.
The review may not hide conflict-making motion inside a generic busy state.

### 4) No-net-gain review

Required rows:

- last confirmed net advance
- motion observed since then
- current no-net-gain window
- whether the no-net-gain boundary is aging or crossed
- what evidence would break the no-net-gain story
- what weaker sentence remains if no new proof arrives

Supported `no_net_gain_posture` values:

- `not-open`
- `watch-open`
- `watch-aging`
- `boundary-crossed`
- `boundary-crossed-with-reroute`

Hard rule:

A no-net-gain watch may open even while the heartbeat remains live.
Alive work and advancing work are separate truths.

### 5) Reroute / rescue review

Required rows:

- current consequence route
- reroute owner
- whether route change is advisory or mandatory
- whether rescue is needed now or only if another boundary is crossed
- whether the work can be requalified without a plan change
- what stronger sentence the route change blocks

Supported `consequence_route` values:

- `keep-observing`
- `lower-progress-claim`
- `tighten-proof-burden`
- `change-plan`
- `activate-rescue`
- `close-without-net-gain`

Hard rule:

Route change is part of progress review, not an afterthought.
A review that proves no-net-gain motion must publish the next allowed operator move.

### 6) Blocked stronger sentence

Render a dedicated section titled:

**Blocked stronger sentence**

List at least one stronger statement that remains unsupported.
Examples:

- `The work is definitely reducing the outstanding obligation.`
- `The visible activity is efficient rather than churn-heavy.`
- `No new debt is being created while the work is active.`
- `The current plan still deserves the same route.`

Hard rule:

The blocked sentence must get stronger when the evidence weakens.
No-net-gain reviews are not allowed to leave the stronger claim vague.
