# Work heartbeat contract sheet page: claimed work, expected motion, and stall boundary interface spec

## Purpose

Once work has been accepted, the operator still needs one page that answers:

> what kind of motion do we expect from this claimed item, how long may it stay quiet for good reasons, and when does quiet become a stall that requires rescue?

## Core decision

AnonSync must expose one first-class **Work heartbeat contract sheet** whenever a dispatched work item enters accepted, committed, active-watch, or in-progress posture.

## Fixed page order

1. **Heartbeat header**
2. **Claimed-work card**
3. **Expected-motion card**
4. **Allowed-quiet-window card**
5. **Blocker-aware waiting card**
6. **Stall-and-rescue card**
7. **Heartbeat sentence**

### 1) Heartbeat header

Show:

- heartbeat id
- linked claim id
- linked work id
- current heartbeat posture
- current custodian
- rescue owner
- last observed motion time if present
- next required heartbeat time if present
- current stall-risk grade

Supported `heartbeat_posture` values:

- `drafted-from-claim`
- `accepted-no-motion-yet`
- `healthy-motion`
- `healthy-wait`
- `blocked-wait`
- `heartbeat-overdue`
- `silent-stall`
- `rescue-active`
- `rescued-and-requalifying`
- `closed-without-heartbeat`

Hard rule:

The header may not imply `healthy-motion` merely because the claim is accepted.
Acceptance is still weaker than verified motion.

### 2) Claimed-work card

Required rows:

- work title
- work class
- current custodian
- why heartbeat tracking is needed
- what visible outcome the work should eventually change
- what weaker sentence remains true if motion stops
- relationship to claim expiry

Supported `heartbeat_need_class` values:

- `bounded-execution`
- `continuous-watch`
- `evidence-chase`
- `external-wait-with-checkback`
- `long-running-remediation`
- `multi-party-coordination`

Hard rule:

The card must preserve the work class and claim context.
Heartbeat pages are not allowed to dissolve the underlying job into a generic progress bar.

### 3) Expected-motion card

Required rows:

- expected motion class
- what counts as heartbeat evidence
- minimum cadence of visible motion
- whether passive observation is enough
- whether operator acknowledgement can count as a heartbeat
- what stronger sentence motion would unlock

Supported `expected_motion_class` values:

- `continuous-visible-progress`
- `periodic-check-in`
- `wait-until-external-change`
- `event-driven-watch`
- `bounded-burst-then-quiet`
- `human-coordination-updates`

Hard rule:

Heartbeat evidence must be typed.
The page may not let generic "someone is on it" language count as motion.

### 4) Allowed-quiet-window card

Required rows:

- quiet window length
- why quiet is allowed
- what observations keep the quiet window healthy
- whether the quiet window renews automatically
- when the window becomes overdue
- whether claim expiry and heartbeat overdue are the same clock

Supported `quiet_window_class` values:

- `no-quiet-allowed`
- `short-grace`
- `bounded-healthy-quiet`
- `blocker-tolerant-quiet`
- `renewable-watch-quiet`
- `operator-must-report-even-if-quiet`

Hard rule:

Last observed motion and next required heartbeat must appear as separate rows.
A long quiet window may not erase the history of the last actual motion.

### 5) Blocker-aware waiting card

Required rows:

- whether waiting is healthy or blocked
- named blocker if any
- blocker owner if any
- what evidence keeps wait healthy
- what evidence would flip wait into stall
- whether the blocker itself is now separate work

Supported `waiting_posture` values:

- `not-waiting`
- `healthy-background-work`
- `healthy-external-wait`
- `blocked-by-dependency`
- `blocked-by-missing-answer`
- `blocked-but-rescue-not-yet-due`

Hard rule:

A wait state must name what would count as continued health.
It may not rely on vague reassurance alone.

### 6) Stall-and-rescue card

Required rows:

- overdue threshold
- stall threshold
- rescue owner
- first rescue action
- stronger rescue escalation if first rescue fails
- whether the work returns to portfolio on unrescued stall

Supported `rescue_route` values:

- `nudge-current-custodian`
- `request-heartbeat-proof`
- `activate-backup-custodian`
- `reclaim-to-portfolio`
- `force-reassessment`
- `external-escalation`

Hard rule:

The page must distinguish overdue from stalled.
Overdue means more proof is needed; stalled means rescue ownership is already live.

### 7) Heartbeat sentence

Render exactly two lines:

- **Heartbeat now**
- **If the next heartbeat does not land, what rescue route activates**

Hard rule:

The sentence may not say `in progress` unless the evidence satisfies the expected motion class.
