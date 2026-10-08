# Representativeness review page — pairwise measurement, swarm coverage, and generalization ceiling interface spec

## Purpose

The archive already had performance hypothesis review.
What it still lacked was one fixed page for another ordinary question:

> is this pairwise result actually allowed to stand in for the rest of the swarm, and if not, what stronger coverage is still required?

AnonSync should therefore add a dedicated **representativeness review page** before any pairwise result is promoted into share-wide language or tuning guidance.

## Core decision

A pairwise result must never become a mesh-wide claim without an explicit representativeness verdict.
The review page exists to publish that verdict and the ceiling on how far the result can travel.

## Fixed review order

1. **Candidate result to promote**
2. **Similarity basis**
3. **Counterexample search**
4. **Generalization ceiling**
5. **Next cheapest widening step**

## 1) Candidate result to promote

Show the specific result under review:

- benchmark or live observation identity
- peer pair involved
- direction(s) covered
- route class covered
- candidate statement to promote

Example candidate statements:

- `network ceiling is not the dominant limiter for this pair`
- `relay penalty dominates for this route segment`
- `slow source uploader is the dominant limiter for these receivers`

## 2) Similarity basis

Score the basis for treating other peers as similar:

- same uploader source
- same network / route class
- same LAN/WAN locality
- same policy/helper posture
- same hardware/resource class
- same workload shape window

The page should make weak similarity visible instead of letting the operator hand-wave it.

## 3) Counterexample search

Require an explicit search for peers or directions that could break the claim, for example:

- another uploader with materially different uplink
- receivers on relay while measured pair was direct
- peers on different LAN/VPN segment
- peers with different helper settings or known hosts
- one direction not yet tested

Each candidate counterexample gets one status:

- `checked and consistent`
- `checked and contradictory`
- `plausible but untested`
- `out of scope by design`

## 4) Generalization ceiling

The page must output one ceiling class:

- `pair-only`
- `direction-only`
- `uploader-cohort`
- `route-segment`
- `share-wide provisional`
- `share-wide strongly supported`

Also publish the forbidden stronger sentence.
For example:

- allowed: `For uploader A to receivers B/C on relayed WAN paths, relay penalty dominates.`
- forbidden: `The whole share is network-limited.`

## 5) Next cheapest widening step

If the ceiling is below the desired claim, the page must propose the cheapest honest widening step, such as:

- test reverse direction
- add one counterexample peer on different route class
- measure one stronger uploader
- widen from pairwise to route-segment slice
- widen from route-segment to all active uploaders

## Compact rendering obligations

Any compact summary for a promoted performance claim must still preserve:

- candidate statement
- evidence slice version
- generalization ceiling
- strongest allowed sentence
- next widening step if ceiling is insufficient

## Anti-clone rule

Do not clone workflows where a neat benchmark or peer-row story silently becomes a share-wide explanation without an explicit ceiling and a visible counterexample search.
