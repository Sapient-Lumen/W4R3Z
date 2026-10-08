# Egress-only proxy and relay-inevitability interface spec

## Purpose

The archive already has route classes, transfer budgets, and disclosure policy.
What it still lacked was one explicit contract for a very particular transport posture:

> when a seat is placed behind an egress-only proxy, what changes about direct reachability, inbound expectations, and relay inevitability, and how does the product keep that from masquerading as ordinary degraded networking?

Current official Resilio docs make this seam explicit.
They still say proxy servers prohibit incoming connections and allow only outgoing ones, and that if two Sync instances are both behind a proxy they will be able to talk only via relay; only when one side is behind a proxy can that proxied side still connect directly to the other side.
A connectivity troubleshooting page still folds proxy cases into the same tracker/relay story unless the operator manually reconstructs what that means.

That is not just a settings detail.
It is an asymmetric reachability contract.

AnonSync should therefore treat egress-only proxy posture as one first-class seat property with route consequences rendered up front.

## Core decision

Any seat whose transport is mediated by an egress-only proxy must declare a first-class **reachability asymmetry posture**.
That posture must compile into route explanations, peer compatibility, expected bottlenecks, and honest next steps.

The product must never let `proxy enabled` behave like a harmless transport preference.
For sync semantics it means:

- inbound direct path classes are narrowed or gone
- direct success becomes topology-dependent and asymmetric
- some peer pairings become relay-inevitable unless other explicit private infrastructure exists
- transfer performance and disclosure trade-offs change accordingly

## Fixed review order

Every proxy-mediated transport review should render the same sections in the same order:

1. **Seat reachability posture**
2. **Peer-pair compatibility**
3. **Relay inevitability and cost**
4. **Receipt and reversal**

### 1) Seat reachability posture

This section should show:

- whether the seat is `direct-capable`, `egress-only`, `egress-only-with-overlay`, or `unknown`
- which dial classes remain allowed
- which accept/inbound classes are no longer possible
- whether the posture comes from reviewed policy, ambient environment detection, or both

The operator must be able to answer: **is this seat still directly reachable, only able to dial out, or fully asymmetrical?**

### 2) Peer-pair compatibility

This section should show, for any selected peer pair:

- direct possible
- direct possible only one way
- relay required
- overlay/private-rendezvous required
- blocked by policy

The operator must be able to answer: **for this exact pair, is relay merely allowed, or inevitable?**

### 3) Relay inevitability and cost

This section should show:

- whether relay is optional, preferred, or unavoidable
- whether any relay/private-overlay budget applies
- expected throughput penalty class
- any widened disclosure or infrastructure dependence that follows from the posture

The operator must be able to answer: **what cost and dependency did the proxy posture just buy me?**

### 4) Receipt and reversal

This section should show:

- posture before/after
- whether the seat became egress-only by policy or by detected environment
- which peer-pair route classes changed
- what is required to restore inbound/direct capability

The operator must be able to answer: **what later proves that the seat became relay-bound, and what would undo that?**

## Public objects

### `seat_reachability_posture`

Fields:

- `seat_reachability_posture_id`
- `seat_ref`
- `posture_class` (`direct-capable`, `egress-only`, `egress-only-with-overlay`, `relay-bound`, `unknown`)
- `origin` (`policy`, `detected`, `policy-and-detected`)
- `allowed_dial_classes[]`
- `allowed_accept_classes[]`
- `proxy_ref` nullable
- `updated_at`

### `peer_pair_route_compatibility`

Fields:

- `peer_pair_route_compatibility_id`
- `seat_a_ref`
- `seat_b_ref`
- `direct_posture`
- `relay_requirement` (`not-needed`, `possible`, `inevitable`, `blocked`)
- `best_available_route_class`
- `cost_notes[]`
- `generated_at`

### `reachability_posture_receipt`

Fields:

- `reachability_posture_receipt_id`
- `seat_ref`
- `before_summary`
- `after_summary`
- `pairwise_delta_summary`
- `created_at`

## Main surface

A compact row should read like one of these:

- `direct-capable seat`
- `egress-only seat · inbound direct unavailable`
- `egress-only seat · relay inevitable with 3 peers`
- `egress-only via reviewed proxy · private overlay available`

## CLI shape

```text
anonsync route posture show --seat self
anonsync route posture explain --peer tablet-citrine
anonsync route posture review --proxy corp-egress
anonsync route posture receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- a proxied seat still appears merely `online` or `healthy` without saying it cannot accept inbound direct paths
- relay inevitability is reconstructed only after slow transfers start
- pairwise asymmetry stays hidden behind one generic route icon
- turning on a proxy silently changes route cost and disclosure posture without a receipt

## Non-clone reason

Resilio's current docs still make proxy behavior feel like one preference line and later troubleshooting notes, even though it changes directness asymmetrically and can make relay unavoidable for some peer pairs.
AnonSync should instead make egress-only posture and relay inevitability explicit.
