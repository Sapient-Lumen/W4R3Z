# Battery saver, auto-sleep, and participation-honesty interface spec

## Purpose

The archive already had pause semantics, suspended-seat resume, and constrained-seat capability language.
What it still lacked was one explicit contract for another very common but semantically slippery case:

> a seat whose participation in the mesh is intentionally intermittent because of battery policy, sleep cadence, charging state, or platform resource posture.

Current official Resilio docs make this seam sharper than a generic `mobile background is limited` shrug.
They still say Android Auto Sleep can stop Sync when no transfers are in progress, can wake only on a configured interval, and can use a different interval while charging.
They also still say peers do not see the device as online while the core is asleep, and that Battery Saver can force Sync to stop below a chosen charge threshold.

That is all operationally real.
It is still not a good participation contract.
An operator should not have to infer whether a seat is live, sleeping on purpose, power-blocked, or merely broken from a single `offline` badge.

## Core decision

AnonSync should treat power policy as part of the public participation contract.
Every seat must therefore publish four separate truths:

- whether it is technically capable of continuous participation
- whether local policy currently allows continuous participation
- what cadence it will use when conserving power
- what other peers should infer when the seat is absent

A sleeping seat must never masquerade as a mysterious failed seat, and a battery-blocked seat must never masquerade as an operator-approved semantic pause.

## Why this matters

Current Resilio docs still reveal four interface mistakes AnonSync should not clone:

- power conservation can deliberately take the core offline while looking externally like an ordinary disappearance
- wake cadence can change by charging state, which means `online enough` is conditional rather than one stable property
- battery floor can force a stop without one shared participation receipt that other operators can inspect later
- background availability, sleep cadence, and power stop can all affect freshness and confidence even before any explicit conflict is visible

AnonSync should therefore keep one stronger rule:

> power policy is not just device preference; it is a shared liveness contract.

## Fixed review order

Every constrained or power-managed seat should render the same sections in the same order:

1. **Participation class now**
2. **Cadence and wake promises**
3. **Absence interpretation**
4. **Power-policy receipt**

### 1) Participation class now

This section should show:

- continuous participation supported or not
- current power mode:
  - continuous
  - idle-sleep eligible
  - scheduled wake only
  - charging-boosted cadence
  - battery-blocked
  - runtime-killed / unplanned suspension
- whether the seat is currently visible to peers
- which policy or runtime fact set that state

The operator must be able to answer: **is this seat absent because it is conserving power, because it is blocked, or because it is actually unhealthy?**

### 2) Cadence and wake promises

This section should show:

- idle-to-sleep threshold if any
- wake interval while on battery
- wake interval while charging
- whether local changes wake the seat immediately or only on schedule
- whether remote arrivals wait for the next wake cycle

The operator must be able to answer: **how stale can this seat honestly become before that is surprising?**

### 3) Absence interpretation

This section should show:

- what peers should infer from the seat being absent
- freshness confidence under the current cadence
- whether conflict or resume review is likely if local edits accumulate during absence
- whether alerts should classify absence as expected, overdue, or suspicious

The operator must be able to answer: **what does `offline` mean for this seat right now?**

### 4) Power-policy receipt

This section should show:

- policy chosen
- cadence chosen
- battery stop floor if any
- charging override if any
- effect on visibility and freshness promises
- whether the policy is seat-wide or subject-scoped

The operator must be able to answer: **what participation promise did I actually configure?**

## Main surface

AnonSync should expose a compact seat row such as:

- `continuous participant`
- `scheduled-wake seat · every 30m on battery`
- `charging boost · every 5m while plugged in`
- `battery floor active below 20%`
- `absence currently expected under power policy`

The product must never let `offline` be the only public truth when the real cause is reviewed power cadence.

## Object model implications

AnonSync should add or strengthen these objects:

- `seat_participation_class`
- `power_policy_review`
- `wake_cadence_contract`
- `absence_interpretation`
- `power_policy_receipt`

Suggested fields for `wake_cadence_contract`:

- `seat_id`
- `continuous_supported`
- `idle_sleep_enabled`
- `battery_wake_interval`
- `charging_wake_interval`
- `battery_stop_floor_percent`
- `peer_visibility_when_sleeping`
- `freshness_confidence_budget`

## Event language

Use explicit phrases such as:

- `seat entered scheduled sleep under reviewed power policy`
- `seat hidden from peers while core is asleep`
- `battery floor stopped participation`
- `charging cadence override enabled`
- `absence remains expected under current wake contract`

Avoid vague lines such as:

- `device offline`
- `background disabled`
- `sync may be delayed`

## CLI shape

Example commands:

```text
anonsync seat power show <seat>
anonsync seat power review <seat>
anonsync seat power apply <review> --wake 30m --charging-wake 5m --stop-below 20
anonsync seat power receipt <id>
```

The CLI must expose the same cadence and absence-meaning truth as the local web UI.

## Failure and edge cases

### Charging cadence differs from battery cadence

The product must show both, not just the currently active one.
Otherwise operators will misread resumed bursts as mysterious intermittence.

### Runtime was killed outside reviewed policy

That is not `scheduled sleep`.
It should be classified as unplanned suspension and may feed directly into the resume-quarantine flow.

### Operator wants aggressive battery saving

That is allowed.
The product must still publish the resulting freshness and visibility downgrade before apply.

## The non-clone reason

This is another clean example of why AnonSync should not merely copy Resilio's surface.
Current official Resilio docs still leave too much meaning about wake cadence, battery floors, and peer visibility scattered across mobile settings pages.
AnonSync should instead publish one participation contract where power policy, absence meaning, and freshness cost stay visible together.
