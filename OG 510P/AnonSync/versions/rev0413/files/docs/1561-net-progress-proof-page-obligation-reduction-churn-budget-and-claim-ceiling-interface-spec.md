# Net progress proof page: obligation reduction, churn budget, and claim ceiling interface spec

## Purpose

After progress review, the product needs one durable proof page that answers:

> what is the strongest progress claim we can still make, what proves real reduction of the named obligation, how much churn remains tolerable, and when does motion stop buying enough to keep the current route?

## Core decision

AnonSync must expose one first-class **Net progress proof** page for every claimed item that has entered motion, churn-present, no-net-gain watch, reroute, or requalification state.

## Fixed page order

1. **Progress verdict banner**
2. **Advance basis card**
3. **Churn-budget card**
4. **No-net-gain consequence card**
5. **Reroute consequence card**
6. **Blocked stronger claim card**

### 1) Progress verdict banner

Show:

- current progress verdict
- current custodian
- strongest allowed progress sentence
- last observed motion time
- last confirmed net-advance time
- current churn budget status
- current no-net-gain posture
- reroute owner if any

Supported `progress_verdict` values:

- `net-progress-proved`
- `partial-net-progress-proved`
- `motion-without-net-progress`
- `churn-dominant`
- `new-debt-created`
- `no-net-gain-proved`
- `reroute-live`
- `requalified-after-reroute`

Hard rule:

A verdict may not say `net-progress-proved` unless there is at least one fresh basis that directly reduces the named obligation or closes a named substep that the contract treats as reduction.

### 2) Advance basis card

Required rows:

- strongest current advance basis
- secondary bases if any
- freshness of the strongest basis
- whether the basis is direct or proxy
- whether the basis reduces outstanding obligation or only prepares for it
- reviewer who accepted the basis

Supported `advance_basis_class` values:

- `direct-obligation-reduction`
- `verified-substep-closure`
- `proxy-motion-only`
- `cleanup-without-closure`
- `new-debt-created`
- `no-fresh-basis`

Hard rule:

Proxy motion may support a weaker sentence than direct reduction.
The proof page must preserve that difference.

### 3) Churn-budget card

Required rows:

- current churn classes in play
- allowed churn budget
- churn consumed so far
- whether churn is within budget
- whether churn created or enlarged debt
- what sentence survives if churn continues at the same rate

Supported `churn_budget_status` values:

- `none`
- `within-budget`
- `aging`
- `exceeded`
- `exceeded-with-reroute-live`

Hard rule:

Budget consumption may weaken a progress claim even before the no-net-gain boundary fully crosses.
The proof page must say so explicitly.

### 4) No-net-gain consequence card

Required rows:

- current no-net-gain posture
- time since last confirmed net advance
- motion observed since then
- whether the no-net-gain watch is still provisional or proved
- what stronger sentence became blocked when the boundary opened or crossed
- what evidence would requalify the work

Supported `no_net_gain_consequence` values:

- `not-open`
- `watch-open`
- `watch-aging`
- `boundary-crossed`
- `boundary-crossed-reroute-live`
- `requalified`

Hard rule:

A proved no-net-gain story must stay visible even if the heartbeat is otherwise healthy.

### 5) Reroute consequence card

Required rows:

- current route consequence
- reroute owner
- whether reroute is optional or required
- whether rescue has started
- what weaker progress sentence survives during reroute
- whether the old route may still return after requalification

Supported `route_consequence` values:

- `none`
- `monitor-more-tightly`
- `lower-claim`
- `change-plan`
- `rescue-active`
- `closed-without-progress`

Hard rule:

The proof page must preserve the next allowed route.
No-net-gain proof is not complete without a consequence.

### 6) Blocked stronger claim card

Render exactly one card titled:

**Blocked stronger progress claim**

Examples:

- `The work is making efficient forward progress.`
- `All visible motion is reducing the outstanding obligation.`
- `No reroute or rescue should be considered yet.`
- `The current route is still proportionate to the return.`

Hard rule:

The blocked stronger claim must remain legible after export and handoff.
