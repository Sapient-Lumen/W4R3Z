# Work progress contract sheet page: obligation reduction, churn signals, and net advance interface spec

## Purpose

A live heartbeat is not enough.
Once work is moving, the operator still needs one page that answers:

> what exact obligation is supposed to shrink, what evidence counts as real reduction, what kinds of churn are temporarily acceptable, and when does motion stop buying progress?

## Core decision

AnonSync must expose one first-class **Work progress contract sheet** whenever a claimed work item has visible motion, proxy motion, repeated retries, heavy preprocessing, merge pressure, or conflict-producing activity.

## Fixed page order

1. **Progress header**
2. **Outstanding-obligation card**
3. **Meaningful-advance card**
4. **Allowed-churn card**
5. **No-net-gain boundary card**
6. **Progress sentence**

### 1) Progress header

Show:

- progress id
- linked heartbeat id
- linked claim id
- linked work id
- current progress posture
- current custodian
- last observed motion time if present
- last confirmed net-advance time if present
- current churn grade
- current no-net-gain posture
- reroute owner if present

Supported `progress_posture` values:

- `drafted-from-heartbeat`
- `motion-seen-net-advance-unknown`
- `net-progress-proved`
- `partial-net-progress`
- `churn-present-but-advancing`
- `churn-dominant`
- `no-net-gain-watch-open`
- `no-net-gain-boundary-crossed`
- `reroute-active`
- `requalified-after-reroute`
- `closed-with-unsettled-delta`

Hard rule:

The header may not imply `net-progress-proved` merely because motion exists.
Motion is still weaker than meaningful advance.

### 2) Outstanding-obligation card

Required rows:

- work obligation
- unit of reduction
- current outstanding amount or open set
- what counts as settled for this work
- what weaker sentence remains true if motion continues without reduction
- relationship to heartbeat status

Supported `obligation_reduction_class` values:

- `bytes-delivered`
- `subjects-cleared`
- `substeps-closed`
- `decision-gap-closed`
- `risk-lowered`
- `evidence-returned`
- `mixed`

Hard rule:

The card must preserve what exact thing is supposed to shrink.
A progress page is not allowed to substitute generic activity for obligation reduction.

### 3) Meaningful-advance card

Required rows:

- what evidence counts as meaningful advance
- smallest unit of meaningful advance
- whether proxy motion can ever count
- whether cleanup-only work can count
- whether newly created debt subtracts from progress
- what stronger sentence confirmed advance would unlock

Supported `meaningful_advance_class` values:

- `direct-obligation-reduction`
- `verified-substep-closure`
- `blocked-item-cleared`
- `fresh-decision-grade-evidence`
- `successful-handback`
- `composite`

Hard rule:

The page must say whether proxy motion is enough.
If not, scan, hash, merge, or queue activity may stay visible without being allowed to claim real progress.

### 4) Allowed-churn card

Required rows:

- accepted churn kinds
- churn budget class
- why churn may happen here
- when churn is still considered healthy preparation
- when churn starts weakening the progress claim
- whether churn can create new debt that must be counted separately

Supported `allowed_churn_class` values:

- `none`
- `low-retry-tolerance`
- `scan-heavy-expected`
- `merge-heavy-expected`
- `conflict-free-required`
- `best-effort-noisy`

Hard rule:

Allowed churn must be named.
`Busy systems are messy` is not a contract.

### 5) No-net-gain boundary card

Required rows:

- no-net-gain watch open time if any
- no-net-gain boundary
- what events can cross the boundary
- what weaker sentence survives once crossed
- who owns reroute or rescue
- what evidence would requalify the work

Supported `no_net_gain_boundary_class` values:

- `not-open`
- `watch-open`
- `aging-toward-boundary`
- `boundary-crossed`
- `boundary-crossed-reroute-live`

Hard rule:

A no-net-gain boundary must be explicit.
The page may not let repeated motion silently consume time forever.

### 6) Progress sentence

Render exactly one sentence:

**Current progress truth:** followed by the strongest supported sentence about net advance, churn posture, and reroute consequence.

Hard rule:

The sentence must state both what is still supported and what stronger progress story remains blocked.
