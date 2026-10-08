# Decision charter contract sheet page: target action threshold and residual uncertainty interface spec

## Purpose

Once evidence has been synthesized, the operator still needs one page that answers:

> what exact decision are we trying to make, what action threshold is in play, and how much unresolved uncertainty is still allowed before a stronger action becomes dishonest?

## Core decision

AnonSync must expose one first-class **Decision charter contract sheet** whenever synthesized evidence is being used to justify a repair, wait posture, escalation, external statement, certification move, or doctrinal application.

## Fixed page order

1. **Decision header**
2. **Target-decision card**
3. **Threshold-ladder card**
4. **Evidence-basis card**
5. **Residual-uncertainty card**
6. **Allowed-action card**
7. **Blocked-stronger-action card**
8. **Decision sentence**

### 1) Decision header

Show:

- decision charter id
- parent case or synthesis id
- decision owner
- current decision posture
- current claim ceiling
- highest cleared threshold
- allowed next verb
- strongest blocked verb
- reopen trigger count

Supported `decision_posture` values:

- `charter-opened`
- `threshold-mapping-in-progress`
- `uncertainty-budget-drafted`
- `bounded-action-ready`
- `monitor-only-ready`
- `ask-before-action`
- `escalation-ready`
- `decision-blocked`
- `superseded`

Hard rule:

The header may not describe a charter as `action-ready` unless at least one threshold has been marked `cleared` and at least one stronger threshold has either been tested or explicitly marked out of scope.

### 2) Target-decision card

Required rows:

- target decision question
- target action being considered
- harm if action is delayed
- harm if action is premature
- governing scope
- excluded scopes

Supported `decision_target_class` values:

- `bounded-repair`
- `wait-and-monitor`
- `ask-for-one-more-fact`
- `heavy-capture-escalation`
- `publish-conclusion`
- `publish-warning-only`
- `halt-or-freeze`
- `external-handoff`

Hard rule:

One decision charter answers one named decision.
It may mention adjacent choices, but cannot quietly decide them too.

### 3) Threshold-ladder card

Render one row per candidate threshold.
Required fields:

- threshold name
- required basis class
- current threshold state
- why cleared or not cleared
- next cheapest upgrade path

Supported `threshold_name` values:

- `observe-only`
- `monitor-with-watch`
- `bounded-local-action`
- `cohort-action`
- `heavy-capture-escalation`
- `publish-claim`
- `close-case`

Supported `threshold_state` values:

- `cleared`
- `not-cleared`
- `blocked-by-conflict`
- `blocked-by-world-mismatch`
- `blocked-by-staleness`
- `deferred`
- `not-attempted`

Hard rule:

A higher threshold may not be implied from a lower one.
`monitor-with-watch` does not imply `bounded-local-action`.
`bounded-local-action` does not imply `publish-claim`.

### 4) Evidence-basis card

Required rows:

- active synthesis id
- packet classes relied on
- known contradictory packets
- freshness posture
- missing high-value source classes
- weighting note

Hard rule:

The decision page may not hide a contradiction that the synthesis page still marks unresolved.

### 5) Residual-uncertainty card

Required rows:

- uncertainty budget class
- concrete open questions
- acceptable uncertainty for this threshold
- uncertainty already consumed
- uncertainty that still blocks stronger action

Supported `uncertainty_budget_class` values:

- `minimal`
- `bounded-and-explicit`
- `moderate-but-tolerable`
- `too-large-to-spend`
- `unknown-because-world-fit-failed`

Hard rule:

`too-large-to-spend` must automatically block any row above `ask-for-one-more-fact`, `monitor-with-watch`, or `heavy-capture-escalation`.

### 6) Allowed-action card

Required rows:

- allowed next verb
- exact scope of permission
- safeguards required
- witness required after action
- expiry or rereview time

Supported `allowed_next_verb` values:

- `wait`
- `monitor`
- `ask`
- `apply-bounded-action`
- `escalate-capture`
- `freeze-or-halt`
- `publish-bounded-claim`
- `handoff-with-warning`

Hard rule:

Exactly one primary next verb must be named.
Secondary verbs can appear as contingencies only.

### 7) Blocked-stronger-action card

Required rows:

- strongest blocked verb
- what evidence gap blocks it
- what contradiction blocks it
- what cheaper path could unblock it
- safe fallback if never unblocked

Hard rule:

The blocked stronger action must be visible even when the allowed next verb looks obvious.

### 8) Decision sentence

Render exactly two lines:

- **Allowed action now**
- **Strongest blocked stronger action and why**

Hard rule:

If the primary next verb is `wait` or `monitor`, the second line must state what future event would re-open the charter automatically.
