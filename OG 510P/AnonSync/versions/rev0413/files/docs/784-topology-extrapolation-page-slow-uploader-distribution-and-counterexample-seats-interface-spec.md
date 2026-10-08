# Topology extrapolation page — slow-uploader distribution and counterexample seats interface spec

## Purpose

The archive already had throughput expectation and representativeness review.
What it still lacked was one fixed page for another ordinary question:

> given what we measured, how does this likely extrapolate across the rest of the active topology, and where could the story still break?

AnonSync should therefore expose a first-class **topology extrapolation page** whenever the system wants to summarize performance or connectivity beyond the directly measured pair.

## Core decision

Extrapolation is a forecast over topology roles, not a vibe.
The page must explicitly map the claim onto uploader cohorts, receiver cohorts, route segments, and known counterexamples.

## Fixed review order

1. **Winning hypothesis**
2. **Role-distribution map**
3. **Expected applicability**
4. **Counterexample seats**
5. **Operational recommendation boundary**

## 1) Winning hypothesis

Show the current explanation being extrapolated, for example:

- relay penalty dominates
- one uploader is the bottleneck
- network ceiling is comfortably above live Sync speed
- local disk/finalize work dominates after network is exonerated

Also show the proof class and freshness.

## 2) Role-distribution map

Group topology members by performance-relevant role:

- slow uploaders
- strong uploaders
- relay-bound receivers
- direct receivers
- peers outside current witness set
- peers currently unavailable

The operator must be able to answer:

> who in the mesh actually shares the measured condition?

## 3) Expected applicability

For each cohort publish one applicability verdict:

- `same condition strongly likely`
- `same condition plausible`
- `insufficient similarity`
- `known different`

Also show why, such as same uploader, same route class, same helper policy, or same hardware/network class.

## 4) Counterexample seats

Highlight the seats most likely to falsify the current hypothesis:

- receivers on a different path class
- an uploader with materially higher or lower capacity
- peers missing direct ingress while measured pair had it
- peers still on relay despite route-change advice
- any unavailable seat whose later return could widen or break the story

Each counterexample seat should show the cheapest validating check.

## 5) Operational recommendation boundary

The page may recommend actions only at the widest level honestly supported, for example:

- pair-only tuning
- uploader-cohort tuning
- route-segment repair
- share-wide advisory
- hold broader advice pending more coverage

It must never let a pair-only result trigger a share-wide knob recommendation without explicitly saying the generalization is weak.

## Compact rendering obligations

Any compact advisory card must still preserve:

- current winning hypothesis
- covered cohorts
- excluded or contradictory cohorts
- recommendation boundary
- stronger forbidden recommendation

## Anti-clone rule

Do not clone workflows where `one slow pair`, `one relay icon`, or `one iperf result` immediately becomes a mesh-wide repair recipe.
