# Duty-cycle timeline page — opportunity windows, gate changes, and late-claim context interface spec

## Purpose

The archive already had posture-drift and incident timelines.
What it still lacked was one ordinary timeline for the question:

> over the period we care about, when was this seat actually capable of observing or acting, and when was it asleep, blocked, foreground-only, or merely waiting for its next window?

AnonSync should therefore publish a dedicated **duty-cycle timeline** whenever lateness or missed observation is under review.

## Core decision

The timeline must align wall-clock time with duty state so the operator can stop guessing.
It must preserve six event families:

1. runtime present vs absent
2. background eligible vs ineligible
3. wake windows
4. rescan windows
5. network/source eligibility windows
6. claim / receipt issuance and expiry

## Fixed page order

1. **Timeline verdict strip**
2. **Duty-state lane**
3. **Opportunity-window lane**
4. **Gate-change lane**
5. **Claim / receipt lane**
6. **Review actions**

## 1) Timeline verdict strip

Show:

- covered interval
- current duty class
- next opportunity label
- strongest late-claim sentence currently allowed

## 2) Duty-state lane

Segment time into states such as:

- continuous runtime
- sleeping between wakes
- foreground-only idle
- fully stopped
- blocked by battery
- blocked by network policy
- rescan-backed observation only

## 3) Opportunity-window lane

Render concrete windows such as:

- wake window opened / closed
- periodic rescan began / ended
- foreground session began / ended
- network eligibility restored / lost
- source presence available / absent

Every window must say whether it created a real observation chance.

## 4) Gate-change lane

Show causal flips, including:

- notifications disabled
- auto-sleep enabled or interval changed
- battery saver threshold crossed
- Wi-Fi-only / forbidden network entered or exited
- watcher exhaustion detected or repaired
- runtime stopped or resumed

## 5) Claim / receipt lane

Overlay:

- freshness claim issued
- invalidated
- late-claim tested
- opportunity receipt issued
- superseded

## 6) Review actions

Examples:

- open next observation opportunity
- open late-claim review
- compare posture drift
- run reviewed revalidation

## Compact rendering obligations

A compact timeline summary must still preserve:

- covered interval
- count of real opportunity windows
- current late-claim status
- strongest missing prerequisite

## Anti-clone rule

Do not clone products where the operator still has to infer from scattered settings and status memories when the seat was actually duty-capable during the interval under dispute.
