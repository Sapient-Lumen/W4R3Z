# Applicability proof page: governing doctrine, distinction gaps, and safe next claim interface spec

## Purpose

After the archive learned how to compare lookalike routes, it still needed one proof page that answers:

> what doctrine currently governs this case, what facts earned that routing, what uncertainty remains, and what stronger sentence is still blocked until more is learned?

## Core decision

AnonSync must expose one first-class **Applicability proof** page whenever a case is materially routed into governing doctrine, provisional doctrine, or an explicit no-current-governing-route state.

## Fixed page order

1. **Routing summary card**
2. **Fact-pattern proof card**
3. **Competing-route disposition card**
4. **Open-gap card**
5. **Safe-next-claim card**
6. **Decision sentence**

### 1) Routing summary card

Required rows:

- current governing route or doctrine
- routing class
- case owner
- adoption time
- current status

Supported `routing_class` values:

- `confirmed-governing-doctrine`
- `provisional-governing-doctrine`
- `cross-route-safe-containment-only`
- `human-adjudication-required`
- `no-current-governing-doctrine`

### 2) Fact-pattern proof card

Required rows:

- key facts that justify the route
- key facts that would have supported rejected routes
- strongest missing fact if any
- witness contradictions if any
- why the current route is still safer than alternatives

Hard rule:

Applicability proof must prove the route against the alternatives, not merely restate the selected doctrine.

### 3) Competing-route disposition card

For each competing route, show:

- route name
- disposition
- decisive fact or lack of fact
- whether it can re-open later
- what evidence would revive it

Supported `route_disposition` values:

- `ruled-out`
- `suppressed-pending-fact`
- `still-live-but-weaker`
- `kept-as-reopen-candidate`
- `promoted-to-co-governing-risk`

Hard rule:

Rejected routes must not disappear.
The proof must preserve why they lost and how they could return.

### 4) Open-gap card

Required rows:

- unresolved factual gap
- impact of that gap on action
- rereview trigger
- expiry for provisional confidence
- stronger claim blocked by the gap

Hard rule:

Open gaps must weaken the claim ceiling explicitly.
A proof with unresolved gaps may not present itself as fully settled.

### 5) Safe-next-claim card

Required rows:

- strongest currently safe routing sentence
- strongest blocked overclaim
- actions safe under current routing
- actions forbidden until gap closure
- evidence that would unlock the stronger claim

Hard rule:

The proof must speak in claim ceilings, not vibes.

### 6) Decision sentence

Render one sentence only:

- `Current applicability is [routing_class]; governing doctrine is [route], justified by [fact basis], with [open gap] still blocking [stronger claim].`

## Required interactions

- **Confirm governing doctrine**
- **Downgrade to provisional**
- **Preserve reopen candidate**
- **Record blocked stronger claim**
- **Trigger rereview**

## Failure state

If no doctrine currently governs, show:

- `No governing doctrine proved yet. Only cross-route-safe containment or fact-capture actions are justified.`
