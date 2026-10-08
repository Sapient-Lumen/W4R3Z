# Fact-pattern routing review page: symptom lookalikes, disqualifiers, and next best question interface spec

## Purpose

After the archive learned how to stage candidate doctrine, it still needed one ordinary workspace for the next harder question:

> among these lookalike routes, which one actually deserves to govern this case, which ones are still alive only because we lack one fact, and what question should we ask next instead of guessing?

## Core decision

AnonSync must expose one first-class **Fact-pattern routing review** page whenever multiple lookalike doctrines or warning families are still plausibly competing for the same case.

## Fixed page order

1. **Review header**
2. **Lookalike-stack card**
3. **Discriminator matrix card**
4. **Evidence-channel card**
5. **Route-reversal risk card**
6. **Proposed governing route card**
7. **Decision sentence**

### 1) Review header

Show:

- routing review id
- active case id
- number of live lookalike routes
- review owner
- current routing risk
- strongest currently safe sentence

Supported `routing_risk` values:

- `low-misroute-risk`
- `moderate-misroute-risk`
- `high-misroute-risk`
- `unknown-routing-risk`

### 2) Lookalike-stack card

For each active lookalike route, show:

- route name
- doctrine or article family behind it
- strongest fact supporting it
- strongest fact against it
- current fit class
- harm if misapplied

Hard rule:

The page must support simultaneous review of several lookalike routes.
Operators should not have to compare them serially in memory.

### 3) Discriminator matrix card

Required rows:

- key distinguishing facts by route
- facts already known
- facts still unknown
- facts contradicted by current witnesses
- cheapest reliable discriminator
- highest-value discriminator

Hard rule:

The matrix must show which routes are separated by which facts.
A review is incomplete if it only lists routes without the factual splits between them.

### 4) Evidence-channel card

Required rows:

- evidence channels available now
- evidence channels unavailable now
- latency/cost to obtain each channel
- witness reliability concerns
- who must be involved for each channel

Hard rule:

The next best question is inseparable from where the answer can actually come from.
A perfect discriminator that cannot be observed now is weaker than a good discriminator that can.

### 5) Route-reversal risk card

Required rows:

- why the leading route might still be wrong
- what new fact would reverse the route
- what damage an early misroute would cause
- whether interim-hold action is required
- what action can still proceed safely across all live routes

Hard rule:

If a route reversal would materially change action, the page must publish that risk before any stronger routing claim.

### 6) Proposed governing route card

Supported `proposed_route_verdict` values:

- `route-now-governing`
- `route-now-provisional`
- `hold-for-primary-discriminator`
- `route-to-dual-path-containment`
- `escalate-for-adjudication`
- `declare-no-current-governing-route`

Required rows:

- proposed route verdict
- governing route if any
- explicit routes ruled out
- explicit routes still alive
- next question if not final
- strongest blocked sentence if not final

Hard rule:

A provisional route must preserve which alternatives are still alive.
The interface may not present provisional routing as settled doctrine.

### 7) Decision sentence

Render one sentence only:

- `Routing review currently [proposed_route_verdict]; leading route is [route], live alternatives are [routes], and the next best distinguishing question is [question].`

## Required interactions

- **Raise new lookalike route**
- **Mark route disqualified**
- **Promote discriminator**
- **Switch to dual-path containment**
- **Escalate for adjudication**

## Failure state

If the case still has no reliable discriminator, show:

- `No reliable discriminator yet. Only cross-route-safe actions may proceed.`
