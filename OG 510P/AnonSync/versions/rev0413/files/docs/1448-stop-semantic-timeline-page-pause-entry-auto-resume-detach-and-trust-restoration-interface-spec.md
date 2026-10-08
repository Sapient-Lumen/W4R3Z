# Stop-semantic timeline page: pause entry, auto-resume, detach, and trust restoration interface spec

## Purpose

After a suspension is armed, the product still needs one durable page for the events that change what the stop actually means over time:

> when did the bypass begin, what auto-resumed or expired, what detached, what re-armed, and when was trust actually restored versus merely unpaused?

## Core decision

AnonSync must expose one first-class **Stop-semantic timeline** for every suspension that lasts long enough to matter, crosses a boundary, or changes trust posture.

## Fixed page order

1. **Timeline header**
2. **Stop-history stream**
3. **Semantic-shift card**
4. **Expiry / reopen ladder**
5. **Trust-restoration card**
6. **Linked-object hooks**

### 1) Timeline header

Show:

- suspension id
- current active/inactive state
- current strongest safe sentence
- last arm or resume event
- next expiry or review
- current restoration state

Supported `current_restoration_state` values:

- `still-bypassed`
- `resume-requested`
- `resumed-but-unattested`
- `rearmed-and-partially-restored`
- `fully-restored`
- `expired-and-overstayed`

### 2) Stop-history stream

Each row must include:

- event time
- event class
- impacted scope
- old status
- new status
- withdrawn or restored sentence
- linked proof or case id

Supported `event_class` values:

- `bypass-armed`
- `schedule-window-entered`
- `schedule-window-ended`
- `environment-gate-entered`
- `environment-gate-cleared`
- `disconnect-performed`
- `peer-revocation-performed`
- `resume-requested`
- `resume-confirmed`
- `attestation-restored`
- `expiry-missed`
- `same-cause-escape-while-bypassed`

### 3) Semantic-shift card

When the selected timeline row changes meaning materially, show:

- what semantic changed
- old surviving effect
- new surviving effect
- whether auto-resume occurred
- whether manual re-arm is still required
- whether path / topology changed

Supported `semantic_shift_source` values:

- `entered-scheduled-pause`
- `left-scheduled-pause`
- `network-forbidden-now-active`
- `network-permitted-again`
- `disconnect-to-reconnect-state`
- `reconnect-created-new-path`
- `peer-access-revoked`
- `trust-restored-after-proof`

### 4) Expiry / reopen ladder

The page must preserve this ladder:

1. `active-within-window`
2. `active-needs-rereview`
3. `expired-but-still-bypassed`
4. `resume-attempted-but-untrusted`
5. `reopened-related-case-or-control`

Hard rule:

Overstayed bypasses must worsen posture even when no visible incident happened.

### 5) Trust-restoration card

Required rows:

- earliest point resume became possible
- actual point control effect returned
- actual point trust sentence returned
- witness that allowed restoration
- stronger sentence still blocked if any

Hard rule:

The timeline must preserve the gap between `activity resumed` and `trust restored` whenever that gap exists.

### 6) Linked-object hooks

Each hook must show:

- linked object type (case / rollout / control / policy)
- why it is linked
- whether it reopened automatically
- first required next page
- sentence withdrawn or restored there
