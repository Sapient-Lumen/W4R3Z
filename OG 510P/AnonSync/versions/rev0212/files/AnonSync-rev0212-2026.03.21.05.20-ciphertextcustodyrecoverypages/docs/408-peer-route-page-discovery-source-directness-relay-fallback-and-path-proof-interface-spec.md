# Peer route page — discovery source, directness, relay fallback, and path proof interface spec

## Purpose

The archive already has generic route policy, performance metrics, and reachability doctrine.
What it still lacked was one ordinary peer-pair page for the question:

> for this exact pair, how did they find each other, what path are they actually using, and why is the path direct, relayed, slow, or failing?

Current official Resilio docs make the gap concrete.
They still say tracker supplies peer addresses, LAN discovery can reveal peers on multicast, predefined hosts can create direct dialing in constrained networks, direct is preferred for speed, relay is fallback when direct is blocked, relay is visibly slower, and listening-port / NAT / proxy / multicast failures shape which path survives.
That is useful truth.
It should not remain scattered across a peer list icon, a speed article, and a troubleshooting article.

## Core decision

AnonSync must expose one first-class **Peer route** page for every meaningful peer pair.

The page exists to answer five things in one place:

1. how the pair most recently found each other
2. what route class is currently active or currently failing
3. which concrete blocker prevents a stronger direct path
4. what performance and privacy implications follow from the active path
5. what exact next repair rung would improve the pair without unnecessary widening

## Fixed page order

1. **Pair route verdict**
2. **Discovery proof**
3. **Route-attempt ladder**
4. **Performance and privacy consequence**
5. **Next repair rung**

### 1) Pair route verdict

Show:

- `peer_route_page_id`
- local peer, remote peer, and subject
- current `route_verdict` (`lan-direct`, `wan-direct`, `relay`, `failing`, `unknown`)
- current `discovery_source` (`tracker`, `lan`, `known-host`, `mixed`, `unknown`)
- strongest honest summary
- last route change time

The operator must be able to answer:

> what path is this pair actually using right now?

### 2) Discovery proof

Show:

- most recent discovery source that produced contactable endpoint data
- whether endpoint data came from tracker, multicast, peer-pinned host, or remembered residue
- whether the proof is fresh, stale, or inherited from earlier wider posture
- whether discovery still works if the active session drops

The page must answer:

> if this session died now, how would the pair find each other again?

### 3) Route-attempt ladder

Show the last attempted classes in honest order, for example:

1. `lan-direct`
2. `wan-direct`
3. `relay`
4. `failed`

For each rung show:

- tried / skipped / blocked / succeeded
- blocker class (`listener-closed`, `nat-firewall`, `proxy`, `protocol-mismatch`, `multicast-unavailable`, `tracker-blocked`, `relay-blocked`, `unknown`)
- whether the blocker is local, remote, pairwise, or network-wide

This section should answer:

> why did the stronger path fail, and was fallback actually necessary?

### 4) Performance and privacy consequence

Show:

- active path speed class
- whether relay is the dominant reason for reduced throughput
- whether public infrastructure is currently in the discovery path, transit path, both, or neither
- whether the current pair posture is narrower, equal, or wider than desired policy

This section should prevent a relayed slow pair from looking like a neutral `connected` success.

### 5) Next repair rung

Actions may include:

- `Keep relay`
- `Open listening-port repair`
- `Verify firewall / NAT mapping`
- `Try verified known host`
- `Enable LAN multicast on this segment`
- `Allow tracker for discovery only`
- `Clear stale route residue`

Each action must preview whether it changes discovery, transport, both, or neither.

## Public object

### Peer route page

Fields:

- `peer_route_page_id`
- `subject_ref`
- `local_peer_ref`
- `remote_peer_ref`
- `discovery_source`
- `route_verdict`
- `attempt_rows[]`
- `active_protocol_hint` nullable
- `public_infra_role` (`none`, `discovery-only`, `relay-only`, `discovery-and-relay`, `unknown`)
- `performance_truth` (`best-known`, `relay-degraded`, `listener-limited`, `protocol-limited`, `unknown`)
- `next_repair_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. remote peer
2. discovery source
3. route verdict
4. strongest blocker or degradation reason
5. next repair rung

Example:

```text
Office NAS     tracker     relay     direct blocked by listener reachability     Open listening-port repair
```

## Non-goals

This page does **not** decide broader disclosure policy for the whole subject and does not replace the subject-wide reachability page.
It is for **this pair**, **this path**, and **this next repair decision**.

