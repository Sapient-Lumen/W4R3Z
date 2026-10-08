# Control activation proof page: rollout, owner, rereview, and does-not-protect interface spec

## Purpose

After promotion review selects a guardrail verdict, the archive still needs one explicit page for the next operator question:

> how do we activate this guardrail honestly, prove who owns it, and preserve what it still does not protect against?

## Core decision

AnonSync must expose one first-class **Control activation proof** before a promoted control can claim `active` posture.

## Fixed page order

1. **Activation header**
2. **Activation target and owner card**
3. **Apply proof card**
4. **Effectiveness watch contract**
5. **Does-not-protect card**
6. **Rereview and expiry card**

### 1) Activation header

Show:

- control id
- chosen rollout class
- approver
- implementer
- activation time
- post-activation watch window
- rollback class
- proof state

Supported `chosen_rollout_class` values:

- `single-subject-test`
- `canary-cohort`
- `profile-revision`
- `config-fleet-apply`
- `world-specific-activation`
- `watch-only-no-mutation`

### 2) Activation target and owner card

Required rows:

- exact target subjects
- excluded subjects
- owning team or person
- escalation owner on escape
- service/config authority owner
- rereview owner

Hard rule:

A control without a named rereview owner may not move to `active`.

### 3) Apply proof card

Each activation must publish:

- what changed
- where it changed
- whether restart or cold-apply occurred
- whether activation succeeded everywhere
- what partial failures remain
- what proof inputs were captured
- what stronger statement is still blocked until the watch window ends

Supported `proof_state` values:

- `applied-not-yet-watched`
- `partially-applied`
- `watching-for-effect`
- `effective-within-claim-ceiling`
- `escaped-on-first-repeat`
- `superseded-before-proven`

### 4) Effectiveness watch contract

Required fields:

- watch window length
- repeat threshold
- near-miss threshold
- signal sources
- automatic reopen conditions
- confidence upgrade rule
- confidence downgrade rule

Supported `confidence_upgrade_rule` values:

- `no-repeat-during-window`
- `near-miss-caught-within-window`
- `same-hazard-blocked`
- `same-hazard-detected-earlier-only`

Hard rule:

`no-repeat-during-window` may increase confidence, but must not by itself upgrade a detective watch into a true preventive control.

### 5) Does-not-protect card

This section is mandatory and prominent.
Each row must show:

- non-covered hazard or world
- why it is not covered
- operator risk if misunderstood
- whether there is a companion watch or playbook

Example rows:

- `does not protect service worlds created by clean install`
- `does not protect versions missing the required power-user preference`
- `does not protect the same symptom when the cause family is identity corruption instead of watcher exhaustion`

### 6) Rereview and expiry card

Publish:

- expiry date or review cadence
- version-change rereview trigger
- platform/world-drift trigger
- entitlement or lane-change trigger
- repeated-escape trigger
- retirement or supersession path

Hard rule:

A control whose prerequisites or mechanism are version-dependent must auto-schedule rereview on version-floor change.
