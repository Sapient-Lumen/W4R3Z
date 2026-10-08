# Mandate shaping review page: inform, observe, decide, execute, and escalate routing interface spec

## Purpose

Operators need one page that answers:

> given this packet and this recipient, are we informing them, asking them to watch, asking them to approve, asking them to execute, or asking them to take custody and route further?

## Core decision

AnonSync must separate downstream action into typed routes instead of letting one generic `notify` or `assign` verb carry too much meaning.

## Fixed page order

1. **Source summary rail**
2. **Recipient routing matrix**
3. **Action-authority conflict review**
4. **Cancellation and supersession review**
5. **Decision footer**

### 1) Source summary rail

Show:

- source reliance charter
- source certificate / case / campaign
- source safe sentence
- source blocked stronger sentence
- source freshness state
- source recall posture

Hard rule:

No route may be stronger than the source charter permits.

### 2) Recipient routing matrix

Each candidate recipient row must show:

- recipient / cohort
- chosen route
- why this route and not a stronger one
- acceptance class
- evidence payload carried
- first required checkpoint

Supported `chosen_route` values:

- `inform-only`
- `watch-and-report`
- `approve-or-block`
- `execute-bounded-step`
- `execute-sequence`
- `take-custody-and-redelegate`
- `no-safe-route`

Hard rule:

A recipient cannot land on `execute` if they only have reliance truth but no bounded authority.

### 3) Action-authority conflict review

Show conflicts for:

- source claim too weak for requested route
- actor role too broad or too vague
- recipient has technical reach but no delegated authority
- recipient has authority but lacks prerequisites
- re-delegation would escape source scope
- world / platform mismatch

Supported `conflict_outcome` values:

- `downgrade-to-inform`
- `downgrade-to-watch`
- `split-route`
- `require-counter-sign`
- `block-route`

Hard rule:

Technical ability does not grant action authority.
Operational seniority does not erase preconditions.

### 4) Cancellation and supersession review

Required rows:

- active superseding sources that would cancel this route
- stale-copy exposure risk
- recipients with queued work but no live link
- in-flight cancellation behavior
- recall acknowledgement gap
- human escalation fallback

Hard rule:

AnonSync must show which downstream routes remain dangerous because a stale packet may still be sitting in someone’s queue.

### 5) Decision footer

Use:

> Route [recipient] as [route]. Carry [evidence]. Require [checkpoint]. Downgrade or block [other route] because [reason].

If no route is safe, use:

> No safe downstream route yet. Keep the recipient at [weaker relation] until [authority or freshness gap] is resolved.
