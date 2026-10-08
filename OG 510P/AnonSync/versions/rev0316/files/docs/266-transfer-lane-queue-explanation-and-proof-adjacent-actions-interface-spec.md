# Transfer lane, queue explanation, and proof-adjacent actions interface spec

## Purpose

The archive already has transfer-policy doctrine and a dedicated transfer-explanation pane.
What it still lacked was a fixed contract for the **Transfers** page itself.

This document answers one everyday operator question:

> when I open Transfers, what row and detail structure lets me tell whether work is actually moving, merely queued, fairness-delayed, source-waiting, schedule-paused, route-degraded, or blocked by policy without cross-reading graphs, preferences, and troubleshooting lore?

Current Resilio docs are useful here precisely because they spread the answer out.
Rate limits, scheduler, LAN exceptions, relay/direct differences, and browser-safe status language all exist, but not as one stable transfer-lane reading order.

## Core decision

Transfers is not a graph wall.
It is a **lane board** for moving, delayed, suspended, and blocked byte work.

Every transfer row must keep these truths adjacent:

1. what subject/file scope is moving
2. what lane state it is in now
3. what route class currently carries or prevents it
4. what budget/schedule/policy is affecting it
5. what bottleneck is dominant right now
6. what next action is honest
7. where the proof / explanation drawer lives

## Transfer row anatomy

Each row should render the following slots in a stable order:

1. **Subject / scope slot**
2. **Lane-state slot**
3. **Route slot**
4. **Budget / schedule slot**
5. **Bottleneck slot**
6. **Primary-action slot**
7. **Why / proof slot**

### Subject / scope slot

Show:

- share title
- file or subtree label when scoped below share level
- source and target seat pair when relevant

### Lane-state slot

Use explicit phrases such as:

- `Transferring now`
- `Queued`
- `Waiting source`
- `Fairness hold`
- `Schedule-paused`
- `Policy-blocked`
- `Retrying`
- `Finalizing`

Avoid vague status words like `active`, `pending`, or `busy` when a more exact lane phrase exists.

### Route slot

Show:

- current selected route class
- any route anomaly that matters now

Examples:

- `LAN direct`
- `Overlay path`
- `Known-host direct`
- `Relay fallback`
- `No viable route`

### Budget / schedule slot

Show the strongest winning limiter, such as:

- `No cap`
- `WAN cap 8 MiB/s`
- `LAN exception active`
- `Scheduler pause`
- `Fairness share 25%`
- `Burst budget exhausted`

This slot exists so the operator does not have to remember whether a transfer is slow because of physics or because of policy.

### Bottleneck slot

Show one primary bottleneck and optional secondary chips.
Examples:

- `Disk bound`
- `High RTT`
- `Relay cost`
- `Source offline`
- `Indexing ahead`
- `Waiting approval`

### Primary-action slot

Show only the safest next honest verb:

- `Why`
- `Inspect route`
- `Review budget`
- `Resume`
- `Keep queued`
- `Inspect blocker`
- `Open subject`

### Why / proof slot

This slot opens the explanation drawer or deep-link to the transfer explanation receipt.
It must always be reachable without hidden menus.

## Lane groups

The page should group rows into explicit lane families:

1. **Moving now**
2. **Queued but healthy**
3. **Waiting on source / route / approval**
4. **Policy or schedule constrained**
5. **Degraded / retrying**
6. **Blocked**
7. **Recently completed**

This grouping is more important than ornamental charts.
It answers whether the operator is dealing with backlog, policy, or failure.

## Fixed detail-pane order

Opening a row should render sections in this order:

1. **Current answer**
2. **Subject and lane scope**
3. **Route and directness**
4. **Winning budgets / schedule / fairness**
5. **Dominant bottleneck and evidence**
6. **Allowed actions and blocked actions**
7. **Receipts, snapshots, and recent continuity**

### 1) Current answer

One sentence first, for example:

- `This transfer is queued because fairness policy is holding it behind higher-priority work.`
- `This transfer is slow because it is relayed and disk pressure is the secondary bottleneck.`
- `This transfer is blocked because no approved byte source is currently eligible.`

### 2) Subject and lane scope

Show:

- share/file scope
- source and target seats
- whether the row is share-wide, subtree, or single-file work

### 3) Route and directness

Show:

- winning route class
- directness grade
- fallback reason
- rejected higher-ranked route candidates when relevant

### 4) Winning budgets / schedule / fairness

Show:

- effective rate cap
- LAN exception state
- fairness lane or class
- scheduler window status
- temporary override if any

### 5) Dominant bottleneck and evidence

Show:

- primary bottleneck kind
- secondary contributors
- recent latency / queue / source-availability evidence
- freshness of that evidence

### 6) Allowed actions and blocked actions

Examples:

- `Inspect route`
- `Review budget`
- `Keep queued`
- `Resume after window`
- `Open blocker review`

And visibly blocked actions such as:

- `Force direct now` blocked by current disclosure policy
- `Resume` blocked by missing source eligibility

### 7) Receipts, snapshots, and recent continuity

Show:

- explanation receipt
- last significant lane change
- whether recent retry history exists
- whether the row is part of a larger batch or family

## Batch rules

Batch actions are allowed only for rows sharing the same honest action class.

Good batch labels:

- `Review budgets for 6 capped rows`
- `Inspect route on 3 relay-fallback rows`
- `Resume 4 scheduler-paused rows`

Bad batch labels:

- `Retry all`
- `Speed up selected`
- `Fix transfers`

## Chart rule

Charts may exist, but they are secondary.
No chart is allowed to become the only place where the operator can learn:

- the winning route class
- the current rate-limiting layer
- the dominant bottleneck
- the honest next action

## Dense and textual surfaces

CLI, TUI, and narrow-width web surfaces should preserve the same semantic order even if the layout compresses.
A compact row should still read like:

```text
Research Vault / dataset.tar   Queued   Overlay path   WAN cap 8 MiB/s   Fairness hold   Why
```

not like:

```text
Research Vault / dataset.tar   Pending   2.3 MiB/s
```

## Relationship to nearby specs

This spec is the Transfers-page companion to:

- `53-transfer-policy-and-throughput-budget-spec.md`
- `227-route-evidence-latency-bottleneck-and-directness-explanation-interface-spec.md`
- `239-effective-rate-policy-lan-exception-and-scheduled-throttle-interface-spec.md`

Those documents already define the truths.
This one fixes the page where operators should be able to read them quickly and honestly.
