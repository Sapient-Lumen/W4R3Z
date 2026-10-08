# Egress-only reachability review page, pairwise directness, relay inevitability, and disclosure-cost interface spec

## Purpose

The archive already had route classes, transfer budgets, and helper-infrastructure language.
What it still lacked was one explicit review page for a seat whose networking posture becomes asymmetric:

> this seat may dial out but cannot accept inbound direct connections — what changes about pairwise reachability, when does relay become inevitable, and what extra cost or infrastructure dependence follows?

Current official Resilio docs make this seam unusually plain.
They still say proxy servers prohibit incoming connections and allow only outgoing ones; that two proxied peers can talk only through relay; and that a single proxied peer can still connect directly outward to a non-proxied peer.
The relay article still says relayed transfer is slower than direct transfer.

That is not just a preference side effect.
It is a reviewed reachability posture.

## Core decision

Any seat that is egress-only must expose one explicit **reachability review** that computes pairwise outcomes rather than leaving them to folklore.
The product must never allow `proxy enabled` to behave like a harmless transport preference.

## Fixed review order

Every egress-only reachability review should render the same sections in the same order:

1. **Seat posture**
2. **Pairwise route matrix**
3. **Relay inevitability and cost**
4. **Disclosure and infrastructure dependence**
5. **Reversal path**

### 1) Seat posture

This section should show:

- posture class (`direct-capable`, `egress-only`, `egress-only-with-overlay`, `relay-bound`, `unknown`)
- origin (`reviewed policy`, `ambient environment detection`, `both`)
- dial classes still allowed
- inbound classes now unavailable

The operator must be able to answer: **is this seat still directly reachable, or only able to dial outward?**

### 2) Pairwise route matrix

This section should show, for each selected peer or peer cohort:

- `direct both ways`
- `direct outward only`
- `relay inevitable`
- `manual/private overlay required`
- `blocked`

The operator must be able to answer: **for this exact peer pairing, what is the best available path class?**

### 3) Relay inevitability and cost

This section should show:

- whether relay is `not needed`, `possible`, `preferred`, or `inevitable`
- expected throughput penalty class
- whether relay budget or policy ceilings apply
- whether the route depends on bootstrap authority still being available

The operator must be able to answer: **did this posture make relay optional, likely, or unavoidable?**

### 4) Disclosure and infrastructure dependence

This section should show:

- whether third-party or private relay infrastructure is now in the path
- whether pairwise metadata disclosure widened
- whether bootstrap/catalog dependence increased
- whether a private overlay would narrow that exposure again

The operator must be able to answer: **what new dependency or disclosure cost comes with the egress-only posture?**

### 5) Reversal path

The page must end with exactly one next restoration path:

- `restore inbound direct reachability`
- `pin private overlay`
- `accept relay-bound posture`
- `remove proxy policy`

## Public objects

### `egress_only_reachability_review`

Fields:

- `egress_only_reachability_review_id`
- `seat_ref`
- `posture_class`
- `origin`
- `pairwise_route_findings[]`
- `relay_requirement_summary`
- `cost_summary`
- `disclosure_dependency_summary`
- `recommended_reversal_action`
- `generated_at`

## Main surface

A compact row should read like one of these:

- `egress-only seat · direct outward only`
- `egress-only seat · relay inevitable with 4 peers`
- `proxy posture accepted · private overlay avoids public relay`
- `relay-bound seat · inbound direct unavailable`

## Event language

Use phrases such as:

- `seat became egress-only; inbound direct paths removed`
- `relay is now inevitable for this peer set`
- `one-way direct dialing preserved toward non-proxied peers`
- `private overlay restored non-relay reachability for selected peers`

Avoid phrases such as:

- `proxy enabled`
- `connected through relay`
- `slower network expected`

Those lines are too narrow and too late.

## CLI shape

```text
anonsync route posture review --seat self
anonsync route posture explain --peer atlas
anonsync route posture accept --seat self --posture egress-only
anonsync route posture receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- a proxied seat still looks generically `healthy`
- the operator discovers relay inevitability only after throughput drops
- pairwise asymmetry is hidden behind one generic route icon
- public relay dependence can widen without one reviewed disclosure/dependency section

## Non-clone reason

Current official Resilio docs still make proxy consequences feel like one settings note plus later troubleshooting.
AnonSync should instead render egress-only posture, pairwise directness, relay inevitability, and dependency cost as one ordinary review.
