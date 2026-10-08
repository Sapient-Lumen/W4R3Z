# Telemetry consent page: data family, carrier, and retention scope interface spec

## Purpose

The most ordinary diagnostics question is not `how do I debug this?`
It is:

> what kinds of operational data does this product observe or emit even before I start an incident-specific capture?

AnonSync should therefore model ongoing low-grade observation as a reviewed **telemetry consent page** rather than burying it in advanced settings.

## Core decision

The page must distinguish at least four data families:

1. **Product heartbeat / statistics**
2. **Local debug logs**
3. **Incident profiler traces**
4. **Crash / fault artifacts**

These families may share storage or transport, but they must never share one vague label.

## Fixed review order

Every telemetry-consent page should render sections in this order:

1. **Data families**
2. **Default posture**
3. **Possible carriers**
4. **Retention scope**
5. **Operator actions**

## Data families

For each family show:

- what it is for
- whether it is on by default, opt-in, incident-only, or fault-triggered
- whether it is local-only, send-capable, or always outbound
- whether personal content, filenames, topology, or host facts may appear

## Default posture

The page must say plainly:

- what the product is already collecting
- what is dormant but not yet collecting
- what would start only after explicit operator action
- which actions require restart to actually take effect

## Possible carriers

Render the possible ways a family can move:

- stays local only
- included in outbound support/feedback send
- exported as a manual bundle
- copied by the operator from local storage
- not sendable from this surface

## Retention scope

Show:

- local retention budget or rotation rule
- whether the artifact lives in hidden application storage
- whether expiry is time-based, size-based, or event-based
- whether the product can attest that a family is fully gone

## Operator actions

The page must offer explicit verbs:

- enable / disable
- escalate to profiler
- open local retention page
- preview send bundle
- export manual bundle

## Anti-clone rule

Do not collapse anonymous statistics, debug logs, profiler traces, and crash dumps into one `Diagnostics` toggle.
