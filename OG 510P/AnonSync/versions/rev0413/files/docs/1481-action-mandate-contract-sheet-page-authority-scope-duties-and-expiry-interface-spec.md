# Action mandate contract sheet page: authority, scope, duties, and expiry interface spec

## Purpose

After the archive learned how to publish a reliance-safe packet, it still needed one ordinary page for the next operator question:

> does this recipient merely know something, or are they actually authorized or required to do something now?

## Core decision

AnonSync must expose one first-class **Action mandate contract sheet** whenever a certification, incident result, rollout decision, or remediation instruction is being turned into downstream action authority.

## Fixed page order

1. **Mandate header**
2. **Actor-and-authority card**
3. **Action-set card**
4. **Scope-and-preconditions card**
5. **Expiry-and-cancellation card**
6. **Decision sentence**

### 1) Mandate header

Show:

- action mandate id
- source reliance charter id
- source certificate / case / campaign ids
- issuing authority
- mandate owner
- issue time
- live status
- strongest currently safe action sentence

Supported `live_status` values:

- `drafting`
- `ready-to-issue`
- `issued-pending-acceptance`
- `issued-active`
- `issued-bounded`
- `superseded`
- `cancelled`
- `expired`
- `retired`

Hard rule:

A reliance charter may inform a recipient without granting action rights.
An action mandate is required once the recipient may approve, execute, or re-delegate work.

### 2) Actor-and-authority card

Required rows:

- target actor class
- named recipient or cohort
- authority class
- may re-delegate
- acceptance required
- source of authority

Supported `target_actor_class` values:

- `observer`
- `approver`
- `executor`
- `delegate-manager`
- `incident-commander`
- `successor-operator`
- `mixed-explicit-list`

Supported `authority_class` values:

- `inform-only`
- `observe-and-report`
- `approve-or-block`
- `execute-bounded`
- `execute-and-escalate`
- `execute-and-redelegate`
- `custodial-handoff-only`

Supported `acceptance_required` values:

- `none`
- `receipt-only`
- `accept-duty`
- `counter-sign-required`
- `dual-control-required`

Hard rule:

A role label like `operator` or `owner` is too weak by itself.
The mandate must say whether the recipient may observe, approve, execute, escalate, or re-delegate.

### 3) Action-set card

Required rows:

- allowed actions
- required actions
- forbidden actions
- optional actions needing recheck
- post-action proof expected
- stronger blocked overclaim

Supported `post_action_proof_expected` values:

- `none`
- `receipt-of-attempt`
- `execution-with-witness`
- `execution-and-outcome-proof`
- `execution-outcome-and-reconciliation-proof`

Hard rule:

A mandate must name both what the recipient may do and what they must not do.
`use your judgment` is illegal when the stronger sentence depends on bounded action.

### 4) Scope-and-preconditions card

Required rows:

- asset / scope covered
- excluded scope
- world / lane / platform boundary
- preconditions before action
- blocked-if conditions
- freshness dependency

Supported `freshness_dependency` values:

- `none`
- `must-be-current-at-start`
- `must-be-current-at-each-checkpoint`
- `expires-on-source-supersession`

Hard rule:

A mandate cannot float free of the world it was issued for.
If scope, platform, world, or preconditions differ, the authority must narrow accordingly.

### 5) Expiry-and-cancellation card

Required rows:

- expiry rule
- superseding event
- cancellation event
- in-flight action rule on cancel
- stale-copy risk class
- recall / cancel channel

Supported `in_flight_action_rule_on_cancel` values:

- `stop-immediately`
- `finish-current-step-then-hold`
- `complete-bounded-safe-close`
- `escalate-for-human-decision`

Supported `stale_copy_risk_class` values:

- `low`
- `moderate`
- `high`
- `severe`

Hard rule:

A mandate is incomplete if it says how to start but not how to stop when the source truth is superseded or recalled.

### 6) Decision sentence

Use:

> Issue mandate to [actor] with authority [class]. Allow [allowed actions]. Require [required actions]. Forbid [forbidden actions]. Cancel via [channel] on [event].

If blocked, use:

> Do not issue action authority yet. The recipient may currently rely only at [weaker level] because [missing authority element] blocks safe execution.
