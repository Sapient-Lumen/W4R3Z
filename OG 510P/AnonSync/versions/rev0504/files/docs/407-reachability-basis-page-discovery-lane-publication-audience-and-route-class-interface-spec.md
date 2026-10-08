# Reachability basis page — discovery lane, publication audience, and route class interface spec

## Purpose

The archive already has route exposure, discovery publication, known-host policy, and endpoint disclosure coverage.
What it still lacked was one ordinary page for the simpler question:

> when this subject or peer pair is `reachable`, what exact discovery lane, publication audience, and route class currently make that true?

Current official Resilio docs make this seam concrete.
They still say peers may be found through tracker, LAN discovery, or predefined hosts; tracker learns share identity plus local/public endpoint facts; LAN discovery multicasts share identity and `IP:port`; relay is a slower fallback when direct connection is impossible; and route residue can survive a later `LAN only` tightening until cache is cleared.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Reachability basis** page for every subject with active or recently attempted peer discovery, and one focused variant for any peer pair under review.

The page exists to answer five things in one place:

1. which discovery lanes are currently enabled and actually contributing
2. which audience currently learns reachability facts
3. what route class currently carries traffic or would carry it first
4. what remembered endpoint residue still influences effective reachability
5. what least-widening next action would strengthen or narrow the posture

## Fixed page order

1. **Current reachability verdict**
2. **Discovery lanes in force**
3. **Publication audience and facts**
4. **Current route class and performance honesty**
5. **Least-widening next actions**

### 1) Current reachability verdict

Show:

- `reachability_basis_page_id`
- subject scope and optional peer-pair scope
- current `discovery_basis_class` (`tracker`, `lan`, `known-host`, `mixed`, `none`, `unknown`)
- current `route_class` (`lan-direct`, `wan-direct`, `relay`, `mixed`, `none`, `unknown`)
- strongest honest summary
- last materially route-shaping event time

The operator must be able to answer:

> what mechanism currently makes this reachability claim true?

### 2) Discovery lanes in force

Show:

- tracker enabled / disabled / blocked
- LAN discovery enabled / disabled / blocked / subnet-limited
- known-host dialing enabled / disabled and whether any verified host rows exist
- relay enabled / disabled / blocked
- whether protocol/common-lane mismatch narrows usable paths

The page must make it ordinary to answer:

> if the current direct path disappears, what other lane would still allow the peers to find each other?

### 3) Publication audience and facts

Show:

- which audience classes currently learn about this subject or pair (`lan-neighbors`, `approved-public-infra`, `peer-pinned-targets`, `none`, `mixed`)
- what exact facts are currently exposed (`share handle`, `local endpoint`, `public endpoint`, `known-host target`, `relay eligibility`, `none`)
- whether exposure comes from baseline policy or remembered endpoint residue
- whether tightening the posture still requires cache clearance to become true in practice

The page must answer:

> who currently learns what because this discovery posture is active?

### 4) Current route class and performance honesty

Show:

- active or expected route class
- whether the current path is direct or relayed
- whether relay or proxy is the main honesty reason for reduced speed
- whether the route class is privacy-narrower, privacy-wider, or performance-stronger than baseline intent

This section must not hide a relayed or publicly discovered pair behind a generic `connected` badge.

### 5) Least-widening next actions

Actions may include:

- `Keep current posture`
- `Verify known host`
- `Open pair route page`
- `Repair direct listening path`
- `Enable relay as fallback`
- `Tighten to LAN only and clear residue`
- `Clear remembered public endpoints`

Each action must preview the resulting discovery basis, audience delta, and route-class delta.

## Public object

### Reachability basis page

Fields:

- `reachability_basis_page_id`
- `subject_ref`
- `peer_pair_ref` nullable
- `discovery_basis_class`
- `route_class`
- `audience_class` (`lan-only`, `peer-pinned`, `approved-public-infra`, `mixed`, `none`, `unknown`)
- `fact_rows[]`
- `tracker_state` (`enabled`, `disabled`, `blocked`, `unused`, `unknown`)
- `lan_discovery_state` (`enabled`, `disabled`, `blocked`, `subnet-limited`, `unused`, `unknown`)
- `known_host_state` (`enabled`, `disabled`, `configured`, `verified`, `stale`, `unknown`)
- `relay_state` (`enabled`, `disabled`, `blocked`, `unused`, `unknown`)
- `protocol_overlap_state` (`sufficient`, `limited`, `none`, `unknown`)
- `residue_state` (`none-known`, `present-benign`, `present-widening-risk`, `unknown`)
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. subject / peer pair
2. discovery basis
3. route class
4. audience class
5. next least-widening action

Example:

```text
Laptop ↔ NAS     known-host     wan-direct     peer-pinned     Verify known host
```

## Non-goals

This page does **not** prove that bytes are already synchronized, that the pair is healthy under load, or that the current route is the globally fastest possible route.
It proves only the current **reachability basis** and the current disclosure/route truth that follows from it.

