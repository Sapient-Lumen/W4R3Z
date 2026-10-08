# Work claim contract sheet page: dispatched item, assignee, commitment window, and reclaim rules interface spec

## Purpose

Once a decision portfolio dispatches one work item, the operator still needs one page that answers:

> who is being asked to take custody of this work, what commitment window is on offer, and what happens if the work is not accepted, not renewed, or deliberately returned?

## Core decision

AnonSync must expose one first-class **Work claim contract sheet** whenever a dispatched item needs a named owner, executor, or active watcher.

## Fixed page order

1. **Claim header**
2. **Dispatched-work card**
3. **Requested-custodian card**
4. **Commitment-window card**
5. **Delegation-boundary card**
6. **Expiry-and-reclaim card**
7. **Claim sentence**

### 1) Claim header

Show:

- claim id
- linked portfolio id
- dispatched work id
- current claim posture
- requested custodian
- current custodian if already accepted
- accepted-by time if present
- claim expiry time if present
- abandonment risk posture

Supported `claim_posture` values:

- `drafted`
- `notified`
- `claim-requested`
- `accepted`
- `committed`
- `in-progress`
- `re-delegation-pending`
- `declined`
- `returned`
- `expired`
- `reclaimed`
- `superseded`

Hard rule:

The header may not imply ownership merely because a person was selected.
A requested custodian is still not an accepted custodian.

### 2) Dispatched-work card

Required rows:

- dispatched work title
- work class
- why it won dispatch
- current action boundary
- blocked stronger action
- portfolio lane before claim
- consequence if unclaimed
- safe-not-to-start-yet condition

Supported `dispatched_work_class` values:

- `bounded-mutation`
- `monitoring-watch`
- `supplement-request`
- `heavy-capture`
- `publication-action`
- `external-escalation`
- `freeze-or-stop`

Hard rule:

The card must preserve why this item won.
Claim pages are not allowed to erase dispatch context.

### 3) Requested-custodian card

Required rows:

- primary requested custodian
- backup or successor custodian
- claim authority basis
- permitted roles for the custodian
- forbidden actions without reapproval
- current acknowledgement state

Supported `custodian_role_scope` values:

- `inform-only`
- `watch-only`
- `execute-bounded`
- `execute-and-redelegate`
- `escalate-only`
- `coordinate-multi-party`

Hard rule:

A person may be the primary recipient without being allowed to re-delegate or mutate.
Role scope must stay explicit.

### 4) Commitment-window card

Required rows:

- acknowledgement deadline
- start-by deadline
- latest safe completion target
- renewal cadence if the work is long-running
- quiet-window allowance if any
- what counts as breach

Supported `commitment_window_class` values:

- `ack-only`
- `ack-and-start`
- `continuous-watch`
- `bounded-execution-window`
- `renewing-custody`
- `until-explicit-return`

Hard rule:

A commitment window must state whether acknowledgement alone is enough or whether actual start is required.

### 5) Delegation-boundary card

Required rows:

- whether re-delegation is allowed
- who may approve re-delegation
- what evidence must accompany re-delegation
- whether partial transfer is allowed
- whether split custody is allowed
- whether the original custodian retains residual duty

Supported `delegation_boundary_posture` values:

- `no-redelegation`
- `redelegation-with-approval`
- `bounded-redelegation`
- `split-custody-allowed`
- `handoff-only`

Hard rule:

Re-delegation may not silently dissolve the original duty.
The page must say whether residual duty survives.

### 6) Expiry-and-reclaim card

Required rows:

- expiry trigger
- grace rule if any
- abandonment threshold
- reclaim owner
- where the work returns after reclaim
- what status survives after reclaim

Supported `reclaim_route` values:

- `return-to-portfolio-now`
- `return-to-portfolio-next`
- `force-reevaluation`
- `escalate-before-requeue`
- `close-as-no-longer-needed`

Hard rule:

Silence may trigger reclaim, but silence may never be rendered as success.

### 7) Claim sentence

Render exactly two lines:

- **Custody now**
- **If this claim expires or is returned, what visible risk comes back and where**

Hard rule:

The second line must name the surviving risk explicitly.
A returned or expired claim may not vanish into a generic `requeued` badge.
