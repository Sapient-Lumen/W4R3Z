# Duty-cycle timeline page: manual pause, scheduled zero-rate, sleep/wake, and power-gate events interface spec

## Purpose

The activity-posture sheet answers *what is true now*.
This page answers the operator's follow-on question:

> how did this node arrive here, when should I expect it to resume fuller work, and which events changed that posture over time?

## Core decision

AnonSync must require a **Duty-cycle timeline** whenever current activity posture depends on time-varying gates rather than a permanent capability.

## Timeline layout

1. **Current posture banner**
2. **Gate-transition sequence**
3. **Wake/resume forecast rail**
4. **Hidden-work intervals**
5. **Blocked stronger sentence**

### 1) Current posture banner

Show:

- current posture label
- entered-at time
- strongest safe sentence
- next expected posture-changing event if known
- blocked stronger sentence

### 2) Gate-transition sequence

Supported events:

- `manual-pause-enabled`
- `manual-pause-cleared`
- `scheduler-cap-entered`
- `scheduler-zero-rate-entered`
- `scheduler-window-exited`
- `sleep-entered`
- `wake-check-fired`
- `battery-floor-entered`
- `battery-floor-cleared`
- `forbidden-network-entered`
- `allowed-network-restored`
- `lan-cap-policy-changed`
- `unknown-transition`

Each event must show:

- timestamp
- cause class
- changed dimensions
- source evidence
- resulting strongest safe sentence

### 3) Wake/resume forecast rail

This rail must answer:

- is there a known schedule boundary?
- is there a next wake check interval?
- is resume contingent on charger, battery, or network change?
- is resume manual only?

Supported forecast states:

- `resume-at-known-time`
- `wake-at-known-interval`
- `resume-when-powered`
- `resume-when-allowed-network-returns`
- `manual-resume-required`
- `unknown`

### 4) Hidden-work intervals

This section preserves work that continued even in reduced activity states, including:

- indexing while paused
- delete propagation while paused
- upload service while download was blocked
- no peer visibility while asleep despite later wake checks

The operator must be able to answer:

> during which intervals did I incorrectly assume nothing was happening?

### 5) Blocked stronger sentence

Examples:

- `This node has been fully inactive since 09:00` blocked because indexing continued during a paused interval
- `This node resumed because the pause ended` blocked because actual resume waited for power or network conditions
- `This was one continuous outage` blocked because the device periodically woke and checked for work

## Hard rules

- the timeline must never collapse recurring wake checks into one generic `offline` block
- posture changes caused by time, operator choice, battery, and network must stay distinguishable
- forecast confidence must be explicit
- when the next resume trigger is external, the timeline must say so plainly
